"""Main simulation loop: orchestrate days, run segment agents, execute actions."""
import random
from pathlib import Path
from typing import Any, Optional

from models import (
    Memory,
    RunLogEntry,
    SegmentState,
    SimulateResult,
)
from memory import append_log, now_iso, save_memory
from api_client import call_endpoint
from orchestrator import generate_segments
from segment_agent import plan_segment_period
from sql_writer import SqlSink
from growth import growth_stage_for_day


# How many days a single LLM planning call covers, per mode. Fewer calls = cheaper
# but less day-to-day continuity (the agent plans the whole period blind to itself).
STEP_DAYS = {"day": 1, "month": 30, "year": 365}


def _find_endpoint(memory: Memory, purpose: str):
    for ep in memory.endpoints:
        if ep.purpose == purpose:
            return ep
    return None


# ---------------------------------------------------------------------------
# SQL sink helpers (used when output_mode == "sql")
# ---------------------------------------------------------------------------

def _build_sink(memory: Memory) -> Optional[SqlSink]:
    s = memory.settings or {}
    if (s.get("output_mode") or "api") != "sql":
        return None
    sql_cfg = dict(s.get("sql") or {})
    file_path = sql_cfg.get("file_path")
    if not file_path:
        file_path = str(Path(__file__).resolve().parent.parent / "Siupo Restaurant.sql")
    sink = SqlSink(file_path, memory.sql_sink, sql_cfg)
    sink.ensure_header()
    return sink


def _iter_products(snapshot: dict) -> list[dict]:
    node = snapshot.get("list_products")
    items: Any = []
    if isinstance(node, dict):
        data = node.get("data", node)
        if isinstance(data, dict):
            items = data.get("content") or data.get("items") or []
        elif isinstance(data, list):
            items = data
    elif isinstance(node, list):
        items = node
    return [p for p in items if isinstance(p, dict)]


_UNAVAILABLE_STATUS = {"UNAVAILABLE", "DELETED", "HIDDEN", "INACTIVE", "OUT_OF_STOCK"}


def _price_of(rec: Optional[dict], keys: tuple) -> float:
    if not rec:
        return 0.0
    for k in keys:
        v = rec.get(k)
        if isinstance(v, (int, float)):
            return float(v)
    return 0.0


def _get_product(snapshot: dict, product_id: Any) -> Optional[dict]:
    for p in _iter_products(snapshot):
        pid = p.get("id") or p.get("productId")
        if pid is not None and str(pid) == str(product_id):
            return p
    return None


def _iter_combos(snapshot: dict) -> list[dict]:
    node = snapshot.get("list_combos")
    items: Any = []
    if isinstance(node, dict):
        data = node.get("data", node)
        if isinstance(data, dict):
            items = data.get("content") or data.get("items") or []
        elif isinstance(data, list):
            items = data
    elif isinstance(node, list):
        items = node
    return [c for c in items if isinstance(c, dict)]


def _get_combo(snapshot: dict, combo_id: Any) -> Optional[dict]:
    for c in _iter_combos(snapshot):
        cid = c.get("id") or c.get("comboId")
        if cid is not None and str(cid) == str(combo_id):
            return c
    return None


def _find_voucher(snapshot: dict, code: Any) -> Optional[dict]:
    node = snapshot.get("list_vouchers")
    arr: Any = []
    if isinstance(node, dict):
        data = node.get("data", node)
        arr = data.get("content") if isinstance(data, dict) else data
    elif isinstance(node, list):
        arr = node
    if not isinstance(arr, list):
        return None
    for v in arr:
        if isinstance(v, dict) and str(v.get("code")) == str(code):
            return v
    return None


_PRODUCT_PRICE_KEYS = ("price", "salePrice", "sale_price", "unitPrice", "currentPrice")
_COMBO_PRICE_KEYS = ("basePrice", "base_price", "price", "originalPrice")


def _resolve_combo_item(snapshot: dict, cid: Any, qty: int) -> Optional[dict]:
    """Only accept combos that exist in the snapshot; always price from the real catalog."""
    combo = _get_combo(snapshot, cid)
    if combo is None:
        return None
    if str(combo.get("status") or "").upper() in _UNAVAILABLE_STATUS:
        return None
    price = _price_of(combo, _COMBO_PRICE_KEYS)
    if price <= 0:
        return None
    return {"combo_id": int(cid), "quantity": qty, "price": price}


def _resolve_product_item(snapshot: dict, pid: Any, qty: int) -> Optional[dict]:
    """Only accept products that exist & are available; always price from the real catalog."""
    prod = _get_product(snapshot, pid)
    if prod is None:  # hallucinated id not in the catalog -> drop it
        return None
    if str(prod.get("status") or "").upper() in _UNAVAILABLE_STATUS:
        return None
    price = _price_of(prod, _PRODUCT_PRICE_KEYS)
    if price <= 0:
        return None
    return {"product_id": int(pid), "quantity": qty, "price": price}


def _extract_items(body: dict, snapshot: dict) -> list[dict]:
    """Build order lines from an LLM action, enforcing real catalog ids + prices.

    The agent may invent product ids or prices; we ignore its prices and silently
    drop any line whose product/combo isn't a real, available entry in the snapshot.
    """
    raw = body.get("items") or body.get("orderItems") or []
    items: list[dict] = []
    if isinstance(raw, list):
        for it in raw:
            if not isinstance(it, dict):
                continue
            qty = int(it.get("quantity") or it.get("qty") or 1)
            cid = it.get("comboId") or it.get("combo_id")
            if isinstance(it.get("combo"), dict):
                cid = cid or it["combo"].get("id")
            if cid is not None:
                line = _resolve_combo_item(snapshot, cid, qty)
                if line:
                    items.append(line)
                continue
            pid = None
            if isinstance(it.get("product"), dict):
                pid = it["product"].get("id")
            pid = pid or it.get("productId") or it.get("product_id") or it.get("id")
            if pid is None:
                continue
            line = _resolve_product_item(snapshot, pid, qty)
            if line:
                items.append(line)
    if not items:
        pid = body.get("productId") or body.get("product_id")
        if pid is not None:
            line = _resolve_product_item(snapshot, pid, int(body.get("quantity") or 1))
            if line:
                items.append(line)
    return items


def _register_user(memory: Memory, uid: int) -> None:
    pool = memory.sql_sink.setdefault("user_ids", [])
    pool.append(uid)
    if len(pool) > 5000:
        del pool[:-5000]


def _create_user_sql(memory: Memory, sink: SqlSink, body: dict) -> int:
    # Let the sink generate a consistent realistic name + matching gender, rather than
    # reusing the LLM's often-generic labels ("Khách lẻ mới"...).
    uid = sink.add_customer()
    _register_user(memory, uid)
    return uid


def _get_or_create_user_sql(memory: Memory, sink: SqlSink) -> int:
    pool = memory.sql_sink.get("user_ids") or []
    if pool and random.random() < 0.7:
        return random.choice(pool)
    return _create_user_sql(memory, sink, {})


def _execute_action_sql(
    memory: Memory,
    action: dict[str, Any],
    last_user_id: Optional[str],
    sink: SqlSink,
) -> tuple[bool, Optional[str], Optional[Any], str]:
    purpose = action.get("endpoint_purpose") or action.get("type")
    body = action.get("body") if isinstance(action.get("body"), dict) else {}

    if purpose == "create_user":
        uid = _create_user_sql(memory, sink, body)
        return True, str(uid), {"userId": uid}, f"SQL user #{uid}"

    if purpose == "create_order":
        items = _extract_items(body, memory.snapshot)
        if not items:
            return False, None, None, "Không trích được item nào cho đơn"
        uid: Optional[int] = None
        if last_user_id:
            try:
                uid = int(last_user_id)
            except (TypeError, ValueError):
                uid = None
        if uid is None:
            uid = _get_or_create_user_sql(memory, sink)
        code = body.get("voucherCode") or body.get("voucher_code")
        voucher = _find_voucher(memory.snapshot, code) if code else None
        pm = body.get("paymentMethod") or body.get("payment_method") or "COD"
        if pm not in ("COD", "MOMO"):
            pm = "COD"
        summ = sink.add_order(uid, items, voucher=voucher, payment_method=pm)
        data = {"totalAmount": summ["total"], **summ}
        return True, None, data, f"SQL order #{summ['order_id']} total {summ['total']}"

    return True, None, None, f"(SQL mode) bỏ qua '{purpose}'"


def _try_extract(data: Any, keys: list[str]) -> Optional[Any]:
    if not isinstance(data, dict):
        return None
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    # Look one level deeper (some APIs nest under "data")
    nested = data.get("data") if isinstance(data.get("data"), dict) else None
    if nested:
        for k in keys:
            if k in nested and nested[k] is not None:
                return nested[k]
    return None


def _resolve_marker(body: Any, last_user_id: Optional[str]) -> Any:
    if isinstance(body, dict):
        return {k: _resolve_marker(v, last_user_id) for k, v in body.items()}
    if isinstance(body, list):
        return [_resolve_marker(v, last_user_id) for v in body]
    if isinstance(body, str) and body == "{{LAST_CREATED_USER}}":
        return last_user_id
    return body


def _execute_action(
    memory: Memory,
    segment: SegmentState,
    action: dict[str, Any],
    last_user_id: Optional[str],
    sink: Optional[SqlSink] = None,
) -> tuple[bool, Optional[str], Optional[Any], str]:
    """Returns (success, new_user_id, response_data, message)."""
    if sink is not None:
        return _execute_action_sql(memory, action, last_user_id, sink)
    purpose = action.get("endpoint_purpose") or action.get("type")
    if purpose == "create_user":
        purpose = "create_user"
    elif purpose == "create_order":
        purpose = "create_order"

    ep = _find_endpoint(memory, purpose)
    if ep is None:
        return False, None, None, f"No endpoint configured for purpose '{purpose}'"

    body = action.get("body") or {}
    body = _resolve_marker(body, last_user_id)

    status, data, err = call_endpoint(memory.business, ep, body=body if isinstance(body, dict) else None)
    if err:
        return False, None, data, err

    user_id = None
    if purpose == "create_user":
        user_id = _try_extract(data, ["id", "userId", "user_id", "_id"])
        if user_id is not None:
            user_id = str(user_id)
    return True, user_id, data, f"{status} OK"


def _segment_for_user(memory: Memory, segment_id: str) -> Optional[SegmentState]:
    for s in memory.simulation.segments:
        if s.id == segment_id:
            return s
    return None


def _ensure_segments(memory: Memory, llm: dict) -> list[RunLogEntry]:
    new_logs: list[RunLogEntry] = []
    if memory.simulation.segments:
        return new_logs
    segments = generate_segments(memory, llm)
    memory.simulation.segments = segments
    entry = RunLogEntry(
        timestamp=now_iso(), day=memory.simulation.current_day,
        action="orchestrator_init", status="ok",
        detail=f"Generated {len(segments)} segments: " + ", ".join(s.name for s in segments),
    )
    append_log(memory, entry)
    new_logs.append(entry)
    return new_logs


def _estimate_order_value(action: dict[str, Any], data: Any) -> float:
    body = action.get("body") if isinstance(action.get("body"), dict) else {}
    for k in ("totalAmount", "total", "amount", "totalPrice", "price"):
        v = body.get(k)
        if isinstance(v, (int, float)):
            return float(v)
    if isinstance(data, dict):
        for k in ("totalAmount", "total", "amount", "totalPrice", "price"):
            v = data.get(k)
            if isinstance(v, (int, float)):
                return float(v)
    return 0.0


def _order_value(action: dict[str, Any], data: Any, snapshot: dict) -> float:
    """Order total: prefer explicit total from body/response, else compute from items + snapshot prices."""
    val = _estimate_order_value(action, data)
    if val > 0:
        return val
    body = action.get("body") if isinstance(action.get("body"), dict) else {}
    return sum(float(it["price"]) * int(it["quantity"]) for it in _extract_items(body, snapshot))


def _order_product_names(action: dict[str, Any], snapshot: dict) -> list[str]:
    """Resolve product names for an order: explicit body field first, else lookup item ids in snapshot."""
    body = action.get("body") if isinstance(action.get("body"), dict) else {}
    names: list[str] = []
    pname = body.get("productName") or body.get("product_name")
    if isinstance(pname, str) and pname:
        names.append(pname)
    for it in _extract_items(body, snapshot):
        pid = it.get("product_id")
        if pid is None:
            continue
        prod = _get_product(snapshot, pid)
        if prod:
            nm = prod.get("name") or prod.get("productName")
            if nm:
                names.append(str(nm))
    return names


def _normalize_action_days(plan: dict[str, Any], period_days: int) -> None:
    """Ensure every action has a valid day_offset in [0, period_days-1].

    Actions missing/out-of-range offsets are spread round-robin so a period plan
    never collapses all activity onto day 0.
    """
    actions = plan.get("actions") or []
    rr = 0
    for a in actions:
        if not isinstance(a, dict):
            continue
        off = a.get("day_offset")
        try:
            off = int(off)
        except (TypeError, ValueError):
            off = None
        if off is None or off < 0 or off >= period_days:
            off = rr % period_days
            rr += 1
        a["day_offset"] = off


def _actions_for_day(plan: dict[str, Any], day_offset: int) -> list[dict[str, Any]]:
    return [a for a in (plan.get("actions") or []) if isinstance(a, dict) and a.get("day_offset") == day_offset]


def _run_segment_actions(
    memory: Memory,
    segment: SegmentState,
    actions: list[dict[str, Any]],
    day: int,
    sink: Optional[SqlSink],
    new_logs: list[RunLogEntry],
) -> dict[str, Any]:
    """Execute one segment's actions for a single day. Updates global counters; returns day stats."""
    last_user_id: Optional[str] = None
    orders_done = 0
    revenue = 0.0
    products_seen: dict[str, int] = {}
    voucher_used = 0
    voucher_total = 0

    for action in actions:
        ok, new_user_id, data, msg = _execute_action(memory, segment, action, last_user_id, sink)
        atype = action.get("type") or action.get("endpoint_purpose")
        log = RunLogEntry(
            timestamp=now_iso(), day=day, segment_id=segment.id,
            action=str(atype), status="ok" if ok else "error",
            endpoint=str(action.get("endpoint_purpose", "")),
            detail=f"{msg} | {str(action.get('note', ''))[:120]}",
        )
        append_log(memory, log)
        new_logs.append(log)

        if not ok:
            continue
        if new_user_id:
            last_user_id = new_user_id
            memory.simulation.total_users_created += 1
        if atype == "create_order":
            orders_done += 1
            memory.simulation.total_orders_created += 1
            val = _order_value(action, data, memory.snapshot)
            revenue += val
            memory.simulation.total_revenue += val
            for name in _order_product_names(action, memory.snapshot):
                products_seen[name] = products_seen.get(name, 0) + 1
            body = action.get("body") if isinstance(action.get("body"), dict) else {}
            voucher_total += 1
            if body.get("voucherId") or body.get("voucher_id") or body.get("voucherCode") or body.get("voucher_code"):
                voucher_used += 1

    return {
        "orders": orders_done,
        "revenue": revenue,
        "products_seen": products_seen,
        "voucher_used": voucher_used,
        "voucher_total": voucher_total,
    }


def _apply_segment_day_stats(segment: SegmentState, stats: dict[str, Any], plan: dict[str, Any]) -> None:
    """Fold one day's stats into a segment. yesterday_* reflects the most recent day; total_* accumulates."""
    orders_done = stats["orders"]
    revenue = stats["revenue"]
    products_seen = stats["products_seen"]
    voucher_total = stats["voucher_total"]
    segment.yesterday_orders = orders_done
    segment.yesterday_revenue = revenue
    segment.total_orders += orders_done
    segment.total_revenue += revenue
    segment.top_products = [p for p, _ in sorted(products_seen.items(), key=lambda kv: -kv[1])[:3]]
    segment.voucher_usage_rate = (stats["voucher_used"] / voucher_total) if voucher_total else 0.0
    segment.yesterday_summary = (
        f"Tạo {orders_done} đơn, doanh thu ~{revenue:,.0f}. "
        + (f"Top: {', '.join(segment.top_products)}. " if segment.top_products else "")
        + str(plan.get("reasoning", ""))[:200]
    )


def _simulate_period(
    memory: Memory,
    llm: dict,
    period_days: int,
    sink: Optional[SqlSink],
    new_logs: list[RunLogEntry],
) -> None:
    """Plan one period (period_days) per segment in a single LLM call, then replay day-by-day."""
    sim = memory.simulation
    start_day = sim.current_day + 1
    sim.growth_stage = growth_stage_for_day(start_day, memory.growth)

    # One planning call per segment for the whole period.
    plans: dict[str, dict[str, Any]] = {}
    for segment in sim.segments:
        try:
            plan = plan_segment_period(memory, segment, llm, period_days, start_day)
        except Exception as e:
            plans[segment.id] = {"actions": [], "reasoning": f"plan failed: {e}"}
            entry = RunLogEntry(
                timestamp=now_iso(), day=start_day, segment_id=segment.id,
                action="segment_plan", status="error", detail=f"Plan failed: {e}",
            )
            append_log(memory, entry)
            new_logs.append(entry)
            continue
        _normalize_action_days(plan, period_days)
        plans[segment.id] = plan
        entry = RunLogEntry(
            timestamp=now_iso(), day=start_day, segment_id=segment.id,
            action="segment_plan", status="ok",
            detail=(
                f"[{segment.name}] kỳ {period_days}d: {plan.get('num_new_users', 0)} new users, "
                f"{plan.get('num_orders', 0)} orders. Reason: {str(plan.get('reasoning', ''))[:200]}"
            ),
        )
        append_log(memory, entry)
        new_logs.append(entry)

    # Replay the period one day at a time so SQL day-blocks and timestamps stay per-day.
    for d in range(period_days):
        day = start_day + d
        sim.current_day = day
        if sink is not None:
            sink.begin_day(day)
        entry = RunLogEntry(
            timestamp=now_iso(), day=day, action="day_start", status="info",
            detail=f"Starting day {day}",
        )
        append_log(memory, entry)
        new_logs.append(entry)

        for segment in sim.segments:
            plan = plans.get(segment.id, {"actions": []})
            day_actions = _actions_for_day(plan, d)
            stats = _run_segment_actions(memory, segment, day_actions, day, sink, new_logs)
            _apply_segment_day_stats(segment, stats, plan)

        if sink is not None:
            sink.end_day()
        entry = RunLogEntry(
            timestamp=now_iso(), day=day, action="day_end", status="info",
            detail=f"Day {day} done. Cumulative: {sim.total_orders_created} orders, {sim.total_users_created} users",
        )
        append_log(memory, entry)
        new_logs.append(entry)


def simulate(memory: Memory, days: int, llm: dict) -> SimulateResult:
    all_new_logs: list[RunLogEntry] = []
    sink = _build_sink(memory)
    all_new_logs.extend(_ensure_segments(memory, llm))

    step = STEP_DAYS.get(memory.growth.mode, 1)
    remaining = days
    while remaining > 0:
        n = min(step, remaining)
        _simulate_period(memory, llm, n, sink, all_new_logs)
        remaining -= n
        memory.simulation.last_run_at = now_iso()
        save_memory(memory)

    return SimulateResult(
        days_simulated=days,
        new_logs=all_new_logs,
        final_day=memory.simulation.current_day,
    )

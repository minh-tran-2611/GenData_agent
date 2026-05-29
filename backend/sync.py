"""Sync phase: call READ endpoints, diff with previous snapshot, update memory."""
import json
import hashlib
from typing import Any

from models import Memory, RunLogEntry, SyncResult
from memory import append_log, now_iso
from api_client import call_endpoint


READ_PURPOSES = {"list_products", "list_vouchers", "list_categories", "list_combos", "get_config", "other_read"}


def _hash_value(value: Any) -> str:
    try:
        s = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        s = str(value)
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _diff_snapshots(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    changes: list[str] = []
    for key in new:
        if key not in old:
            changes.append(f"Mới: {key} = {_brief(new[key])}")
            continue
        if _hash_value(old[key]) != _hash_value(new[key]):
            changes.append(f"Thay đổi: {key} → {_brief(new[key])}")
    for key in old:
        if key not in new:
            changes.append(f"Bị xóa: {key}")
    return changes


def _brief(value: Any, max_len: int = 200) -> str:
    if isinstance(value, list):
        return f"list[{len(value)} items]"
    s = json.dumps(value, ensure_ascii=False)
    return s if len(s) <= max_len else s[:max_len] + "..."


def run_sync(memory: Memory) -> SyncResult:
    business = memory.business
    new_snapshot: dict[str, Any] = {}
    synced: list[str] = []
    errors: list[str] = []

    for ep in memory.endpoints:
        if ep.purpose not in READ_PURPOSES:
            continue
        status, data, err = call_endpoint(business, ep)
        ts = now_iso()
        if err:
            errors.append(f"{ep.name}: {err}")
            append_log(memory, RunLogEntry(
                timestamp=ts, day=memory.simulation.current_day,
                action="sync_read", endpoint=ep.name, status="error",
                detail=f"{err}",
            ))
            continue
        new_snapshot[ep.purpose] = data
        synced.append(ep.name)
        append_log(memory, RunLogEntry(
            timestamp=ts, day=memory.simulation.current_day,
            action="sync_read", endpoint=ep.name, status="ok",
            detail=f"{status} {_brief(data)}",
        ))

    changes = _diff_snapshots(memory.snapshot, new_snapshot)
    memory.snapshot = new_snapshot
    memory.changes_from_last_run = changes

    append_log(memory, RunLogEntry(
        timestamp=now_iso(), day=memory.simulation.current_day,
        action="sync_complete", status="info",
        detail=f"Synced {len(synced)} endpoints, {len(changes)} changes, {len(errors)} errors",
    ))

    return SyncResult(synced_endpoints=synced, changes=changes, errors=errors)

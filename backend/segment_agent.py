"""Segment agent: each represents one customer segment. Plans a period of activity."""
import json
from typing import Any

from models import Memory, SegmentState, EndpointConfig
from llm import call_llm_json
from growth import expected_total_orders_over


SEGMENT_SYSTEM = """Bạn là Segment Agent đại diện cho MỘT TỆP KHÁCH HÀNG cụ thể trong hệ thống mô phỏng doanh nghiệp.

Nhiệm vụ: Dựa trên thông tin tệp (size, personality), giai đoạn tăng trưởng, mục tiêu định hướng, snapshot sản phẩm/voucher hiện tại, và lịch sử gần nhất — quyết định nhóm bạn sẽ tạo ra những bản ghi gì trong KỲ mô phỏng này.

Nguyên tắc:
- 1 segment = nhóm size người. Mỗi người có thể tạo 0-3 đơn/ngày.
- Số đơn phụ thuộc:
  * Giai đoạn tăng trưởng (early=ít, growing=tăng dần, stable=đều, plateau=bão hòa)
  * MỤC TIÊU ĐỊNH HƯỚNG được cung cấp (số đơn / user mới gợi ý cho cả kỳ) — bám sát nhưng được dao động ±25% cho tự nhiên
  * Personality (tệp nhạy giá → đơn nhỏ; tệp giàu → đơn lớn; tệp mua sáng → giờ sớm)
  * Lịch sử gần nhất (không nên giống y chang, có biến thiên tự nhiên: cuối tuần / cao điểm khác ngày thường)
  * Voucher/sản phẩm mới có thể kích đơn tăng
- Mỗi action phải REALISTIC: chỉ chọn sản phẩm có trong snapshot, voucher hợp lệ (phù hợp tệp).
- Tỉ lệ user mới: bám theo mục tiêu (cần create_user trước rồi create_order cho user đó).

QUAN TRỌNG về phân bổ theo ngày:
- Kỳ này gồm N ngày. MỖI action PHẢI có trường "day_offset" là số nguyên trong [0, N-1] cho biết action xảy ra vào ngày thứ mấy trong kỳ.
- Phân bổ action trải đều/realistic qua các ngày (không dồn hết vào 1 ngày), phản ánh nhịp mua theo ngày trong tuần.

Output: JSON object đúng schema sau, KHÔNG có text thừa:
{
  "reasoning": "1-2 câu giải thích ngắn vì sao chọn số đơn này",
  "num_new_users": <int tổng cho cả kỳ>,
  "num_orders": <int tổng cho cả kỳ>,
  "actions": [
    {
      "type": "create_user" | "create_order",
      "endpoint_purpose": "create_user" | "create_order",
      "day_offset": <int 0..N-1>,
      "body": { ... payload phù hợp endpoint ... },
      "note": "mô tả ngắn (ví dụ: 'user mới mua cà phê sữa lúc sáng')"
    }
  ]
}

QUAN TRỌNG về body:
- "body" phải dùng key/field name khớp với endpoint thực tế. Hãy xem mô tả endpoint + body_schema mẫu (nếu có) để format đúng.
- Nếu không chắc field nào, hãy chọn key thông dụng (userId, productId, quantity, totalAmount, voucherId/voucherCode, paymentMethod, items[], ...).
- Mỗi create_order nên reference 1 user (mới hoặc cũ — nếu cũ thì bịa userId giống pattern hoặc dùng marker {{LAST_CREATED_USER}}).
"""


def _summarize_snapshot(snapshot: dict[str, Any], max_items: int = 20) -> str:
    parts = []
    for key, value in snapshot.items():
        if isinstance(value, list):
            sample = value[:max_items]
            parts.append(f"### {key} (tổng {len(value)}, hiển thị {len(sample)})\n{json.dumps(sample, ensure_ascii=False, indent=2)[:2000]}")
        else:
            parts.append(f"### {key}\n{json.dumps(value, ensure_ascii=False, indent=2)[:1000]}")
    return "\n\n".join(parts) if parts else "(không có snapshot)"


def _endpoint_brief(endpoints: list[EndpointConfig]) -> str:
    lines = []
    for e in endpoints:
        if e.purpose not in ("create_user", "create_order", "apply_voucher", "other_write"):
            continue
        lines.append(f"- [{e.purpose}] {e.method} {e.url} — {e.description or e.name}")
        if e.body_schema:
            lines.append(f"    body_schema: {json.dumps(e.body_schema, ensure_ascii=False)[:500]}")
    return "\n".join(lines) if lines else "(chưa khai báo endpoint create_user/create_order)"


def plan_segment_period(
    memory: Memory,
    segment: SegmentState,
    llm: dict,
    period_days: int = 1,
    start_day: int = 1,
) -> dict[str, Any]:
    """Ask the segment agent to plan `period_days` worth of activity in one call."""
    business = memory.business
    sim = memory.simulation
    g = memory.growth
    period_days = max(1, int(period_days))

    # Soft growth targets for THIS segment over the whole period.
    total_orders_period = expected_total_orders_over(start_day, period_days, g) * max(0.0, segment.weight)
    target_orders = max(0, round(total_orders_period))
    target_new_users = max(0, round(target_orders * max(0.0, g.new_user_ratio)))
    end_day = start_day + period_days - 1

    snapshot_text = _summarize_snapshot(memory.snapshot)
    endpoint_text = _endpoint_brief(memory.endpoints)
    changes_text = "\n".join(f"- {c}" for c in memory.changes_from_last_run) or "(không có thay đổi)"

    user_prompt = f"""## Bối cảnh doanh nghiệp
- Tên: {business.name}
- Loại: {business.business_type}
- Giai đoạn tăng trưởng: {sim.growth_stage}
- KỲ mô phỏng hiện tại: {period_days} ngày (ngày {start_day} → ngày {end_day})

## Tệp khách hàng của bạn
- Tên: {segment.name}
- Mô tả: {segment.description}
- Size nhóm: {segment.size} người
- Tỷ trọng trong toàn quán (weight): {segment.weight:.2f}
- Personality hints: {", ".join(segment.personality_hints) or "(không có)"}

## MỤC TIÊU ĐỊNH HƯỚNG cho cả kỳ (bám sát, ±25%)
- Số đơn gợi ý: ~{target_orders} đơn
- Số user mới gợi ý: ~{target_new_users} user
(Mục tiêu đã tính theo đường cong tăng trưởng: đầu {g.start_orders_per_day} đơn/ngày toàn quán, +{g.monthly_growth_rate:.0%}/tháng, bão hòa tháng {g.plateau_at_month}, tỷ lệ user mới {g.new_user_ratio:.0%}.)

## Lịch sử gần nhất của tệp này
- Số đơn ngày gần nhất: {segment.yesterday_orders}
- Doanh thu ngày gần nhất: {segment.yesterday_revenue:,.0f}
- Sản phẩm bán chạy: {", ".join(segment.top_products) or "(chưa có)"}
- Tỷ lệ dùng voucher: {segment.voucher_usage_rate:.2%}
- Tóm tắt: {segment.yesterday_summary or "(chưa có)"}

## Thay đổi từ lần sync mới nhất
{changes_text}

## Snapshot sản phẩm/voucher hiện có
{snapshot_text}

## Endpoint write có thể gọi (để format body đúng)
{endpoint_text}

## Yêu cầu
Hãy quyết định cho CẢ KỲ {period_days} ngày này: tổng bao nhiêu user mới, bao nhiêu đơn, và list từng action chi tiết kèm "day_offset" (0..{period_days - 1}) để trải hành vi qua các ngày. Trả về JSON đúng schema. Bám mục tiêu định hướng, giữ liên tục với lịch sử nhưng có biến thiên tự nhiên.
"""

    result = call_llm_json(
        llm=llm,
        system=SEGMENT_SYSTEM,
        user=user_prompt,
        max_tokens=8000 if period_days > 1 else 4000,
        temperature=0.85,
    )

    if not isinstance(result, dict):
        result = {"reasoning": "fallback", "num_new_users": 0, "num_orders": 0, "actions": []}
    result.setdefault("reasoning", "")
    result.setdefault("num_new_users", 0)
    result.setdefault("num_orders", 0)
    result.setdefault("actions", [])
    return result

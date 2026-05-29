"""Orchestrator agent: analyzes business and decides customer segments + growth plan."""
import json
from typing import Any
from uuid import uuid4

from models import Memory, SegmentState
from llm import call_llm_json


ORCHESTRATOR_SYSTEM = """Bạn là Orchestrator Agent của hệ thống sinh data mô phỏng doanh nghiệp.

Nhiệm vụ: Phân tích thông tin doanh nghiệp + danh sách sản phẩm/voucher thực tế để đề xuất các TỆP KHÁCH HÀNG (customer segments) phù hợp.

Nguyên tắc:
- Mỗi tệp = một NHÓM người (1 segment đại diện 1-100 người có hành vi tương tự)
- Tỷ trọng (weight) các tệp phải cộng lại ≈ 1.0
- Số tệp: thường 3-6 tệp, không quá nhiều
- Tệp phải phản ánh ĐÚNG đặc thù doanh nghiệp này, KHÔNG dùng template chung
- Personality hints: 3-5 từ khóa ngắn mô tả thói quen mua (ví dụ: "nhạy giá", "mua sáng", "thường dùng voucher")

Output: JSON object đúng schema sau, KHÔNG có text thừa:
{
  "growth_stage": "early" | "growing" | "stable" | "plateau",
  "segments": [
    {
      "name": "Tên tệp ngắn gọn",
      "description": "1-2 câu mô tả tệp này là ai",
      "size": <int 1-100>,
      "weight": <float 0-1>,
      "personality_hints": ["hint1", "hint2", ...]
    }
  ]
}
"""


def _summarize_snapshot(snapshot: dict[str, Any], max_items: int = 20) -> str:
    parts = []
    for key, value in snapshot.items():
        if isinstance(value, list):
            sample = value[:max_items]
            parts.append(f"== {key} (total {len(value)}, showing {len(sample)}) ==\n{json.dumps(sample, ensure_ascii=False, indent=2)}")
        else:
            parts.append(f"== {key} ==\n{json.dumps(value, ensure_ascii=False, indent=2)[:1500]}")
    return "\n\n".join(parts) if parts else "(no snapshot data)"


def generate_segments(memory: Memory, llm: dict) -> list[SegmentState]:
    business = memory.business
    snapshot_text = _summarize_snapshot(memory.snapshot)

    user_prompt = f"""## Thông tin doanh nghiệp
- Tên: {business.name or "(chưa khai báo)"}
- Loại hình: {business.business_type or "(chưa khai báo)"}
- Mô tả: {business.description or "(chưa có)"}
- Địa điểm: {business.location or "(chưa khai báo)"}
- Ngày mở: {business.open_date or "(chưa khai báo)"}
- Ghi chú: {business.notes or "(không có)"}

## Snapshot từ API doanh nghiệp (đã sync)
{snapshot_text}

## Yêu cầu
Phân tích doanh nghiệp trên và đề xuất 3-6 tệp khách hàng. Trả về JSON đúng schema.
"""

    result = call_llm_json(
        llm=llm,
        system=ORCHESTRATOR_SYSTEM,
        user=user_prompt,
        max_tokens=3000,
        temperature=0.6,
    )

    segments: list[SegmentState] = []
    raw_segments = result.get("segments", []) if isinstance(result, dict) else []
    for s in raw_segments:
        segments.append(SegmentState(
            id=str(uuid4())[:8],
            name=str(s.get("name", "Unknown")),
            description=str(s.get("description", "")),
            size=int(s.get("size", 10)),
            weight=float(s.get("weight", 0.1)),
            personality_hints=[str(h) for h in s.get("personality_hints", [])],
        ))

    if isinstance(result, dict) and result.get("growth_stage"):
        stage = result["growth_stage"]
        if stage in ("early", "growing", "stable", "plateau"):
            memory.simulation.growth_stage = stage

    return segments

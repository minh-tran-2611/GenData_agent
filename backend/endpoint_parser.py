"""Parse raw text (cURL, docs, notes...) into structured EndpointConfig list via Claude."""
from typing import Any

from llm import call_llm_json


PARSER_SYSTEM = """Bạn là agent phân tích tài liệu API. Nhiệm vụ: đọc đoạn text user dán vào (có thể là cURL, Postman, swagger snippet, mô tả tay, ...) và trích xuất ra DANH SÁCH endpoint, mỗi endpoint có cấu trúc chuẩn.

PURPOSE phải chọn từ danh sách CỐ ĐỊNH:
- list_products    (GET danh sách sản phẩm/menu/items)
- list_vouchers    (GET danh sách voucher/discount/promotion)
- list_categories  (GET danh sách danh mục/category)
- list_combos      (GET danh sách combo/set/bundle)
- get_config       (GET cấu hình/policy/settings của shop)
- other_read       (GET khác)
- create_user      (POST tạo user/customer/account)
- create_order     (POST tạo đơn hàng/order/invoice/booking)
- apply_voucher    (POST áp voucher vào đơn)
- other_write      (POST/PUT/PATCH/DELETE khác)

Quy tắc:
- Nếu URL bắt đầu bằng http(s):// → giữ nguyên. Nếu là path tương đối (/api/...) → giữ nguyên path, base_url sẽ ghép sau.
- Headers: chỉ lấy header có giá trị thật. Nếu thấy Bearer token / API key → giữ lại đúng.
- body_schema: nếu tài liệu có ví dụ JSON body, đưa vào dạng object schema (key + giá trị mẫu/type).
- description: 1 câu ngắn mô tả endpoint làm gì (tiếng Việt OK).
- name: snake_case ngắn gọn, ví dụ "get_all_products", "create_order".
- Bỏ qua endpoint không liên quan đến hành vi mua bán (auth/login/logout, admin, health-check) — TRỪ KHI user chỉ định rõ.
- Nếu không chắc purpose → chọn other_read / other_write.

Output: JSON ARRAY (không object wrapper), KHÔNG có text thừa, KHÔNG markdown fence:
[
  {
    "name": "get_all_products",
    "method": "GET",
    "url": "/api/products",
    "purpose": "list_products",
    "headers": {"Authorization": "Bearer xxx"},
    "description": "Lấy toàn bộ danh sách sản phẩm",
    "body_schema": null,
    "query_params": {"limit": "100"}
  },
  ...
]

Nếu text không chứa endpoint nào hợp lệ → trả về [].
"""


ALLOWED_PURPOSES = {
    "list_products", "list_vouchers", "list_categories", "list_combos", "get_config", "other_read",
    "create_user", "create_order", "apply_voucher", "other_write",
}
ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def _normalize(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        method = str(item.get("method", "GET")).upper()
        if method not in ALLOWED_METHODS:
            method = "GET"
        purpose = str(item.get("purpose", "other_read"))
        if purpose not in ALLOWED_PURPOSES:
            purpose = "other_write" if method != "GET" else "other_read"
        url = str(item.get("url", "")).strip()
        if not url:
            continue
        name = str(item.get("name", "")).strip() or f"{method.lower()}_{url.strip('/').replace('/', '_')}"[:50]
        headers = item.get("headers") or {}
        if not isinstance(headers, dict):
            headers = {}
        query_params = item.get("query_params") or {}
        if not isinstance(query_params, dict):
            query_params = {}
        body_schema = item.get("body_schema")
        if body_schema is not None and not isinstance(body_schema, (dict, list)):
            body_schema = None
        out.append({
            "name": name,
            "method": method,
            "url": url,
            "purpose": purpose,
            "headers": {str(k): str(v) for k, v in headers.items()},
            "description": str(item.get("description", "")),
            "body_schema": body_schema,
            "query_params": {str(k): str(v) for k, v in query_params.items()},
        })
    return out


def parse_endpoints_from_text(text: str, llm: dict) -> list[dict[str, Any]]:
    if not text or not text.strip():
        return []
    user_prompt = f"""## Text user dán vào

```
{text.strip()[:15000]}
```

## Yêu cầu
Trích xuất tất cả endpoint và trả về JSON ARRAY đúng schema. Không có text thừa."""
    result = call_llm_json(
        llm=llm,
        system=PARSER_SYSTEM,
        user=user_prompt,
        max_tokens=4000,
        temperature=0.2,
    )
    if isinstance(result, dict):
        # Some models may wrap in {"endpoints": [...]} despite instruction
        if "endpoints" in result and isinstance(result["endpoints"], list):
            result = result["endpoints"]
        else:
            result = [result]
    if not isinstance(result, list):
        return []
    return _normalize(result)

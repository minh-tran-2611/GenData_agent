# Data Generator Agent

Tool sinh data thực tế cho doanh nghiệp dùng kiến trúc multi-agent. Orchestrator phân tích loại hình doanh nghiệp + sản phẩm/voucher hiện có → đề xuất các tệp khách hàng. Mỗi tệp là một Segment Agent tự quyết định mỗi ngày tạo bao nhiêu user mới, bao nhiêu đơn, dùng voucher gì, rồi gọi thẳng API của bạn.

## Kiến trúc

```
[Frontend (React + Vite)]
        ↓ HTTP
[Backend (FastAPI)]
   ├── Sync phase   → gọi GET endpoint của bạn → snapshot + diff
   ├── Orchestrator → Claude → đề xuất segments
   ├── Segment Agent (mỗi tệp 1 con) → Claude → action plan
   └── Executor     → gọi POST endpoint (createUser/createOrder/…)
        ↓
[memory.json] (file duy nhất lưu tất cả: business, endpoints, snapshot, segments, logs)
```

## Yêu cầu

- Python 3.10+
- Node.js 18+
- Gemini (Vertex AI): app hard-code dùng `backend/vertex-sa.json` (project `smiling-foundry-477815-s7`, `us-central1`, `gemini-2.5-flash`). Không cần API key — chỉ cần đặt đúng file service account.

## Cài đặt

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend

```powershell
cd frontend
npm install
```

## Chạy

Mở 2 terminal:

**Terminal 1 — backend:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8200
```

**Terminal 2 — frontend:**
```powershell
cd frontend
npm run dev
```

Mở http://localhost:5273

## Luồng sử dụng

1. **Tab 1. Settings** — LLM đã hard-code (Gemini Vertex AI), không cần nhập gì. Chỉ chọn **Output**: `API` (gọi BE thật) hoặc `SQL file`.
2. **Tab 2. Business** — nhập thông tin doanh nghiệp (tên, loại hình, mô tả, base URL của API).
3. **Tab 3. Endpoints** — khai báo các endpoint của bạn:
   - GET endpoints (`list_products`, `list_vouchers`, `get_config`...) — agent dùng để biết inventory.
   - POST endpoints (`create_user`, `create_order`, `apply_voucher`) — agent gọi để tạo data.
   - Mỗi endpoint nên có **body_schema mẫu** (JSON) để agent format đúng field name.
4. **Tab 4. Sync & Run**:
   - Bấm **Sync now** → backend gọi tất cả GET endpoint, lưu snapshot + diff với lần trước.
   - Bấm **Re-generate segments** (lần đầu hoặc khi muốn tạo lại) → Orchestrator phân tích và đề xuất tệp khách hàng.
   - Nhập số ngày → **Run** → Segment agents chạy lần lượt, gọi API thật.
5. **Tab 5. Segments** — xem các tệp đã sinh + thống kê hôm qua.
6. **Tab 6. Logs** — xem từng action của agent (sync, plan, create_user, create_order).
7. **Tab 7. Memory** — xem raw `memory.json`.

## Marker đặc biệt trong body

Trong `body` của action `create_order`, agent có thể dùng marker `{{LAST_CREATED_USER}}` để reference user vừa tạo trong cùng segment (executor sẽ thay bằng userId thực tế).

## Cấu trúc file

```
.
├── backend/
│   ├── data/memory.json     # toàn bộ state
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic schemas
│   ├── memory.py            # đọc/ghi memory.json
│   ├── api_client.py        # HTTP client gọi API doanh nghiệp
│   ├── sync.py              # Sync phase
│   ├── orchestrator.py      # Orchestrator agent (Claude)
│   ├── segment_agent.py     # Segment agent (Claude)
│   ├── simulator.py         # vòng lặp simulate N ngày
│   ├── llm.py               # wrapper Anthropic SDK + parse JSON
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   └── components/      # 7 tabs
    ├── package.json
    └── vite.config.js
```

## Chi phí & lưu ý

- Số lần gọi LLM = `ceil(days / step) × (N segments)`, với `step` = 1 (day) / 30 (month) / 365 (year). Mặc định provider Gemini (Vertex AI); có thể đổi sang OpenAI / Anthropic trong Settings.
- Mode `day`: 1 lần gọi/segment/ngày — chi tiết & liên tục nhất nhưng tốn API call nhất.
- Mode `month`: 1 lần gọi/segment cho mỗi 30 ngày — agent lập kế hoạch cả tháng, mỗi action gắn `day_offset` để trải qua các ngày; rẻ hơn nhưng kém liên tục.
- Mode `year`: 1 lần gọi/segment cho mỗi 365 ngày — rẻ nhất, kém liên tục nhất.
- API doanh nghiệp của bạn phải đang chạy được khi sync/run, nếu không executor sẽ ghi log error.
- Memory chỉ ở local — backup `backend/data/memory.json` nếu muốn giữ.

## Reset

- **Reset simulation** (tab 4): xóa segments + logs + counters, giữ business + endpoints + settings.
- **Wipe all memory** (tab 1): xóa sạch.

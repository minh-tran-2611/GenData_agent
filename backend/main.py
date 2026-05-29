import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import (
    Memory,
    BusinessConfig,
    GrowthConfig,
    EndpointConfig,
    SimulateRequest,
    SimulateResult,
    SyncResult,
)
from memory import load_memory, save_memory, reset_simulation, DATA_DIR
from sync import run_sync
from simulator import simulate
from orchestrator import generate_segments
from endpoint_parser import parse_endpoints_from_text


app = FastAPI(title="Data Generator Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


SA_FILE = DATA_DIR / "vertex_sa.json"

# ── Hard-coded LLM: the app always uses Gemini (Vertex AI) ──────────────────
# Matches the AiAgent-service Vertex setup (same GCP project). The private key
# lives in backend/vertex-sa.json (gitignored) — only the path/ids are in source.
VERTEX_SA_PATH = str(Path(__file__).parent / "vertex-sa.json")
VERTEX_PROJECT_ID = "smiling-foundry-477815-s7"
VERTEX_LOCATION = "us-central1"
VERTEX_MODEL = "gemini-2.5-flash"


def _bundled_vertex_sa() -> str | None:
    """Path to the bundled Vertex service account, if present (no UI upload needed)."""
    if Path(VERTEX_SA_PATH).exists():
        return VERTEX_SA_PATH
    if SA_FILE.exists():
        return str(SA_FILE)
    return None


def _llm_config(memory: Memory) -> dict:
    """Resolve the active LLM provider config.

    Gemini (Vertex AI) is wired to the bundled service account so it works with no
    setup. OpenAI / Anthropic still require an API key entered in Settings.
    """
    s = memory.settings or {}
    legacy_key = s.get("anthropic_api_key") or ""
    provider = s.get("provider") or "gemini_vertex"

    if provider == "gemini_vertex":
        cfg = dict(s.get("gemini_vertex") or {})
        sa_path = cfg.get("service_account_path")
        if not sa_path or not Path(sa_path).exists():
            sa_path = _bundled_vertex_sa()
        if not sa_path:
            raise HTTPException(
                400,
                f"Không tìm thấy service account Vertex AI. Đặt file tại {VERTEX_SA_PATH} hoặc dán JSON trong Settings.",
            )
        return {
            "provider": "gemini_vertex",
            "service_account_path": sa_path,
            "project_id": cfg.get("project_id") or VERTEX_PROJECT_ID,
            "location": cfg.get("location") or VERTEX_LOCATION,
            "model": cfg.get("model") or VERTEX_MODEL,
        }

    if provider == "openai":
        cfg = dict(s.get("openai") or {})
        if not cfg.get("api_key"):
            raise HTTPException(400, "Chưa cấu hình OpenAI API key (Settings).")
        cfg.setdefault("model", "gpt-4o")
        return {"provider": provider, **cfg}

    if provider == "anthropic":
        cfg = dict(s.get("anthropic") or {})
        key = cfg.get("api_key") or legacy_key
        if not key:
            raise HTTPException(400, "Chưa cấu hình Anthropic API key (Settings).")
        cfg["api_key"] = key
        cfg.setdefault("model", "claude-sonnet-4-6")
        return {"provider": provider, **cfg}

    raise HTTPException(400, f"Provider không hợp lệ: {provider}")


class SettingsPayload(BaseModel):
    provider: str | None = None
    gemini_vertex: dict[str, Any] | None = None
    openai: dict[str, Any] | None = None
    anthropic: dict[str, Any] | None = None
    # legacy single-key field (kept for backward compatibility)
    anthropic_api_key: str | None = None
    # output sink
    output_mode: str | None = None  # "api" | "sql"
    sql: dict[str, Any] | None = None


def _key_preview(key: str) -> str:
    return (key[:7] + "..." + key[-4:]) if len(key) > 12 else ("•" * len(key) if key else "")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/memory")
def get_memory():
    return load_memory().model_dump()


@app.post("/api/memory/reset")
def reset_memory():
    """Reset simulation state only (keep business + endpoints + settings)."""
    mem = load_memory()
    reset_simulation(mem)
    save_memory(mem)
    return mem.model_dump()


@app.post("/api/memory/wipe")
def wipe_memory():
    """Wipe everything."""
    mem = Memory()
    save_memory(mem)
    return mem.model_dump()


@app.get("/api/settings")
def get_settings():
    mem = load_memory()
    s = mem.settings or {}
    legacy_key = s.get("anthropic_api_key") or ""
    gv = s.get("gemini_vertex") or {}
    oa = s.get("openai") or {}
    an = s.get("anthropic") or {}
    anthropic_key = an.get("api_key") or legacy_key
    sql = s.get("sql") or {}
    bundled = _bundled_vertex_sa() is not None
    return {
        "provider": s.get("provider") or "gemini_vertex",
        "gemini_vertex": {
            # Bundled service account means Vertex works with no UI upload.
            "configured": bundled or bool(gv.get("service_account_path") and gv.get("project_id")),
            "bundled": bundled,
            "project_id": gv.get("project_id") or VERTEX_PROJECT_ID,
            "location": gv.get("location") or VERTEX_LOCATION,
            "model": gv.get("model") or VERTEX_MODEL,
        },
        "openai": {
            "configured": bool(oa.get("api_key")),
            "key_preview": _key_preview(oa.get("api_key", "")),
            "model": oa.get("model", "gpt-4o"),
        },
        "anthropic": {
            "configured": bool(anthropic_key),
            "key_preview": _key_preview(anthropic_key),
            "model": an.get("model", "claude-sonnet-4-6"),
        },
        "output_mode": s.get("output_mode") or "api",
        "sql": {
            "file_path": sql.get("file_path", ""),
            "start_date": sql.get("start_date", ""),
            "id_base": sql.get("id_base", 100000),
            "shipping_fee": sql.get("shipping_fee", 0),
            "vat_rate": sql.get("vat_rate", 0),
            "seed_password": "Simulated@123",
        },
    }


@app.post("/api/settings")
def set_settings(payload: SettingsPayload):
    mem = load_memory()
    s = mem.settings

    if payload.provider is not None:
        if payload.provider not in ("gemini_vertex", "openai", "anthropic"):
            raise HTTPException(400, f"Provider không hợp lệ: {payload.provider}")
        s["provider"] = payload.provider

    if payload.gemini_vertex is not None:
        gv = dict(s.get("gemini_vertex") or {})
        incoming = payload.gemini_vertex
        sa_json = incoming.get("service_account_json")
        if sa_json:
            try:
                info = json.loads(sa_json) if isinstance(sa_json, str) else sa_json
            except json.JSONDecodeError:
                raise HTTPException(400, "Service account JSON không hợp lệ.")
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            SA_FILE.write_text(json.dumps(info), encoding="utf-8")
            gv["service_account_path"] = str(SA_FILE)
            if not incoming.get("project_id") and info.get("project_id"):
                gv["project_id"] = info["project_id"]
        for field in ("project_id", "location", "model"):
            if incoming.get(field):
                gv[field] = incoming[field]
        s["gemini_vertex"] = gv

    if payload.openai is not None:
        oa = dict(s.get("openai") or {})
        if payload.openai.get("api_key") is not None:
            oa["api_key"] = (payload.openai["api_key"] or "").strip()
        if payload.openai.get("model"):
            oa["model"] = payload.openai["model"]
        s["openai"] = oa

    if payload.anthropic is not None:
        an = dict(s.get("anthropic") or {})
        if payload.anthropic.get("api_key") is not None:
            an["api_key"] = (payload.anthropic["api_key"] or "").strip()
        if payload.anthropic.get("model"):
            an["model"] = payload.anthropic["model"]
        s["anthropic"] = an

    if payload.anthropic_api_key is not None:
        s["anthropic_api_key"] = payload.anthropic_api_key.strip()

    if payload.output_mode is not None:
        if payload.output_mode not in ("api", "sql"):
            raise HTTPException(400, f"output_mode không hợp lệ: {payload.output_mode}")
        s["output_mode"] = payload.output_mode

    if payload.sql is not None:
        sql = dict(s.get("sql") or {})
        for field in ("file_path", "start_date"):
            if payload.sql.get(field) is not None:
                sql[field] = str(payload.sql[field]).strip()
        for field in ("id_base", "shipping_fee", "vat_rate"):
            if payload.sql.get(field) is not None:
                sql[field] = payload.sql[field]
        s["sql"] = sql

    save_memory(mem)
    return {"ok": True}


@app.get("/api/business")
def get_business():
    return load_memory().business.model_dump()


@app.post("/api/business")
def set_business(payload: BusinessConfig):
    mem = load_memory()
    mem.business = payload
    save_memory(mem)
    return mem.business.model_dump()


@app.get("/api/growth")
def get_growth():
    return load_memory().growth.model_dump()


@app.post("/api/growth")
def set_growth(payload: GrowthConfig):
    mem = load_memory()
    mem.growth = payload
    save_memory(mem)
    return mem.growth.model_dump()


@app.get("/api/endpoints")
def list_endpoints():
    return [e.model_dump() for e in load_memory().endpoints]


class EndpointPayload(BaseModel):
    name: str
    method: str
    url: str
    purpose: str
    headers: dict[str, str] = {}
    description: str = ""
    body_schema: dict[str, Any] | None = None
    query_params: dict[str, str] = {}


@app.post("/api/endpoints")
def add_endpoint(payload: EndpointPayload):
    mem = load_memory()
    ep = EndpointConfig(id=str(uuid4())[:8], **payload.model_dump())
    mem.endpoints.append(ep)
    save_memory(mem)
    return ep.model_dump()


@app.put("/api/endpoints/{endpoint_id}")
def update_endpoint(endpoint_id: str, payload: EndpointPayload):
    mem = load_memory()
    for i, ep in enumerate(mem.endpoints):
        if ep.id == endpoint_id:
            mem.endpoints[i] = EndpointConfig(id=endpoint_id, **payload.model_dump())
            save_memory(mem)
            return mem.endpoints[i].model_dump()
    raise HTTPException(404, "Endpoint not found")


class ParseTextPayload(BaseModel):
    text: str


@app.post("/api/endpoints/parse")
def parse_endpoints(payload: ParseTextPayload):
    """Parse raw text into endpoint dicts via LLM. Does NOT save — returns preview."""
    mem = load_memory()
    llm = _llm_config(mem)
    if not payload.text or not payload.text.strip():
        raise HTTPException(400, "text rỗng")
    try:
        parsed = parse_endpoints_from_text(payload.text, llm)
    except Exception as e:
        raise HTTPException(500, f"Parse failed: {e}")
    return {"count": len(parsed), "endpoints": parsed}


class BulkEndpointsPayload(BaseModel):
    endpoints: list[EndpointPayload]
    replace_all: bool = False


@app.post("/api/endpoints/bulk")
def bulk_save_endpoints(payload: BulkEndpointsPayload):
    """Save multiple endpoints at once. If replace_all=True, wipe existing first."""
    mem = load_memory()
    if payload.replace_all:
        mem.endpoints = []
    added: list[dict[str, Any]] = []
    for ep_payload in payload.endpoints:
        ep = EndpointConfig(id=str(uuid4())[:8], **ep_payload.model_dump())
        mem.endpoints.append(ep)
        added.append(ep.model_dump())
    save_memory(mem)
    return {"added": added, "total": len(mem.endpoints)}


@app.delete("/api/endpoints/{endpoint_id}")
def delete_endpoint(endpoint_id: str):
    mem = load_memory()
    before = len(mem.endpoints)
    mem.endpoints = [e for e in mem.endpoints if e.id != endpoint_id]
    if len(mem.endpoints) == before:
        raise HTTPException(404, "Endpoint not found")
    save_memory(mem)
    return {"ok": True}


@app.post("/api/sync", response_model=SyncResult)
def sync_now():
    mem = load_memory()
    result = run_sync(mem)
    save_memory(mem)
    return result


@app.post("/api/segments/regenerate")
def regenerate_segments():
    mem = load_memory()
    llm = _llm_config(mem)
    segments = generate_segments(mem, llm)
    mem.simulation.segments = segments
    save_memory(mem)
    return [s.model_dump() for s in segments]


@app.get("/api/segments")
def get_segments():
    return [s.model_dump() for s in load_memory().simulation.segments]


@app.post("/api/simulate", response_model=SimulateResult)
def simulate_days(payload: SimulateRequest):
    mem = load_memory()
    llm = _llm_config(mem)
    if payload.days < 1 or payload.days > 365:
        raise HTTPException(400, "days must be between 1 and 365")
    mem.growth.mode = payload.mode
    save_memory(mem)
    result = simulate(mem, payload.days, llm)
    return result


@app.get("/api/logs")
def get_logs(limit: int = 200, offset: int = 0):
    mem = load_memory()
    logs = mem.logs
    total = len(logs)
    # newest first
    sliced = list(reversed(logs))[offset: offset + limit]
    return {"total": total, "logs": [l.model_dump() for l in sliced]}


@app.get("/")
def root():
    return {"name": "Data Generator Agent", "docs": "/docs"}


# Default port 8200 (frontend vite proxy points here). Avoids clashing with
# AiAgent-service (8000). Run with: `python main.py`.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8200, reload=True)

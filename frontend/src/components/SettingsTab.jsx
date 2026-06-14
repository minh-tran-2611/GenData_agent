import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const PROVIDERS = [
  { id: "gemini_vertex", label: "Gemini (Vertex AI)" },
  { id: "openai", label: "OpenAI (GPT)" },
  { id: "anthropic", label: "Anthropic (Claude)" },
];

const emptyInfo = {
  provider: "gemini_vertex",
  gemini_vertex: { configured: false, bundled: false, project_id: "", location: "us-central1", model: "gemini-2.5-flash" },
  openai: { configured: false, key_preview: "", model: "gpt-4o" },
  anthropic: { configured: false, key_preview: "", model: "claude-sonnet-4-6" },
  output_mode: "api",
  sql: { file_path: "", start_date: "", id_base: 100000, shipping_fee: 0, vat_rate: 0, seed_password: "Simulated@123" },
};

function StatusBadge({ configured }) {
  return configured ? (
    <span className="badge bg-emerald-900 text-emerald-300">đã cấu hình</span>
  ) : (
    <span className="badge bg-rose-900 text-rose-300">chưa cấu hình</span>
  );
}

export default function SettingsTab() {
  const [info, setInfo] = useState(emptyInfo);
  const [provider, setProvider] = useState("gemini_vertex");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  // editable fields
  const [saJson, setSaJson] = useState("");
  const [gvProject, setGvProject] = useState("");
  const [gvLocation, setGvLocation] = useState("us-central1");
  const [gvModel, setGvModel] = useState("gemini-2.5-flash");
  const [openaiKey, setOpenaiKey] = useState("");
  const [openaiModel, setOpenaiModel] = useState("gpt-4o");
  const [anthropicKey, setAnthropicKey] = useState("");
  const [anthropicModel, setAnthropicModel] = useState("claude-sonnet-4-6");

  // output sink
  const [outputMode, setOutputMode] = useState("api");
  const [sqlFilePath, setSqlFilePath] = useState("");
  const [sqlStartDate, setSqlStartDate] = useState("");
  const [sqlShipping, setSqlShipping] = useState(0);
  const [sqlVat, setSqlVat] = useState(0);

  const load = async () => {
    try {
      const data = await api.getSettings();
      setInfo(data);
      setProvider(data.provider || "gemini_vertex");
      setGvProject(data.gemini_vertex?.project_id || "");
      setGvLocation(data.gemini_vertex?.location || "us-central1");
      setGvModel(data.gemini_vertex?.model || "gemini-2.5-flash");
      setOpenaiModel(data.openai?.model || "gpt-4o");
      setAnthropicModel(data.anthropic?.model || "claude-sonnet-4-6");
      setOutputMode(data.output_mode || "api");
      setSqlFilePath(data.sql?.file_path || "");
      setSqlStartDate(data.sql?.start_date || "");
      setSqlShipping(data.sql?.shipping_fee ?? 0);
      setSqlVat(data.sql?.vat_rate ?? 0);
    } catch (e) {
      setMsg(e.message);
    }
  };
  useEffect(() => { load(); }, []);

  const save = async () => {
    setSaving(true); setMsg("");
    try {
      const payload = { provider };
      if (provider === "gemini_vertex") {
        payload.gemini_vertex = { location: gvLocation, model: gvModel };
        if (saJson.trim()) payload.gemini_vertex.service_account_json = saJson.trim();
        if (gvProject.trim()) payload.gemini_vertex.project_id = gvProject.trim();
      } else if (provider === "openai") {
        payload.openai = { model: openaiModel };
        if (openaiKey.trim()) payload.openai.api_key = openaiKey.trim();
      } else if (provider === "anthropic") {
        payload.anthropic = { model: anthropicModel };
        if (anthropicKey.trim()) payload.anthropic.api_key = anthropicKey.trim();
      }
      payload.output_mode = outputMode;
      payload.sql = {
        file_path: sqlFilePath.trim(),
        start_date: sqlStartDate.trim(),
        shipping_fee: Number(sqlShipping) || 0,
        vat_rate: Number(sqlVat) || 0,
      };
      await api.setSettings(payload);
      setSaJson(""); setOpenaiKey(""); setAnthropicKey("");
      await load();
      setMsg("Đã lưu cấu hình.");
    } catch (e) {
      setMsg(e.message);
    } finally { setSaving(false); }
  };

  const wipe = async () => {
    if (!confirm("Xóa TOÀN BỘ memory (bao gồm business, endpoints, settings)? Không thể hoàn tác.")) return;
    await api.wipeMemory();
    await load();
    setMsg("Đã wipe memory.");
  };

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="card">
        <h2 className="text-lg font-semibold mb-2">Nhà cung cấp LLM</h2>
        <p className="text-xs text-slate-400 mb-3">
          Chọn provider để chạy Orchestrator + Segment Agent. Cấu hình lưu trong <code>memory.json</code> ở máy bạn (không gửi đi đâu).
        </p>

        <div className="flex gap-2 mb-4">
          {PROVIDERS.map((p) => (
            <button
              key={p.id}
              onClick={() => setProvider(p.id)}
              className={`btn ${provider === p.id ? "ring-2 ring-emerald-500" : "opacity-70"}`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {provider === "gemini_vertex" && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-slate-400">Trạng thái:</span>
              <StatusBadge configured={info.gemini_vertex?.configured} />
              {info.gemini_vertex?.bundled && (
                <span className="badge bg-sky-900 text-sky-300">service account gắn sẵn</span>
              )}
            </div>
            {info.gemini_vertex?.bundled ? (
              <p className="text-xs text-emerald-400/80">
                Đã có sẵn service account ở <code>backend/vertex-sa.json</code> — chọn Vertex là chạy được ngay, không cần dán JSON.
                Các ô dưới chỉ để <b>ghi đè</b> nếu muốn dùng project/model khác.
              </p>
            ) : (
              <p className="text-xs text-emerald-400/80">
                Đang dùng <b>ADC</b> — chạy <code>gcloud auth application-default login</code> một lần là Vertex chạy được, <b>không cần</b> dán JSON.
                Ô JSON bên dưới chỉ để ghi đè nếu muốn dùng service account khác.
              </p>
            )}
            <label className="block text-xs text-slate-400">Service account JSON (tuỳ chọn — dán nếu muốn dùng SA khác)</label>
            <textarea
              className="input h-28 font-mono text-xs"
              placeholder={info.gemini_vertex?.bundled ? "(đang dùng SA gắn sẵn — để trống)" : '{\n  "type": "service_account",\n  ...\n}'}
              value={saJson}
              onChange={(e) => setSaJson(e.target.value)}
            />
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-slate-400">Project ID (để trống = mặc định gắn sẵn)</label>
                <input className="input" value={gvProject} onChange={(e) => setGvProject(e.target.value)} placeholder={info.gemini_vertex?.project_id || "smiling-foundry-477815-s7"} />
              </div>
              <div>
                <label className="block text-xs text-slate-400">Location</label>
                <input className="input" value={gvLocation} onChange={(e) => setGvLocation(e.target.value)} placeholder="us-central1" />
              </div>
            </div>
            <div>
              <label className="block text-xs text-slate-400">Model</label>
              <input className="input" value={gvModel} onChange={(e) => setGvModel(e.target.value)} placeholder="gemini-2.5-flash" />
            </div>
          </div>
        )}

        {provider === "openai" && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-slate-400">Trạng thái:</span>
              <StatusBadge configured={info.openai?.configured} />
              {info.openai?.key_preview && <span className="text-xs text-slate-500">({info.openai.key_preview})</span>}
            </div>
            <label className="block text-xs text-slate-400">OpenAI API Key</label>
            <input type="password" className="input" placeholder="sk-..." value={openaiKey} onChange={(e) => setOpenaiKey(e.target.value)} />
            <label className="block text-xs text-slate-400">Model</label>
            <input className="input" value={openaiModel} onChange={(e) => setOpenaiModel(e.target.value)} placeholder="gpt-4o" />
          </div>
        )}

        {provider === "anthropic" && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-slate-400">Trạng thái:</span>
              <StatusBadge configured={info.anthropic?.configured} />
              {info.anthropic?.key_preview && <span className="text-xs text-slate-500">({info.anthropic.key_preview})</span>}
            </div>
            <label className="block text-xs text-slate-400">Anthropic API Key</label>
            <input type="password" className="input" placeholder="sk-ant-..." value={anthropicKey} onChange={(e) => setAnthropicKey(e.target.value)} />
            <label className="block text-xs text-slate-400">Model</label>
            <input className="input" value={anthropicModel} onChange={(e) => setAnthropicModel(e.target.value)} placeholder="claude-sonnet-4-6" />
          </div>
        )}

        <div className="mt-4">
          <button className="btn-primary" onClick={save} disabled={saving}>
            {saving ? "Đang lưu..." : "Lưu"}
          </button>
        </div>
        {msg && <div className="text-xs mt-2 text-slate-400">{msg}</div>}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-2">Nơi ghi dữ liệu (Output)</h2>
        <p className="text-xs text-slate-400 mb-3">
          <b>API</b>: gọi thẳng endpoint write của doanh nghiệp. <b>SQL file</b>: không gọi API, sinh câu lệnh <code>INSERT</code> nối vào file .sql (né OTP + giỏ hàng).
        </p>
        <div className="flex gap-2 mb-3">
          {[
            { id: "api", label: "API (gọi endpoint)" },
            { id: "sql", label: "SQL file" },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => setOutputMode(m.id)}
              className={`btn ${outputMode === m.id ? "ring-2 ring-emerald-500" : "opacity-70"}`}
            >
              {m.label}
            </button>
          ))}
        </div>

        {outputMode === "sql" && (
          <div className="space-y-2">
            <div>
              <label className="block text-xs text-slate-400">Đường dẫn file SQL (để trống = <code>Siupo Restaurant.sql</code> ở thư mục gốc)</label>
              <input className="input" value={sqlFilePath} onChange={(e) => setSqlFilePath(e.target.value)} placeholder="C:\...\Siupo Restaurant.sql" />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-xs text-slate-400">Ngày bắt đầu (ngày 1)</label>
                <input className="input" type="date" value={sqlStartDate} onChange={(e) => setSqlStartDate(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs text-slate-400">Phí ship/đơn</label>
                <input className="input" type="number" value={sqlShipping} onChange={(e) => setSqlShipping(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs text-slate-400">VAT (vd 0.08)</label>
                <input className="input" type="number" step="0.01" value={sqlVat} onChange={(e) => setSqlVat(e.target.value)} />
              </div>
            </div>
            <p className="text-xs text-slate-500">
              ID khách/đơn cấp tường minh từ 100000; mật khẩu seed: <code>Simulated@123</code>; mỗi ngày là 1 block bọc <code>FOREIGN_KEY_CHECKS</code>. Nhấn <b>Lưu</b> để áp dụng.
            </p>
          </div>
        )}
        <div className="mt-3">
          <button className="btn-primary" onClick={save} disabled={saving}>
            {saving ? "Đang lưu..." : "Lưu"}
          </button>
        </div>
      </div>

      <div className="card border-rose-800">
        <h2 className="text-lg font-semibold mb-2 text-rose-400">Danger zone</h2>
        <p className="text-xs text-slate-400 mb-3">Xóa toàn bộ memory (business + endpoints + simulation + logs + settings).</p>
        <button className="btn-danger" onClick={wipe}>Wipe all memory</button>
      </div>
    </div>
  );
}

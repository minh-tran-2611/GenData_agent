import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const PURPOSES = [
  { value: "list_products", label: "list_products (GET sản phẩm)" },
  { value: "list_vouchers", label: "list_vouchers (GET voucher)" },
  { value: "list_categories", label: "list_categories (GET danh mục)" },
  { value: "list_combos", label: "list_combos (GET combo/bundle)" },
  { value: "get_config", label: "get_config (GET cấu hình/chính sách)" },
  { value: "other_read", label: "other_read (GET khác)" },
  { value: "create_user", label: "create_user (POST tạo user)" },
  { value: "create_order", label: "create_order (POST tạo đơn)" },
  { value: "apply_voucher", label: "apply_voucher (POST áp voucher)" },
  { value: "other_write", label: "other_write (POST/PUT khác)" },
];

const BLANK = {
  name: "", method: "GET", url: "", purpose: "list_products",
  headers: "", description: "", body_schema: "", query_params: "",
};

function parseKV(text) {
  const out = {};
  if (!text || !text.trim()) return out;
  for (const line of text.split("\n")) {
    const i = line.indexOf(":");
    if (i === -1) continue;
    const k = line.slice(0, i).trim();
    const v = line.slice(i + 1).trim();
    if (k) out[k] = v;
  }
  return out;
}

function dumpKV(obj) {
  if (!obj) return "";
  return Object.entries(obj).map(([k, v]) => `${k}: ${v}`).join("\n");
}

export default function EndpointsTab() {
  const [list, setList] = useState([]);
  const [form, setForm] = useState(BLANK);
  const [editId, setEditId] = useState(null);
  const [msg, setMsg] = useState("");

  // bulk import state
  const [rawText, setRawText] = useState("");
  const [parsing, setParsing] = useState(false);
  const [preview, setPreview] = useState([]); // array of parsed endpoint dicts
  const [previewSelected, setPreviewSelected] = useState({}); // index -> bool
  const [replaceAll, setReplaceAll] = useState(false);
  const [importMsg, setImportMsg] = useState("");

  const load = async () => {
    try { setList(await api.listEndpoints()); }
    catch (e) { setMsg(e.message); }
  };
  useEffect(() => { load(); }, []);

  const f = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const startEdit = (ep) => {
    setEditId(ep.id);
    setForm({
      name: ep.name, method: ep.method, url: ep.url, purpose: ep.purpose,
      headers: dumpKV(ep.headers),
      description: ep.description || "",
      body_schema: ep.body_schema ? JSON.stringify(ep.body_schema, null, 2) : "",
      query_params: dumpKV(ep.query_params),
    });
  };

  const reset = () => { setEditId(null); setForm(BLANK); };

  const save = async () => {
    setMsg("");
    let body_schema = null;
    if (form.body_schema.trim()) {
      try { body_schema = JSON.parse(form.body_schema); }
      catch (e) { setMsg("body_schema không phải JSON hợp lệ"); return; }
    }
    const payload = {
      name: form.name, method: form.method, url: form.url, purpose: form.purpose,
      headers: parseKV(form.headers),
      description: form.description,
      body_schema,
      query_params: parseKV(form.query_params),
    };
    try {
      if (editId) await api.updateEndpoint(editId, payload);
      else await api.addEndpoint(payload);
      reset();
      await load();
      setMsg("Đã lưu endpoint.");
    } catch (e) { setMsg(e.message); }
  };

  const del = async (id) => {
    if (!confirm("Xóa endpoint này?")) return;
    await api.deleteEndpoint(id);
    if (editId === id) reset();
    await load();
  };

  // ---- BULK IMPORT ----
  const doParse = async () => {
    setImportMsg(""); setPreview([]); setPreviewSelected({});
    if (!rawText.trim()) { setImportMsg("Nhập text trước."); return; }
    setParsing(true);
    try {
      const r = await api.parseEndpointsText(rawText);
      setPreview(r.endpoints || []);
      const sel = {};
      (r.endpoints || []).forEach((_, i) => { sel[i] = true; });
      setPreviewSelected(sel);
      setImportMsg(`Agent tìm được ${r.count} endpoint. Review rồi bấm "Save selected".`);
    } catch (e) {
      setImportMsg(`Parse error: ${e.message}`);
    } finally {
      setParsing(false);
    }
  };

  const updatePreviewItem = (i, key, value) => {
    const next = [...preview];
    next[i] = { ...next[i], [key]: value };
    setPreview(next);
  };

  const removePreview = (i) => {
    const next = preview.filter((_, idx) => idx !== i);
    setPreview(next);
    const sel = {};
    next.forEach((_, idx) => { sel[idx] = previewSelected[idx < i ? idx : idx + 1] ?? true; });
    setPreviewSelected(sel);
  };

  const saveSelected = async () => {
    setImportMsg("");
    const chosen = preview.filter((_, i) => previewSelected[i]);
    if (chosen.length === 0) { setImportMsg("Chưa chọn endpoint nào."); return; }
    if (replaceAll && !confirm("Replace ALL endpoints hiện tại bằng list này?")) return;
    try {
      const r = await api.bulkSaveEndpoints(chosen, replaceAll);
      setImportMsg(`Đã lưu ${r.added.length} endpoint. Tổng hiện tại: ${r.total}.`);
      setPreview([]); setPreviewSelected({}); setRawText("");
      await load();
    } catch (e) {
      setImportMsg(`Save error: ${e.message}`);
    }
  };

  return (
    <div className="space-y-4">
      {/* BULK IMPORT */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-2">Bulk import (paste text → agent parse)</h2>
        <p className="text-xs text-slate-400 mb-3">
          Dán cURL, Postman collection, swagger snippet, hoặc mô tả tay. Agent sẽ tự nhận diện method/URL/purpose/headers/body schema rồi cho bạn preview trước khi save.
        </p>
        <textarea
          className="input font-mono text-xs"
          rows="8"
          placeholder={`Ví dụ:\ncurl -X POST https://api.shop.com/orders \\\n  -H "Authorization: Bearer xxx" \\\n  -d '{"userId":"u1","items":[{"productId":"p1","qty":2}],"totalAmount":50000}'\n\nGET /api/products?limit=100\nGET /api/vouchers\nPOST /api/users  body: {"name":"string","phone":"string"}`}
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
        />
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          <button className="btn-primary" onClick={doParse} disabled={parsing || !rawText.trim()}>
            {parsing ? "Đang parse..." : "Parse with agent"}
          </button>
          <label className="text-xs text-slate-400 flex items-center gap-1">
            <input type="checkbox" checked={replaceAll} onChange={e => setReplaceAll(e.target.checked)} />
            Replace ALL existing endpoints khi save
          </label>
          {importMsg && <span className="text-xs text-slate-400">{importMsg}</span>}
        </div>

        {preview.length > 0 && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold">Preview ({preview.length})</h3>
              <button className="btn text-xs" onClick={() => {
                const allSel = Object.values(previewSelected).every(Boolean);
                const next = {};
                preview.forEach((_, i) => { next[i] = !allSel; });
                setPreviewSelected(next);
              }}>Toggle all</button>
              <button className="btn-primary ml-auto" onClick={saveSelected}>Save selected</button>
            </div>
            <div className="space-y-2 max-h-[50vh] overflow-y-auto pr-1">
              {preview.map((ep, i) => (
                <div key={i} className={`border rounded p-2 text-xs ${previewSelected[i] ? "border-emerald-700 bg-emerald-950/20" : "border-slate-700"}`}>
                  <div className="flex items-center gap-2 flex-wrap">
                    <input
                      type="checkbox"
                      checked={!!previewSelected[i]}
                      onChange={e => setPreviewSelected({ ...previewSelected, [i]: e.target.checked })}
                    />
                    <select
                      className="input w-24 text-xs"
                      value={ep.method}
                      onChange={e => updatePreviewItem(i, "method", e.target.value)}
                    >
                      {["GET","POST","PUT","PATCH","DELETE"].map(m => <option key={m} value={m}>{m}</option>)}
                    </select>
                    <input
                      className="input flex-1 font-mono text-xs"
                      value={ep.url}
                      onChange={e => updatePreviewItem(i, "url", e.target.value)}
                    />
                    <select
                      className="input w-44 text-xs"
                      value={ep.purpose}
                      onChange={e => updatePreviewItem(i, "purpose", e.target.value)}
                    >
                      {PURPOSES.map(p => <option key={p.value} value={p.value}>{p.value}</option>)}
                    </select>
                    <button className="btn-danger text-xs" onClick={() => removePreview(i)}>X</button>
                  </div>
                  <div className="mt-1">
                    <input
                      className="input text-xs"
                      placeholder="name"
                      value={ep.name}
                      onChange={e => updatePreviewItem(i, "name", e.target.value)}
                    />
                  </div>
                  <div className="mt-1">
                    <input
                      className="input text-xs"
                      placeholder="description"
                      value={ep.description || ""}
                      onChange={e => updatePreviewItem(i, "description", e.target.value)}
                    />
                  </div>
                  {(Object.keys(ep.headers || {}).length > 0 || ep.body_schema) && (
                    <details className="mt-1 text-slate-400">
                      <summary className="cursor-pointer text-xs">chi tiết (headers / body_schema)</summary>
                      <pre className="bg-slate-900 p-2 rounded mt-1 overflow-x-auto">{JSON.stringify({ headers: ep.headers, query_params: ep.query_params, body_schema: ep.body_schema }, null, 2)}</pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* MANUAL CRUD */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="text-lg font-semibold mb-3">{editId ? "Sửa endpoint" : "Thêm thủ công"}</h2>
          <div className="grid grid-cols-1 gap-3">
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="label">Method</label>
                <select className="input" value={form.method} onChange={f("method")}>
                  {["GET","POST","PUT","PATCH","DELETE"].map(m=> <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
              <div className="col-span-2">
                <label className="label">Tên (gợi nhớ)</label>
                <input className="input" value={form.name} onChange={f("name")} placeholder="getAllProducts" />
              </div>
            </div>
            <div>
              <label className="label">URL (đầy đủ hoặc bắt đầu bằng / để dùng base_url)</label>
              <input className="input" value={form.url} onChange={f("url")} placeholder="/api/products hoặc https://..." />
            </div>
            <div>
              <label className="label">Purpose (agent dùng cái này để chọn)</label>
              <select className="input" value={form.purpose} onChange={f("purpose")}>
                {PURPOSES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Mô tả (cho agent hiểu)</label>
              <textarea className="input" rows="2" value={form.description} onChange={f("description")} placeholder="Tạo 1 đơn hàng với userId, productId, quantity..." />
            </div>
            <div>
              <label className="label">Headers (mỗi dòng: Key: Value)</label>
              <textarea className="input font-mono text-xs" rows="3" value={form.headers} onChange={f("headers")}
                placeholder={"Authorization: Bearer xxx\nX-Api-Key: abc"} />
            </div>
            <div>
              <label className="label">Query params (mỗi dòng: key: value)</label>
              <textarea className="input font-mono text-xs" rows="2" value={form.query_params} onChange={f("query_params")} placeholder="limit: 100" />
            </div>
            <div>
              <label className="label">Body schema mẫu (JSON — để agent biết format)</label>
              <textarea className="input font-mono text-xs" rows="5" value={form.body_schema} onChange={f("body_schema")}
                placeholder={'{\n  "userId": "string",\n  "items": [{"productId": "string", "qty": 1}],\n  "totalAmount": 0\n}'} />
            </div>
            <div className="flex gap-2 items-center">
              <button className="btn-primary" onClick={save}>{editId ? "Cập nhật" : "Thêm"}</button>
              {editId && <button className="btn" onClick={reset}>Hủy</button>}
              {msg && <span className="text-xs text-slate-400">{msg}</span>}
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-3">Danh sách endpoints ({list.length})</h2>
          {list.length === 0 && <div className="text-sm text-slate-500">Chưa có endpoint nào.</div>}
          <div className="space-y-2 max-h-[70vh] overflow-y-auto pr-1">
            {list.map(ep => (
              <div key={ep.id} className="border border-slate-700 rounded p-2 text-sm">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={`badge ${ep.method === "GET" ? "bg-sky-900 text-sky-300" : "bg-amber-900 text-amber-300"}`}>{ep.method}</span>
                  <span className="font-mono text-xs">{ep.url}</span>
                  <span className="badge bg-slate-700 text-slate-300">{ep.purpose}</span>
                  <span className="ml-auto flex gap-1">
                    <button className="btn" onClick={() => startEdit(ep)}>Edit</button>
                    <button className="btn-danger" onClick={() => del(ep.id)}>Xóa</button>
                  </span>
                </div>
                <div className="text-slate-300 mt-1">{ep.name}</div>
                {ep.description && <div className="text-xs text-slate-500 mt-0.5">{ep.description}</div>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

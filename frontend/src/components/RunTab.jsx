import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function RunTab() {
  const [memory, setMemory] = useState(null);
  const [busy, setBusy] = useState("");
  const [msg, setMsg] = useState("");
  const [days, setDays] = useState(1);
  const [mode, setMode] = useState("day");
  const [syncResult, setSyncResult] = useState(null);
  const [runResult, setRunResult] = useState(null);

  const load = async () => {
    try { setMemory(await api.getMemory()); }
    catch (e) { setMsg(e.message); }
  };
  useEffect(() => { load(); }, []);

  const doSync = async () => {
    setBusy("sync"); setMsg(""); setSyncResult(null);
    try {
      const r = await api.sync();
      setSyncResult(r);
      await load();
    } catch (e) { setMsg(e.message); }
    finally { setBusy(""); }
  };

  const doRegen = async () => {
    if (!confirm("Re-generate segments (sẽ ghi đè segments hiện tại)?")) return;
    setBusy("regen"); setMsg("");
    try {
      await api.regenerateSegments();
      await load();
      setMsg("Đã regenerate segments.");
    } catch (e) { setMsg(e.message); }
    finally { setBusy(""); }
  };

  const doSimulate = async () => {
    setBusy("simulate"); setMsg(""); setRunResult(null);
    try {
      const r = await api.simulate(days, mode);
      setRunResult(r);
      await load();
    } catch (e) { setMsg(e.message); }
    finally { setBusy(""); }
  };

  const doReset = async () => {
    if (!confirm("Reset simulation (giữ business + endpoints, xóa segments + logs + counters)?")) return;
    await api.resetSimulation();
    await load();
    setMsg("Đã reset simulation.");
  };

  const sim = memory?.simulation;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="card">
        <h2 className="text-lg font-semibold mb-3">1. Sync API doanh nghiệp</h2>
        <p className="text-xs text-slate-400 mb-3">
          Gọi tất cả endpoint GET (purpose = list_products / list_vouchers / get_config / ...) để lấy snapshot mới nhất.
          So sánh với snapshot cũ, ghi lại diff vào memory.
        </p>
        <button className="btn-primary" onClick={doSync} disabled={busy === "sync"}>
          {busy === "sync" ? "Đang sync..." : "Sync now"}
        </button>
        {syncResult && (
          <div className="mt-3 text-sm space-y-1">
            <div>Synced: {syncResult.synced_endpoints.length} endpoint(s)</div>
            <div>Errors: {syncResult.errors.length}</div>
            <div>Changes detected: {syncResult.changes.length}</div>
            {syncResult.changes.length > 0 && (
              <ul className="text-xs text-slate-400 list-disc pl-5">
                {syncResult.changes.slice(0, 10).map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            )}
            {syncResult.errors.length > 0 && (
              <ul className="text-xs text-rose-400 list-disc pl-5">
                {syncResult.errors.slice(0, 10).map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            )}
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-3">2. Khởi tạo / Re-generate Segments</h2>
        <p className="text-xs text-slate-400 mb-3">
          Orchestrator phân tích business + snapshot → đề xuất các tệp khách hàng. Lần đầu chạy simulate sẽ tự gọi cái này. Bạn cũng có thể bấm để tạo lại.
        </p>
        <button className="btn" onClick={doRegen} disabled={busy === "regen"}>
          {busy === "regen" ? "Đang phân tích..." : "Re-generate segments"}
        </button>
      </div>

      <div className="card lg:col-span-2">
        <h2 className="text-lg font-semibold mb-3">3. Run simulation</h2>
        <p className="text-xs text-slate-400 mb-3">
          Mô phỏng N ngày. <b>Mode</b> quyết định mức gộp khi gọi LLM: <code>day</code> = 1 lần gọi/segment/ngày (chi tiết, liên tục nhất);
          <code>month</code> = 1 lần gọi/segment cho mỗi 30 ngày; <code>year</code> = mỗi 365 ngày (rẻ hơn nhưng kém liên tục).
        </p>
        <div className="flex items-end gap-3 flex-wrap">
          <div>
            <label className="label">Mode</label>
            <select className="input w-40" value={mode} onChange={e => setMode(e.target.value)}>
              <option value="day">day</option>
              <option value="month">month</option>
              <option value="year">year</option>
            </select>
          </div>
          <div>
            <label className="label">Số ngày</label>
            <input type="number" min="1" max="365" className="input w-32" value={days} onChange={e => setDays(Number(e.target.value))} />
          </div>
          <button className="btn-primary" onClick={doSimulate} disabled={busy === "simulate"}>
            {busy === "simulate" ? `Đang chạy ${days} ngày...` : `Run ${days} day(s)`}
          </button>
          <button className="btn-danger" onClick={doReset}>Reset simulation</button>
          {msg && <span className="text-xs text-slate-400">{msg}</span>}
        </div>

        {runResult && (
          <div className="mt-3 text-sm">
            Đã chạy {runResult.days_simulated} ngày. Hiện ở ngày {runResult.final_day}. Sinh thêm {runResult.new_logs.length} log entries.
          </div>
        )}
      </div>

      <div className="card lg:col-span-2">
        <h2 className="text-lg font-semibold mb-3">Trạng thái hiện tại</h2>
        {!sim && <div className="text-sm text-slate-500">Chưa có dữ liệu.</div>}
        {sim && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <Stat label="Current day" value={sim.current_day} />
            <Stat label="Growth stage" value={sim.growth_stage} />
            <Stat label="Total users created" value={sim.total_users_created} />
            <Stat label="Total orders created" value={sim.total_orders_created} />
            <Stat label="Total revenue" value={Number(sim.total_revenue).toLocaleString()} />
            <Stat label="Segments" value={sim.segments?.length || 0} />
            <Stat label="Endpoints" value={memory?.endpoints?.length || 0} />
            <Stat label="Last run" value={sim.last_run_at ? new Date(sim.last_run_at).toLocaleString() : "(chưa)"} />
          </div>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="border border-slate-700 rounded p-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-base text-slate-100">{String(value)}</div>
    </div>
  );
}

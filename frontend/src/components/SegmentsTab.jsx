import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function SegmentsTab() {
  const [segs, setSegs] = useState([]);
  const [msg, setMsg] = useState("");

  const load = async () => {
    try { setSegs(await api.getSegments()); }
    catch (e) { setMsg(e.message); }
  };
  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Segments hiện tại ({segs.length})</h2>
        <button className="btn" onClick={load}>Reload</button>
      </div>
      {msg && <div className="text-sm text-rose-400">{msg}</div>}
      {segs.length === 0 && (
        <div className="card text-sm text-slate-500">
          Chưa có segment. Vào tab "Sync & Run" → bấm "Re-generate segments" hoặc chạy simulate.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {segs.map(s => (
          <div key={s.id} className="card">
            <div className="flex items-center gap-2">
              <span className="text-base font-semibold text-emerald-300">{s.name}</span>
              <span className="badge bg-slate-700 text-slate-300">size {s.size}</span>
              <span className="badge bg-slate-700 text-slate-300">weight {(s.weight * 100).toFixed(0)}%</span>
            </div>
            <div className="text-xs text-slate-400 mt-1">{s.description}</div>
            <div className="text-xs mt-2 flex flex-wrap gap-1">
              {s.personality_hints?.map((h, i) => (
                <span key={i} className="badge bg-indigo-900 text-indigo-300">{h}</span>
              ))}
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-400">
              <div>Yesterday orders: <span className="text-slate-200">{s.yesterday_orders}</span></div>
              <div>Yesterday revenue: <span className="text-slate-200">{Number(s.yesterday_revenue).toLocaleString()}</span></div>
              <div>Total orders: <span className="text-slate-200">{s.total_orders}</span></div>
              <div>Total revenue: <span className="text-slate-200">{Number(s.total_revenue).toLocaleString()}</span></div>
              <div>Voucher rate: <span className="text-slate-200">{(s.voucher_usage_rate * 100).toFixed(0)}%</span></div>
              <div>Top: <span className="text-slate-200">{s.top_products?.join(", ") || "—"}</span></div>
            </div>
            {s.yesterday_summary && (
              <div className="mt-2 text-xs text-slate-400 italic">"{s.yesterday_summary}"</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

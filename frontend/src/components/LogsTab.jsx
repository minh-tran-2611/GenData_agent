import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const STATUS_COLOR = {
  ok: "bg-emerald-900 text-emerald-300",
  error: "bg-rose-900 text-rose-300",
  info: "bg-slate-700 text-slate-300",
};

export default function LogsTab() {
  const [data, setData] = useState({ total: 0, logs: [] });
  const [limit, setLimit] = useState(200);
  const [filter, setFilter] = useState("");

  const load = async () => {
    try { setData(await api.getLogs(limit, 0)); }
    catch (e) { setData({ total: 0, logs: [] }); }
  };
  useEffect(() => { load(); }, [limit]);

  const filtered = filter
    ? data.logs.filter(l => JSON.stringify(l).toLowerCase().includes(filter.toLowerCase()))
    : data.logs;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <h2 className="text-lg font-semibold">Logs ({data.total} total, hiển thị {filtered.length})</h2>
        <input className="input w-64 ml-auto" placeholder="Filter..." value={filter} onChange={e => setFilter(e.target.value)} />
        <select className="input w-32" value={limit} onChange={e => setLimit(Number(e.target.value))}>
          <option value="100">100</option>
          <option value="200">200</option>
          <option value="500">500</option>
          <option value="2000">2000</option>
        </select>
        <button className="btn" onClick={load}>Reload</button>
      </div>
      <div className="card overflow-x-auto p-0">
        <table className="w-full text-xs">
          <thead className="bg-slate-900/60 text-slate-400">
            <tr>
              <th className="text-left p-2">Time</th>
              <th className="text-left p-2">Day</th>
              <th className="text-left p-2">Action</th>
              <th className="text-left p-2">Endpoint</th>
              <th className="text-left p-2">Status</th>
              <th className="text-left p-2">Detail</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((l, i) => (
              <tr key={i} className="border-t border-slate-800 hover:bg-slate-800/40">
                <td className="p-2 font-mono text-slate-500">{new Date(l.timestamp).toLocaleTimeString()}</td>
                <td className="p-2">{l.day}</td>
                <td className="p-2">{l.action}</td>
                <td className="p-2 font-mono text-slate-400">{l.endpoint || "—"}</td>
                <td className="p-2">
                  <span className={`badge ${STATUS_COLOR[l.status] || ""}`}>{l.status}</span>
                </td>
                <td className="p-2 text-slate-300">{l.detail}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan="6" className="p-4 text-center text-slate-500">Chưa có log nào.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

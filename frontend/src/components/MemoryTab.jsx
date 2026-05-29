import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function MemoryTab() {
  const [mem, setMem] = useState(null);
  const [msg, setMsg] = useState("");

  const load = async () => {
    try { setMem(await api.getMemory()); }
    catch (e) { setMsg(e.message); }
  };
  useEffect(() => { load(); }, []);

  const copy = () => {
    navigator.clipboard.writeText(JSON.stringify(mem, null, 2));
    setMsg("Đã copy memory JSON.");
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold">Memory file (raw)</h2>
        <span className="text-xs text-slate-500">backend/data/memory.json</span>
        <span className="ml-auto"></span>
        <button className="btn" onClick={load}>Reload</button>
        <button className="btn" onClick={copy}>Copy JSON</button>
        {msg && <span className="text-xs text-slate-400">{msg}</span>}
      </div>
      <pre className="card text-xs overflow-auto max-h-[80vh] whitespace-pre-wrap">
{mem ? JSON.stringify(mem, null, 2) : "(loading...)"}
      </pre>
    </div>
  );
}

import React, { useState } from "react";
import SettingsTab from "./components/SettingsTab.jsx";
import BusinessTab from "./components/BusinessTab.jsx";
import EndpointsTab from "./components/EndpointsTab.jsx";
import RunTab from "./components/RunTab.jsx";
import SegmentsTab from "./components/SegmentsTab.jsx";
import LogsTab from "./components/LogsTab.jsx";
import MemoryTab from "./components/MemoryTab.jsx";

const TABS = [
  { id: "settings", label: "1. Settings" },
  { id: "business", label: "2. Business" },
  { id: "endpoints", label: "3. Endpoints" },
  { id: "run", label: "4. Sync & Run" },
  { id: "segments", label: "5. Segments" },
  { id: "logs", label: "6. Logs" },
  { id: "memory", label: "7. Memory" },
];

export default function App() {
  const [tab, setTab] = useState("settings");

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-700 bg-slate-900/60">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
          <div className="text-emerald-400 font-semibold">Data Generator Agent</div>
          <div className="text-xs text-slate-500">Multi-agent business data simulator</div>
        </div>
        <nav className="max-w-7xl mx-auto px-4 flex gap-1 overflow-x-auto">
          {TABS.map((t) => (
            <div
              key={t.id}
              className={`tab ${tab === t.id ? "tab-active" : ""}`}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </div>
          ))}
        </nav>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4">
        {tab === "settings" && <SettingsTab />}
        {tab === "business" && <BusinessTab />}
        {tab === "endpoints" && <EndpointsTab />}
        {tab === "run" && <RunTab />}
        {tab === "segments" && <SegmentsTab />}
        {tab === "logs" && <LogsTab />}
        {tab === "memory" && <MemoryTab />}
      </main>

      <footer className="border-t border-slate-700 text-center text-xs text-slate-500 py-2">
        Backend: <code>http://127.0.0.1:8200</code> · Memory file: <code>backend/data/memory.json</code>
      </footer>
    </div>
  );
}

const BASE = "/api";

async function req(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    try {
      const j = await resp.json();
      detail = j.detail || JSON.stringify(j);
    } catch {}
    throw new Error(detail);
  }
  if (resp.status === 204) return null;
  return resp.json();
}

export const api = {
  // memory + settings
  getMemory: () => req("/memory"),
  resetSimulation: () => req("/memory/reset", { method: "POST" }),
  wipeMemory: () => req("/memory/wipe", { method: "POST" }),
  getSettings: () => req("/settings"),
  setSettings: (s) => req("/settings", { method: "POST", body: JSON.stringify(s) }),
  // business
  getBusiness: () => req("/business"),
  setBusiness: (b) => req("/business", { method: "POST", body: JSON.stringify(b) }),
  // growth
  getGrowth: () => req("/growth"),
  setGrowth: (g) => req("/growth", { method: "POST", body: JSON.stringify(g) }),
  // endpoints
  listEndpoints: () => req("/endpoints"),
  addEndpoint: (e) => req("/endpoints", { method: "POST", body: JSON.stringify(e) }),
  updateEndpoint: (id, e) => req(`/endpoints/${id}`, { method: "PUT", body: JSON.stringify(e) }),
  deleteEndpoint: (id) => req(`/endpoints/${id}`, { method: "DELETE" }),
  parseEndpointsText: (text) => req("/endpoints/parse", { method: "POST", body: JSON.stringify({ text }) }),
  bulkSaveEndpoints: (endpoints, replace_all = false) =>
    req("/endpoints/bulk", { method: "POST", body: JSON.stringify({ endpoints, replace_all }) }),
  // sync + simulate
  sync: () => req("/sync", { method: "POST" }),
  regenerateSegments: () => req("/segments/regenerate", { method: "POST" }),
  getSegments: () => req("/segments"),
  simulate: (days, mode = "day") => req("/simulate", { method: "POST", body: JSON.stringify({ days, mode }) }),
  getLogs: (limit = 200, offset = 0) => req(`/logs?limit=${limit}&offset=${offset}`),
};

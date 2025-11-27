// src/api/client.js
const API_BASE = import.meta.env.VITE_API_URL;

// Health check
export async function apiHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
  return res.json(); // { ok: true } expected
}

// Get stores
export async function apiGetStores() {
  const res = await fetch(`${API_BASE}/stores`);
  if (!res.ok) throw new Error(`Get stores failed: HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data.stores) ? data.stores : [];
}

// Get forecast for a store
export async function apiGetForecast(storeId) {
  const res = await fetch(`${API_BASE}/forecast/${storeId}`);
  if (!res.ok) throw new Error(`Forecast failed: HTTP ${res.status}`);
  return res.json(); // { store_id, prediction }
}
// src/api/client.js
export async function apiExplainForecast({ storeId, prediction }) {
  const res = await fetch(`${API_BASE}/explain_forecast`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      store_id: storeId,
      prediction,
    }),
  });

  if (!res.ok) throw new Error(`Explain forecast failed: HTTP ${res.status}`);
  return res.json();
}



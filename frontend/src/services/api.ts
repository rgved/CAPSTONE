const API_BASE = "http://localhost:8000/api";

async function fetchJson(url: string, options?: RequestInit) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "API request failed");
  }
  return res.json();
}

export const api = {
  getDashboard: () => fetchJson(`${API_BASE}/dashboard`),
  getMissions: () => fetchJson(`${API_BASE}/missions`),
  getMissionDetail: (id: string) => fetchJson(`${API_BASE}/missions/${id}`),
  getMissionTimeline: (id: string) => fetchJson(`${API_BASE}/missions/${id}/timeline`),
  startScan: (url: string) => fetchJson(`${API_BASE}/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  }),
  getFindings: (severity?: string, category?: string, search?: string) => {
    const params = new URLSearchParams();
    if (severity && severity !== "all") params.append("severity", severity);
    if (category && category !== "all") params.append("category", category);
    if (search) params.append("search", search);
    return fetchJson(`${API_BASE}/findings?${params.toString()}`);
  },
  getReports: () => fetchJson(`${API_BASE}/reports`),
  getReportDetail: (id: string) => fetchJson(`${API_BASE}/reports/${id}`),
  getMetrics: () => fetchJson(`${API_BASE}/metrics`),
};
export type ApiService = typeof api;

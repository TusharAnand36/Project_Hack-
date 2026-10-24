import type { components } from "./types";

export type Health = components["schemas"]["Health"];
export type AnalyzeRequest = components["schemas"]["AnalyzeRequest"];
export type AnalyzeResponse = components["schemas"]["AnalyzeResponse"];

const BASE = import.meta.env.VITE_API_BASE ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
  return (await res.json()) as T;
}

export const api = {
  health: () => request<Health>("/health"),
  analyze: (body: AnalyzeRequest) =>
    request<AnalyzeResponse>("/analyze", { method: "POST", body: JSON.stringify(body) }),
};

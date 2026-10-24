import type { components } from "./types";

type S = components["schemas"];
export type Health = S["Health"];
export type AnalyzeRequest = S["AnalyzeRequest"];
export type AnalyzeResponse = S["AnalyzeResponse"];
export type Value = S["Value"];
export type Range = S["Range"];
export type Gate = S["Gate"];
export type Chain = S["Chain"];
export type Diagnosis = S["Diagnosis"];
export type Issue = S["Issue"];
export type Pea = S["Pea"];
export type Tag = Value["tag"];

export interface Preset {
  id: string;
  title: string;
  story: string;
  payload: AnalyzeRequest;
}

export interface Source {
  id: string;
  citation: string;
  url?: string | null;
  kind: string;
  notes?: string | null;
}

export interface DataReport {
  dataset_version: string;
  params_total: number;
  params_filled: number;
  params_missing: number;
  by_tag: Record<string, number>;
  by_grade: Record<string, number>;
  completeness_ab_share: number;
}

/** An analysis plus where it came from (live API or the offline demo snapshot). */
export interface AnalysisResult {
  data: AnalyzeResponse;
  offline: boolean;
}

const BASE = import.meta.env.VITE_API_BASE ?? "/api";
export const ANALYZE_TIMEOUT_MS = 8000;

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit, timeoutMs = ANALYZE_TIMEOUT_MS): Promise<T> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE}${path}`, {
      ...init,
      signal: ctrl.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const body = await res.json();
        detail = typeof body.detail === "string" ? body.detail : detail;
      } catch {
        /* not JSON */
      }
      throw new ApiError(detail, res.status);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

async function snapshot(presetId: string, lang: string): Promise<AnalyzeResponse | null> {
  for (const l of [lang, "en"]) {
    try {
      const res = await fetch(`/snapshots/${presetId}.${l}.json`);
      if (res.ok) return (await res.json()) as AnalyzeResponse;
    } catch {
      /* try next */
    }
  }
  return null;
}

export const api = {
  health: () => request<Health>("/health", undefined, 4000),
  presets: () => request<Preset[]>("/presets"),
  dataFile: <T>(name: string) => request<T>(`/data/${name}`),
  /** Live analysis; on network failure or timeout, fall back to the preset's demo snapshot. */
  analyze: async (body: AnalyzeRequest, presetId: string | null, lang: string): Promise<AnalysisResult> => {
    try {
      return {
        data: await request<AnalyzeResponse>("/analyze", { method: "POST", body: JSON.stringify(body) }),
        offline: false,
      };
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) throw e; // the request itself is wrong
      const snap = presetId ? await snapshot(presetId, lang) : null;
      if (snap) return { data: snap, offline: true };
      throw e;
    }
  },
};

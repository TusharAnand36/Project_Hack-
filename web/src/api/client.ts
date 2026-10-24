import type { components } from "./types";

type S = components["schemas"];
export type Health = S["Health"];
export type AnalyzeRequest = S["AnalyzeRequest-Input"];
export type AnalyzeResponse = S["AnalyzeResponse"];
export type Value = S["Value"];
export type Range = S["Range"];
export type Gate = S["Gate"];
export type Chain = S["Chain"];
export type Diagnosis = S["Diagnosis"];
export type Issue = S["Issue"];
export type Pea = S["Pea"];
export type Tag = Value["tag"];
export type AiText = S["AiText"];
export type ParseResponse = S["ParseResponse"];
export type PlanResponse = S["PlanResponse"];
export type UpdateEvidenceRequest = S["UpdateEvidenceRequest"];
export type UpdateEvidenceResponse = S["UpdateEvidenceResponse"];
export type Snapshot = S["Snapshot"];

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
  data: AnalyzeResponse & { snapshot?: SnapshotStamp };
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

function post<T>(path: string, body: unknown, timeoutMs?: number): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) }, timeoutMs);
}

async function staticJson<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(path);
    return res.ok ? ((await res.json()) as T) : null;
  } catch {
    return null;
  }
}

async function snapshot<T>(presetId: string, lang: string, suffix = ""): Promise<T | null> {
  for (const l of [lang, "en"]) {
    const s = await staticJson<T>(`/snapshots/${presetId}.${l}${suffix}.json`);
    if (s) return s;
  }
  return null;
}

/** Live call first; if the API cannot be reached (not a 422), use the static file built by `make snapshots`. */
async function withFallback<T>(live: () => Promise<T>, fallback: () => Promise<T | null>): Promise<T> {
  try {
    return await live();
  } catch (e) {
    if (e instanceof ApiError && e.status === 422) throw e;
    const f = await fallback();
    if (f) return f;
    throw e;
  }
}

export interface SnapshotStamp {
  engine_version: string;
  dataset_version: string;
  generated_at: string;
  lang: string;
}

export const api = {
  feedback: (body: S["FeedbackRequest"]) => post<S["FeedbackReceipt"]>("/feedback", body),
  health: () => request<Health>("/health", undefined, 4000),
  presets: () =>
    withFallback(
      () => request<Preset[]>("/presets"),
      () => staticJson<Preset[]>("/snapshots/presets.json"),
    ),
  dataFile: <T>(name: string) =>
    withFallback(
      () => request<T>(`/data/${name}`),
      () => staticJson<T>(`/offline-data/${name}.json`),
    ),
  explain: (request: AnalyzeRequest, lang: string, presetId: string | null = null) =>
    withFallback(
      () => post<AiText>("/explain", { request, lang }, 30000),
      async () => (presetId ? snapshot<AiText>(presetId, lang, ".explain") : null),
    ),
  plan: (request: AnalyzeRequest, lang: string) => post<PlanResponse>("/plan", { request, lang }, 30000),
  parseText: (text: string, base: AnalyzeRequest | null, lang: string) =>
    post<ParseResponse>("/parse-text", { text, base, lang }, 30000),
  updateEvidence: (body: UpdateEvidenceRequest) =>
    post<UpdateEvidenceResponse>("/update-evidence", body, 20000),
  /** Live analysis; on network failure or timeout, fall back to the preset's demo snapshot. */
  analyze: async (body: AnalyzeRequest, presetId: string | null, lang: string): Promise<AnalysisResult> => {
    try {
      return {
        data: await request<AnalyzeResponse>("/analyze", { method: "POST", body: JSON.stringify(body) }),
        offline: false,
      };
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) throw e; // the request itself is wrong
      const snap = presetId ? await snapshot<AnalysisResult["data"]>(presetId, lang) : null;
      if (snap) return { data: snap, offline: true };
      throw e;
    }
  },
};

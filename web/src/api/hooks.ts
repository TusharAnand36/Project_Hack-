import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { useStore } from "@/store";

import { api, type DataReport, type Preset, type Source } from "./client";

export function useHealth() {
  return useQuery({ queryKey: ["health"], queryFn: api.health, retry: 1 });
}

export function usePresets() {
  return useQuery<Preset[]>({ queryKey: ["presets"], queryFn: api.presets, staleTime: Infinity });
}

export function useDataFile<T>(name: string) {
  return useQuery<T>({
    queryKey: ["data", name],
    queryFn: () => api.dataFile<T>(name),
    staleTime: Infinity,
    retry: 1,
  });
}

export function useSources() {
  const q = useDataFile<{ sources: Source[] }>("sources");
  const map = new Map((q.data?.sources ?? []).map((s) => [s.id, s]));
  return map;
}

export function useDataReport() {
  return useDataFile<DataReport>("report");
}

function useDebounced<T>(value: T, ms: number): T {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return v;
}

/** The current analysis. Slider changes are debounced 400 ms before re-calling /analyze. */
export function useAnalysis() {
  const { i18n } = useTranslation();
  const request = useStore((s) => s.request);
  const presetId = useStore((s) => s.presetId);
  const debounced = useDebounced(request, 400);
  return useQuery({
    queryKey: ["analyze", debounced, presetId, i18n.language],
    queryFn: () => api.analyze(debounced!, presetId, i18n.language),
    enabled: debounced !== null,
    placeholderData: keepPreviousData,
    retry: false,
    staleTime: Infinity,
  });
}

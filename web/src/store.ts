import { create } from "zustand";

import type { AnalyzeRequest } from "@/api/client";

export type Screen = "input" | "verdict" | "diagnosis" | "chains" | "cost" | "next" | "memo";
export const SCREENS: Screen[] = ["input", "verdict", "diagnosis", "chains", "cost", "next"];

interface UiState {
  screen: Screen;
  runRevision: number;
  request: AnalyzeRequest | null;
  presetId: string | null; // set while the request is an unmodified preset (snapshot fallback)
  showSources: boolean;
  selectedChain: string | null;
  setScreen: (s: Screen) => void;
  runRequest: (r: AnalyzeRequest, presetId?: string | null, screen?: Screen) => void;
  patchRequest: (fn: (r: AnalyzeRequest) => AnalyzeRequest) => void;
  toggleSources: () => void;
  selectChain: (id: string | null) => void;
}

export const useStore = create<UiState>((set) => ({
  screen: "input",
  runRevision: 0,
  request: null,
  presetId: null,
  showSources: false,
  selectedChain: null,
  setScreen: (screen) => set({ screen }),
  runRequest: (request, presetId = null, screen = "verdict") =>
    set((s) => {
      const pea = s.request?.pea ?? request.pea;
      const changed = JSON.stringify(pea) !== JSON.stringify(request.pea);
      return {
        request: { ...request, pea },
        runRevision: s.runRevision + 1,
        presetId: changed ? null : presetId,
        screen,
        selectedChain: null,
      };
    }),
  patchRequest: (fn) => set((s) => (s.request ? { request: fn(s.request), presetId: null } : {})),
  toggleSources: () => set((s) => ({ showSources: !s.showSources })),
  selectChain: (selectedChain) => set({ selectedChain }),
}));

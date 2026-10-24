import { create } from "zustand";

import type { AnalyzeRequest } from "@/api/client";

export type Screen = "input" | "verdict" | "diagnosis" | "chains" | "cost" | "next";
export const SCREENS: Screen[] = ["input", "verdict", "diagnosis", "chains", "cost", "next"];

interface UiState {
  screen: Screen;
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
  request: null,
  presetId: null,
  showSources: false,
  selectedChain: null,
  setScreen: (screen) => set({ screen }),
  runRequest: (request, presetId = null, screen = "verdict") =>
    set({ request, presetId, screen, selectedChain: null }),
  patchRequest: (fn) => set((s) => (s.request ? { request: fn(s.request), presetId: null } : {})),
  toggleSources: () => set((s) => ({ showSources: !s.showSources })),
  selectChain: (selectedChain) => set({ selectedChain }),
}));

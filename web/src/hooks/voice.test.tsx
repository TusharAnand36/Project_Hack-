import { act, renderHook, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { VoiceInput } from "@/components/VoiceInput";
import { gloss } from "@/lib/glossary";
import { renderWithProviders } from "@/test/render";

import { useReadAloud } from "./useReadAloud";
import { useSpeechInput, type Recognition } from "./useSpeechInput";

class FakeRecognition implements Partial<Recognition> {
  static last: FakeRecognition;
  lang = "";
  interimResults = false;
  continuous = false;
  onstart: (() => void) | null = null;
  onresult: ((e: unknown) => void) | null = null;
  onerror: ((e: { error: string }) => void) | null = null;
  onend: (() => void) | null = null;
  constructor() {
    FakeRecognition.last = this;
  }
  start() {}
  stop() {
    this.onend?.();
  }
  abort() {}
}

const result = (text: string, isFinal: boolean) => ({
  resultIndex: 0,
  results: [Object.assign([{ transcript: text }], { isFinal })],
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete (window as unknown as Record<string, unknown>).webkitSpeechRecognition;
});

describe("useSpeechInput", () => {
  it("goes requesting -> listening -> processing -> ready and hands over an editable transcript", () => {
    (window as unknown as Record<string, unknown>).webkitSpeechRecognition = FakeRecognition;
    const onFinal = vi.fn();
    const { result: h } = renderHook(() => useSpeechInput("hi", onFinal));
    expect(h.current.supported).toBe(true);
    act(() => h.current.start());
    expect(h.current.state).toBe("requesting");
    expect(FakeRecognition.last.lang).toBe("hi-IN");
    act(() => FakeRecognition.last.onstart?.());
    expect(h.current.state).toBe("listening");
    act(() => FakeRecognition.last.onresult?.(result("मूंगफली की खली", false)));
    expect(h.current.interim).toBe("मूंगफली की खली");
    act(() => FakeRecognition.last.onresult?.(result("मूंगफली की खली पेय के लिए", true)));
    act(() => h.current.stop());
    expect(h.current.state).toBe("ready");
    expect(onFinal).toHaveBeenCalledWith("मूंगफली की खली पेय के लिए");
  });

  it("maps browser errors and silence to friendly states", () => {
    (window as unknown as Record<string, unknown>).webkitSpeechRecognition = FakeRecognition;
    const { result: h } = renderHook(() => useSpeechInput("en", vi.fn()));
    act(() => h.current.start());
    expect(FakeRecognition.last.lang).toBe("en-IN");
    act(() => FakeRecognition.last.onerror?.({ error: "not-allowed" }));
    expect([h.current.state, h.current.error]).toEqual(["error", "denied"]);
    act(() => h.current.start());
    act(() => FakeRecognition.last.onend?.());
    expect(h.current.error).toBe("noSpeech");
  });

  it("hides the mic when the browser has no speech recognition (e.g. Firefox)", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new Error("offline"))),
    );
    renderWithProviders(<VoiceInput onTranscript={vi.fn()} onTypeInstead={vi.fn()} />);
    expect(screen.queryByTestId("voice")).toBeNull();
  });
});

describe("useReadAloud", () => {
  it("is only available when a voice exists for the language", () => {
    const synth = { getVoices: () => [{ lang: "hi-IN" }], cancel: vi.fn(), speak: vi.fn() };
    vi.stubGlobal("speechSynthesis", synth);
    expect(renderHook(() => useReadAloud("hi")).result.current.available).toBe(true);
    synth.getVoices = () => [{ lang: "fr-FR" }];
    expect(renderHook(() => useReadAloud("hi")).result.current.available).toBe(false);
  });
});

describe("glossary", () => {
  it("adds a Hindi gloss after the English term only in Hindi", () => {
    expect(gloss("Aflatoxin B1", "hi")).toBe("Aflatoxin B1 (एफ्लाटॉक्सिन)");
    expect(gloss("Phytic acid", "hi")).toBe("Phytic acid (फाइटिक एसिड)");
    expect(gloss("Aflatoxin B1", "en")).toBe("Aflatoxin B1");
  });
});

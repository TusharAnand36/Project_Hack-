import { useCallback, useEffect, useRef, useState } from "react";

/** Minimal Web Speech API types (not in the TS DOM lib). */
interface SpeechAlternative {
  transcript: string;
}
interface SpeechResult {
  isFinal: boolean;
  0: SpeechAlternative;
}
interface SpeechEvent {
  resultIndex: number;
  results: ArrayLike<SpeechResult>;
}
interface SpeechErrorEvent {
  error: string;
}
export interface Recognition {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: (() => void) | null;
  onresult: ((e: SpeechEvent) => void) | null;
  onerror: ((e: SpeechErrorEvent) => void) | null;
  onend: (() => void) | null;
}
type Ctor = new () => Recognition;

export type VoiceState = "idle" | "requesting" | "listening" | "processing" | "ready" | "error";
export type VoiceError = "denied" | "noSpeech" | "network" | "aborted" | "failed";

const LOCALE: Record<string, string> = { en: "en-IN", hi: "hi-IN" };

export function getRecognition(): Ctor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as { SpeechRecognition?: Ctor; webkitSpeechRecognition?: Ctor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

function mapError(code: string): VoiceError {
  if (code === "not-allowed" || code === "service-not-allowed") return "denied";
  if (code === "no-speech") return "noSpeech";
  if (code === "network") return "network";
  if (code === "aborted") return "aborted";
  return "failed";
}

/**
 * Voice input for the "describe in words" box (website plan §7.4). Never submits anything:
 * the final transcript is handed to `onFinal` so the user can edit it.
 */
export function useSpeechInput(lang: string, onFinal: (text: string) => void) {
  const Rec = getRecognition();
  const [state, setState] = useState<VoiceState>("idle");
  const [error, setError] = useState<VoiceError | null>(null);
  const [interim, setInterim] = useState("");
  const rec = useRef<Recognition | null>(null);
  const finalText = useRef("");
  const failed = useRef(false);
  const onFinalRef = useRef(onFinal);
  onFinalRef.current = onFinal;

  useEffect(() => () => rec.current?.abort(), []);

  const start = useCallback(() => {
    if (!Rec) return;
    rec.current?.abort();
    const r = new Rec();
    r.lang = LOCALE[lang] ?? "en-IN";
    r.interimResults = true;
    r.continuous = true;
    finalText.current = "";
    failed.current = false;
    setInterim("");
    setError(null);
    setState("requesting");
    r.onstart = () => setState("listening");
    r.onresult = (e) => {
      let live = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const res = e.results[i];
        if (res.isFinal) finalText.current += res[0].transcript;
        else live += res[0].transcript;
      }
      setInterim((finalText.current + " " + live).trim());
    };
    r.onerror = (e) => {
      failed.current = true;
      setError(mapError(e.error));
      setState("error");
    };
    r.onend = () => {
      if (failed.current) return;
      const text = finalText.current.trim();
      if (text) {
        onFinalRef.current(text);
        setState("ready");
      } else {
        setError("noSpeech");
        setState("error");
      }
    };
    rec.current = r;
    try {
      r.start();
    } catch {
      failed.current = true;
      setError("failed");
      setState("error");
    }
  }, [Rec, lang]);

  const stop = useCallback(() => {
    if (!rec.current) return;
    setState("processing");
    rec.current.stop();
  }, []);

  const reset = useCallback(() => {
    rec.current?.abort();
    setState("idle");
    setError(null);
    setInterim("");
  }, []);

  return { supported: Rec !== null, state, error, interim, start, stop, reset };
}

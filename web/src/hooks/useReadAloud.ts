import { useEffect, useState } from "react";

/** Read-aloud (website plan §7.5): only offered when the browser has a voice for the current language. */
export function useReadAloud(lang: string) {
  const synth = typeof window !== "undefined" ? window.speechSynthesis : undefined;
  const [voice, setVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    if (!synth) return;
    const pick = () => {
      const voices = synth.getVoices();
      const exact = voices.find((v) => v.lang === `${lang}-IN`);
      setVoice(exact ?? voices.find((v) => v.lang.toLowerCase().startsWith(lang)) ?? null);
    };
    pick();
    synth.addEventListener?.("voiceschanged", pick);
    return () => {
      synth.removeEventListener?.("voiceschanged", pick);
      synth.cancel();
    };
  }, [synth, lang]);

  const speak = (text: string) => {
    if (!synth || !voice) return;
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.voice = voice;
    u.lang = voice.lang;
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    setSpeaking(true);
    synth.speak(u);
  };
  const stop = () => {
    synth?.cancel();
    setSpeaking(false);
  };
  return { available: !!voice, speaking, speak, stop };
}

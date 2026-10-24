import { useTranslation } from "react-i18next";

import { useSpeechInput } from "@/hooks/useSpeechInput";
import { cn } from "@/lib/utils";

import { Button } from "./ui/button";

/** Mic for the describe box. Hidden when the browser has no speech recognition (e.g. Firefox). */
export function VoiceInput({
  onTranscript,
  onTypeInstead,
}: {
  onTranscript: (t: string) => void;
  onTypeInstead: () => void;
}) {
  const { t, i18n } = useTranslation();
  const v = useSpeechInput(i18n.language, onTranscript);
  if (!v.supported) return null;
  const busy = v.state === "requesting" || v.state === "listening" || v.state === "processing";
  return (
    <div className="mt-2 space-y-2" data-testid="voice">
      <div className="flex flex-wrap items-center gap-2">
        {!busy ? (
          <Button type="button" variant="outline" onClick={v.start} data-testid="mic">
            <span aria-hidden="true">🎤</span> {t("voice.speak")}
          </Button>
        ) : (
          <Button type="button" onClick={v.stop} disabled={v.state !== "listening"} data-testid="mic-stop">
            <span
              aria-hidden="true"
              className={cn(
                "inline-block h-3 w-3 rounded-full bg-bad",
                v.state === "listening" && "animate-pulse",
              )}
            />
            {t("voice.stop")}
          </Button>
        )}
        <p className="text-xs text-muted-foreground">{t("voice.privacy")}</p>
      </div>
      <div role="status" aria-live="polite" className="text-sm" data-testid="voice-status">
        {v.state === "requesting" && t("voice.requesting")}
        {v.state === "listening" && t("voice.listening")}
        {v.state === "processing" && t("voice.processing")}
        {v.state === "ready" && t("voice.ready")}
        {v.state === "error" && v.error && <span className="text-warn">{t(`voice.${v.error}`)}</span>}
      </div>
      {busy && v.interim && (
        <p className="rounded bg-muted p-2 text-sm italic" data-testid="voice-interim">
          {v.interim}
        </p>
      )}
      {v.state === "error" && (
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="outline" size="sm" onClick={v.start}>
            {t("voice.tryAgain")}
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => {
              v.reset();
              onTypeInstead();
            }}
          >
            {t("voice.typeInstead")}
          </Button>
        </div>
      )}
    </div>
  );
}

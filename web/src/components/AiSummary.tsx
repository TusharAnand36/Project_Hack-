import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { api, type AnalyzeRequest } from "@/api/client";
import { useReadAloud } from "@/hooks/useReadAloud";
import { useStore } from "@/store";

import { Button } from "./ui/button";
import { Card, Skeleton } from "./ui/card";

/** Plain-language explanation. Rendered as plain text (never HTML); the badge says how it was made. */
export function AiSummary({ request }: { request: AnalyzeRequest }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const [showEnglish, setShowEnglish] = useState(false);
  const presetId = useStore((s) => s.presetId);
  const q = useQuery({
    queryKey: ["explain", request, lang],
    queryFn: () => api.explain(request, lang, presetId),
    staleTime: Infinity,
    retry: false,
  });
  const english = useQuery({
    queryKey: ["explain", request, "en"],
    queryFn: () => api.explain(request, "en", presetId),
    staleTime: Infinity,
    retry: false,
    enabled: lang !== "en" && showEnglish,
  });
  const shown = showEnglish && english.data ? english.data : q.data;
  const voiceLang = showEnglish ? "en" : lang;
  const reader = useReadAloud(voiceLang);
  const badge =
    shown &&
    (shown.machine_translated
      ? t("ai.badgeTranslated")
      : shown.llm_used
        ? t("ai.badgeAi")
        : t("ai.badgeTemplate"));

  return (
    <Card data-testid="ai-summary" aria-busy={q.isPending}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-medium">{t("ai.summary")}</h3>
        {shown && (
          <span
            className={`rounded border px-2 text-xs ${shown.llm_used ? "border-primary text-primary" : "border-border text-muted-foreground"}`}
            data-testid="ai-badge"
          >
            {badge}
          </span>
        )}
      </div>
      {q.isPending && (
        <div className="mt-2 space-y-2" role="status">
          <span className="sr-only">{t("ai.loading")}</span>
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>
      )}
      {q.isError && <p className="mt-2 text-sm text-muted-foreground">{t("ai.unavailable")}</p>}
      {shown && (
        <>
          <p className="mt-2 whitespace-pre-line" lang={shown.lang} data-testid="ai-text">
            {shown.text}
          </p>
          {shown.note && <p className="mt-1 text-xs text-muted-foreground">{shown.note}</p>}
          <div className="mt-2 flex flex-wrap gap-2">
            {lang !== "en" && (
              <Button
                variant="outline"
                size="sm"
                aria-pressed={showEnglish}
                onClick={() => setShowEnglish((x) => !x)}
                data-testid="show-english"
              >
                {showEnglish ? t("ai.showOriginal") : t("ai.showEnglish")}
              </Button>
            )}
            {reader.available &&
              (reader.speaking ? (
                <Button variant="outline" size="sm" onClick={reader.stop}>
                  <span aria-hidden="true">■</span> {t("readAloud.stop")}
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => reader.speak(shown.text)}
                  data-testid="read-aloud"
                >
                  <span aria-hidden="true">🔊</span> {t("readAloud.play")}
                </Button>
              ))}
          </div>
        </>
      )}
    </Card>
  );
}

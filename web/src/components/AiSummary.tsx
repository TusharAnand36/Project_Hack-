import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { api, type AnalyzeRequest } from "@/api/client";

import { Card, Skeleton } from "./ui/card";

/** Plain-language explanation. Rendered as plain text (never HTML); the badge says how it was made. */
export function AiSummary({ request }: { request: AnalyzeRequest }) {
  const { t, i18n } = useTranslation();
  const q = useQuery({
    queryKey: ["explain", request, i18n.language],
    queryFn: () => api.explain(request, i18n.language),
    staleTime: Infinity,
    retry: false,
  });
  return (
    <Card data-testid="ai-summary" aria-busy={q.isPending}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-medium">{t("ai.summary")}</h3>
        {q.data && (
          <span
            className={`rounded border px-2 text-xs ${q.data.llm_used ? "border-primary text-primary" : "border-border text-muted-foreground"}`}
            data-testid="ai-badge"
          >
            {q.data.llm_used ? t("ai.badgeAi") : t("ai.badgeTemplate")}
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
      {q.data && (
        <>
          <p className="mt-2 whitespace-pre-line">{q.data.text}</p>
          {q.data.note && <p className="mt-1 text-xs text-muted-foreground">{q.data.note}</p>}
        </>
      )}
    </Card>
  );
}

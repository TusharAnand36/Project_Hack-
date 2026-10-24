import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { api } from "@/api/client";
import { Badge } from "@/components/ui/badge";

export function HealthIndicator() {
  const { t } = useTranslation();
  const { data, isPending, isError } = useQuery({ queryKey: ["health"], queryFn: api.health, retry: 1 });

  const state = isPending ? "checking" : isError || data?.status !== "ok" ? "down" : "ok";
  const variant = state === "ok" ? "ok" : state === "down" ? "bad" : "muted";
  const icon = state === "ok" ? "✓" : state === "down" ? "✕" : "…";

  return (
    <div role="status" aria-live="polite" className="flex flex-col items-start gap-1">
      <Badge variant={variant} data-testid="health">
        <span aria-hidden="true">{icon}</span>
        {t("health.label")}: {t(`health.${state}`)}
      </Badge>
      {data && (
        <span className="text-sm text-muted-foreground">
          {t("health.engine", { engine: data.engine_version, dataset: data.dataset_version })}
        </span>
      )}
    </div>
  );
}

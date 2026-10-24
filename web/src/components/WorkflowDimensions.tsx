import { useTranslation } from "react-i18next";
import type { AnalyzeResponse } from "@/api/client";

export function WorkflowDimensions({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  return (
    <div className="my-6 grid gap-4 sm:grid-cols-2" data-testid="assessment-dimensions">
      {Object.entries(data.dimensions).map(([key, dimension]) => (
        <div key={key} className="border-t border-border pt-4">
          <p className="workspace-eyebrow">{t(`workflow.dimensions.${key}`)}</p>
          <h3 className="mt-2">
            {t(`workflow.status.${dimension.status}`, { defaultValue: dimension.status.replace(/_/g, " ") })}
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">{dimension.note}</p>
        </div>
      ))}
    </div>
  );
}

import { useTranslation } from "react-i18next";

import type { AnalyzeResponse } from "@/api/client";
import { ScreenHeader } from "@/components/States";
import { Card } from "@/components/ui/card";

export function NextScreen({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  return (
    <section>
      <ScreenHeader title={t("next.title")} summary={t("next.summary")} />
      <Card>
        <h3 className="font-medium">{t("next.actions")}</h3>
        {data.verdict.actions.length ? (
          <ul className="list-disc ps-5">
            {data.verdict.actions.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground">{t("next.none")}</p>
        )}
        <p className="mt-3 text-sm text-muted-foreground">{t("next.pending")}</p>
      </Card>
      <Card className="mt-4" id="limitations">
        <h3 className="font-medium">{t("next.limitations")}</h3>
        <ul className="list-disc ps-5 text-sm">
          {data.limitations.map((l) => (
            <li key={l}>{l}</li>
          ))}
        </ul>
      </Card>
    </section>
  );
}

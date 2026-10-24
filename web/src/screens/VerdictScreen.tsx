import { useTranslation } from "react-i18next";

import type { AnalyzeResponse } from "@/api/client";
import { AiSummary } from "@/components/AiSummary";
import { WorkflowDimensions } from "@/components/WorkflowDimensions";
import { Num } from "@/components/Num";
import { SafetyLimits } from "@/components/SafetyLimits";
import { ScreenHeader } from "@/components/States";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { GateCard, VerdictLabel } from "@/components/Verdict";
import { useStore } from "@/store";

export function VerdictScreen({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const setScreen = useStore((s) => s.setScreen);
  const request = useStore((s) => s.request);
  const v = data.verdict;
  return (
    <section>
      <ScreenHeader title={t("verdict.title")} summary={t("verdict.summary")} />
      <Card className="space-y-3" data-testid="verdict-card">
        <div className="flex flex-wrap items-center gap-3">
          <VerdictLabel label={v.label} large />
          <span className="text-sm">
            {t("verdict.grade")}: <strong>{v.grade}</strong>
          </span>
          {v.p_go && (
            <span className="text-sm">
              {t("verdict.pGo")}: {v.p_go_note && <span aria-hidden="true">≤ </span>}
              <Num v={v.p_go} label={t("verdict.pGo")} />
              {v.p_go_note && <span className="text-muted-foreground"> ({t("verdict.pGoUpper")})</span>}
            </span>
          )}
        </div>
        {v.p_go_note && <p className="text-sm text-muted-foreground">{v.p_go_note}</p>}
        <div>
          <h3 className="font-medium">{t("verdict.reasons")}</h3>
          <ul className="list-disc ps-5">
            {v.reasons.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </div>
        {v.actions.length > 0 && (
          <div>
            <h3 className="font-medium">{t("verdict.actions")}</h3>
            <ul className="list-disc ps-5">
              {v.actions.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          </div>
        )}
        <p className="text-sm text-muted-foreground">{t("verdict.disclaimer")}</p>
      </Card>

      {request && (
        <div className="mt-4">
          <AiSummary request={request} />
        </div>
      )}

      <WorkflowDimensions data={data} />
      <SafetyLimits gates={data.gates} />
      <h3 className="mb-2 mt-6 font-medium">{t("verdict.gates")}</h3>
      <div className="grid gap-3 md:grid-cols-2">
        {data.gates.map((g) => (
          <GateCard key={g.id} gate={g} />
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button variant="outline" onClick={() => setScreen("diagnosis")}>
          {t("verdict.seeDiagnosis")}
        </Button>
        <Button variant="outline" onClick={() => setScreen("memo")} data-testid="open-memo">
          {t("memo.open")}
        </Button>
      </div>
    </section>
  );
}

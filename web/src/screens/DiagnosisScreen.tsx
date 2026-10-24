import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { AnalyzeResponse } from "@/api/client";
import { ExceedanceBars } from "@/charts/ExceedanceBars";
import { EvidenceExplorer } from "@/components/EvidenceExplorer";
import { FunctionalComparison } from "@/components/FunctionalComparison";
import { Num } from "@/components/Num";
import { ScreenHeader } from "@/components/States";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { gloss } from "@/lib/glossary";

export function DiagnosisScreen({ data }: { data: AnalyzeResponse }) {
  const { t, i18n } = useTranslation();
  const [table, setTable] = useState(false);
  const rows = data.diagnosis;
  const limiting = rows.find((d) => d.limiting)?.name ?? t("diagnosis.none");
  return (
    <section>
      <ScreenHeader title={t("diagnosis.title")} summary={t("diagnosis.summary")} />
      <p className="mb-4 text-sm text-muted-foreground">
        {t("safety.policy")} {t("safety.units")}
      </p>
      <p className="mb-3 text-sm" aria-live="polite">
        {t("diagnosis.textSummary", { n: rows.length, limiting })}
      </p>
      <Button
        variant="outline"
        size="sm"
        className="mb-3"
        onClick={() => setTable((x) => !x)}
        aria-pressed={table}
      >
        {table ? t("diagnosis.showChart") : t("diagnosis.showTable")}
      </Button>
      {!table && <ExceedanceBars rows={rows} />}
      <div className={table ? "relative overflow-x-auto" : "relative mt-4 overflow-x-auto"} tabIndex={0}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-start">
              <th scope="col" className="py-2 text-start">
                #
              </th>
              <th scope="col" className="text-start">
                {t("diagnosis.compound")}
              </th>
              <th scope="col" className="text-start">
                {t("diagnosis.role")}
              </th>
              <th scope="col" className="text-start">
                {t("diagnosis.level")}
              </th>
              <th scope="col" className="text-start">
                {t("diagnosis.tolerance")}
              </th>
              <th scope="col" className="text-start">
                {t("workflow.thresholdCheck")}
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr
                key={d.compound}
                className="border-b border-border align-top"
                data-testid={`diag-${d.compound}`}
              >
                <td className="py-2">{d.rank}</td>
                <td>
                  {gloss(d.name, i18n.language)}
                  {d.limiting && (
                    <span className="ms-2 rounded bg-bad/15 px-1 text-xs text-bad">
                      {t("diagnosis.limiting")}
                    </span>
                  )}
                  {d.note && <p className="text-xs text-muted-foreground">{d.note}</p>}
                  {d.basis !== "unknown" && (
                    <p className="text-xs text-muted-foreground">
                      {d.basis.replace(/_/g, " ")}
                      {d.method && ` · ${d.method}`}
                    </p>
                  )}
                </td>
                <td>{d.role === "gate" ? t("diagnosis.gate") : t("diagnosis.tunable")}</td>
                <td>
                  {d.level ? (
                    <Num v={d.level} label={t("diagnosis.level")} />
                  ) : (
                    <span className="text-muted-foreground">{t("diagnosis.noData")}</span>
                  )}
                </td>
                <td>
                  {d.tolerance ? (
                    <Num v={d.tolerance} label={t("diagnosis.tolerance")} />
                  ) : (
                    <span className="text-muted-foreground">{t("diagnosis.noLimit")}</span>
                  )}
                </td>
                <td>
                  {d.p_exceed ? (
                    <Num v={d.p_exceed} label={t("workflow.thresholdCheck")} />
                  ) : (
                    t(`workflow.comparison.${d.comparison_status ?? "not_estimated"}`, {
                      defaultValue: (d.comparison_status ?? "not_estimated").replace(/_/g, " "),
                    })
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <FunctionalComparison data={data} />
      <EvidenceExplorer />
      <h3 className="mb-2 mt-6 font-medium">{t("diagnosis.issues")}</h3>
      <div className="grid gap-3 md:grid-cols-2">
        {data.issues.map((i) => (
          <Card key={i.kind + i.message} data-testid={`issue-${i.kind}`}>
            <p>{i.message}</p>
            {i.value && <Num v={i.value} className="mt-1" />}
          </Card>
        ))}
      </div>
    </section>
  );
}

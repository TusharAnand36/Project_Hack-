import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { AnalyzeResponse } from "@/api/client";
import { Tornado } from "@/charts/Tornado";
import { LabResult } from "@/components/LabResult";
import { Num } from "@/components/Num";
import { ScreenHeader } from "@/components/States";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { formatLakhCrore, formatValue } from "@/lib/format";
import { cn } from "@/lib/utils";

const MARK: Record<string, { icon: string; cls: string }> = {
  true: { icon: "✓", cls: "text-ok" },
  false: { icon: "✕", cls: "text-bad" },
  null: { icon: "?", cls: "text-muted-foreground" },
};

function Readiness({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const r = data.readiness;
  if (!r) return null;
  return (
    <Card data-testid="readiness">
      <h3 className="font-medium">
        {t("next.readiness")}: <span className="font-bold">{t(`next.grades.${r.grade}`)}</span>
      </h3>
      <ul className="mt-2 space-y-1 text-sm">
        {r.checks.map((c) => {
          const mk = MARK[String(c.passed)];
          return (
            <li key={c.id} className="flex flex-wrap items-center gap-2">
              <span aria-hidden="true" className={cn("w-4 font-bold", mk.cls)}>
                {mk.icon}
              </span>
              <span>{c.label}</span>
              {c.value ? (
                <Num v={c.value} />
              ) : (
                c.passed === null && (
                  <span className="text-muted-foreground">({t("next.notComputable")})</span>
                )
              )}
              {c.threshold && (
                <span className="text-muted-foreground">
                  {t("next.threshold")} <Num v={c.threshold} />
                </span>
              )}
              <span className="sr-only">
                {c.passed === null ? t("next.notComputable") : c.passed ? "✓" : "✕"}
              </span>
            </li>
          );
        })}
      </ul>
      {r.must_demonstrate.length > 0 && (
        <>
          <h4 className="mt-3 font-medium">{t("next.mustDemonstrate")}</h4>
          <ul className="list-disc ps-5 text-sm">
            {r.must_demonstrate.map((m) => (
              <li key={m.item}>
                <strong>{m.item}</strong>
                {m.test_id && <> ({m.test_id.replace(/_/g, " ")})</>}: {m.acceptance}
              </li>
            ))}
          </ul>
        </>
      )}
    </Card>
  );
}

function Voi({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const [table, setTable] = useState(false);
  const v = data.voi;
  if (!v) return <Card className="text-warn">{t("next.notAvailable")}</Card>;
  const rec = v.tests.find((x) => x.test_id === v.recommended_test);
  return (
    <>
      <Card className="border-s-4 border-primary" data-testid="recommended-test">
        <h3 className="font-medium">{t("next.recommended")}</h3>
        {rec ? (
          <div className="mt-1 space-y-1">
            <p className="text-lg font-semibold">{rec.name}</p>
            <p className="text-sm">
              {t("next.evsi")}: <Num v={rec.evsi} />
              {rec.evsi_is_upper_bound && (
                <span className="text-muted-foreground"> · {t("next.upperBound")}</span>
              )}
            </p>
            <p className="text-sm">
              {t("next.cost")}:{" "}
              {rec.cost_inr ? (
                <Num v={rec.cost_inr} />
              ) : (
                t("next.costMissing", { evsi: formatValue(rec.evsi.value, "inr") })
              )}{" "}
              · {t(`next.worth.${rec.worth_it}`)}
            </p>
          </div>
        ) : (
          <p className="mt-1 font-semibold">{t("next.noTest")}</p>
        )}
        <p className="mt-2 text-sm text-muted-foreground">{v.recommendation}</p>
      </Card>

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-sm" aria-live="polite">
            {v.evppi[0] && t("next.evppiSummary", { label: v.evppi[0].label })}
          </p>
          <Button variant="outline" size="sm" onClick={() => setTable((x) => !x)} aria-pressed={table}>
            {table ? t("next.showChart") : t("next.showTable")}
          </Button>
        </div>
        {!table ? (
          <Tornado
            title={t("next.evppiTitle")}
            bars={v.evppi.map((e) => ({ label: e.label, value: e.value.value }))}
          />
        ) : (
          <table className="mt-2 w-full text-sm">
            <tbody>
              {v.evppi.map((e) => (
                <tr key={e.input} className="border-b border-border">
                  <th scope="row" className="py-1 text-start font-normal">
                    {e.label}
                  </th>
                  <td>
                    <Num v={e.value} />
                  </td>
                  <td className="text-muted-foreground">{e.test_id?.replace(/_/g, " ") ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <Card>
        <h3 className="mb-2 font-medium">{t("next.tests")}</h3>
        <div className="relative overflow-x-auto" tabIndex={0}>
          <table className="w-full min-w-[36rem] text-sm">
            <thead>
              <tr className="border-b border-border">
                <th scope="col" className="text-start">
                  {t("next.test")}
                </th>
                <th scope="col" className="text-start">
                  {t("next.inputs")}
                </th>
                <th scope="col" className="text-start">
                  {t("next.evsi")}
                </th>
                <th scope="col" className="text-start">
                  {t("next.cost")}
                </th>
                <th scope="col" className="text-start">
                  {t("next.roi")}
                </th>
              </tr>
            </thead>
            <tbody>
              {v.tests.map((x) => (
                <tr key={x.test_id} className="border-b border-border align-top">
                  <td className="py-1">{x.name}</td>
                  <td className="text-xs">{x.inputs.join("; ")}</td>
                  <td>
                    <Num v={x.evsi} />
                  </td>
                  <td>
                    {x.cost_inr ? (
                      <Num v={x.cost_inr} />
                    ) : (
                      <span className="text-muted-foreground">{t(`next.worth.${x.worth_it}`)}</span>
                    )}
                  </td>
                  <td>{x.roi ? <Num v={x.roi} /> : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card>
        <h3 className="font-medium">{t("next.utility")}</h3>
        <p className="text-sm">{v.utility.description}</p>
        <dl className="mt-2 grid gap-1 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-muted-foreground">{t("next.campaign")}</dt>
            <dd>
              <Num v={v.utility.campaign_kg_cake} />
            </dd>
          </div>
          <div>
            <dt className="text-muted-foreground">{t("next.eNow")}</dt>
            <dd>
              <Num v={v.e_now} />
            </dd>
          </div>
          <div>
            <dt className="text-muted-foreground">{t("next.evpi")}</dt>
            <dd>
              <Num v={v.evpi} />
            </dd>
          </div>
        </dl>
        <p className="mt-2 text-xs text-muted-foreground">{v.note}</p>
      </Card>
    </>
  );
}

function PlanBlock({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const p = data.plan;
  if (!p) return null;
  const b = p.budget_inr;
  return (
    <Card data-testid="plan">
      <h3 className="mb-2 font-medium">{t("next.plan")}</h3>
      <div className="relative overflow-x-auto" tabIndex={0}>
        <table className="w-full min-w-[44rem] text-sm">
          <thead>
            <tr className="border-b border-border">
              <th scope="col" className="text-start">
                {t("next.test")}
              </th>
              <th scope="col" className="text-start">
                {t("next.samplePlan")}
              </th>
              <th scope="col" className="text-start">
                {t("next.cost")}
              </th>
              <th scope="col" className="text-start">
                {t("next.turnaround")}
              </th>
              <th scope="col" className="text-start">
                {t("next.acceptance")}
              </th>
              <th scope="col" className="text-start">
                {t("next.why")}
              </th>
            </tr>
          </thead>
          <tbody>
            {p.tests.map((x) => (
              <tr key={x.test_id} className="border-b border-border align-top">
                <td className="py-1">
                  {x.name}
                  <p className="text-xs text-muted-foreground">{x.method}</p>
                </td>
                <td className="text-xs">{x.sample_plan}</td>
                <td>{x.cost_inr ? <Num v={x.cost_inr} /> : "—"}</td>
                <td>{x.turnaround_days ? <Num v={x.turnaround_days} /> : "—"}</td>
                <td className="text-xs">{x.acceptance}</td>
                <td className="text-xs">{x.why}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h4 className="mt-4 font-medium">{t("next.timeline")}</h4>
      <ol className="mt-1 space-y-2 text-sm">
        {p.timeline.map((m) => (
          <li key={m.months} className="grid gap-1 sm:grid-cols-[5rem_1fr_1fr]">
            <span className="font-semibold">{m.months}</span>
            <span>{m.work}</span>
            <span className="text-muted-foreground">{m.output}<span className="mt-2 block text-xs">{m.decision_gate}</span></span>
          </li>
        ))}
      </ol>
      <p className="mt-4 text-sm">
        <strong>{t("next.budget")}:</strong>{" "}
        {b.low != null && b.high != null ? (
          <span title={`₹${b.low.toLocaleString("en-IN")} – ₹${b.high.toLocaleString("en-IN")}`}>
            {formatLakhCrore(b.low)} – {formatLakhCrore(b.high)} [{b.tag}]
          </span>
        ) : null}{" "}
        <span className="text-muted-foreground">{b.note}</span>
      </p>
      <p className="mt-2 text-sm">
        <strong>{t("next.partner")}:</strong> {p.pilot_partner}
      </p>
    </Card>
  );
}

export function NextScreen({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  return (
    <section className="space-y-4">
      <ScreenHeader title={t("next.title")} summary={t("next.summary")} />
      <section className="mb-6 border-l-2 border-primary pl-4" data-testid="critical-tests">
        <h3>{t("workflow.criticalTests")}</h3>
        <p className="mt-2 text-sm">{data.voi_note}</p>
        <ul className="mt-3 list-disc ps-5 text-sm">
          {data.plan?.tests
            .filter((test) => test.why.startsWith("Critical safety"))
            .map((test) => (
              <li key={test.test_id}>
                <strong>{test.name}</strong>: {test.acceptance}
              </li>
            ))}
        </ul>
        {data.feedback_context.next_actions.length > 0 && (
          <>
            <h4 className="mt-4">{t("feedback.learning")}</h4>
            <ul className="list-disc ps-5 text-sm">
              {data.feedback_context.next_actions.map((action) => (
                <li key={action}>{action}</li>
              ))}
            </ul>
          </>
        )}
      </section>
      <Voi data={data} />
      <LabResult data={data} />
      <Readiness data={data} />
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
      </Card>
      <PlanBlock data={data} />
      <Card id="limitations">
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

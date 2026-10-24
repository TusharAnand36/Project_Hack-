import { useTranslation } from "react-i18next";

import type { AnalyzeResponse, Range, Value } from "@/api/client";
import { useDataFile, useSources } from "@/api/hooks";
import { WorkflowDimensions } from "@/components/WorkflowDimensions";
import { Num } from "@/components/Num";
import { Button } from "@/components/ui/button";
import { VerdictLabel } from "@/components/Verdict";
import { useStore } from "@/store";

const today = () =>
  new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Kolkata",
  }).format(new Date());

function collectSources(...leaves: (Value | Range | null | undefined)[]): string[] {
  return [...new Set(leaves.flatMap((l) => l?.source_ids ?? []))];
}

/** One-page decision memo (FR-19). Printed with the browser: "Save as PDF" gives the file. */
export function MemoScreen({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const request = useStore((s) => s.request);
  const setScreen = useStore((s) => s.setScreen);
  const sources = useSources();
  const applications = useDataFile<{ applications: { id: string; name: string }[] }>("applications");
  const applicationName = applications.data?.applications.find(
    (app) => app.id === request?.application,
  )?.name;
  const v = data.verdict;
  const top = data.chains[0];
  const rec = data.voi?.tests.find((x) => x.test_id === data.voi?.recommended_test);
  const g1 = data.gates.find((g) => g.id === "G1");
  const ids = [
    ...new Set([
      ...collectSources(
        g1?.prior_p_fail,
        g1?.limit,
        top?.protein_pct_final,
        top?.cost_inr_per_kg_protein,
        data.pea.landed_inr_per_kg_protein,
        data.pea.b2b_cross_check_inr_per_kg_protein,
      ),
      ...data.gates.flatMap((gate) => gate.checks.flatMap((check) => check.limit.source_ids ?? [])),
      ...data.functional_comparison.properties.flatMap((property) => property.source_ids),
    ]),
  ];
  return (
    <article className="memo mx-auto max-w-3xl space-y-3 text-sm" data-testid="memo">
      <div className="no-print flex flex-wrap gap-2">
        <Button onClick={() => window.print()} data-testid="memo-print">
          {t("memo.print")}
        </Button>
        <Button
          variant="outline"
          onClick={() => {
            const blob = new Blob([JSON.stringify({ request, result: data }, null, 2)], {
              type: "application/json",
            });
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = "upcycle-compass-case.json";
            anchor.click();
            URL.revokeObjectURL(url);
          }}
        >
          {t("workflow.downloadCase")}
        </Button>
        <Button variant="outline" onClick={() => setScreen("verdict")}>
          {t("memo.back")}
        </Button>
      </div>
      <header className="flex flex-wrap items-baseline justify-between gap-2 border-b border-border pb-2">
        <h2 className="text-xl font-semibold">
          {t("app.title")} · {t("memo.title")}
        </h2>
        <span>
          {t("memo.date")}:{" "}
          {data.meta.generated_at
            ? new Date(data.meta.generated_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })
            : today()}{" "}
          · engine {data.meta.engine_version} · dataset {data.meta.dataset_version}
        </span>
      </header>
      <section>
        <h3 className="font-semibold">{t("memo.batch")}</h3>
        <p>
          {data.case_id && <>Case {data.case_id} · </>}
          {request?.batch?.lot_id && <>Lot {request.batch.lot_id} · </>}
          {request?.byproduct.replace(/_/g, " ")} →{" "}
          {applicationName ?? request?.application.replace(/_/g, " ")} ({request?.market ?? "domestic"})
        </p>
      </section>
      <section className="flex flex-wrap items-center gap-3">
        <h3 className="font-semibold">{t("memo.verdict")}</h3>
        <VerdictLabel label={v.label} />
        <span>{v.grade}</span>
        {v.p_go && (
          <span>
            P(GO) {v.p_go_note ? "≤ " : ""}
            <Num v={v.p_go} />
          </span>
        )}
      </section>
      <WorkflowDimensions data={data} />
      <section>
        <h3 className="font-semibold">{t("memo.why")}</h3>
        <ul className="list-disc ps-5">
          {v.reasons.slice(0, 4).map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
      </section>
      <section>
        <h3 className="font-semibold">{t("memo.gates")}</h3>
        <p>{data.gates.map((g) => `${g.id} ${g.name}: ${g.state}`).join(" · ")}</p>
      </section>
      <section>
        <h3 className="font-semibold">{t("memo.chain")}</h3>
        {top ? (
          <p>
            {top.steps.join(" → ") || t("chains.rawFlour")} ({top.tier.replace("_", " ")}): protein{" "}
            <Num v={top.protein_pct_final} />, P(spec) <Num v={top.p_spec} />
          </p>
        ) : (
          <p>{t("memo.noChain")}</p>
        )}
      </section>
      <section>
        <h3 className="font-semibold">{t("memo.vsPea")}</h3>
        <p>
          {top?.cost_inr_per_kg_protein && (
            <>
              <Num v={top.cost_inr_per_kg_protein} /> {top.cost_complete ? "" : "(lower bound)"} vs{" "}
            </>
          )}
          <Num v={data.pea.landed_inr_per_kg_protein} /> ({data.pea.duty_mode})
        </p>
        <p>
          {data.cost_target.formula}: <Num v={data.cost_target.amount} />
        </p>
        <p>
          {data.cost_target.note} {top?.cost_missing.join("; ")}
        </p>
      </section>
      {!data.voi && (
        <section>
          <h3 className="font-semibold">{t("memo.test")}</h3>
          <p>
            {data.plan?.tests[0]?.name ?? t("workflow.notEstimated")}: {data.plan?.tests[0]?.why}
          </p>
          <p>{data.voi_note}</p>
        </section>
      )}
      {data.voi && (
        <section>
          <h3 className="font-semibold">{t("memo.test")}</h3>
          <p>
            {rec ? (
              <>
                {rec.name}: <Num v={rec.evsi} />
              </>
            ) : (
              data.voi.recommendation
            )}
          </p>
        </section>
      )}
      {data.readiness && (
        <section>
          <h3 className="font-semibold">{t("memo.readiness")}</h3>
          <p>
            {data.readiness.grade}:{" "}
            {data.readiness.checks
              .map((c) => `${c.passed === null ? "?" : c.passed ? "✓" : "✕"} ${c.label}`)
              .join("; ")}
          </p>
        </section>
      )}
      <section>
        <h3 className="font-semibold">{t("memo.limits")}</h3>
        <ul className="list-disc ps-5">
          {data.limitations.slice(0, 4).map((l) => (
            <li key={l}>{l}</li>
          ))}
        </ul>
      </section>
      <section>
        <h3 className="font-semibold">{t("memo.sources")}</h3>
        <ol className="memo-sources list-decimal ps-5">
          {ids.map((id) => (
            <li key={id}>
              {sources.get(id)?.citation ?? id}
              {sources.get(id)?.url && <> · {sources.get(id)?.url}</>}
            </li>
          ))}
        </ol>
      </section>
      <footer className="border-t border-border pt-2">
        <p>{t("memo.notes")}</p>
        <p className="font-medium">{t("verdict.disclaimer")}</p>
      </footer>
    </article>
  );
}

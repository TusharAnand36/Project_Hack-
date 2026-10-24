import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import type { AnalyzeResponse, Chain, Range } from "@/api/client";
import { ParetoScatter } from "@/charts/ParetoScatter";
import { Num } from "@/components/Num";
import { ScreenHeader } from "@/components/States";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useStore } from "@/store";

type Col = "rank" | "retained" | "protein" | "cost" | "pspec" | "eu";

const sortValue: Record<Col, (c: Chain) => number> = {
  rank: (c) => c.rank,
  retained: (c) => c.protein_retained?.p50 ?? Number.NEGATIVE_INFINITY,
  protein: (c) => c.protein_pct_final?.p50 ?? Number.NEGATIVE_INFINITY,
  cost: (c) => c.cost_inr_per_kg_protein?.p50 ?? Number.POSITIVE_INFINITY,
  pspec: (c) => c.p_spec?.value ?? Number.NEGATIVE_INFINITY,
  eu: (c) => c.e_utility?.value ?? Number.NEGATIVE_INFINITY,
};

function Steps({ chain }: { chain: Chain }) {
  const { t } = useTranslation();
  return (
    <>
      {chain.steps.length ? chain.steps.map((s) => s.replace(/_/g, " ")).join(" → ") : t("chains.rawFlour")}
    </>
  );
}

function Cell({ v, missing }: { v?: Range | null; missing?: string }) {
  return v ? (
    <Num v={v} showRange={false} />
  ) : (
    <span className="text-muted-foreground">{missing ?? "—"}</span>
  );
}

function ChainDetail({ chain, data }: { chain: Chain; data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const raw = data.chains.find((c) => c.id === "raw_flour");
  const row = (label: string, before?: Range | null, after?: Range | null) => (
    <tr className="border-b border-border">
      <th scope="row" className="py-2 text-start font-normal text-muted-foreground">
        {label}
      </th>
      <td>{before ? <Num v={before} /> : "—"}</td>
      <td>
        {after ? (
          <Num v={after} />
        ) : (
          <span className="text-muted-foreground">{t("chains.notComputable")}</span>
        )}
      </td>
    </tr>
  );
  return (
    <Card className="mt-4 space-y-4" data-testid="chain-detail" aria-live="polite">
      <h3 className="font-medium">
        {t("chains.detail")}: <Steps chain={chain} />
      </h3>
      <p className="text-sm text-muted-foreground">{chain.assessment_note}</p>
      <p className="text-sm">
        {t("workflow.economicState")}: {chain.economic_status.replace(/_/g, " ")}
      </p>
      <details>
        <summary className="min-h-11 cursor-pointer underline">{t("workflow.studyEvidence")}</summary>
        <pre className="max-h-80 overflow-auto whitespace-pre-wrap text-xs">
          {JSON.stringify(chain.evidence, null, 2)}
        </pre>
      </details>
      <div className="relative overflow-x-auto" tabIndex={0}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th scope="col" />
              <th scope="col" className="text-start">
                {t("chains.before")}
              </th>
              <th scope="col" className="text-start">
                {t("chains.after")}
              </th>
            </tr>
          </thead>
          <tbody>
            {row(t("chains.proteinPct"), raw?.protein_pct_final, chain.protein_pct_final)}
            {row(t("chains.retained"), raw?.protein_retained, chain.protein_retained)}
            {row(t("workflow.ingredientYield"), raw?.ingredient_yield, chain.ingredient_yield)}
            {row(t("workflow.initialProtein"), raw?.initial_protein_kg, chain.initial_protein_kg)}
            {row(t("workflow.recoveredProtein"), raw?.recovered_protein_kg, chain.recovered_protein_kg)}
            {(raw?.phytate_pct_final || chain.phytate_pct_final) &&
              row(t("chains.phytate"), raw?.phytate_pct_final, chain.phytate_pct_final)}
            {(raw?.tia_pct_raw_final || chain.tia_pct_raw_final) &&
              row(t("chains.tia"), raw?.tia_pct_raw_final, chain.tia_pct_raw_final)}
            {row(t("chains.ofi"), raw?.ofi, chain.ofi)}
            {row(t("chains.cost"), raw?.cost_inr_per_kg_protein, chain.cost_inr_per_kg_protein)}
          </tbody>
        </table>
      </div>
      <div>
        <h4 className="font-medium">{t("chains.criteria")}</h4>
        <ul className="space-y-1 text-sm">
          {chain.criteria.map((c) => (
            <li key={c.id} className="flex flex-wrap items-center gap-2">
              <span>{t(`chains.criterion.${c.id}`)}</span>
              <Num v={c.target} />
              <span aria-hidden="true">→</span>
              {c.p_pass ? (
                <Num v={c.p_pass} />
              ) : (
                <span className="text-muted-foreground">{t("chains.notEvaluated")}</span>
              )}
              {c.note && <span className="text-xs text-muted-foreground">({c.note})</span>}
            </li>
          ))}
        </ul>
      </div>
      {chain.transferred.length > 0 && (
        <div>
          <h4 className="font-medium text-warn">{t("chains.transferred")}</h4>
          <ul className="list-disc ps-5 text-sm">
            {chain.transferred.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </div>
      )}
      {chain.no_data_inputs.length > 0 && (
        <div>
          <h4 className="font-medium">{t("chains.noDataInputs")}</h4>
          <p className="text-sm">{chain.no_data_inputs.join("; ")}</p>
        </div>
      )}
      {chain.cost_missing.length > 0 && (
        <div>
          <h4 className="font-medium">{t("chains.costMissing")}</h4>
          <p className="text-sm">{chain.cost_missing.join("; ")}</p>
        </div>
      )}
    </Card>
  );
}

function Pareto({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const viable = data.chains.filter(
    (c) => c.p_spec && c.p_spec.value >= 0.2 && c.protein_retained && c.cost_inr_per_kg_protein,
  );
  const ties = data.picks?.ties ?? [];
  if (viable.length === 0)
    return <p className="mb-4 text-sm text-muted-foreground">{t("chains.paretoNone")}</p>;
  return (
    <Card className="mb-4">
      <p className="mb-2 text-sm" aria-live="polite">
        {t("chains.paretoSummary", { n: viable.length, front: viable.filter((c) => c.pareto).length })}
      </p>
      <ParetoScatter chains={viable} title={t("chains.paretoTitle")} />
      {ties.length > 0 && (
        <p className="mt-2 text-xs text-muted-foreground">
          {t("chains.ties", { pairs: ties.map((p) => p.join(" ≈ ")).join("; ") })}
        </p>
      )}
    </Card>
  );
}

export function ChainsScreen({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const selected = useStore((s) => s.selectedChain);
  const select = useStore((s) => s.selectChain);
  const [sort, setSort] = useState<{ col: Col; dir: 1 | -1 }>({ col: "rank", dir: 1 });
  const rows = useMemo(
    () => [...data.chains].sort((a, b) => sort.dir * (sortValue[sort.col](a) - sortValue[sort.col](b))),
    [data.chains, sort],
  );
  const chosen = data.chains.find((c) => c.id === selected);

  const header = (col: Col, label: string) => {
    const active = sort.col === col;
    return (
      <th
        scope="col"
        className="text-start"
        aria-sort={active ? (sort.dir === 1 ? "ascending" : "descending") : "none"}
      >
        <button
          type="button"
          className="min-h-9 font-medium underline-offset-4 hover:underline"
          aria-label={t("chains.sortBy", { col: label })}
          onClick={() =>
            setSort({
              col,
              dir: active ? (-sort.dir as 1 | -1) : col === "pspec" || col === "retained" ? -1 : 1,
            })
          }
        >
          {label} {active ? (sort.dir === 1 ? "▲" : "▼") : ""}
        </button>
      </th>
    );
  };

  return (
    <section>
      <ScreenHeader title={t("chains.title")} summary={t("chains.summary")} />
      {data.chains.length > 0 && <Pareto data={data} />}
      {data.chains.length === 0 ? (
        <Card>{t("chains.none")}</Card>
      ) : (
        <>
          <p className="mb-2 text-sm text-muted-foreground">
            {t("chains.shown", { shown: data.meta.chains_shown, total: data.meta.chains_total })}
          </p>
          <div className="relative overflow-x-auto" tabIndex={0}>
            <table className="w-full min-w-[44rem] text-sm">
              <thead>
                <tr className="border-b border-border">
                  {header("rank", "#")}
                  <th scope="col" className="text-start">
                    {t("chains.steps")}
                  </th>
                  <th scope="col" className="text-start">
                    {t("chains.tier")}
                  </th>
                  {header("retained", t("chains.retained"))}
                  {header("protein", t("chains.proteinPct"))}
                  <th scope="col" className="text-start">
                    {t("chains.ofi")}
                  </th>
                  {header("cost", t("chains.cost"))}
                  {header("pspec", t("chains.pSpec"))}
                  {header("eu", t("chains.eu"))}
                  <th scope="col" className="text-start">
                    {t("chains.badges")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((c) => (
                  <tr
                    key={c.id}
                    className={cn("border-b border-border align-top", c.id === selected && "bg-muted")}
                  >
                    <td className="py-2">{c.rank || "—"}</td>
                    <td>
                      <button
                        type="button"
                        className="min-h-9 text-start underline underline-offset-4"
                        aria-expanded={c.id === selected}
                        onClick={() => select(c.id === selected ? null : c.id)}
                        data-testid={`chain-${c.id}`}
                      >
                        <Steps chain={c} />
                      </button>
                    </td>
                    <td>{t(`chains.tiers.${c.tier}`)}</td>
                    <td>
                      <Cell v={c.protein_retained} />
                    </td>
                    <td>
                      <Cell v={c.protein_pct_final} />
                    </td>
                    <td>
                      <Cell v={c.ofi} missing={t("chains.notComputable")} />
                    </td>
                    <td>
                      <Cell v={c.cost_inr_per_kg_protein} missing={t("chains.notComputable")} />
                    </td>
                    <td>
                      <Num v={c.p_spec} />
                    </td>
                    <td>{c.e_utility ? <Num v={c.e_utility} /> : "—"}</td>
                    <td className="text-xs">{c.badges.map((b) => t(`chains.badge.${b}`)).join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {chosen && <ChainDetail chain={chosen} data={data} />}
        </>
      )}
    </section>
  );
}

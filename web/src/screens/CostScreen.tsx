import * as Slider from "@radix-ui/react-slider";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { AnalyzeRequest, AnalyzeResponse } from "@/api/client";
import { CostStack, type Part } from "@/charts/CostStack";
import { Num } from "@/components/Num";
import { ScreenHeader } from "@/components/States";
import { TagChip } from "@/components/TagChip";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { formatNumber, formatValue } from "@/lib/format";
import { useStore } from "@/store";

type DutyMode = NonNullable<NonNullable<AnalyzeRequest["pea"]>["duty_mode"]>;
const DUTY_MODES: DutyMode[] = ["full_stack_44", "full_stack_49", "bcd_only_igst_credited_22"];

function SliderRow({
  id,
  label,
  value,
  min,
  max,
  step,
  display,
  onChange,
}: {
  id: string;
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  display: string;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span id={`${id}-label`}>{label}</span>
        <span className="flex items-center gap-1 font-semibold tabular-nums">
          {display} <TagChip tag="assumed" />
        </span>
      </div>
      <Slider.Root
        className="relative mt-2 flex h-11 touch-none select-none items-center"
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={([v]) => onChange(v)}
        data-testid={`slider-${id}`}
      >
        <Slider.Track className="relative h-2 grow rounded-full bg-muted">
          <Slider.Range className="absolute h-full rounded-full bg-primary" />
        </Slider.Track>
        <Slider.Thumb
          aria-labelledby={`${id}-label`}
          aria-valuetext={display}
          className="block h-6 w-6 rounded-full border-2 border-primary bg-background"
        />
      </Slider.Root>
    </div>
  );
}

export function CostScreen({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const request = useStore((s) => s.request);
  const patch = useStore((s) => s.patchRequest);
  const [scenario, setScenario] = useState<string | null>(null);
  const pea = data.pea;
  const top = data.chains.find((c) => c.cost_inr_per_kg_protein) ?? data.chains[0];
  const inp = pea.inputs;
  const base = request?.pea?.base_usd_per_kg ?? inp.base_usd_per_kg.p50;
  const fx = request?.pea?.usd_inr ?? inp.usd_inr.p50;
  const freightPct = request?.pea?.freight_pct ?? inp.freight_frac.p50 * 100;
  const duty = (request?.pea?.duty_mode ?? pea.duty_mode) as DutyMode;
  const scale = request?.scale_kg_day ?? 500;

  const setPea = (k: keyof NonNullable<AnalyzeRequest["pea"]>, v: number | string) =>
    patch((r) => ({ ...r, pea: { ...r.pea, [k]: v } }));

  // approximate P50 split of the pea landed cost per kg protein
  const prot = inp.protein_frac.p50;
  const baseInr = (inp.base_usd_per_kg.p50 * inp.usd_inr.p50) / prot;
  const freight = baseInr * inp.freight_frac.p50;
  const dutyAmt = (baseInr + freight) * inp.duty_frac.p50;
  const allocation = pea.landed_inr_per_kg_protein.p50 / (baseInr + freight + dutyAmt);
  const peaParts: Part[] = [
    { key: "base", value: baseInr * allocation },
    { key: "freight", value: freight * allocation },
    { key: "duty", value: dutyAmt * allocation },
  ];
  const ourParts: Part[] = top?.cost_breakdown
    ? Object.entries(top.cost_breakdown).map(([key, r]) => ({ key, value: r.p50 }))
    : [];
  const shock = pea.scenarios.find((s) => s.id === scenario);

  return (
    <section>
      <ScreenHeader title={t("cost.title")} summary={t("cost.summary")} />
      <section className="mb-5 border-l-2 border-primary pl-4 text-sm">
        <h3>{t("workflow.costTarget")}</h3>
        <p className="mt-2">
          <Num v={data.cost_target.amount} />
        </p>
        <p>{data.cost_target.formula}</p>
        <p className="mt-2 text-muted-foreground">{data.cost_target.note}</p>
        <p className="mt-3">{t("workflow.costBoundary")}</p>
        <p className="mt-3">{t("workflow.marginFormula")}</p>
        <details className="mt-3">
          <summary className="min-h-9 cursor-pointer underline">{t("workflow.dutyBasis")}</summary>
          <p>{t("workflow.dutyExplanation")}</p>
        </details>
      </section>
      {top?.cost_inr_per_kg_protein ? (
        <Card className="space-y-3">
          <p className="text-sm">
            {t("cost.chartSummary", {
              ours: formatValue(top.cost_inr_per_kg_protein.p50, "inr"),
              pea: formatValue(pea.landed_inr_per_kg_protein.p50, "inr"),
            })}
          </p>
          <CostStack
            ours={ourParts}
            pea={peaParts}
            oursLabel={t("cost.ours", { chain: `#${top.rank}` })}
            peaLabel={t("cost.pea")}
          />
          <p className="text-xs text-muted-foreground">{t("cost.allocationNote")}</p>
          {!top.cost_complete && <p className="text-sm text-warn">{t("cost.lowerBound")}</p>}
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">
                {t("cost.ours", { chain: top.id.replace(/_/g, " ") })}
              </dt>
              <dd>
                <Num v={top.cost_inr_per_kg_protein} />
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">{t("cost.pea")}</dt>
              <dd data-testid="pea-landed">
                <Num v={pea.landed_inr_per_kg_protein} />
              </dd>
            </div>
            {top.margin_vs_pea && (
              <div>
                <dt className="text-muted-foreground">{t("cost.margin")}</dt>
                <dd>
                  <Num v={top.margin_vs_pea} />
                </dd>
              </div>
            )}
            {top.p_margin_positive && (
              <div>
                <dt className="text-muted-foreground">{t("cost.pMargin")}</dt>
                <dd>
                  <Num v={top.p_margin_positive} />
                </dd>
              </div>
            )}
            {pea.break_even_base_usd_per_kg && (
              <div>
                <dt className="text-muted-foreground">{t("cost.breakEven")}</dt>
                <dd>
                  <Num v={pea.break_even_base_usd_per_kg} />
                  {pea.break_even_note && (
                    <p className="text-xs text-muted-foreground">{pea.break_even_note}</p>
                  )}
                </dd>
              </div>
            )}
            {pea.b2b_cross_check_inr_per_kg_protein && (
              <div>
                <dt className="text-muted-foreground">{t("cost.b2b")}</dt>
                <dd>
                  <Num v={pea.b2b_cross_check_inr_per_kg_protein} />
                </dd>
              </div>
            )}
          </dl>
        </Card>
      ) : (
        <Card className="space-y-2">
          <p className="text-warn">{t("cost.notComputable")}</p>
          <p className="text-sm">
            {t("cost.pea")}:{" "}
            <span data-testid="pea-landed">
              <Num v={pea.landed_inr_per_kg_protein} />
            </span>
          </p>
        </Card>
      )}

      <p className="mt-4 text-sm text-muted-foreground">
        {t("cost.sharedBenchmark")} <Num v={pea.landed_inr_per_kg_product} />
      </p>

      <Card className="mt-4 space-y-4">
        <h3 className="font-medium">{t("cost.sliders")}</h3>
        <SliderRow
          id="base"
          label={t("cost.base")}
          value={base}
          min={2.3}
          max={4.6}
          step={0.1}
          display={formatValue(base, "usd")}
          onChange={(v) => setPea("base_usd_per_kg", Math.round(v * 10) / 10)}
        />
        <SliderRow
          id="fx"
          label={t("cost.fx")}
          value={fx}
          min={85}
          max={110}
          step={0.5}
          display={formatNumber(fx, 1)}
          onChange={(v) => setPea("usd_inr", v)}
        />
        <SliderRow
          id="freight"
          label={t("cost.freight")}
          value={freightPct}
          min={0}
          max={20}
          step={0.5}
          display={`${formatNumber(freightPct, 1)}%`}
          onChange={(v) => setPea("freight_pct", v)}
        />
        <SliderRow
          id="scale"
          label={t("cost.scale")}
          value={scale}
          min={100}
          max={10000}
          step={100}
          display={formatNumber(scale, 0)}
          onChange={(v) => patch((r) => ({ ...r, scale_kg_day: v }))}
        />
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            {t("cost.duty")}
            <select
              className="mt-1 block min-h-11 w-full rounded-md border border-border bg-background px-3"
              value={duty}
              onChange={(e) => setPea("duty_mode", e.target.value)}
            >
              {DUTY_MODES.map((m) => (
                <option key={m} value={m}>
                  {t(`cost.dutyModes.${m}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="flex min-h-11 items-center gap-2 self-end text-sm">
            <input
              type="checkbox"
              className="h-5 w-5"
              checked={duty === "bcd_only_igst_credited_22"}
              onChange={(e) =>
                setPea("duty_mode", e.target.checked ? "bcd_only_igst_credited_22" : "full_stack_44")
              }
            />
            {t("cost.gstCredit")}
          </label>
        </div>
        <Button
          variant="outline"
          onClick={() =>
            patch((r) => ({
              ...r,
              scale_kg_day: null,
              pea: { ...r.pea, base_usd_per_kg: null, usd_inr: null, freight_pct: null },
            }))
          }
        >
          {t("cost.reset")}
        </Button>
      </Card>

      <Card className="mt-4">
        <h3 className="mb-2 font-medium">{t("cost.scenarios")}</h3>
        <div className="flex flex-wrap gap-2">
          {pea.scenarios.map((s) => (
            <Button
              key={s.id}
              variant={scenario === s.id ? "primary" : "outline"}
              aria-pressed={scenario === s.id}
              onClick={() => setScenario(scenario === s.id ? null : s.id)}
            >
              {s.name}
            </Button>
          ))}
        </div>
        {shock && (
          <p className="mt-3 text-sm" aria-live="polite">
            {shock.name}: {t("cost.pea")} <Num v={shock.landed} />
          </p>
        )}
      </Card>
    </section>
  );
}

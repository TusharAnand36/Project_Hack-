import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { useForm, useWatch, type FieldPath, type UseFormRegister } from "react-hook-form";
import { useTranslation } from "react-i18next";

import { api } from "@/api/client";
import { useDataFile, useDataReport, usePresets } from "@/api/hooks";
import { ScreenHeader } from "@/components/States";
import { VoiceInput } from "@/components/VoiceInput";
import { Button } from "@/components/ui/button";
import { Card, Skeleton } from "@/components/ui/card";
import {
  EMPTY_FORM,
  formSchema,
  fromRequest,
  toRequest,
  type FormInput,
  type FormOutput,
} from "@/forms/schema";
import { formatValue } from "@/lib/format";
import { cn } from "@/lib/utils";
import { useStore } from "@/store";

interface Named {
  id: string;
  name: string;
  notes?: string;
  composition?: Record<
    string,
    {
      value?: number | null;
      dist?: { low: number; high: number } | null;
      unit: string;
      tag: string;
      source_id?: string;
      notes?: string;
      conditions?: Record<string, unknown>;
    }
  >;
}

const field = "mt-1 block min-h-11 w-full rounded-md border border-border bg-background px-3";
const HL = "ring-2 ring-warn";

/** /parse-text field names -> form field names (for highlighting what the reader filled). */
const PARSED_TO_FORM: Record<string, string> = {
  byproduct: "byproduct",
  application: "application",
  market: "market",
  scale_kg_day: "scale",
  raw_price_inr_per_kg: "price",
  "targets.min_protein_pct": "minProtein",
  "targets.max_cost_inr_per_kg_protein": "maxCost",
  "batch.protein_pct": "protein",
  "batch.moisture_pct": "moisture",
  "batch.afb1_ppb": "afb1",
  "batch.ffa_pct": "ffa",
  "batch.phytate_pct": "phytate",
  "process.oil_route": "oilRoute",
  "process.stabilised": "stabilised",
  "process.hours_since_milling": "hours",
  "constraints.no_solvents": "noSolvents",
};
const BATCH_FIELDS = new Set([
  "protein",
  "moisture",
  "afb1",
  "ffa",
  "phytate",
  "oilRoute",
  "stabilised",
  "hours",
]);

function Labelled({
  id,
  label,
  error,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  children: ReactNode;
}) {
  const { t } = useTranslation();
  return (
    <div>
      <label htmlFor={id} className="flex items-center gap-2 text-sm font-medium">
        {label}
      </label>
      {children}
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-bad" role="alert">
          {t(error)}
        </p>
      )}
    </div>
  );
}

function NumField({
  name,
  label,
  register,
  errors,
  highlighted,
}: {
  name: FieldPath<FormInput>;
  label: string;
  register: UseFormRegister<FormInput>;
  errors: Record<string, { message?: string } | undefined>;
  highlighted?: boolean;
}) {
  const err = errors[name]?.message;
  return (
    <Labelled id={name} label={label} error={err}>
      <input
        id={name}
        inputMode="decimal"
        className={cn(field, highlighted && HL)}
        aria-invalid={!!err}
        aria-describedby={err ? `${name}-error` : undefined}
        {...register(name)}
      />
    </Labelled>
  );
}

function TriField({
  name,
  label,
  register,
  highlighted,
}: {
  name: FieldPath<FormInput>;
  label: string;
  register: UseFormRegister<FormInput>;
  highlighted?: boolean;
}) {
  const { t } = useTranslation();
  return (
    <Labelled id={name} label={label}>
      <select id={name} className={cn(field, highlighted && HL)} {...register(name)}>
        <option value="unknown">{t("input.unknown")}</option>
        <option value="yes">{t("input.yes")}</option>
        <option value="no">{t("input.no")}</option>
      </select>
    </Labelled>
  );
}

export function InputScreen() {
  const { t } = useTranslation();
  const runRequest = useStore((s) => s.runRequest);
  const request = useStore((s) => s.request);
  const presets = usePresets();
  const byproducts = useDataFile<{ byproducts: Named[] }>("byproducts");
  const applications = useDataFile<{ applications: Named[] }>("applications");
  const treatments = useDataFile<{ equipment: string[]; treatments: Named[] }>("treatments");
  const report = useDataReport();

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm<FormInput, unknown, FormOutput>({
    resolver: zodResolver(formSchema),
    defaultValues: request ? fromRequest(request) : EMPTY_FORM,
  });
  const selectedMaterial = useWatch({ control, name: "byproduct" });
  const costMethod = useWatch({ control, name: "costMethod" });
  const materialReference = byproducts.data?.byproducts.find((item) => item.id === selectedMaterial);
  const [parsedReview, setParsedReview] = useState(false);
  const [parsedConfirmed, setParsedConfirmed] = useState(false);
  useEffect(() => {
    if (request) reset(fromRequest(request));
  }, [request, reset]);

  const { i18n } = useTranslation();
  const [text, setText] = useState("");
  const [highlight, setHighlight] = useState<Set<string>>(new Set());
  const [batchOpen, setBatchOpen] = useState(false);
  const parse = useMutation({
    mutationFn: () => api.parseText(text, null, i18n.language),
    onSuccess: (r) => {
      if (!r.payload) return;
      reset(fromRequest(r.payload));
      setParsedReview(true);
      setParsedConfirmed(false);
      const hl = new Set(r.changed.map((k) => PARSED_TO_FORM[k]).filter(Boolean));
      setHighlight(hl);
      if ([...hl].some((f) => BATCH_FIELDS.has(f))) setBatchOpen(true);
    },
  });
  const hl = (name: string) => highlight.has(name);

  const errs = errors as Record<string, { message?: string } | undefined>;
  const num = (name: FieldPath<FormInput>, label: string) => (
    <NumField name={name} label={label} register={register} errors={errs} highlighted={hl(name)} />
  );

  const textField = (name: FieldPath<FormInput>, label: string) => (
    <Labelled id={name} label={label} error={errs[name]?.message}>
      <input id={name} className={field} {...register(name)} />
    </Labelled>
  );
  const selectField = (name: FieldPath<FormInput>, label: string, options: string[]) => (
    <Labelled id={name} label={label}>
      <select id={name} className={field} {...register(name)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {t(`workflow.options.${option}`, { defaultValue: option.replace(/_/g, " ") })}
          </option>
        ))}
      </select>
    </Labelled>
  );

  return (
    <section className="workspace-input" aria-labelledby="input-title">
      <div className="workspace-input-intro">
        <ScreenHeader
          eyebrow={t("workspace.eyebrow")}
          title={t("workspace.inputTitle")}
          accent={t("workspace.inputAccent")}
          summary={t("input.summary")}
        />
        <figure className="workspace-intro-photo" aria-hidden="true">
          <img src="/images/circular-ingredients.webp" alt="" width="1122" height="1402" />
          <figcaption>{t("site.photoCaption")}</figcaption>
        </figure>
      </div>

      <h3 id="input-title" className="workspace-section-title">
        <span className="workspace-section-number" aria-hidden="true">
          01
        </span>
        {t("input.presets")}
      </h3>
      <div className="workspace-presets grid gap-4 lg:grid-cols-3">
        {presets.isPending && [0, 1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-28" />)}
        {presets.data?.map((p, i) => (
          <Card key={p.id} className="workspace-preset flex flex-col justify-between gap-5">
            <div className="workspace-preset-top">
              <span className="workspace-eyebrow">
                {t("workspace.sample")} 0{i + 1}
              </span>
              <span aria-hidden="true">↗</span>
            </div>
            <div>
              <h4>{p.title}</h4>
              <p className="workspace-preset-story">{p.story}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button data-testid={`preset-${p.id}`} onClick={() => runRequest(p.payload, p.id)}>
                {t("input.presetRun")}
              </Button>
              <Button variant="outline" onClick={() => reset(fromRequest(p.payload))}>
                {t("input.presetEdit")}
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <aside className="my-6 border-l-2 border-primary pl-4 text-sm text-muted-foreground">
        <p>{t("input.peaResearch")}</p>
        <a
          className="mt-2 inline-block underline underline-offset-4"
          href="https://doi.org/10.1016/j.fochx.2025.102898"
          target="_blank"
          rel="noreferrer"
        >
          {t("input.peaPaper")}
        </a>
      </aside>

      <Card className="workspace-describe">
        <div className="workspace-describe-intro">
          <p className="workspace-eyebrow">{t("workspace.yourWords")}</p>
          <label htmlFor="describe" className="workspace-describe-title">
            {t("ai.describe")}
          </label>
          <p id="describe-hint" className="text-sm text-muted-foreground">
            {t("ai.describeHint")}
          </p>
        </div>
        <div>
          <textarea
            id="describe"
            rows={3}
            maxLength={2000}
            className="mt-2 block w-full rounded-md border border-border bg-background p-3"
            aria-describedby="describe-hint"
            value={text}
            onChange={(e) => setText(e.target.value)}
            data-testid="describe"
          />
          <VoiceInput
            onTranscript={(said) => setText((prev) => (prev.trim() ? `${prev.trim()} ${said}` : said))}
            onTypeInstead={() => document.getElementById("describe")?.focus()}
          />
          <Button
            type="button"
            className="mt-2"
            disabled={text.trim().length < 3 || parse.isPending}
            onClick={() => parse.mutate()}
            data-testid="fill-form"
          >
            {parse.isPending ? t("ai.filling") : t("ai.fill")}
          </Button>
          <p role="status" aria-live="polite" className="mt-2 text-sm" data-testid="parse-message">
            {parse.data?.payload && t("ai.filled", { provider: parse.data.provider })}
            {parse.data && !parse.data.payload && <span className="text-warn">{parse.data.message}</span>}
            {parse.isError && <span className="text-warn">{t("ai.failed")}</span>}
          </p>
        </div>
      </Card>

      <form
        className="workspace-form space-y-6"
        noValidate
        onSubmit={handleSubmit((v) => runRequest(toRequest(v)))}
        aria-labelledby="form-title"
      >
        <h3 id="form-title" className="workspace-section-title">
          <span className="workspace-section-number" aria-hidden="true">
            02
          </span>
          {t("input.form")}
        </h3>
        <div className="workspace-input-panel grid gap-6 sm:grid-cols-2">
          <Labelled id="byproduct" label={t("input.byproduct")} error={errs.byproduct?.message}>
            <select id="byproduct" className={cn(field, hl("byproduct") && HL)} {...register("byproduct")}>
              <option value="">{t("input.choose")}</option>
              {byproducts.data?.byproducts.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </Labelled>
          <Labelled id="application" label={t("input.application")} error={errs.application?.message}>
            <select
              id="application"
              className={cn(field, hl("application") && HL)}
              {...register("application")}
            >
              <option value="">{t("input.choose")}</option>
              {applications.data?.applications.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </Labelled>
          <Labelled id="market" label={t("input.market")}>
            <select id="market" className={cn(field, hl("market") && HL)} {...register("market")}>
              <option value="domestic">{t("input.marketDomestic")}</option>
              <option value="export_EU">{t("input.marketEU")}</option>
            </select>
          </Labelled>
          {num("scale", t("input.scale"))}
          <div className="grid grid-cols-[1fr_auto] gap-2">
            {num("price", t("input.price"))}
            <Labelled id="priceUnit" label={t("input.priceUnit")}>
              <select id="priceUnit" className={field} {...register("priceUnit")}>
                <option value="per_kg">{t("input.perKg")}</option>
                <option value="per_quintal">{t("input.perQuintal")}</option>
                <option value="per_tonne">{t("input.perTonne")}</option>
              </select>
            </Labelled>
          </div>
        </div>

        {materialReference && (
          <details className="workspace-input-panel">
            <summary className="min-h-11 cursor-pointer py-2 font-medium">
              {t("workflow.referenceData")}: {materialReference.name}
            </summary>
            <p className="my-3 text-sm text-muted-foreground">{t("workflow.referenceWarning")}</p>
            <div className="overflow-x-auto" tabIndex={0}>
              <table className="w-full text-sm">
                <tbody>
                  {Object.entries(materialReference.composition ?? {}).map(([key, param]) => (
                    <tr key={key} className="border-b border-border align-top">
                      <th className="py-3 pe-4 text-start font-medium" scope="row">
                        {key.replace(/_/g, " ")}
                      </th>
                      <td className="py-3 pe-4">
                        {param.value ??
                          (param.dist
                            ? `${param.dist.low}–${param.dist.high}`
                            : t("workflow.notEstimated"))}{" "}
                        {param.unit}
                      </td>
                      <td className="py-3">
                        <span>{param.tag === "published" ? t("workflow.reviewReported") : param.tag}</span>
                        <p className="text-xs">{param.source_id}</p>
                        <p className="text-xs text-muted-foreground">{param.notes}</p>
                        {param.conditions && (
                          <p className="text-xs text-muted-foreground">{JSON.stringify(param.conditions)}</p>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-sm">{materialReference.notes}</p>
          </details>
        )}

        <fieldset className="workspace-input-panel grid gap-6 sm:grid-cols-2">
          <legend className="mb-2 font-medium">{t("workflow.lotIdentity")}</legend>
          {selectField("materialForm", t("workflow.materialForm"), [
            "unknown",
            "cake",
            "meal",
            "flour",
            "concentrate",
            "isolate",
          ])}
          {textField("lotId", t("workflow.lotId"))}
          {textField("supplier", t("workflow.supplier"))}
          {textField("origin", t("workflow.origin"))}
          {textField("sourceReference", t("workflow.sourceReference"))}
          {textField("routeReference", t("workflow.routeReference"))}
          <TriField name="dehulled" label={t("workflow.dehulled")} register={register} />
          {textField("regulatoryReference", t("workflow.regulatoryReference"))}
          {textField("functionalReference", t("workflow.functionalReference"))}
          {textField("priceSource", t("workflow.priceSource"))}
          {textField("priceDate", t("workflow.priceDate"))}
          {textField("priceBoundary", t("workflow.priceBoundary"))}
        </fieldset>

        <fieldset className="workspace-input-panel grid gap-6 sm:grid-cols-2">
          <legend className="mb-2 font-medium">{t("input.targets")}</legend>
          {num("minProtein", t("input.minProtein"))}
          {selectField("targetProteinBasis", t("workflow.targetProteinBasis"), ["as_received", "dry_matter"])}
          {selectField("costMethod", t("workflow.costMethod"), ["manual", "benchmark", "product_budget"])}
          {costMethod === "manual" && num("maxCost", t("input.maxCost"))}
          {costMethod === "benchmark" && num("discount", t("workflow.discount"))}
          {costMethod === "product_budget" && (
            <>
              {num("productBudget", t("workflow.productBudget"))}
              {num("productProtein", t("workflow.productProtein"))}
            </>
          )}
          <p className="text-xs text-muted-foreground sm:col-span-2">
            {t(`workflow.costFormula.${costMethod}`)}
          </p>
          {num("maxOfi", t("input.maxOfi"))}
          {selectField("phytateType", t("workflow.phytateType"), ["not_established", "internal_target"])}
          {num("maxPhytate", t("input.maxPhytate"))}
          {textField("sensoryRubric", t("workflow.sensoryRubric"))}
        </fieldset>

        <fieldset className="workspace-input-panel">
          <legend className="mb-2 font-medium">{t("input.constraints")}</legend>
          <label className="flex min-h-11 items-center gap-2">
            <input
              type="checkbox"
              className={cn("h-5 w-5", hl("noSolvents") && HL)}
              {...register("noSolvents")}
            />{" "}
            {t("input.noSolvents")}
          </label>
          <p className="mt-2 text-sm font-medium">{t("input.equipment")}</p>
          <div className="flex flex-wrap gap-x-4">
            {treatments.data?.equipment.map((e) => (
              <label key={e} className="flex min-h-11 items-center gap-2">
                <input type="checkbox" className="h-5 w-5" value={e} {...register("equipment")} />{" "}
                {e.replace(/_/g, " ")}
              </label>
            ))}
          </div>
          <p className="mt-2 text-sm font-medium">{t("input.exclude")}</p>
          <div className="flex flex-wrap gap-x-4">
            {treatments.data?.treatments.map((tr) => (
              <label key={tr.id} className="flex min-h-11 items-center gap-2">
                <input type="checkbox" className="h-5 w-5" value={tr.id} {...register("exclude")} /> {tr.name}
              </label>
            ))}
          </div>
        </fieldset>

        <details
          className="workspace-input-panel"
          open={batchOpen}
          onToggle={(e) => setBatchOpen((e.target as HTMLDetailsElement).open)}
        >
          <summary className="min-h-11 cursor-pointer py-2 font-medium">{t("input.batch")}</summary>
          <p className="mb-3 text-sm text-muted-foreground">{t("input.batchHint")}</p>
          <div className="grid gap-4 sm:grid-cols-2">
            {num("protein", t("input.protein"))}
            {selectField("proteinBasis", t("workflow.proteinBasis"), [
              "unknown",
              "as_received",
              "dry_matter",
            ])}
            {num("nFactor", t("input.nFactor"))}
            {num("fat", t("workflow.fat"))}
            {num("ash", t("workflow.ash"))}
            {num("crudeFibre", t("workflow.crudeFibre"))}
            {num("dietaryFibre", t("workflow.dietaryFibre"))}
            {textField("method", t("workflow.method"))}
            {textField("laboratory", t("workflow.laboratory"))}
            {textField("reportReference", t("workflow.reportReference"))}
            {textField("reportDate", t("workflow.reportDate"))}
            {num("moisture", t("input.moisture"))}
            {num("ffa", t("input.ffa"))}
            {num("phytate", t("input.phytate"))}
          </div>
          <h4 className="mb-2 mt-6 font-medium">{t("input.contaminants")}</h4>
          <p className="mb-3 text-sm text-muted-foreground">{t("input.contaminantHint")}</p>
          <div className="grid gap-4 sm:grid-cols-2">
            {num("hexane", t("input.hexane"))}
            {num("afb1", t("input.afb1"))}
            {num("totalAflatoxins", t("input.totalAflatoxins"))}
            {num("lead", t("input.lead"))}
            {num("cadmium", t("input.cadmium"))}
            {num("arsenic", t("input.arsenic"))}
            {num("mercury", t("input.mercury"))}
          </div>
          <h4 className="mb-2 mt-4 font-medium">{t("input.process")}</h4>
          <div className="grid gap-4 sm:grid-cols-2">
            <Labelled id="oilRoute" label={t("input.oilRoute")}>
              <select id="oilRoute" className={cn(field, hl("oilRoute") && HL)} {...register("oilRoute")}>
                <option value="">{t("input.oilRouteUnknown")}</option>
                <option value="cold_pressed">{t("input.cold_pressed")}</option>
                <option value="expeller">{t("input.expeller")}</option>
                <option value="solvent">{t("input.solvent")}</option>
                <option value="other">{t("workflow.options.other")}</option>
              </select>
            </Labelled>
            {num("hours", t("input.hours"))}
            <TriField
              name="stabilised"
              label={t("input.stabilised")}
              register={register}
              highlighted={hl("stabilised")}
            />
            <TriField
              name="foodGrade"
              label={t("input.foodGrade")}
              register={register}
              highlighted={hl("foodGrade")}
            />
            <TriField
              name="hygienic"
              label={t("input.hygienic")}
              register={register}
              highlighted={hl("hygienic")}
            />
            <TriField
              name="sorted"
              label={t("input.sorted")}
              register={register}
              highlighted={hl("sorted")}
            />
            <TriField
              name="hexaneCert"
              label={t("input.hexaneCert")}
              register={register}
              highlighted={hl("hexaneCert")}
            />
          </div>
        </details>

        {parsedReview && (
          <label className="flex min-h-11 items-center gap-3 text-sm">
            <input
              type="checkbox"
              checked={parsedConfirmed}
              onChange={(event) => setParsedConfirmed(event.target.checked)}
            />
            {t("workflow.confirmParsed")}
          </label>
        )}
        <Button
          type="submit"
          disabled={parsedReview && !parsedConfirmed}
          className="workspace-analyse"
          data-testid="submit"
        >
          {t("input.submit")}
          <span aria-hidden="true">↗</span>
        </Button>
      </form>

      {report.data && (
        <Card className="workspace-completeness mt-6">
          <p className="text-sm font-medium">{t("input.completeness")}</p>
          <meter
            className="mt-2 h-3 w-full"
            min={0}
            max={report.data.params_total}
            value={report.data.params_filled}
            aria-label={t("input.completeness")}
          />
          <p className="text-sm text-muted-foreground">
            {t("input.completenessText", {
              filled: report.data.params_filled,
              total: report.data.params_total,
              ab: formatValue(report.data.completeness_ab_share, "prob"),
            })}
          </p>
        </Card>
      )}
    </section>
  );
}

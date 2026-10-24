import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, type ReactNode } from "react";
import { useForm, useWatch, type FieldPath, type UseFormRegister } from "react-hook-form";
import { useTranslation } from "react-i18next";

import { useDataFile, useDataReport, usePresets } from "@/api/hooks";
import { ScreenHeader } from "@/components/States";
import { TagChip } from "@/components/TagChip";
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
import { useStore } from "@/store";

interface Named {
  id: string;
  name: string;
}

const field = "mt-1 block min-h-11 w-full rounded-md border border-border bg-background px-3";

function Labelled({
  id,
  label,
  error,
  chip,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  chip?: ReactNode;
  children: ReactNode;
}) {
  const { t } = useTranslation();
  return (
    <div>
      <label htmlFor={id} className="flex items-center gap-2 text-sm font-medium">
        {label} {chip}
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

function DefaultChip() {
  const { t } = useTranslation();
  return (
    <span className="rounded border border-border px-1 text-[0.7rem] text-muted-foreground">
      {t("input.default")}
    </span>
  );
}

function NumField({
  name,
  label,
  register,
  errors,
  value,
  measured,
}: {
  name: FieldPath<FormInput>;
  label: string;
  register: UseFormRegister<FormInput>;
  errors: Record<string, { message?: string } | undefined>;
  value: unknown;
  measured?: boolean;
}) {
  const err = errors[name]?.message;
  const filled = typeof value === "string" && value.trim() !== "";
  return (
    <Labelled
      id={name}
      label={label}
      error={err}
      chip={filled ? <TagChip tag={measured ? "measured" : "assumed"} /> : <DefaultChip />}
    >
      <input
        id={name}
        inputMode="decimal"
        className={field}
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
}: {
  name: FieldPath<FormInput>;
  label: string;
  register: UseFormRegister<FormInput>;
}) {
  const { t } = useTranslation();
  return (
    <Labelled id={name} label={label}>
      <select id={name} className={field} {...register(name)}>
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
  const values = useWatch({ control });
  useEffect(() => {
    if (request) reset(fromRequest(request));
  }, [request, reset]);

  const errs = errors as Record<string, { message?: string } | undefined>;
  const num = (name: FieldPath<FormInput>, label: string, measured = false) => (
    <NumField
      name={name}
      label={label}
      register={register}
      errors={errs}
      value={values[name as keyof FormInput]}
      measured={measured}
    />
  );

  return (
    <section aria-labelledby="input-title">
      <ScreenHeader title={t("nav.input")} summary={t("input.summary")} />

      <h3 id="input-title" className="mb-2 font-medium">
        {t("input.presets")}
      </h3>
      <div className="grid gap-3 sm:grid-cols-3">
        {presets.isPending && [0, 1, 2].map((i) => <Skeleton key={i} className="h-28" />)}
        {presets.data?.map((p) => (
          <Card key={p.id} className="flex flex-col justify-between gap-2">
            <div>
              <p className="font-medium">{p.title}</p>
              <p className="text-sm text-muted-foreground">{p.story}</p>
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

      <form
        className="mt-6 space-y-6"
        noValidate
        onSubmit={handleSubmit((v) => runRequest(toRequest(v)))}
        aria-labelledby="form-title"
      >
        <h3 id="form-title" className="font-medium">
          {t("input.form")}
        </h3>
        <div className="grid gap-4 sm:grid-cols-2">
          <Labelled id="byproduct" label={t("input.byproduct")} error={errs.byproduct?.message}>
            <select id="byproduct" className={field} {...register("byproduct")}>
              <option value="">{t("input.choose")}</option>
              {byproducts.data?.byproducts.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </Labelled>
          <Labelled id="application" label={t("input.application")} error={errs.application?.message}>
            <select id="application" className={field} {...register("application")}>
              <option value="">{t("input.choose")}</option>
              {applications.data?.applications.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </Labelled>
          <Labelled id="market" label={t("input.market")}>
            <select id="market" className={field} {...register("market")}>
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

        <fieldset className="grid gap-4 sm:grid-cols-2">
          <legend className="mb-2 font-medium">{t("input.targets")}</legend>
          {num("minProtein", t("input.minProtein"))}
          {num("maxCost", t("input.maxCost"))}
          {num("maxOfi", t("input.maxOfi"))}
          {num("maxPhytate", t("input.maxPhytate"))}
        </fieldset>

        <fieldset>
          <legend className="mb-2 font-medium">{t("input.constraints")}</legend>
          <label className="flex min-h-11 items-center gap-2">
            <input type="checkbox" className="h-5 w-5" {...register("noSolvents")} /> {t("input.noSolvents")}
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

        <details className="rounded-lg border border-border p-4">
          <summary className="min-h-11 cursor-pointer py-2 font-medium">{t("input.batch")}</summary>
          <p className="mb-3 text-sm text-muted-foreground">{t("input.batchHint")}</p>
          <div className="grid gap-4 sm:grid-cols-2">
            {num("protein", t("input.protein"), true)}
            {num("nFactor", t("input.nFactor"), true)}
            {num("moisture", t("input.moisture"), true)}
            {num("ffa", t("input.ffa"), true)}
            {num("afb1", t("input.afb1"), true)}
            {num("phytate", t("input.phytate"), true)}
          </div>
          <h4 className="mb-2 mt-4 font-medium">{t("input.process")}</h4>
          <div className="grid gap-4 sm:grid-cols-2">
            <Labelled id="oilRoute" label={t("input.oilRoute")}>
              <select id="oilRoute" className={field} {...register("oilRoute")}>
                <option value="">{t("input.oilRouteUnknown")}</option>
                <option value="cold_pressed">{t("input.cold_pressed")}</option>
                <option value="expeller">{t("input.expeller")}</option>
                <option value="solvent">{t("input.solvent")}</option>
              </select>
            </Labelled>
            {num("hours", t("input.hours"), true)}
            <TriField name="stabilised" label={t("input.stabilised")} register={register} />
            <TriField name="foodGrade" label={t("input.foodGrade")} register={register} />
            <TriField name="hygienic" label={t("input.hygienic")} register={register} />
            <TriField name="sorted" label={t("input.sorted")} register={register} />
            <TriField name="hexaneCert" label={t("input.hexaneCert")} register={register} />
          </div>
        </details>

        <Button type="submit" data-testid="submit">
          {t("input.submit")}
        </Button>
      </form>

      {report.data && (
        <Card className="mt-6">
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

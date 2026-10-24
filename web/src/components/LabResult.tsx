import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { api, type AnalyzeResponse, type Snapshot } from "@/api/client";
import { useStore } from "@/store";

import { Num } from "./Num";
import { Button } from "./ui/button";
import { Card } from "./ui/card";

const field = "mt-1 block min-h-11 w-full rounded-md border border-border bg-background px-3";

function options(data: AnalyzeResponse, t: (k: string) => string): { key: string; label: string }[] {
  const out = new Map<string, string>();
  for (const e of data.voi?.evppi ?? []) {
    if (
      e.input.startsWith("cmp.") ||
      e.input.startsWith("t.") ||
      e.input === "bp.protein" ||
      e.input === "gate.G1.u"
    ) {
      out.set(e.input, e.label);
    }
  }
  if (data.gates.some((g) => g.id === "G1")) out.set("gate.G1.u", t("lab.g1Label"));
  for (const d of data.diagnosis)
    if (d.role === "tunable") out.set(`cmp.${d.compound}`, `${d.name.toLowerCase()} ${t("lab.baseline")}`);
  const gateFields: Record<string, string> = {
    total_aflatoxins: "total_aflatoxins_ppb",
    hexane_residue: "hexane_ppm",
    lead: "pb_ppm",
    cadmium: "cd_ppm",
    arsenic: "arsenic_ppm",
    mercury: "hg_ppm",
  };
  for (const row of data.diagnosis)
    if (gateFields[row.compound]) out.set(`batch.${gateFields[row.compound]}`, row.name);
  out.set("bp.protein", t("lab.proteinLabel"));
  return [...out].map(([key, label]) => ({ key, label }));
}

function Row({ label, before, after }: { label: string; before: React.ReactNode; after: React.ReactNode }) {
  return (
    <tr className="border-b border-border align-top">
      <th scope="row" className="py-1 text-start font-normal text-muted-foreground">
        {label}
      </th>
      <td>{before}</td>
      <td>{after}</td>
    </tr>
  );
}

function Compare({ before, after }: { before: Snapshot; after: Snapshot }) {
  const { t } = useTranslation();
  const changed = (a: unknown, b: unknown) =>
    JSON.stringify(a) !== JSON.stringify(b) ? "font-semibold underline decoration-2 underline-offset-4" : "";
  return (
    <div className="relative overflow-x-auto" tabIndex={0}>
      <table className="w-full min-w-[30rem] text-sm" data-testid="before-after">
        <thead>
          <tr className="border-b border-border">
            <th scope="col" />
            <th scope="col" className="text-start">
              {t("lab.before")}
            </th>
            <th scope="col" className="text-start">
              {t("lab.after")}
            </th>
          </tr>
        </thead>
        <tbody>
          <Row
            label={t("lab.verdict")}
            before={before.verdict}
            after={<span className={changed(before.verdict, after.verdict)}>{after.verdict}</span>}
          />
          <Row
            label={t("lab.grade")}
            before={before.grade}
            after={<span className={changed(before.grade, after.grade)}>{after.grade}</span>}
          />
          <Row
            label={t("lab.pGo")}
            before={before.p_go ? <Num v={before.p_go} /> : "—"}
            after={after.p_go ? <Num v={after.p_go} /> : "—"}
          />
          <Row
            label={t("lab.bestChain")}
            before={before.best_chain ?? "—"}
            after={
              <span className={changed(before.best_chain, after.best_chain)}>{after.best_chain ?? "—"}</span>
            }
          />
          <Row
            label={t("lab.pSpec")}
            before={before.best_p_spec ? <Num v={before.best_p_spec} /> : "—"}
            after={after.best_p_spec ? <Num v={after.best_p_spec} /> : "—"}
          />
          <Row
            label={t("lab.recommended")}
            before={before.recommended_test?.replace(/_/g, " ") ?? "—"}
            after={
              <span className={changed(before.recommended_test, after.recommended_test)}>
                {after.recommended_test?.replace(/_/g, " ") ?? "—"}
              </span>
            }
          />
          <Row
            label={t("lab.topDriver")}
            before={before.evppi[0]?.label ?? "—"}
            after={
              <span className={changed(before.evppi[0]?.input, after.evppi[0]?.input)}>
                {after.evppi[0]?.label ?? "—"}
              </span>
            }
          />
        </tbody>
      </table>
    </div>
  );
}

/** "Enter one lab number and the recommendation sharpens" (source plan §12.12). */
export function LabResult({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const request = useStore((s) => s.request);
  const runRequest = useStore((s) => s.runRequest);
  const opts = options(data, t);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<"hplc" | "positive" | "negative">("hplc");
  const [value, setValue] = useState("");
  const [cv, setCv] = useState("");
  const [method, setMethod] = useState("");
  const [report, setReport] = useState({
    unit: "",
    basis: "as_received" as "as_received" | "dry_matter" | "unknown" | "not_applicable",
    laboratory: "",
    report_reference: "",
    report_date: "",
  });
  const unitFor = (key: string) =>
    key === "gate.G1.u" || key === "batch.total_aflatoxins_ppb"
      ? "µg/kg"
      : key.startsWith("batch.")
        ? "mg/kg"
        : key === "bp.protein"
          ? "%"
          : key === "cmp.phytic_acid" || key === "cmp.tannins"
            ? "% dry basis"
            : key === "cmp.trypsin_inhibitor"
              ? "% of raw activity"
              : "fraction";
  const isGate = input === "gate.G1.u";
  const m = useMutation({
    mutationFn: () =>
      api.updateEvidence({
        request: request!,
        ...report,
        batch_id: request?.batch?.lot_id ?? null,
        input,
        value: isGate && mode !== "hplc" ? null : Number(value),
        result: isGate && mode !== "hplc" ? mode : null,
        cv: cv.trim() ? Number(cv) / 100 : null,
        method: method.trim() || null,
      }),
  });
  const needsValue = !(isGate && mode !== "hplc");
  const valid = input && (!needsValue || (value.trim() !== "" && Number.isFinite(Number(value))));
  return (
    <Card data-testid="lab-result">
      <h3 className="font-medium">{t("lab.title")}</h3>
      <p className="text-sm text-muted-foreground">{t("lab.hint")}</p>
      <form
        className="mt-3 grid gap-3 sm:grid-cols-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (valid) m.mutate();
        }}
      >
        <label className="text-sm">
          {t("lab.input")}
          <select
            className={field}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              setReport({
                ...report,
                unit: unitFor(e.target.value),
                basis: e.target.value.startsWith("t.") ? "not_applicable" : e.target.value === "cmp.phytic_acid" ? "dry_matter" : "as_received",
              });
            }}
            data-testid="lab-input"
          >
            <option value="">{t("lab.choose")}</option>
            {opts.map((o) => (
              <option key={o.key} value={o.key}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          {t("workflow.unit")}
          <select
            className={field}
            value={report.unit}
            onChange={(e) => setReport({ ...report, unit: e.target.value })}
          >
            {["", "%", "% dry basis", "% of raw activity", "fraction", "µg/kg", "mg/kg"].map((unit) => (
              <option key={unit} value={unit}>
                {unit || t("input.choose")}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          {t("workflow.proteinBasis")}
          <select
            className={field}
            value={report.basis}
            onChange={(e) => setReport({ ...report, basis: e.target.value as typeof report.basis })}
          >
            {["as_received", "dry_matter", "unknown", "not_applicable"].map((basis) => (
              <option key={basis} value={basis}>
                {basis.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </label>
        {(["laboratory", "report_reference", "report_date"] as const).map((key) => (
          <label className="text-sm" key={key}>
            {t(`workflow.reportFields.${key}`)}
            <input
              className={field}
              value={report[key]}
              maxLength={key === "report_date" ? 32 : 200}
              onChange={(e) => setReport({ ...report, [key]: e.target.value })}
            />
          </label>
        ))}
        {isGate && (
          <label className="text-sm">
            {t("lab.mode")}
            <select className={field} value={mode} onChange={(e) => setMode(e.target.value as typeof mode)}>
              <option value="hplc">{t("lab.hplc")}</option>
              <option value="negative">{`${t("lab.elisa")}: ${t("lab.negative")}`}</option>
              <option value="positive">{`${t("lab.elisa")}: ${t("lab.positive")}`}</option>
            </select>
          </label>
        )}
        {needsValue && (
          <label className="text-sm">
            {t("lab.value")}
            <input
              className={field}
              inputMode="decimal"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              data-testid="lab-value"
            />
            {input.startsWith("t.") && (
              <span className="text-xs text-muted-foreground">{t("lab.fractionHint")}</span>
            )}
          </label>
        )}
        <label className="text-sm">
          {t("lab.cv")}
          <input className={field} inputMode="decimal" value={cv} onChange={(e) => setCv(e.target.value)} />
        </label>
        <label className="text-sm sm:col-span-2">
          {t("lab.method")}
          <input
            className={field}
            value={method}
            maxLength={200}
            onChange={(e) => setMethod(e.target.value)}
          />
        </label>
        <div className="sm:col-span-2">
          <Button type="submit" disabled={!valid || m.isPending} data-testid="lab-submit">
            {m.isPending ? t("lab.updating") : t("lab.submit")}
          </Button>
        </div>
      </form>
      <div aria-live="polite">
        {m.isError && <p className="mt-3 text-sm text-bad">{(m.error as Error).message}</p>}
        {m.data && (
          <div className="mt-4 space-y-3">
            <p className="text-sm">
              <strong>{m.data.label}</strong>: {t("lab.prior")}{" "}
              {m.data.prior ? <Num v={m.data.prior} /> : "—"} → {t("lab.posterior")}{" "}
              {m.data.posterior ? <Num v={m.data.posterior} /> : "—"}
            </p>
            <p className="text-xs text-muted-foreground">{m.data.note}</p>
            <Compare before={m.data.before} after={m.data.after} />
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => runRequest(m.data!.after_request, null, "next")} data-testid="lab-keep">
                {t("lab.keep")}
              </Button>
              <Button variant="outline" onClick={() => m.reset()}>
                {t("lab.discard")}
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

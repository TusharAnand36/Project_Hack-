import { useTranslation } from "react-i18next";

import type { Gate } from "@/api/client";
import { gloss } from "@/lib/glossary";
import { cn } from "@/lib/utils";

import { Num } from "./Num";
import { Card } from "./ui/card";

const VERDICT_STYLE: Record<string, { icon: string; cls: string }> = {
  GO: { icon: "✓", cls: "border-ok text-ok" },
  "NO-GO": { icon: "✕", cls: "border-bad text-bad" },
  "TEST-FIRST": { icon: "⚑", cls: "border-warn text-warn" },
};

const GATE_STYLE: Record<string, { icon: string; cls: string }> = {
  PASS: { icon: "✓", cls: "border-ok text-ok" },
  FAIL: { icon: "✕", cls: "border-bad text-bad" },
  "TEST-FIRST": { icon: "⚑", cls: "border-warn text-warn" },
  FLAG: { icon: "ℹ", cls: "border-border text-muted-foreground" },
};

export function VerdictLabel({ label, large = false }: { label: string; large?: boolean }) {
  const { t } = useTranslation();
  const s = VERDICT_STYLE[label] ?? VERDICT_STYLE["TEST-FIRST"];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-md border-2 px-3 font-bold",
        s.cls,
        large ? "py-2 text-2xl" : "py-0.5",
      )}
      data-testid="verdict-label"
    >
      <span aria-hidden="true">{s.icon}</span>
      {t(`verdict.${label}`)}
    </span>
  );
}

export function GateCard({ gate }: { gate: Gate }) {
  const { t, i18n } = useTranslation();
  const s = GATE_STYLE[gate.state];
  return (
    <Card className={cn("border-s-4", s.cls.split(" ")[0])} data-testid={`gate-${gate.id}`}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h4 className="font-medium text-foreground">
          {gate.id} · {gloss(gate.name, i18n.language)}
        </h4>
        <span
          className={cn("inline-flex items-center gap-1 rounded border px-2 text-sm font-semibold", s.cls)}
        >
          <span aria-hidden="true">{s.icon}</span>
          {t(`verdict.gateState.${gate.state}`)}
        </span>
      </div>
      <dl className="mt-2 grid gap-1 text-sm">
        {gate.prior_p_fail && (
          <div className="flex flex-wrap gap-2">
            <dt className="text-muted-foreground">{t("verdict.prior")}</dt>
            <dd>
              <Num v={gate.prior_p_fail} label={t("verdict.prior")} />
            </dd>
          </div>
        )}
        {gate.measured && (
          <div className="flex flex-wrap gap-2">
            <dt className="text-muted-foreground">{t("verdict.measured")}</dt>
            <dd>
              <Num v={gate.measured} label={t("verdict.measured")} />
            </dd>
          </div>
        )}
        {gate.limit && (
          <div className="flex flex-wrap gap-2">
            <dt className="text-muted-foreground">{t("verdict.limit")}</dt>
            <dd>
              <Num v={gate.limit} label={t("verdict.limit")} />
            </dd>
          </div>
        )}
        {gate.required_test && (
          <div className="flex flex-wrap gap-2">
            <dt className="text-muted-foreground">{t("verdict.requiredTest")}</dt>
            <dd>{gate.required_test.replace(/_/g, " ")}</dd>
          </div>
        )}
        {gate.flip_condition && (
          <div className="flex flex-wrap gap-2">
            <dt className="text-muted-foreground">{t("verdict.flips")}</dt>
            <dd>{gate.flip_condition}</dd>
          </div>
        )}
      </dl>
      {[...gate.reasons, ...gate.flags].length > 0 && (
        <ul className="mt-2 list-disc ps-5 text-sm">
          {[...gate.reasons, ...gate.flags].map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
      )}
    </Card>
  );
}

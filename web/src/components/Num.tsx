import * as Popover from "@radix-ui/react-popover";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { Range, Value } from "@/api/client";
import { useSources } from "@/api/hooks";
import { formatValue, kindForUnit, type NumKind } from "@/lib/format";
import { cn } from "@/lib/utils";
import { useStore } from "@/store";

import { TagChip } from "./TagChip";

type Leaf = Value | Range;

function isRange(v: Leaf): v is Range {
  return (v as Range).p50 !== undefined;
}

interface NumProps {
  /** Any numeric leaf from the engine: a Value or a P10/P50/P90 Range. */
  v: Leaf | null | undefined;
  kind?: NumKind;
  /** Show the P10–P90 range inline (default true for ranges). */
  showRange?: boolean;
  className?: string;
  label?: string;
}

/** The only way numbers are shown: formatted value, tag chip, and a details popover (hover, focus, tap). */
export function Num({ v, kind, showRange = true, className, label }: NumProps) {
  const { t } = useTranslation();
  const showSources = useStore((s) => s.showSources);
  const sources = useSources();
  // hover/focus shows a transient preview; click, tap or Enter pins it open and moves focus inside
  const [peek, setPeek] = useState(false);
  const [pinned, setPinned] = useState(false);
  const open = peek || pinned;
  const close = () => {
    setPeek(false);
    setPinned(false);
  };
  if (!v) return <span className="text-muted-foreground">{t("workflow.notEstimated")}</span>;
  const k = kind ?? kindForUnit(v.unit);
  const main = isRange(v) ? v.p50 : v.value;
  const text = formatValue(main, k);
  const range =
    isRange(v) && showRange && v.p10 !== v.p90 ? `${formatValue(v.p10, k)}–${formatValue(v.p90, k)}` : null;
  const transferred = v.alpha != null && v.alpha < 0.7;
  const ids = v.source_ids ?? [];

  return (
    <Popover.Root open={open} onOpenChange={(next) => !next && close()}>
      <span className={cn("inline-flex flex-wrap items-baseline gap-1", className)}>
        <Popover.Trigger
          className="inline-flex items-baseline gap-1 rounded underline decoration-dotted underline-offset-4"
          aria-label={`${label ? label + ": " : ""}${text}${range ? ` (${t("num.range")} ${range})` : ""}, ${t(`tag.${v.tag}`)}. ${t("num.details")}`}
          onPointerEnter={(e) => e.pointerType === "mouse" && setPeek(true)}
          onPointerLeave={(e) => e.pointerType === "mouse" && setPeek(false)}
          onFocus={(e) => e.currentTarget.matches(":focus-visible") && setPeek(true)}
          onBlur={() => setPeek(false)}
          onClick={(e) => {
            e.preventDefault(); // we manage open state; Radix would otherwise toggle a hover-opened popover shut
            if (pinned) close();
            else setPinned(true);
          }}
          data-testid="num"
        >
          <span className="font-semibold tabular-nums">{text}</span>
          {range && <span className="text-xs text-muted-foreground tabular-nums">{range}</span>}
        </Popover.Trigger>
        <TagChip tag={v.tag} />
        {transferred && (
          <span className="rounded bg-muted px-1 text-[0.7rem] text-warn">{t("num.transferred")}</span>
        )}
        {showSources && ids.length > 0 && (
          <span className="text-[0.7rem] text-muted-foreground">[{ids.join(", ")}]</span>
        )}
      </span>
      <Popover.Portal>
        <Popover.Content
          sideOffset={6}
          onOpenAutoFocus={(e) => !pinned && e.preventDefault()}
          collisionPadding={16}
          className={cn(
            "z-50 w-[min(22rem,calc(100vw-2rem))] rounded-lg border border-border bg-background p-3 text-sm shadow-lg",
            !pinned && "pointer-events-none", // a hover preview never blocks clicks underneath
          )}
        >
          <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
            <dt className="text-muted-foreground">{label ?? t("num.details")}</dt>
            <dd className="font-semibold tabular-nums">
              {text} {v.unit && <span className="font-normal text-muted-foreground">{v.unit}</span>}
            </dd>
            {isRange(v) && (
              <>
                <dt className="text-muted-foreground">{t("num.range")}</dt>
                <dd className="tabular-nums">
                  {formatValue(v.p10, k)} – {formatValue(v.p90, k)}
                </dd>
              </>
            )}
            <dt className="text-muted-foreground">{t("num.tag")}</dt>
            <dd className="flex items-center gap-1">
              <TagChip tag={v.tag} /> {t(`tag.${v.tag}`)}
            </dd>
            {v.grade && (
              <>
                <dt className="text-muted-foreground">{t("num.grade")}</dt>
                <dd>{v.grade}</dd>
              </>
            )}
            {v.alpha != null && (
              <>
                <dt className="text-muted-foreground">{t("num.alpha")}</dt>
                <dd>{v.alpha}</dd>
              </>
            )}
          </dl>
          {transferred && <p className="mt-2 text-warn">{t("num.transferredLong", { alpha: v.alpha })}</p>}
          <p className="mt-2 font-medium">{t("num.sources")}</p>
          {ids.length === 0 ? (
            <p className="text-muted-foreground">{t("num.noSources")}</p>
          ) : (
            <ul className="list-disc ps-5">
              {ids.map((id) => {
                const s = sources.get(id);
                return (
                  <li key={id}>
                    {s?.url ? (
                      <a className="underline" href={s.url} target="_blank" rel="noreferrer">
                        {s.citation}
                      </a>
                    ) : (
                      (s?.citation ?? id)
                    )}
                  </li>
                );
              })}
            </ul>
          )}
          <Popover.Close className="mt-3 min-h-9 rounded border border-border px-3 text-xs">
            {t("num.close")}
          </Popover.Close>
          <Popover.Arrow className="fill-border" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}

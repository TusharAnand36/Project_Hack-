import { useTranslation } from "react-i18next";

import type { Diagnosis } from "@/api/client";
import { formatNumber } from "@/lib/format";

/** Horizontal bars of level / tolerance with P10-P90 whiskers and the tolerance line at 1. */
export function ExceedanceBars({ rows }: { rows: Diagnosis[] }) {
  const { t } = useTranslation();
  const data = rows
    .filter((d) => d.ratio)
    .map((d) => ({
      name: d.name,
      limiting: d.limiting,
      p10: d.ratio!.p10,
      p50: d.ratio!.p50,
      p90: d.ratio!.p90,
    }));
  if (data.length === 0)
    return <p className="my-4 text-sm text-muted-foreground">{t("workflow.ratioMissing")}</p>;
  const max = Math.max(2, ...data.map((d) => d.p90)) * 1.05;
  const W = 640;
  const label = 170;
  const rowH = 36;
  const H = data.length * rowH + 30;
  const x = (v: number) => label + (Math.min(v, max) / max) * (W - label - 16);
  return (
    <figure>
      <figcaption className="mb-2 text-sm font-medium">{t("diagnosis.chartTitle")}</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={t("diagnosis.chartTitle")}>
        {data.map((d, i) => {
          const y = i * rowH + 8;
          return (
            <g key={d.name}>
              <text x={0} y={y + 16} className="fill-foreground text-[13px]">
                {d.name}
                {d.limiting ? " *" : ""}
              </text>
              <rect
                x={label}
                y={y + 4}
                width={x(d.p50) - label}
                height={16}
                rx={3}
                className={d.p50 > 1 ? "fill-bad/70" : "fill-ok/70"}
              />
              <line
                x1={x(d.p10)}
                x2={x(d.p90)}
                y1={y + 12}
                y2={y + 12}
                className="stroke-foreground"
                strokeWidth={2}
              />
              <line
                x1={x(d.p10)}
                x2={x(d.p10)}
                y1={y + 6}
                y2={y + 18}
                className="stroke-foreground"
                strokeWidth={2}
              />
              <line
                x1={x(d.p90)}
                x2={x(d.p90)}
                y1={y + 6}
                y2={y + 18}
                className="stroke-foreground"
                strokeWidth={2}
              />
              <text
                x={Math.min(x(d.p90) + 6, W - 40)}
                y={y + 16}
                className="fill-muted-foreground text-[12px]"
              >
                ×{formatNumber(d.p50, 1)}
              </text>
            </g>
          );
        })}
        <line
          x1={x(1)}
          x2={x(1)}
          y1={0}
          y2={H - 22}
          className="stroke-warn"
          strokeWidth={2}
          strokeDasharray="5 4"
        />
        <text x={x(1) + 4} y={H - 8} className="fill-warn text-[12px]">
          1.0× = {t("diagnosis.tolerance")}
        </text>
      </svg>
    </figure>
  );
}

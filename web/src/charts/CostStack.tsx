import { useTranslation } from "react-i18next";

import { formatValue } from "@/lib/format";

export interface Part {
  key: string;
  value: number;
}

const COLOURS = [
  "#243f32",
  "#78905e",
  "#e17b54",
  "#a78b5a",
  "#587e78",
  "#7b697a",
  "#a5b47b",
  "#b88c7b",
  "#686c53",
];

/** Two horizontal stacked bars (ours vs pea) on one ₹/kg-protein axis, with a legend. */
export function CostStack({
  ours,
  pea,
  oursLabel,
  peaLabel,
}: {
  ours: Part[];
  pea: Part[];
  oursLabel: string;
  peaLabel: string;
}) {
  const { t } = useTranslation();
  const total = (p: Part[]) => p.reduce((s, x) => s + x.value, 0);
  const max = Math.max(total(ours), total(pea), 1) * 1.05;
  const W = 640;
  const label = 150;
  const x = (v: number) => (v / max) * (W - label - 70);
  const keys = Array.from(new Set([...ours, ...pea].map((p) => p.key)));
  const colour = (k: string) => COLOURS[keys.indexOf(k) % COLOURS.length];
  const bar = (parts: Part[], y: number, name: string) => {
    let acc = 0;
    return (
      <g>
        <text x={0} y={y + 18} className="fill-foreground text-[13px]">
          {name}
        </text>
        {parts.map((p) => {
          const r = (
            <rect
              key={p.key}
              x={label + x(acc)}
              y={y}
              width={Math.max(x(p.value), 0)}
              height={26}
              fill={colour(p.key)}
            />
          );
          acc += p.value;
          return r;
        })}
        <text x={label + x(acc) + 6} y={y + 18} className="fill-foreground text-[12px]">
          {formatValue(acc, "inr")}
        </text>
      </g>
    );
  };
  return (
    <figure>
      <svg viewBox={`0 0 ${W} 90`} className="w-full" role="img" aria-label={t("cost.title")}>
        {bar(ours, 6, oursLabel)}
        {bar(pea, 50, peaLabel)}
      </svg>
      <figcaption>
        <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs">
          {keys.map((k) => (
            <li key={k} className="flex items-center gap-1">
              <span
                aria-hidden="true"
                className="inline-block h-3 w-3 rounded-sm"
                style={{ background: colour(k) }}
              />
              {t(`cost.parts.${k}`)}
            </li>
          ))}
        </ul>
      </figcaption>
    </figure>
  );
}

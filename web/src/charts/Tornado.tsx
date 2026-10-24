import { formatValue } from "@/lib/format";

export interface Bar {
  label: string;
  value: number;
}

/** Sorted horizontal bars (EVPPI tornado, top 8). */
export function Tornado({ bars, title }: { bars: Bar[]; title: string }) {
  const max = Math.max(...bars.map((b) => b.value), 1);
  const W = 640;
  const label = 260;
  const rowH = 28;
  const H = bars.length * rowH + 8;
  return (
    <figure>
      <figcaption className="mb-2 text-sm font-medium">{title}</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={title}>
        {bars.map((b, i) => {
          const y = i * rowH + 4;
          const w = (b.value / max) * (W - label - 90);
          return (
            <g key={b.label}>
              <text x={label - 8} y={y + 15} textAnchor="end" className="fill-foreground text-[12px]">
                {b.label.length > 40 ? `${b.label.slice(0, 38)}…` : b.label}
              </text>
              <rect
                x={label}
                y={y + 3}
                width={Math.max(w, 1)}
                height={16}
                rx={3}
                className="fill-primary/80"
              />
              <text x={label + w + 6} y={y + 15} className="fill-muted-foreground text-[12px]">
                {formatValue(b.value, "inr")}
              </text>
            </g>
          );
        })}
      </svg>
    </figure>
  );
}

import type { Chain } from "@/api/client";
import { formatValue } from "@/lib/format";

/** Cost (x) vs protein retained (y); dot size = P(spec); P10-P90 bars on both axes; Pareto front outlined. */
export function ParetoScatter({ chains, title }: { chains: Chain[]; title: string }) {
  const pts = chains.filter((c) => c.cost_inr_per_kg_protein && c.protein_retained && c.p_spec);
  const W = 640;
  const H = 320;
  const m = { l: 56, r: 48, t: 12, b: 40 };
  const xs = pts.flatMap((c) => [c.cost_inr_per_kg_protein!.p10, c.cost_inr_per_kg_protein!.p90]);
  const xMax = Math.max(...xs) * 1.05;
  const xMin = Math.min(0, ...xs);
  const x = (v: number) => m.l + ((v - xMin) / (xMax - xMin)) * (W - m.l - m.r);
  const y = (v: number) => H - m.b - v * (H - m.t - m.b);
  const ticks = [0, 0.25, 0.5, 0.75, 1];
  return (
    <figure>
      <figcaption className="mb-2 text-sm font-medium">{title}</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={title}>
        <line x1={m.l} x2={W - m.r} y1={H - m.b} y2={H - m.b} className="stroke-border" />
        <line x1={m.l} x2={m.l} y1={m.t} y2={H - m.b} className="stroke-border" />
        {ticks.map((tk) => (
          <text
            key={tk}
            x={m.l - 6}
            y={y(tk) + 4}
            textAnchor="end"
            className="fill-muted-foreground text-[11px]"
          >
            {formatValue(tk, "prob")}
          </text>
        ))}
        {[0, 0.5, 1].map((f) => {
          const v = xMin + f * (xMax - xMin);
          return (
            <text
              key={f}
              x={x(v)}
              y={H - m.b + 16}
              textAnchor="middle"
              className="fill-muted-foreground text-[11px]"
            >
              {formatValue(v, "inr")}
            </text>
          );
        })}
        <text x={(W + m.l) / 2} y={H - 4} textAnchor="middle" className="fill-foreground text-[12px]">
          ₹ / kg protein
        </text>
        {pts.map((c) => {
          const cx = x(c.cost_inr_per_kg_protein!.p50);
          const cy = y(c.protein_retained!.p50);
          const r = 4 + 10 * c.p_spec!.value;
          return (
            <g key={c.id}>
              <line
                x1={x(c.cost_inr_per_kg_protein!.p10)}
                x2={x(c.cost_inr_per_kg_protein!.p90)}
                y1={cy}
                y2={cy}
                className="stroke-muted-foreground"
                strokeWidth={1}
              />
              <line
                x1={cx}
                x2={cx}
                y1={y(c.protein_retained!.p10)}
                y2={y(c.protein_retained!.p90)}
                className="stroke-muted-foreground"
                strokeWidth={1}
              />
              <circle
                cx={cx}
                cy={cy}
                r={r}
                className={c.pareto ? "fill-primary/70 stroke-foreground" : "fill-muted-foreground/40"}
                strokeWidth={c.pareto ? 2 : 0}
              />
              <text x={cx + r + 3} y={cy - r} className="fill-foreground text-[11px]">
                #{c.rank}
              </text>
            </g>
          );
        })}
      </svg>
    </figure>
  );
}

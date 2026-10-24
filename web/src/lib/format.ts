/** Number formatting with Indian conventions (website plan §4, SR-10). Always en-IN digits. */

const inr0 = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
const usd2 = new Intl.NumberFormat("en-IN", { style: "currency", currency: "USD", maximumFractionDigits: 2 });

export type NumKind = "inr" | "usd" | "pct" | "prob" | "num" | "index";

/** Pick a display kind from an engine unit string. */
export function kindForUnit(unit?: string | null): NumKind {
  const u = (unit ?? "").toLowerCase();
  if (u.startsWith("inr")) return "inr";
  if (u.startsWith("usd")) return "usd";
  if (u === "probability" || u === "fraction") return "prob";
  if (u.startsWith("%") || u === "percentage points") return "pct";
  if (u.startsWith("index")) return "index";
  return "num";
}

function digits(x: number): number {
  const a = Math.abs(x);
  if (a >= 100) return 0;
  if (a >= 10) return 1;
  return 2;
}

export function formatNumber(x: number, maxFractionDigits = digits(x)): string {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: maxFractionDigits }).format(x);
}

/** Format one number for display. `prob` values are fractions shown as %. */
export function formatValue(x: number, kind: NumKind): string {
  switch (kind) {
    case "inr":
      return inr0.format(x);
    case "usd":
      return usd2.format(x);
    case "prob":
      return `${formatNumber(x * 100, x * 100 >= 10 ? 0 : 1)}%`;
    case "pct":
      return `${formatNumber(x, 1)}%`;
    case "index":
      return formatNumber(x, 1);
    default:
      return formatNumber(x);
  }
}

/** Lakh / crore for large rupee amounts (budgets); full figure goes in a tooltip. */
export function formatLakhCrore(x: number): string {
  if (Math.abs(x) >= 1e7) return `₹${formatNumber(x / 1e7, 2)} crore`;
  if (Math.abs(x) >= 1e5) return `₹${formatNumber(x / 1e5, 2)} lakh`;
  return inr0.format(x);
}

/** Price unit conversion: mandi prices are quoted per quintal (100 kg) or per tonne. */

export type PriceUnit = "per_kg" | "per_quintal" | "per_tonne";

const KG: Record<PriceUnit, number> = { per_kg: 1, per_quintal: 100, per_tonne: 1000 };

export function toInrPerKg(value: number, unit: PriceUnit): number {
  return value / KG[unit];
}

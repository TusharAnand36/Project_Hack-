import { z } from "zod";

import type { AnalyzeRequest } from "@/api/client";
import { toInrPerKg, type PriceUnit } from "@/lib/units";

/** Empty input -> undefined (use the dataset default); otherwise a number with bounds. Messages are i18n keys. */
function optNum(opts: { max?: number; min?: number; positive?: boolean } = {}) {
  return z
    .string()
    .trim()
    .transform((s, ctx) => {
      if (s === "") return undefined;
      const x = Number(s.replace(/,/g, ""));
      if (!Number.isFinite(x)) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: "input.errors.number" });
        return z.NEVER;
      }
      if (opts.positive && x <= 0)
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: "input.errors.positive" });
      if (!opts.positive && x < (opts.min ?? 0))
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: "input.errors.number" });
      if (opts.max === 100 && x > 100)
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: "input.errors.max100" });
      if (opts.max === 10 && x > 10)
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: "input.errors.max10" });
      return x;
    });
}

const tri = z.enum(["unknown", "yes", "no"]);
export type Tri = z.infer<typeof tri>;

export const formSchema = z
  .object({
    byproduct: z.string().min(1, "input.errors.required"),
    application: z.string().min(1, "input.errors.required"),
    minProtein: optNum({ max: 100 }),
    maxCost: optNum({ positive: true }),
    maxOfi: optNum({ max: 10 }),
    maxPhytate: optNum({ max: 100 }),
    market: z.enum(["domestic", "export_EU"]),
    scale: optNum({ positive: true }),
    price: optNum({ positive: true }),
    priceUnit: z.enum(["per_kg", "per_quintal", "per_tonne"]),
    noSolvents: z.boolean(),
    equipment: z.array(z.string()),
    exclude: z.array(z.string()),
    protein: optNum({ max: 100 }),
    nFactor: optNum({ positive: true }).refine(
      (x) => x === undefined || (x >= 4 && x <= 7),
      "input.errors.nFactor",
    ),
    moisture: optNum({ max: 100 }),
    ffa: optNum({ max: 100 }),
    afb1: optNum(),
    totalAflatoxins: optNum(),
    hexane: optNum(),
    lead: optNum(),
    cadmium: optNum(),
    arsenic: optNum(),
    mercury: optNum(),

    phytate: optNum({ max: 100 }),
    oilRoute: z.enum(["", "cold_pressed", "expeller", "solvent"]),
    hours: optNum(),
    stabilised: tri,
    foodGrade: tri,
    hygienic: tri,
    sorted: tri,
    hexaneCert: tri,
  })
  .superRefine((v, ctx) => {
    if (v.afb1 !== undefined && v.totalAflatoxins !== undefined && v.totalAflatoxins < v.afb1) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["totalAflatoxins"],
        message: "input.errors.aflatoxinTotal",
      });
    }

    if (v.protein !== undefined && v.moisture !== undefined && v.protein + v.moisture > 100) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["protein"], message: "input.errors.proximate" });
    }
  });

export type FormInput = z.input<typeof formSchema>;
export type FormOutput = z.output<typeof formSchema>;

export const EMPTY_FORM: FormInput = {
  byproduct: "",
  application: "",
  minProtein: "",
  maxCost: "",
  maxOfi: "",
  maxPhytate: "",
  market: "domestic",
  scale: "",
  price: "",
  priceUnit: "per_kg",
  noSolvents: false,
  equipment: [],
  exclude: [],
  protein: "",
  nFactor: "",
  moisture: "",
  ffa: "",
  afb1: "",
  totalAflatoxins: "",
  hexane: "",
  lead: "",
  cadmium: "",
  arsenic: "",
  mercury: "",

  phytate: "",
  oilRoute: "",
  hours: "",
  stabilised: "unknown",
  foodGrade: "unknown",
  hygienic: "unknown",
  sorted: "unknown",
  hexaneCert: "unknown",
};

const triToBool = (x: Tri) => (x === "unknown" ? null : x === "yes");
const boolToTri = (x?: boolean | null): Tri => (x == null ? "unknown" : x ? "yes" : "no");
const str = (x?: number | null) => (x == null ? "" : String(x));

/** Form values -> /analyze request. Batch values are tagged measured. */
export function toRequest(v: FormOutput): AnalyzeRequest {
  const m = (x: number | undefined) => (x === undefined ? null : { value: x, tag: "measured" as const });
  return {
    byproduct: v.byproduct,
    application: v.application,
    market: v.market,
    scale_kg_day: v.scale ?? null,
    raw_price_inr_per_kg: v.price === undefined ? null : toInrPerKg(v.price, v.priceUnit as PriceUnit),
    targets: {
      min_protein_pct: v.minProtein ?? null,
      max_cost_inr_per_kg_protein: v.maxCost ?? null,
      max_offflavour_index: v.maxOfi ?? null,
      max_phytate_pct: v.maxPhytate ?? null,
    },
    constraints: { exclude_treatments: v.exclude, no_solvents: v.noSolvents, equipment: v.equipment },
    batch: {
      protein_pct:
        v.protein === undefined ? null : { value: v.protein, tag: "measured", n_factor: v.nFactor ?? null },
      moisture_pct: m(v.moisture),
      ffa_pct: m(v.ffa),
      afb1_ppb: m(v.afb1),
      total_aflatoxins_ppb: m(v.totalAflatoxins),
      hexane_ppm: m(v.hexane),
      pb_ppm: m(v.lead),
      cd_ppm: m(v.cadmium),
      arsenic_ppm: m(v.arsenic),
      hg_ppm: m(v.mercury),

      phytate_pct: m(v.phytate),
    },
    process: {
      oil_route: v.oilRoute === "" ? null : v.oilRoute,
      hours_since_milling: v.hours ?? null,
      stabilised: triToBool(v.stabilised),
      food_grade_supply: triToBool(v.foodGrade),
      storage: v.hygienic === "unknown" ? null : v.hygienic === "yes" ? "hygienic" : "open",
      sorted_food_grade_supply: triToBool(v.sorted),
      hexane_cert: triToBool(v.hexaneCert),
    },
  };
}

/** A request (e.g. a preset payload) -> form values, so a preset can be edited. */
export function fromRequest(r: AnalyzeRequest): FormInput {
  const b = r.batch ?? {};
  const p = r.process ?? {};
  const t = r.targets ?? {};
  const c = r.constraints ?? {};
  return {
    ...EMPTY_FORM,
    byproduct: r.byproduct,
    application: r.application,
    market: r.market ?? "domestic",
    scale: str(r.scale_kg_day),
    price: str(r.raw_price_inr_per_kg),
    minProtein: str(t.min_protein_pct),
    maxCost: str(t.max_cost_inr_per_kg_protein),
    maxOfi: str(t.max_offflavour_index),
    maxPhytate: str(t.max_phytate_pct),
    noSolvents: c.no_solvents ?? false,
    equipment: c.equipment ?? [],
    exclude: c.exclude_treatments ?? [],
    protein: str(b.protein_pct?.value),
    nFactor: str(b.protein_pct?.n_factor),
    moisture: str(b.moisture_pct?.value),
    ffa: str(b.ffa_pct?.value),
    afb1: str(b.afb1_ppb?.value),
    totalAflatoxins: str(b.total_aflatoxins_ppb?.value),
    hexane: str(b.hexane_ppm?.value),
    lead: str(b.pb_ppm?.value),
    cadmium: str(b.cd_ppm?.value),
    arsenic: str(b.arsenic_ppm?.value),
    mercury: str(b.hg_ppm?.value),

    phytate: str(b.phytate_pct?.value),
    oilRoute: p.oil_route ?? "",
    hours: str(p.hours_since_milling),
    stabilised: boolToTri(p.stabilised),
    foodGrade: boolToTri(p.food_grade_supply),
    hygienic: p.storage == null ? "unknown" : p.storage === "hygienic" ? "yes" : "no",
    sorted: boolToTri(p.sorted_food_grade_supply),
    hexaneCert: boolToTri(p.hexane_cert),
  };
}

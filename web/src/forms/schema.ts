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
    lotId: z.string().trim().max(100),
    supplier: z.string().trim().max(200),
    origin: z.string().trim().max(200),
    sourceReference: z.string().trim().max(300),
    routeReference: z.string().trim().max(300),
    regulatoryReference: z.string().trim().max(300),
    functionalReference: z.string().trim().max(300),
    priceSource: z.string().trim().max(300),
    priceDate: z.string().trim().max(32),
    priceBoundary: z.string().trim().max(300),
    method: z.string().trim().max(200),
    laboratory: z.string().trim().max(200),
    reportReference: z.string().trim().max(200),
    reportDate: z.string().trim().max(32),
    sensoryRubric: z.string().trim().max(500),
    materialForm: z.enum(["unknown", "cake", "meal", "flour", "concentrate", "isolate"]),
    proteinBasis: z.enum(["unknown", "as_received", "dry_matter"]),
    targetProteinBasis: z.enum(["as_received", "dry_matter"]),
    costMethod: z.enum(["manual", "benchmark", "product_budget"]),
    discount: optNum({ max: 100 }),
    productBudget: optNum({ positive: true }),
    productProtein: optNum({ positive: true }),
    phytateType: z.enum(["not_established", "internal_target"]),
    crudeFibre: optNum({ max: 100 }),
    dietaryFibre: optNum({ max: 100 }),
    fat: optNum({ max: 100 }),
    ash: optNum({ max: 100 }),
    dehulled: tri,

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
    oilRoute: z.enum(["", "cold_pressed", "expeller", "solvent", "other"]),
    hours: optNum(),
    stabilised: tri,
    foodGrade: tri,
    hygienic: tri,
    sorted: tri,
    hexaneCert: tri,
  })
  .superRefine((v, ctx) => {
    if (v.discount !== undefined && v.discount >= 100)
      ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["discount"], message: "input.errors.max100" });
    if (v.productProtein !== undefined && v.productProtein > 1)
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["productProtein"],
        message: "input.errors.proteinKg",
      });

    if (v.afb1 !== undefined && v.totalAflatoxins !== undefined && v.totalAflatoxins < v.afb1) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["totalAflatoxins"],
        message: "input.errors.aflatoxinTotal",
      });
    }

    if (
      v.proteinBasis !== "dry_matter" &&
      v.protein !== undefined &&
      v.moisture !== undefined &&
      v.protein + v.moisture > 100
    ) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["protein"], message: "input.errors.proximate" });
    }
  });

export type FormInput = z.input<typeof formSchema>;
export type FormOutput = z.output<typeof formSchema>;

export const EMPTY_FORM: FormInput = {
  byproduct: "",
  lotId: "",
  supplier: "",
  origin: "",
  sourceReference: "",
  routeReference: "",
  regulatoryReference: "",
  functionalReference: "",
  priceSource: "",
  priceDate: "",
  priceBoundary: "",
  method: "",
  laboratory: "",
  reportReference: "",
  reportDate: "",
  sensoryRubric: "",
  materialForm: "unknown",
  proteinBasis: "unknown",
  targetProteinBasis: "as_received",
  costMethod: "manual",
  discount: "10",
  productBudget: "",
  productProtein: "",
  phytateType: "not_established",
  crudeFibre: "",
  dietaryFibre: "",
  fat: "",
  ash: "",
  dehulled: "unknown",

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
  const m = (x: number | undefined) =>
    x === undefined
      ? null
      : {
          value: x,
          tag: (v.method && v.reportReference ? "measured" : "assumed") as "measured" | "assumed",
          method: v.method || null,
          laboratory: v.laboratory || null,
          report_reference: v.reportReference || null,
          report_date: v.reportDate || null,
        };
  return {
    byproduct: v.byproduct,
    application: v.application,
    market: v.market,
    scale_kg_day: v.scale ?? null,
    price_source: v.priceSource || null,
    price_date: v.priceDate || null,
    price_boundary: v.priceBoundary || "Supplier price; logistics not supplied",
    original_price: v.price ?? null,
    original_price_unit: v.priceUnit,

    raw_price_inr_per_kg: v.price === undefined ? null : toInrPerKg(v.price, v.priceUnit as PriceUnit),
    targets: {
      min_protein_pct: v.minProtein ?? null,
      protein_basis: v.targetProteinBasis,
      cost_method: v.costMethod,
      required_discount_pct: v.discount ?? 10,
      product_budget_inr: v.productBudget ?? null,
      product_protein_kg: v.productProtein ?? null,
      phytate_target_type: v.phytateType,
      sensory_rubric: v.sensoryRubric || null,

      max_cost_inr_per_kg_protein: v.maxCost ?? null,
      max_offflavour_index: v.maxOfi ?? null,
      max_phytate_pct: v.maxPhytate ?? null,
    },
    constraints: { exclude_treatments: v.exclude, no_solvents: v.noSolvents, equipment: v.equipment },
    batch: {
      lot_id: v.lotId || null,
      supplier: v.supplier || null,
      origin: v.origin || null,
      source_reference: v.sourceReference || null,
      material_form: v.materialForm,
      dehulled: triToBool(v.dehulled),
      crude_fibre_pct: m(v.crudeFibre),
      dietary_fibre_pct: m(v.dietaryFibre),
      fat_pct: m(v.fat),
      ash_pct: m(v.ash),

      protein_pct:
        v.protein === undefined
          ? null
          : {
              ...m(v.protein)!,
              value: v.protein,
              tag: (v.method && v.reportReference ? "measured" : "assumed"),
              n_factor: v.nFactor ?? null,
              basis: v.proteinBasis,
            },
      moisture_pct: m(v.moisture),
      ffa_pct: m(v.ffa),
      afb1_ppb: m(v.afb1),
      total_aflatoxins_ppb: m(v.totalAflatoxins),
      hexane_ppm: m(v.hexane),
      pb_ppm: m(v.lead),
      cd_ppm: m(v.cadmium),
      arsenic_ppm: m(v.arsenic),
      hg_ppm: m(v.mercury),

      phytate_pct:
        v.phytate === undefined
          ? null
          : { ...m(v.phytate)!, value: v.phytate, tag: (v.method && v.reportReference ? "measured" : "assumed"), basis: "dry_matter" },
    },
    process: {
      route_reference: v.routeReference || null,
      regulatory_review_reference: v.regulatoryReference || null,
      functional_validation_reference: v.functionalReference || null,

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
    lotId: b.lot_id ?? "",
    supplier: b.supplier ?? "",
    origin: b.origin ?? "",
    sourceReference: b.source_reference ?? "",
    materialForm: b.material_form ?? "unknown",
    dehulled: boolToTri(b.dehulled),
    proteinBasis:
      b.protein_pct?.basis === "dry_matter"
        ? "dry_matter"
        : b.protein_pct?.basis === "as_received"
          ? "as_received"
          : "unknown",
    targetProteinBasis: t.protein_basis ?? "as_received",
    costMethod: t.cost_method ?? "manual",
    discount: str(t.required_discount_pct ?? 10),
    productBudget: str(t.product_budget_inr),
    productProtein: str(t.product_protein_kg),
    phytateType: t.phytate_target_type ?? "not_established",
    sensoryRubric: t.sensory_rubric ?? "",
    crudeFibre: str(b.crude_fibre_pct?.value),
    dietaryFibre: str(b.dietary_fibre_pct?.value),
    fat: str(b.fat_pct?.value),
    ash: str(b.ash_pct?.value),
    routeReference: p.route_reference ?? "",
    regulatoryReference: p.regulatory_review_reference ?? "",
    functionalReference: p.functional_validation_reference ?? "",
    priceSource: r.price_source ?? "",
    priceDate: r.price_date ?? "",
    priceBoundary: r.price_boundary ?? "",
    method: b.protein_pct?.method ?? "",
    laboratory: b.protein_pct?.laboratory ?? "",
    reportReference: b.protein_pct?.report_reference ?? "",
    reportDate: b.protein_pct?.report_date ?? "",

    application: r.application,
    market: r.market ?? "domestic",
    scale: str(r.scale_kg_day),
    price: str(r.original_price ?? r.raw_price_inr_per_kg),
    priceUnit: r.original_price_unit ?? "per_kg",
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

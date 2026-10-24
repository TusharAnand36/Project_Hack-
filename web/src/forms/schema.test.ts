import { describe, expect, it } from "vitest";

import { EMPTY_FORM, formSchema, fromRequest, toRequest } from "./schema";

const base = { ...EMPTY_FORM, byproduct: "groundnut_cake", application: "beverage" };

describe("form schema", () => {
  it("rejects protein over 100%", () => {
    const r = formSchema.safeParse({ ...base, protein: "120" });
    expect(r.success).toBe(false);
    expect(r.error?.issues.some((i) => i.message === "input.errors.max100")).toBe(true);
  });

  it("requires a by-product and use", () => {
    const r = formSchema.safeParse(EMPTY_FORM);
    expect(r.success).toBe(false);
  });

  it("treats empty fields as dataset defaults and converts ₹/quintal to ₹/kg", () => {
    const r = formSchema.parse({ ...base, price: "2,800", priceUnit: "per_quintal", afb1: "12" });
    const req = toRequest(r);
    expect(req.raw_price_inr_per_kg).toBe(28);
    expect(req.targets?.min_protein_pct).toBeNull();
    expect(req.batch?.afb1_ppb).toEqual({ value: 12, tag: "measured" });
    expect(req.process?.stabilised).toBeNull();
  });

  it("flags protein + moisture over 100%", () => {
    const r = formSchema.safeParse({ ...base, protein: "70", moisture: "40" });
    expect(r.success).toBe(false);
  });

  it("round-trips a preset payload", () => {
    const req = toRequest(formSchema.parse({ ...base, minProtein: "60", maxCost: "300", stabilised: "yes" }));
    const again = toRequest(formSchema.parse(fromRequest(req)));
    expect(again).toEqual(req);
  });
});

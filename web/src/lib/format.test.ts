import { describe, expect, it } from "vitest";

import { formatLakhCrore, formatValue, kindForUnit } from "./format";

describe("format", () => {
  it("uses Indian grouping and units", () => {
    expect(formatValue(1234567, "inr")).toBe("₹12,34,567");
    expect(formatValue(0.531, "prob")).toBe("53%");
    expect(formatValue(48.24, "pct")).toBe("48.2%");
    expect(kindForUnit("INR/kg protein")).toBe("inr");
    expect(kindForUnit("% dry basis")).toBe("pct");
    expect(formatLakhCrore(2500000)).toBe("₹25 lakh");
    expect(formatLakhCrore(35000000)).toBe("₹3.5 crore");
  });
});

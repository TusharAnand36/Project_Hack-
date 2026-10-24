"""Cost and resource model, everything per kg of protein (source plan §12.7).

per step i, per kg of its input mass:
    energy = kWh * tariff, water = L/1000 * water price, chem = INR/kg,
    labour = h_per_t / 1000 * wage,
    capital = capex(S) * CRF / annual throughput,  capex(S) = capex_ref * (S / S_ref) ** 0.6
step cost per kg raw = (sum of the above) * (kg input to the step per kg raw cake)
total per kg raw = raw price + sum(step costs) + QA + overhead share of processing
cost per kg protein = total per kg raw / protein out per kg raw - co-product credit

A component whose inputs are missing is left out and named in `missing`; the total is then
a lower bound, and the API must say so. Nothing here invents a number.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

Arr = np.ndarray
COMPONENTS = ("energy", "water", "chemicals", "labour", "capital")


def crf(rate: Arr | float, years: Arr | float) -> Arr | float:
    """Capital recovery factor r(1+r)^n / ((1+r)^n - 1)."""
    g = (1.0 + rate) ** years
    return rate * g / (g - 1.0)


def scaled_capex(capex_ref: Arr, scale: Arr, scale_ref: Arr, exponent: Arr | float = 0.6) -> Arr:
    """Six-tenths rule."""
    return capex_ref * (scale / scale_ref) ** exponent


@dataclass
class StepResources:
    """Per kg of input to the step. Any field may be None (missing data)."""

    name: str
    input_per_kg_raw: Arr
    kwh_per_kg: Arr | None = None
    water_l_per_kg: Arr | None = None
    chem_inr_per_kg: Arr | None = None
    labour_h_per_t: Arr | None = None
    capex_ref_inr: Arr | None = None
    capex_ref_scale_kg_day: Arr | None = None


@dataclass
class Economics:
    """Plant-level inputs. Any field may be None (missing data)."""

    scale_kg_day: Arr | float
    discount_rate: Arr | float
    life_years: Arr | float
    operating_days: Arr | float
    utilisation: Arr | float
    scale_exponent: Arr | float = 0.6
    tariff_inr_per_kwh: Arr | None = None
    water_inr_per_m3: Arr | None = None
    wage_inr_per_h: Arr | None = None
    qa_inr_per_kg_raw: Arr | None = None
    overhead_frac: Arr | None = None


@dataclass
class CostResult:
    per_kg_raw: Arr
    per_kg_product: Arr
    per_kg_protein: Arr
    kwh_per_kg_protein: Arr | None
    l_water_per_kg_protein: Arr | None
    breakdown_per_kg_protein: dict[str, Arr]
    missing: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return not self.missing


def _need(missing: list[str], label: str, *xs: Arr | None) -> bool:
    if any(x is None for x in xs):
        missing.append(label)
        return False
    return True


def chain_cost(
    raw_price_inr_per_kg: Arr | None,
    steps: list[StepResources],
    mass_final_per_kg_raw: Arr,
    protein_final_per_kg_raw: Arr,
    econ: Economics,
    co_product_credit_inr_per_kg_protein: Arr | float = 0.0,
) -> CostResult:
    n = np.shape(protein_final_per_kg_raw)[0]
    zero = np.zeros(n)
    missing: list[str] = []
    parts: dict[str, Arr] = {"raw": zero.copy()}
    for c in COMPONENTS:
        parts[c] = zero.copy()
    kwh = zero.copy()
    litres = zero.copy()
    kwh_known = litres_known = True

    if _need(missing, "raw material price", raw_price_inr_per_kg):
        parts["raw"] = np.broadcast_to(raw_price_inr_per_kg, (n,)).astype(float)

    annual_raw = econ.scale_kg_day * econ.operating_days * econ.utilisation
    recovery = crf(econ.discount_rate, econ.life_years)
    for s in steps:
        x = s.input_per_kg_raw
        if s.kwh_per_kg is None:
            kwh_known = False
        else:
            kwh = kwh + s.kwh_per_kg * x
        if s.water_l_per_kg is None:
            litres_known = False
        else:
            litres = litres + s.water_l_per_kg * x
        if _need(missing, f"{s.name}: energy", s.kwh_per_kg, econ.tariff_inr_per_kwh):
            parts["energy"] += s.kwh_per_kg * econ.tariff_inr_per_kwh * x
        if _need(missing, f"{s.name}: water", s.water_l_per_kg, econ.water_inr_per_m3):
            parts["water"] += s.water_l_per_kg / 1000.0 * econ.water_inr_per_m3 * x
        if _need(missing, f"{s.name}: chemicals", s.chem_inr_per_kg):
            parts["chemicals"] += s.chem_inr_per_kg * x
        if _need(missing, f"{s.name}: labour", s.labour_h_per_t, econ.wage_inr_per_h):
            parts["labour"] += s.labour_h_per_t / 1000.0 * econ.wage_inr_per_h * x
        if _need(missing, f"{s.name}: capital", s.capex_ref_inr, s.capex_ref_scale_kg_day):
            step_scale = econ.scale_kg_day * x  # kg/day entering this step
            capex = scaled_capex(s.capex_ref_inr, step_scale, s.capex_ref_scale_kg_day, econ.scale_exponent)
            parts["capital"] += capex * recovery / annual_raw  # per kg raw cake

    processing = sum(parts[c] for c in COMPONENTS)
    if steps or econ.qa_inr_per_kg_raw is not None:
        if _need(missing, "QA cost", econ.qa_inr_per_kg_raw):
            parts["qa"] = np.broadcast_to(econ.qa_inr_per_kg_raw, (n,)).astype(float)
            processing = processing + parts["qa"]
    if steps:
        # overhead is read as a share of processing cost (raw material excluded): stated assumption
        if _need(missing, "overhead", econ.overhead_frac):
            parts["overhead"] = processing * econ.overhead_frac

    per_kg_raw = sum(parts.values())
    per_kg_protein = per_kg_raw / protein_final_per_kg_raw - co_product_credit_inr_per_kg_protein
    return CostResult(
        per_kg_raw=per_kg_raw,
        per_kg_product=per_kg_raw / mass_final_per_kg_raw,
        per_kg_protein=per_kg_protein,
        kwh_per_kg_protein=kwh / protein_final_per_kg_raw if kwh_known else None,
        l_water_per_kg_protein=litres / protein_final_per_kg_raw if litres_known else None,
        breakdown_per_kg_protein={k: v / protein_final_per_kg_raw for k, v in parts.items()},
        missing=missing,
    )

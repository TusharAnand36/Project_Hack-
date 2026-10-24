"""Imported pea isolate: landed cost, parity, margin, break-even and shocks (source plan §12.8).

landed per kg product = base USD * USD/INR * (1 + freight) * (1 + duty) * (1 + clearing)
landed per kg protein = landed per kg product / pea protein fraction
price we can charge   = landed per kg protein * (1 - buyer discount)
margin vs pea         = price we can charge - our cost per kg protein
break-even base USD   = base at which landed per kg protein equals our cost (closed form)

All comparisons are per kg protein, never per kg product.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

Arr = np.ndarray


@dataclass(frozen=True)
class PeaInputs:
    base_usd_per_kg: Arr | float
    usd_inr: Arr | float
    freight_frac: Arr | float
    duty_frac: Arr | float
    protein_frac: Arr | float
    clearing_frac: Arr | float = 0.0
    buyer_discount: Arr | float = 0.0


def _multiplier(p: PeaInputs) -> Arr | float:
    """INR per kg product for each USD of base price."""
    return p.usd_inr * (1 + p.freight_frac) * (1 + p.duty_frac) * (1 + p.clearing_frac)


def landed_per_kg_product(p: PeaInputs) -> Arr | float:
    return p.base_usd_per_kg * _multiplier(p)


def landed_per_kg_protein(p: PeaInputs) -> Arr | float:
    return landed_per_kg_product(p) / p.protein_frac


def price_we_can_charge(p: PeaInputs) -> Arr | float:
    return landed_per_kg_protein(p) * (1 - p.buyer_discount)


def margin_vs_pea(p: PeaInputs, our_cost_per_kg_protein: Arr | float) -> Arr | float:
    return price_we_can_charge(p) - our_cost_per_kg_protein


def break_even_base_usd(p: PeaInputs, our_cost_per_kg_protein: Arr | float) -> Arr | float:
    """Pea base price (USD/kg product) at which landed cost per kg protein equals ours."""
    return our_cost_per_kg_protein * p.protein_frac / _multiplier(p)


def apply_scenario(p: PeaInputs, set_values: dict[str, float], scale: dict[str, float]) -> PeaInputs:
    """Shock scenario: `set` replaces a field, `scale` multiplies it (costs.json scenarios)."""
    changes: dict[str, Arr | float] = {k: v for k, v in set_values.items()}
    for k, f in scale.items():
        changes[k] = np.asarray(getattr(p, k)) * f
    return replace(p, **changes)

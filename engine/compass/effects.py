"""Effect model: normalisation, compound reduction, mass/protein balance and tiers.

Source plan §12.2 (normalisation), §12.4 (first-order effect with a floor) and §12.5
(mass and protein balance). Everything is vectorised over Monte Carlo draws and works on
fractions internally (0.48, not 48 %); conversion to % happens only at the API edge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

CRUDE_N_FACTOR = 6.25  # convention for "crude protein" (N x 6.25)
MAX_PROTEIN_FRAC = 0.95

# ---------------------------------------------------------------- normalisation (§12.2)


def to_dry_basis(x_wet: np.ndarray, moisture_frac: np.ndarray) -> np.ndarray:
    """x_db = x_wb / (1 - moisture)."""
    return x_wet / (1.0 - moisture_frac)


def true_protein(
    crude_frac: np.ndarray, n_factor: np.ndarray, n_factor_used: float = CRUDE_N_FACTOR
) -> np.ndarray:
    """True protein = N x f, where N = reported protein / the factor used to report it."""
    return crude_frac / n_factor_used * n_factor


def proximate_sum_warning(parts_pct: dict[str, float | None], tolerance: float = 5.0) -> str | None:
    """Warn when protein + fat + fibre + ash + carbohydrate is not ~100 % (all parts known)."""
    if any(v is None for v in parts_pct.values()):
        return None
    total = sum(v for v in parts_pct.values() if v is not None)
    if abs(total - 100.0) > tolerance:
        return f"proximate parts sum to {total:.1f}% (expected 100 ± {tolerance:.0f}%)"
    return None


# ---------------------------------------------------------------- compounds (§12.4)


def reduce_compound(level: np.ndarray, reduction: np.ndarray, floor: np.ndarray | float = 0.0) -> np.ndarray:
    """L_after = floor + (L_before - floor) * (1 - r). Never below the floor, never above L_before.

    No synergy terms: consecutive steps simply compose (source plan §12.4).
    """
    r = np.clip(reduction, 0.0, 1.0)
    floor = np.minimum(floor, level)
    return floor + (level - floor) * (1.0 - r)


# ---------------------------------------------------------------- mass and protein balance (§12.5)


@dataclass
class Balance:
    """State after a step, per kg of raw cake: mass M (kg) and protein (kg)."""

    mass: np.ndarray
    protein: np.ndarray

    @property
    def protein_frac(self) -> np.ndarray:
        return self.protein / self.mass


def start(n: int, protein_frac: np.ndarray) -> Balance:
    return Balance(np.ones(n), np.broadcast_to(protein_frac, (n,)).astype(float))


def step(
    b: Balance,
    kind: Literal["process", "fractionation"],
    *,
    mass_yield: np.ndarray | None = None,
    protein_retention: np.ndarray | None = None,
    purity: np.ndarray | None = None,
    recovery: np.ndarray | None = None,
    cap: float = MAX_PROTEIN_FRAC,
) -> Balance:
    """Apply one step. Process: M' = M·m, P' = P·rho. Fractionation: P' = P·rho, M' = P'/pi.

    The protein fraction is capped at `cap` by holding mass at P'/cap, and protein can
    never exceed the mass that carries it.
    """
    if kind == "process":
        m = np.clip(mass_yield, 0.0, 1.0)
        rho = np.clip(protein_retention, 0.0, 1.0)
        protein = b.protein * rho
        mass = b.mass * m
    else:
        rho = np.clip(recovery, 0.0, 1.0)
        pi = np.clip(purity, 1e-6, 1.0)
        protein = b.protein * rho
        mass = protein / pi
    mass = np.maximum(mass, protein / cap)
    mass = np.maximum(mass, 1e-12)
    return Balance(mass, protein)


def retained(final: Balance, initial: Balance) -> np.ndarray:
    """Share of the raw cake's protein that ends up in the product."""
    return final.protein / initial.protein


Tier = Literal["flour", "treated_flour", "concentrate", "isolate"]


def tier_of(protein_pct_p50: float, n_steps: int, concentrate_min: float, isolate_min: float) -> Tier:
    """Tier by final protein % (thresholds from applications.json, configurable)."""
    if protein_pct_p50 >= isolate_min:
        return "isolate"
    if protein_pct_p50 >= concentrate_min:
        return "concentrate"
    return "treated_flour" if n_steps else "flour"

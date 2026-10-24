"""Distributions, quasi-random sampling and provenance propagation (source plan §11.1, §12.9).

- PERT(low, mode, high, lambda=4), triangular, uniform and lognormal, all by inverse CDF so
  that one Sobol (or Latin-hypercube) point set drives every uncertain input.
- Extrapolation penalty: a row applied with applicability alpha < 1 has its range widened
  around the mode by w = 1 + k * (1 - alpha), then clipped to the unit's physical bounds.
- Missing data policy (stated on screen): a missing *process* fraction (yield, retention,
  reduction, purity, recovery) is sampled from its full feasible range U(0, 1), tagged
  `assumed` grade D ("no data"); callers opt in with `missing="full_range"`. Any other
  missing quantity is *not computable*; callers must report it instead of guessing a number.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from scipy import stats
from scipy.stats import qmc

from compass.models import Dist, Grade, Param, Range, Tag, Value

PERT_LAMBDA = 4.0
LOGNORMAL_Z = 1.6448536269514722  # low/high of a lognormal row are read as P5/P95 (stated assumption)
_EPS = 1e-9

# ---------------------------------------------------------------- provenance

_TAG_RANK = {Tag.synthetic: 0, Tag.assumed: 1, Tag.published: 2, Tag.measured: 3}
_GRADE_RANK = {Grade.A: 0, Grade.B: 1, Grade.C: 2, Grade.D: 3}


@dataclass(frozen=True)
class Provenance:
    tag: Tag
    grade: Grade | None = None
    source_ids: tuple[str, ...] = ()
    alpha: float | None = None
    status: Literal["data", "no_data", "derived"] = "data"

    @staticmethod
    def of(p: Param) -> Provenance:
        return Provenance(p.tag, p.grade, (p.source_id,) if p.source_id else (), p.alpha)


NO_DATA = Provenance(Tag.assumed, Grade.D, (), None, "no_data")


def combine(provs: Iterable[Provenance]) -> Provenance:
    """Provenance of a derived number: the weakest tag and grade, the lowest alpha, all sources."""
    provs = list(provs)
    if not provs:
        return Provenance(Tag.synthetic, None, (), None, "derived")
    tag = min((p.tag for p in provs), key=_TAG_RANK.__getitem__)
    grades = [p.grade for p in provs if p.grade is not None]
    grade = max(grades, key=_GRADE_RANK.__getitem__) if grades else None
    if any(p.status == "no_data" for p in provs):
        grade = Grade.D
    alphas = [p.alpha for p in provs if p.alpha is not None]
    sources = tuple(dict.fromkeys(s for p in provs for s in p.source_ids))
    return Provenance(tag, grade, sources, min(alphas) if alphas else None, "derived")


# ---------------------------------------------------------------- distributions


def unit_bounds(unit: str) -> tuple[float, float]:
    u = unit.lower()
    if u in ("fraction", "probability"):
        return (0.0, 1.0)
    if u.startswith("%"):
        return (0.0, 100.0)
    return (0.0, np.inf)


def pert_params(low: float, mode: float, high: float, lam: float = PERT_LAMBDA) -> tuple[float, float]:
    span = high - low
    return 1 + lam * (mode - low) / span, 1 + lam * (high - mode) / span


def pert_mean(low: float, mode: float, high: float, lam: float = PERT_LAMBDA) -> float:
    return (low + lam * mode + high) / (lam + 2)


def ppf(dist: Dist, u: np.ndarray, lam: float = PERT_LAMBDA) -> np.ndarray:
    """Inverse CDF of `dist` evaluated at uniform points `u` in (0, 1)."""
    lo, hi = dist.low, dist.high
    if hi == lo:
        return np.full_like(u, lo, dtype=float)
    if dist.type == "uniform":
        return lo + (hi - lo) * u
    if dist.type == "triangular":
        c = (dist.mode - lo) / (hi - lo)
        return stats.triang.ppf(u, c, loc=lo, scale=hi - lo)
    if dist.type == "pert":
        a, b = pert_params(lo, dist.mode, hi, lam)
        return lo + (hi - lo) * stats.beta.ppf(u, a, b)
    if dist.type == "lognormal":
        if lo <= 0:
            raise ValueError("lognormal needs low > 0")
        mu = (np.log(lo) + np.log(hi)) / 2
        sigma = (np.log(hi) - np.log(lo)) / (2 * LOGNORMAL_Z)
        return np.exp(mu + sigma * stats.norm.ppf(u))
    raise ValueError(f"unknown distribution {dist.type}")


def widen(dist: Dist, alpha: float | None, k: float, bounds: tuple[float, float]) -> Dist:
    """Extrapolation penalty: stretch the range around the mode by 1 + k(1 - alpha)."""
    if alpha is None or alpha >= 1.0 or k <= 0:
        return dist
    w = 1.0 + k * (1.0 - alpha)
    centre = dist.mode if dist.mode is not None else (dist.low + dist.high) / 2
    lo = max(bounds[0], centre - (centre - dist.low) * w)
    hi = min(bounds[1], centre + (dist.high - centre) * w)
    if dist.type == "lognormal":
        lo = max(lo, dist.low / w)  # stay positive
    return Dist(type=dist.type, low=lo, mode=dist.mode, high=hi)


# ---------------------------------------------------------------- sampler


@dataclass
class Sampled:
    """One input across all draws. `values` is None when the input is not computable."""

    key: str
    values: np.ndarray | None
    prov: Provenance
    unit: str
    dist: Dist | None = None  # the distribution actually sampled (after widening)

    @property
    def missing(self) -> bool:
        return self.values is None


@dataclass
class _Spec:
    key: str
    param: Param | None
    unit: str
    alpha: float | None
    dist: Dist | None = None
    const: float | None = None
    prov: Provenance = field(default_factory=lambda: NO_DATA)
    col: int | None = None


class Sampler:
    """Register inputs, then draw them all at once from one seeded quasi-random point set."""

    def __init__(
        self,
        n_draws: int,
        seed: int,
        method: Literal["sobol", "lhs"] = "sobol",
        lam: float = PERT_LAMBDA,
        k: float = 1.0,
    ) -> None:
        if n_draws < 2:
            raise ValueError("need at least 2 draws")
        self.n, self.seed, self.method, self.lam, self.k = n_draws, seed, method, lam, k
        self._specs: dict[str, _Spec] = {}
        self.overrides: dict[str, Param] = {}  # lab results (evidence) replace dataset rows
        self.used_overrides: set[str] = set()

    def add(
        self,
        key: str,
        param: Param | None,
        *,
        unit: str | None = None,
        alpha: float | None = None,
        missing: Literal["full_range", "none"] = "none",
    ) -> None:
        """Register `param` under `key`. `alpha` overrides the row's applicability.

        `missing="full_range"`: if the row has no data and is a fraction, sample U(0, 1).
        """
        if key in self._specs:
            return
        if key in self.overrides:
            param, alpha = self.overrides[key], 1.0  # measured on this batch: fully applicable
            self.used_overrides.add(key)
        unit = unit or (param.unit if param else "")
        a = alpha if alpha is not None else (param.alpha if param else None)
        spec = _Spec(key, param, unit, a)
        bounds = unit_bounds(unit)
        if param is not None and param.value is not None:
            spec.const, spec.prov = param.value, Provenance.of(param)
        elif param is not None and param.dist is not None:
            spec.dist, spec.prov = widen(param.dist, a, self.k, bounds), Provenance.of(param)
        elif missing == "full_range" and bounds == (0.0, 1.0):
            spec.dist, spec.prov = Dist(type="uniform", low=0.0, high=1.0), NO_DATA
        if spec.prov is not NO_DATA and a is not None:
            spec.prov = Provenance(spec.prov.tag, spec.prov.grade, spec.prov.source_ids, a)
        self._specs[key] = spec

    def add_value(self, key: str, value: float, unit: str, prov: Provenance) -> None:
        """Register a known constant (e.g. a user input) with explicit provenance."""
        self._specs[key] = _Spec(key, None, unit, prov.alpha, const=value, prov=prov)

    def sample(self) -> dict[str, Sampled]:
        stochastic = [s for s in self._specs.values() if s.dist is not None and s.dist.low != s.dist.high]
        for i, s in enumerate(stochastic):
            s.col = i
        u = self._points(len(stochastic))
        out: dict[str, Sampled] = {}
        for s in self._specs.values():
            if s.const is not None:
                vals = np.full(self.n, float(s.const))
            elif s.dist is not None and s.col is None:
                vals = np.full(self.n, float(s.dist.low))
            elif s.dist is not None:
                lo, hi = unit_bounds(s.unit)
                vals = np.clip(ppf(s.dist, u[:, s.col], self.lam), lo, hi)
            else:
                vals = None
            out[s.key] = Sampled(s.key, vals, s.prov, s.unit, s.dist)
        return out

    def _points(self, d: int) -> np.ndarray:
        if d == 0:
            return np.empty((self.n, 0))
        if self.method == "lhs":
            pts = qmc.LatinHypercube(d=d, seed=self.seed).random(self.n)
        else:
            sob = qmc.Sobol(d=d, scramble=True, seed=self.seed)
            m = int(np.log2(self.n))
            pts = sob.random_base2(m) if 2**m == self.n else sob.random(self.n)
        return np.clip(pts, _EPS, 1 - _EPS)


# ---------------------------------------------------------------- summaries


def summarise(x: np.ndarray, prov: Provenance, unit: str | None = None) -> Range:
    p10, p50, p90 = np.percentile(x, [10, 50, 90])
    return Range(
        p10=float(p10),
        p50=float(p50),
        p90=float(p90),
        unit=unit,
        tag=prov.tag,
        grade=prov.grade,
        source_ids=list(prov.source_ids),
        alpha=prov.alpha,
    )


def as_value(x: float, prov: Provenance, unit: str | None = None) -> Value:
    return Value(
        value=float(x),
        unit=unit,
        tag=prov.tag,
        grade=prov.grade,
        source_ids=list(prov.source_ids),
        alpha=prov.alpha,
    )

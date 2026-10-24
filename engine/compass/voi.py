"""Value of information (source plan §12.9): which single measurement is worth buying first.

Utility of pursuing a chain, per draw (stated on screen):
    U = campaign protein (kg) * margin vs pea (INR/kg protein)      if the spec is met and gates pass
      = - campaign variable cost (INR)                             otherwise (failed pilot)
    U(sell as feed) = 0                                            reference option, always available

    E_now   = max_option E[U]
    EVPI    = E[max_option U] - E_now
    EVPPI(x)= E_x[max_option E[U | x]] - E_now
One input: 25 equal-count bins (the plan's reference estimator). A test that informs several
inputs: regression estimator (Strong-Oakley-Brennan style, quadratic basis per input).
EVSI ~ EVPPI * R with R = var_prior / (var_prior + var_meas) on the log scale (stated
approximation); without an assay CV, R = 1 and EVSI is an upper bound.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

Arr = np.ndarray


def utility(
    campaign_kg: float, protein_per_kg_raw: Arr, margin: Arr, cost_per_kg_raw: Arr, success: Arr
) -> Arr:
    return np.where(success, campaign_kg * protein_per_kg_raw * margin, -campaign_kg * cost_per_kg_raw)


def with_feed(U: Arr) -> Arr:
    """Append the always-available 'sell as feed' option (utility 0)."""
    return np.column_stack([U, np.zeros(U.shape[0])])


def e_now(U: Arr) -> float:
    return float(U.mean(axis=0).max())


def evpi(U: Arr) -> float:
    return max(0.0, float(U.max(axis=1).mean()) - e_now(U))


def evppi_bins(x: Arr, U: Arr, bins: int = 25) -> float:
    """Binning estimator. Discrete inputs (few unique values) use one bin per value."""
    uniq = np.unique(x)
    if uniq.size <= 1:
        return 0.0
    if uniq.size <= bins:
        idx = np.searchsorted(uniq, x)
        k = uniq.size
    else:
        qs = np.quantile(x, np.linspace(0, 1, bins + 1))
        idx = np.clip(np.searchsorted(qs[1:-1], x, side="right"), 0, bins - 1)
        k = bins
    counts = np.bincount(idx, minlength=k).astype(float)
    sums = np.vstack([np.bincount(idx, weights=U[:, o], minlength=k) for o in range(U.shape[1])]).T
    ok = counts > 0
    cond_best = (sums[ok] / counts[ok, None]).max(axis=1)
    w = counts[ok] / counts.sum()
    return _clip(float((w * cond_best).sum()) - e_now(U), U)


def evppi_regression(X: Arr, U: Arr) -> float:
    """E[U_o | X] fitted on [1, x, x^2] per input; EVPPI = E[max fitted] - max E[fitted]."""
    X = np.atleast_2d(X.T).T if X.ndim == 1 else X
    keep = [j for j in range(X.shape[1]) if np.ptp(X[:, j]) > 0]
    if not keep:
        return 0.0
    Z = (X[:, keep] - X[:, keep].mean(0)) / X[:, keep].std(0)
    B = np.column_stack([np.ones(len(Z)), Z, Z**2])
    coef, *_ = np.linalg.lstsq(B, U, rcond=None)
    fitted = B @ coef
    return _clip(float(fitted.max(axis=1).mean() - fitted.mean(axis=0).max()), U)


def _clip(v: float, U: Arr) -> float:
    return float(min(max(v, 0.0), evpi(U)))


def reliability(x: Arr, cv: float | None) -> float | None:
    """R = var_prior / (var_prior + var_meas) on the log scale; None when the assay CV is unknown."""
    if cv is None:
        return None
    x = x[x > 0]
    if x.size < 2:
        return None
    vp = float(np.var(np.log(x)))
    vm = float(np.log1p(cv) ** 2)
    return vp / (vp + vm) if vp + vm > 0 else None


@dataclass
class TestEval:
    test_id: str
    evppi: float
    evsi: float
    upper_bound: bool
    cost: float | None

    @property
    def roi(self) -> float | None:
        return None if not self.cost else self.evsi / self.cost

    @property
    def worth_it(self) -> str:
        if self.cost is None:
            return "unknown"
        return "yes" if self.evsi > self.cost else "no"


def recommend(tests: list[TestEval], evpi_value: float, tiny: float = 1.0) -> tuple[str | None, str]:
    """argmax ROI subject to EVSI > cost; honest outcomes when nothing qualifies (source plan §12.9)."""
    if evpi_value <= tiny or not tests or max(t.evsi for t in tests) <= tiny:
        return None, "No measurement can change the decision: decide now."
    priced = [t for t in tests if t.cost is not None and t.evsi > t.cost]
    if priced:
        best = max(priced, key=lambda t: t.roi or 0.0)
        return best.test_id, "Highest value of information per rupee among tests worth their cost."
    if all(t.cost is not None for t in tests):
        return None, "No test is worth its cost: decide now."
    best = max(tests, key=lambda t: t.evsi)
    return best.test_id, (
        "Highest value of information. Its lab cost is not in the dataset yet: "
        "buy it if a quote is below the expected value shown."
    )

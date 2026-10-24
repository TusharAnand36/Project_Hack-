"""Learning loop: fold one lab result into the analysis (source plan §12.12).

Continuous inputs: lognormal prior (mu0, sigma0) fitted on the log of the current draws,
measurement y with log-error sigma_m = ln(1 + CV):
    mu1 = (mu0/s0^2 + y/sm^2) / (1/s0^2 + 1/sm^2),  s1^2 = 1 / (1/s0^2 + 1/sm^2)
Without a CV the measurement is treated as exact (posterior = measured value) and the UI says so.
Gate priors: Bayes with test sensitivity/specificity, posterior odds = prior odds x LR,
LR+ = sens / (1 - spec), LR- = (1 - sens) / spec.
The input becomes tag `measured`, grade A.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from compass.models import Dist
from compass.sampling import LOGNORMAL_Z


@dataclass(frozen=True)
class Normal:
    mu: float
    sigma: float


def fit_lognormal(samples: np.ndarray) -> Normal | None:
    x = samples[samples > 0]
    if x.size < 2:
        return None
    lx = np.log(x)
    return Normal(float(lx.mean()), float(lx.std()))


def posterior(prior: Normal | None, y: float, cv: float | None) -> Normal | None:
    """None = exact measurement (no assay error known)."""
    if cv is None or y <= 0:
        return None
    sm = float(np.log1p(cv))
    if prior is None or prior.sigma <= 0:
        return Normal(float(np.log(y)), sm)
    w0, wm = 1 / prior.sigma**2, 1 / sm**2
    return Normal((prior.mu * w0 + np.log(y) * wm) / (w0 + wm), float(np.sqrt(1 / (w0 + wm))))


def to_dist(n: Normal, upper: float | None = None) -> Dist:
    """Lognormal row with low/high read as P5/P95 (the sampler's convention)."""
    lo = float(np.exp(n.mu - LOGNORMAL_Z * n.sigma))
    hi = float(np.exp(n.mu + LOGNORMAL_Z * n.sigma))
    if upper is not None:
        hi = min(hi, upper)
        lo = min(lo, hi)
    return Dist(type="lognormal", low=lo, high=hi)


def lr_update(p_fail: float, positive: bool, sensitivity: float, specificity: float) -> float:
    odds = p_fail / (1 - p_fail)
    lr = sensitivity / (1 - specificity) if positive else (1 - sensitivity) / specificity
    post = odds * lr
    return post / (1 + post)

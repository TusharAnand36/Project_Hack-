"""Decision-readiness grade (source plan §12.11): when can a prediction support a reliable decision?

DECISION-GRADE  gates PASS, P(spec) >= 0.80, EVPI / |E_now| <= 0.15 and >= 70% of the top-5
                value drivers graded A/B
NOT VIABLE      any gate FAIL, best P(spec) < 0.20, or best margin P50 < 0
HYPOTHESIS      otherwise, with a "what must be demonstrated" checklist
Thresholds come from costs.json (readiness) and are shown on screen.
"""

from __future__ import annotations

from dataclasses import dataclass

from compass.contract import DecisionGrade, MustDemonstrate, Readiness, ReadinessCheck
from compass.models import Tag
from compass.sampling import Provenance, as_value

CONFIG = Provenance(Tag.assumed, None, (), None, "data")


@dataclass
class Inputs:
    gates_pass: bool
    any_gate_fail: bool
    best_p_spec: float | None
    best_margin_p50: float | None
    evpi: float | None
    e_now: float | None
    driver_grades: list[str | None]  # grades of the top value drivers, best first
    must_demonstrate: list[MustDemonstrate]


def grade(inp: Inputs, cfg: dict[str, float]) -> Readiness:
    p_min, ratio_max = cfg["decision_p_spec_min"], cfg["decision_evpi_ratio_max"]
    ab_min, top_n, nv = (
        cfg["decision_ab_driver_share_min"],
        int(cfg["top_drivers"]),
        cfg["not_viable_p_spec_max"],
    )
    prob = lambda x: as_value(x, CONFIG, "probability")  # noqa: E731
    frac = lambda x: as_value(x, CONFIG, "fraction")  # noqa: E731

    checks = [ReadinessCheck(id="gates", label="All safety gates pass", passed=inp.gates_pass)]
    checks.append(
        ReadinessCheck(
            id="p_spec",
            label=f"Best chain P(spec) ≥ {p_min:g}",
            passed=None if inp.best_p_spec is None else inp.best_p_spec >= p_min,
            value=None if inp.best_p_spec is None else prob(inp.best_p_spec),
            threshold=prob(p_min),
        )
    )
    ratio = None
    if inp.evpi is not None and inp.e_now not in (None, 0):
        ratio = inp.evpi / abs(inp.e_now)
    checks.append(
        ReadinessCheck(
            id="evpi_ratio",
            label=f"Remaining uncertainty EVPI / |E_now| ≤ {ratio_max:g}",
            passed=None if ratio is None else ratio <= ratio_max,
            value=None if ratio is None else frac(ratio),
            threshold=frac(ratio_max),
        )
    )
    top = inp.driver_grades[:top_n]
    share = (sum(g in ("A", "B") for g in top) / len(top)) if top else None
    checks.append(
        ReadinessCheck(
            id="evidence",
            label=f"≥ {ab_min:.0%} of the top {top_n} value drivers graded A/B",
            passed=None if share is None else share >= ab_min,
            value=None if share is None else frac(share),
            threshold=frac(ab_min),
        )
    )

    if (
        inp.any_gate_fail
        or (inp.best_p_spec is not None and inp.best_p_spec < nv)
        or (inp.best_margin_p50 is not None and inp.best_margin_p50 < 0)
    ):
        g = DecisionGrade.not_viable
    elif all(c.passed for c in checks):
        g = DecisionGrade.decision_grade
    else:
        g = DecisionGrade.hypothesis_grade
    return Readiness(
        grade=g,
        checks=checks,
        must_demonstrate=inp.must_demonstrate if g is not DecisionGrade.decision_grade else [],
    )

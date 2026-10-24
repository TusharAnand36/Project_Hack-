import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from compass import voi
from compass.analyze import analyze
from compass.contract import AnalyzeRequest, DecisionGrade
from compass.data import load_dataset
from compass.readiness import Inputs, grade


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


def toy(n=4096, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 1, n)  # informative input
    z = rng.uniform(0, 1, n)  # pure noise input
    U = voi.with_feed(np.column_stack([1000 * (x - 0.5), 200 * (0.4 - x)]))
    return x, z, U


def test_evppi_bounds_and_informative_input():
    x, z, U = toy()
    total = voi.evpi(U)
    ex, ez = voi.evppi_bins(x, U), voi.evppi_bins(z, U)
    assert 0 <= ez <= ex <= total + 1e-9
    assert ex > 0.9 * total  # x explains all the uncertainty
    assert ez < 0.1 * total


@settings(max_examples=30, deadline=None)
@given(st.integers(0, 10_000))
def test_evppi_never_negative_or_above_evpi(seed):
    rng = np.random.default_rng(seed)
    U = voi.with_feed(rng.normal(0, 1, (512, 3)))
    x = rng.normal(size=512)
    for v in (voi.evppi_bins(x, U), voi.evppi_regression(np.column_stack([x, rng.normal(size=512)]), U)):
        assert 0 <= v <= voi.evpi(U) + 1e-9


def test_binary_input_uses_one_bin_per_value():
    rng = np.random.default_rng(1)
    g = rng.uniform(size=2000) > 0.5
    U = voi.with_feed(np.where(g, 100.0, -100.0)[:, None])
    assert voi.evppi_bins(g.astype(float), U) == pytest.approx(voi.evpi(U))


def test_reliability_and_recommendation_rules():
    assert voi.reliability(np.exp(np.random.default_rng(2).normal(0, 0.5, 1000)), None) is None
    r = voi.reliability(np.exp(np.random.default_rng(2).normal(0, 0.5, 1000)), 0.1)
    assert 0 < r < 1
    tests = [voi.TestEval("a", 100, 100, True, 50), voi.TestEval("b", 300, 300, True, 1000)]
    assert voi.recommend(tests, 500)[0] == "a"  # only one is worth its cost
    none_worth = [voi.TestEval("a", 100, 100, True, 500)]
    assert voi.recommend(none_worth, 500) == (None, "No test is worth its cost: decide now.")
    assert voi.recommend(tests, 0.0)[0] is None  # nothing can change the decision
    unpriced = [voi.TestEval("a", 100, 100, True, None), voi.TestEval("b", 300, 300, True, None)]
    assert voi.recommend(unpriced, 500)[0] == "b"


def test_readiness_rules():
    cfg = {
        "decision_p_spec_min": 0.8,
        "decision_evpi_ratio_max": 0.15,
        "decision_ab_driver_share_min": 0.7,
        "top_drivers": 5,
        "not_viable_p_spec_max": 0.2,
    }
    ok = Inputs(True, False, 0.9, 50.0, 10.0, 1000.0, ["A", "B", "A", "A", "C"], [])
    assert grade(ok, cfg).grade is DecisionGrade.decision_grade
    assert grade(Inputs(**{**ok.__dict__, "best_p_spec": 0.5}), cfg).grade is DecisionGrade.hypothesis_grade
    assert (
        grade(Inputs(**{**ok.__dict__, "driver_grades": ["D", "D", "A"]}), cfg).grade
        is DecisionGrade.hypothesis_grade
    )
    assert grade(Inputs(**{**ok.__dict__, "any_gate_fail": True}), cfg).grade is DecisionGrade.not_viable
    assert grade(Inputs(**{**ok.__dict__, "best_p_spec": 0.1}), cfg).grade is DecisionGrade.not_viable
    assert grade(Inputs(**{**ok.__dict__, "best_margin_p50": -5.0}), cfg).grade is DecisionGrade.not_viable


def run(ds, **kw):
    kw.setdefault("n_draws", 2048)
    return analyze(AnalyzeRequest.model_validate(kw), ds)


def test_missing_utility_and_quotes_leave_economic_voi_unestimated(ds):
    r = analyze(AnalyzeRequest.model_validate(ds.presets["groundnut_beverage"].payload), ds)
    assert r.voi is None and r.voi_status == "not_estimated"
    assert r.verdict.p_go is None
    assert r.readiness.grade is DecisionGrade.hypothesis_grade
    assert r.plan.tests and any("Critical safety" in t.why for t in r.plan.tests)
    assert r.plan.budget_inr.low is None
    assert r.picks is None


def test_higher_pea_price_changes_reference_without_inventing_margin_probability(ds):
    lo = run(ds, byproduct="groundnut_cake", application="beverage", pea={"base_usd_per_kg": 2.5})
    hi = run(ds, byproduct="groundnut_cake", application="beverage", pea={"base_usd_per_kg": 4.5})
    assert hi.pea.landed_inr_per_kg_protein.p50 > lo.pea.landed_inr_per_kg_protein.p50
    assert all(c.p_margin_positive is None for c in hi.chains)


def test_measured_b1_does_not_clear_missing_total_aflatoxins(ds):
    r = run(ds, byproduct="groundnut_cake", application="beverage", batch={"afb1_ppb": {"value": 5}})
    assert r.voi is None
    assert any(g.id == "G1" and g.state.value == "TEST-FIRST" for g in r.gates)

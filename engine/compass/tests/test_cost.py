import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from compass.cost import Economics, StepResources, chain_cost, crf, scaled_capex

ECON = dict(scale_kg_day=500.0, discount_rate=0.12, life_years=10, operating_days=300, utilisation=0.8)


def full_step(x=1.0):
    one = np.ones(4)
    return StepResources("phytase", one * x, one * 0.2, one * 5, one * 3, one * 2, one * 2e6, one * 1000)


def test_crf_and_six_tenths():
    assert crf(0.12, 10) == pytest.approx(0.176984, rel=1e-5)
    assert scaled_capex(100.0, 2.0, 1.0) == pytest.approx(100 * 2**0.6)


@settings(max_examples=60, deadline=None)
@given(st.floats(1, 100), st.floats(0.05, 0.9), st.floats(0, 20), st.floats(0, 0.5))
def test_cost_at_least_raw_cost(raw, prot, tariff, overhead):
    e = Economics(
        **ECON,
        tariff_inr_per_kwh=tariff,
        water_inr_per_m3=30.0,
        wage_inr_per_h=100.0,
        qa_inr_per_kg_raw=1.0,
        overhead_frac=overhead,
    )
    p = np.full(4, prot)
    r = chain_cost(raw, [full_step()], np.ones(4), p, e)
    assert r.complete
    assert np.all(r.per_kg_raw >= raw) and np.all(r.per_kg_protein >= raw / prot - 1e-9)
    assert not np.isnan(r.per_kg_protein).any()


def test_missing_components_are_named_and_excluded():
    e = Economics(**ECON)  # no tariff, water price, wage, QA, overhead
    step = StepResources("extrude", np.ones(4))
    r = chain_cost(27.0, [step], np.ones(4), np.full(4, 0.5), e)
    assert not r.complete
    assert {"extrude: energy", "extrude: labour", "QA cost", "overhead"} <= set(r.missing)
    assert np.allclose(r.per_kg_protein, 54.0)  # lower bound = raw material only
    assert r.kwh_per_kg_protein is None


def test_raw_flour_baseline_needs_no_processing_inputs():
    r = chain_cost(27.0, [], np.ones(4), np.full(4, 0.5), Economics(**ECON))
    assert r.complete and np.allclose(r.per_kg_protein, 54.0)


def test_missing_raw_price_is_reported():
    r = chain_cost(None, [], np.ones(4), np.full(4, 0.5), Economics(**ECON))
    assert r.missing == ["raw material price"]


def test_larger_scale_lowers_capital_per_kg():
    small = chain_cost(
        27.0, [full_step()], np.ones(4), np.full(4, 0.5), Economics(**{**ECON, "scale_kg_day": 500.0})
    )
    big = chain_cost(
        27.0, [full_step()], np.ones(4), np.full(4, 0.5), Economics(**{**ECON, "scale_kg_day": 5000.0})
    )
    assert np.all(big.breakdown_per_kg_protein["capital"] < small.breakdown_per_kg_protein["capital"])

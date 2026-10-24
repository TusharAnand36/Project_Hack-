import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from compass.models import Dist, Grade, Param, Tag
from compass.sampling import (
    NO_DATA,
    Provenance,
    Sampler,
    combine,
    pert_mean,
    ppf,
    widen,
)

U = np.linspace(0.0005, 0.9995, 20000)


@st.composite
def ordered(draw):
    a = draw(st.floats(-100, 100, allow_nan=False))
    span = draw(st.floats(0.1, 100))
    m = a + span * draw(st.floats(0.0, 1.0))
    return a, m, a + span


@settings(max_examples=60, deadline=None)
@given(ordered())
def test_pert_mean_matches_analytic(t):
    a, m, b = t
    x = ppf(Dist(type="pert", low=a, mode=m, high=b), U)
    assert abs(x.mean() - pert_mean(a, m, b)) <= 0.01 * (b - a)


@settings(max_examples=60, deadline=None)
@given(ordered(), st.sampled_from(["pert", "triangular", "uniform"]))
def test_draws_within_bounds(t, kind):
    a, m, b = t
    x = ppf(Dist(type=kind, low=a, mode=m, high=b), U)
    assert np.all(x >= a - 1e-9) and np.all(x <= b + 1e-9) and not np.isnan(x).any()


def test_lognormal_low_high_are_p5_p95():
    x = ppf(Dist(type="lognormal", low=1.0, high=4.0), np.array([0.05, 0.95]))
    assert x == pytest.approx([1.0, 4.0], rel=1e-6)


def test_widen_respects_alpha_and_bounds():
    d = Dist(type="pert", low=0.75, mode=0.84, high=0.92)
    assert widen(d, 1.0, 1.0, (0, 1)) == d
    w = widen(d, 0.4, 1.0, (0, 1))  # w = 1.6
    assert w.low == pytest.approx(0.84 - 0.09 * 1.6) and w.high == pytest.approx(0.84 + 0.08 * 1.6)
    assert w.mode == d.mode
    clipped = widen(Dist(type="uniform", low=0.825, high=0.95), 0.0, 1.0, (0, 1))  # w = 2
    assert clipped.high == pytest.approx(1.0) and clipped.low == pytest.approx(0.8875 - 0.0625 * 2)


def test_same_seed_same_draws_and_different_seed_differs():
    p = Param(dist=Dist(type="pert", low=1, mode=2, high=5), unit="ppb", tag="published", source_id="x")

    def run(seed):
        s = Sampler(1024, seed)
        s.add("a", p)
        s.add("b", p.model_copy(update={"dist": Dist(type="uniform", low=0, high=1)}))
        return s.sample()

    r1, r2, r3 = run(42), run(42), run(7)
    assert np.array_equal(r1["a"].values, r2["a"].values)
    assert not np.array_equal(r1["a"].values, r3["a"].values)


def test_missing_fraction_gets_full_range_and_other_missing_is_not_computable():
    s = Sampler(256, 1)
    s.add("yield", Param(unit="fraction", tag="assumed"), missing="full_range")
    s.add("kwh", Param(unit="kWh/kg input", tag="assumed"), missing="full_range")
    s.add("overhead", Param(unit="fraction", tag="assumed"))  # not a process fraction: no full range
    out = s.sample()
    assert out["overhead"].missing
    assert out["yield"].prov is NO_DATA and 0 <= out["yield"].values.min() and out["yield"].values.max() <= 1
    assert out["kwh"].missing


def test_combine_takes_weakest():
    a = Provenance(Tag.published, Grade.B, ("s1",), 1.0)
    b = Provenance(Tag.assumed, Grade.D, ("s2",), 0.4)
    c = combine([a, b])
    assert (c.tag, c.grade, c.alpha, c.source_ids) == (Tag.assumed, Grade.D, 0.4, ("s1", "s2"))
    assert combine([a, NO_DATA]).grade is Grade.D

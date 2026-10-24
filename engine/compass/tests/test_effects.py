import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from compass import effects as fx

frac = st.floats(0.0, 1.0, allow_nan=False)
pos_frac = st.floats(0.01, 1.0, allow_nan=False)
vec = lambda s: arrays(np.float64, 16, elements=s)  # noqa: E731


@settings(max_examples=100, deadline=None)
@given(vec(frac), vec(frac), vec(pos_frac), vec(pos_frac), vec(st.floats(0.05, 0.9)))
def test_balance_never_creates_protein(m, rho, purity, recovery, p0):
    start = fx.start(16, p0)
    b = fx.step(start, "process", mass_yield=np.maximum(m, 1e-3), protein_retention=rho)
    b = fx.step(b, "fractionation", purity=purity, recovery=recovery)
    assert np.all(b.protein <= start.protein + 1e-12)
    assert np.all(b.protein_frac <= fx.MAX_PROTEIN_FRAC + 1e-9)
    assert np.all(fx.retained(b, start) <= 1 + 1e-12)
    assert not np.isnan(b.protein_frac).any()


def test_fractionation_sets_purity():
    b = fx.step(
        fx.start(3, np.full(3, 0.5)), "fractionation", purity=np.full(3, 0.85), recovery=np.full(3, 0.6)
    )
    assert np.allclose(b.protein, 0.3) and np.allclose(b.protein_frac, 0.85)


def test_protein_fraction_capped():
    b = fx.step(
        fx.start(2, np.full(2, 0.6)), "process", mass_yield=np.full(2, 0.5), protein_retention=np.ones(2)
    )
    assert np.allclose(b.protein_frac, 0.95)


@settings(max_examples=100, deadline=None)
@given(vec(st.floats(0, 10)), vec(frac), vec(st.floats(0, 10)))
def test_reduction_between_floor_and_start(level, r, floor):
    after = fx.reduce_compound(level, r, floor)
    assert np.all(after <= level + 1e-12)
    assert np.all(after >= np.minimum(floor, level) - 1e-12)


def test_reductions_compose_without_synergy():
    lvl = np.array([2.0])
    two = fx.reduce_compound(fx.reduce_compound(lvl, np.array([0.5])), np.array([0.5]))
    assert np.allclose(two, 0.5)


def test_normalisation():
    assert np.allclose(fx.to_dry_basis(np.array([46.0]), np.array([0.08])), 50.0)
    assert np.allclose(fx.true_protein(np.array([0.625]), np.array([5.71])), 0.571)
    assert fx.proximate_sum_warning({"p": 50, "f": 10, "fi": 5, "a": 5, "c": 10}) is not None
    assert fx.proximate_sum_warning({"p": 50, "f": None}) is None


def test_tiers():
    assert fx.tier_of(30, 0, 45, 75) == "flour"
    assert fx.tier_of(30, 2, 45, 75) == "treated_flour"
    assert fx.tier_of(60, 1, 45, 75) == "concentrate"
    assert fx.tier_of(85, 1, 45, 75) == "isolate"

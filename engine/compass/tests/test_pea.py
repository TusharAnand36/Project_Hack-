import numpy as np
import pytest

from compass.pea import (
    PeaInputs,
    apply_scenario,
    break_even_base_usd,
    landed_per_kg_product,
    landed_per_kg_protein,
    margin_vs_pea,
)


def defaults(duty):
    return PeaInputs(base_usd_per_kg=3.2, usd_inr=96.0, freight_frac=0.08, duty_frac=duty, protein_frac=0.85)


def test_source_plan_sanity_example():
    # §12.8: 3.2 x 96 = 307; x 1.08 = 332; x 1.44 = 478 per kg product; / 0.85 = ~562 per kg protein
    full = defaults(0.4396)
    assert landed_per_kg_product(full) == pytest.approx(477.6, abs=0.5)
    assert landed_per_kg_protein(full) == pytest.approx(562, abs=1)
    # IGST credited (~22%): 332 x 1.22 = 405 per kg product, ~476 per kg protein
    assert landed_per_kg_protein(defaults(0.22)) == pytest.approx(476, abs=1)


def test_break_even_inverts_landed_cost():
    p = defaults(0.4396)
    be = break_even_base_usd(p, 400.0)
    assert landed_per_kg_protein(PeaInputs(be, 96.0, 0.08, 0.4396, 0.85)) == pytest.approx(400.0)


def test_higher_pea_price_never_lowers_margin():
    base = np.linspace(2.3, 4.6, 50)
    m = margin_vs_pea(PeaInputs(base, 96.0, 0.08, 0.4396, 0.85, buyer_discount=0.1), 400.0)
    assert np.all(np.diff(m) > 0)


def test_scenarios_set_and_scale():
    p = defaults(0.4396)
    assert apply_scenario(p, {"usd_inr": 105}, {}).usd_inr == 105
    assert float(apply_scenario(p, {}, {"base_usd_per_kg": 1.25}).base_usd_per_kg) == pytest.approx(4.0)
    assert landed_per_kg_protein(apply_scenario(p, {}, {"freight_frac": 1.2})) > landed_per_kg_protein(p)

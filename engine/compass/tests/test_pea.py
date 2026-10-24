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


def test_shared_benchmark_and_as_supplied_isolate_match():
    from compass.analyze import analyze
    from compass.contract import AnalyzeRequest
    from compass.data import load_dataset

    ds = load_dataset()
    results = [
        analyze(AnalyzeRequest.model_validate({**p.payload, "n_draws": 256}), ds) for p in ds.presets.values()
    ]
    benchmark = results[0].pea.landed_inr_per_kg_protein
    for result in results:
        assert result.pea.landed_inr_per_kg_protein == benchmark
    isolate = results[-1]
    assert len(isolate.chains) == 1 and isolate.chains[0].steps == []
    raw = isolate.chains[0]
    assert raw.protein_pct_final.p50 == pytest.approx(80.2)
    assert raw.cost_complete
    assert raw.cost_inr_per_kg_protein.p50 == pytest.approx(benchmark.p50)


def test_isolate_supplier_quote_overrides_shared_purchase_cost():
    from compass.analyze import analyze
    from compass.contract import AnalyzeRequest
    from compass.data import load_dataset

    r = analyze(
        AnalyzeRequest(
            byproduct="pea_protein_isolate", application="beverage", raw_price_inr_per_kg=400, n_draws=256
        ),
        load_dataset(),
    )
    assert r.chains[0].cost_inr_per_kg_protein.p50 == pytest.approx(400 / 0.802)

import pytest

from compass.analyze import AnalyzeError, analyze
from compass.contract import AnalyzeRequest, UpdateEvidenceRequest
from compass.data import load_dataset
from compass.learning import update_evidence


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


def run(ds, **kw):
    return analyze(
        AnalyzeRequest.model_validate(
            {"byproduct": "sunflower_cake", "application": "extruded_snack", "n_draws": 256, **kw}
        ),
        ds,
    )


def test_missing_evidence_is_not_zero_probability_or_fabricated_yield(ds):
    result = run(ds)
    assert result.verdict.label.value == "TEST-FIRST" and result.verdict.p_go is None
    assert result.voi is None and result.voi_status == "not_estimated"
    assert result.picks is None and set(result.dimensions) == {"safety", "technical", "economic", "evidence"}
    assert any(c.steps for c in result.chains)
    assert all(c.p_spec is None and c.e_utility is None for c in result.chains)
    assert all(c.protein_pct_final is None and c.cost_inr_per_kg_protein is None for c in result.chains)
    assert all(c.ingredient_yield is None for c in result.chains)
    assert result.plan.tests[0].why.startswith("Critical safety")
    from compass.analyze import build_sampler

    draws = build_sampler(
        AnalyzeRequest(byproduct="sunflower_cake", application="extruded_snack"), ds, 256, 42
    ).sample()
    assert draws["t.phytase.m"].values is None


def test_scenario_values_never_clear_contaminant_gates(ds):
    result = run(
        ds, batch={"hexane_ppm": {"value": 1, "tag": "assumed"}, "afb1_ppb": {"value": 1, "tag": "synthetic"}}
    )
    assert next(g for g in result.gates if g.id == "G1").state.value == "TEST-FIRST"
    assert next(g for g in result.gates if g.id == "G4").state.value == "TEST-FIRST"


def test_incompatible_assay_basis_does_not_create_a_diagnosis_ratio(ds):
    result = run(
        ds,
        batch={
            "pb_ppm": {
                "value": 2,
                "basis": "dry_matter",
                "method": "ICP-MS",
                "report_reference": "TEST-DRY-REPORT",
            }
        },
    )
    row = next(d for d in result.diagnosis if d.compound == "lead")
    assert row.ratio is None and row.p_exceed is None
    assert row.comparison_status == "incompatible_basis"
    assert row.basis == "dry_matter" and row.method == "ICP-MS"
    assert "TEST-DRY-REPORT" in row.note


def test_cost_target_changes_economics_not_safety_or_diagnosis(ds):
    base = dict(byproduct="pea_protein_isolate", raw_price_inr_per_kg=400)
    low = run(ds, **base, targets={"max_cost_inr_per_kg_protein": 100})
    high = run(ds, **base, targets={"max_cost_inr_per_kg_protein": 1000})
    assert low.gates == high.gates and low.diagnosis == high.diagnosis
    assert low.chains[0].economic_status == "exceeds_target"
    assert high.chains[0].economic_status == "meets_target"
    assert low.verdict.label.value == high.verdict.label.value == "TEST-FIRST"


def test_target_calculators_and_original_price_basis(ds):
    benchmark = run(ds, targets={"cost_method": "benchmark", "required_discount_pct": 20})
    assert benchmark.cost_target.amount.value == pytest.approx(
        benchmark.pea.landed_inr_per_kg_protein.p50 * 0.8
    )
    budget = run(
        ds, targets={"cost_method": "product_budget", "product_budget_inr": 25, "product_protein_kg": 0.1}
    )
    assert budget.cost_target.amount.value == 250
    missing = run(ds, targets={"cost_method": "product_budget"})
    assert missing.cost_target.amount is None


def test_reported_protein_basis_and_mass_balance_are_separate(ds):
    result = run(ds, batch={"protein_pct": {"value": 30, "basis": "as_received"}}, raw_price_inr_per_kg=60)
    raw = next(c for c in result.chains if not c.steps)
    assert raw.protein_pct_final.p50 == 30 and raw.initial_protein_kg.p50 == 30
    assert raw.recovered_protein_kg.p50 == 30 and raw.protein_retained.p50 == 1
    assert raw.ingredient_yield.p50 == 1
    assert raw.cost_inr_per_kg_protein.p50 == 200
    dry = run(ds, batch={"protein_pct": {"value": 50, "basis": "dry_matter"}, "moisture_pct": {"value": 20}})
    assert next(c for c in dry.chains if not c.steps).protein_pct_final.p50 == 40
    unknown = run(ds, batch={"protein_pct": {"value": 50, "basis": "dry_matter"}})
    assert all(c.cost_inr_per_kg_protein is None for c in unknown.chains)


def test_ratio_needs_compatible_measured_values_and_justified_threshold(ds):
    result = run(ds, byproduct="groundnut_cake")
    tia = next(row for row in result.diagnosis if row.compound == "trypsin_inhibitor")
    assert tia.p_exceed is None and tia.ratio is None and not tia.limiting
    assert "Illustrative" in tia.note
    measured = run(
        ds,
        batch={"phytate_pct": {"value": 2}},
        targets={"max_phytate_pct": 1, "phytate_target_type": "internal_target"},
    )
    row = next(row for row in measured.diagnosis if row.compound == "phytic_acid")
    assert row.ratio.p50 == 2


def test_functional_reference_separates_sample_forms_and_assay_times(ds):
    comparison = run(ds).functional_comparison
    assert len(comparison.properties) == 8
    wac = next(row for row in comparison.properties if row.id == "wac")
    assert "2.8" in wac.oilseed_flour and "3.2" in wac.oilseed_isolate
    assert "Not reported" in wac.pea_isolate and not wac.comparable
    esi = next(row for row in comparison.properties if row.id == "esi")
    assert "30" in esi.pea_conditions and "24" in esi.oilseed_flour
    assert "not a head-to-head" in comparison.note


def test_lab_unit_and_lot_mismatch_are_rejected(ds):
    req = AnalyzeRequest(
        byproduct="sunflower_cake", application="extruded_snack", batch={"lot_id": "LOT-1"}, n_draws=256
    )
    with pytest.raises(AnalyzeError, match="Incompatible unit"):
        update_evidence(UpdateEvidenceRequest(request=req, input="batch.pb_ppm", value=1, unit="µg/kg"), ds)
    with pytest.raises(AnalyzeError, match="batch ID"):
        update_evidence(
            UpdateEvidenceRequest(request=req, input="batch.pb_ppm", value=1, unit="mg/kg", batch_id="LOT-2"),
            ds,
        )


def test_go_to_pilot_needs_documented_safety_quote_and_functional_validation(ds):
    batch = {
        key: {"value": 0}
        for key in (
            "afb1_ppb",
            "total_aflatoxins_ppb",
            "hexane_ppm",
            "pb_ppm",
            "cd_ppm",
            "arsenic_ppm",
            "hg_ppm",
        )
    }
    batch.update(
        protein_pct={
            "value": 80.2,
            "basis": "as_received",
            "method": "Kjeldahl, recorded laboratory factor",
            "report_reference": "TEST-COA",
        },
        lot_id="TEST-LOT",
        supplier="Test supplier",
        source_reference="TEST-SUPPLIER-RECORD",
    )
    process = {
        "food_grade_supply": True,
        "storage": "hygienic",
        "regulatory_review_reference": "TEST-REVIEW",
        "functional_validation_reference": "TEST-FUNCTIONAL-REPORT",
    }
    kw = dict(
        byproduct="pea_protein_isolate",
        batch=batch,
        process=process,
        raw_price_inr_per_kg=400,
        price_source="TEST-QUOTE",
        price_date="2026-10-25",
        price_boundary="Delivered as-supplied isolate purchase, QA included",
        targets={"max_cost_inr_per_kg_protein": 600},
    )
    ready = run(ds, **kw)
    assert ready.verdict.label.value == "GO" and ready.verdict.p_go is None
    process["regulatory_review_reference"] = None
    held = run(ds, **kw)
    assert held.verdict.label.value == "TEST-FIRST"

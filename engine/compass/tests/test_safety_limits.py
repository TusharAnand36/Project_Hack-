import pytest
from pydantic import ValidationError

from compass.analyze import analyze
from compass.contract import AnalyzeRequest, Batch, GateState
from compass.data import load_dataset
from compass.gates import evaluate

LIMITS = [
    ("hexane_ppm", "hexane_residue", "G4", 10),
    ("afb1_ppb", "aflatoxin_b1", "G1", 10),
    ("total_aflatoxins_ppb", "total_aflatoxins", "G1", 15),
    ("pb_ppm", "lead", "G3", 1),
    ("cd_ppm", "cadmium", "G3", 0.1),
    ("arsenic_ppm", "arsenic", "G3", 0.5),
    ("hg_ppm", "mercury", "G3", 0.1),
]


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


def request(**kw):
    return AnalyzeRequest(byproduct="sunflower_cake", application="beverage", n_draws=256, **kw)


@pytest.mark.parametrize("field,compound,gid,limit", LIMITS)
@pytest.mark.parametrize("factor,state", [(0.9, GateState.PASS), (1, GateState.PASS), (1.01, GateState.FAIL)])
def test_contaminant_boundaries(ds, field, compound, gid, limit, factor, state):
    outcomes = evaluate(request(batch={field: {"value": limit * factor}}), ds)
    gate = next(x.gate for x in outcomes if x.gate.id == gid)
    check = next(c for c in gate.checks if c.compound == compound)
    assert check.state is state and check.limit.value == limit
    if state is GateState.FAIL:
        assert gate.state is GateState.FAIL


def test_all_materials_and_markets_use_all_seven_project_thresholds(ds):
    for bp in ds.byproducts:
        for market in ("domestic", "export_EU"):
            req = AnalyzeRequest(byproduct=bp, application="beverage", market=market)
            checks = [c for outcome in evaluate(req, ds) for c in outcome.gate.checks]
            assert {c.compound: c.limit.value for c in checks} == {c: v for _, c, _, v in LIMITS}
            assert all(c.state is GateState.TEST_FIRST for c in checks)


def test_all_results_at_limits_clear_contaminant_gates(ds):
    req = request(batch={field: {"value": v} for field, _, _, v in LIMITS})
    assert all(g.gate.state is GateState.PASS for g in evaluate(req, ds) if g.gate.checks)
    req.batch.total_aflatoxins_ppb = None
    g1 = next(g.gate for g in evaluate(req, ds) if g.gate.id == "G1")
    assert g1.state is GateState.TEST_FIRST
    assert "Total aflatoxins" in g1.reasons[0] and "not measured" in g1.reasons[0]


def test_exceedance_reaches_verdict_and_individual_diagnosis(ds):
    r = analyze(request(batch={"pb_ppm": {"value": 1.1}, "cd_ppm": {"value": 0.05}}), ds)
    assert r.verdict.label.value == "NO-GO" and not r.chains
    lead = next(d for d in r.diagnosis if d.compound == "lead")
    cadmium = next(d for d in r.diagnosis if d.compound == "cadmium")
    assert (
        lead.level.p50 == 1.1
        and lead.tolerance.value == 1
        and lead.p_exceed is None
        and lead.comparison_status == "exceeds_threshold"
    )
    assert (
        cadmium.level.p50 == 0.05
        and cadmium.tolerance.value == 0.1
        and cadmium.p_exceed is None
        and cadmium.comparison_status == "within_threshold"
    )


def test_hexane_certificate_or_route_cannot_override_high_measured_result(ds):
    req = request(
        batch={"hexane_ppm": {"value": 11}}, process={"oil_route": "cold_pressed", "hexane_cert": True}
    )
    assert next(g.gate.state for g in evaluate(req, ds) if g.gate.id == "G4") is GateState.FAIL
    req = request(process={"solvent_extracted": True, "hexane_cert": True})
    assert next(g.gate.state for g in evaluate(req, ds) if g.gate.id == "G4") is GateState.TEST_FIRST
    req = request(process={"oil_route": "cold_pressed", "route_reference": "mill process record"})
    assert next(g.gate.state for g in evaluate(req, ds) if g.gate.id == "G4") is GateState.PASS


def test_inorganic_arsenic_does_not_substitute_for_total_arsenic(ds):
    g3 = next(
        g.gate for g in evaluate(request(batch={"inorganic_as_ppm": {"value": 0.1}}), ds) if g.gate.id == "G3"
    )
    assert next(c for c in g3.checks if c.compound == "arsenic").measured is None


def test_total_aflatoxins_cannot_be_less_than_b1():
    with pytest.raises(ValidationError, match="Total aflatoxins"):
        Batch(afb1_ppb={"value": 10}, total_aflatoxins_ppb={"value": 9})

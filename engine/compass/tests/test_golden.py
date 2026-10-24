"""Golden scenarios GT1-GT6 (source plan §15). GT7/GT8 arrive with Phase 6."""

import pytest

from compass.analyze import analyze
from compass.contract import AnalyzeRequest, GateState, VerdictLabel
from compass.data import load_dataset

N = 2048  # enough draws for stable assertions, fast tests


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


def run(ds, **payload):
    payload.setdefault("n_draws", N)
    return analyze(AnalyzeRequest.model_validate(payload), ds)


def gate(r, gid):
    return next(g for g in r.gates if g.id == gid)


def test_gt1_groundnut_unmeasured_aflatoxin(ds):
    r = run(ds, byproduct="groundnut_cake", application="beverage", market="domestic")
    g1 = gate(r, "G1")
    assert g1.state is GateState.TEST_FIRST
    assert g1.prior_p_fail.value == pytest.approx(0.53) and g1.prior_p_fail.tag.value == "published"
    assert r.verdict.label is not VerdictLabel.GO
    assert any("prior P(fail) = 0.53" in x for x in r.verdict.reasons)


def test_gt2_groundnut_aflatoxin_60_ppb(ds):
    r = run(ds, byproduct="groundnut_cake", application="beverage", batch={"afb1_ppb": {"value": 60}})
    assert gate(r, "G1").state is GateState.FAIL
    assert r.verdict.label is VerdictLabel.NO_GO
    assert r.chains == []  # chains are not ranked for a failed gate
    assert any("divert to feed or re-source" in a.lower() for a in r.verdict.actions)


def test_legacy_stability_gate_still_handles_measured_and_unstabilised_batches(ds):
    from compass.gates import g2_rancidity

    req = AnalyzeRequest(
        byproduct="sunflower_cake",
        application="beverage",
        process={"hours_since_milling": 24, "stabilised": False},
    )
    assert g2_rancidity(ds.gates["G2"], req).gate.state is GateState.FAIL
    req = AnalyzeRequest.model_validate(
        {
            "byproduct": "sunflower_cake",
            "application": "beverage",
            "batch": {"ffa_pct": {"value": 2}},
            "process": {"stabilised": True},
        }
    )
    assert g2_rancidity(ds.gates["G2"], req).gate.state is GateState.PASS


def test_gt5_almond_meat_analogue(ds):
    r = run(ds, byproduct="almond_cake", application="meat_analogue")
    kinds = {i.kind for i in r.issues}
    assert "no_treatment_needed" in kinds and "allergen" in kinds
    assert gate(r, "G6").state is GateState.FLAG
    assert any("raw material price missing" in x for x in r.verdict.reasons)  # price flag
    assert r.chains  # not an empty page


def test_gt6_no_solvents(ds):
    for bp, app in [("groundnut_cake", "beverage"), ("soybean_cake", "extruded_snack")]:
        r = run(ds, byproduct=bp, application=app, constraints={"no_solvents": True})
        assert all("ethanol_wash" not in c.steps for c in r.chains)


def test_presets_run_fast_and_tag_every_number(ds):
    import time

    for p in ds.presets.values():
        t = time.perf_counter()
        r = analyze(AnalyzeRequest.model_validate(p.payload), ds)
        assert time.perf_counter() - t < 3.0  # NFR-01
        _assert_tagged(r.model_dump(mode="json"))


def _assert_tagged(node, path="$"):
    if isinstance(node, dict):
        if ("p50" in node or "value" in node) and isinstance(node.get("p50", node.get("value")), int | float):
            assert node.get("tag") in ("measured", "published", "assumed", "synthetic"), path
        for k, v in node.items():
            _assert_tagged(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _assert_tagged(v, f"{path}[{i}]")


def test_same_seed_same_result(ds):
    a = run(ds, byproduct="groundnut_cake", application="beverage", seed=7)
    b = run(ds, byproduct="groundnut_cake", application="beverage", seed=7)
    a.meta.elapsed_ms = b.meta.elapsed_ms = 0
    assert a.model_dump() == b.model_dump()


def test_measured_aflatoxin_below_half_limit_passes(ds):
    r = run(ds, byproduct="groundnut_cake", application="beverage", batch={"afb1_ppb": {"value": 10}})
    assert gate(r, "G1").state is GateState.PASS


def test_allergen_free_claim_fails(ds):
    r = run(ds, byproduct="groundnut_cake", application="beverage", claims=["allergen_free"])
    assert gate(r, "G6").state is GateState.FAIL and r.verdict.label is VerdictLabel.NO_GO


def test_measured_phytate_is_used_and_tagged(ds):
    r = run(ds, byproduct="groundnut_cake", application="beverage", batch={"phytate_pct": {"value": 2.0}})
    d = next(x for x in r.diagnosis if x.compound == "phytic_acid")
    assert d.level.p50 == pytest.approx(2.0) and d.level.tag.value == "measured" and d.p_exceed.value == 1.0


def test_user_price_makes_almond_cost_computable(ds):
    r = run(ds, byproduct="almond_cake", application="meat_analogue", raw_price_inr_per_kg=60)
    top = r.chains[0]
    assert top.cost_inr_per_kg_protein is not None and "cost_not_computable" not in top.badges
    assert r.pea.break_even_base_usd_per_kg is not None

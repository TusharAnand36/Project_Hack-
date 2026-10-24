"""Learning loop (§12.12) and GT8."""

import numpy as np
import pytest

from compass import update as upd
from compass.analyze import analyze
from compass.contract import AnalyzeRequest, UpdateEvidenceRequest
from compass.data import load_dataset
from compass.learning import update_evidence


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


def test_posterior_variance_shrinks_and_moves_towards_measurement():
    prior = upd.Normal(mu=np.log(2.0), sigma=0.5)
    post = upd.posterior(prior, 1.0, 0.1)
    assert post.sigma < prior.sigma
    assert np.log(1.0) < post.mu < prior.mu
    assert upd.posterior(prior, 1.0, None) is None  # no CV: exact measurement


def test_likelihood_ratio_update():
    assert upd.lr_update(0.53, False, 0.95, 0.90) < 0.1
    assert upd.lr_update(0.53, True, 0.95, 0.90) > 0.9


def req(ds, **kw):
    return AnalyzeRequest.model_validate({**ds.presets["groundnut_beverage"].payload, "n_draws": 2048, **kw})


def test_gt8_measured_phytate_is_tagged_and_changes_value_of_information(ds):
    r = update_evidence(
        UpdateEvidenceRequest(request=req(ds), input="cmp.phytic_acid", value=1.8, cv=0.05), ds
    )
    assert r.measurement.tag.value == "measured" and r.measurement.grade.value == "A"
    after = analyze(r.after_request, ds)
    d = next(x for x in after.diagnosis if x.compound == "phytic_acid")
    assert d.level.tag.value == "measured" and d.level.grade.value == "A"
    assert r.before.best_p_spec is None and r.after.best_p_spec is None
    assert after.voi is None  # an assay does not create missing process costs or calibrated priors
    assert d.level.p50 == pytest.approx(1.8, rel=0.05)


def test_measured_aflatoxin_over_limit_flips_to_no_go(ds):
    r = update_evidence(UpdateEvidenceRequest(request=req(ds), input="gate.G1.u", value=60), ds)
    assert r.before.verdict.value == "TEST-FIRST" and r.after.verdict.value == "NO-GO"


def test_negative_elisa_records_screen_without_uncalibrated_probability(ds):
    r = update_evidence(UpdateEvidenceRequest(request=req(ds), input="gate.G1.u", result="negative"), ds)
    assert r.posterior is None and r.prior is None
    assert "no calibrated prior" in r.note
    g1 = next(g for g in analyze(r.after_request, ds).gates if g.id == "G1")
    assert g1.state.value == "TEST-FIRST" and g1.prior_p_fail is None


def test_fraction_inputs_reject_percentages(ds):
    from compass.analyze import AnalyzeError

    with pytest.raises(AnalyzeError, match="fraction"):
        update_evidence(UpdateEvidenceRequest(request=req(ds), input="t.moist_heat.rho", value=62), ds)
    r = update_evidence(
        UpdateEvidenceRequest(request=req(ds), input="t.moist_heat.rho", value=0.62, cv=0.05), ds
    )
    assert r.posterior.p90 <= 1.0


def test_unknown_evidence_input_rejected(ds):
    from compass.analyze import AnalyzeError

    bad = req(ds, evidence=[{"input": "cmp.unobtainium", "value": 1, "unit": "%"}])
    with pytest.raises(AnalyzeError, match="unknown"):
        analyze(bad, ds)

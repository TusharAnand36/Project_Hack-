"""/update-evidence: enter one lab result, re-run the analysis, show before and after (§12.12).



"Enter one lab number and the recommendation sharpens" is the demo moment, so the before/after

snapshot names the parts that move: verdict, readiness, P(GO), best chain, P(spec), the

recommended test and the EVPPI ranking.

"""

from __future__ import annotations

from pydantic import ValidationError

from compass import update as upd
from compass.analyze import AnalyzeError, _cfg, _input_label, analyze, build_sampler
from compass.contract import (
    AnalyzeRequest,
    AnalyzeResponse,
    Evidence,
    Measurement,
    Snapshot,
    UpdateEvidenceRequest,
    UpdateEvidenceResponse,
)
from compass.data import Dataset
from compass.models import Grade, Param, Tag
from compass.sampling import Provenance, Sampler, as_value, summarise

MEASURED = Provenance(Tag.measured, Grade.A, ("user_batch",))


def snapshot(r: AnalyzeResponse) -> Snapshot:
    best_id = (r.picks.best_expected_value if r.picks else None) or (r.chains[0].id if r.chains else None)
    best = next((c for c in r.chains if c.id == best_id), None)
    return Snapshot(
        verdict=r.verdict.label,
        grade=r.verdict.grade,
        p_go=r.verdict.p_go,
        best_chain=best_id,
        best_p_spec=best.p_spec if best else None,
        recommended_test=r.voi.recommended_test if r.voi else None,
        evppi=r.voi.evppi[:5] if r.voi else [],
    )


def _with_evidence(req: AnalyzeRequest, ev: Evidence) -> AnalyzeRequest:
    out = req.model_copy(deep=True)
    out.evidence = [e for e in out.evidence if e.input != ev.input] + [ev]
    return out


def update_evidence(body: UpdateEvidenceRequest, ds: Dataset) -> UpdateEvidenceResponse:
    req = body.request
    before = analyze(req, ds)
    key = body.input
    gate_fields = {
        "batch.total_aflatoxins_ppb": "total_aflatoxins_ppb",
        "batch.hexane_ppm": "hexane_ppm",
        "batch.pb_ppm": "pb_ppm",
        "batch.cd_ppm": "cd_ppm",
        "batch.arsenic_ppm": "arsenic_ppm",
        "batch.hg_ppm": "hg_ppm",
    }
    expected_unit = (
        "µg/kg"
        if key in ("gate.G1.u", "gate.G1", "batch.total_aflatoxins_ppb")
        else "mg/kg" if key in gate_fields else None
    )
    aliases = {"ppb": "µg/kg", "ug/kg": "µg/kg", "ppm": "mg/kg"}
    if expected_unit and body.unit and aliases.get(body.unit, body.unit) != expected_unit:
        raise AnalyzeError(f"Incompatible unit: this analyte requires {expected_unit}")
    metadata = dict(
        method=body.method,
        laboratory=body.laboratory,
        report_reference=body.report_reference,
        report_date=body.report_date,
        basis=body.basis,
    )
    if body.batch_id and req.batch.lot_id and body.batch_id != req.batch.lot_id:
        raise AnalyzeError("Lab report batch ID does not match the selected lot")
    label, test_id = _input_label(key, ds)
    if key in gate_fields:
        if body.value is None:
            raise AnalyzeError("Enter a quantitative laboratory result")
        after_req = req.model_copy(deep=True)
        setattr(
            after_req.batch, gate_fields[key], Measurement(value=body.value, tag=Tag.measured, **metadata)
        )
        after_req.batch = type(req.batch).model_validate(after_req.batch.model_dump())
        prior, post = None, None
        measurement = as_value(body.value, MEASURED, expected_unit)
        note = "Traceable batch laboratory result recorded; the affected contaminant gate is re-evaluated."
    elif key in ("gate.G1.u", "gate.G1"):
        label = "aflatoxin B1 of this lot (G1)"
        if body.value is not None:  # quantitative HPLC result decides the gate
            after_req = req.model_copy(deep=True)
            after_req.batch.afb1_ppb = Measurement(value=body.value, tag=Tag.measured, **metadata)
            after_req.evidence = [e for e in after_req.evidence if e.input != "gate.G1"]
            measurement = as_value(body.value, MEASURED, "ppb")
            prior, post = None, None
            note = "AFB1 measured on a composite sample: the gate is now decided by the measurement."
        elif body.result is not None:
            if req.batch.afb1_ppb is not None:
                raise AnalyzeError("G1 already has a measured AFB1 value; a screen cannot update it")
            note = (
                f"ELISA screen {body.result} recorded. Confirm B1 and total aflatoxins by HPLC; "
                "no calibrated prior is available for the project thresholds, so no probability is inferred."
            )
            ev = Evidence(input="gate.G1", unit="probability", tag=Tag.measured, grade=Grade.B, note=note)
            after_req = _with_evidence(req, ev)
            prior, measurement, post = None, None, None
        else:
            raise AnalyzeError("for aflatoxin give a measured value in ppb (HPLC) or an ELISA result")
    else:
        if body.value is None:
            raise AnalyzeError("give the measured value")
        n = req.n_draws or int(_cfg(ds, "engine", "n_draws"))
        seed = req.seed if req.seed is not None else int(_cfg(ds, "engine", "seed"))
        draws = build_sampler(req, ds, n, seed).sample()
        if key not in draws:
            raise AnalyzeError(f"'{key}' is not an input of this analysis")
        s = draws[key]
        unit = s.unit
        if body.unit and aliases.get(body.unit, body.unit) != unit:
            raise AnalyzeError(f"Incompatible unit: {label} requires {unit}")
        if unit in ("fraction", "probability") and body.value > 1:
            raise AnalyzeError(f"'{label}' is a fraction: enter 0-1 (e.g. 0.62), not a percentage")
        prior_n = upd.fit_lognormal(s.values) if s.values is not None else None
        prior = summarise(s.values, s.prov, unit) if s.values is not None else None
        cv = body.cv
        if cv is None and test_id in ds.lab_tests and ds.lab_tests[test_id].cv.value is not None:
            cv = ds.lab_tests[test_id].cv.value
        post_n = upd.posterior(prior_n, body.value, cv)
        method = f" ({body.method})" if body.method else ""
        if post_n is None:
            ev = Evidence(
                input=key,
                value=body.value,
                unit=unit,
                note=f"measured{method}; no assay CV given: treated as exact",
            )
            post = as_value(body.value, MEASURED, unit)
            note = "No assay CV was given, so the measurement is treated as exact. Enter the lab's CV to account for assay error."
        else:
            dist = upd.to_dist(post_n, upper=1.0 if unit in ("fraction", "probability") else None)
            ev = Evidence(
                input=key, dist=dist, unit=unit, note=f"posterior after measurement{method}, CV {cv:g}"
            )
            post = summarise(draws_from(dist, n, seed, unit), MEASURED, unit)
            note = f"Lognormal update with assay CV {cv:g}: the range narrows around the measurement."
        ev.basis = body.basis
        ev.method, ev.laboratory = body.method, body.laboratory
        ev.report_reference, ev.report_date = body.report_reference, body.report_date
        after_req = _with_evidence(req, ev)
        # a batch field for the same input would win over evidence; the lab result replaces it
        if key == "cmp.phytic_acid":
            after_req.batch.phytate_pct = None
        if key == "bp.protein":
            after_req.batch.protein_pct = None
        measurement = as_value(body.value, MEASURED, unit)
    try:
        after_req = AnalyzeRequest.model_validate(after_req.model_dump())
    except ValidationError as exc:
        raise AnalyzeError("Inconsistent batch or assay metadata: " + str(exc)) from exc
    after = analyze(after_req, ds)
    return UpdateEvidenceResponse(
        input=key,
        label=label,
        prior=prior,
        measurement=measurement,
        posterior=post,
        note=note,
        before=snapshot(before),
        after=snapshot(after),
        after_request=after_req,
    )


def draws_from(dist, n: int, seed: int, unit: str):
    s = Sampler(n, seed)
    s.add("x", Param(dist=dist, unit=unit, tag=Tag.measured))
    return s.sample()["x"].values

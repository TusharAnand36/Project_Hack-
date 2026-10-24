"""Regression snapshot of preset 1 (website plan Phase 5): key outputs must not drift silently.

Regenerate deliberately after a data or engine change:
    PYTHONPATH=engine .venv/bin/python -m compass.tests.test_regression
"""

import json
from pathlib import Path

import pytest

from compass.analyze import analyze
from compass.contract import AnalyzeRequest
from compass.data import load_dataset

SNAP = Path(__file__).with_name("golden") / "preset1.json"


def key_values() -> dict:
    ds = load_dataset()
    r = analyze(AnalyzeRequest.model_validate(ds.presets["groundnut_beverage"].payload), ds)
    top = r.chains[0]
    return {
        "dataset_version": ds.version,
        "verdict": r.verdict.label.value,
        "grade": r.verdict.grade.value,
        "g1_prior": next(g for g in r.gates if g.id == "G1").prior_p_fail,
        "top_chain": top.id,
        "top_p_spec": None if top.p_spec is None else round(top.p_spec.value, 3),
        "top_protein_p50": None if top.protein_pct_final is None else round(top.protein_pct_final.p50, 2),
        "pea_landed_p50": round(r.pea.landed_inr_per_kg_protein.p50, 1),
        "recommended_test": None if r.voi is None else r.voi.recommended_test,
        "evpi": None if r.voi is None else round(r.voi.evpi.value, -2),
        "chains_total": r.meta.chains_total,
    }


def test_preset1_matches_snapshot():
    if not SNAP.exists():
        pytest.skip("no snapshot yet")
    want = json.loads(SNAP.read_text())
    got = key_values()
    if got["dataset_version"] != want["dataset_version"]:
        pytest.skip("dataset changed: regenerate the snapshot")
    for k, v in want.items():
        if isinstance(v, float):
            assert got[k] == pytest.approx(v, rel=0.02), k
        else:
            assert got[k] == v, k


if __name__ == "__main__":
    SNAP.parent.mkdir(exist_ok=True)
    SNAP.write_text(json.dumps(key_values(), indent=2) + "\n")
    print(f"wrote {SNAP}")

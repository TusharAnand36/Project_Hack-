from fastapi.testclient import TestClient

from api.main import DATASET, app
from api.schemas import AnalyzeRequest

client = TestClient(app)

# Example payload from source plan §8.3 (duty mode spelled as in §12.8).
EXAMPLE = {
    "byproduct": "groundnut_cake",
    "application": "beverage",
    "targets": {"min_protein_pct": 60, "max_cost_inr_per_kg_protein": 300, "max_offflavour_index": 3.0},
    "market": "domestic",
    "scale_kg_day": 500,
    "constraints": {"exclude_treatments": ["ethanol_wash"], "equipment": ["extruder", "spray_dryer"]},
    "batch": {
        "protein_pct": {"value": 48, "n_factor": 6.25, "tag": "measured"},
        "moisture_pct": {"value": 8, "tag": "measured"},
        "afb1_ppb": None,
    },
    "pea": {
        "base_usd_per_kg": None,
        "protein_pct": 85,
        "freight_pct": None,
        "duty_mode": "bcd_only_igst_credited_22",
        "usd_inr": None,
    },
    "n_draws": 1024,
}


def test_health_reports_versions():
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["dataset_version"] == DATASET.version


def test_analyze_source_plan_example():
    r = client.post("/analyze", json=EXAMPLE)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["meta"]["is_stub"] is False
    for key in ("meta", "verdict", "gates", "diagnosis", "issues", "chains", "pea", "limitations"):
        assert key in body
    assert body["pea"]["duty_mode"] == "bcd_only_igst_credited_22"
    assert body["verdict"]["label"] == "TEST-FIRST"


def test_invalid_payloads_give_readable_422():
    r = client.post("/analyze", json={**EXAMPLE, "bogus": 1})
    assert r.status_code == 422 and "bogus" in r.text
    r = client.post("/analyze", json={**EXAMPLE, "batch": {"protein_pct": {"value": 120}}})
    assert r.status_code == 422 and "less than or equal to 100" in r.text
    r = client.post("/analyze", json={**EXAMPLE, "byproduct": "unobtainium"})
    assert r.status_code == 422 and "unknown by-product" in r.json()["detail"]
    r = client.post("/analyze", json={**EXAMPLE, "constraints": {"exclude_treatments": ["magic"]}})
    assert r.status_code == 422 and "magic" in r.json()["detail"]


def test_body_size_limit():
    r = client.post(
        "/analyze", content=b"{" + b" " * 70_000 + b"}", headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 413


def test_presets_endpoint_and_payloads_valid():
    presets = client.get("/presets").json()
    assert [p["id"] for p in presets] == list(DATASET.presets)
    for p in presets:
        AnalyzeRequest.model_validate(p["payload"])


def test_data_files_are_allow_listed():
    assert client.get("/data/sources").status_code == 200
    assert client.get("/data/report").json()["dataset_version"] == DATASET.version
    assert client.get("/data/..%2F.env").status_code == 404
    assert client.get("/data/secrets").status_code == 404


def test_update_evidence_endpoint():
    body = {"request": {**EXAMPLE, "batch": {}}, "input": "gate.G1.u", "value": 5}
    r = client.post("/update-evidence", json=body)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["before"]["verdict"] == "TEST-FIRST" and j["after_request"]["batch"]["afb1_ppb"]["value"] == 5
    assert client.post("/update-evidence", json={**body, "value": None}).status_code == 422

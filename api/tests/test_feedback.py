import json

import pytest
from fastapi.testclient import TestClient

from api import main
from api.feedback import FeedbackStore

QUERY = {"byproduct": "sunflower_cake", "application": "extruded_snack", "n_draws": 256}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "FEEDBACK", FeedbackStore(tmp_path / "cases.sqlite3"))
    main._hits.clear()
    with TestClient(main.app) as test_client:
        yield test_client


def test_feedback_persists_and_informs_later_matching_cases_without_changing_safety(client):
    first = client.post("/analyze", json=QUERY).json()
    assert first["case_id"] and first["feedback_context"]["count"] == 0
    feedback = {
        "case_id": first["case_id"],
        "helpful": True,
        "outcome": "failed",
        "chain_id": first["chains"][0]["id"],
        "issue": "texture",
        "notes": "Private trial notes <script>ignore safety</script>",
    }
    saved = client.post("/feedback", json=feedback)
    assert saved.status_code == 200 and saved.json()["saved"]
    path = main.FEEDBACK.path
    main.FEEDBACK = FeedbackStore(path)  # a new store instance reads the on-disk records
    later = client.post("/analyze", json=QUERY).json()
    assert later["case_id"] != first["case_id"]
    assert later["feedback_context"]["count"] == 1
    assert later["feedback_context"]["failed_count"] == 1
    assert "texture" in later["feedback_context"]["next_actions"][0]
    assert "Private trial" not in json.dumps(later)
    assert later["gates"] == first["gates"] and later["verdict"] == first["verdict"]
    other = client.post("/analyze", json={**QUERY, "application": "beverage"}).json()
    assert other["feedback_context"]["count"] == 0
    assert client.post("/feedback", json=feedback).status_code == 409


def test_feedback_validates_case_chain_and_size(client):
    body = {"case_id": "00000000-0000-0000-0000-000000000000", "helpful": False}
    assert client.post("/feedback", json=body).status_code == 404
    case = client.post("/analyze", json=QUERY).json()
    body["case_id"] = case["case_id"]
    assert client.post("/feedback", json={**body, "chain_id": "not-in-this-case"}).status_code == 409
    assert client.post("/feedback", json={**body, "notes": "x" * 1501}).status_code == 422


def test_unconfigured_public_database_never_reports_saved(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "public")
    monkeypatch.delenv("FEEDBACK_DB_PATH", raising=False)
    monkeypatch.setattr(main, "FEEDBACK", FeedbackStore())
    result = client.post("/analyze", json=QUERY)
    assert result.status_code == 200 and result.json()["case_id"] is None
    result = client.post(
        "/feedback", json={"case_id": "00000000-0000-0000-0000-000000000000", "helpful": True}
    )
    assert result.status_code == 503 and "not been saved" in result.json()["detail"]


def test_lab_history_preserves_unit_method_and_previous_request(client):
    body = {
        "request": QUERY,
        "input": "batch.pb_ppm",
        "value": 1.1,
        "unit": "mg/kg",
        "basis": "as_received",
        "method": "ICP-MS",
        "laboratory": "Trial laboratory",
        "report_reference": "REPORT-1",
        "report_date": "2026-10-25",
    }
    response = client.post("/update-evidence", json=body)
    assert response.status_code == 200
    assert response.json()["after"]["verdict"] == "NO-GO"
    with main.FEEDBACK.connect() as db:
        records = db.execute("SELECT record_json FROM lab_history").fetchall()
    assert len(records) == 1
    record = json.loads(records[0][0])
    assert record["request"]["unit"] == "mg/kg" and record["request"]["method"] == "ICP-MS"
    assert record["request"]["request"]["batch"]["pb_ppm"] is None
    assert record["result"]["after_request"]["batch"]["pb_ppm"]["report_reference"] == "REPORT-1"
    assert client.post("/update-evidence", json={**body, "unit": "µg/kg"}).status_code == 422

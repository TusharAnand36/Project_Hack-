from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_stub_is_marked_synthetic():
    r = client.post("/analyze", json={"byproduct_id": "groundnut_cake", "application_id": "beverage"})
    assert r.status_code == 200
    body = r.json()
    assert body["is_stub"] is True
    assert body["verdict"]["p_go"]["tag"] == "synthetic"
    assert all(c["cost_per_kg_protein"]["tag"] == "synthetic" for c in body["chains"])


def test_analyze_rejects_unknown_fields():
    r = client.post("/analyze", json={"byproduct_id": "x", "application_id": "y", "bogus": 1})
    assert r.status_code == 422

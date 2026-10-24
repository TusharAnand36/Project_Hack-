from fastapi.testclient import TestClient

from api.main import app

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
}


def _numeric_leaves(node, path=""):
    """Yield (path, dict) for every Value/Range-like dict in a response."""
    if isinstance(node, dict):
        if "p50" in node or ("value" in node and isinstance(node["value"], int | float)):
            yield path, node
        for k, v in node.items():
            yield from _numeric_leaves(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _numeric_leaves(v, f"{path}[{i}]")


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_accepts_source_plan_example():
    r = client.post("/analyze", json=EXAMPLE)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["meta"]["is_stub"] is True
    for key in ("meta", "verdict", "gates", "diagnosis", "chains", "pea", "voi", "plan", "limitations"):
        assert key in body
    assert body["pea"]["duty_mode"] == "bcd_only_igst_credited_22"


def test_every_numeric_leaf_is_tagged_synthetic_in_stub():
    leaves = list(_numeric_leaves(client.post("/analyze", json=EXAMPLE).json()))
    assert leaves
    for path, leaf in leaves:
        assert leaf.get("tag") == "synthetic", path


def test_analyze_rejects_unknown_fields():
    r = client.post("/analyze", json={**EXAMPLE, "bogus": 1})
    assert r.status_code == 422


def test_analyze_rejects_impossible_protein():
    bad = {**EXAMPLE, "batch": {"protein_pct": {"value": 120}}}
    assert client.post("/analyze", json=bad).status_code == 422

import json
import shutil
from pathlib import Path

import pytest

from compass.data import (
    DEFAULT_DATA_DIR,
    DataError,
    is_missing,
    iter_params,
    load_dataset,
    preset_inputs,
    render_todo,
    report,
)
from compass.models import Param, Tag


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


@pytest.fixture
def data_copy(tmp_path: Path) -> Path:
    dst = tmp_path / "data"
    shutil.copytree(DEFAULT_DATA_DIR, dst)
    return dst


def _edit(path: Path, fn) -> None:
    obj = json.loads(path.read_text(encoding="utf-8"))
    fn(obj)
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_all_files_load(ds):
    assert ds.version
    assert next(iter(ds.byproducts)) == "sunflower_cake"
    assert "deoiled_rice_bran" not in ds.byproducts
    assert {"sunflower_cake", "groundnut_cake", "soybean_cake", "almond_cake", "pea_protein_isolate"} <= set(
        ds.byproducts
    )
    assert {"beverage", "extruded_snack", "meat_analogue"} == set(ds.applications)
    assert len(ds.treatments) >= 7
    assert {f"G{i}" for i in range(1, 8)} == set(ds.gates)
    assert len(ds.presets) == 5


def test_every_source_id_resolves(ds):
    for ref in iter_params(ds):
        if ref.param.source_id is not None:
            assert ref.param.source_id in ds.sources, ref.path


def test_distributions_ordered_and_units_bounded(ds):
    for ref in iter_params(ds):
        d = ref.param.dist
        if d is not None:
            assert d.low <= d.high, ref.path
            if d.mode is not None:
                assert d.low <= d.mode <= d.high, ref.path
        nums = [ref.param.value] if ref.param.value is not None else []
        if d is not None:
            nums += [x for x in (d.low, d.mode, d.high) if x is not None]
        if ref.param.unit.startswith("%"):
            assert all(0 <= x <= 100 for x in nums), ref.path
        if ref.param.unit in ("fraction", "probability"):
            assert all(0 <= x <= 1 for x in nums), ref.path


def test_published_numbers_have_sources(ds):
    for ref in iter_params(ds):
        p = ref.param
        if p.tag in (Tag.published, Tag.measured) and not is_missing(p):
            assert p.source_id, ref.path


def test_no_measured_rows_without_permission(ds):
    # PhD measured data is excluded until the owner gives permission (source plan §11.3).
    assert not [r.path for r in iter_params(ds) if r.param.tag is Tag.measured]


def test_review_draft_rows_are_grade_c_and_flagged(ds):
    for ref in iter_params(ds):
        p = ref.param
        if p.source_id in ("user_review_draft", "user_review_final"):
            assert p.grade is not None and p.grade.value == "C", ref.path
            assert p.notes and "verify" in p.notes.lower(), ref.path


def test_no_treatment_claims_to_remove_aflatoxin(ds):
    for t in ds.treatments.values():
        assert all(e.compound != "aflatoxin_b1" for e in t.effects), t.id


def test_transferred_evidence_has_alpha_below_one(ds):
    for t in ds.treatments.values():
        for e in t.effects:
            measured_on = (e.reduction.conditions or {}).get("measured_on")
            if measured_on in ds.reference_species and set(e.applies_to) & set(ds.byproducts):
                assert e.reduction.alpha is not None and e.reduction.alpha < 0.7, (t.id, e.compound)


def test_bad_row_names_file_and_id(data_copy):
    def break_range(obj):
        gnc = next(b for b in obj["byproducts"] if b["id"] == "groundnut_cake")
        gnc["composition"]["crude_protein_pct"]["dist"] = {"type": "uniform", "low": 60, "high": 45}

    _edit(data_copy / "byproducts.json", break_range)
    with pytest.raises(DataError, match=r"byproducts\.json: row 'groundnut_cake'"):
        load_dataset(data_copy)


def test_percent_out_of_range_rejected(data_copy):
    def too_much_fat(o):
        o["byproducts"][0]["composition"]["fat_pct"].update(dist=None, value=140)

    _edit(data_copy / "byproducts.json", too_much_fat)
    with pytest.raises(DataError, match="outside"):
        load_dataset(data_copy)


def test_unknown_source_rejected(data_copy):
    _edit(data_copy / "costs.json", lambda o: o["pea"]["base_usd_per_kg"].update(source_id="nope_2020"))
    with pytest.raises(DataError, match="unknown source_id 'nope_2020'"):
        load_dataset(data_copy)


def test_unknown_compound_in_treatment_rejected(data_copy):
    def bad_compound(o):
        o["treatments"][0]["effects"][0].update(compound="unobtainium")

    _edit(data_copy / "treatments.json", bad_compound)
    with pytest.raises(DataError, match="unknown compound 'unobtainium'"):
        load_dataset(data_copy)


def test_report_counts(ds):
    rep = report(ds)
    assert rep["params_filled"] + rep["params_missing"] == rep["params_total"]
    assert sum(rep["by_tag"].values()) == rep["params_filled"]
    assert set(rep["presets"]) == set(ds.presets)


def test_todo_lists_missing_and_skips_config(ds):
    todo = render_todo(ds)
    assert "groundnut_cake.compounds.phytic_acid" in todo
    assert "engine.n_draws" not in todo
    assert "trypsin_inhibitor` |" not in todo or "definitional" not in todo


def test_preset_inputs_respect_exclusions_and_species(ds):
    paths = {r.path for r in preset_inputs(ds, "groundnut_beverage")}
    assert not any(p.startswith("ethanol_wash.") for p in paths)  # excluded by the preset
    assert "beverage.tolerances.min_protein_pct" in paths
    assert "G1.params.prior_p_fail" in paths
    assert not any("sesame" in p for p in paths)
    phytase_effects = [p for p in paths if p.startswith("phytase.effects[")]
    assert phytase_effects and all(p.startswith("phytase.effects[0:") for p in phytase_effects)


def test_staging_candidates_are_valid_and_unmerged(ds):
    files = sorted((DEFAULT_DATA_DIR / "_staging").glob("*.json"))  # includes git-ignored *.local.json
    for c in [c for f in files for c in json.loads(f.read_text(encoding="utf-8"))["candidates"]]:
        p = Param.model_validate(c["proposed"])
        if c.get("requires") == "owner_permission":
            assert p.tag is Tag.measured and p.source_id == "user_phd_report", c["id"]
        else:
            assert p.tag is Tag.assumed and p.grade.value == "D", c["id"]
        assert p.source_id in ds.sources, c["id"]
        assert c["status"] in ("pending", "merged", "rejected")

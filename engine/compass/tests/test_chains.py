import pytest

from compass.chains import candidates, enumerate_chains, valid
from compass.data import load_dataset


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


def all_chains(ds, bp, app, **kw):
    c = candidates(ds, bp, kw.get("exclude", []), kw.get("no_solvents", False), kw.get("equipment", []))
    return c, enumerate_chains(c.allowed, ds, bp, app)


def test_raw_flour_always_first(ds):
    _, seqs = all_chains(ds, "groundnut_cake", "beverage")
    assert seqs[0] == ()


def test_rules_hold_for_every_chain(ds):
    for bp in ds.byproducts:
        for app in ds.applications:
            _, seqs = all_chains(ds, bp, app)
            assert len(seqs) == len(set(seqs))
            for s in seqs:
                assert valid(s, ds, bp, app)
                assert len(s) <= 4
                assert not (
                    "phytase" in s and "moist_heat" in s and s.index("phytase") < s.index("moist_heat")
                )
                assert not ("ssf_ferment" in s and "soak_germinate" in s)
                if "phytase" in s and "ae_iep" in s:
                    assert s.index("phytase") < s.index("ae_iep")
                if "ae_iep" in s and s[-1] != "ae_iep":
                    assert app == "meat_analogue" and s[-1] == "extrude"
                if "extrude" in s:
                    assert s.index("extrude") in (0, len(s) - 1)
                if bp == "deoiled_rice_bran" and s:
                    assert s[0] == "stabilise"


def test_exclusions_never_add_chains(ds):
    _, base = all_chains(ds, "groundnut_cake", "beverage")
    _, fewer = all_chains(ds, "groundnut_cake", "beverage", exclude=["phytase"])
    assert set(fewer) <= set(base) and all("phytase" not in s for s in fewer)


def test_equipment_filter(ds):
    c, seqs = all_chains(ds, "groundnut_cake", "beverage", equipment=["extruder"])
    assert "ae_iep" in c.removed and "ssf_ferment" in c.removed
    assert all("ae_iep" not in s for s in seqs)


def test_no_solvents_removes_ethanol_wash(ds):
    c, _ = all_chains(ds, "groundnut_cake", "beverage", no_solvents=True)
    assert "ethanol_wash" in c.removed

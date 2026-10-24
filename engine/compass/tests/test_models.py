import pytest
from pydantic import ValidationError

from compass.models import Dist, Param, Range, Tag


def test_dist_rejects_mode_outside_bounds():
    with pytest.raises(ValidationError):
        Dist(type="pert", low=1, mode=5, high=3)


def test_pert_requires_mode():
    with pytest.raises(ValidationError):
        Dist(type="pert", low=1, high=3)


def test_param_value_xor_dist():
    with pytest.raises(ValidationError):
        Param(value=1, dist=Dist(type="uniform", low=0, high=2), unit="ppb", tag=Tag.assumed)


def test_range_ordered():
    with pytest.raises(ValidationError):
        Range(p10=3, p50=2, p90=1, tag=Tag.synthetic)
    assert Range(p10=1, p50=2, p90=3, tag="published").tag is Tag.published


def test_param_accepts_source_plan_field_names():
    p = Param(
        dist=Dist(type="pert", low=0.75, mode=0.84, high=0.92),
        unit="fraction",
        tag="published",
        evidence_grade="C",
        applicability=0.4,
        conditions={"measured_on": "sunflower_cake", "pH": 5.5},
    )
    assert p.grade.value == "C" and p.alpha == 0.4


def test_param_missing_data_is_allowed():
    assert Param(unit="% dry basis", tag="assumed").value is None

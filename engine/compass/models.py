"""Core provenance types shared by the engine, the API and the generated TS types.

Every numeric value the engine returns is wrapped in one of these so that its
origin (tag), evidence strength (grade) and applicability (alpha) travel with it.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class Tag(str, Enum):
    """Where a number came from."""

    measured = "measured"
    published = "published"
    assumed = "assumed"
    synthetic = "synthetic"


class Grade(str, Enum):
    """Evidence grade, A (strongest) to D (weakest)."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


class _Strict(BaseModel):
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, json_schema_serialization_defaults_required=True
    )


Conditions = dict[str, str | float | int | bool | None]


class Dist(_Strict):
    """A probability distribution described by low / mode / high."""

    type: Literal["pert", "triangular", "uniform", "lognormal"]
    low: float
    mode: float | None = None
    high: float

    @model_validator(mode="after")
    def _ordered(self) -> Dist:
        if self.low > self.high:
            raise ValueError(f"low ({self.low}) > high ({self.high})")
        if self.mode is not None and not (self.low <= self.mode <= self.high):
            raise ValueError(f"mode ({self.mode}) outside [{self.low}, {self.high}]")
        if self.type in ("pert", "triangular") and self.mode is None:
            raise ValueError(f"{self.type} needs a mode")
        return self


class Param(_Strict):
    """One input parameter: a point value or a distribution, with provenance.

    Both `value` and `dist` may be missing (null); that means "no data yet" and
    the row must appear in DATA_TODO.md (source plan §11.1). The data files use
    the source plan's names `evidence_grade` / `applicability`; both spellings load.
    """

    value: float | None = None
    dist: Dist | None = None
    unit: str
    tag: Tag
    grade: Grade | None = Field(default=None, validation_alias=AliasChoices("evidence_grade", "grade"))
    source_id: str | None = None
    alpha: float | None = Field(
        default=None, ge=0.0, le=1.0, validation_alias=AliasChoices("applicability", "alpha")
    )
    conditions: Conditions | None = None
    notes: str | None = None
    verification_status: str | None = None
    basis: str | None = None
    method: str | None = None
    material_form: str | None = None
    extraction_route: str | None = None
    source_location: str | None = None

    @model_validator(mode="after")
    def _value_or_dist(self) -> Param:
        if self.value is not None and self.dist is not None:
            raise ValueError("give either value or dist, not both")
        return self


class Value(_Strict):
    """A single engine output number (e.g. a probability), with provenance."""

    value: float
    unit: str | None = None
    tag: Tag
    grade: Grade | None = None
    source_ids: list[str] = Field(default_factory=list)
    alpha: float | None = Field(default=None, ge=0.0, le=1.0)


class Range(_Strict):
    """An engine output summarised as P10 / P50 / P90, with provenance."""

    p10: float
    p50: float
    p90: float
    unit: str | None = None
    tag: Tag
    grade: Grade | None = None
    source_ids: list[str] = Field(default_factory=list)
    alpha: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _ordered(self) -> Range:
        if not (self.p10 <= self.p50 <= self.p90):
            raise ValueError("expected p10 <= p50 <= p90")
        return self

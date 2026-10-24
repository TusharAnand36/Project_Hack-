"""Upcycle Compass HTTP API.

Phase 0: /health and a stub /analyze whose numbers are placeholders tagged
"synthetic". The real pipeline replaces the stub in Phase 3.
"""

from __future__ import annotations

import os
from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from compass import DATASET_VERSION, __version__
from compass.models import Range, Tag

app = FastAPI(title="Upcycle Compass API", version=__version__)

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------- request ----------


class AnalyzeRequest(_Strict):
    """Phase 0 request shape. Fields are refined against the source plan in Phase 3."""

    byproduct_id: str = Field(examples=["groundnut_cake"])
    application_id: str = Field(examples=["beverage"])
    scale_tonnes_per_day: float | None = Field(default=None, gt=0)
    constraints: list[str] = Field(default_factory=list)
    seed: int = 42


# ---------- response ----------


class VerdictLabel(str, Enum):
    GO = "GO"
    NO_GO = "NO_GO"
    TEST_FIRST = "TEST_FIRST"


class GateState(str, Enum):
    PASS = "PASS"
    TEST_FIRST = "TEST_FIRST"
    FAIL = "FAIL"


class Verdict(_Strict):
    label: VerdictLabel
    p_go: Range
    reasons: list[str]


class Gate(_Strict):
    id: str
    name: str
    state: GateState
    required_test: str | None = None
    what_flips_it: str | None = None


class CompoundDiagnosis(_Strict):
    compound_id: str
    level: Range
    tolerance: Range | None = None
    p_exceed: Range


class Chain(_Strict):
    id: str
    steps: list[str]
    tier: str
    protein_retained: Range
    cost_per_kg_protein: Range
    p_spec: Range


class PeaComparison(_Strict):
    pea_landed_per_kg_protein: Range
    ours_per_kg_protein: Range
    duty_mode: str


class RecommendedTest(_Strict):
    test_id: str
    name: str
    cost_inr: Range
    evsi_inr: Range | None = None


class AnalyzeResponse(_Strict):
    is_stub: bool
    engine_version: str
    dataset_version: str
    verdict: Verdict
    gates: list[Gate]
    diagnosis: list[CompoundDiagnosis]
    chains: list[Chain]
    pea: PeaComparison
    recommended_test: RecommendedTest | None
    disclaimer: str


class Health(_Strict):
    status: str
    engine_version: str
    dataset_version: str


DISCLAIMER = "Decision support only. Not a regulatory approval. " "Confirm FSSAI classification and limits."


def _placeholder(p10: float, p50: float, p90: float, unit: str | None = None) -> Range:
    """A visibly fake range: tagged synthetic, grade D, no sources."""
    return Range(p10=p10, p50=p50, p90=p90, unit=unit, tag=Tag.synthetic, grade=None)


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", engine_version=__version__, dataset_version=DATASET_VERSION)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """STUB. Returns the response shape filled with placeholder values (tag: synthetic)."""
    return AnalyzeResponse(
        is_stub=True,
        engine_version=__version__,
        dataset_version=DATASET_VERSION,
        verdict=Verdict(
            label=VerdictLabel.TEST_FIRST,
            p_go=_placeholder(0.0, 0.5, 1.0, "probability"),
            reasons=["STUB: engine not implemented yet (Phase 3)."],
        ),
        gates=[
            Gate(
                id="G1",
                name="STUB gate",
                state=GateState.TEST_FIRST,
                required_test="STUB",
                what_flips_it="STUB",
            )
        ],
        diagnosis=[
            CompoundDiagnosis(
                compound_id="stub_compound",
                level=_placeholder(0.0, 1.0, 2.0),
                tolerance=None,
                p_exceed=_placeholder(0.0, 0.5, 1.0, "probability"),
            )
        ],
        chains=[
            Chain(
                id="raw_flour",
                steps=[],
                tier="flour",
                protein_retained=_placeholder(0.0, 0.5, 1.0, "fraction"),
                cost_per_kg_protein=_placeholder(0.0, 1.0, 2.0, "INR/kg protein"),
                p_spec=_placeholder(0.0, 0.5, 1.0, "probability"),
            )
        ],
        pea=PeaComparison(
            pea_landed_per_kg_protein=_placeholder(0.0, 1.0, 2.0, "INR/kg protein"),
            ours_per_kg_protein=_placeholder(0.0, 1.0, 2.0, "INR/kg protein"),
            duty_mode="full_stack_44",
        ),
        recommended_test=None,
        disclaimer=DISCLAIMER,
    )

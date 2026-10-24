"""Upcycle Compass HTTP API.

Phase 0: /health and a stub /analyze that returns the §14.2 response shape.
Every number in the stub is a visible placeholder tagged "synthetic" and
`meta.is_stub` is true. The real pipeline replaces the stub in Phase 3.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    Budget,
    Chain,
    DecisionGrade,
    Diagnosis,
    Gate,
    GateState,
    Health,
    Meta,
    Pea,
    Plan,
    Verdict,
    VerdictLabel,
    Voi,
)
from compass import __version__
from compass.data import load_dataset
from compass.models import Range, Tag, Value

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

# Load and validate /data at startup: a bad dataset stops the server with the file and row id.
DATASET = load_dataset()
DATASET_VERSION = DATASET.version

app = FastAPI(title="Upcycle Compass API", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

DISCLAIMER = (
    "Proof of concept. Not a substitute for laboratory validation. "
    "Decision support only. Not a regulatory approval. Confirm FSSAI classification and limits."
)
STUB_NOTE = "STUB: placeholder value (Phase 0). The engine is not implemented yet."


def _v(x: float, unit: str | None = None) -> Value:
    """A visibly fake single value: tagged synthetic, no sources."""
    return Value(value=x, unit=unit, tag=Tag.synthetic)


def _r(unit: str | None = None) -> Range:
    """A visibly fake range: all zeros, tagged synthetic, no sources."""
    return Range(p10=0, p50=0, p90=0, unit=unit, tag=Tag.synthetic)


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", engine_version=__version__, dataset_version=DATASET_VERSION)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """STUB. Validates the §8.3 payload and returns the §14.2 shape filled with placeholders."""
    return AnalyzeResponse(
        meta=Meta(
            seed=req.seed,
            n_draws=0,
            engine_version=__version__,
            dataset_version=DATASET_VERSION,
            is_stub=True,
        ),
        verdict=Verdict(
            label=VerdictLabel.TEST_FIRST,
            grade=DecisionGrade.hypothesis_grade,
            p_go=_v(0, "probability"),
            reasons=[STUB_NOTE],
        ),
        gates=[Gate(id="G0", name="STUB gate", state=GateState.TEST_FIRST, flip_condition=STUB_NOTE)],
        diagnosis=[
            Diagnosis(
                compound="stub_compound", tolerance=None, level=_r(), p_exceed=_v(0, "probability"), rank=1
            )
        ],
        chains=[
            Chain(
                id="raw_flour",
                steps=[],
                tier="flour",
                protein_retained=_r("fraction"),
                protein_pct_final=_r("%"),
                ofi=_r("index 0-10"),
                cost_inr_per_kg_protein=_r("INR/kg protein"),
                kwh_per_kg_protein=_r("kWh/kg protein"),
                l_water_per_kg_protein=_r("L/kg protein"),
                p_spec=_v(0, "probability"),
                e_utility=_v(0, "INR"),
            )
        ],
        pea=Pea(
            duty_mode=req.pea.duty_mode,
            landed_inr_per_kg_protein=_r("INR/kg protein"),
            break_even_base_usd_per_kg=_r("USD/kg"),
            scenarios=[],
        ),
        voi=Voi(evpi=_v(0, "INR/kg protein"), evppi=[], recommended_test=None, note=STUB_NOTE),
        plan=Plan(tests=[], timeline=[], budget_inr=Budget(low=0, high=0, tag=Tag.synthetic)),
        limitations=[STUB_NOTE],
        disclaimer=DISCLAIMER,
    )

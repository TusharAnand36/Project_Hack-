"""Upcycle Compass HTTP API (source plan §14.1).

GET  /health          keep-alive and versions
GET  /presets         the three one-click presets with full payloads
GET  /data/{file}     read-only dataset files (allow-listed) and /data/report
POST /analyze         the decision pipeline; returns the §14.2 result

Phase 6 adds /parse-text, /explain, /update-evidence and /plan.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.schemas import AnalyzeRequest, AnalyzeResponse, Health
from compass import __version__
from compass.analyze import AnalyzeError
from compass.analyze import analyze as run_analysis
from compass.data import FILES, load_dataset, read_raw, report

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
MAX_BODY_BYTES = 64 * 1024  # website plan §9.1

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


@app.middleware("http")
async def limit_body(request: Request, call_next):
    size = request.headers.get("content-length")
    if size is not None and int(size) > MAX_BODY_BYTES:
        return JSONResponse({"detail": f"request body over {MAX_BODY_BYTES // 1024} KB"}, status_code=413)
    return await call_next(request)


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", engine_version=__version__, dataset_version=DATASET_VERSION)


@app.get("/presets")
def presets() -> list[dict[str, Any]]:
    return [p.model_dump() for p in DATASET.presets.values()]


@app.get("/data/{name}")
def data_file(name: str) -> Any:
    if name == "report":
        return report(DATASET)
    if name not in FILES:
        raise HTTPException(404, f"unknown data file; choose one of {list(FILES)} or 'report'")
    return read_raw(name)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return run_analysis(req, DATASET)
    except AnalyzeError as e:
        raise HTTPException(422, str(e)) from e

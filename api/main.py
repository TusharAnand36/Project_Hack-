"""Upcycle Compass HTTP API (source plan §14.1).

GET  /health            keep-alive and versions (and which LLM provider is active)
GET  /presets           the five one-click presets with full payloads
GET  /data/{file}       read-only dataset files (allow-listed) and /data/report
POST /analyze           the decision pipeline; returns the §14.2 result
POST /update-evidence   enter one lab result -> posterior -> before/after (§12.12)
POST /explain           plain-language explanation, numbers verified (LLM or template)
POST /plan              validation plan + next-experiment paragraph
POST /parse-text        free text -> filled form payload; never analyses by itself
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from collections import OrderedDict, defaultdict, deque
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.feedback import FeedbackReceipt, FeedbackRequest, FeedbackStore
from api.llm import service
from api.llm.client import LLMClient
from api.schemas import (
    AiText,
    AnalyzeRequest,
    AnalyzeResponse,
    ExplainRequest,
    Health,
    ParseRequest,
    ParseResponse,
    PlanResponse,
    UpdateEvidenceRequest,
    UpdateEvidenceResponse,
)
from compass import __version__
from compass.analyze import AnalyzeError
from compass.analyze import analyze as run_analysis
from compass.data import FILES, load_dataset, read_raw, report
from compass.learning import update_evidence

logging.basicConfig(level=logging.INFO)
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
MAX_BODY_BYTES = 64 * 1024  # website plan §9.1
AI_RATE_PER_MIN = 10  # website plan §9.1

# Load and validate /data at startup: a bad dataset stops the server with the file and row id.
DATASET = load_dataset()
DATASET_VERSION = DATASET.version
SOURCES = set(DATASET.sources)
LLM = LLMClient()
FEEDBACK = FeedbackStore()

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


_hits: dict[str, deque] = defaultdict(deque)


def _rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "?"
    now = time.monotonic()
    q = _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= AI_RATE_PER_MIN:
        raise HTTPException(429, "too many AI requests; try again in a minute")
    q.append(now)


_cache: OrderedDict[str, AnalyzeResponse] = OrderedDict()


def _analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """Analysis results are deterministic for a request, so cache the last few (sliders, explain)."""
    key = json.dumps(req.model_dump(mode="json"), sort_keys=True)
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    try:
        r = run_analysis(req, DATASET)
    except AnalyzeError as e:
        raise HTTPException(422, str(e)) from e
    _cache[key] = r
    if len(_cache) > 64:
        _cache.popitem(last=False)
    return r


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
    result = _analyze(req).model_copy(deep=True)
    result.meta.generated_at = datetime.now(UTC).isoformat()
    try:
        result.case_id = FEEDBACK.register(req, result)
        result.feedback_context = FEEDBACK.context(req, DATASET_VERSION)
    except (OSError, RuntimeError, sqlite3.Error) as exc:
        result.limitations.append(str(exc))
    return result


@app.post("/feedback", response_model=FeedbackReceipt)
def feedback(body: FeedbackRequest, request: Request) -> FeedbackReceipt:
    _rate_limit(request)
    try:
        return FEEDBACK.save(body)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    except (OSError, RuntimeError, sqlite3.Error) as exc:
        raise HTTPException(503, "Feedback database unavailable; your feedback has not been saved") from exc


@app.post("/update-evidence", response_model=UpdateEvidenceResponse)
def update(body: UpdateEvidenceRequest) -> UpdateEvidenceResponse:
    try:
        result = update_evidence(body, DATASET)
        try:
            FEEDBACK.record_lab(
                json.dumps(
                    {"request": body.model_dump(mode="json"), "result": result.model_dump(mode="json")}
                )
            )
        except (OSError, RuntimeError, sqlite3.Error):
            result.note += " Lab history was not persisted: configure the feedback database."
        return result
    except AnalyzeError as e:
        raise HTTPException(422, str(e)) from e


@app.post("/explain", response_model=AiText)
def explain(body: ExplainRequest, request: Request) -> AiText:
    _rate_limit(request)
    r = _analyze(body.request)
    return AiText(**service.explain(r, body.request, LLM, SOURCES, body.lang))


@app.post("/plan", response_model=PlanResponse)
def plan(body: ExplainRequest, request: Request) -> PlanResponse:
    _rate_limit(request)
    r = _analyze(body.request)
    return PlanResponse(plan=r.plan, paragraph=AiText(**service.plan_paragraph(r, LLM, SOURCES, body.lang)))


@app.post("/parse-text", response_model=ParseResponse)
def parse_text(body: ParseRequest, request: Request) -> ParseResponse:
    _rate_limit(request)
    return ParseResponse(**service.parse_text(body.text, body.base, LLM, DATASET))

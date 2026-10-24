"""API contract. The analysis models live in the engine (`compass.contract`) so the engine
can build its own result; this module re-exports them and adds API-only models.
web/src/api/types.ts is generated from these models (`make types`).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from compass.contract import *  # noqa: F401,F403
from compass.contract import AnalyzeRequest, AnalyzeResponse, Plan  # noqa: F401


class Health(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    engine_version: str
    dataset_version: str


class _Api(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_serialization_defaults_required=True)


class ExplainRequest(_Api):
    request: AnalyzeRequest
    lang: str = "en"


class AiText(_Api):
    text: str
    llm_used: bool
    provider: str
    verifier_passed: bool
    note: str | None = None
    lang: str = "en"
    machine_translated: bool = False  # Hindi text is machine-written: show a badge and an English toggle


class ParseRequest(_Api):
    text: str = Field(min_length=3, max_length=2000)
    base: AnalyzeRequest | None = None
    lang: str = "en"


class ParseResponse(_Api):
    payload: AnalyzeRequest | None
    changed: list[str]
    provider: str
    llm_used: bool
    message: str


class PlanResponse(_Api):
    plan: Plan | None
    paragraph: AiText

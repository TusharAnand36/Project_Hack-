"""API contract. The analysis models live in the engine (`compass.contract`) so the engine
can build its own result; this module re-exports them and adds API-only models.
web/src/api/types.ts is generated from these models (`make types`).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from compass.contract import *  # noqa: F401,F403
from compass.contract import AnalyzeRequest, AnalyzeResponse  # noqa: F401


class Health(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    engine_version: str
    dataset_version: str

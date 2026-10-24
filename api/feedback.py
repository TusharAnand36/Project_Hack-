"""Case-specific feedback in SQLite; no feedback text is exposed to other cases.

Set FEEDBACK_DB_PATH to a persistent mounted volume for a hosted API. SQLite is
the standard-library storage engine; observations never overwrite scientific data.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from compass.contract import AnalyzeRequest, AnalyzeResponse, FeedbackContext


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: str = Field(min_length=32, max_length=36)
    helpful: bool
    outcome: Literal["not_tested", "worked", "failed"] = "not_tested"
    chain_id: str | None = Field(default=None, max_length=200)
    issue: Literal["none", "solubility", "texture", "sensory", "cost", "yield", "safety"] = "none"
    notes: str = Field(default="", max_length=1500)


class FeedbackReceipt(BaseModel):
    saved: bool
    case_id: str
    context: FeedbackContext


class FeedbackStore:
    def __init__(self, path: str | Path | None = None):
        explicit = path or os.getenv("FEEDBACK_DB_PATH")
        if not explicit and os.getenv("APP_ENV") == "public":
            self.path = None  # Do not silently save production feedback on ephemeral storage.
        else:
            self.path = Path(
                explicit or Path(__file__).resolve().parents[1] / ".runtime" / "feedback.sqlite3"
            )

    @contextmanager
    def connect(self):
        if self.path is None:
            raise RuntimeError("Feedback database is not configured on persistent storage")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=10)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY, material TEXT NOT NULL, application TEXT NOT NULL,
                route TEXT NOT NULL, dataset TEXT NOT NULL, created TEXT NOT NULL,
                request_json TEXT NOT NULL, chain_ids TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS feedback (
                case_id TEXT PRIMARY KEY REFERENCES cases(id), helpful INTEGER NOT NULL,
                outcome TEXT NOT NULL, chain_id TEXT, issue TEXT NOT NULL,
                notes TEXT NOT NULL, created TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS cases_scope ON cases(material, application, route, dataset);
            CREATE TABLE IF NOT EXISTS lab_history (
                id TEXT PRIMARY KEY, created TEXT NOT NULL, record_json TEXT NOT NULL
            );
        """
        )
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    @staticmethod
    def scope(req, version):
        return (
            req.byproduct,
            req.application,
            req.process.oil_route
            or (
                "solvent"
                if req.process.solvent_extracted is True
                else "non_solvent" if req.process.solvent_extracted is False else "unknown"
            ),
            version,
        )

    def register(self, req: AnalyzeRequest, result: AnalyzeResponse) -> str:
        case_id = str(uuid.uuid4())
        with self.connect() as db:
            db.execute(
                "INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    case_id,
                    *self.scope(req, result.meta.dataset_version),
                    result.meta.generated_at or datetime.now(UTC).isoformat(),
                    req.model_dump_json(),
                    json.dumps([c.id for c in result.chains]),
                ),
            )
        return case_id

    def _context(self, db, scope) -> FeedbackContext:
        rows = db.execute(
            """SELECT f.helpful, f.outcome, f.issue FROM feedback f JOIN cases c ON c.id=f.case_id
            WHERE c.material=? AND c.application=? AND c.route=? AND c.dataset=?""",
            scope,
        ).fetchall()
        issues = {
            issue: sum(r[2] == issue for r in rows)
            for issue in ("solubility", "texture", "sensory", "cost", "yield", "safety")
        }
        actions = {
            "solubility": "Prioritise a matched solubility and sedimentation assay; similar-case feedback reported a solubility issue.",
            "texture": "Prioritise application-specific texture/expansion tests; similar-case feedback reported texture issues.",
            "sensory": "Run a blinded sensory panel with a defined scoring rubric; similar-case feedback reported sensory issues.",
            "cost": "Obtain an updated supplier/process quote; similar-case feedback reported cost disagreement.",
            "yield": "Measure recovered protein and ingredient mass before costing; similar-case feedback reported yield disagreement.",
            "safety": "Resolve the existing critical safety gates with a qualified reviewer; feedback is not a safety clearance.",
        }
        return FeedbackContext(
            count=len(rows),
            helpful_count=sum(r[0] for r in rows),
            worked_count=sum(r[1] == "worked" for r in rows),
            failed_count=sum(r[1] == "failed" for r in rows),
            observations=[f"{n} case(s) reported {issue}" for issue, n in issues.items() if n],
            next_actions=[actions[issue] for issue, n in issues.items() if n],
        )

    def context(self, req, version):
        with self.connect() as db:
            return self._context(db, self.scope(req, version))

    def save(self, body: FeedbackRequest) -> FeedbackReceipt:
        with self.connect() as db:
            case = db.execute(
                "SELECT material, application, route, dataset, chain_ids FROM cases WHERE id=?",
                (body.case_id,),
            ).fetchone()
            if case is None:
                raise KeyError("Case not found; run a live analysis before submitting feedback")
            if body.chain_id and body.chain_id not in json.loads(case[4]):
                raise ValueError("Selected chain does not belong to this analysed case")
            try:
                db.execute(
                    "INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        body.case_id,
                        int(body.helpful),
                        body.outcome,
                        body.chain_id,
                        body.issue,
                        body.notes,
                        datetime.now(UTC).isoformat(),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("Feedback has already been recorded for this case") from exc
            context = self._context(db, case[:4])
        return FeedbackReceipt(saved=True, case_id=body.case_id, context=context)

    def record_lab(self, record):
        with self.connect() as db:
            db.execute(
                "INSERT INTO lab_history VALUES (?, ?, ?)",
                (str(uuid.uuid4()), datetime.now(UTC).isoformat(), record),
            )

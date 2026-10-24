"""AI features with guardrails (source plan §13): explain, plan paragraph, parse text.

Every LLM output passes schema validation and the number verifier, or falls back to the
deterministic template / rule-based parser. Nothing here can change an engine number.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import ValidationError

from compass.contract import AnalyzeRequest, AnalyzeResponse
from compass.data import Dataset

from . import prompts, rules, template
from .client import LLMClient, LLMUnavailable
from .verify import numbers_in, verify

log = logging.getLogger("compass.llm")


def _facts(r: AnalyzeResponse) -> dict[str, Any]:
    """The compact JSON the LLM may use (and the verifier checks against)."""
    top = r.chains[0] if r.chains else None
    rec = None
    if r.voi and r.voi.recommended_test:
        t = next(x for x in r.voi.tests if x.test_id == r.voi.recommended_test)
        rec = {
            "name": t.name,
            "expected_value_inr_per_decision": round(t.evsi.value),
            "cost_known": t.cost_inr is not None,
        }
    return {
        "verdict": r.verdict.label.value,
        "decision_grade": r.verdict.grade.value,
        "p_go": None if r.verdict.p_go is None else round(r.verdict.p_go.value, 2),
        "p_go_is_upper_bound": bool(r.verdict.p_go_note),
        "reasons": r.verdict.reasons[:4],
        "next_actions": r.verdict.actions[:3],
        "best_chain": (
            None
            if top is None
            else {
                "steps": top.steps,
                "tier": top.tier,
                "p_spec": None if top.p_spec is None else round(top.p_spec.value, 2),
                "protein_pct_p50": (
                    None if top.protein_pct_final is None else round(top.protein_pct_final.p50, 1)
                ),
                "cost_inr_per_kg_protein_p50": (
                    None if top.cost_inr_per_kg_protein is None else round(top.cost_inr_per_kg_protein.p50)
                ),
                "cost_is_lower_bound": not top.cost_complete,
            }
        ),
        "pea_isolate_landed_inr_per_kg_protein_p50": round(r.pea.landed_inr_per_kg_protein.p50),
        "test_to_buy_first": rec,
        "limitations": r.limitations[:3],
    }


def _result(
    text: str, llm_used: bool, provider: str, ok: bool, note: str | None = None, lang: str = "en"
) -> dict[str, Any]:
    return {
        "text": text,
        "llm_used": llm_used,
        "provider": provider,
        "verifier_passed": ok,
        "note": note,
        "lang": lang,
        "machine_translated": lang != "en",
    }


def _verified_completion(
    client: LLMClient,
    endpoint: str,
    task: str,
    facts: dict,
    extra_allowed: set[float],
    sources: set[str],
    lang: str,
) -> dict[str, Any] | None:
    allowed = numbers_in(facts) | extra_allowed
    user = f"{task}\n\n{prompts.data_block('analysis_json', facts)}"
    cache_input = json.dumps(facts, sort_keys=True)
    try:
        c = client.complete(endpoint, prompts.FORMATTER, user, lang, cache_input=cache_input)
        v = verify(c.text, allowed, sources)
        if not v.ok:
            retry = user + "\n\n" + prompts.RETRY.format(bad=", ".join(v.bad_numbers + v.bad_sources))
            c = client.complete(
                endpoint + ":retry", prompts.FORMATTER, retry, lang, cache_input=cache_input + "retry"
            )
            v = verify(c.text, allowed, sources)
        log.info("llm endpoint=%s provider=%s verifier_passed=%s", endpoint, c.provider, v.ok)
        if v.ok:
            return _result(
                c.text,
                True,
                c.provider,
                True,
                "AI-written summary; numbers checked against the engine.",
                lang,
            )
        return None
    except LLMUnavailable:
        return None


def explain(
    r: AnalyzeResponse, req: AnalyzeRequest, client: LLMClient, sources: set[str], lang: str = "en"
) -> dict:
    facts = _facts(r)
    lang = "hi" if lang == "hi" else "en"
    task = prompts.EXPLAIN_HI if lang == "hi" else prompts.EXPLAIN
    got = _verified_completion(client, "explain", task, facts, numbers_in(req.model_dump()), sources, lang)
    if got:
        return got
    note = (
        "AI summary unavailable; template text."
        if not client.enabled
        else "AI text failed the number check; template text shown instead."
    )
    text = template.explain_hi(r) if lang == "hi" else template.explain(r)
    return _result(text, False, "template", True, note, lang)


def plan_paragraph(r: AnalyzeResponse, client: LLMClient, sources: set[str], lang: str = "en") -> dict:
    facts = {
        "plan": r.plan.model_dump(mode="json") if r.plan else None,
        "tests": [t.model_dump(mode="json") for t in (r.voi.tests if r.voi else [])][:4],
    }
    got = _verified_completion(client, "plan", prompts.PLAN, facts, set(), sources, lang)
    return got or _result(
        template.plan_paragraph(r), False, "template", True, "AI paragraph unavailable; template text."
    )


def _set_dotted(d: dict, key: str, value: Any) -> None:
    parts = key.split(".")
    for p in parts[:-1]:
        d = d.setdefault(p, {})
    if parts[0] == "batch" and len(parts) == 2:
        d[parts[-1]] = {"value": value, "tag": "measured"}
    else:
        d[parts[-1]] = value


def _flatten(d: dict, prefix: str = "") -> dict[str, Any]:
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict) and not ("value" in v and "tag" in v):
            out.update(_flatten(v, key + "."))
        else:
            out[key] = v
    return out


ALLOWED_KEYS = {
    "byproduct",
    "application",
    "market",
    "scale_kg_day",
    "raw_price_inr_per_kg",
    "targets.min_protein_pct",
    "targets.max_cost_inr_per_kg_protein",
    "batch.protein_pct",
    "batch.moisture_pct",
    "batch.afb1_ppb",
    "batch.ffa_pct",
    "batch.phytate_pct",
    "process.oil_route",
    "process.stabilised",
    "process.hours_since_milling",
    "constraints.no_solvents",
}


def _llm_fields(client: LLMClient, text: str, ds: Dataset) -> dict[str, Any] | None:
    task = prompts.PARSE.format(byproducts=", ".join(ds.byproducts), applications=", ".join(ds.applications))
    try:
        c = client.complete("parse", prompts.FORMATTER, f"{task}\n\n{prompts.data_block('user_text', text)}")
    except LLMUnavailable:
        return None
    m = re.search(r"\{.*\}", c.text, re.S)
    if not m:
        return None
    try:
        raw = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    flat = _flatten(raw) if isinstance(raw, dict) else {}
    fields = {k: v for k, v in flat.items() if k in ALLOWED_KEYS}
    # numbers must come from the user's text (unit conversions per quintal / tonne allowed)
    said = numbers_in(text)
    said |= {x / 100 for x in said} | {x / 1000 for x in said}
    nums = {k: v for k, v in fields.items() if isinstance(v, int | float) and not isinstance(v, bool)}
    if nums and not verify(" ".join(str(v) for v in nums.values()), said, set()).ok:
        return None
    return fields


def parse_text(text: str, base: AnalyzeRequest | None, client: LLMClient, ds: Dataset) -> dict[str, Any]:
    fields = _llm_fields(client, text, ds) if client.enabled else None
    provider, llm_used = (client.provider, True) if fields is not None else ("rules", False)
    if fields is None:
        fields = rules.parse(text)
    payload: dict[str, Any] = base.model_dump(mode="json", exclude_none=True) if base else {}
    for k, v in fields.items():
        _set_dotted(payload, k, v)
    if "byproduct" not in payload or "application" not in payload:
        return {
            "payload": None,
            "changed": sorted(fields),
            "provider": provider,
            "llm_used": llm_used,
            "message": "Could not read the by-product and target use from this text; please fill the form.",
        }
    try:
        req = AnalyzeRequest.model_validate(payload)
    except ValidationError:
        return {
            "payload": None,
            "changed": [],
            "provider": provider,
            "llm_used": llm_used,
            "message": "Could not read this automatically; please fill the form.",
        }
    if req.byproduct not in ds.byproducts or req.application not in ds.applications:
        return {
            "payload": None,
            "changed": [],
            "provider": provider,
            "llm_used": llm_used,
            "message": "Could not read this automatically; please fill the form.",
        }
    return {
        "payload": req.model_dump(mode="json"),
        "changed": sorted(fields),
        "provider": provider,
        "llm_used": llm_used,
        "message": "Check the highlighted fields, then press Analyse.",
    }

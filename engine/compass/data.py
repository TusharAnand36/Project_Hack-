"""Dataset loader: the only place the engine touches the file system (SR-4).

Reads every JSON file in /data, validates it with Pydantic, checks cross-references
(source ids, compound ids, test ids, ...) and fails loudly with the file and row id.

CLI:
    python -m compass.data --report        counts by tag and grade, preset gaps
    python -m compass.data --todo PATH     regenerate DATA_TODO.md
    python -m compass.data --schema DIR    export JSON Schema for every data file
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from compass.contract import FunctionalProperty
from compass.models import Param, Tag

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FILES = (
    "sources",
    "byproducts",
    "compounds",
    "treatments",
    "applications",
    "costs",
    "safety_gates",
    "lab_tests",
    "presets",
    "functional_evidence",
    "research_evidence",
)


class DataError(ValueError):
    """Raised with a message naming the file and the row id that failed."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------- sources.json


class Source(_Strict):
    id: str
    citation: str
    url: str | None = None
    doi: str | None = None
    kind: Literal["peer_reviewed", "review", "patent", "trade", "regulatory", "user_draft", "web", "plan"]
    accessed: str | None = None
    verified_by_team: bool = False
    notes: str | None = None


class SourcesFile(_Strict):
    dataset_version: str
    sources: list[Source]


# ---------------------------------------------------------------- byproducts.json


class Byproduct(_Strict):
    id: str
    name: str
    role: Literal["core", "control", "stretch"]
    allergen: str | None = None
    oil_routes: list[str] = Field(default_factory=list)
    gates: list[str]
    composition: dict[str, Param]
    compounds: dict[str, Param]
    flavour_baseline: dict[str, Param]
    limiting_amino_acid: str | None = None
    price_inr_per_kg: Param
    notes: str | None = None


class ByproductsFile(_Strict):
    defaults: dict[str, Param]
    reference_species: list[str]  # species that evidence was measured on, not analysable here
    byproducts: list[Byproduct]


# ---------------------------------------------------------------- compounds.json

Role = Literal["safety", "bitter", "beany", "rancid", "colour", "mineral_binding", "digestibility", "toxic"]


class Compound(_Strict):
    id: str
    name: str
    roles: list[Role]
    gate: str | None = None  # compounds handled by a safety gate are not tunable
    unit: str
    relative_to_raw: bool = False  # level expressed as % of the raw material's own value
    flavour_class: str | None = None
    floor: Param | None = None
    assay_test_id: str | None = None
    notes: str | None = None


class CompoundsFile(_Strict):
    flavour_classes: list[str]
    compounds: list[Compound]


# ---------------------------------------------------------------- treatments.json


class Effect(_Strict):
    compound: str
    applies_to: list[str]
    reduction: Param


class SideEffect(_Strict):
    flavour_class: str
    addition: Param


class Resources(_Strict):
    kwh_per_kg: Param
    water_l_per_kg: Param
    chem_inr_per_kg: Param
    labour_h_per_t: Param
    time_h: Param
    capex_ref_inr: Param
    capex_ref_scale_kg_day: Param


class Treatment(_Strict):
    id: str
    name: str
    kind: Literal["process", "fractionation"]
    wet: bool
    uses_solvent: bool
    requires_equipment: list[str]
    effects: list[Effect]
    mass_yield: Param | None = None  # process steps
    protein_retention: Param | None = None  # process steps
    purity: Param | None = None  # fractionation steps
    recovery: Param | None = None  # fractionation steps
    resources: Resources
    side_effects: list[SideEffect] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def _balance_fields(self) -> Treatment:
        if self.kind == "process" and (self.mass_yield is None or self.protein_retention is None):
            raise ValueError("process step needs mass_yield and protein_retention (use a null Param)")
        if self.kind == "fractionation" and (self.purity is None or self.recovery is None):
            raise ValueError("fractionation step needs purity and recovery (use a null Param)")
        return self


Pair = tuple[str, str]


class Precedence(_Strict):
    """Ordering rules from source plan §12.4."""

    max_length: int
    first_for: dict[str, list[str]]  # treatment -> by-products where it must come first
    before: list[Pair]  # (a, b): if both present, a precedes b
    forbidden_sequences: list[Pair]  # (a, b): a may never come before b
    mutually_exclusive: list[Pair]
    max_fractionation: int
    after_fractionation_allowed: dict[str, list[str]]  # treatment -> applications
    not_between: list[tuple[str, str, str]]  # (x, a, b): x never between a and b
    notes: list[str] = Field(default_factory=list)


class TreatmentsFile(_Strict):
    equipment: list[str]
    treatments: list[Treatment]
    precedence: Precedence


# ---------------------------------------------------------------- applications.json


class Application(_Strict):
    id: str
    name: str
    tolerances: dict[str, Param]
    preferred_tiers: list[str]
    inclusion_pct: Param | None = None
    functionality: str
    functionality_tests: list[str]
    notes: str | None = None


class ApplicationsFile(_Strict):
    tiers: list[str]
    tier_thresholds: dict[str, Param]
    applications: list[Application]


# ---------------------------------------------------------------- costs.json


class Scenario(_Strict):
    id: str
    name: str
    set: dict[str, float] = Field(default_factory=dict)  # absolute values
    scale: dict[str, float] = Field(default_factory=dict)  # multipliers
    source_id: str | None = None


class CostsFile(_Strict):
    utilities: dict[str, Param]
    capital: dict[str, Param]
    overheads: dict[str, Param]
    pea: dict[str, Param]
    duty_modes: dict[str, Param]
    scenarios: list[Scenario]
    decision: dict[str, Param]
    engine: dict[str, Param]
    readiness: dict[str, Param]


# ---------------------------------------------------------------- safety_gates.json


class SafetyGate(_Strict):
    id: str
    name: str
    kind: Literal["stop", "flag"]
    applies_to: list[str]  # by-product ids, or ["*"]
    inputs: list[str]
    rule: str
    required_tests: list[str]
    flip_condition: str | None = None
    limits: dict[str, Param] = Field(default_factory=dict)
    params: dict[str, Param] = Field(default_factory=dict)
    allergens: dict[str, str] = Field(default_factory=dict)
    notes: str | None = None


class SafetyGatesFile(_Strict):
    gates: list[SafetyGate]


# ---------------------------------------------------------------- lab_tests.json


class LabTest(_Strict):
    id: str
    name: str
    measures: list[str]
    method: str
    cost_inr: Param
    turnaround_days: Param
    cv: Param
    replicates_min: int = 3
    sensitivity: Param | None = None
    specificity: Param | None = None
    notes: str | None = None


class LabTestsFile(_Strict):
    tests: list[LabTest]


# ---------------------------------------------------------------- presets.json


class Preset(_Strict):
    id: str
    title: str
    story: str
    payload: dict[str, Any]  # validated against the API request model in api/tests


class PresetsFile(_Strict):
    presets: list[Preset]


class FunctionalEvidenceFile(_Strict):
    note: str
    by_material: dict[str, list[FunctionalProperty]]
    application_tests: dict[str, list[str]]


class ResearchEvidenceFile(_Strict):
    source_id: str
    note: str
    records: list[dict[str, str | dict[str, str]]]


# ---------------------------------------------------------------- dataset


@dataclass(frozen=True)
class Dataset:
    version: str
    sources: dict[str, Source]
    byproducts: dict[str, Byproduct]
    byproduct_defaults: dict[str, Param]
    reference_species: list[str]
    compounds: dict[str, Compound]
    flavour_classes: list[str]
    treatments: dict[str, Treatment]
    equipment: list[str]
    precedence: Precedence
    applications: dict[str, Application]
    tiers: list[str]
    tier_thresholds: dict[str, Param]
    costs: CostsFile
    gates: dict[str, SafetyGate]
    lab_tests: dict[str, LabTest]
    presets: dict[str, Preset]
    functional_evidence: FunctionalEvidenceFile


M = TypeVar("M", bound=BaseModel)


def _read(data_dir: Path, name: str) -> dict[str, Any]:
    path = data_dir / f"{name}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise DataError(f"{name}.json: file missing in {data_dir}") from e
    except json.JSONDecodeError as e:
        raise DataError(f"{name}.json: invalid JSON at line {e.lineno} col {e.colno}: {e.msg}") from e


def _validate(model: type[M], raw: dict[str, Any], name: str) -> M:
    """Validate a whole file; on error, name the file and the id of the failing row."""
    try:
        return model.model_validate(raw)
    except ValidationError as e:
        err = e.errors()[0]
        loc = err["loc"]
        row_id = "?"
        node: Any = raw
        for part in loc:  # walk to the deepest list item that has an id
            try:
                node = node[part]
            except (KeyError, IndexError, TypeError):
                break
            if isinstance(node, dict) and "id" in node:
                row_id = node["id"]
        where = ".".join(str(p) for p in loc)
        raise DataError(f"{name}.json: row '{row_id}' at {where}: {err['msg']}") from e


def _index(items: list[M], name: str) -> dict[str, M]:
    out: dict[str, M] = {}
    for it in items:
        key = it.id  # type: ignore[attr-defined]
        if key in out:
            raise DataError(f"{name}.json: duplicate id '{key}'")
        out[key] = it
    return out


def _data_dir(data_dir: Path | str | None = None) -> Path:
    return Path(data_dir or os.getenv("COMPASS_DATA_DIR") or DEFAULT_DATA_DIR)


def read_raw(name: str, data_dir: Path | str | None = None) -> dict[str, Any]:
    """One dataset file as raw JSON (for the provenance UI and the open data pack)."""
    if name not in FILES:
        raise DataError(f"{name}: not a dataset file")
    return _read(_data_dir(data_dir), name)


def load_dataset(data_dir: Path | str | None = None) -> Dataset:
    data_dir = _data_dir(data_dir)
    raw = {n: _read(data_dir, n) for n in FILES}

    src = _validate(SourcesFile, raw["sources"], "sources")
    bp = _validate(ByproductsFile, raw["byproducts"], "byproducts")
    cp = _validate(CompoundsFile, raw["compounds"], "compounds")
    tr = _validate(TreatmentsFile, raw["treatments"], "treatments")
    ap = _validate(ApplicationsFile, raw["applications"], "applications")
    co = _validate(CostsFile, raw["costs"], "costs")
    sg = _validate(SafetyGatesFile, raw["safety_gates"], "safety_gates")
    lt = _validate(LabTestsFile, raw["lab_tests"], "lab_tests")
    pr = _validate(PresetsFile, raw["presets"], "presets")
    fe = _validate(FunctionalEvidenceFile, raw["functional_evidence"], "functional_evidence")
    _validate(ResearchEvidenceFile, raw["research_evidence"], "research_evidence")

    ds = Dataset(
        version=src.dataset_version,
        sources=_index(src.sources, "sources"),
        byproducts=_index(bp.byproducts, "byproducts"),
        byproduct_defaults=bp.defaults,
        reference_species=bp.reference_species,
        compounds=_index(cp.compounds, "compounds"),
        flavour_classes=cp.flavour_classes,
        treatments=_index(tr.treatments, "treatments"),
        equipment=tr.equipment,
        precedence=tr.precedence,
        applications=_index(ap.applications, "applications"),
        tiers=ap.tiers,
        tier_thresholds=ap.tier_thresholds,
        costs=co,
        gates=_index(sg.gates, "safety_gates"),
        lab_tests=_index(lt.tests, "lab_tests"),
        presets=_index(pr.presets, "presets"),
        functional_evidence=fe,
    )
    check_dataset(ds)
    for material, rows in fe.by_material.items():
        if material not in ds.byproducts:
            raise DataError(f"functional_evidence.json: unknown material {material}")
        for row in rows:
            if set(row.source_ids) - ds.sources.keys():
                raise DataError(f"functional_evidence.json: unknown source in {row.id}")
    return ds


# ---------------------------------------------------------------- checks


@dataclass(frozen=True)
class ParamRef:
    file: str
    path: str
    param: Param


def iter_params(ds: Dataset) -> Iterator[ParamRef]:
    """Every Param in the dataset with a stable dotted path (used by checks, report, TODO)."""

    def walk(file: str, prefix: str, obj: Any) -> Iterator[ParamRef]:
        if isinstance(obj, Param):
            yield ParamRef(file, prefix, obj)
        elif isinstance(obj, BaseModel):
            key = getattr(obj, "id", None)
            for name in type(obj).model_fields:
                if name == "id":
                    continue
                sub = f"{prefix}.{name}" if key is None else f"{prefix}.{key}.{name}"
                yield from walk(file, sub.lstrip("."), getattr(obj, name))
        elif isinstance(obj, dict):
            for k, v in obj.items():
                yield from walk(file, f"{prefix}.{k}", v)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                label = getattr(v, "compound", None) or getattr(v, "flavour_class", None)
                tag = getattr(v, "id", None) or (f"{i}:{label}" if label else str(i))
                yield from walk(file, f"{prefix}[{tag}]", v)

    yield from walk("byproducts", "defaults", ds.byproduct_defaults)
    for b in ds.byproducts.values():
        yield from walk("byproducts", "", b)
    for c in ds.compounds.values():
        yield from walk("compounds", "", c)
    for t in ds.treatments.values():
        yield from walk("treatments", "", t)
    yield from walk("applications", "tier_thresholds", ds.tier_thresholds)
    for a in ds.applications.values():
        yield from walk("applications", "", a)
    yield from walk("costs", "", ds.costs)
    for g in ds.gates.values():
        yield from walk("safety_gates", "", g)
    for t in ds.lab_tests.values():
        yield from walk("lab_tests", "", t)


def _bounds(unit: str) -> tuple[float, float] | None:
    u = unit.lower()
    if u.startswith("%"):
        return (0.0, 100.0)
    if u in ("fraction", "probability"):
        return (0.0, 1.0)
    return None


def _numbers(p: Param) -> list[float]:
    if p.value is not None:
        return [p.value]
    if p.dist is not None:
        return [x for x in (p.dist.low, p.dist.mode, p.dist.high) if x is not None]
    return []


def check_dataset(ds: Dataset) -> None:
    errors: list[str] = []
    for ref in iter_params(ds):
        p = ref.param
        if p.source_id is not None and p.source_id not in ds.sources:
            errors.append(f"{ref.file}.json: {ref.path}: unknown source_id '{p.source_id}'")
        if p.tag in (Tag.published, Tag.measured) and p.source_id is None and _numbers(p):
            errors.append(f"{ref.file}.json: {ref.path}: tag '{p.tag.value}' needs a source_id")
        b = _bounds(p.unit)
        if b is not None:
            for x in _numbers(p):
                if not b[0] <= x <= b[1]:
                    errors.append(f"{ref.file}.json: {ref.path}: {x} outside {b} for unit '{p.unit}'")
    for sc in ds.costs.scenarios:
        if sc.source_id is not None and sc.source_id not in ds.sources:
            errors.append(f"costs.json: scenario '{sc.id}': unknown source_id '{sc.source_id}'")

    known_species = set(ds.byproducts) | set(ds.reference_species)
    for b in ds.byproducts.values():
        for c in b.compounds:
            if c not in ds.compounds:
                errors.append(f"byproducts.json: row '{b.id}': unknown compound '{c}'")
        for f in b.flavour_baseline:
            if f not in ds.flavour_classes:
                errors.append(f"byproducts.json: row '{b.id}': unknown flavour class '{f}'")
        for g in b.gates:
            if g not in ds.gates:
                errors.append(f"byproducts.json: row '{b.id}': unknown gate '{g}'")
    for c in ds.compounds.values():
        if c.gate is not None and c.gate not in ds.gates:
            errors.append(f"compounds.json: row '{c.id}': unknown gate '{c.gate}'")
        if c.assay_test_id is not None and c.assay_test_id not in ds.lab_tests:
            errors.append(f"compounds.json: row '{c.id}': unknown test '{c.assay_test_id}'")
        if c.flavour_class is not None and c.flavour_class not in ds.flavour_classes:
            errors.append(f"compounds.json: row '{c.id}': unknown flavour class '{c.flavour_class}'")
    for t in ds.treatments.values():
        for e in t.effects:
            if e.compound not in ds.compounds:
                errors.append(f"treatments.json: row '{t.id}': unknown compound '{e.compound}'")
            for s in e.applies_to:
                if s not in known_species:
                    errors.append(f"treatments.json: row '{t.id}': unknown species '{s}'")
        for s in t.side_effects:
            if s.flavour_class not in ds.flavour_classes:
                errors.append(f"treatments.json: row '{t.id}': unknown flavour class '{s.flavour_class}'")
        for eq in t.requires_equipment:
            if eq not in ds.equipment:
                errors.append(f"treatments.json: row '{t.id}': unknown equipment '{eq}'")
    pc = ds.precedence
    named = (
        list(pc.first_for)
        + [x for pair in pc.before + pc.forbidden_sequences + pc.mutually_exclusive for x in pair]
        + list(pc.after_fractionation_allowed)
        + [x for triple in pc.not_between for x in triple]
    )
    for x in named:
        if x not in ds.treatments:
            errors.append(f"treatments.json: precedence: unknown treatment '{x}'")
    for g in ds.gates.values():
        for t in g.required_tests:
            if t not in ds.lab_tests:
                errors.append(f"safety_gates.json: row '{g.id}': unknown test '{t}'")
        for s in g.applies_to:
            if s != "*" and s not in ds.byproducts:
                errors.append(f"safety_gates.json: row '{g.id}': unknown by-product '{s}'")
    for a in ds.applications.values():
        for tier in a.preferred_tiers:
            if tier not in ds.tiers:
                errors.append(f"applications.json: row '{a.id}': unknown tier '{tier}'")
        for t in a.functionality_tests:
            if t not in ds.lab_tests:
                errors.append(f"applications.json: row '{a.id}': unknown test '{t}'")
    for p in ds.presets.values():
        if p.payload.get("byproduct") not in ds.byproducts:
            errors.append(f"presets.json: row '{p.id}': unknown by-product")
        if p.payload.get("application") not in ds.applications:
            errors.append(f"presets.json: row '{p.id}': unknown application")
    if errors:
        raise DataError("dataset checks failed:\n  " + "\n  ".join(errors))


# ---------------------------------------------------------------- gaps, report, TODO


def is_missing(p: Param) -> bool:
    return p.value is None and p.dist is None


def preset_inputs(ds: Dataset, preset_id: str) -> list[ParamRef]:
    """Every Param the engine needs to analyse a preset (by-product x application)."""
    preset = ds.presets[preset_id]
    bp_id = preset.payload["byproduct"]
    app_id = preset.payload["application"]
    excluded = set(preset.payload.get("constraints", {}).get("exclude_treatments", []))
    bp = ds.byproducts[bp_id]
    gates = {g for g in bp.gates} | {g.id for g in ds.gates.values() if "*" in g.applies_to}
    tests = {t for g in gates for t in ds.gates[g].required_tests}
    tests |= {c.assay_test_id for c in ds.compounds.values() if c.id in bp.compounds and c.assay_test_id}

    def wanted(ref: ParamRef) -> bool:
        path = ref.path
        if ref.file == "byproducts":
            return path.startswith("defaults") or path.startswith(f"{bp_id}.")
        if ref.file == "compounds":
            return path.split(".")[0] in bp.compounds
        if ref.file == "treatments":
            tid = path.split(".")[0]
            if tid in excluded:
                return False
            if ".effects[" in path:
                idx = int(path.split(".effects[")[1].split(":")[0])
                return bp_id in ds.treatments[tid].effects[idx].applies_to
            return True
        if ref.file == "applications":
            return path.startswith("tier_thresholds") or path.startswith(f"{app_id}.")
        if ref.file == "safety_gates":
            return path.split(".")[0] in gates
        if ref.file == "lab_tests":
            return path.split(".")[0] in tests
        return True  # costs

    return [r for r in iter_params(ds) if wanted(r)]


def _priority(ref: ParamRef) -> int:
    p = ref.path
    core_bp = ref.file == "byproducts" and (".composition." in p or ".compounds." in p)
    if ref.file == "safety_gates" or core_bp:
        return 1
    if ref.file == "treatments" and (".purity" in p or ".recovery" in p or ".effects[" in p):
        return 1
    if ref.file in ("treatments", "lab_tests", "compounds") or ".flavour_baseline." in p:
        return 2
    if ref.file == "costs" and not p.startswith("pea"):
        return 2
    return 3


def _where_to_look(ref: ParamRef) -> tuple[str, str]:
    """(best source to check, owner) per the source plan §19 DATA_TODO template."""
    p = ref.path
    if ref.file == "safety_gates":
        return "FSSAI regulation; EU Reg. 1881/2006 as amended; Codex", "Data lead"
    if ref.file == "lab_tests":
        return "NABL lab quotes, NIFTEM", "Story lead"
    if "price_inr_per_kg" in p:
        return "AGMARKNET / data.gov.in mandi prices", "Data lead"
    if ref.file == "costs" and p.startswith("pea"):
        return "Importer quotes, customs data", "Story lead"
    if ref.file == "costs" or ".resources." in p:
        return "Process-engineering papers, supplier quotes", "Engine lead"
    if ".composition." in p:
        return "IFCT 2017 / USDA FoodData Central / literature", "Data lead"
    if ".flavour_baseline." in p or ".side_effects[" in p:
        return "Sensory papers; FooDB / FlavorDB; later own panel", "Data lead"
    if ref.file == "compounds" or ".compounds." in p:
        return "IFCT 2017 / FooDB / papers cited in the review", "Data lead"
    return "Papers cited in the team review", "Data lead"


def _is_config(p: Param) -> bool:
    """Engine settings and unit definitions are decisions, not data to source."""
    return bool(p.notes) and p.notes.startswith(("config:", "definitional:"))


def todo_rows(ds: Dataset) -> list[tuple[int, str, str, str, str, str]]:
    rows = []
    for ref in iter_params(ds):
        p = ref.param
        if _is_config(p):
            continue
        if is_missing(p):
            status = "missing (null)"
        elif p.tag is Tag.assumed:
            status = f"assumed, grade {p.grade.value if p.grade else '?'}"
        elif p.notes and "verify" in p.notes.lower():
            status = f"{p.tag.value}, grade {p.grade.value if p.grade else '?'}: verify"
        else:
            continue
        rows.append((_priority(ref), ref.file, ref.path, p.unit, status, p.notes or ""))
    rows.sort(key=lambda r: (r[0], 0 if r[4].startswith("missing") else 1, r[1], r[2]))
    return rows


def render_todo(ds: Dataset) -> str:
    rows = todo_rows(ds)
    out = [
        "# DATA_TODO",
        "",
        f"Generated by `python -m compass.data --todo DATA_TODO.md` from dataset {ds.version}. "
        "Do not edit by hand; fix the JSON and regenerate.",
        "",
        "Priority 1 = safety gates, composition, compound levels, key treatment effects. "
        "Priority 2 = process resources, yields, lab tests, flavour. Priority 3 = prices and the rest. "
        "Within a priority, missing values come before assumed ones.",
        "",
        f"**{sum(r[4].startswith('missing') for r in rows)} missing, "
        f"{sum(r[4].startswith('assumed') for r in rows)} assumed, "
        f"{sum(r[4].endswith('verify') for r in rows)} to verify.** "
        "Candidate rows awaiting human review are in `data/_staging/` (not used by the engine).",
        "",
    ]
    for pid in ds.presets:
        gaps = [r for r in preset_inputs(ds, pid) if is_missing(r.param)]
        out.append(f"- Preset `{pid}`: {len(gaps)} required inputs still missing.")
    out += [
        "",
        "| Priority | Cell | Needed value | Status | Best source to check | Owner | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    refs = {(r.file, r.path): r for r in iter_params(ds)}
    for pr, f, path, unit, status, notes in rows:
        where, owner = _where_to_look(refs[(f, path)])
        needed = "distribution or value" if status.startswith("missing") else "sourced replacement"
        out.append(
            f"| {pr} | `{f}.json:{path}` | {needed} ({unit}) | {status} | {where} | {owner} "
            f"| {notes.replace('|', '/')} |"
        )
    return "\n".join(out) + "\n"


def report(ds: Dataset) -> dict[str, Any]:
    refs = list(iter_params(ds))
    filled = [r for r in refs if not is_missing(r.param)]
    tags = Counter(r.param.tag.value for r in filled)
    grades = Counter(r.param.grade.value if r.param.grade else "none" for r in filled)
    ab = sum(grades[g] for g in ("A", "B"))
    return {
        "dataset_version": ds.version,
        "params_total": len(refs),
        "params_filled": len(filled),
        "params_missing": len(refs) - len(filled),
        "by_tag": dict(sorted(tags.items())),
        "by_grade": dict(sorted(grades.items())),
        "completeness_ab_share": round(ab / len(filled), 3) if filled else 0.0,
        "sources": len(ds.sources),
        "presets": {
            pid: {
                "required": len(req := preset_inputs(ds, pid)),
                "missing": sorted(f"{r.file}:{r.path}" for r in req if is_missing(r.param)),
            }
            for pid in ds.presets
        },
    }


FILE_MODELS: dict[str, type[BaseModel]] = {
    "sources": SourcesFile,
    "byproducts": ByproductsFile,
    "compounds": CompoundsFile,
    "treatments": TreatmentsFile,
    "applications": ApplicationsFile,
    "costs": CostsFile,
    "safety_gates": SafetyGatesFile,
    "lab_tests": LabTestsFile,
    "presets": PresetsFile,
    "functional_evidence": FunctionalEvidenceFile,
    "research_evidence": ResearchEvidenceFile,
}


def export_schemas(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, model in FILE_MODELS.items():
        schema = model.model_json_schema()
        (out_dir / f"{name}.schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m compass.data", description=__doc__.split("\n\n")[0])
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--report", action="store_true", help="print counts by tag and grade (JSON)")
    ap.add_argument("--todo", metavar="PATH", help="write DATA_TODO.md to PATH")
    ap.add_argument("--full", action="store_true", help="with --report: list every missing preset input")
    ap.add_argument("--schema", metavar="DIR", help="export JSON Schema files to DIR")
    args = ap.parse_args(argv)
    if args.schema:
        export_schemas(Path(args.schema))
        print(f"wrote schemas to {args.schema}")
        return 0
    try:
        ds = load_dataset(args.data_dir)
    except DataError as e:
        print(f"DATA ERROR: {e}", file=sys.stderr)
        return 1
    if args.todo:
        Path(args.todo).write_text(render_todo(ds), encoding="utf-8")
        print(f"wrote {args.todo}")
    if args.report or not args.todo:
        rep = report(ds)
        if not args.full:
            for v in rep["presets"].values():
                v["missing"] = len(v["missing"])
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Analysis contract: the request (source plan §8.3) and the /analyze result (§14.2).

Plain Pydantic models so the engine can build its own result without web imports.
`api/schemas.py` re-exports them; `web/src/api/types.ts` is generated from the API.
Every numeric leaf in a result is a `Value` or a `Range`, so it carries a tag.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from compass.models import Range, Tag, Value


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _pct():
    return Field(default=None, ge=0, le=100)


# ---------------------------------------------------------------- request (§8.3)


class DutyMode(str, Enum):
    """Import duty stack on HS 3504 (sources disagree; source plan §12.8)."""

    full_stack_44 = "full_stack_44"
    full_stack_49 = "full_stack_49"
    bcd_only_igst_credited_22 = "bcd_only_igst_credited_22"


class Targets(_Strict):
    """Targets per kg protein. Null = the application's default tolerance."""

    min_protein_pct: float | None = _pct()
    max_cost_inr_per_kg_protein: float | None = Field(default=None, gt=0)
    max_offflavour_index: float | None = Field(default=None, ge=0, le=10)
    max_phytate_pct: float | None = _pct()


class Constraints(_Strict):
    exclude_treatments: list[str] = Field(default_factory=list)
    no_solvents: bool = False
    equipment: list[str] = Field(
        default_factory=list, description="Available equipment. Empty = not stated (no equipment filter)."
    )
    electricity_inr_per_kwh: float | None = Field(default=None, ge=0)
    water_inr_per_m3: float | None = Field(default=None, ge=0)
    labour_inr_per_h: float | None = Field(default=None, ge=0)


class Measurement(_Strict):
    """A batch measurement on the material as received. Defaults to tag `measured`."""

    value: float = Field(ge=0)
    tag: Tag = Tag.measured
    n_factor: float | None = Field(
        default=None, gt=0, le=7, description="Protein only: N-to-protein factor used"
    )


class PctMeasurement(Measurement):
    value: float = Field(ge=0, le=100)


class Batch(_Strict):
    """Own batch data. Any field left null falls back to a labelled dataset default."""

    protein_pct: PctMeasurement | None = None
    moisture_pct: PctMeasurement | None = None
    fat_pct: PctMeasurement | None = None
    ffa_pct: PctMeasurement | None = None
    ash_pct: PctMeasurement | None = None
    phytate_pct: PctMeasurement | None = Field(default=None, description="% dry basis")
    afb1_ppb: Measurement | None = None
    tia: Measurement | None = None
    inorganic_as_ppm: Measurement | None = None
    cd_ppm: Measurement | None = None


class Process(_Strict):
    oil_route: Literal["cold_pressed", "expeller", "solvent"] | None = None
    hours_since_milling: float | None = Field(default=None, ge=0)
    stabilised: bool | None = None
    storage: Literal["hygienic", "open"] | None = None
    food_grade_supply: bool | None = None
    sorted_food_grade_supply: bool | None = None
    solvent_extracted: bool | None = None
    hexane_cert: bool | None = None


class PeaInputs(_Strict):
    """Imported pea isolate parameters. Null = dataset default (labelled)."""

    base_usd_per_kg: float | None = Field(default=None, gt=0)
    protein_pct: float | None = Field(default=None, gt=0, le=100)
    freight_pct: float | None = Field(default=None, ge=0, le=100)
    duty_mode: DutyMode = DutyMode.full_stack_44
    usd_inr: float | None = Field(default=None, gt=0)


class AnalyzeRequest(_Strict):
    byproduct: str = Field(examples=["groundnut_cake"])
    application: str = Field(examples=["beverage"])
    targets: Targets = Field(default_factory=Targets)
    market: Literal["domestic", "export_EU"] = "domestic"
    scale_kg_day: float | None = Field(default=None, gt=0)
    constraints: Constraints = Field(default_factory=Constraints)
    batch: Batch = Field(default_factory=Batch)
    process: Process = Field(default_factory=Process)
    claims: list[str] = Field(default_factory=list, description='e.g. ["allergen_free"] (gate G6)')
    pea: PeaInputs = Field(default_factory=PeaInputs)
    co_product_credit_inr_per_kg_protein: float | None = Field(default=None, ge=0)
    seed: int | None = None
    n_draws: int | None = Field(default=None, ge=256, le=16384)


# ---------------------------------------------------------------- result (§14.2)


class VerdictLabel(str, Enum):
    GO = "GO"
    NO_GO = "NO-GO"
    TEST_FIRST = "TEST-FIRST"


class DecisionGrade(str, Enum):
    decision_grade = "decision-grade"
    hypothesis_grade = "hypothesis-grade"
    not_viable = "not viable"


class GateState(str, Enum):
    PASS = "PASS"
    TEST_FIRST = "TEST-FIRST"
    FAIL = "FAIL"
    FLAG = "FLAG"  # information only (allergen, regulatory); never blocks


class Meta(_Strict):
    seed: int
    n_draws: int
    engine_version: str
    dataset_version: str
    elapsed_ms: int = 0
    chains_total: int = 0
    chains_shown: int = 0
    chains_capped: bool = False
    is_stub: bool = False


class Verdict(_Strict):
    label: VerdictLabel
    grade: DecisionGrade
    p_go: Value | None
    p_go_note: str | None = None
    reasons: list[str]
    actions: list[str] = Field(default_factory=list)


class Gate(_Strict):
    id: str
    name: str
    kind: Literal["stop", "flag"]
    state: GateState
    reasons: list[str] = Field(default_factory=list)
    measured: Value | None = None
    limit: Value | None = None
    prior_p_fail: Value | None = None
    required_test: str | None = None
    flip_condition: str | None = None
    flags: list[str] = Field(default_factory=list)


class Diagnosis(_Strict):
    compound: str
    name: str
    role: Literal["gate", "tunable"]
    level: Range | None  # null = no data for this compound
    tolerance: Value | None  # null = "no limit available (qualitative)"
    p_exceed: Value | None
    severity: float | None = None
    rank: int
    limiting: bool = False
    note: str | None = None


class Issue(_Strict):
    """A diagnosis chip that is not a compound-removal problem (source plan §12.3)."""

    kind: Literal[
        "protein_density_gap",
        "amino_acid_limitation",
        "functionality",
        "allergen",
        "no_treatment_needed",
        "diagnosis_blocked",
    ]
    message: str
    value: Range | None = None


class Criterion(_Strict):
    id: Literal["protein", "phytate", "tia", "ofi", "cost"]
    target: Value
    evaluated: bool
    p_pass: Value | None = None
    note: str | None = None


class Chain(_Strict):
    id: str
    steps: list[str]
    tier: Literal["flour", "treated_flour", "concentrate", "isolate"]
    rank: int
    protein_retained: Range
    protein_pct_final: Range
    ofi: Range | None = None
    phytate_pct_final: Range | None = None
    tia_pct_raw_final: Range | None = None
    cost_inr_per_kg_protein: Range | None = None
    cost_complete: bool = False
    cost_missing: list[str] = Field(default_factory=list)
    cost_breakdown: dict[str, Range] = Field(default_factory=dict)
    kwh_per_kg_protein: Range | None = None
    l_water_per_kg_protein: Range | None = None
    margin_vs_pea: Range | None = None
    p_margin_positive: Value | None = None
    p_spec: Value
    criteria: list[Criterion] = Field(default_factory=list)
    e_utility: Value | None = None
    transferred: list[str] = Field(default_factory=list)
    no_data_inputs: list[str] = Field(default_factory=list)
    pareto: bool = False
    badges: list[str] = Field(default_factory=list)


class Scenario(_Strict):
    id: str
    name: str
    landed: Range


class Pea(_Strict):
    duty_mode: DutyMode
    inputs: dict[str, Range]
    landed_inr_per_kg_product: Range
    landed_inr_per_kg_protein: Range
    b2b_cross_check_inr_per_kg_protein: Range | None = None
    break_even_base_usd_per_kg: Range | None = None
    break_even_note: str | None = None
    scenarios: list[Scenario]


class Evppi(_Strict):
    input: str
    value: Value
    test_id: str | None
    evsi: Value | None
    cost_inr: Value | None
    roi: Value | None


class Voi(_Strict):
    evpi: Value
    evppi: list[Evppi]
    recommended_test: str | None
    note: str = ""


class PlanTest(_Strict):
    test_id: str
    method: str
    replicates: int
    cost_inr: Range | None
    turnaround_days: Range | None
    acceptance: str


class PlanMonth(_Strict):
    months: str
    work: str
    output: str


class Budget(_Strict):
    low: float | None
    high: float | None
    tag: Tag
    note: str | None = None


class Plan(_Strict):
    tests: list[PlanTest]
    timeline: list[PlanMonth]
    budget_inr: Budget


class AnalyzeResponse(_Strict):
    meta: Meta
    verdict: Verdict
    gates: list[Gate]
    diagnosis: list[Diagnosis]
    issues: list[Issue] = Field(default_factory=list)
    chains: list[Chain]
    pea: Pea
    voi: Voi | None = None  # Phase 5
    plan: Plan | None = None  # Phase 5
    limitations: list[str]
    disclaimer: str

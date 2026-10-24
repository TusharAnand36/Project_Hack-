"""API contract: request (source plan §8.3) and /analyze response (§14.2).

These Pydantic models are the single source of truth for the API shape;
web/src/api/types.ts is generated from them (`make types`).
Every numeric leaf in a response is a `Value` or a `Range`, so it carries a tag.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from compass.models import Range, Tag, Value


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


Pct = Field(default=None, ge=0, le=100)

# ---------------------------------------------------------------- request (§8.3)


class DutyMode(str, Enum):
    """Import duty stack on HS 3504 (sources disagree; source plan §12.8)."""

    full_stack_44 = "full_stack_44"
    full_stack_49 = "full_stack_49"
    bcd_only_igst_credited_22 = "bcd_only_igst_credited_22"


class Targets(_Strict):
    min_protein_pct: float | None = Pct
    max_cost_inr_per_kg_protein: float | None = Field(default=None, gt=0)
    max_offflavour_index: float | None = Field(default=None, ge=0, le=10)
    max_phytate_pct: float | None = Pct  # null = application default


class Constraints(_Strict):
    exclude_treatments: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    electricity_inr_per_kwh: float | None = Field(default=None, ge=0)
    water_inr_per_m3: float | None = Field(default=None, ge=0)
    labour_inr_per_h: float | None = Field(default=None, ge=0)


class Measurement(_Strict):
    """A user-entered batch measurement. Defaults to tag `measured`."""

    value: float = Field(ge=0)
    tag: Tag = Tag.measured
    n_factor: float | None = Field(default=None, gt=0, le=7)  # protein only: N-to-protein factor used


class PctMeasurement(Measurement):
    value: float = Field(ge=0, le=100)


class Batch(_Strict):
    """Own batch data. Any field left null falls back to a labelled dataset default."""

    protein_pct: PctMeasurement | None = None
    moisture_pct: PctMeasurement | None = None
    fat_pct: PctMeasurement | None = None
    ffa_pct: PctMeasurement | None = None
    ash_pct: PctMeasurement | None = None
    phytate_pct: PctMeasurement | None = None
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
    """Imported pea isolate parameters. null = dataset default (labelled)."""

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
    claims: list[str] = Field(default_factory=list)  # e.g. ["allergen_free"] → G6
    pea: PeaInputs = Field(default_factory=PeaInputs)
    co_product_credit_inr_per_kg_protein: float = Field(default=0, ge=0)  # conservative default
    seed: int = 42


# ---------------------------------------------------------------- response (§14.2)


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


class Meta(_Strict):
    seed: int
    n_draws: int
    engine_version: str
    dataset_version: str
    is_stub: bool = False


class Verdict(_Strict):
    label: VerdictLabel
    grade: DecisionGrade
    p_go: Value
    reasons: list[str]


class Gate(_Strict):
    id: str
    name: str
    state: GateState
    prior_p_fail: Value | None = None
    required_test: str | None = None
    flip_condition: str | None = None
    flags: list[str] = Field(default_factory=list)


class Diagnosis(_Strict):
    compound: str
    tolerance: Value | None  # null → "no limit available (qualitative)"
    level: Range
    p_exceed: Value | None
    rank: int


class Chain(_Strict):
    id: str
    steps: list[str]
    tier: Literal["flour", "treated_flour", "concentrate", "isolate"]
    protein_retained: Range
    protein_pct_final: Range
    ofi: Range
    cost_inr_per_kg_protein: Range
    kwh_per_kg_protein: Range
    l_water_per_kg_protein: Range
    p_spec: Value
    e_utility: Value
    transferred: list[str] = Field(default_factory=list)
    pareto: bool = False
    badges: list[str] = Field(default_factory=list)


class Scenario(_Strict):
    name: str
    landed: Range


class Pea(_Strict):
    duty_mode: DutyMode
    landed_inr_per_kg_protein: Range
    break_even_base_usd_per_kg: Range
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
    cost_inr: Range
    turnaround_days: Range
    acceptance: str


class PlanMonth(_Strict):
    months: str
    work: str
    output: str


class Budget(_Strict):
    low: float
    high: float
    tag: Tag


class Plan(_Strict):
    tests: list[PlanTest]
    timeline: list[PlanMonth]
    budget_inr: Budget


class AnalyzeResponse(_Strict):
    meta: Meta
    verdict: Verdict
    gates: list[Gate]
    diagnosis: list[Diagnosis]
    chains: list[Chain]
    pea: Pea
    voi: Voi
    plan: Plan
    limitations: list[str]
    disclaimer: str


class Health(_Strict):
    status: str
    engine_version: str
    dataset_version: str

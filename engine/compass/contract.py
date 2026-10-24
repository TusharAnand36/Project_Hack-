"""Analysis contract: the request (source plan §8.3) and the /analyze result (§14.2).

Plain Pydantic models so the engine can build its own result without web imports.
`api/schemas.py` re-exports them; `web/src/api/types.ts` is generated from the API.
Every numeric leaf in a result is a `Value` or a `Range`, so it carries a tag.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from compass.models import Dist, Grade, Range, Tag, Value


class _Strict(BaseModel):
    # in responses every field is always present, so the generated TS types mark them required
    model_config = ConfigDict(extra="forbid", json_schema_serialization_defaults_required=True)


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
    protein_basis: Literal["as_received", "dry_matter"] = "as_received"
    cost_method: Literal["manual", "benchmark", "product_budget"] = "manual"
    required_discount_pct: float = Field(default=10, ge=0, lt=100)
    product_budget_inr: float | None = Field(default=None, gt=0)
    product_protein_kg: float | None = Field(default=None, gt=0, le=1)
    phytate_target_type: Literal["internal_target", "not_established"] = "not_established"
    sensory_rubric: str | None = Field(default=None, max_length=500)


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
    basis: Literal["as_received", "dry_matter", "not_applicable", "unknown"] = "as_received"
    method: str | None = Field(default=None, max_length=200)
    laboratory: str | None = Field(default=None, max_length=200)
    report_reference: str | None = Field(default=None, max_length=200)
    report_date: str | None = Field(default=None, max_length=32)
    n_factor: float | None = Field(
        default=None, gt=0, le=7, description="Protein only: N-to-protein factor used"
    )


class PctMeasurement(Measurement):
    value: float = Field(ge=0, le=100)


class DryBasisMeasurement(PctMeasurement):
    basis: Literal["dry_matter"] = "dry_matter"


class Batch(_Strict):
    """Own batch data. Any field left null falls back to a labelled dataset default."""

    protein_pct: PctMeasurement | None = None
    moisture_pct: PctMeasurement | None = None
    fat_pct: PctMeasurement | None = None
    ffa_pct: PctMeasurement | None = None
    ash_pct: PctMeasurement | None = None
    phytate_pct: DryBasisMeasurement | None = Field(default=None, description="% dry basis")
    afb1_ppb: Measurement | None = None
    total_aflatoxins_ppb: Measurement | None = None
    hexane_ppm: Measurement | None = None
    pb_ppm: Measurement | None = None
    arsenic_ppm: Measurement | None = None
    hg_ppm: Measurement | None = None
    tia: Measurement | None = None
    inorganic_as_ppm: Measurement | None = None
    cd_ppm: Measurement | None = None
    crude_fibre_pct: PctMeasurement | None = None
    dietary_fibre_pct: PctMeasurement | None = None
    lot_id: str | None = Field(default=None, max_length=100)
    supplier: str | None = Field(default=None, max_length=200)
    origin: str | None = Field(default=None, max_length=200)
    material_form: Literal["cake", "meal", "flour", "concentrate", "isolate", "unknown"] = "unknown"
    dehulled: bool | None = None
    source_reference: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def _aflatoxin_total(self):
        if self.afb1_ppb is not None and self.total_aflatoxins_ppb is not None:
            if self.total_aflatoxins_ppb.value < self.afb1_ppb.value:
                raise ValueError("Total aflatoxins cannot be less than aflatoxin B1")
        return self


class Process(_Strict):
    oil_route: Literal["cold_pressed", "expeller", "solvent", "other"] | None = None
    hours_since_milling: float | None = Field(default=None, ge=0)
    stabilised: bool | None = None
    storage: Literal["hygienic", "open"] | None = None
    food_grade_supply: bool | None = None
    sorted_food_grade_supply: bool | None = None
    solvent_extracted: bool | None = None
    hexane_cert: bool | None = None
    route_reference: str | None = Field(default=None, max_length=300)
    regulatory_review_reference: str | None = Field(default=None, max_length=300)
    functional_validation_reference: str | None = Field(default=None, max_length=300)


class PeaInputs(_Strict):
    """Imported pea isolate parameters. Null = dataset default (labelled)."""

    base_usd_per_kg: float | None = Field(default=None, gt=0)
    protein_pct: float | None = Field(default=None, gt=0, le=100)
    freight_pct: float | None = Field(default=None, ge=0, le=100)
    duty_mode: DutyMode = DutyMode.bcd_only_igst_credited_22
    usd_inr: float | None = Field(default=None, gt=0)


class Evidence(_Strict):
    """A lab result folded into the analysis (source plan §12.12): replaces one input's distribution.

    `input` is an engine input key (e.g. "cmp.phytic_acid", "t.phytase.m", "bp.protein") or "gate.G1"
    for an updated aflatoxin prior. Produced by /update-evidence; the client sends it back unchanged.
    """

    input: str
    value: float | None = None
    dist: Dist | None = None
    p_fail: float | None = Field(default=None, ge=0, le=1)  # gate.G1 only
    unit: str
    tag: Tag = Tag.measured
    grade: Grade | None = Grade.A
    note: str | None = None
    basis: str = "unknown"
    method: str | None = None
    laboratory: str | None = None
    report_reference: str | None = None
    report_date: str | None = None


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
    raw_price_inr_per_kg: float | None = Field(
        default=None,
        gt=0,
        description="By-product price; overrides the dataset default (convert ₹/quintal or ₹/t first)",
    )
    co_product_credit_inr_per_kg_protein: float | None = Field(default=None, ge=0)
    evidence: list[Evidence] = Field(default_factory=list, max_length=20)
    seed: int | None = None
    n_draws: int | None = Field(default=None, ge=256, le=16384)
    price_source: str | None = Field(default=None, max_length=300)
    price_date: str | None = Field(default=None, max_length=32)
    price_boundary: str = Field(default="Supplier price; logistics not supplied", max_length=300)
    original_price: float | None = Field(default=None, gt=0)
    original_price_unit: Literal["per_kg", "per_quintal", "per_tonne"] | None = None


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
    generated_at: str | None = None


class Verdict(_Strict):
    label: VerdictLabel
    grade: DecisionGrade
    p_go: Value | None
    p_go_note: str | None = None
    reasons: list[str]
    actions: list[str] = Field(default_factory=list)


class SafetyCheck(_Strict):
    compound: str
    name: str
    limit: Value
    measured: Value | None = None
    state: GateState
    note: str


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
    checks: list[SafetyCheck] = Field(default_factory=list)


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
    ratio: Range | None = None
    evidence_status: str = "not_available"
    basis: str = "unknown"
    method: str | None = None
    comparison_status: str = "not_estimated"


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
    tier: Literal["flour", "treated_flour", "concentrate", "isolate", "fraction"]
    rank: int
    protein_retained: Range | None
    protein_pct_final: Range | None
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
    p_spec: Value | None
    criteria: list[Criterion] = Field(default_factory=list)
    e_utility: Value | None = None
    transferred: list[str] = Field(default_factory=list)
    no_data_inputs: list[str] = Field(default_factory=list)
    pareto: bool = False
    badges: list[str] = Field(default_factory=list)
    assessment_status: str = "scenario_only"
    assessment_note: str = ""
    economic_status: str = "not_calculable"
    ingredient_yield: Range | None = None
    initial_protein_kg: Range | None = None
    recovered_protein_kg: Range | None = None
    basis: str = "as_received"
    evidence: list[dict] = Field(default_factory=list)


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
    """Expected value of perfectly learning one input (or one test's group of inputs)."""

    input: str
    label: str
    value: Value  # INR per decision
    test_id: str | None
    grade: str | None = None
    note: str | None = None


class TestValue(_Strict):
    test_id: str
    name: str
    inputs: list[str]
    evppi: Value
    evsi: Value
    evsi_is_upper_bound: bool
    cost_inr: Value | None
    roi: Value | None
    worth_it: Literal["yes", "no", "unknown"]


class Utility(_Strict):
    """Decision utility, stated on screen (source plan §12.9)."""

    campaign_kg_cake: Value
    failure_cost_basis: str
    description: str


class Voi(_Strict):
    utility: Utility
    e_now: Value
    evpi: Value
    evppi: list[Evppi]
    tests: list[TestValue]
    recommended_test: str | None
    recommendation: str
    note: str = ""


class ReadinessCheck(_Strict):
    id: str
    label: str
    passed: bool | None  # None = not computable
    value: Value | None = None
    threshold: Value | None = None


class MustDemonstrate(_Strict):
    item: str
    test_id: str | None
    acceptance: str


class Readiness(_Strict):
    grade: DecisionGrade
    checks: list[ReadinessCheck]
    must_demonstrate: list[MustDemonstrate]


class Picks(_Strict):
    best_expected_value: str | None
    safest: str | None
    cheapest_viable: str | None
    ties: list[list[str]] = Field(
        default_factory=list
    )  # pairs "statistically tied" (neither dominates w.p. >= 0.8)


class PlanTest(_Strict):
    test_id: str
    name: str
    method: str
    replicates: int
    sample_plan: str
    cost_inr: Range | None
    turnaround_days: Range | None
    acceptance: str
    why: str


class PlanMonth(_Strict):
    months: str
    work: str
    output: str
    decision_gate: str = "Hold until the required evidence is reviewed. This is a proposed future phase."


class Budget(_Strict):
    low: float | None
    high: float | None
    tag: Tag
    note: str | None = None


class Plan(_Strict):
    tests: list[PlanTest]
    timeline: list[PlanMonth]
    budget_inr: Budget
    pilot_partner: str


class AssessmentDimension(_Strict):
    status: str
    note: str


class FunctionalProperty(_Strict):
    id: str
    name: str
    oilseed_flour: str
    oilseed_isolate: str
    pea_isolate: str
    oilseed_conditions: str
    pea_conditions: str
    comparable: bool = False
    next_test: str
    source_ids: list[str]
    evidence_status: str


class FunctionalComparison(_Strict):
    material: str = ""
    note: str = ""
    properties: list[FunctionalProperty] = Field(default_factory=list)
    application_tests: list[str] = Field(default_factory=list)


class CostTarget(_Strict):
    amount: Value | None = None
    method: str = "manual"
    formula: str = ""
    note: str = ""


class FeedbackContext(_Strict):
    count: int = 0
    helpful_count: int = 0
    worked_count: int = 0
    failed_count: int = 0
    observations: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    note: str = "Unverified case feedback; does not override laboratory evidence or safety gates."


class AnalyzeResponse(_Strict):
    meta: Meta
    verdict: Verdict
    gates: list[Gate]
    diagnosis: list[Diagnosis]
    issues: list[Issue] = Field(default_factory=list)
    chains: list[Chain]
    pea: Pea
    voi: Voi | None = None  # null when utility is not computable (e.g. price missing)
    readiness: Readiness | None = None
    picks: Picks | None = None
    plan: Plan | None = None
    limitations: list[str]
    disclaimer: str
    dimensions: dict[str, AssessmentDimension] = Field(default_factory=dict)
    functional_comparison: FunctionalComparison = Field(default_factory=FunctionalComparison)
    cost_target: CostTarget = Field(default_factory=CostTarget)
    voi_status: str = "not_estimated"
    voi_note: str = ""
    case_id: str | None = None
    feedback_context: FeedbackContext = Field(default_factory=FeedbackContext)


# ---------------------------------------------------------------- learning loop (§12.12)


class Snapshot(_Strict):
    """The parts of a result that a lab result can change (for before/after)."""

    verdict: VerdictLabel
    grade: DecisionGrade
    p_go: Value | None
    best_chain: str | None
    best_p_spec: Value | None
    recommended_test: str | None
    evppi: list[Evppi]


class UpdateEvidenceRequest(_Strict):
    request: AnalyzeRequest
    input: str = Field(description="engine input key from the EVPPI list, or 'gate.G1.u' for aflatoxin")
    value: float | None = Field(default=None, ge=0, description="measured value in the input's unit")
    cv: float | None = Field(
        default=None, gt=0, le=1, description="assay coefficient of variation (fraction)"
    )
    result: Literal["positive", "negative"] | None = Field(
        default=None, description="ELISA screen result (G1)"
    )
    method: str | None = Field(default=None, max_length=200)
    unit: str | None = Field(default=None, max_length=100)
    basis: Literal["as_received", "dry_matter", "not_applicable", "unknown"] = "as_received"
    laboratory: str | None = Field(default=None, max_length=200)
    report_reference: str | None = Field(default=None, max_length=200)
    report_date: str | None = Field(default=None, max_length=32)
    batch_id: str | None = Field(default=None, max_length=100)


class UpdateEvidenceResponse(_Strict):
    input: str
    label: str
    prior: Range | Value | None
    measurement: Value | None
    posterior: Range | Value | None
    note: str
    before: Snapshot
    after: Snapshot
    after_request: AnalyzeRequest

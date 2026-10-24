"""Evidence-aware public assessment, following the final coding-agent handoff.

Scenario Monte Carlo draws are not evidence that a new batch will perform that way.
This layer validates what the available inputs actually permit us to report.
"""

from __future__ import annotations

from compass.contract import (
    AnalyzeRequest,
    AnalyzeResponse,
    AssessmentDimension,
    CostTarget,
    Criterion,
    DecisionGrade,
    FunctionalComparison,
    GateState,
    ReadinessCheck,
    VerdictLabel,
)
from compass.data import Dataset
from compass.models import Grade, Tag
from compass.sampling import Provenance, as_value, summarise

ASSUMPTION = Provenance(Tag.assumed, Grade.D)


def cost_target(req: AnalyzeRequest, result: AnalyzeResponse) -> CostTarget:
    t = req.targets
    amount = t.max_cost_inr_per_kg_protein
    formula = "Manually entered maximum acceptable INR/kg recovered protein"
    note = "Commercial target, not estimated production cost or a legal limit."
    if t.cost_method == "benchmark":
        amount = result.pea.landed_inr_per_kg_protein.p50 * (1 - t.required_discount_pct / 100)
        formula = "Landed benchmark INR/kg isolate ÷ protein mass fraction × (1 − required discount)"
        note += " The benchmark and import charges remain illustrative market assumptions."
    elif t.cost_method == "product_budget":
        amount = (
            t.product_budget_inr / t.product_protein_kg
            if t.product_budget_inr is not None and t.product_protein_kg is not None
            else None
        )
        formula = (
            "Protein-ingredient budget INR/kg finished product ÷ kg protein required/kg finished product"
        )
        if amount is None:
            note += " Enter both the finished-product budget and required protein mass."
    return CostTarget(
        amount=None if amount is None else as_value(amount, ASSUMPTION, "INR/kg protein"),
        method=t.cost_method,
        formula=formula,
        note=note,
    )


def missing_balance(req, ds, steps):
    missing = []
    for tid in steps:
        treatment = ds.treatments[tid]
        fields = (
            {"m": treatment.mass_yield, "rho": treatment.protein_retention}
            if treatment.kind == "process"
            else {"pi": treatment.purity, "rec": treatment.recovery}
        )
        for suffix, param in fields.items():
            measured = any(
                e.input == f"t.{tid}.{suffix}" and (e.value is not None or e.dist is not None)
                for e in req.evidence
            )
            if not measured and (param is None or (param.value is None and param.dist is None)):
                missing.append(f"{tid}: {suffix} not supplied")
    return missing


def assess(req: AnalyzeRequest, ds: Dataset, result: AnalyzeResponse, draws, evaluations) -> AnalyzeResponse:
    result.cost_target = cost_target(req, result)
    result.functional_comparison = FunctionalComparison(
        material=ds.byproducts[req.byproduct].name,
        note=ds.functional_evidence.note,
        properties=ds.functional_evidence.by_material.get(req.byproduct, []),
        application_tests=ds.functional_evidence.application_tests.get(req.application, []),
    )
    measured_protein = req.batch.protein_pct or next(
        (e for e in req.evidence if e.input == "bp.protein" and e.tag is Tag.measured), None
    )
    ppi_reference = req.byproduct == "pea_protein_isolate" and measured_protein is None
    basis_known = ppi_reference or (
        measured_protein is not None
        and (
            measured_protein.basis == "as_received"
            or (measured_protein.basis == "dry_matter" and req.batch.moisture_pct is not None)
        )
    )
    # Use the chain's own step tuple; the legacy id separator is an implementation detail.
    eval_by_steps = {e.seq: e for e in evaluations}
    for chain in result.chains:
        ev = eval_by_steps.get(tuple(chain.steps))
        missing = missing_balance(req, ds, chain.steps)
        chain.basis = "as_received"
        chain.evidence = []
        for tid in chain.steps:
            treatment = ds.treatments[tid]
            effects = [e for e in treatment.effects if req.byproduct in e.applies_to]
            chain.evidence.append(
                {
                    "treatment": tid,
                    "name": treatment.name,
                    "scope": req.byproduct,
                    "required_equipment": treatment.requires_equipment,
                    "verification_status": "review_reported_primary_not_checked",
                    "conditions": [e.reduction.conditions or {} for e in effects],
                    "sources": sorted({e.reduction.source_id for e in effects if e.reduction.source_id}),
                    "notes": treatment.notes
                    or "Batch efficacy, mass balance and resource use need validation.",
                    "reported_effects": [e.reduction.model_dump(mode="json") for e in effects],
                }
            )
        chain.assessment_status = "batch_scenario" if basis_known else "reference_only"
        if measured_protein is not None and measured_protein.tag is Tag.synthetic:
            chain.assessment_status = "synthetic_demo"
        elif measured_protein is not None and measured_protein.tag is Tag.assumed:
            chain.assessment_status = "assumption_scenario"
        chain.assessment_note = "Scenario calculation, not a calibrated batch success probability."
        if missing or not basis_known:
            chain.assessment_status = "research_candidate" if chain.steps else "reference_only"
            chain.assessment_note = "; ".join(
                missing or ["Batch protein and compatible moisture basis not supplied"]
            )
            chain.protein_pct_final = None
            chain.protein_retained = None
            chain.cost_inr_per_kg_protein = None
            chain.cost_breakdown = {}
            chain.cost_complete = False
            chain.no_data_inputs = sorted(set(chain.no_data_inputs + missing))
            chain.cost_missing = sorted(set(chain.cost_missing + ["validated recovery / protein basis"]))
            chain.phytate_pct_final = None
            chain.tia_pct_raw_final = None
            chain.kwh_per_kg_protein = None
            chain.l_water_per_kg_protein = None
        elif ev is not None:
            prov = ev.provs["protein"]
            chain.ingredient_yield = summarise(ev.mass, prov, "kg ingredient/kg starting material")
            p0 = ev.retained * 0 + draws["bp.protein"].values / 100
            if ppi_reference:
                p0 = draws["pea.protein_frac"].values
            elif measured_protein.basis == "dry_matter":
                p0 = p0 * (1 - req.batch.moisture_pct.value / 100)
            chain.initial_protein_kg = summarise(100 * p0, prov, "kg protein/100 kg starting material")
            chain.recovered_protein_kg = summarise(
                100 * p0 * ev.retained, prov, "kg protein/100 kg starting material"
            )
            if req.targets.protein_basis == "dry_matter":
                # A final moisture assay is required for a dry-basis product specification.
                chain.protein_pct_final = None
                chain.assessment_note += " Final product moisture is needed for the dry-matter target."
        if not chain.steps and req.byproduct != "pea_protein_isolate":
            chain.tier = "flour"
            chain.cost_complete = False
            chain.cost_missing = sorted(
                set(chain.cost_missing + ["QA, logistics and preprocessing boundary not supplied"])
            )
        elif chain.protein_pct_final is None and any(
            ds.treatments[t].kind == "fractionation" for t in chain.steps
        ):
            chain.tier = "fraction"
        if not req.targets.sensory_rubric:
            chain.ofi = None
        chain.p_spec = None
        chain.p_margin_positive = None
        chain.e_utility = None
        chain.pareto = False
        chain.badges = [chain.assessment_status]
        if not chain.cost_complete:
            chain.margin_vs_pea = None
        for criterion in chain.criteria:
            criterion.p_pass = None
            criterion.evaluated = False
            criterion.note = "No calibrated probability model for this batch; collect compatible batch and process evidence."
        cap = result.cost_target.amount
        if chain.cost_inr_per_kg_protein is None:
            chain.economic_status = "not_calculable"
        elif not chain.cost_complete:
            chain.economic_status = "partial_cost"
        elif cap is None:
            chain.economic_status = "target_not_supplied"
        elif chain.cost_inr_per_kg_protein.p90 <= cap.value:
            chain.economic_status = "meets_target"
        elif chain.cost_inr_per_kg_protein.p10 > cap.value:
            chain.economic_status = "exceeds_target"
        else:
            chain.economic_status = "sensitive_to_assumptions"
        chain.criteria = [
            criterion
            for criterion in chain.criteria
            if criterion.id not in ("cost", "tia")
            and not (criterion.id == "phytate" and req.targets.phytate_target_type != "internal_target")
            and not (criterion.id == "ofi" and not req.targets.sensory_rubric)
        ]
        if cap is not None:
            chain.criteria.append(
                Criterion(
                    id="cost",
                    target=cap,
                    evaluated=False,
                    note="Economic scenario: "
                    + chain.economic_status
                    + "; separate from technical success probability",
                )
            )
    # Public probabilities and economic VOI need calibrated batch and process evidence.
    result.verdict.p_go = None
    result.verdict.p_go_note = (
        "Not estimated: no calibrated joint probability model is available for this batch and process."
    )
    result.voi = None
    result.voi_status = "not_estimated"
    result.voi_note = "Economic VOI is not estimated: complete process costs, calibrated distributions and actual laboratory quotes are required. Critical safety tests remain necessary independently of economic VOI."
    result.picks = None
    result.pea.break_even_base_usd_per_kg = None
    result.pea.break_even_note = "Not estimated without a complete, comparable production-cost boundary."
    result.limitations = [
        x
        for x in result.limitations
        if "full 0-1" not in x and "Value of information" not in x and "gates without a prior" not in x
    ]
    result.limitations += [
        result.voi_note,
        "Oilseed references are secondary/review-reported unless stated otherwise; their reported ranges are not batch assays.",
        "Cost boundary excludes unsupplied transport/storage, preprocessing, drying/separation, packaging/logistics and waste treatment; partial costs are lower bounds, not full production costs.",
        "Pea price, freight, exchange rate and import charges form an illustrative scenario, not a current verified supplier quote or customs ruling.",
    ]
    batch_fields = {
        "aflatoxin_b1": "afb1_ppb",
        "total_aflatoxins": "total_aflatoxins_ppb",
        "lead": "pb_ppm",
        "cadmium": "cd_ppm",
        "arsenic": "arsenic_ppm",
        "mercury": "hg_ppm",
        "hexane_residue": "hexane_ppm",
        "phytic_acid": "phytate_pct",
        "trypsin_inhibitor": "tia",
    }
    for row in result.diagnosis:
        assay = getattr(req.batch, batch_fields.get(row.compound, ""), None)
        if assay is not None:
            row.basis, row.method = assay.basis, assay.method
            records = [assay.laboratory, assay.report_reference, assay.report_date]
            if any(records):
                row.note = (row.note or "") + "; Report: " + " · ".join(x for x in records if x)
        row.evidence_status = (
            "not_available"
            if row.level is None
            else (
                "batch_measurement"
                if row.level.tag is Tag.measured
                else (
                    "review_reported_primary_not_checked"
                    if row.level.tag is Tag.published
                    else "illustrative_scenario"
                )
            )
        )
        if row.compound == "trypsin_inhibitor":
            row.tolerance = None
            row.p_exceed = None
            row.limiting = False
            row.note = "Assay-specific TIA unit, method and justified threshold are required before comparing activity."
            if row.level is None or row.level.tag is not Tag.measured:
                row.note = (
                    "Illustrative relative activity only: raw = 100% of its own activity, not a measured TIA assay. "
                    + row.note
                )
        if row.compound == "phytic_acid" and req.targets.phytate_target_type != "internal_target":
            row.tolerance = None
            row.p_exceed = None
            row.limiting = False
            row.note = "Threshold not established; enter a justified internal dry-basis target to compare."
        if (
            row.level
            and row.tolerance
            and row.tolerance.value > 0
            and row.level.unit == row.tolerance.unit
            and row.level.tag is Tag.measured
            and (assay is None or assay.basis == ("as_received" if row.role == "gate" else "dry_matter"))
        ):
            ratio = row.level.model_copy(deep=True)
            ratio.p10 /= row.tolerance.value
            ratio.p50 /= row.tolerance.value
            ratio.p90 /= row.tolerance.value
            ratio.unit = "ratio"
            row.ratio = ratio
        elif row.role != "gate":
            row.p_exceed = None
            row.limiting = False
        if row.ratio is not None:
            row.comparison_status = "exceeds_threshold" if row.ratio.p50 > 1 else "within_threshold"
        if row.level is None:
            row.comparison_status = "not_measured"
        elif row.tolerance is None:
            row.comparison_status = "threshold_not_established"
        if row.level is not None and row.level.p10 == row.level.p90:
            row.p_exceed = None  # A point comparison is not a calibrated exceedance probability.
        if assay is not None and row.role == "gate" and assay.basis != "as_received":
            row.p_exceed, row.ratio = None, None
            row.comparison_status = "incompatible_basis"
    for issue in result.issues:
        if issue.kind == "protein_density_gap":
            issue.message = (
                "Reference composition suggests a possible protein-density gap; assay this batch on the target basis before choosing concentration or blending trials."
                if measured_protein is None
                else "Entered protein suggests a possible gap to the target; verify assay basis and evaluate concentration or blending with measured recovery."
            )
        if issue.kind == "amino_acid_limitation":
            issue.message = (
                "Review-reported amino-acid constraint: "
                + (ds.byproducts[req.byproduct].limiting_amino_acid or "not established")
                + ". Verify a batch amino-acid profile and the relevant reference pattern before selecting a complementary blend."
            )
        if issue.kind == "no_treatment_needed":
            issue.kind = "diagnosis_blocked"
            issue.message = "No quantified, applicable anti-nutrient exceedance is established. Missing assay or tolerance data cannot establish that no treatment is needed; validate the batch first."
    stops = [g for g in result.gates if g.kind == "stop" or g.state is GateState.FAIL]
    failures = [g for g in stops if g.state is GateState.FAIL]
    unresolved = [g for g in stops if g.state is not GateState.PASS]
    safety = "failed" if failures else "needs_verification" if unresolved else "documented_for_pilot_review"
    technical = "needs_validation"
    if any(c.protein_pct_final is not None for c in result.chains):
        technical = "scenario_available"
    econ = next((c.economic_status for c in result.chains if c.cost_inr_per_kg_protein), "not_calculable")
    result.dimensions = {
        "safety": AssessmentDimension(
            status=safety, note="; ".join(g.name + ": " + g.state.value for g in stops)
        ),
        "technical": AssessmentDimension(
            status=technical,
            note="Protein concentration, retention and application-specific functionality need batch validation; candidate routes are not industrial predictions.",
        ),
        "economic": AssessmentDimension(
            status=econ,
            note="Only comparable complete costs can establish target compliance. Partial costs cannot establish commercial viability.",
        ),
        "evidence": AssessmentDimension(
            status="hypothesis_grade",
            note="References, assumptions and batch measurements remain separate. Primary-source and pilot validation are outstanding.",
        ),
    }
    result.chains.sort(key=lambda chain: (len(chain.steps), chain.id))
    for chain in result.chains:
        chain.rank = 0  # Evidence-only candidates are not scientifically ranked.
    result.verdict.grade = DecisionGrade.not_viable if failures else DecisionGrade.hypothesis_grade
    result.verdict.label = VerdictLabel.NO_GO if failures else VerdictLabel.TEST_FIRST
    result.verdict.reasons = (
        [f"{g.id} {g.name}: {reason}" for g in failures for reason in g.reasons]
        if failures
        else [f"{g.id} {g.name}: {g.reasons[0] if g.reasons else 'Evidence required'}" for g in unresolved]
    )
    if not failures:
        result.verdict.reasons += [
            "Treatment performance and functional fit require validation; no calibrated probability of success is claimed.",
            "Economics remain separate from safety and technical feasibility.",
        ]
        if econ == "not_calculable":
            raw_price = ds.byproducts[req.byproduct].price_inr_per_kg
            reason = (
                "raw material price missing; "
                if req.raw_price_inr_per_kg is None and raw_price.value is None and raw_price.dist is None
                else ""
            )
            result.verdict.reasons.append(
                "Cost not calculable: "
                + reason
                + "compatible batch protein basis, recovery and full process-cost evidence are required."
            )
    result.verdict.actions = (
        [
            "Hold this lot for qualified safety review and disposition; do not infer that an unsafe food lot is suitable for feed."
        ]
        if failures
        else [
            "Resolve the critical safety and regulatory evidence listed below before food pilot work.",
            "Then test the applicable candidate routes and compare the extracted ingredient with pea isolate using matched functional assays.",
        ]
    )
    target_protein = (
        req.targets.min_protein_pct or ds.applications[req.application].tolerances["min_protein_pct"].value
    )
    pilot_ready = [
        c
        for c in result.chains
        if c.protein_pct_final
        and c.protein_pct_final.p10 >= target_protein
        and c.economic_status == "meets_target"
        and c.cost_complete
    ]
    documented_quote = bool(
        req.price_source
        and req.price_date
        and req.raw_price_inr_per_kg is not None
        and req.price_boundary != "Supplier price; logistics not supplied"
    )
    if (
        not unresolved
        and pilot_ready
        and documented_quote
        and req.process.functional_validation_reference
        and measured_protein is not None
        and measured_protein.tag is Tag.measured
        and measured_protein.method
        and measured_protein.report_reference
    ):
        result.verdict.label = VerdictLabel.GO
        result.verdict.grade = DecisionGrade.decision_grade
        result.verdict.reasons = [
            "Documented safety and category review, current protein specification, declared quote boundary and functional validation support the next pilot step. This is not regulatory approval or validated industrial performance."
        ]
        result.verdict.actions = [
            "Proceed to a controlled pilot within the recorded scope; retain reports and measure mass balance, performance and full process costs."
        ]
        result.dimensions["technical"].status = "documented_for_pilot_review"
        result.dimensions["evidence"].status = "documented_for_pilot_review"
    if result.readiness:
        result.readiness.grade = result.verdict.grade
        result.readiness.checks = [
            ReadinessCheck(
                id="critical_safety",
                label="Critical safety and regulatory evidence documented",
                passed=False if failures else True if not unresolved else None,
            ),
            ReadinessCheck(
                id="batch_basis",
                label="Compatible entered batch protein basis",
                passed=True if measured_protein is not None and basis_known else None,
            ),
            ReadinessCheck(
                id="cost_boundary",
                label="Complete quoted cost within the declared boundary",
                passed=True if documented_quote and pilot_ready else None,
            ),
            ReadinessCheck(
                id="functional_validation",
                label="Application-specific functional validation report",
                passed=True if req.process.functional_validation_reference else None,
            ),
        ]
    if result.plan:
        critical_ids = {t for g in unresolved for t in ds.gates[g.id].required_tests}
        result.plan.tests.sort(key=lambda t: (t.test_id not in critical_ids, t.test_id))
        for test in result.plan.tests:
            if test.test_id in critical_ids:
                test.why = "Critical safety evidence; required independently of economic value-of-information rankings."
    return result

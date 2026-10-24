"""Safety gates G1-G7 (source plan §12.1), evaluated before any treatment.

States: PASS, TEST-FIRST (cannot decide without a measurement), FAIL (hard stop for human
food), FLAG (information only). The overall gate is the worst stop-gate state.
A modelled treatment can never turn FAIL into PASS: gates read only measurements and
supply facts, never treatment effects.
"""

from __future__ import annotations

from dataclasses import dataclass

from compass.contract import AnalyzeRequest, Gate, GateState, SafetyCheck
from compass.data import Byproduct, Dataset, SafetyGate
from compass.models import Grade, Param, Tag
from compass.sampling import Provenance, as_value

_ORDER = {GateState.PASS: 0, GateState.FLAG: 0, GateState.TEST_FIRST: 1, GateState.FAIL: 2}


@dataclass
class GateOutcome:
    gate: Gate
    p_pass: float | None  # probability the gate passes; None = unknown (no prior)
    prior_prov: Provenance | None = None


def _val(p: Param):
    return as_value(p.value, Provenance.of(p), p.unit)


def _measured(m, unit: str):
    return as_value(m.value, Provenance(m.tag, Grade.A if m.tag is Tag.measured else None), unit)


def worst(states: list[GateState]) -> GateState:
    stops = [s for s in states if s is not GateState.FLAG] or [GateState.PASS]
    return max(stops, key=_ORDER.__getitem__)


def _numeric_check(compound, name, measurement, limit: Param) -> SafetyCheck:
    measured = None if measurement is None else _measured(measurement, limit.unit)
    state = (
        GateState.TEST_FIRST
        if measurement is None
        else (GateState.FAIL if measurement.value > limit.value else GateState.PASS)
    )
    note = (
        f"{name} not measured; project threshold ≤ {limit.value:g} {limit.unit}"
        if measured is None
        else f"{name} {measured.value:g} {limit.unit} {'>' if state is GateState.FAIL else '≤'} "
        f"project threshold {limit.value:g} {limit.unit}"
    )
    if measurement is not None and measurement.basis != "as_received":
        state = GateState.TEST_FIRST
        note = f"{name}: assay basis {measurement.basis}; a compatible as-received result is required before threshold comparison"
    if measurement is not None and measurement.tag is not Tag.measured:
        state = GateState.TEST_FIRST
        note = f"{name}: scenario/demo value only; enter a batch assay before clearing this safety gate"
    return SafetyCheck(
        compound=compound, name=name, limit=_val(limit), measured=measured, state=state, note=note
    )


def _checked_gate(g: SafetyGate, checks: list[SafetyCheck]) -> GateOutcome:
    state = worst([c.state for c in checks])
    gate = Gate(
        id=g.id,
        name=g.name,
        kind=g.kind,
        state=state,
        checks=checks,
        reasons=[c.note for c in sorted(checks, key=lambda c: _ORDER[c.state], reverse=True)],
        required_test=" + ".join(g.required_tests),
        flip_condition=g.flip_condition,
    )
    return GateOutcome(gate, {GateState.PASS: 1.0, GateState.FAIL: 0.0}.get(state))


def g1_aflatoxin(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    checks = [
        _numeric_check("aflatoxin_b1", "Aflatoxin B1", req.batch.afb1_ppb, g.limits[req.market]),
        _numeric_check(
            "total_aflatoxins",
            "Total aflatoxins (B1+B2+G1+G2)",
            req.batch.total_aflatoxins_ppb,
            g.limits["total_aflatoxins"],
        ),
    ]
    out = _checked_gate(g, checks)
    out.gate.limit = checks[0].limit
    out.gate.measured = checks[0].measured
    for evidence in req.evidence:
        if evidence.input == "gate.G1" and evidence.note:
            out.gate.reasons.append(evidence.note)
    if out.gate.state is GateState.TEST_FIRST:
        out.gate.reasons.append(
            "Confirm B1 and total aflatoxins by HPLC on a representative composite. "
            "The historical 20-ppb groundnut prior is not calibrated to these project thresholds."
        )
    return out


def g2_rancidity(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    fail = g.limits["ffa_fail_pct"].value
    tf = g.params["ffa_test_first_pct"].value
    window = g.params["unstabilised_window_h"].value
    out = Gate(
        id=g.id,
        name=g.name,
        kind=g.kind,
        state=GateState.TEST_FIRST,
        limit=_val(g.limits["ffa_fail_pct"]),
        required_test=" + ".join(g.required_tests),
        flip_condition=g.flip_condition,
    )
    ffa = req.batch.ffa_pct
    hours, stab = req.process.hours_since_milling, req.process.stabilised
    fresh = stab is True or (hours is not None and hours <= window)
    if ffa is not None:
        out.measured = _measured(ffa, "%")
        if ffa.value > fail:
            out.state = GateState.FAIL
            out.reasons.append(f"FFA {ffa.value:g}% > {fail:g}%: unfit for human food")
            return GateOutcome(out, 0.0)
        if ffa.value > tf:
            out.reasons.append(
                f"FFA {ffa.value:g}% between {tf:g}% and {fail:g}%: stabilise immediately and retest"
            )
            return GateOutcome(out, None)
        if fresh:
            out.state = GateState.PASS
            out.reasons.append(
                f"FFA {ffa.value:g}% ≤ {tf:g}% on {'stabilised' if stab else 'fresh'} material"
            )
            return GateOutcome(out, 1.0)
        out.reasons.append(
            f"FFA {ffa.value:g}% ≤ {tf:g}% but material is not stabilised: retest after stabilising"
        )
        return GateOutcome(out, None)
    if stab is False and hours is not None and hours > window:
        out.state = GateState.FAIL
        out.reasons.append(f"not stabilised and {hours:g} h since milling (> {window:g} h): lipase has acted")
        return GateOutcome(out, 0.0)
    out.reasons.append("FFA not measured: titrate free fatty acids / acid value")
    return GateOutcome(out, None)


def g3_heavy_metals(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    checks = [
        _numeric_check(key, name, measurement, g.limits[key])
        for key, name, measurement in [
            ("lead", "Lead", req.batch.pb_ppm),
            ("cadmium", "Cadmium", req.batch.cd_ppm),
            ("arsenic", "Arsenic (total)", req.batch.arsenic_ppm),
            ("mercury", "Mercury", req.batch.hg_ppm),
        ]
    ]
    return _checked_gate(g, checks)


def g4_solvent(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    check = _numeric_check(
        "hexane_residue", "Hexane residue", req.batch.hexane_ppm, g.limits["hexane_residue"]
    )
    if req.batch.hexane_ppm is None:
        non_solvent = req.process.solvent_extracted is False or (
            req.process.solvent_extracted is None and req.process.oil_route in ("cold_pressed", "expeller")
        )
        if non_solvent and req.process.route_reference:
            check.state = GateState.PASS
            check.note = (
                "Confirmed non-solvent processing: hexane residue testing is not required for this route."
            )
        elif non_solvent:
            check.note = "Non-solvent route declared but supporting process documentation is not supplied; verify the route."
        elif req.process.hexane_cert:
            check.note = "Supplier certificate available: enter its quantitative hexane result to check the 10 mg/kg threshold."
    return _checked_gate(g, [check])


def g5_provenance(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    out = Gate(
        id=g.id,
        name=g.name,
        kind=g.kind,
        state=GateState.TEST_FIRST,
        required_test=" + ".join(g.required_tests),
        flip_condition=g.flip_condition,
    )
    if (
        req.process.food_grade_supply
        and req.process.storage == "hygienic"
        and req.batch.lot_id
        and req.batch.supplier
        and req.batch.source_reference
    ):
        out.state = GateState.PASS
        out.reasons.append("food-grade supply with hygienic storage")
        return GateOutcome(out, 1.0)
    what = []
    if not req.process.food_grade_supply:
        what.append("feed-grade or unknown supply")
    if req.process.storage != "hygienic":
        what.append("open or unknown storage")
    out.reasons.append(
        f"{' and '.join(what) or 'Supplier / lot documentation not supplied'}: document lot traceability, supplier records and handling; a micro panel alone does not prove food-grade provenance."
    )
    return GateOutcome(out, None)


def g6_allergen(g: SafetyGate, req: AnalyzeRequest, bp: Byproduct) -> GateOutcome:
    allergen = g.allergens.get(bp.id, bp.allergen or "allergen")
    out = Gate(id=g.id, name=g.name, kind=g.kind, state=GateState.FLAG)
    out.flags.append(f"major allergen ({allergen}): must be labelled; cannot support an allergen-free claim")
    if "allergen_free" in req.claims:
        out.state = GateState.FAIL
        out.reasons.append("an allergen-free claim is impossible for this by-product")
        return GateOutcome(out, 0.0)
    return GateOutcome(out, 1.0)


def g7_regulatory(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    passed = bool(req.process.regulatory_review_reference)
    out = Gate(id=g.id, name=g.name, kind="stop", state=GateState.PASS if passed else GateState.TEST_FIRST)
    out.reasons.append(
        "Regulatory review reference recorded for pilot review: " + req.process.regulatory_review_reference
        if passed
        else "Regulatory category / intended-use review not documented; obtain a qualified review before pilot food work."
    )
    out.flip_condition = "documented category and intended-use review, including applicable limits and claims"
    return GateOutcome(out, 1.0 if passed else None)


def evaluate(req: AnalyzeRequest, ds: Dataset) -> list[GateOutcome]:
    bp = ds.byproducts[req.byproduct]
    out: list[GateOutcome] = []
    for g in ds.gates.values():
        if "*" not in g.applies_to and bp.id not in g.applies_to:
            continue
        if g.id == "G1":
            out.append(g1_aflatoxin(g, req))
        elif g.id == "G2":
            out.append(g2_rancidity(g, req))
        elif g.id == "G3":
            out.append(g3_heavy_metals(g, req))
        elif g.id == "G4":
            out.append(g4_solvent(g, req))
        elif g.id == "G5":
            out.append(g5_provenance(g, req))
        elif g.id == "G6":
            out.append(g6_allergen(g, req, bp))
        elif g.id == "G7":
            out.append(g7_regulatory(g, req))
    return out

"""Safety gates G1-G7 (source plan §12.1), evaluated before any treatment.

States: PASS, TEST-FIRST (cannot decide without a measurement), FAIL (hard stop for human
food), FLAG (information only). The overall gate is the worst stop-gate state.
A modelled treatment can never turn FAIL into PASS: gates read only measurements and
supply facts, never treatment effects.
"""

from __future__ import annotations

from dataclasses import dataclass

from compass.contract import AnalyzeRequest, Gate, GateState
from compass.data import Byproduct, Dataset, SafetyGate
from compass.models import Grade, Param, Tag
from compass.sampling import Provenance, as_value

_ORDER = {GateState.PASS: 0, GateState.FLAG: 0, GateState.TEST_FIRST: 1, GateState.FAIL: 2}


@dataclass
class GateOutcome:
    gate: Gate
    p_pass: float | None  # probability the gate passes; None = unknown (no prior)
    prior_prov: Provenance | None = None


def odds_to_p(o: float) -> float:
    return o / (1 + o)


def p_to_odds(p: float) -> float:
    return p / (1 - p)


def _val(p: Param):
    return as_value(p.value, Provenance.of(p), p.unit)


def _measured(m, unit: str):
    return as_value(m.value, Provenance(m.tag, Grade.A if m.tag is Tag.measured else None), unit)


def worst(states: list[GateState]) -> GateState:
    stops = [s for s in states if s is not GateState.FLAG] or [GateState.PASS]
    return max(stops, key=_ORDER.__getitem__)


def solvent_extracted(req: AnalyzeRequest, bp: Byproduct) -> tuple[bool, str | None]:
    """True when the material is solvent-extracted. Unknown route = the by-product's first listed route."""
    if req.process.solvent_extracted is not None:
        return req.process.solvent_extracted, None
    route = req.process.oil_route
    note = None
    if route is None and bp.oil_routes:
        route = bp.oil_routes[0]
        note = f"oil-extraction route not given; assumed '{route}'"
    return route == "solvent", note


def g1_aflatoxin(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    lim = g.limits[req.market]
    L = lim.value
    frac = g.params["pass_fraction_of_limit"].value
    out = Gate(
        id=g.id,
        name=g.name,
        kind=g.kind,
        state=GateState.TEST_FIRST,
        limit=_val(lim),
        required_test=" + ".join(g.required_tests),
        flip_condition=g.flip_condition,
    )
    x = req.batch.afb1_ppb
    if x is not None:
        out.measured = _measured(x, "ppb")
        if x.value <= frac * L:
            out.state = GateState.PASS
            out.reasons.append(f"AFB1 {x.value:g} ppb ≤ {frac:g} × limit ({L:g} ppb, {req.market})")
            return GateOutcome(out, 1.0)
        if x.value <= L:
            out.reasons.append(
                f"AFB1 {x.value:g} ppb is within the limit but above {frac:g} × limit: confirm by HPLC"
            )
            return GateOutcome(out, None)
        out.state = GateState.FAIL
        out.reasons.append(
            f"AFB1 {x.value:g} ppb > limit {L:g} ppb ({req.market}): divert to feed or re-source"
        )
        return GateOutcome(out, 0.0)
    prior = g.params["prior_p_fail"]
    p_fail = prior.value
    prov = Provenance.of(prior)
    if req.process.sorted_food_grade_supply:
        mult = g.params["sorted_supply_odds_multiplier"]
        p_fail = odds_to_p(p_to_odds(p_fail) * mult.value)
        prov = Provenance(Tag.assumed, Grade.D, prov.source_ids, None, "derived")
        out.reasons.append(f"sorted food-grade supply: prior odds × {mult.value:g} (assumed)")
    out.prior_p_fail = as_value(p_fail, prov, "probability")
    n_sub = g.params["composite_subsamples_min"].value
    out.reasons.insert(
        0,
        f"AFB1 not measured; prior P(fail) = {p_fail:.2f} [{prov.tag.value}]. "
        f"Test a composite of ≥ {n_sub:g} sub-samples (sampling error often dominates assay error).",
    )
    return GateOutcome(out, 1.0 - p_fail, prov)


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
    out = Gate(
        id=g.id,
        name=g.name,
        kind=g.kind,
        state=GateState.TEST_FIRST,
        required_test=" + ".join(g.required_tests),
        flip_condition=g.flip_condition,
    )
    pairs = [
        ("inorganic_arsenic", req.batch.inorganic_as_ppm, "inorganic As"),
        ("cadmium", req.batch.cd_ppm, "Cd"),
    ]
    states = []
    for key, m, label in pairs:
        lim = g.limits[key]
        if m is None:
            out.reasons.append(f"{label} not measured (ICP-MS)")
            states.append(GateState.TEST_FIRST)
        elif lim.value is None:
            out.reasons.append(
                f"{label} measured at {m.value:g} mg/kg, but no limit is available in the dataset"
            )
            states.append(GateState.TEST_FIRST)
        elif m.value > lim.value:
            out.reasons.append(f"{label} {m.value:g} mg/kg > limit {lim.value:g} mg/kg")
            states.append(GateState.FAIL)
        else:
            states.append(GateState.PASS)
    out.state = worst(states)
    return GateOutcome(out, {GateState.PASS: 1.0, GateState.FAIL: 0.0}.get(out.state))


def g4_solvent(g: SafetyGate, req: AnalyzeRequest, bp: Byproduct) -> GateOutcome:
    out = Gate(
        id=g.id,
        name=g.name,
        kind=g.kind,
        state=GateState.PASS,
        required_test=" + ".join(g.required_tests),
        flip_condition=g.flip_condition,
    )
    solvent, note = solvent_extracted(req, bp)
    if note:
        out.reasons.append(note)
    if not solvent:
        out.reasons.append("not solvent-extracted: no hexane residue risk")
        return GateOutcome(out, 1.0)
    if req.process.hexane_cert:
        out.reasons.append("solvent-extracted with a hexane-residue certificate")
        return GateOutcome(out, 1.0)
    out.state = GateState.TEST_FIRST
    out.reasons.append("solvent-extracted and no hexane-residue certificate")
    return GateOutcome(out, None)


def g5_provenance(g: SafetyGate, req: AnalyzeRequest) -> GateOutcome:
    out = Gate(
        id=g.id,
        name=g.name,
        kind=g.kind,
        state=GateState.TEST_FIRST,
        required_test=" + ".join(g.required_tests),
        flip_condition=g.flip_condition,
    )
    if req.process.food_grade_supply and req.process.storage == "hygienic":
        out.state = GateState.PASS
        out.reasons.append("food-grade supply with hygienic storage")
        return GateOutcome(out, 1.0)
    what = []
    if not req.process.food_grade_supply:
        what.append("feed-grade or unknown supply")
    if req.process.storage != "hygienic":
        what.append("open or unknown storage")
    out.reasons.append(f"{' and '.join(what)}: run a micro panel; re-source if possible")
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


def g7_regulatory(g: SafetyGate) -> GateOutcome:
    out = Gate(id=g.id, name=g.name, kind=g.kind, state=GateState.FLAG)
    out.flags.append(
        "confirm FSSAI classification / approval route for a novel or non-standardised ingredient"
    )
    return GateOutcome(out, 1.0)


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
            out.append(g4_solvent(g, req, bp))
        elif g.id == "G5":
            out.append(g5_provenance(g, req))
        elif g.id == "G6":
            out.append(g6_allergen(g, req, bp))
        elif g.id == "G7":
            out.append(g7_regulatory(g))
    return out

"""Diagnosis: which compounds hold the by-product back (source plan §12.3).

For each tunable compound c with data:
    ER_c = L_c / T_c,  P_exceed_c = P(ER_c > 1),  severity_c = median(log10(max(ER_c, 1)))
    rank by P_exceed_c * (1 + severity_c)
Safety compounds (handled by gates) are always listed first; they are not tunable.
A compound without a tolerance is shown as "no limit available (qualitative)", never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from compass.contract import Diagnosis, Issue
from compass.data import Application, Byproduct, Dataset
from compass.gates import GateOutcome
from compass.models import Param, Tag
from compass.sampling import Provenance, as_value, combine, summarise

# application tolerance key for each tunable compound
TOLERANCE_KEY = {"phytic_acid": "max_phytate_pct_db", "trypsin_inhibitor": "max_tia_pct_raw"}
GATE_COMPOUNDS = {
    "G1": ["aflatoxin_b1"],
    "G2": ["free_fatty_acids"],
    "G3": ["inorganic_arsenic", "cadmium"],
    "G4": ["hexane_residue"],
}


@dataclass
class Level:
    values: np.ndarray | None
    prov: Provenance
    unit: str


def tolerance_param(app: Application, compound: str, override: float | None) -> Param | None:
    if compound == "phytic_acid" and override is not None:
        return Param(value=override, unit="% dry basis", tag=Tag.assumed, notes="user target")
    key = TOLERANCE_KEY.get(compound)
    return app.tolerances.get(key) if key else None


def diagnose(
    ds: Dataset,
    bp: Byproduct,
    app: Application,
    levels: dict[str, Level],
    gate_outcomes: list[GateOutcome],
    phytate_target: float | None,
) -> list[Diagnosis]:
    out: list[Diagnosis] = []
    rank = 0
    for go in gate_outcomes:  # safety compounds first
        if go.gate.checks:
            for check in go.gate.checks:
                rank += 1
                measured = check.measured
                lvl = (
                    None
                    if measured is None
                    else summarise(
                        np.full(3, measured.value), Provenance(measured.tag, measured.grade), measured.unit
                    )
                )
                exceed = (
                    None
                    if measured is None
                    else as_value(
                        float(measured.value > check.limit.value),
                        combine(
                            [
                                Provenance(measured.tag, measured.grade),
                                Provenance(check.limit.tag, check.limit.grade, tuple(check.limit.source_ids)),
                            ]
                        ),
                        "probability",
                    )
                )
                out.append(
                    Diagnosis(
                        compound=check.compound,
                        name=check.name,
                        role="gate",
                        level=lvl,
                        tolerance=check.limit,
                        p_exceed=exceed,
                        rank=rank,
                        note=f"{check.state.value}: {check.note}; not tunable by treatment",
                    )
                )
            continue
        for cid in GATE_COMPOUNDS.get(go.gate.id, []):
            rank += 1
            c = ds.compounds[cid]
            measured = go.gate.measured
            lvl = None
            if measured is not None:
                lvl = summarise(
                    np.full(3, measured.value), Provenance(measured.tag, measured.grade), measured.unit
                )
            note = f"gate {go.gate.id}: {go.gate.state.value}; not tunable by treatment"
            out.append(
                Diagnosis(
                    compound=cid,
                    name=c.name,
                    role="gate",
                    level=lvl,
                    tolerance=go.gate.limit,
                    p_exceed=go.gate.prior_p_fail,
                    rank=rank,
                    note=note,
                )
            )
    scored: list[tuple[float, Diagnosis]] = []
    for cid in bp.compounds:
        c = ds.compounds[cid]
        lv = levels.get(cid)
        tol = tolerance_param(app, cid, phytate_target)
        d = Diagnosis(
            compound=cid, name=c.name, role="tunable", level=None, tolerance=None, p_exceed=None, rank=0
        )
        if lv is None or lv.values is None:
            d.note = "no data for this compound in the dataset or the batch"
            scored.append((-1.0, d))
            continue
        d.level = summarise(lv.values, lv.prov, lv.unit)
        if tol is None or tol.value is None or tol.value <= 0:
            d.note = "no limit available (qualitative)"
            scored.append((-0.5, d))
            continue
        er = lv.values / tol.value
        p = float(np.mean(er > 1.0))
        sev = float(np.median(np.log10(np.maximum(er, 1.0))))
        prov = combine([lv.prov, Provenance.of(tol)])
        d.tolerance = as_value(tol.value, Provenance.of(tol), tol.unit)
        d.p_exceed = as_value(p, prov, "probability")
        d.severity = round(sev, 3)
        scored.append((p * (1 + sev), d))
    scored.sort(key=lambda x: -x[0])
    first = True
    for score, d in scored:
        rank += 1
        d.rank = rank
        if first and score > 0:
            d.limiting, first = True, False
        out.append(d)
    return out


def issues(
    bp: Byproduct,
    app: Application,
    diagnosis: list[Diagnosis],
    base_protein_pct: np.ndarray,
    base_prov: Provenance,
    required_protein_pct: float,
    required_prov: Provenance,
    functionality_tests: list[str],
) -> list[Issue]:
    out: list[Issue] = []
    gap = required_protein_pct - base_protein_pct
    if np.median(gap) > 0:
        out.append(
            Issue(
                kind="protein_density_gap",
                message=f"Base protein is about {np.median(base_protein_pct):.0f}% against {required_protein_pct:g}% "
                "required: flour cannot reach it; a protein concentration (fractionation) step is needed.",
                value=summarise(gap, combine([base_prov, required_prov]), "percentage points"),
            )
        )
    if bp.limiting_amino_acid:
        out.append(
            Issue(
                kind="amino_acid_limitation",
                message=f"Limited by {bp.limiting_amino_acid}: blend, not treatment "
                "(processing cannot add an amino acid).",
            )
        )
    out.append(
        Issue(
            kind="functionality",
            message=f"Functionality is not modelled ({app.functionality}) Validate with: "
            f"{', '.join(functionality_tests) or 'functional tests'}.",
        )
    )
    if bp.allergen:
        out.append(
            Issue(
                kind="allergen", message=f"Major allergen ({bp.allergen}): label it; no allergen-free claim."
            )
        )
    tunable = [d for d in diagnosis if d.role == "tunable"]
    with_data = [d for d in tunable if d.level is not None]
    if tunable and not with_data:
        names = ", ".join(d.name.lower() for d in tunable)
        out.append(
            Issue(
                kind="diagnosis_blocked",
                message=f"Cannot diagnose anti-nutrients: no data for {names}. Measure them first; "
                "no detox claim is made either way.",
            )
        )
    elif not any(d.limiting for d in tunable):
        if not tunable:
            msg = (
                "No anti-nutrient treatment needed: the dataset lists no anti-nutrient that exceeds a tolerance "
                "for this by-product (none are listed; confirm with literature). The constraints are "
                "allergen, price and protein level."
            )
        else:
            msg = "No anti-nutrient with data exceeds its tolerance: no detox treatment needed on current evidence."
        out.append(Issue(kind="no_treatment_needed", message=msg))
    return out

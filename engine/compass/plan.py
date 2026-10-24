"""Validation plan and 6-month pilot (source plan §12.13): rule-based, not LLM.

Tests come from the outstanding gate tests and the top value-of-information tests. Costs and
turnaround come from lab_tests.json; while those are missing the budget is "not computable"
rather than guessed. The timeline is the plan's template.
"""

from __future__ import annotations

import numpy as np

from compass.contract import Budget, Plan, PlanMonth, PlanTest
from compass.data import Dataset, LabTest
from compass.models import Param, Tag
from compass.sampling import Provenance, summarise

TIMELINE = [
    (
        "0–1",
        "Source 3–5 batches from food-grade mills; composite sampling; gate tests",
        "Gate decisions on real lots",
    ),
    (
        "1–3",
        "Bench trials of up to two eligible, evidence-supported candidates; assay before and after",
        "Transferred evidence replaced by measured (grade A)",
    ),
    (
        "3–4",
        "Sensory panel (triangle test + scaling); solubility, emulsification, gelation",
        "Off-flavour index and functionality flags calibrated",
    ),
    (
        "4–5",
        "Pilot-scale run (≈ 10 t cake decision volume) with a contract processor or institute pilot plant; "
        "micro and contaminants",
        "Real yield, energy and water",
    ),
    (
        "5–6",
        "Re-run the engine with measured data; customer sample trials; regulatory classification check",
        "Updated ₹/kg protein vs pea; go / no-go for a plant",
    ),
]
PARTNER = (
    "A feed-grade mill moving one line to food grade, with an accredited (NABL) testing lab and an "
    "incubator or institute pilot plant. Name institutions only after the team has spoken to them."
)


def _range(p: Param, unit: str):
    if p.value is None and p.dist is None:
        return None
    lo = p.value if p.value is not None else p.dist.low
    hi = p.value if p.value is not None else p.dist.high
    mid = p.value if p.value is not None else (p.dist.mode if p.dist.mode is not None else (lo + hi) / 2)
    return summarise(np.array([lo, mid, hi]), Provenance.of(p), unit)


def acceptance(
    test: LabTest, targets: dict, market: str, limit: float | None, functionality: str, gates: dict
) -> str:
    t = test.id
    if t.startswith("afb1"):
        total = gates["G1"].limits["total_aflatoxins"].value
        return f"AFB1 ≤ {limit:g} µg/kg AND total B1+B2+G1+G2 ≤ {total:g} µg/kg on a representative composite (project thresholds)"
    if t == "ffa_titration":
        return "FFA ≤ 3% on stabilised material"
    if t == "peroxide_value":
        return "Peroxide value within the product spec (limit to be set with the buyer)"
    if t == "icp_ms_metals":
        return (
            "; ".join(f"{key} ≤ {p.value:g} {p.unit}" for key, p in gates["G3"].limits.items())
            + " (project thresholds; total arsenic)"
        )
    if t == "hexane_residue_gchs":
        p = gates["G4"].limits["hexane_residue"]
        return f"Quantitative hexane residue ≤ {p.value:g} {p.unit}, or confirmed non-solvent processing (project threshold)"
    if t == "micro_panel":
        return "Total plate count and yeast & mould within spec; Salmonella absent"
    if t == "phytate_assay" and targets.get("phytate"):
        return f"Phytate ≤ {targets['phytate'][0]:g}% dry basis in the product (and baseline measured)"
    if t == "tia_assay" and targets.get("tia"):
        return f"Trypsin inhibitor ≤ {targets['tia'][0]:g}% of raw activity after the chain"
    if t == "proximate_kjeldahl" and targets.get("protein"):
        return f"Protein ≥ {targets['protein'][0]:g}% in the product; record mass yield and protein retention"
    if t == "sensory_panel" and targets.get("ofi"):
        return f"Off-flavour index ≤ {targets['ofi'][0]:g} on a trained panel (triangle + scaling)"
    if t == "functionality_panel":
        return f"Fit for use: {functionality}"
    return "Measured before and after the chain (no tolerance in the dataset yet)"


def build(
    ds: Dataset,
    ordered_tests: list[tuple[str, str]],  # (test_id, why), most valuable first
    targets: dict,
    market: str,
    g1_limit: float | None,
    functionality: str,
) -> Plan:
    tests: list[PlanTest] = []
    seen: set[str] = set()
    lows, highs = [], []
    budget_known = True
    for tid, why in ordered_tests:
        if tid in seen or tid not in ds.lab_tests:
            continue
        seen.add(tid)
        lt = ds.lab_tests[tid]
        cost = _range(lt.cost_inr, "INR")
        if cost is None:
            budget_known = False
        else:
            lows.append(cost.p10 * lt.replicates_min)
            highs.append(cost.p90 * lt.replicates_min)
        sample = (
            "Composite of ≥ 10 sub-samples from the lot (hot kernels: sampling error dominates)"
            if tid.startswith("afb1")
            else f"{lt.replicates_min} replicates on a representative composite"
        )
        tests.append(
            PlanTest(
                test_id=tid,
                name=lt.name,
                method=lt.method,
                replicates=lt.replicates_min,
                sample_plan=sample,
                cost_inr=cost,
                turnaround_days=_range(lt.turnaround_days, "days"),
                acceptance=acceptance(lt, targets, market, g1_limit, functionality, ds.gates),
                why=why,
            )
        )
    budget = (
        Budget(
            low=sum(lows),
            high=sum(highs),
            tag=Tag.assumed,
            note="tests only; pilot fees and staff not included",
        )
        if budget_known and tests
        else Budget(
            low=None,
            high=None,
            tag=Tag.assumed,
            note="not computable: lab test costs are missing in lab_tests.json (see DATA_TODO); get NABL lab quotes",
        )
    )
    return Plan(
        tests=tests,
        timeline=[
            PlanMonth(months=m, work=w, output=o, decision_gate=gate)
            for (m, w, o), gate in zip(
                TIMELINE,
                [
                    "Proceed only after lot identity, process records and required safety evidence are accepted.",
                    "Continue only if an eligible candidate improves the measured constraint and reconciles protein/mass balance.",
                    "Hold until application-specific functionality and sensory acceptance are demonstrated.",
                    "Continue scale-up only if the pilot meets the product specification and records yields, losses, utilities and costs.",
                    "Approve further development only after customer, regulatory and comparable economic review; otherwise hold or stop.",
                ],
                strict=True,
            )
        ],
        budget_inr=budget,
        pilot_partner=PARTNER,
    )

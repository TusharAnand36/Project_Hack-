"""Monte Carlo evaluation of treatment chains (source plan §12.9, first pass).

Every chain is evaluated on the same draws (common random numbers), so chains can be
compared draw by draw. Per draw and chain: final protein %, protein retained, compound
levels, off-flavour index, cost per kg protein, kWh and litres per kg protein, margin vs
pea isolate, and the joint spec indicator. P(spec) is the mean of the joint indicator,
not the product of marginals. Value of information is added in Phase 5.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from compass import cost as costm
from compass import effects as fx
from compass import flavour
from compass import pea as peam
from compass.data import Byproduct, Dataset
from compass.sampling import Provenance, Sampled, combine

Arr = np.ndarray


@dataclass
class Context:
    ds: Dataset
    bp: Byproduct
    application: str
    draws: dict[str, Sampled]
    n: int
    p0: Arr  # true protein fraction of the raw cake, dry basis
    p0_prov: Provenance
    compounds: dict[str, tuple[Arr, Provenance, bool]]  # id -> (level, prov, relative_to_raw)
    econ: costm.Economics
    econ_prov: list[Provenance]
    pea: peam.PeaInputs
    pea_prov: Provenance
    credit: float


@dataclass
class Criterion:
    id: str
    target: float
    unit: str
    target_prov: Provenance
    evaluated: bool
    passed: Arr | None = None
    note: str | None = None


@dataclass
class ChainEval:
    seq: tuple[str, ...]
    protein_pct: Arr
    retained: Arr
    mass: Arr
    compound_final: dict[str, Arr]
    ofi: Arr | None
    cost: costm.CostResult
    margin: Arr | None
    spec: Arr
    criteria: list[Criterion]
    provs: dict[str, Provenance]
    transferred: list[str] = field(default_factory=list)
    no_data: list[str] = field(default_factory=list)


def _get(ctx: Context, key: str) -> Sampled:
    return ctx.draws[key]


def _note_no_data(ev_no_data: list[str], s: Sampled, label: str) -> None:
    if s.prov.status == "no_data" and label not in ev_no_data:
        ev_no_data.append(label)


def evaluate(
    seq: tuple[str, ...], ctx: Context, targets: dict[str, tuple[float, str, Provenance] | None]
) -> ChainEval:
    ds, bp, n = ctx.ds, ctx.bp, ctx.n
    b0 = fx.start(n, ctx.p0)
    b = b0
    used: list[Provenance] = [ctx.p0_prov]
    transferred: list[str] = []
    no_data: list[str] = []
    comp_mass = {
        c: v.copy() for c, (v, _, rel) in ctx.compounds.items()
    }  # % of dry raw (or % of raw activity)
    comp_prov = {c: [p] for c, (_, p, _) in ctx.compounds.items()}
    flav_steps: list[tuple[dict[str, Arr], dict[str, Arr | None]]] = []
    resources: list[costm.StepResources] = []

    for tid in seq:
        t = ds.treatments[tid]
        mass_in = b.mass
        # compound effects of this step on this by-product
        red_by_class: dict[str, Arr] = {}
        for i, e in enumerate(t.effects):
            if bp.id not in e.applies_to or e.compound not in comp_mass:
                continue
            s = _get(ctx, f"t.{tid}.e{i}")
            _note_no_data(no_data, s, f"{tid}: {e.compound} reduction")
            r = s.values
            if r is None:
                # An unknown reduction makes the residual unknown, not a random 0–100% removal.
                del comp_mass[e.compound]
                continue
            floor_s = ctx.draws.get(f"floor.{e.compound}")
            floor = 0.0 if floor_s is None or floor_s.values is None else floor_s.values
            rel = ctx.compounds[e.compound][2]
            if rel:
                comp_mass[e.compound] = fx.reduce_compound(comp_mass[e.compound], r, floor)
            else:  # track mass per kg raw; the floor is a concentration in the product
                comp_mass[e.compound] = fx.reduce_compound(comp_mass[e.compound], r, floor * mass_in)
            comp_prov[e.compound].append(s.prov)
            if e.reduction.alpha is not None and e.reduction.alpha < 0.7:
                src = (e.reduction.conditions or {}).get("measured_on", "another material")
                transferred.append(f"{tid}: {e.compound} from {src}, α={e.reduction.alpha:g}")
            cls = ds.compounds[e.compound].flavour_class
            if cls:
                red_by_class[cls] = 1 - (1 - red_by_class.get(cls, 0.0)) * (1 - r)
        adds: dict[str, Arr | None] = {}
        for i, se in enumerate(t.side_effects):
            s = _get(ctx, f"t.{tid}.se{i}")
            adds[se.flavour_class] = s.values
        flav_steps.append((red_by_class, adds))
        # mass and protein balance
        if t.kind == "process":
            sm, sr = _get(ctx, f"t.{tid}.m"), _get(ctx, f"t.{tid}.rho")
            _note_no_data(no_data, sm, f"{tid}: mass yield")
            _note_no_data(no_data, sr, f"{tid}: protein retention")
            m = sm.values
            if sm.prov.status == "no_data" and sr.prov.status == "no_data":
                # no data at all: a non-fractionation step keeps protein % as-is (§7.3, "treated
                # flour ~ protein as-is"); only the loss is uncertain, so mass yield = retention
                m = sr.values
            b = fx.step(b, "process", mass_yield=m, protein_retention=sr.values)
            used += [sm.prov, sr.prov]
        else:
            sp, sc = _get(ctx, f"t.{tid}.pi"), _get(ctx, f"t.{tid}.rec")
            b = fx.step(b, "fractionation", purity=sp.values, recovery=sc.values)
            used += [sp.prov, sc.prov]
            if t.purity.alpha is not None and t.purity.alpha < 0.7:
                transferred.append(
                    f"{tid}: purity/recovery from {(t.purity.conditions or {}).get('measured_on')}, "
                    f"α={t.purity.alpha:g}"
                )
        res = {
            f: _get(ctx, f"t.{tid}.res.{f}").values
            for f in (
                "kwh_per_kg",
                "water_l_per_kg",
                "chem_inr_per_kg",
                "labour_h_per_t",
                "capex_ref_inr",
                "capex_ref_scale_kg_day",
            )
        }
        resources.append(costm.StepResources(tid, mass_in, **res))

    protein_pct = b.protein_frac * 100
    retained = fx.retained(b, b0)
    finals: dict[str, Arr] = {}
    for c, m in comp_mass.items():
        finals[c] = m if ctx.compounds[c][2] else m / b.mass  # concentration in product (% dry basis)

    base_flav = {c: (_get(ctx, f"flav.{c}").values) for c in bp.flavour_baseline}
    ofi = flavour.ofi(base_flav, flav_steps)

    price = _get(ctx, "bp.price")
    c = costm.chain_cost(price.values, resources, b.mass, b.protein, ctx.econ, ctx.credit)
    if bp.id == "pea_protein_isolate" and not seq:
        # The purchase price already covers the isolate; do not add cake-processing overhead.
        per_protein = price.values / b.protein
        c = costm.CostResult(price.values, price.values, per_protein, None, None, {"raw": per_protein})
    margin = None if price.values is None else peam.margin_vs_pea(ctx.pea, c.per_kg_protein)

    prov_protein = combine(used)
    provs = {"protein": prov_protein, "cost": combine(used + [price.prov] + ctx.econ_prov)}
    if bp.id == "pea_protein_isolate":
        provs["cost"] = combine(used + [price.prov])
    if margin is not None:
        provs["margin"] = combine([provs["cost"], ctx.pea_prov])
    for comp, ps in comp_prov.items():
        provs[comp] = combine(ps + used)

    # joint spec
    crit: list[Criterion] = []
    spec = np.ones(n, dtype=bool)

    def add(cid: str, ok: Arr | None, note: str | None = None) -> None:
        nonlocal spec
        t = targets.get(cid)
        if t is None:
            return
        val, unit, tprov = t
        if ok is None:
            crit.append(Criterion(cid, val, unit, tprov, False, None, note))
            return
        crit.append(Criterion(cid, val, unit, tprov, True, ok, note))
        if cid != "cost":
            spec &= ok

    add("protein", protein_pct >= targets["protein"][0] if targets.get("protein") else None)
    if targets.get("phytate"):
        ph = finals.get("phytic_acid")
        add(
            "phytate",
            None if ph is None else ph <= targets["phytate"][0],
            None if ph is not None else "no phytate data for this by-product",
        )
    if targets.get("tia") and "trypsin_inhibitor" in finals:
        add("tia", finals["trypsin_inhibitor"] <= targets["tia"][0])
    if targets.get("ofi"):
        add(
            "ofi",
            None if ofi is None else ofi <= targets["ofi"][0],
            None if ofi is not None else "off-flavour index not computable: no sensory baseline data",
        )
    if targets.get("cost"):
        if price.values is None:
            add("cost", None, "raw material price missing")
        else:
            note = None if c.complete else "cost is a lower bound (missing components), so this is optimistic"
            add("cost", c.per_kg_protein <= targets["cost"][0], note)

    return ChainEval(
        seq, protein_pct, retained, b.mass, finals, ofi, c, margin, spec, crit, provs, transferred, no_data
    )

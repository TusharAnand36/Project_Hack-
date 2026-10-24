"""The /analyze pipeline (source plan §12.0): inputs -> gates -> diagnosis -> chains ->
Monte Carlo -> pea parity -> ranking -> verdict. Returns the §14.2 result object.

Recommendation rules follow §12.14; value of information, Pareto, readiness and the plan
arrive in Phase 5 and are left empty here.
"""

from __future__ import annotations

import time

import numpy as np

from compass import __version__
from compass import chains as chainsm
from compass import cost as costm
from compass import diagnosis as diag
from compass import effects as fx
from compass import gates as gatesm
from compass import pea as peam
from compass.contract import (
    AnalyzeRequest,
    AnalyzeResponse,
    Chain,
    Criterion,
    DecisionGrade,
    GateState,
    Meta,
    Pea,
    Scenario,
    Verdict,
    VerdictLabel,
)
from compass.data import Dataset
from compass.models import Grade, Param, Tag
from compass.montecarlo import ChainEval, Context, evaluate
from compass.sampling import Provenance, Sampler, as_value, combine, summarise

DISCLAIMER = (
    "Proof of concept. Not a substitute for laboratory validation. "
    "Decision support only. Not a regulatory approval. Confirm FSSAI classification and limits."
)
USER = Provenance(Tag.assumed, None, (), None, "data")  # a value the user typed (not a measurement)
RESOURCE_FIELDS = (
    "kwh_per_kg",
    "water_l_per_kg",
    "chem_inr_per_kg",
    "labour_h_per_t",
    "capex_ref_inr",
    "capex_ref_scale_kg_day",
)


class AnalyzeError(ValueError):
    """Request refers to something the dataset does not have (-> HTTP 422)."""


def _cfg(ds: Dataset, section: str, key: str) -> float:
    return getattr(ds.costs, section)[key].value


def _measured_prov(tag: Tag) -> Provenance:
    return Provenance(
        tag, Grade.A if tag is Tag.measured else None, ("user_batch",) if tag is Tag.measured else ()
    )


def build_sampler(req: AnalyzeRequest, ds: Dataset, n: int, seed: int) -> Sampler:
    bp = ds.byproducts[req.byproduct]
    s = Sampler(n, seed, k=_cfg(ds, "engine", "extrapolation_k"), lam=_cfg(ds, "engine", "pert_lambda"))
    # protein and N factor
    if req.batch.protein_pct is not None:
        s.add_value("bp.protein", req.batch.protein_pct.value, "%", _measured_prov(req.batch.protein_pct.tag))
    else:
        s.add("bp.protein", bp.composition["crude_protein_pct"])
    if req.batch.moisture_pct is not None:
        s.add_value(
            "bp.moisture", req.batch.moisture_pct.value, "%", _measured_prov(req.batch.moisture_pct.tag)
        )
    s.add("nf", ds.byproduct_defaults["n_factor"])
    s.add("bp.price", bp.price_inr_per_kg)
    # compound levels (batch measurement overrides the dataset)
    for cid, p in bp.compounds.items():
        if cid == "phytic_acid" and req.batch.phytate_pct is not None:
            s.add_value(
                f"cmp.{cid}", req.batch.phytate_pct.value, p.unit, _measured_prov(req.batch.phytate_pct.tag)
            )
        else:
            s.add(f"cmp.{cid}", p)
        floor = ds.compounds[cid].floor
        if floor is not None and not (floor.value is None and floor.dist is None):
            s.add(f"floor.{cid}", floor)
    for cls, p in bp.flavour_baseline.items():
        s.add(f"flav.{cls}", p)
    # treatments
    for tid, t in ds.treatments.items():
        for i, e in enumerate(t.effects):
            if bp.id in e.applies_to:
                s.add(f"t.{tid}.e{i}", e.reduction, missing="full_range")
        for i, se in enumerate(t.side_effects):
            s.add(f"t.{tid}.se{i}", se.addition)
        if t.kind == "process":
            s.add(f"t.{tid}.m", t.mass_yield, missing="full_range")
            s.add(f"t.{tid}.rho", t.protein_retention, missing="full_range")
        else:
            s.add(f"t.{tid}.pi", t.purity, missing="full_range")
            s.add(f"t.{tid}.rec", t.recovery, missing="full_range")
        for f in RESOURCE_FIELDS:
            s.add(f"t.{tid}.res.{f}", getattr(t.resources, f))
    # plant economics
    c = req.constraints
    for key, user in (
        ("electricity_inr_per_kwh", c.electricity_inr_per_kwh),
        ("water_inr_per_m3", c.water_inr_per_m3),
        ("labour_inr_per_h", c.labour_inr_per_h),
    ):
        if user is not None:
            s.add_value(f"u.{key}", user, ds.costs.utilities[key].unit, USER)
        else:
            s.add(f"u.{key}", ds.costs.utilities[key])
    for key, p in ds.costs.overheads.items():
        s.add(f"o.{key}", p)
    # pea isolate (user sliders override)
    pea = ds.costs.pea
    overrides = {
        "base_usd_per_kg": req.pea.base_usd_per_kg,
        "usd_inr": req.pea.usd_inr,
        "freight_frac": None if req.pea.freight_pct is None else req.pea.freight_pct / 100,
        "protein_frac": None if req.pea.protein_pct is None else req.pea.protein_pct / 100,
    }
    for key, p in pea.items():
        if overrides.get(key) is not None:
            s.add_value(f"pea.{key}", overrides[key], p.unit, USER)
        else:
            s.add(f"pea.{key}", p)
    return s


def _vals(d, key):
    x = d.get(key)
    return None if x is None else x.values


def _rng(x, prov, unit):
    return summarise(x, prov, unit)


def analyze(req: AnalyzeRequest, ds: Dataset) -> AnalyzeResponse:
    t0 = time.perf_counter()
    if req.byproduct not in ds.byproducts:
        raise AnalyzeError(f"unknown by-product '{req.byproduct}'; choose one of {sorted(ds.byproducts)}")
    if req.application not in ds.applications:
        raise AnalyzeError(
            f"unknown application '{req.application}'; choose one of {sorted(ds.applications)}"
        )
    unknown = sorted(set(req.constraints.exclude_treatments) - set(ds.treatments))
    if unknown:
        raise AnalyzeError(f"unknown treatment(s) in exclude_treatments: {unknown}")
    bad_eq = sorted(set(req.constraints.equipment) - set(ds.equipment))
    if bad_eq:
        raise AnalyzeError(f"unknown equipment {bad_eq}; choose from {ds.equipment}")

    bp, app = ds.byproducts[req.byproduct], ds.applications[req.application]
    n = req.n_draws or int(_cfg(ds, "engine", "n_draws"))
    seed = req.seed if req.seed is not None else int(_cfg(ds, "engine", "seed"))
    d = build_sampler(req, ds, n, seed).sample()
    limitations: list[str] = [
        "Inputs are sampled independently (no correlations between inputs).",
        "Functionality fit (solubility, emulsification, gelation) is a qualitative flag, not a computed score.",
    ]

    # ---- normalisation: true protein fraction of the raw cake on a dry basis (§12.2)
    prot = d["bp.protein"]
    crude = prot.values / 100
    if "bp.moisture" in d:
        crude = fx.to_dry_basis(crude, d["bp.moisture"].values / 100)
    elif req.batch.protein_pct is not None:
        limitations.append("Batch protein used as given (no moisture entered, so no dry-basis conversion).")
    n_used = (
        req.batch.protein_pct.n_factor if req.batch.protein_pct and req.batch.protein_pct.n_factor else 6.25
    )
    p0 = fx.true_protein(crude, d["nf"].values, n_used)
    p0_prov = combine([prot.prov, d["nf"].prov])
    if req.batch.protein_pct is None and not prot.unit.startswith("% dry"):
        limitations.append(f"{bp.name}: composition basis not stated in the source; treated as dry basis.")

    compounds = {}
    for cid in bp.compounds:
        s = d[f"cmp.{cid}"]
        if s.values is not None:
            compounds[cid] = (s.values.astype(float), s.prov, ds.compounds[cid].relative_to_raw)

    # ---- gates (§12.1)
    outcomes = gatesm.evaluate(req, ds)
    overall = gatesm.worst([o.gate.state for o in outcomes])

    # ---- targets (user overrides application defaults)
    tol = app.tolerances

    def tgt(user, key, unit):
        if user is not None:
            return (float(user), unit, USER)
        p = tol.get(key)
        return None if p is None or p.value is None else (p.value, p.unit, Provenance.of(p))

    targets = {
        "protein": tgt(req.targets.min_protein_pct, "min_protein_pct", "%"),
        "phytate": tgt(req.targets.max_phytate_pct, "max_phytate_pct_db", "% dry basis"),
        "tia": tgt(None, "max_tia_pct_raw", "% of raw activity"),
        "ofi": tgt(req.targets.max_offflavour_index, "max_ofi", "index 0-10"),
        "cost": (
            None
            if req.targets.max_cost_inr_per_kg_protein is None
            else (req.targets.max_cost_inr_per_kg_protein, "INR/kg protein", USER)
        ),
    }

    # ---- diagnosis (§12.3)
    levels = {
        cid: diag.Level(d[f"cmp.{cid}"].values, d[f"cmp.{cid}"].prov, bp.compounds[cid].unit)
        for cid in bp.compounds
    }
    diagnosis = diag.diagnose(ds, bp, app, levels, outcomes, req.targets.max_phytate_pct)
    req_protein = targets["protein"]
    issues = diag.issues(
        bp, app, diagnosis, p0 * 100, p0_prov, req_protein[0], req_protein[2], app.functionality_tests
    )

    # ---- pea isolate (§12.8)
    duty_p = ds.costs.duty_modes[req.pea.duty_mode.value]
    pea_in = peam.PeaInputs(
        base_usd_per_kg=d["pea.base_usd_per_kg"].values,
        usd_inr=d["pea.usd_inr"].values,
        freight_frac=d["pea.freight_frac"].values,
        duty_frac=duty_p.value,
        protein_frac=d["pea.protein_frac"].values,
        clearing_frac=0.0 if d["pea.clearing_frac"].values is None else d["pea.clearing_frac"].values,
        buyer_discount=d["pea.buyer_discount"].values,
    )
    pea_keys = ["base_usd_per_kg", "usd_inr", "freight_frac", "protein_frac", "buyer_discount"]
    pea_prov = combine([d[f"pea.{k}"].prov for k in pea_keys] + [Provenance.of(duty_p)])
    landed = peam.landed_per_kg_protein(pea_in)

    # ---- plant economics (§12.7)
    scale = req.scale_kg_day or _cfg(ds, "decision", "default_scale_kg_day")
    cap = ds.costs.capital
    econ = costm.Economics(
        scale_kg_day=scale,
        discount_rate=cap["discount_rate"].value,
        life_years=cap["life_years"].value,
        operating_days=cap["operating_days"].value,
        utilisation=cap["utilisation"].value,
        scale_exponent=cap["scale_exponent"].value,
        tariff_inr_per_kwh=_vals(d, "u.electricity_inr_per_kwh"),
        water_inr_per_m3=_vals(d, "u.water_inr_per_m3"),
        wage_inr_per_h=_vals(d, "u.labour_inr_per_h"),
        qa_inr_per_kg_raw=_vals(d, "o.qa_inr_per_kg_raw"),
        overhead_frac=_vals(d, "o.overhead_frac"),
    )
    econ_prov = [Provenance.of(cap[k]) for k in cap]
    credit = req.co_product_credit_inr_per_kg_protein
    if credit is None:
        credit = _cfg(ds, "decision", "co_product_credit_inr_per_kg_protein")

    ctx = Context(
        ds, bp, app.id, d, n, p0, p0_prov, compounds, econ, econ_prov, pea_in, pea_prov, float(credit)
    )

    # ---- chains (§12.4) + Monte Carlo (§12.9)
    cands = chainsm.candidates(
        ds, bp.id, req.constraints.exclude_treatments, req.constraints.no_solvents, req.constraints.equipment
    )
    seqs = chainsm.enumerate_chains(cands.allowed, ds, bp.id, app.id)
    max_chains = int(_cfg(ds, "engine", "max_chains"))
    evals: list[ChainEval] = []
    stop_fail = overall is GateState.FAIL
    if not stop_fail:
        for seq in seqs:
            ev = evaluate(seq, ctx, targets)
            if targets["cost"] and ev.cost.per_kg_protein is not None and seq:
                if np.percentile(ev.cost.per_kg_protein, 10) > targets["cost"][0]:  # prune rule 8a
                    continue
            evals.append(ev)
    total = len(evals)
    evals.sort(key=lambda e: (-float(e.spec.mean()), float(np.median(e.cost.per_kg_protein)), len(e.seq)))
    capped = len(evals) > max_chains
    evals = evals[:max_chains]

    not_viable = _cfg(ds, "readiness", "not_viable_p_spec_max")
    chain_models = [_chain_model(ev, i + 1, ds, app, landed, not_viable) for i, ev in enumerate(evals)]
    _badges(chain_models, not_viable)

    # ---- pea block
    best = evals[0] if evals else None
    pea_block = _pea_block(req, ds, d, pea_in, pea_prov, landed, best, duty_p)

    # ---- verdict (§12.14)
    verdict = _verdict(outcomes, overall, chain_models, best, landed, pea_block, not_viable, issues)

    # ---- limitations
    no_data = sorted({x for ev in evals for x in ev.no_data})
    if no_data:
        limitations.append(
            f"{len(no_data)} fractions have no data and are sampled over their full 0-1 range "
            f"(assumed, grade D), e.g. {', '.join(no_data[:3])}. Ranges are wide on purpose."
        )
    if any(not ev.cost.complete for ev in evals):
        missing = sorted({m.split(":")[-1].strip() for ev in evals for m in ev.cost.missing})
        limitations.append(f"Costs are lower bounds: missing {', '.join(missing)} inputs are excluded.")
    if evals and all(ev.ofi is None for ev in evals):
        limitations.append("Off-flavour index not computable: no sensory baseline data for this by-product.")
    if cands.removed:
        limitations.append(
            "Treatments not considered: " + "; ".join(f"{k} ({v})" for k, v in cands.removed.items())
        )
    for o in outcomes:
        limitations += [r for r in o.gate.reasons if r.startswith("oil-extraction route not given")]
    limitations.append("This is a proof of concept; the next step is laboratory validation.")

    return AnalyzeResponse(
        meta=Meta(
            seed=seed,
            n_draws=n,
            engine_version=__version__,
            dataset_version=ds.version,
            elapsed_ms=int((time.perf_counter() - t0) * 1000),
            chains_total=total,
            chains_shown=len(chain_models),
            chains_capped=capped,
        ),
        verdict=verdict,
        gates=[o.gate for o in outcomes],
        diagnosis=diagnosis,
        issues=issues,
        chains=chain_models,
        pea=pea_block,
        limitations=limitations,
        disclaimer=DISCLAIMER,
    )


# ---------------------------------------------------------------- helpers


def _chain_model(ev: ChainEval, rank: int, ds: Dataset, app, landed, not_viable: float) -> Chain:
    pv = ev.provs
    p50_protein = float(np.median(ev.protein_pct))
    th = ds.tier_thresholds
    tier = fx.tier_of(
        p50_protein, len(ev.seq), th["concentrate_min_protein_pct"].value, th["isolate_min_protein_pct"].value
    )
    spec_prov = combine([pv["protein"]] + [c.target_prov for c in ev.criteria])
    criteria = [
        Criterion(
            id=c.id,
            target=as_value(c.target, c.target_prov, c.unit),
            evaluated=c.evaluated,
            p_pass=None if c.passed is None else as_value(float(c.passed.mean()), spec_prov, "probability"),
            note=c.note,
        )
        for c in ev.criteria
    ]
    cost_ok = ev.cost.per_kg_protein is not None and "raw material price" not in ev.cost.missing
    ch = Chain(
        id=chainsm.chain_id(ev.seq),
        steps=list(ev.seq),
        tier=tier,
        rank=rank,
        protein_retained=summarise(ev.retained, pv["protein"], "fraction"),
        protein_pct_final=summarise(ev.protein_pct, pv["protein"], "%"),
        ofi=None if ev.ofi is None else summarise(ev.ofi, pv["protein"], "index 0-10"),
        phytate_pct_final=(
            summarise(ev.compound_final["phytic_acid"], pv["phytic_acid"], "% dry basis")
            if "phytic_acid" in ev.compound_final
            else None
        ),
        tia_pct_raw_final=(
            summarise(ev.compound_final["trypsin_inhibitor"], pv["trypsin_inhibitor"], "% of raw activity")
            if "trypsin_inhibitor" in ev.compound_final
            else None
        ),
        cost_complete=ev.cost.complete,
        cost_missing=ev.cost.missing,
        p_spec=as_value(float(ev.spec.mean()), spec_prov, "probability"),
        criteria=criteria,
        transferred=ev.transferred,
        no_data_inputs=ev.no_data,
    )
    if cost_ok:
        ch.cost_inr_per_kg_protein = summarise(ev.cost.per_kg_protein, pv["cost"], "INR/kg protein")
        ch.cost_breakdown = {
            k: summarise(v, pv["cost"], "INR/kg protein")
            for k, v in ev.cost.breakdown_per_kg_protein.items()
            if np.any(v)
        }
        if ev.margin is not None:
            ch.margin_vs_pea = summarise(ev.margin, pv["margin"], "INR/kg protein")
            ch.p_margin_positive = as_value(float(np.mean(ev.margin > 0)), pv["margin"], "probability")
    if ev.cost.kwh_per_kg_protein is not None:
        ch.kwh_per_kg_protein = summarise(ev.cost.kwh_per_kg_protein, pv["cost"], "kWh/kg protein")
    if ev.cost.l_water_per_kg_protein is not None:
        ch.l_water_per_kg_protein = summarise(ev.cost.l_water_per_kg_protein, pv["cost"], "L/kg protein")
    if ch.transferred:
        ch.badges.append("transferred")
    if not cost_ok:
        ch.badges.append("cost_not_computable")
    elif not ev.cost.complete:
        ch.badges.append("cost_lower_bound")
    if ch.p_spec.value < not_viable:
        ch.badges.append("not_recommended")
    return ch


def _badges(chains: list[Chain], not_viable: float) -> None:
    viable = [c for c in chains if c.p_spec.value >= not_viable]
    if viable:
        viable[0].badges.insert(0, "highest_p_spec")
    priced = [c for c in chains if c.p_spec.value >= 0.5 and c.cost_inr_per_kg_protein is not None]
    if priced:
        min(priced, key=lambda c: c.cost_inr_per_kg_protein.p50).badges.insert(0, "cheapest_viable")


def _pea_block(req, ds, d, pea_in, pea_prov, landed, best: ChainEval | None, duty_p: Param) -> Pea:
    keys = {
        "base_usd_per_kg": "USD/kg",
        "usd_inr": "INR/USD",
        "freight_frac": "fraction",
        "protein_frac": "fraction",
    }
    inputs = {
        k: summarise(np.broadcast_to(d[f"pea.{k}"].values, (len(landed),)), d[f"pea.{k}"].prov, u)
        for k, u in keys.items()
    }
    inputs["duty_frac"] = summarise(np.full(3, duty_p.value), Provenance.of(duty_p), "fraction")
    b2b = d.get("pea.india_b2b_inr_per_kg_product")
    b2b_r = None
    if b2b is not None and b2b.values is not None:
        b2b_r = summarise(
            b2b.values / pea_in.protein_frac,
            combine([b2b.prov, d["pea.protein_frac"].prov]),
            "INR/kg protein",
        )
    block = Pea(
        duty_mode=req.pea.duty_mode,
        inputs=inputs,
        landed_inr_per_kg_product=summarise(peam.landed_per_kg_product(pea_in), pea_prov, "INR/kg product"),
        landed_inr_per_kg_protein=summarise(landed, pea_prov, "INR/kg protein"),
        b2b_cross_check_inr_per_kg_protein=b2b_r,
        scenarios=[],
    )
    for sc in ds.costs.scenarios:
        shocked = peam.landed_per_kg_protein(peam.apply_scenario(pea_in, sc.set, sc.scale))
        prov = combine([pea_prov, Provenance(Tag.assumed, Grade.D, (sc.source_id,) if sc.source_id else ())])
        block.scenarios.append(
            Scenario(id=sc.id, name=sc.name, landed=summarise(shocked, prov, "INR/kg protein"))
        )
    if best is not None and best.margin is not None:
        be = peam.break_even_base_usd(pea_in, best.cost.per_kg_protein)
        block.break_even_base_usd_per_kg = summarise(be, combine([best.provs["cost"], pea_prov]), "USD/kg")
        block.break_even_note = f"for the top chain ({chainsm.chain_id(best.seq)})" + (
            "; our cost is a lower bound, so the true break-even is higher" if not best.cost.complete else ""
        )
    elif best is not None:
        block.break_even_note = "not computable: raw material price missing"
    return block


def _verdict(
    outcomes, overall, chains: list[Chain], best, landed, pea_block: Pea, not_viable, issues
) -> Verdict:
    stop = [o for o in outcomes if o.gate.kind == "stop" or o.gate.state is GateState.FAIL]
    reasons: list[str] = []
    actions: list[str] = []
    if overall is GateState.FAIL:
        for o in stop:
            if o.gate.state is GateState.FAIL:
                reasons += [f"{o.gate.id} {o.gate.name}: {r}" for r in o.gate.reasons]
        actions.append("Divert to feed or re-source the material; chains are not ranked for a failed gate.")
        return Verdict(
            label=VerdictLabel.NO_GO,
            grade=DecisionGrade.not_viable,
            p_go=as_value(0.0, Provenance(Tag.published, None), "probability"),
            reasons=reasons,
            actions=actions,
        )
    viable = [c for c in chains if c.p_spec.value >= not_viable]
    top = viable[0] if viable else (chains[0] if chains else None)
    # P(GO) = P(gates pass) x P(spec | gates pass), using gates with a known pass probability
    unknown = [o.gate.id for o in stop if o.gate.state is GateState.TEST_FIRST and o.p_pass is None]
    p_gates = float(np.prod([o.p_pass for o in stop if o.p_pass is not None])) if stop else 1.0
    gate_provs = [o.prior_prov for o in stop if o.prior_prov is not None]
    p_go = None
    note = None
    if top is not None:
        prov = combine(
            gate_provs + [Provenance(top.p_spec.tag, top.p_spec.grade, tuple(top.p_spec.source_ids))]
        )
        p_go = as_value(p_gates * top.p_spec.value, prov, "probability")
        if unknown:
            note = f"upper bound: gates {', '.join(unknown)} have no prior probability yet"
    tf = [o for o in stop if o.gate.state is GateState.TEST_FIRST]
    if tf:
        label = VerdictLabel.TEST_FIRST
        for o in tf:
            reasons.append(
                f"{o.gate.id} {o.gate.name}: {o.gate.reasons[0] if o.gate.reasons else 'test required'}"
            )
            if o.gate.required_test:
                actions.append(
                    f"Run {o.gate.required_test} ({o.gate.id}); flips when {o.gate.flip_condition}."
                )
    elif viable:
        label = VerdictLabel.GO
        reasons.append(
            f"All safety gates pass; best chain {top.id} meets spec with P = {top.p_spec.value:.2f}."
        )
    else:
        label = VerdictLabel.NO_GO
        reasons.append(f"No chain reaches P(spec) ≥ {not_viable:g}: no route is likely to meet the targets.")
    if not viable:
        grade = DecisionGrade.not_viable
        if label is VerdictLabel.TEST_FIRST:
            reasons.append(f"Even if the gates pass, no chain reaches P(spec) ≥ {not_viable:g}.")
    elif top.margin_vs_pea is not None and top.margin_vs_pea.p50 < 0:
        grade = DecisionGrade.not_viable
    else:
        grade = DecisionGrade.hypothesis_grade  # decision-grade needs the readiness check (Phase 5)
    if top is not None:
        if top.cost_inr_per_kg_protein is not None:
            parity = pea_block.landed_inr_per_kg_protein.p50
            if top.cost_inr_per_kg_protein.p50 > parity:
                driver = (
                    max(top.cost_breakdown.items(), key=lambda kv: kv[1].p50)[0]
                    if top.cost_breakdown
                    else "?"
                )
                be = pea_block.break_even_base_usd_per_kg
                reasons.append(
                    f"Not competitive today: {top.id} costs more than imported pea isolate at P50 "
                    f"(main cost driver: {driver}"
                    + (f"; break-even pea base ≈ US${be.p50:.2f}/kg" if be else "")
                    + ")."
                )
        else:
            reasons.append("Cost per kg protein not computable: raw material price missing.")
        if top.transferred:
            reasons.append(
                "Key evidence is transferred from other materials: must be demonstrated on this one."
            )
    for i in issues:
        if i.kind in ("no_treatment_needed", "protein_density_gap", "diagnosis_blocked"):
            reasons.append(i.message)
    return Verdict(label=label, grade=grade, p_go=p_go, p_go_note=note, reasons=reasons, actions=actions)

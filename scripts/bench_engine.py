"""Phase 2 acceptance check: P10/P50/P90 cost for one chain in < 1 s at 8,192 draws.

Chain: groundnut cake -> phytase -> ae_iep. Dataset values are used where they exist.
Every MISSING process input is replaced by a SYNTHETIC timing value defined below; these
numbers exist only in this script, are not data, and never reach the API or the UI.

Run: PYTHONPATH=engine .venv/bin/python scripts/bench_engine.py
"""

from __future__ import annotations

import sys
import time

import numpy as np

from compass import cost, effects, pea
from compass.data import load_dataset
from compass.sampling import Sampler

SYNTHETIC = {  # per kg input; timing-only stand-ins for null cells
    "kwh_per_kg": 0.3,
    "water_l_per_kg": 8.0,
    "chem_inr_per_kg": 4.0,
    "labour_h_per_t": 3.0,
    "capex_ref_inr": 5e6,
    "capex_ref_scale_kg_day": 1000.0,
}


def main(n: int = 8192) -> int:
    ds = load_dataset()
    t0 = time.perf_counter()
    gnc = ds.byproducts["groundnut_cake"]
    k = ds.costs.engine["extrapolation_k"].value
    s = Sampler(n, seed=int(ds.costs.engine["seed"].value), k=k)
    s.add("protein", gnc.composition["crude_protein_pct"])
    s.add("nf", ds.byproduct_defaults["n_factor"])
    s.add("price", gnc.price_inr_per_kg)
    phy, iep = ds.treatments["phytase"], ds.treatments["ae_iep"]
    s.add("phy.m", phy.mass_yield, missing="full_range")
    s.add("phy.rho", phy.protein_retention, missing="full_range")
    s.add("iep.pi", iep.purity)
    s.add("iep.rec", iep.recovery)
    for name, p in ds.costs.pea.items():
        s.add(f"pea.{name}", p)
    d = s.sample()

    p0 = effects.true_protein(d["protein"].values / 100, d["nf"].values)
    b0 = effects.start(n, p0)
    b1 = effects.step(b0, "process", mass_yield=d["phy.m"].values, protein_retention=d["phy.rho"].values)
    b2 = effects.step(b1, "fractionation", purity=d["iep.pi"].values, recovery=d["iep.rec"].values)

    def res(name: str, x: np.ndarray) -> cost.StepResources:
        return cost.StepResources(name, x, **{f: np.full(n, v) for f, v in SYNTHETIC.items()})

    econ = cost.Economics(
        500.0,
        0.12,
        10,
        300,
        0.8,
        0.6,
        np.full(n, 8.0),
        np.full(n, 30.0),
        np.full(n, 120.0),
        np.full(n, 1.0),
        np.full(n, 0.1),
    )
    c = cost.chain_cost(
        d["price"].values, [res("phytase", b0.mass), res("ae_iep", b1.mass)], b2.mass, b2.protein, econ
    )
    duty = ds.costs.duty_modes["full_stack_44"].value
    pi = pea.PeaInputs(
        d["pea.base_usd_per_kg"].values,
        d["pea.usd_inr"].values,
        d["pea.freight_frac"].values,
        duty,
        d["pea.protein_frac"].values,
        buyer_discount=d["pea.buyer_discount"].values,
    )
    landed = pea.landed_per_kg_protein(pi)
    dt = time.perf_counter() - t0

    q = lambda x: np.percentile(x, [10, 50, 90]).round(0)  # noqa: E731
    print(f"draws={n}  elapsed={dt:.3f}s  (SYNTHETIC process inputs; not results)")
    print(f"protein retained P10/P50/P90 : {np.percentile(b2.protein / b0.protein, [10, 50, 90]).round(2)}")
    print(f"our cost INR/kg protein      : {q(c.per_kg_protein)}")
    print(f"pea landed INR/kg protein    : {q(landed)}")
    return 0 if dt < 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())

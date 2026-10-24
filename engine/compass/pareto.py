"""Pareto view and named picks (source plan §12.10).

Objectives on medians: maximise protein retained, minimise off-flavour index (when computable)
and minimise cost per kg protein (when computable). P(A dominates B) is computed draw by draw
on the common random numbers; two chains are "statistically tied" when neither dominates the
other with probability >= 0.8.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

Arr = np.ndarray
TIE_THRESHOLD = 0.8


@dataclass
class Objectives:
    id: str
    retained: Arr
    cost: Arr | None
    ofi: Arr | None
    p_spec: float
    e_utility: float | None


def _cols(o: Objectives, use_cost: bool, use_ofi: bool) -> list[Arr]:
    cols = [-o.retained]  # everything as "lower is better"
    if use_cost:
        cols.append(o.cost)
    if use_ofi:
        cols.append(o.ofi)
    return cols


def front(items: list[Objectives]) -> set[str]:
    """Ids of chains not dominated on medians."""
    use_cost = all(i.cost is not None for i in items)
    use_ofi = all(i.ofi is not None for i in items)
    med = {i.id: np.array([float(np.median(c)) for c in _cols(i, use_cost, use_ofi)]) for i in items}
    out = set()
    for a in items:
        ma = med[a.id]
        dominated = any(np.all(med[b.id] <= ma) and np.any(med[b.id] < ma) for b in items if b.id != a.id)
        if not dominated:
            out.add(a.id)
    return out


def p_dominates(a: Objectives, b: Objectives, use_cost: bool, use_ofi: bool) -> float:
    ca, cb = np.vstack(_cols(a, use_cost, use_ofi)), np.vstack(_cols(b, use_cost, use_ofi))
    return float(np.mean(np.all(ca <= cb, axis=0) & np.any(ca < cb, axis=0)))


def ties(items: list[Objectives], ids: set[str]) -> list[list[str]]:
    sel = [i for i in items if i.id in ids]
    use_cost = all(i.cost is not None for i in sel)
    use_ofi = all(i.ofi is not None for i in sel)
    out = []
    for i, a in enumerate(sel):
        for b in sel[i + 1 :]:
            if (
                max(p_dominates(a, b, use_cost, use_ofi), p_dominates(b, a, use_cost, use_ofi))
                < TIE_THRESHOLD
            ):
                out.append([a.id, b.id])
    return out


def picks(items: list[Objectives], cost_target: float | None, not_viable: float) -> dict[str, str | None]:
    viable = [i for i in items if i.p_spec >= not_viable]
    with_u = [i for i in viable if i.e_utility is not None]
    best_ev = max(with_u, key=lambda i: i.e_utility).id if with_u else None
    safe_pool = [
        i
        for i in viable
        if cost_target is None or (i.cost is not None and float(np.median(i.cost)) <= cost_target)
    ]
    safest = max(safe_pool, key=lambda i: i.p_spec).id if safe_pool else None
    cheap_pool = [i for i in items if i.p_spec >= 0.5 and i.cost is not None]
    cheapest = min(cheap_pool, key=lambda i: float(np.median(i.cost))).id if cheap_pool else None
    return {"best_expected_value": best_ev, "safest": safest, "cheapest_viable": cheapest}

"""Off-flavour index (source plan §12.6): a transparent index, not a taste predictor.

    OFI_before = min(10, sum_c s_c)                      s_c = baseline of flavour class c
    per step:  s_c <- s_c * (1 - r_step,c) + a_step,c     r from compound effects of that class,
                                                          a = side-note the step adds (heat -> roasted)
    OFI_after  = min(10, sum_c s_c)

Returns None (not computable) when any baseline or any side-note of a step is missing:
the dataset has no sensory data yet, and an index built on guesses would be false precision.
"""

from __future__ import annotations

import numpy as np

Arr = np.ndarray
OFI_MAX = 10.0


def ofi(
    baselines: dict[str, Arr | None],
    steps: list[tuple[dict[str, Arr], dict[str, Arr | None]]],
) -> Arr | None:
    """`steps` = [(reduction by class, addition by class), ...] in chain order."""
    if not baselines or any(v is None for v in baselines.values()):
        return None
    s = {c: np.asarray(v, dtype=float).copy() for c, v in baselines.items()}
    for reductions, additions in steps:
        if any(v is None for v in additions.values()):
            return None
        for c, r in reductions.items():
            if c in s:
                s[c] = s[c] * (1.0 - np.clip(r, 0.0, 1.0))
        for c, a in additions.items():
            s[c] = s.get(c, 0.0) + a
    return np.minimum(OFI_MAX, sum(s.values()))

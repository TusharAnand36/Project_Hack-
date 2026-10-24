"""Treatment-chain enumeration (source plan §12.4).

Depth-first search over the treatments that survive exclusions and equipment, applying
the precedence rules in treatments.json. The no-op chain (raw flour) is always included.

Also removed before enumeration (stated assumption): treatments with no listed effect on
this by-product, unless they change the product tier (fractionation) or its form
(extrusion); such steps would only add cost.
"""

from __future__ import annotations

from dataclasses import dataclass

from compass.data import Dataset, Treatment

TEXTURISING = {"extrude"}


@dataclass(frozen=True)
class Candidates:
    allowed: list[str]
    removed: dict[str, str]  # treatment -> reason


def candidates(
    ds: Dataset,
    byproduct: str,
    exclude: list[str],
    no_solvents: bool,
    equipment: list[str],
) -> Candidates:
    if byproduct == "pea_protein_isolate":
        return Candidates(
            [],
            {tid: "Commercial isolate reference; no validated cake treatment model" for tid in ds.treatments},
        )
    allowed: list[str] = []
    removed: dict[str, str] = {}
    have = set(equipment)
    for t in ds.treatments.values():
        if t.id in exclude:
            removed[t.id] = "excluded by user"
        elif no_solvents and t.uses_solvent:
            removed[t.id] = "uses a solvent ('no solvents' selected)"
        elif have and not set(t.requires_equipment) <= have:
            removed[t.id] = f"needs {', '.join(sorted(set(t.requires_equipment) - have))}"
        elif not _relevant(t, byproduct):
            removed[t.id] = "no listed effect on this by-product"
        else:
            allowed.append(t.id)
    return Candidates(allowed, removed)


def _relevant(t: Treatment, byproduct: str) -> bool:
    if t.kind == "fractionation" or t.id in TEXTURISING:
        return True
    return any(byproduct in e.applies_to for e in t.effects)


def valid(seq: tuple[str, ...], ds: Dataset, byproduct: str, application: str) -> bool:
    """True if a complete sequence obeys every rule. Used for the final check."""
    return _prefix_ok(seq, ds, byproduct, application) and _complete_ok(seq, ds, byproduct)


def _prefix_ok(seq: tuple[str, ...], ds: Dataset, byproduct: str, application: str) -> bool:
    pc = ds.precedence
    if len(seq) > pc.max_length or len(set(seq)) != len(seq):
        return False
    pos = {t: i for i, t in enumerate(seq)}
    for t, bps in pc.first_for.items():  # e.g. stabilise first for rice bran
        if byproduct in bps and seq and seq[0] != t:
            return False
    for a, b in pc.before:
        if a in pos and b in pos and pos[a] > pos[b]:
            return False
    for a, b in pc.forbidden_sequences:
        if a in pos and b in pos and pos[a] < pos[b]:
            return False
    for a, b in pc.mutually_exclusive:
        if a in pos and b in pos:
            return False
    fr = [i for i, t in enumerate(seq) if ds.treatments[t].kind == "fractionation"]
    if len(fr) > pc.max_fractionation:
        return False
    if fr:  # fractionation ends the chain, except steps allowed after it for some applications
        for t in seq[fr[0] + 1 :]:
            if application not in pc.after_fractionation_allowed.get(t, []):
                return False
    for x, a, b in pc.not_between:
        if x in pos and a in pos and b in pos and min(pos[a], pos[b]) < pos[x] < max(pos[a], pos[b]):
            return False
    return True


def _complete_ok(seq: tuple[str, ...], ds: Dataset, byproduct: str) -> bool:
    # extrusion is either the first step (flour route) or the last (texturise a concentrate)
    for t in TEXTURISING:
        if t in seq and seq.index(t) not in (0, len(seq) - 1):
            return False
    return True


def enumerate_chains(
    allowed: list[str], ds: Dataset, byproduct: str, application: str
) -> list[tuple[str, ...]]:
    """All valid sequences, raw flour `()` first. Deterministic order."""
    out: list[tuple[str, ...]] = [()]

    def dfs(prefix: tuple[str, ...]) -> None:
        for t in allowed:
            seq = prefix + (t,)
            if not _prefix_ok(seq, ds, byproduct, application):
                continue
            if _complete_ok(seq, ds, byproduct):
                out.append(seq)
            dfs(seq)

    dfs(())
    return out


def chain_id(seq: tuple[str, ...]) -> str:
    return "raw_flour" if not seq else "+".join(seq)

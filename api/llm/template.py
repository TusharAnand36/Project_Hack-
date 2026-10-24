"""Deterministic texts used when no LLM is available, or when LLM text fails the verifier.
Built only from engine numbers, formatted the way the UI formats them (en-IN)."""

from __future__ import annotations

from compass.contract import AnalyzeResponse


def inr(x: float) -> str:
    """Indian digit grouping: 151823 -> 1,51,823."""
    neg, n = x < 0, abs(int(round(x)))
    s = str(n)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups) + "," + tail
    return ("−" if neg else "") + s


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def pct(p: float) -> str:
    return f"{p * 100:.0f}%"


def explain(r: AnalyzeResponse) -> str:
    v = r.verdict
    parts = [f"Verdict: {v.label.value} ({v.grade.value})."]
    parts += [x.rstrip(".") + "." for x in v.reasons[:2]]
    top = r.chains[0] if r.chains else None
    if top:
        steps = " then ".join(s.replace("_", " ") for s in top.steps) or "no treatment (raw flour)"
        parts.append(
            f"The leading chain is {steps}, giving {_article(top.tier)} {top.tier.replace('_', ' ')} with about "
            f"{top.protein_pct_final.p50:.1f}% protein and a {pct(top.p_spec.value)} chance of meeting your spec."
        )
        if top.cost_inr_per_kg_protein:
            lb = (
                " (a lower bound, because some process costs have no data yet)"
                if not top.cost_complete
                else ""
            )
            parts.append(
                f"Our cost is about ₹{inr(top.cost_inr_per_kg_protein.p50)} per kg protein{lb}, against "
                f"₹{inr(r.pea.landed_inr_per_kg_protein.p50)} for imported pea isolate landed in India."
            )
        else:
            parts.append("Our cost per kg protein is not available because the by-product price is missing.")
    elif v.actions:
        parts.append(v.actions[0])
    if r.voi and r.voi.recommended_test:
        t = next(x for x in r.voi.tests if x.test_id == r.voi.recommended_test)
        parts.append(f"The test to buy first is {t.name}, worth about ₹{inr(t.evsi.value)} per decision.")
    elif r.voi:
        parts.append(r.voi.recommendation)
    parts.append("Decision support only; confirm FSSAI classification.")
    return " ".join(parts)


def plan_paragraph(r: AnalyzeResponse) -> str:
    if not r.plan or not r.plan.tests:
        return "No validation tests are outstanding for this analysis."
    first = r.plan.tests[:3]
    names = ", ".join(t.name for t in first)
    crit = " ".join(f"{t.name}: {t.acceptance}." for t in first)
    return (
        f"Next experiment: run {names} on a representative composite, at least "
        f"{first[0].replicates} replicates each. Acceptance criteria. {crit} "
        f"Then re-run the engine with the measured values."
    )

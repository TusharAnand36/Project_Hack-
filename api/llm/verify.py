"""Number verifier (source plan §13): every number in LLM text must come from the engine.

Extracts numbers written the way an Indian reader would see them (₹1,00,000; 12.5%; 3–5;
"2 lakh"; "1.5 crore"; −4,075) and checks each against the numbers in the engine JSON and the
user's input, at the precision the text shows. Probabilities may appear as fractions or %.
Also rejects source ids that are not in sources.json.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

# a number not glued to letters (so "G1", "AFB1", "N×6.25"-style ids are skipped), with
# Indian or western grouping, optional decimals, optional "lakh"/"crore" multiplier
_NUM = re.compile(
    r"(?<![A-Za-z0-9_.])([-−]?)(\d{1,3}(?:,\d{2,3})+|\d+)(\.\d+)?(?![A-Za-z0-9_])(\s*(?:lakh|crore))?",
    re.IGNORECASE,
)
_SOURCE_LIKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)*_(?:19|20)\d{2}\b")
_MULT = {"lakh": 1e5, "crore": 1e7}


@dataclass(frozen=True)
class Found:
    text: str
    value: float
    decimals: int  # precision shown in the text
    scale: float  # 1, 1e5 or 1e7


_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def extract(text: str) -> list[Found]:
    out = []
    text = text.translate(_DEVANAGARI_DIGITS)  # Hindi text may use Devanagari digits
    for m in _NUM.finditer(text):
        sign, whole, frac, mult = m.group(1), m.group(2), m.group(3) or "", (m.group(4) or "").strip().lower()
        v = float(whole.replace(",", "") + frac)
        if sign:
            v = -v
        scale = _MULT.get(mult, 1.0)
        out.append(Found(m.group(0).strip(), v * scale, len(frac) - 1 if frac else 0, scale))
    return out


def numbers_in(obj: Any) -> set[float]:
    """Every number in a JSON-like object, including numbers written inside its strings."""
    found: set[float] = set()

    def walk(x: Any) -> None:
        if isinstance(x, bool) or x is None:
            return
        if isinstance(x, int | float):
            found.add(float(x))
        elif isinstance(x, str):
            found.update(f.value for f in extract(x))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list | tuple):
            for v in x:
                walk(v)

    walk(obj)
    return found


def _matches(f: Found, allowed: Iterable[float]) -> bool:
    tol = 0.5 * 10 ** (-f.decimals) * f.scale  # half a unit of the last digit shown
    for a in allowed:
        for cand in (a, a * 100, -a):  # fractions may be written as %
            if abs(cand - f.value) <= tol + 1e-9 * max(1.0, abs(cand)):
                return True
    return False


@dataclass
class Verdict:
    ok: bool
    bad_numbers: list[str] = field(default_factory=list)
    bad_sources: list[str] = field(default_factory=list)


def verify(text: str, allowed_numbers: set[float], known_sources: set[str]) -> Verdict:
    bad = [f.text for f in extract(text) if not _matches(f, allowed_numbers)]
    srcs = [s for s in _SOURCE_LIKE.findall(text) if s not in known_sources]
    return Verdict(ok=not bad and not srcs, bad_numbers=bad, bad_sources=srcs)

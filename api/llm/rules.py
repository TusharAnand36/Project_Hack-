"""Rule-based reader for "describe in words" (fallback when no LLM is available).

Only copies numbers the user wrote; never guesses. English plus common Hindi words for the
by-products. Anything it cannot read is left for the user to fill in the form.
"""

from __future__ import annotations

import re
from typing import Any

_F = r"(\d+(?:\.\d+)?)"
BYPRODUCT = [
    (r"sunflower|सूरजमुखी", "sunflower_cake"),
    (r"soy\s*bean|\bsoy\b|सोयाबीन", "soybean_cake"),
    (r"pea\s*(?:protein|isolate)|मटर", "pea_protein_isolate"),
    (r"ground\s*nut|peanut|moong\s*phali|मूंगफली", "groundnut_cake"),
    (r"almond|badam|बादाम", "almond_cake"),
]
APPLICATION = [
    (r"protein[-\s]+isolate", "beverage"),
    (r"protein[-\s]+rich[-\s]+flour|\bbakery\b", "extruded_snack"),
    (r"protein[-\s]+concentrate", "meat_analogue"),
    (r"drink|beverage|shake|smoothie|पेय", "beverage"),
    (r"snack|puff|extrud|chips|namkeen|नमकीन", "extruded_snack"),
    (r"meat|analogu|analog|textur|\btvp\b|patty|nugget", "meat_analogue"),
]
UNIT_KG = {"kg": 1, "quintal": 100, "tonne": 1000, "ton": 1000, "t": 1000}


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def parse(text: str) -> dict[str, Any]:
    t = text.lower()
    out: dict[str, Any] = {}
    for pat, val in BYPRODUCT:
        if re.search(pat, t):
            out["byproduct"] = val
            break
    # The source ingredient can also contain "protein isolate"; prefer its stated target clause.
    target_text = re.split(r"\b(?:for|to make)\b", t)[-1]
    for pat, val in APPLICATION:
        if re.search(pat, target_text):
            out["application"] = val
            break
    m = re.search(rf"{_F}\s*%\s*(?:of\s+)?protein|protein[^0-9%]{{0,20}}{_F}\s*%", t)
    if m:
        out["batch.protein_pct"] = _num(m.group(1) or m.group(2))
    m = re.search(rf"{_F}\s*%\s*moisture|moisture[^0-9%]{{0,20}}{_F}\s*%", t)
    if m:
        out["batch.moisture_pct"] = _num(m.group(1) or m.group(2))
    m = re.search(rf"(?:aflatoxin(?:\s*b1)?|afb1)[^0-9]{{0,20}}{_F}\s*(?:ppb|µg/kg|ug/kg)", t)
    if m:
        out["batch.afb1_ppb"] = _num(m.group(1))
    m = re.search(rf"(?:\bffa\b|free fatty acids?)[^0-9]{{0,15}}{_F}\s*%", t)
    if m:
        out["batch.ffa_pct"] = _num(m.group(1))
    if re.search(r"no\s+solvents?|without\s+solvents?|solvent[- ]free", t):
        out["constraints.no_solvents"] = True
    if re.search(r"\bexport\b|\beu\b|europe", t):
        out["market"] = "export_EU"
    for pat, val in (
        (r"cold[- ]?press", "cold_pressed"),
        (r"expeller", "expeller"),
        (r"solvent[- ]extract", "solvent"),
    ):
        if re.search(pat, t):
            out["process.oil_route"] = val
            break
    if re.search(r"\b(?:not|un)[- ]?stabili[sz]ed\b", t):
        out["process.stabilised"] = False
    elif re.search(r"\bstabili[sz]ed\b", t):
        out["process.stabilised"] = True
    m = re.search(r"(\d[\d,]*)\s*kg\s*(?:/|per|a)\s*day", t)
    if m:
        out["scale_kg_day"] = _num(m.group(1))
    m = re.search(r"(?:₹|rs\.?\s*)\s*(\d[\d,]*(?:\.\d+)?)\s*(?:/|per|a)\s*(kg|quintal|tonne|ton|t)\b", t)
    if m:
        out["raw_price_inr_per_kg"] = round(_num(m.group(1)) / UNIT_KG[m.group(2)], 4)
    return out

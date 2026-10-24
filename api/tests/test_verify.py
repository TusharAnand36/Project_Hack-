from api.llm.verify import extract, numbers_in, verify


def vals(text):
    return [f.value for f in extract(text)]


def test_extracts_indian_formats():
    assert vals("costs ₹1,00,000 per tonne") == [100000.0]
    assert vals("phytate is 12.5% here") == [12.5]
    assert vals("a range of 3–5 days") == [3.0, 5.0]
    assert vals("about 2 lakh rupees, or 1.5 crore") == [200000.0, 15000000.0]
    assert vals("margin −4,075") == [-4075.0]
    assert vals("gate G1 and AFB1 under N x 6.25") == [6.25]  # ids are not numbers


def test_matches_at_displayed_precision_and_percentages():
    allowed = numbers_in({"p": 0.531, "cost": 192.4, "evsi": 151823.0, "s": "limit 30 ppb"})
    assert verify("P(fail) is 53% and cost ₹192; the limit is 30 ppb", allowed, set()).ok
    assert verify("worth about 1.52 lakh", allowed, set()).ok
    assert not verify("cost ₹777 per kg", allowed, set()).ok  # GT7-style injection


def test_rejects_unknown_sources():
    allowed = {1.0}
    assert not verify("as shown by smith_2021", allowed, {"murugeswari_2023"}).ok
    assert verify("as shown by murugeswari_2023", allowed, {"murugeswari_2023"}).ok

# Pitch deck content: 4 minutes

Copy this into the **official template**. Each slide gives the on-screen text (keep it short), the speaker notes (what to say) and a time budget. The total is 4:00. One person speaks; one person drives the demo.

The source plan's §18.1 was written for an earlier engine. This version matches the build at engine 0.8.0 / dataset 2026-10-25.1:

- The lead demo is **sunflower cake → Protein Rich Flour**, not groundnut. Target names were renamed in `e74f6aa` (Protein Isolate, Protein Rich Flour, Protein Concentrate); IDs and the underlying profiles are unchanged.
- P(GO), Pareto break-even and the EVPPI "tornado" are **not shown**. The build withholds them until it has calibrated inputs. Do not promise them on stage.
- Every number below can be traced to the app, `data/sources.json` or the snapshot `web/public/snapshots/sunflower_snack.en.json`.

---

## Slide 1: Problem and stake (0:00–0:30)

**On screen**

> India imports about **90%** of its plant-protein ingredients.
> Oilseed cakes are made here every day and mostly sold as feed.
> A mill or brand has no fast, honest way to ask: *can this batch become food protein?*

Small print: PBFIA via Agron Food Processing; GFI India.

**Say**

"Indian plant-protein brands import roughly nine-tenths of their protein ingredients, mostly pea isolate. That import is exposed to the exchange rate and to anti-dumping action: the EU and Canada have both acted on Chinese pea protein. Meanwhile oilseed cake, the solid left after pressing oil, is sold as cattle feed. The problem is not a lack of protein. It is that nobody can quickly tell a mill owner whether *this* batch is safe, what it would cost, and what to test first."

> Do **not** say ">25 Mt of oilseed cake a year". There is no source for it in `sources.json`. Add it only after checking it on FAOSTAT and adding the row.

---

## Slide 2: The decision and the gap (0:30–1:00)

**On screen**

> **One batch. One target use. One honest answer.**
> GO / NO-GO / TEST-FIRST, with separate verdicts for safety, technical fit, cost and evidence quality.
>
> - Safety is usually a footnote. Here it is the first gate.
> - Treatments are studied one at a time. Here they are combined into candidate routes.
> - Cost is quoted per kg of product. Here it is **₹ per kg of protein**, against landed pea isolate.
> - Labs measure everything. Here the tool says what to test **first**.

**Say**

"Existing AI food platforms look for new molecules. We do something plainer and more useful for India: take a commodity by-product batch and a target product, and say Go, No-go or Test-first. The answer is split into four parts (safety, technical fit, economics and evidence quality), so a good price can never hide a safety gap. Most importantly, when we don't know, we say so, and we tell you which test would change the answer."

---

## Slide 3: Live demo (1:00–2:30, 90 s)

**On screen:** the app (live, or the stamped offline snapshot). Driver follows `DEMO_SCRIPT.md`. Three beats:

1. **Sunflower cake → Protein Rich Flour → TEST-FIRST** (about 30 s)
   - Show the four dimensions: safety needs verification, technical needs validation, economics not calculable, evidence hypothesis-grade.
   - Show the seven contaminant checks. None is measured, so there are no fake bars.
2. **Evidence, not guesses** (about 30 s)
   - The Diagnosis functional table: cake flour vs extracted isolate vs pea study, 8 properties, no invented winner.
   - Cost: pea isolate landed at about **₹518 per kg protein** (P10–P90 ₹431–619, an *assumed* scenario). Our own cost is "not calculable" until yields and prices are measured.
3. **One lab number changes the answer** (about 30 s)
   - Next → enter lead **1.6 mg/kg** (project limit 1.0) → **NO-GO**, with a before/after table.
   - Say it: a *low* lead result (0.4) keeps TEST-FIRST, because one passed test does not clear the other gates.

**Say (speaker, while the driver clicks)**

"Here is a real use: sunflower cake, to make a protein-rich flour. The answer is Test-first, and the screen says exactly why: aflatoxin, metals, hexane, food-grade records and regulatory review are all unmeasured. It does not draw a bar for a number it doesn't have. On cost, imported pea isolate lands at about five hundred rupees per kg of protein in our scenario. We do not claim to beat it until yields and quotes are measured. Now the lab sends one result: lead at 1.6 mg/kg. The verdict flips to No-go, with the before and after side by side. That is the loop: measure, update, decide."

---

## Slide 4: How it works (2:30–3:05, 35 s)

**On screen** (diagram)

```
batch + target use
   → safety gates G1–G7 (measured evidence only)
   → diagnosis (what blocks this use)
   → candidate routes (extrusion, phytase, alkaline extraction + isoelectric precipitation, combinations)
   → mass balance and ₹/kg protein vs landed pea
   → readiness + the next test + a 6-month validation plan
Every number: measured | published | assumed | synthetic, with source and grade
AI: parses your text and explains the result; it cannot change a number
```

**Say**

"Under the hood is a Python engine, not a chatbot. It applies safety gates first, then looks at which treatment routes the evidence supports for this material, then computes protein mass balance and cost per kg of protein. Every number carries a tag: measured, published, assumed or synthetic, with its source. The language model only turns your description into a form and writes a plain summary. A verifier rejects any sentence containing a number the engine didn't produce, and if the model is unavailable we fall back to a fixed template."

---

## Slide 5: Honesty and limits (3:05–3:25, 20 s)

**On screen**

> - This is a decision-support prototype, **not** a regulatory approval. Contaminant limits are our project settings, to be reviewed.
> - The dataset ledger is public: **161 missing, 41 assumed, 37 to verify**.
> - Most cases say TEST-FIRST today. That is correct, not a bug.
> - First things to validate: lot assays (aflatoxin B1 + total, metals, hexane), measured yield, and matched pea-vs-cake functional tests.

**Say**

"We are strict about limits. This is not food-safety approval. Our dataset openly lists 161 missing values, and that is why most answers today are Test-first. The tool is useful precisely because it shows what's missing and what to measure next."

---

## Slide 6: Six-month plan and ask (3:25–4:00, 35 s)

**On screen** (from the app's plan, `/plan`)

| Months | Work | Output |
|---|---|---|
| 0–1 | Source 3–5 lots from food-grade mills; safety assays | Gate decisions on real lots |
| 1–3 | Bench trials of up to two supported routes; before/after assays | Measured replaces transferred evidence |
| 3–4 | Sensory panel; solubility, emulsifying, gelation | Functional fit for the target product |
| 4–5 | Pilot run (≈ 10 t cake) with a contract processor or institute | Real yield, energy, water |
| 5–6 | Re-run with measured data; customer samples; regulatory check | ₹/kg protein vs pea on real data |

> **Budget:** not yet computable; needs NABL lab quotes (the tool says so).
> **We need:** a food-grade oil mill, an accredited lab, and a brand to test samples.

**Say**

"The tool writes its own six-month plan, starting with safety assays on three to five real lots and ending with a pilot run and a cost comparison on measured data. We won't put a budget on this slide until we have lab quotes, and the tool won't either. What we need is a food-grade mill, an accredited lab, and a brand willing to test samples. Thank you."

---

## Slide 7: References (not timed)

Use `REFERENCES.md`. Every link must be clickable in the exported PDF.

---

## Video slide

Attach the ≤ 2-minute screen recording (`DEMO_SCRIPT.md`, part A) on slide 3 or as a separate slide, as the template allows. If the live demo fails, play the video.

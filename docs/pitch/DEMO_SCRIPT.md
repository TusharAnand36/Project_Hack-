# Demo script, video script and rehearsal log

Plan deadlines (website plan, Phase 9):

- official template arrives by 10 PM;
- video recorded **before 3 AM**;
- deck PDF submitted by **7:30 AM**.

## Setup (demo laptop, 10 minutes before)

1. Charge the laptop.
2. Start a **fresh, disposable feedback database**, so rehearsal clicks don't seed real cases:
   ```bash
   export FEEDBACK_DB_PATH=$PWD/.runtime/demo-$(date +%H%M).sqlite3
   make api        # Bedrock if AWS_PROFILE/BEDROCK_MODEL_ID are set; template otherwise
   make web        # http://localhost:5173/#/compass
   ```
   On Windows, follow the PowerShell steps in `PROJECT_OVERVIEW.md` §18 with `$env:FEEDBACK_DB_PATH` set.
3. Browser:
   - zoom 125%;
   - close other tabs;
   - turn notifications off;
   - language **English**.
4. Fallback check: stop the API once and confirm a preset still loads with "Demo snapshot (offline)". Then start it again.
5. Open the recorded video in a second window, ready to play if the live demo fails.

## A. Video: ≤ 2 minutes (record first; re-record only if time allows)

Record the browser window at 1280×800 or larger, with the narration over it. Target 1:50.

| Time | Screen and click | Narration |
|---|---|---|
| 0:00 | Home page (`/#/`) | "Upcycle Compass helps a mill or brand decide whether one by-product batch can become a food protein, for one target product." |
| 0:08 | **Open Compass** → One-click presets → **Sunflower cake → Protein Rich Flour** → **Analyse** | "Sunflower cake, to make a protein-rich flour." |
| 0:15 | **Verdict**: TEST-FIRST, hypothesis grade; point to the four dimensions | "The answer is Test-first. Safety needs verification, technical fit needs validation, economics can't be calculated yet, and the evidence is hypothesis-grade." |
| 0:30 | Scroll to the seven contaminant checks | "Aflatoxin B1 and total, lead, cadmium, arsenic, mercury and hexane: all unmeasured. So no bars are drawn; we don't invent a number." |
| 0:42 | **Diagnosis** → the functional comparison table | "Eight functional properties: cake flour, extracted isolate and the pea-isolate study side by side, with their conditions. No winner is declared, because these aren't head-to-head experiments." |
| 0:58 | **Chains** | "Nine evidence-backed routes (extrusion, phytase, alkaline extraction and combinations), shown as hypotheses to test, not a ranking." |
| 1:08 | **Cost** | "Imported pea isolate lands at about ₹518 per kg of protein in this scenario. Our own route cost stays 'not calculable' until yields and prices are measured." |
| 1:20 | **Next** → Enter your lab result → *What was measured:* Lead → *Measured value:* **1.6** mg/kg, as received, method ICP-MS → **Update the analysis** | "Now a lab result arrives: lead at 1.6 milligrams per kilo, against our limit of 1.0." |
| 1:35 | The Before / After table: **TEST-FIRST → NO-GO** | "The verdict flips to No-go, with before and after side by side. One measured number changes the decision." |
| 1:45 | **Decision memo (print / PDF)** | "And the team gets a one-page memo with sources and limits. Measure, update, decide." |
| 1:50 | End | |

Rules for the video:

- Real clicks only, no editing tricks.
- If the API is offline during recording, it is fine to show the stamped snapshot. The lab update needs the live API.

## B. Live demo during the pitch (90 s, slide 3)

Same click path as the video, but shorter:

1. Preset → Verdict (four dimensions, contaminant checks).
2. Diagnosis table → Cost (₹518 pea).
3. Next → lead 1.6 → NO-GO.

**If asked**, show the contrast: lead **0.4** stays TEST-FIRST, because other gates are still open. Checked against the API on 2026-10-25: 1.6 → NO-GO; 0.4 → TEST-FIRST.

**If the lab form asks for a lot ID**, use the one on the preset or leave it blank. A mismatched lot ID is rejected on purpose. Rehearse this step.

## C. Rehearsal log (do it twice, with a timer)

One person drives, one speaks. Use `SLIDES.md` timings. Stop at 4:00 even if unfinished, and note where you were.

| Run | Date/time | Total time | Over/under per slide | What went wrong | Fix |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |

Then run a Q&A drill: one person reads 8 random questions from `QA.md`, and the other answers each in under 20 s.

## D. Submission checklist

- [ ] `Upcycle_Compass_Pitch.pptx` (already on the official template): TEAM and MEMBERS filled in on slide 1; video attached on slide 5.
- [ ] References slide from `REFERENCES.md`; the Bedrock **model id** filled in; organiser datasets labelled "listed, no values drawn yet".
- [ ] Every link in the **exported PDF** clicked once.
- [ ] Repository link: the repo is **private**. Make it public before submission, or remove the link (the jury cannot open a private repo).
- [ ] Video ≤ 2:00 attached in the deck and played once from the exported file.
- [ ] No claims without a source on the slides. ">25 Mt oilseed cake" is **not** on the slides unless checked on FAOSTAT.
- [ ] Deck PDF submitted by 7:30 AM.
- [ ] Demo laptop charged; offline snapshots load with the API stopped (`cd web && npm run e2e:offline`).

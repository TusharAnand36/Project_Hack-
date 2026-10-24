# Upcycle Compass

For one food by-product batch and one target use, Upcycle Compass answers **Go / No-go / Test-first**. It also says:

- which supported treatment candidates need testing;
- what can be costed per kg of recovered protein against a defined pea-isolate scenario;
- which critical evidence to collect before a pilot decision.

Every number carries a provenance tag: `measured`, `published`, `assumed` or `synthetic`.

> **Proof of concept, Hack the Fork 2026 (Problem Statement 2).** Decision support only. Not a regulatory approval. Confirm FSSAI classification and limits.

**Status:** Evidence-aware prototype, engine 0.8.0. The final workflow audit,
current validation results and outstanding scientific/deployment work are in
[`docs/FINAL_WORKFLOW_AUDIT.md`](docs/FINAL_WORKFLOW_AUDIT.md).
`docs/PHASES.md` records the earlier implementation history. The pitch package
(slides, references, Q&A sheet, demo and video script) is in [`docs/pitch/`](docs/pitch/README.md).

The website opens on a public home page with About us, Our mission, and How it works pages.
Choose **Open Compass** to enter the decision tool, or open `/#/compass` directly.
Both the public pages and the tool support English and Hindi. Design and image-source notes are in
[`docs/WEBSITE.md`](docs/WEBSITE.md).

The five presets are **sunflower cake** (first), groundnut cake, soybean cake, almond cake,
and pea protein isolate. Rice bran is no longer offered as an analysable material.
The displayed target names are **Protein Isolate**, **Protein Rich Flour** and
**Protein Concentrate**, replacing Beverage, Bakery/snack and Meat analogue respectively.
Preset cards, the target selector, homepage example and memo use these names.
Existing application IDs and scientific profiles remain unchanged for compatibility;
selecting a target does not certify that the resulting ingredient meets that classification.
Sunflower and soybean composition is cited to the team's final oilseed review; missing
purchase prices remain blank for a supplier quote.

Pea isolate uses the supplied Qi et al. (2025) paper's **80.2% protein** value
([DOI](https://doi.org/10.1016/j.fochx.2025.102898)). Its gellan-gum/salt findings are
qualitative formulation guidance, not simulated extraction or anti-nutrient treatments.
The paper gives no price: every preset uses the same existing market-price model and
shared pea settings, with IGST-credit duty mode as the default scenario. The Cost screen
distinguishes ₹/kg of isolate from ₹/kg of protein; an explicit supplier quote overrides
the isolate's purchase cost. Historical source documents retain their original scope.

The Verdict and Diagnosis screens use these **user-specified project contaminant thresholds**:

| Contaminant | Maximum |
|---|---|
| Hexane residue | 10 mg/kg (10 ppm) |
| Aflatoxin B1 | 10 µg/kg (10 ppb) |
| Total aflatoxins, B1+B2+G1+G2 | 15 µg/kg (15 ppb) |
| Lead | 1.0 mg/kg |
| Cadmium | 0.1 mg/kg |
| Total arsenic | 0.5 mg/kg |
| Mercury | 0.1 mg/kg |

These are project acceptance settings, applied to all materials and both market scenarios;
they are not independently verified regulatory limits. Arsenic is interpreted as total
arsenic in mg/kg. Enter the batch report under **Contaminant lab results**. An entered
measured value on the compatible as-received basis at or below its threshold passes that check; an exceedance fails the safety gate;
missing results require testing. Both B1 and total aflatoxins must pass. A hexane
certificate checkbox alone cannot override a high or missing quantitative result;
documented non-solvent processing clears that route's hexane check without an assay.
The older 20-ppb groundnut survey prior is not used to infer compliance at 10 ppb.
Form labels no longer show provenance/default badges; result provenance remains available.

## What it does

| Screen | Answers |
|---|---|
| Input | By-product, target use, batch values (form, sample text or voice; English or Hindi) |
| Verdict | Go / No-go / Test-first, with separate safety, technical, economic and evidence status |
| Diagnosis | Compatible measured exceedances, missing assays, and functional comparisons with pea isolate |
| Chains | Supported research candidates, mass-balance evidence, missing process data and partial costs |
| Cost | ₹/kg recovered protein against the landed pea scenario, target formula and cost boundary |
| Next | Critical tests, unestimated economic VOI, proposed six-month validation plan, lab-result update |
| Memo | Printable decision memo, traceable sources and matching case JSON export |

P(GO), P(spec), margin probabilities and economic VOI are **not estimated** without
a calibrated model. Missing yields/recoveries do not produce simulated performance
predictions. References are not batch assays, and raw flour is not an extracted isolate.
The default demo therefore returns **TEST-FIRST**, rather than a commercial promise.

Each live analysis gets a fresh case ID and a feedback form. Feedback is saved to
SQLite locally and future matching queries receive aggregate issue counts and
follow-up suggestions. It never changes safety thresholds or verified assays.
For hosted persistence, configure `FEEDBACK_DB_PATH` on a persistent disk; see
[`docs/DEPLOY.md`](docs/DEPLOY.md). Offline snapshots cannot save feedback.

## Architecture

```
browser (React 18 + TS + Vite + Tailwind)
  │  /api/*  (Vite proxy locally, Vercel rewrite when deployed)
  ▼
FastAPI  api/main.py   /health /presets /data/* /analyze /feedback /update-evidence /explain /plan /parse-text
  │                    LRU cache · 64 KB body limit · 10/min/IP on AI endpoints
  ├── engine/compass/  pure Python decision engine (no web or LLM imports)
  │     data → sampling (Sobol QMC, 8,192 draws, seed 42) → effects → gates G1–G7 → diagnosis
  │     → candidate chains → supported mass balance / cost → evidence-aware assessment → readiness → plan
  ├── api/feedback.py  SQLite case feedback + lab-update history; scoped aggregate follow-up suggestions
  └── api/llm/         Bedrock → Groq → template; every AI sentence passes the number verifier
data/*.json            dataset with tag, grade, source and applicability on every value
web/public/snapshots/  precomputed preset results for the offline fallback
```

- **The AI layer cannot change an engine number.** It only rewords the engine's JSON. Any number the verifier cannot find in that JSON makes the server fall back to the template text. See `docs/AI.md`.
- **Offline fallback.** If `/analyze` fails or takes longer than 8 s, the web app loads the preset snapshot and shows "Demo snapshot (offline)" with the engine and dataset version stamp.

## Layout

```
data/                 JSON datasets; schema/ (generated JSON Schemas); _staging/ (unreviewed rows, never read)
engine/compass/       models, data, sampling, effects, flavour, cost, pea, gates, diagnosis, chains,
                      montecarlo, voi, pareto, readiness, plan, update, learning, analyze, contract
  tests/              pytest + hypothesis; golden tests GT1–GT8; regression snapshot
api/                  FastAPI app, schemas, llm/ (client, prompts, verifier, template, rule parser)
web/src/              api/ (client, generated types), screens/, components/, charts/ (plain SVG),
                      locales/ (en, hi, glossary, review status), hooks/ (voice, read-aloud)
web/e2e/              Playwright journeys + axe (run.mjs), Wi-Fi-off rehearsal (offline.mjs)
web/public/           snapshots/, offline-data/, open-data-pack.zip (generated by `make snapshots`)
scripts/              build_snapshots.py, bench_engine.py, gen_types.sh
docs/                 source plan, website plan, PHASES.md, AI.md, DEPLOY.md, voice-tests.md,
                      pitch/ (Phase 9), screenshots/, reports/ (Lighthouse)
```

## Run

You need Python 3.11+ and Node 20+.

```bash
make setup        # venv + pip install + npm ci (once)
cp .env.example .env
make api          # http://localhost:8000  (OpenAPI docs at /docs)
make web          # http://localhost:5173
```

On Windows (PowerShell), use Python 3.11–3.13 for the pinned dependencies:

```powershell
uv venv --python 3.13 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements-dev.txt
cd web
npm.cmd ci
cd ..
$env:PYTHONPATH = "engine;."
$env:LLM_PROVIDER = "template"
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8001
```

In a second PowerShell terminal, from the repository folder:

```powershell
$env:API_PROXY_TARGET = "http://127.0.0.1:8001"
cd web
npm.cmd run dev -- --host 127.0.0.1
```

Open http://127.0.0.1:5173. Port 8001 avoids conflicts with another API on 8000.
The Windows setup uses [uv](https://docs.astral.sh/uv/) to install a compatible Python.

Other targets:

```bash
make test         # pytest + vitest + locale check + web build
make e2e          # Playwright journeys + axe scan (API and web running)
cd web && npm run e2e:offline   # "Wi-Fi off" rehearsal: built app, no API
make snapshots    # regenerate offline snapshots, offline data and the open data pack
make types        # regenerate web/src/api/types.ts from the running API's OpenAPI schema
make bench        # engine timing
make lint
make data         # dataset report: counts by tag and grade, missing inputs per preset
make todo         # regenerate DATA_TODO.md and data/schema/
```

AI text:

- With no LLM configured (`LLM_PROVIDER=template`, the default), every summary is the deterministic template.
- For Bedrock, set `AWS_PROFILE` and `BEDROCK_MODEL_ID` in `.env`.

Deployment (Vercel and Render, with a keep-alive ping) is described in `docs/DEPLOY.md`.

## How to regenerate snapshots

Run this after any change to the engine, the data or the presets:

```bash
make snapshots    # runs /analyze and the template /explain for each preset × {en, hi}
make test
```

It writes the following and stamps each one with `engine_version`, `dataset_version` and `generated_at`:

- `web/public/snapshots/<preset>.<lang>.json` and `.explain.json`
- `web/public/snapshots/presets.json`
- `web/public/offline-data/` (form options for offline use)
- `web/public/open-data-pack.zip`

Commit the regenerated files.

## Data labels

| Tag | Meaning |
|---|---|
| **M** measured | From the user's own batch or a lab result entered in the app |
| **P** published | From a cited source (team documents or the organiser's open datasets) |
| **A** assumed | A stated assumption: a team estimate or a value transferred from a similar material |
| **S** synthetic | A placeholder distribution, used only so the pipeline runs; never presented as a result |

- **Grades.** Each value has an evidence grade from A (strong) to D (weak).
- **Applicability α.** Evidence transferred from another material carries α. The extrapolation penalty 1 + k(1 − α) widens its range.
- **Derived numbers** take the weakest tag and grade of their inputs.
- **Missing values** are `null` and listed in `DATA_TODO.md`. Costs that depend on a missing value are shown as labelled lower bounds.
- **Sources** are limited to the team's documents and the organiser's resources:
  - FAOSTAT
  - IFCT 2017
  - USDA FoodData Central
  - FooDB
  - Open Food Facts
  - AGMARKNET
  - data.gov.in mandi prices
- **Unpublished data.** Unpublished team data, such as the PhD proximate report, is not used without the owner's permission and is not committed.
- **Open data pack.** The footer links to the data pack: all `/data` files, `sources.json`, schemas, `DATA_TODO.md` and a licence note. The team has not chosen a licence yet.

## Limitations

- **Hypothesis-grade results.** Many process parameters are still `synthetic` or `assumed`, so most verdicts are hypothesis-grade. TEST-FIRST is the expected answer until lab results are entered.
- **Missing raw prices.** Several presets have no raw-material price, so cost per kg protein is not computable there, or is shown as a lower bound.
- **Hindi.** The Hindi UI strings were drafted by the coding assistant and have not been reviewed by a Hindi reader. Safety wording (verdict labels, gate states, disclaimers) stays in English until it is reviewed.
- **Voice input.** Voice input is unit-tested with a mocked recogniser. It has not been tried with a real microphone on Chrome Android or Safari iOS (`docs/voice-tests.md`).
- **Accessibility.** The axe scan shows 0 serious or critical issues on every screen, and the keyboard walk-through passes. A manual screen-reader pass (NVDA or VoiceOver) has not been done yet.
- **No regulatory decision.** FSSAI and EU limits in the dataset are reference values; confirm them before use.
- **Known dependency advisory.** `zod` 3.24.1 has GHSA-mrhx-c7xc-m3w5: memory exhaustion when validating oversized collections. We accept this for the prototype:
  - zod runs only in the browser, on the app's own input form;
  - the form's arrays are bounded checkbox lists;
  - the fix is a breaking major (zod 4) released less than two weeks ago.
  - Upgrade to zod 4 together with `@hookform/resolvers` after the hackathon.

## AI tools used

- **Building the code.** An AI coding assistant (Claude Code) wrote and tested the code phase by phase from `docs/Website_Development_Master_Plan.md`. The team reviewed and committed it.
- **Runtime summaries.** At runtime the optional LLM layer uses Amazon Bedrock, with Groq as an alternative, to reword the engine's results and to parse free text. The deterministic engine makes every decision. Every LLM sentence is checked by the number verifier, and the template is the fallback.

## Rules for contributors

- **No secrets.** Never commit secrets. `.env` and `.aws/` are git-ignored. Credentials come only from the environment or a local AWS profile.
- **No invented numbers.** Missing data stays `null` and gets a line in `DATA_TODO.md`.
- **Tags on every output.** Every numeric output carries a `tag`, plus `grade`, `source_ids` and `alpha` where they apply.
- **Regenerate after changes.**
  - After any API change, run `make types` and commit the regenerated `types.ts`.
  - After any engine or data change, run `make snapshots`.

The science and engine specification is `docs/Upcycle_Compass_Master_Prompt.md` (source plan v2).

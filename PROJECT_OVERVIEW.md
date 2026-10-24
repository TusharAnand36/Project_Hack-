# Upcycle Compass — Project Overview, Current Build and Roadmap

**Document date:** 25 October 2026  
**Repository:** [TusharAnand36/Project_Hack-](https://github.com/TusharAnand36/Project_Hack-)  
**Implementation baseline:** [`911fe7c`](https://github.com/TusharAnand36/Project_Hack-/commit/911fe7c9bb1011e3ae09cabbfc9f5ba49445c326)  
**Engine version:** `0.8.0`  
**Dataset version:** `2026-10-25.1`  
**Current stage:** Working, tested research and decision-support prototype

This document explains what we are building, why it matters, what is already implemented, how the repository works, and what is required to turn the prototype into a validated product. It is an onboarding document for a developer, researcher, collaborator or presentation reviewer joining the project.

The repository name is `Project_Hack-`; the product name shown on the website is **Upcycle Compass**. The latest implementation baseline was authored and committed as **Utkarsh Raj**. Repository ownership and commit authorship are separate: the GitHub repository is hosted under `TusharAnand36`.

## Contents

1. [Project in one paragraph](#1-project-in-one-paragraph)
2. [Problem and purpose](#2-problem-and-purpose)
3. [Mission, direction and intended users](#3-mission-direction-and-intended-users)
4. [What we are building](#4-what-we-are-building)
5. [What is already built](#5-what-is-already-built)
6. [Materials and applications](#6-materials-and-applications)
7. [Public website and design](#7-public-website-and-design)
8. [The six-step decision workflow](#8-the-six-step-decision-workflow)
9. [Safety and evidence rules](#9-safety-and-evidence-rules)
10. [Research and pea-isolate comparison](#10-research-and-pea-isolate-comparison)
11. [Protein, mass balance and cost calculations](#11-protein-mass-balance-and-cost-calculations)
12. [Case feedback and future queries](#12-case-feedback-and-future-queries)
13. [Laboratory updates](#13-laboratory-updates)
14. [AI and language support](#14-ai-and-language-support)
15. [Offline demo, memo and exports](#15-offline-demo-memo-and-exports)
16. [Architecture and technology](#16-architecture-and-technology)
17. [Repository map and API](#17-repository-map-and-api)
18. [Running the prototype locally](#18-running-the-prototype-locally)
19. [Verification and current quality](#19-verification-and-current-quality)
20. [What remains to be built or validated](#20-what-remains-to-be-built-or-validated)
21. [Development roadmap](#21-development-roadmap)
22. [Demo walkthrough](#22-demo-walkthrough)
23. [Working rules and supporting documents](#23-working-rules-and-supporting-documents)

## 1. Project in one paragraph

**Upcycle Compass helps a user assess one food by-product batch for one intended protein application.** It brings together material references, batch measurements, contaminant checks, candidate processing routes, functional properties, protein-cost calculations and next-test planning. The output is a reasoned **GO**, **NO-GO** or **TEST-FIRST**, with separate statements about safety, technical feasibility, economics and evidence quality. Its current purpose is to help a team choose a defensible next experiment or pilot step while making missing information visible.

The project was developed for **Hack the Fork 2026, Problem Statement 2: upcycling by-products for alternative proteins**. Its primary demonstration is **sunflower cake for an extruded high-protein/fibre snack**.

## 2. Problem and purpose

An oilseed cake can contain useful protein and other components, but protein percentage alone does not establish suitability for a food product. A potential user also needs to understand:

- The identity, origin, extraction route and handling history of the actual lot.
- Whether required contaminant and safety evidence is available.
- Which anti-nutritional or functional constraints are relevant to the intended use.
- Whether a proposed treatment has evidence for this material and processing context.
- How much ingredient and protein would actually be recovered.
- Whether the resulting ingredient can perform in a beverage, snack or meat analogue.
- What a kilogram of recovered protein costs within a comparable cost boundary.
- Which measurement would help resolve the next decision.

Research findings, supplier statements, laboratory results and commercial assumptions often describe different materials or conditions. Upcycle Compass organises them into one case while preserving those distinctions. It helps identify evidence gaps before a team treats a literature range or demonstration value as a result for its own batch.

## 3. Mission, direction and intended users

### Mission

Help teams explore higher-value food uses for suitable by-products through transparent evidence, clear calculations and practical validation steps.

### Product direction

The intended direction is a traceable decision workspace connecting material selection, research, laboratory work, pilot processing and commercial comparison. As verified evidence becomes available, the workspace can support stronger lot-specific decisions.

This direction is an ambition. The current prototype has not demonstrated a validated industrial optimum, proven environmental benefit, confirmed market adoption or guaranteed cost saving.

### Intended users

| User group | Intended use |
|---|---|
| Food researchers and students | Organise evidence, identify unknowns and plan experiments. |
| Product-development teams | Explore material/application fit and matched functional testing. |
| Mills and ingredient processors | Understand documentation, handling and processing evidence needed for a food-use investigation. |
| Startups and pilot teams | Compare candidate routes and identify missing technical or commercial inputs. |
| Laboratory and institute collaborators | Understand the case, required measurements and before/after decision changes. |
| Hackathon reviewers | Follow a reproducible demonstration with visible assumptions and limitations. |

These are target audiences, not a list of existing customers or confirmed partners.

## 4. What we are building

The product has two connected surfaces:

1. **A public website** explaining who we are, what the project does, its mission and how to use it.
2. **The Compass workspace** where a user enters a case and follows the decision process.

The workspace follows this sequence:

```text
Input → Verdict → Diagnosis → Chains → Cost → Next
                         ↓
             Decision memo and case JSON

Live analysis → case-specific feedback → observations for future matching cases
Laboratory result → before/after comparison → updated analysis
```

The website introduces the idea. The workspace exposes the reasoning and next actions behind an individual case.

## 5. What is already built

| Capability | Current implementation | Boundary |
|---|---|---|
| Public website | Home, About, Mission and How it works pages | Project introduction; no invented team credentials or partnerships. |
| Decision workspace | All six main screens and a memo screen | Research/pilot decision support. |
| Material presets | Five presets, with sunflower first | Reference coverage varies by material. |
| Batch entry | Structured form, editable text parsing and browser speech input | Parsed values require review; speech depends on browser support. |
| Traceability | Lot, supplier, origin, material form, route records and report metadata | Records are user-supplied, not independently authenticated. |
| Safety checks | Seven project contaminant thresholds, plus applicable provenance, regulatory and other gates | Internal project settings; no independent legal approval. |
| Diagnosis | Measured threshold comparisons, missing-evidence explanations and functional references | Unsupported ratios and uncalibrated probabilities stay unavailable. |
| Candidate routes | Applicable routes with study conditions, source context and missing inputs | Research candidates are not validated industrial rankings. |
| Cost comparison | Recovered-protein cost where calculable, shared pea scenario and three target methods | Missing process costs prevent a full economic claim. |
| Functional comparison | Eight property categories separating cake flour, extracted isolate and pea-study evidence | Cross-study differences do not establish a head-to-head winner. |
| Next-test planning | Critical tests, readiness checks and proposed six-month plan | Economic VOI needs additional calibrated data. |
| Laboratory update | Unit/lot validation and before/after results | A compatible prior is required for a Bayesian update. |
| Feedback database | Persistent local SQLite cases, feedback and lab history | Hosted durability requires configured persistent storage. |
| Future-query feedback use | Matching-case aggregate observations and follow-up suggestions | Feedback does not retrain a predictive model or change safety limits. |
| Memo and exports | Printable memo, case JSON and downloadable data pack | Arbitrary long memos may print over multiple pages. |
| Offline demonstration | Five precomputed presets in English and Hindi | Preset snapshots, not arbitrary offline batch computation. |
| Verification | Backend/frontend tests, lint, build and recorded browser checks | Software checks do not establish experimental validation. |

## 6. Materials and applications

### Current presets

| Order | Material | Preset application | Preset ID |
|---|---|---|---|
| 1 | Sunflower cake | Extruded high-protein/fibre snack | `sunflower_snack` |
| 2 | Groundnut cake | Beverage protein | `groundnut_beverage` |
| 3 | Soybean cake | Meat analogue | `soybean_meat` |
| 4 | Almond cake | Meat analogue | `almond_meat` |
| 5 | Pea protein isolate | Beverage protein reference | `pea_beverage` |

The form supports beverage, extruded snack and meat-analogue target applications. Rice bran was removed from the active analysable materials because the project did not have the required supporting paper for that path.

Pea isolate serves both as a selectable reference material and as the shared commercial comparison. It is an already-produced ingredient; the application does not simulate oil-cake extraction for it.

Material availability in the interface does not mean all its composition, treatment or functional data is complete. Unsupported values remain missing.

## 7. Public website and design

### Pages

| URL path | Purpose |
|---|---|
| `/#/` | Introduce the project, intended audiences, process and evidence approach. |
| `/#/about` | Explain the project background, approach and principles. |
| `/#/mission` | Describe the mission, commitments and future direction. |
| `/#/how-it-works` | Explain the user journey and answer common questions. |
| `/#/compass` | Open the working decision tool. |

Hash navigation supports these pages on static hosting.

### Visual system

The public pages and prototype workspace share an ivory background, forest-green accents, editorial typography and consistent cards, controls and tables. The workspace was updated to match the homepage design rather than retaining the earlier dark interface.

The implemented interaction design includes responsive layouts, desktop navigation, mobile bottom navigation, visible focus states, skip links and focus transfer on screen changes. Decorative motion uses opacity and transforms; reduced-motion preferences disable it. The main conceptual hero image is an AI-generated illustration of ingredients, not a photograph of a project facility or real batch.

Single-letter `A` and `default` badges were removed from form labels. Result values still retain readable provenance and evidence details.

## 8. The six-step decision workflow

### Step 1 — Input

The user selects a preset or describes an actual batch and target use. The form can record:

- Material, intended application, market scenario and daily processing scale.
- Material form, lot ID, supplier, origin and dehulling information.
- Extraction route and supporting supplier/process records.
- Food-grade handling/storage information and review references.
- Protein, moisture, fat, ash, fibre and relevant compound/contaminant results.
- Assay basis, method, laboratory, report reference and date.
- Raw-material price, price unit, quote source/date and delivery boundary.
- Required protein, commercial cost target and relevant sensory/phytate targets.
- Available equipment, solvent constraints and excluded treatments.

Users can type a description or use browser speech recognition to draft the form. They review the parsed information before analysis. Unknown values should remain blank; a reference default is not reclassified as a measurement.

### Step 2 — Verdict

The result uses three labels:

| Verdict | Meaning in this prototype |
|---|---|
| `TEST-FIRST` | Required evidence is unresolved or insufficient for the next decision. |
| `NO-GO` | A relevant failed gate or incompatible claim blocks the proposed path. |
| `GO` | Recorded evidence supports the next controlled pilot step within its declared scope. |

A GO is not regulatory approval or proof of industrial performance. The screen separates **safety readiness**, **technical feasibility**, **economic feasibility** and **evidence quality**, and explains the reasons and next actions.

### Step 3 — Diagnosis

Diagnosis identifies constraints relevant to the material and application. It distinguishes contaminant gates, anti-nutritional concerns, protein-density questions, allergens and functional validation needs.

Measured level-to-threshold ratios require compatible units and basis, a positive justified threshold and applicable evidence. Missing measurements do not become zero bars. A point estimate does not become a 0% or 100% exceedance probability.

The screen also contains the oilseed-versus-pea functional comparison and an expandable research-evidence explorer.

### Step 4 — Chains

The tool lists supported baseline and treatment candidates, subject to material applicability and user constraints. Candidate detail includes treatment steps, relevant study conditions, sources, equipment needs and unresolved inputs.

Where supported, ingredient yield, recovered protein, final concentration and cost can be shown separately. Missing yield or recovery prevents a fabricated prediction. Current evidence-only candidates are unranked, and an unsupported Pareto optimum is not presented.

The treatment dataset includes routes such as extrusion, phytase treatment and alkaline extraction with isoelectric precipitation. Inclusion in the dataset does not make every route applicable to every material.

### Step 5 — Cost

The Cost screen distinguishes price per kilogram of ingredient from cost per kilogram of protein. It shows the declared commercial target and its formula, the shared illustrative landed-pea benchmark, and calculable costs or missing components for the selected case.

Price, freight, exchange-rate and duty settings are scenarios. They are not a live supplier-quotation or customs-verification service. Partial costs are labelled; changing a commercial cap does not change contaminant diagnosis or safety status.

### Step 6 — Next

Next identifies required safety evidence, relevant laboratory work, decision readiness and a proposed six-month validation programme. Safety-critical testing is separate from economic value-of-information ranking.

The user can enter a traceable lab result and inspect before/after effects. Where previous matching cases reported an issue, the screen can suggest an additional check such as measuring yield or running a matched texture test.

## 9. Safety and evidence rules

### Internal project contaminant thresholds

The following are the user's project acceptance settings in the implementation. They are **not independently verified regulatory limits**. Applicability to a real food category and intended use needs qualified review.

| Analyte | Project maximum |
|---|---|
| Hexane residue | 10 mg/kg, equivalent to 10 ppm |
| Aflatoxin B1 | 10 µg/kg, equivalent to 10 ppb |
| Total aflatoxins, B1+B2+G1+G2 | 15 µg/kg, equivalent to 15 ppb |
| Lead | 1.0 mg/kg |
| Cadmium | 0.1 mg/kg |
| Total arsenic | 0.5 mg/kg |
| Mercury | 0.1 mg/kg |

Both B1 and total-aflatoxin checks must pass. A certificate checkbox cannot override a missing or excessive quantitative residue result. A documented non-solvent route can establish that the corresponding hexane test is not required for that route. Unknown process history requires verification.

Contaminant comparison uses the compatible as-received basis. Assumed or synthetic contaminant inputs cannot clear a safety gate. Food-grade provenance and regulatory/intended-use review remain separate requirements; a low production cost cannot override them.

### Provenance

| Tag | Meaning |
|---|---|
| `measured` | An entered batch or laboratory result. |
| `published` | A cited source reference, within that source's scope. |
| `assumed` | A declared scenario or modelling assumption. |
| `synthetic` | Artificial demonstration or test data. |

Evidence grades, source identifiers and applicability metadata accompany relevant values. A measured tag records the origin of an entered result; the prototype does not independently authenticate the submitter or laboratory.

### Missing and uncertain data

- Missing values remain `null` or explicitly unavailable.
- A literature range is not a current-lot assay.
- Unknown does not mean safe, failed, zero or free.
- Missing mass yield/recovery is not filled with an arbitrary uniform prediction.
- Raw flour is not automatically classified as a concentrate or isolate.
- TIA normalised to raw activity is not treated as a measured activity assay.
- Phytate comparison requires an explicit justified internal dry-basis target.
- P(GO), P(spec), margin probabilities and economic VOI remain unestimated without a suitable calibrated model.

## 10. Research and pea-isolate comparison

### Resources integrated

The current build uses the project's final coding-agent handoff, build/presentation playbook, research evidence matrix, final oilseed review, earlier review drafts, research plan and the supplied pea-isolate paper. Preliminary LoR/proximate evidence was examined but is withheld from production predictions pending appropriate sample identity, basis and permission.

The structured research matrix contains **75 contextual records**. Review data is identified as secondary/review-reported where primary papers have not been independently checked. Overlapping drafts are not counted as independent experiments.

### Functional properties shown

The comparison covers:

1. Water absorption capacity.
2. Oil absorption capacity.
3. Foaming capacity.
4. Foam stability.
5. Emulsifying activity index.
6. Emulsion stability.
7. Least gelation concentration.
8. Protein solubility.

It has separate columns for **whole-cake flour**, **extracted oilseed isolate** and **the pea-isolate study**. Material form, assay conditions, units and duration matter. An emulsion result measured after 30 minutes cannot be treated as the same experiment as a 24-hour result.

The supplied paper, [Qi et al. (2025), *Modulating the functional properties of pea protein isolate*](https://doi.org/10.1016/j.fochx.2025.102898), supplies the **80.2% protein** reference and evidence about gellan gum/sodium chloride formulations. It does not supply a purchase price, oil-cake extraction yield or detoxification performance.

Relative improvements in that study are not absolute property values. Where a property is absent from the paper, the comparison says it was not reported. The interface does not claim a universal winner between pea and oilseed ingredients; it proposes matched assays for the intended application.

## 11. Protein, mass balance and cost calculations

### Protein and mass balance

```text
Initial protein mass = starting material mass × initial protein fraction

Recovered protein mass = final ingredient mass × final protein fraction

Protein retention (%) = recovered protein mass ÷ initial protein mass × 100

Final protein concentration (%) = recovered protein mass ÷ final ingredient mass × 100

Ingredient yield (%) = final ingredient mass ÷ starting material mass × 100
```

For an illustrative explanation only: 100 kg of material at 30% protein contains 30 kg protein. If an experiment produced 50 kg ingredient at 50% protein, it would contain 25 kg protein. Ingredient yield would be 50%, protein retention approximately 83.3%, and final protein concentration 50%. These are different quantities. This example is not a measured project result.

Crude protein retains its recorded laboratory factor. The engine does not apply a generic oilseed nitrogen factor to claim true or digestible protein. Dry-matter composition needs compatible moisture information before conversion to as-received mass or cost.

### Cost per kilogram of recovered protein

```text
Cost/kg recovered protein = relevant costs within the declared boundary
                            ÷ recovered protein mass
```

Relevant costs may include raw material, utilities, chemicals, labour, processing, drying/separation, QA, capital, logistics, packaging and waste handling. Only supported supplied components can be included. An incomplete result is a partial cost or lower bound, not validated total production cost.

### Maximum acceptable cost target

| Method | Formula |
|---|---|
| Manual | User-entered maximum acceptable ₹/kg recovered protein. |
| Benchmark discount | Pea benchmark cost/kg protein × (1 − required discount). |
| Finished-product budget | Allocated protein-ingredient budget per kg finished product ÷ kg protein required per kg finished product. |

Illustrative examples: a ₹600/kg-protein benchmark with a 20% required discount gives a ₹480 cap; a ₹25 budget for 0.10 kg protein per kg finished product gives a ₹250/kg-protein cap. These examples explain the arithmetic and are not supplier quotes.

### Shared pea benchmark

All presets use the same underlying pea settings unless the user changes the scenario. Protein cost is ingredient price divided by protein mass fraction; the 80.2% reference is `0.802` in that denominator. A supplied isolate-purchase quote can override its model purchase cost.

Freight, exchange rate and import-charge assumptions are displayed as scenarios. The price-plus-25% scenario is illustrative and makes no unsupported claim about an anti-dumping measure. A discount-adjusted benchmark difference is not automatically profit or proven savings.

## 12. Case feedback and future queries

### Case creation and submission

Every completed live analysis receives a fresh case UUID, even when its scientific calculation is served from cache. The database records the request snapshot, material, application, route, dataset version, time and candidate IDs.

The feedback form can record usefulness, trial outcome, optional candidate, issue category and private notes. Outcomes include not tested, worked and failed; trial outcomes are unverified reports. Issue categories cover solubility, texture, sensory, cost, yield and safety.

The API validates that the case exists and that a selected candidate belongs to it. One feedback record is accepted per case. Failed writes do not display a successful-save message.

### How future queries use feedback

Matching uses **material + application + extraction route + dataset version**. A future matching query receives aggregate counts and relevant follow-up suggestions. For example, reported texture issues can prompt application-specific texture/expansion tests; yield disagreements can prompt measured protein and ingredient recovery before costing.

Private free-text notes are not returned to other matching cases. Feedback cannot clear safety gates, replace a lab assay or silently overwrite scientific parameters. This is a stored observational feedback loop; an automatically trained prediction model has not been implemented.

### Storage

| Table | Purpose |
|---|---|
| `cases` | Case identity, matching scope, request snapshot and candidate IDs. |
| `feedback` | Case-linked feedback, outcome, issue, notes and time. |
| `lab_history` | Laboratory-update request and before/after result history. |

Local storage defaults to `.runtime/feedback.sqlite3`, which is excluded from Git. Hosted persistence requires `FEEDBACK_DB_PATH` pointing to a persistent mounted disk. With public storage unconfigured, analysis can continue but feedback storage is unavailable. Offline snapshots cannot create a live case or save feedback.

Authenticated accounts, verified laboratory submitters and production-grade access/retention management remain future work. Avoid entering personal or confidential information into this prototype.

## 13. Laboratory updates

The lab-result interface accepts the selected measurement, value, unit, basis and report metadata. It checks incompatible units and mismatched lot IDs, then shows the decision before and after the update. The user can keep the resulting request and rerun the analysis.

A measured contaminant exceedance can change a case to NO-GO. Other missing gates remain unresolved: entering one low contaminant result does not prove every safety requirement has passed. Bayesian updating is used only where a compatible prior model exists; a direct point comparison is not presented as a calibrated probability.

## 14. AI and language support

The decision engine is Python code. The optional AI layer explains existing results and helps parse descriptions; it cannot change a safety threshold or engine value.

The repository supports template explanations and two optional configured providers, Bedrock and Groq. `.env.example` also lists `gemini`, but no Gemini client is implemented; that setting falls back to the template. Explanations pass a number-verification check against the engine result, with deterministic template fallback. The local demonstration can run with `LLM_PROVIDER=template`, without paid AI credentials.

English/Hindi locale infrastructure and bilingual preset explanations are present. Hindi scientific wording still needs human review; unreviewed safety wording stays in English. Browser speech services and read-aloud controls depend on platform capabilities. Real-device microphone and screen-reader reviews remain outstanding.

## 15. Offline demo, memo and exports

If the API is unavailable, eligible unmodified preset requests can load precomputed results. The page identifies them as **Demo snapshot (offline)** and shows generation and dataset metadata. This supports a demonstration without a working backend; it does not create a fresh laboratory assessment.

The printable memo uses the current analysis object and includes case/version/time information, lot/use, verdict, decision dimensions, candidate or reference baseline, cost target, next test, sources and limitations. A JSON download includes the request and result for that case. A case-switch guard withholds the previous result while a new request is debounced or loading, keeping feedback and exports aligned.

The open-data ZIP contains structured data, sources, schemas, DATA_TODO and a licence note. Original unpublished source documents and the operational SQLite database are not distributed in that pack. The project has not yet selected a data-pack licence.

## 16. Architecture and technology

```text
Browser: React + TypeScript + Vite + Tailwind
    │
    │ /api requests through local proxy / configured deployment rewrite
    ▼
FastAPI
    ├── Pydantic request/response validation
    ├── Cached scientific analysis
    ├── Fresh live case IDs and SQLite feedback/history
    ├── Optional AI explanations and text parsing
    └── Read-only dataset endpoints
             │
             ▼
Pure Python Compass engine
    data → evidence/units → safety gates → diagnosis
         → candidate routes → supported mass balance/cost
         → evidence-aware assessment → readiness/validation plan
             │
             ▼
Versioned JSON data + sources + generated schemas

Build script → preset snapshots + offline data + downloadable ZIP
```

| Layer | Main technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS. |
| UI/state/forms | Existing Radix controls, TanStack Query, Zustand, React Hook Form and Zod. |
| Languages | i18next and react-i18next. |
| API | FastAPI, Uvicorn and Pydantic. |
| Computation | Python, NumPy and SciPy; sampling machinery for supported scenarios. |
| Persistence | Python standard-library SQLite. |
| Tests | pytest/Hypothesis, Vitest and React Testing Library. |
| Quality | Black, Ruff, ESLint, TypeScript and locale checks. |
| Deployment configuration | Vercel frontend and Render API configuration in the repository. |

The presence of sampling, Pareto and VOI modules does not mean every public estimate is enabled or calibrated. The evidence-aware assessment withholds unsupported outputs.

## 17. Repository map and API

```text
Project_Hack-/
├── PROJECT_OVERVIEW.md       This product/engineering overview
├── README.md                Quick start and project entry point
├── DATA_TODO.md             Generated missing/assumed/verification ledger
├── api/
│   ├── main.py              HTTP endpoints and orchestration
│   ├── feedback.py          SQLite cases, feedback and lab history
│   ├── llm/                 Parsing, explanations, templates and verifier
│   └── tests/               API/persistence tests
├── engine/compass/
│   ├── analyze.py           Analysis pipeline
│   ├── workflow.py          Evidence-aware public assessment
│   ├── contract.py          Request/response models
│   ├── gates.py             Safety and documentation gates
│   ├── learning.py          Laboratory-result updates
│   └── tests/               Formula, safety, workflow and regression tests
├── data/
│   ├── byproducts.json      Material references
│   ├── treatments.json      Candidate treatment evidence
│   ├── functional_evidence.json
│   ├── research_evidence.json
│   ├── safety_gates.json
│   ├── presets.json
│   ├── sources.json
│   ├── schema/              Generated data schemas
│   └── _staging/            Unreviewed rows, outside production calculations
├── web/
│   ├── src/Site.tsx         Public website
│   ├── src/App.tsx          Decision workspace
│   ├── src/screens/         Six screens and memo
│   ├── src/components/      Forms, evidence, feedback and result components
│   ├── src/api/             Client, hooks and generated API types
│   ├── src/locales/         English/Hindi content
│   ├── public/snapshots/    Bilingual preset results
│   ├── public/offline-data/ Offline reference data
│   └── e2e/                Browser journey scripts
├── scripts/                 Snapshot generation and development utilities
└── docs/                    Plans, audit, website and deployment notes
```

### Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API status and engine/dataset versions. |
| GET | `/presets` | Preset definitions and payloads. |
| GET | `/data/{name}` | Allow-listed structured reference files or report. |
| POST | `/analyze` | Case analysis and live case registration when storage is available. |
| POST | `/feedback` | Validated case-specific feedback submission. |
| POST | `/update-evidence` | Laboratory update and before/after comparison. |
| POST | `/explain` | Verified explanation or template. |
| POST | `/plan` | Validation plan and explanatory paragraph. |
| POST | `/parse-text` | Editable structured draft from a description. |

Generated API documentation is available at `/docs` on the running API.

## 18. Running the prototype locally

The repository documents Python 3.11–3.13 for its pinned dependencies and Node 20+. Run the following from the repository root in PowerShell; `uv` is used for the environment setup.

### Initial setup

```powershell
uv venv --python 3.13 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements-dev.txt
Push-Location web
npm.cmd ci
Pop-Location
```

### Terminal 1: API

```powershell
$env:PYTHONPATH = "engine;."
$env:LLM_PROVIDER = "template"
$env:APP_ENV = "local"
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8001
```

### Terminal 2: website

```powershell
$env:API_PROXY_TARGET = "http://127.0.0.1:8001"
Push-Location web
npm.cmd run dev -- --host 127.0.0.1
```

Open the website at `http://127.0.0.1:5173/` or the tool directly at `http://127.0.0.1:5173/#/compass`. API documentation is at `http://127.0.0.1:8001/docs`.

Local feedback uses the ignored `.runtime/feedback.sqlite3` file by default. For a hosted API, configure `FEEDBACK_DB_PATH` to durable mounted storage. The repository contains deployment configuration; this document does not establish that a public deployment or hosted feedback database is operational.

## 19. Verification and current quality

The last recorded implementation verification at baseline `911fe7c` reported:

| Check | Recorded result |
|---|---|
| Backend tests | 144 passed. |
| Frontend tests | 26 passed across 11 files. |
| Combined automated tests | 170 passed. |
| Python formatting/lint | Black and Ruff passed. |
| Frontend quality | ESLint, TypeScript/Vite production build and locale validation passed. |
| HTTP smoke | All five presets, fresh case IDs, contaminant checks, functional rows and evidence endpoints passed. |
| Offline artifacts | Ten bilingual analysis snapshots and data-pack integrity checked. |
| Browser inspection | Live workflow, functional comparison, mobile layout, offline presets, Hindi template and memo inspected. |
| Database behaviour | Persistence, matching-case observations, private-note isolation, duplicates, invalid candidates, failure states and lab history tested. |

The build had a non-blocking main-bundle size warning. Backend tests had upstream deprecation warnings. These are recorded implementation results, not a fresh test run caused by creating this document.

Software validation establishes that tested rules work as implemented. Laboratory validation must separately establish that the material, treatment and resulting product behave as required.

## 20. What remains to be built or validated

### Scientific and commercial evidence

- Verify the full treatment database against original primary papers.
- Collect identifiable lot-specific composition and contaminant results.
- Measure ingredient yield, protein recovery, losses and processing resource use.
- Run matched oilseed/pea functional assays under comparable conditions.
- Establish application-specific sensory protocols and acceptance results.
- Obtain dated supplier, processor and laboratory quotations.
- Review intended food category, handling, claims and applicable requirements with qualified reviewers.
- Calibrate probability and VOI models only when the required inputs exist.
- Develop validated techno-economic analysis and, later, life-cycle analysis.

### Production engineering and operations

- Configure and verify public hosting and durable feedback storage.
- Add authenticated users, appropriate access control and verified evidence-submission workflows when needed.
- Establish backup, retention, deletion and data-governance processes.
- Review Hindi scientific copy with a qualified reader.
- Complete real-device speech, screen-reader and broader accessibility checks.
- Improve bundle size and production monitoring based on actual usage.
- Verify print pagination for long cases and citations.

### Current data backlog

At the documented dataset version, `DATA_TODO.md` reports **161 missing values, 41 assumed values and 37 values to verify**. These are data-ledger categories, not a percentage of unfinished software. They explain why a working interface can correctly return TEST-FIRST and unavailable predictions.

## 21. Development roadmap

| Stage | Goal | Evidence or deliverable needed |
|---|---|---|
| Current prototype | Demonstrate the complete evidence-aware workflow | Implemented screens, calculations, tests, persistence and offline artifacts. |
| Evidence consolidation | Replace unsupported references/assumptions where possible | Checked primary sources, material forms, methods, units and applicability. |
| Controlled bench work | Test suitable material/process hypotheses | Identifiable samples, safety records, before/after assays and mass balance. |
| Application trials | Establish product-specific functional fit | Matched comparison tests, sensory protocol and finished-product measurements. |
| Pilot economics | Establish comparable practical cost | Recorded yield, utilities, losses, process quotes and declared cost boundary. |
| Product hardening | Support dependable shared use | Durable hosting, authentication, governance, monitoring and reviewed language/accessibility. |

The tool's proposed six-month research sequence covers sourcing and baseline evidence, bench trials, application testing, pilot resource/cost measurement, then customer/regulatory/economic review. It is a proposed validation programme, not six months of work already completed or a guaranteed delivery schedule.

## 22. Demo walkthrough

1. Open the Home page and introduce the purpose, mission and evidence principles.
2. Choose **Open Compass** and run **Sunflower cake → high-protein / fibre snack**.
3. Expect **TEST-FIRST**, hypothesis grade: batch assays, documentation and process evidence are unresolved.
4. Show the four decision dimensions and seven project contaminant checks.
5. Open Diagnosis and explain why missing assays do not generate valid exceedance ratios.
6. Show the eight-property comparison and separate cake flour, extracted isolate and pea evidence.
7. Open Chains. The current primary preset shows nine baseline/candidate routes; these are hypotheses, not validated rankings. Unsupported outputs remain unavailable.
8. Open Cost. Explain the shared pea benchmark and manual/benchmark/budget target options without claiming an established saving.
9. Open Next. Show required tests, laboratory update, readiness and proposed validation phase gates.
10. Open the memo or download the case JSON to preserve the current result.
11. Explain the live feedback loop. Use a disposable database for artificial feedback or laboratory demonstrations so they do not influence normal cases.
12. Demonstrate a stamped offline preset and explain why it cannot save live feedback.

The strongest demonstration shows a clear next step and the evidence required to change the answer. A default TEST-FIRST result is expected behaviour for incomplete research evidence.

## 23. Working rules and supporting documents

### Rules for continuing development

- Preserve the distinction between measured, published, assumed and synthetic evidence.
- Keep units, basis, material form and source conditions attached to relevant inputs.
- Leave missing inputs unavailable and update the data ledger.
- Keep safety, technical suitability and commercial targets separate.
- Do not let feedback or AI text override verified calculations or safety rules.
- Add meaningful regression tests for formula, safety, persistence or case-integrity changes.
- Regenerate API types after contract changes and snapshots/data packs after engine/data changes.
- Keep credentials, operational databases and unpublished source documents out of Git.
- Record the verification actually performed and any unresolved limits.

### Supporting documents

| Document | Use |
|---|---|
| [README.md](README.md) | Quick introduction, setup and commands. |
| [Final workflow audit](docs/FINAL_WORKFLOW_AUDIT.md) | Detailed implementation changes, scientific corrections, checks and limitations. |
| [Website notes](docs/WEBSITE.md) | Public pages, visual system, motion and image provenance; includes historical design context. |
| [Deployment notes](docs/DEPLOY.md) | Hosting configuration, offline behaviour and persistent feedback storage. |
| [Data TODO](DATA_TODO.md) | Generated missing/assumed/verification backlog. |
| [AI notes](docs/AI.md) | Explanation/parsing boundaries and verification. |
| [Phase history](docs/PHASES.md) | Earlier development history, read alongside the current audit. |

**Current milestone:** the complete prototype workflow is implemented and its recorded software checks pass. The next major step is verified material/process evidence and operational deployment, which will determine how far the prototype can support real pilot decisions.

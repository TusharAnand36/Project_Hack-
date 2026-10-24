# MASTER PROMPT v2: "Upcycle Compass" — By-product Decision Engine
**Hack the Fork 2026, India Edition (NIFTEM-K) · Problem Statement 2 · 24-hour proof of concept**

> Paste this whole file into your coding assistant (Claude Code / Cursor). Tell it: *"Read the whole file first. Then execute Section 17 (Build order) one phase at a time. Do not ask me questions unless you are blocked; state assumptions in one line and keep going."*

---

## 0. How to read this document

| Part | What it gives you |
|---|---|
| 1–3 | Context, rules, how we are judged, and who is judging |
| 4–5 | What already exists in the market and the **gaps** (with sources) |
| 6 | The idea: what we build and why it is rare |
| 7–8 | Scope, users, inputs and outputs |
| 9–10 | Architecture and the exact tech stack, with reasons |
| 11 | Data layer: schemas, evidence grading, seed data, what is still missing |
| 12 | **The rule/recommendation engine in full detail** (gates, diagnosis, treatment chains, cost, Monte Carlo, value of information, Pareto) |
| 13 | LLM usage rules and the number-verifier |
| 14 | API contract and UI screens |
| 15 | Tests and acceptance criteria |
| 16 | Honesty rules |
| 17 | 24-hour build order |
| 18 | Pitch, Q&A prep and the 6-month plan |
| 19 | References (clickable) and DATA_TODO template |

**Tag legend used everywhere in this document**
- `[V]` verified from a source I retrieved while writing this (URL given).
- `[U]` taken from the user's own papers/drafts (the oilseed-cake review draft, research plan, PhD progress report). **Draft values, treat as unverified until checked against the original paper.**
- `[A]` assumption or indicative number. Must be replaced or shown with wide uncertainty.

---

## 1. Context and hard rules from the organisers

Source: official Problem Statements PDF (released 11:00 AM, 24 Oct 2026).

**Our statement:** PS2 "Upcycling India's By-products for Alternative Proteins".
- *Problem:* India's food processing leaves protein-rich by-products (guar meal, groundnut and almond cake, rice bran, pulse residues). Most go to animal feed because bitter or beany flavours and anti-nutrients make them unfit for people. Companies need to quickly tell **which compounds hold a by-product back, or which treatment fixes it**.
- *Build:* a platform that (1) identifies those compounds, (2) recommends how to remove them, (3) predicts the effect on taste and protein, (4) estimates cost and resources versus **imported pea isolate**.
- *Key metrics named by organisers:* accuracy of identified limiting compounds; scientific justification of treatments; estimated protein retention; processing cost and resource requirements; comparison with a reference ingredient.

**Rules we must obey (these are scored or can disqualify):**
1. Declare the problem statement by **1:00 PM on 24 Oct**.
2. Nobody leaves the venue 10:00 PM (24 Oct) to 6:00 AM (25 Oct).
3. Round-1 ideas and prototypes are welcome; **only the final presentation is scored**.
4. **Label every data input as `measured`, `published`, `assumed` or `synthetic`.** (Four labels, not three.) Never use personal or sensitive data.
5. List all data sources, papers, models and tools on the **References slide as clickable links**.
6. Use the **official pitch deck template** (shared by 10:00 PM on 24 Oct).
7. Submit the final deck between **6:00 AM and 8:00 AM on 25 Oct**. Closes strictly at 8:00 AM. Pitch = **4 minutes**, then **4 minutes of questions**.
8. Not expected: a commercially validated solution. Expected: a working proof of concept, a clearly defined industry decision, credible data and assumptions, **communicated uncertainty**, and practical next steps for validation.

**Official optional resources we should use (and cite):** IFCT 2017 (Indian food composition), USDA FoodData Central, FooDB (compounds in foods), Open Food Facts, AGMARKNET / e-NAM / daily mandi prices, FAOSTAT (crop volumes), HESTIA life-cycle data on AWS Open Data.

---

## 2. How we are judged, and what each criterion forces us to build

| Criterion (from PDF) | What judges will look for | Feature that answers it |
|---|---|---|
| 1. Presentation and relevance | A specific industry decision; clear use case; convincing pitch | One sentence decision: *"Can this batch become a human-grade protein ingredient, and what is the cheapest safe route versus imported pea isolate?"* Three one-click presets |
| 2. Technical approach and scientific validity | Sound methods, credible data, justified assumptions, stated limitations | Evidence-graded data layer, safety gates, transparent formulas, extrapolation penalties, "decision readiness" label, limitations panel |
| 3. Functionality | Prototype works and produces useful outputs | End-to-end flow with precomputed fallback snapshots so the demo cannot fail |
| 4. Feasibility and impact in 6 months | First pilot or customer, what is needed, what it costs | Auto-generated **validation plan and pilot budget** from the engine's own value-of-information output |
| 5. Innovation and use of AI | Novel or thoughtful approach; AI used meaningfully, not bolted on | Probabilistic decision engine + expected value of information + Bayesian updating from lab results; LLM restricted to parsing/explaining with a **number verifier** |

---

## 3. Who is judging (design the pitch for them)

Source: the jury information file provided.

| Judge | Background | What will impress them | What will annoy them |
|---|---|---|---|
| **Dr. Lipika Dey** (Ashoka University) | NLP, ML, AI systems; ex-TCS | AI used with purpose: grounded LLM, schema validation, calibrated uncertainty, learning loop from new data | "We fine-tuned a model" with no data; LLM inventing numbers |
| **Dr. Padma Ishwarya S.** (Senior Scientist, GFI India) | Plant-based protein, by-product valorisation, functionality (foams, emulsions, gels) | Correct food science: anti-nutrients, protein recovery, N-to-protein factor, functionality fit; honest limits. She authored GFI India's recent whitepaper on indigenous crops to cut import dependence on pea/soy | Claims such as "autoclave removes aflatoxin"; ignoring functionality; false precision |
| **Prof. Kavya Dashora** (IIT Delhi) | AI for agriculture, decision support, safety, translation to field | "When can a prediction support a reliable decision?" and "what must be demonstrated before it is safe, useful and ready to scale" | Predictions presented without data quality or readiness criteria |
| **Prof. Ganesh Bagler** | Computational gastronomy, FlavorDB/Foodoscope, "making food computable" | Structured, open, computable knowledge (compound → flavour → treatment); APIs; flavour-compound grounding | Free-text black boxes; no data model |

**Design consequence:** every screen must answer "how sure are we, and why?" Every number carries a tag and a source.

---

## 4. Market research: what exists today

*(Retrieved Oct 2026. URLs are in Section 19.)*

### 4.1 AI food-ingredient platforms (all proprietary, mostly Western)
| Player | What it does | Why it does not solve PS2 |
|---|---|---|
| NotCo (Giuseppe) | Reverse-engineers animal foods from plant ingredient combinations | Formulation to mimic a target; not a by-product safety/treatment/cost decision tool |
| Shiru (Flourish, ProteinDiscovery.ai) | Searches ~33M protein sequences to find novel functional proteins; marketplace | Discovers *new molecules*, not how to make commodity Indian by-products food-grade |
| Climax Foods | ML for plant-based dairy | Dairy-analogue formulation |
| Brightseed (Forager; Hummingbird launched May 2026) | Bioactive discovery from a 21M-compound dataset | Bioactives for health, not anti-nutrient removal economics |
| Nuritas | Bioactive peptide discovery | Peptides, not bulk protein ingredients |

**Takeaway:** the funded "AI for food" wave is aimed at *novel molecules and formulation*. None offers an open, India-specific tool that takes a *commodity by-product batch* and answers "safe? which treatment chain? what cost versus imported isolate? which test first?"

### 4.2 Upcycling companies (physical, not decision tools)
- **ReGrained / Upcycled Foods Inc.** (brewer's spent grain), **revyve** (brewer's spent yeast), **Kern Tec** (fruit pits), **NapiFeryn** (rapeseed cake to protein powder, Poland), **CoryPro** (guar meal to protein concentrate/isolate; notes guar meal is single-ingredient and available at scale, ~1.3 Mt/yr). Indian capacity signal: **RELSUS** opened a functional plant-based ingredient plant in Ujjain (not a by-product player, but shows local ingredient manufacturing is starting).
- Their stated hardest problems: **batch-to-batch variability** (colour, moisture, nutrients), **guaranteeing supply**, consistency of flavour and shelf life.

### 4.3 Open techno-economic tools
- GFI publishes open-access techno-economic models (e.g. an Excel TEA for mycoprotein) and says explicitly that **similar open models are still needed for plant-based production**, and that functional-property databases are proprietary and duplicated.
- These are spreadsheets for *one process at a time*: no safety gate, no treatment chain search, no uncertainty ranking of which measurement matters.

### 4.4 Academic literature (including the user's own review)
- Many reviews list anti-nutrients and treatments **one at a time**. The user's own review draft (Table 13) states the gap itself: *"Treatments studied one at a time; effects on bioactives, colour and function seldom co-measured → multi-response optimisation of sequential treatments is needed."* Also: *"Scale-up and techno-economics: cost and return estimates rely on models with few independent validations."* And: *no harmonised specifications for cold-pressed cake as a food ingredient.*
- Scientific findings relevant to the build:
  - Rice bran degrades into an unpalatable material in about **six hours** under normal milling conditions because of lipase; free fatty acid above **5%** is considered unfit for human food (Dubey et al. 2019 citing Tao et al. 1993). `[V]`
  - Groundnut cake in India: in a 5-year survey, **only 47.2% of 118 groundnut-cake samples were below 20 ppb aflatoxin B1** (Murugeswari 2023). `[V]` (feed-grade samples; see caveats in Section 12.1)
  - Aflatoxin is heat-resistant (decomposes ~237–306 °C); moist heat under pressure gives *partial* reduction in some studies; reported effects vary a lot with moisture and conditions. `[V]` So **a model must never assume that heat "fixes" aflatoxin**.
  - India permitted aflatoxin in groundnut: **30 ppb** vs EU 4 ppb and US 20 ppb per one Indian institute summary `[V]` (verify the exact legal basis before use).

### 4.5 India market facts that make the problem real
- Roughly **90% of plant-protein ingredients used in India are imported** and the plant-protein ingredient market is expected to double from about ₹4,500 crore to ₹9,000 crore in five years (PBFIA). `[V]`
- GFI India's whitepaper says the smart-protein sector depends on imports mainly from **China and Europe**. `[V]`
- India produces **>25 million tonnes of oilseed cake a year**; mostly feed or export. `[V]` (cited in the user's review and a 2024 review)
- Trade-policy risk: the **EU (provisional duties, 31 Mar 2026), the US and Canada** have anti-dumping/countervailing measures on Chinese pea protein; trade press notes players expect China to try re-routing. This is a supply and price risk for imported isolate. `[V]`
- India's customs stack on protein substances (HS 3504): Basic Customs Duty 20% + IGST 18% + social welfare surcharge. **Two sources disagree on the total: 43.96% vs 49.15%.** `[V]` We treat it as an uncertain input, and note that a GST-registered manufacturer can usually claim IGST as input credit, so the economic duty may be only ~22%. `[A]` (confirm with a CA/customs source)
- China export price of pea protein 80–85%: about **US$2.3–4.6/kg** across 2023–24. `[V]` (Tridge). USD/INR was **≈ ₹95–97** in Sep–Oct 2026. `[V]`
- Indicative Indian by-product prices (trader listings): groundnut cake about **₹27,000–30,000/tonne**, de-oiled rice bran about **₹10,500/tonne**. `[A]` Replace using AGMARKNET / SEA / NCDEX.

---

## 5. The gaps (what is missing in the market and in the literature)

| # | Gap | Evidence | How we exploit it |
|---|---|---|---|
| G1 | **No open decision tool for commodity by-products** (safety → treatment → cost vs import). AI players chase novel molecules | 4.1 | Build exactly that |
| G2 | **Safety is treated as a footnote.** Real batches of Indian groundnut cake fail aflatoxin limits more than half the time in surveys; rice bran spoils in hours | 4.4 | Safety gate first, with a *prior probability of failure* before any test |
| G3 | **Treatments studied one at a time**, not as *sequences* with cross-effects (the user's own review gap) | 4.4 | Chain enumerator + Pareto of protein retained vs flavour vs cost |
| G4 | **Uncertainty is hidden.** Papers report single values from different cultivars, presses and assay methods; the review itself says composition ranges are wide and N-to-protein factors vary (6.25 vs 5.71 vs 5.45) | User's review §2.1.1 | Distributions everywhere; evidence-graded inputs; extrapolation penalty |
| G5 | **Nobody tells you which single test to run first.** Labs spend money measuring everything | GFI/Problem statement ("the one measurement that would most change the ranking" appears in PS3 and in the draft) | Expected value of information (EVPPI) per input, divided by test cost |
| G6 | **Cost comparison is on the wrong basis.** Isolate vs flour vs concentrate have different protein %. Pea isolate quoted per kg product, not per kg protein; India duty stack and FX are uncertain | 4.5 | Everything on **₹ per kg protein**, India-specific duty/GST toggle, break-even price, shock scenarios |
| G7 | **Batch variability and supply** is the #1 scale-up killer for upcycled ingredients | 4.2 | Batch-data input mode; blending/tiering hint; variability widens ranges |
| G8 | **No bridge from model to lab and pilot.** Judges want a 6-month plan | Judging criterion 4 | Auto-generated validation plan and pilot budget |
| G9 | **Open knowledge graph for Indian by-products doesn't exist** (compound → taste effect → treatment → evidence) | Jury (Bagler: "making food computable") | Publish our JSON dataset as an open, versioned, cited data pack |
| G10 | **Allergen and positioning blind spot.** Groundnut is a major allergen; pea wins "hypoallergenic" positioning | Review §11; India market reports | Application gate flags allergen-free claims as impossible for groundnut |

---

## 6. The idea: what we build, and why it is rare

### 6.1 One-sentence product
**Upcycle Compass** tells a food company, for a specific by-product batch and target application: *Go / No-go / Test-first*, *which treatment chain is best and how likely it is to meet the spec*, *the cost per kg protein versus imported pea isolate (with break-even)*, and *the single lab measurement worth buying first (with its ₹ cost versus the value of the information).*

### 6.2 The six differentiators (build these; they are what other teams will not have)

1. **Safety gate with a prior.** Before treatment: three-state result `PASS / FAIL / TEST-FIRST`. For unmeasured batches we show the *prior* probability that the batch fails (from published Indian surveys), so a company knows the risk before spending anything. Gate failures are **hard stops**; the engine never "treats its way out" of aflatoxin on paper.
2. **Treatment chains, not single treatments.** Sequences with ordering rules, per-step protein/yield loss, side effects on flavour, and a Pareto front of *protein retained vs flavour vs ₹/kg protein*. This directly fills the multi-response/sequential-treatment gap stated in the user's own review.
3. **Expected Value of Information (EVPI/EVPPI).** Monte Carlo over all uncertain inputs, then compute how much *expected regret* each input causes. Recommend the test with the best (value ÷ test cost). Verified in a prototype (Section 12.9): the answer is often *not* the obvious one (e.g. measure baseline phytate, not the price of the cake).
4. **Per-kg-protein landed cost versus imported pea isolate** with India's duty stack, a GST-credit toggle, FX and freight sliders, break-even price, and shock scenarios (INR depreciation, anti-dumping re-routing).
5. **Evidence grading and extrapolation penalty.** Each treatment effect carries grade A–D and an *applicability score* (same species? same conditions?). If a number comes from sunflower but we apply it to groundnut, its range is automatically widened and the UI says so. The tool outputs **"decision-grade" vs "hypothesis-grade"** instead of pretending certainty. (This is Prof. Dashora's question: *when can a prediction support a reliable decision?*)
6. **Closed learning loop.** The user enters a lab result; the engine does a Bayesian update of that input and re-ranks. That is AI used meaningfully: a system that gets more certain as data arrives, with the LLM only translating.

**Bonus rare features (cheap, high impact):**
- **Product-tier ladder:** flour → treated flour → concentrate → isolate. Many applications (snacks, bakery) need only 10–20% inclusion of treated flour, not an isolate; beverages usually need concentrate/isolate. The tool recommends the *cheapest tier that meets the spec*.
- **True protein vs crude protein:** protein = N × factor; the factor is a parameter with its own range, so we do not overstate protein.
- **Open data pack** (JSON + citations) published with the repo.

### 6.3 What we explicitly do NOT do
- No model training. No image models. No synthetic "AI predicts taste" claims.
- No invented numbers. If data is missing we show a wide range and tag it `assumed`.
- No claim that this replaces lab validation. It tells you **what to validate first**.

---

## 7. Scope of the proof of concept (depth over breadth)

### 7.1 By-products
| Role | By-product | Why this one | Main limiting issue the engine must show |
|---|---|---|---|
| Core 1 | **Groundnut cake** (cold-pressed/expeller and solvent-extracted variants) | Named in PS2. High protein (45–60% crude, `[U]` Table 2 of review). India is a top producer | **Safety first** (aflatoxin), then trypsin inhibitor, phytate, tannins, lipid-oxidation "beany/green" volatiles, allergen |
| Core 2 | **De-oiled rice bran (DORB)** | Named in PS2. India is a very large rice and rice-bran-oil producer (verify volumes on FAOSTAT) | **Stability and low base protein**: lipase/FFA (rancidity in ~6 h unstabilised), high phytate, heavy-metal risk, base protein far below 60% so protein concentration step is mandatory |
| Control (recommended) | **Almond cake** | Named in PS2. We hold the user's own *measured* proximate data on almond cake `[U]` | Few anti-nutrients; the engine should say **"no detox treatment needed; the constraints are allergen and price"**. This proves the tool discriminates rather than rubber-stamps |
| Stretch only | Guar meal | Named in PS2; India is a leading guar producer (verify on FAOSTAT/APEDA); CoryPro proves a commercial path | Galactomannan/viscosity, saponins, bitterness. **Only if everything else is done** |

### 7.2 Target applications (each sets tolerances; see 11.5)
1. **Beverage** (needs high solubility, very low off-flavour, no gritty fibre)
2. **Extruded snack / puffed product** (tolerates 10–20% inclusion of treated flour; darker colour acceptable)
3. **Meat analogue (textured protein)** (needs gelation/texture; moderate flavour tolerance; extrusion step natural)

### 7.3 Product tiers (a decision variable, not a given)
`flour` (cake milled, optionally treated, ~protein as-is) → `concentrate` (60–75% protein, washing/sieving/ultrafiltration) → `isolate` (≥80–90%, alkaline extraction + isoelectric precipitation). All costs are expressed **per kg protein** so tiers are comparable.

### 7.4 Treatments in the catalogue (7 for the PoC)
`stabilise` (heat/steam/antilipase, for rice bran), `moist_heat` (autoclave/steam), `phytase`, `soak_germinate` (0.1% NaHCO₃ soak + germination), `ssf_ferment` (solid-state fermentation), `ae_iep` (alkaline extraction + isoelectric precipitation), `extrude`. Optional: `ethanol_wash` (excluded automatically when the user selects "no solvents").

---

## 8. Users, decision, inputs and outputs

### 8.1 Personas (use in the pitch)
1. **Edible-oil / rice-mill owner** (Guntur, Rajkot, Punjab): "I sell this at feed prices. Can I sell it to a food company? What must I test and change?"
2. **R&D head at an Indian plant-based brand:** "Pea isolate is imported, costly and exposed to FX and anti-dumping risk. Is there a local protein I can trust, at what cost and risk?"
3. **Incubator / GFI-style programme manager:** "Which pilots should we fund first?"

### 8.2 The decision the tool supports (write this on slide 2)
> *"For this batch and this application: Go, No-go, or Test-first? If Go, which treatment chain at which product tier, at what ₹ per kg protein compared with imported pea isolate, with what probability of meeting spec, and which one lab test should we run first?"*

### 8.3 Inputs (structured form; never empty; every field carries a tag)
**Core**
1. By-product (dropdown)
2. Target application (dropdown)
3. Targets (**state cost per kg protein, not per kg product**; the earlier draft's example of 'beverage protein under ₹150/kg' sits far below imported isolate's landed cost per kg product, roughly ₹400–480 at default inputs, so it is reachable only for flour/concentrate tiers): minimum final protein %, maximum ₹/kg **protein**, maximum off-flavour index (0–10), maximum phytate % (default from application), target market (`domestic` | `export_EU`) which sets the aflatoxin limit
4. Scale (kg of by-product per day)

**Optional**
- Constraints: exclude treatments (e.g. no solvents), available equipment (extruder, fermenter, spray dryer, ultrafiltration), electricity ₹/kWh, water ₹/m³, labour ₹/h
- **Own batch data** (manual or CSV): protein % (and N factor used), moisture, fat, FFA %, AFB1 ppb, phytate %, TIA, ash, heavy metals. Anything not entered falls back to published defaults, labelled `published`/`assumed`
- Process context: oil-extraction route (cold-pressed / expeller / solvent), hours since milling (rice bran), storage conditions
- Pea isolate parameters (all sliders with defaults): base US$/kg, protein %, freight %, import duty stack choice, GST-credit toggle, USD/INR
- Co-product credits (oil, fibre) default **0** (conservative); user may enable
- Free text box → LLM extracts structured fields → user confirms (nice to have)

**Presets (one click):**
1. *Groundnut cake → beverage protein* (shows safety gate + chain Pareto)
2. *De-oiled rice bran → extruded snack* (shows stability gate + low-protein reality)
3. *Almond cake → meat analogue* (shows "no treatment needed", allergen/price flags)

**Example payload**
```json
{
  "byproduct": "groundnut_cake",
  "application": "beverage",
  "targets": {"min_protein_pct": 60, "max_cost_inr_per_kg_protein": 300, "max_offflavour_index": 3.0},
  "market": "domestic",
  "scale_kg_day": 500,
  "constraints": {"exclude_treatments": ["ethanol_wash"], "equipment": ["extruder","spray_dryer"]},
  "batch": {"protein_pct": {"value": 48, "n_factor": 6.25, "tag": "measured"},
            "moisture_pct": {"value": 8, "tag": "measured"},
            "afb1_ppb": null},
  "pea": {"base_usd_per_kg": null, "protein_pct": 85, "freight_pct": null,
          "duty_mode": "bcd_only_igst_credited", "usd_inr": null}
}
```
(`null` = use dataset default and label it.)

### 8.4 Outputs (what the user sees)
1. **Verdict card:** `GO / NO-GO / TEST-FIRST`, plus *decision grade* (`decision-grade` / `hypothesis-grade` / `not viable`)
2. **Safety gate cards** with required tests and what would flip the result
3. **Diagnosis:** compounds ranked by exceedance of application tolerance, with uncertainty bars
4. **Treatment chains table + Pareto plot** with P(meets spec)
5. **Cost vs imported pea isolate** (₹/kg protein, stacked breakdown, break-even, sliders, shock scenarios)
6. **Next step:** the one test to buy first (EVPPI per ₹), plus a validation plan and 6-month pilot budget
7. **Provenance:** hover/tap any number to see tag, source, evidence grade, applicability
8. **Export:** one-page "Decision Memo" (PDF/Markdown) for the pitch and for companies

---

## 9. Architecture

```
┌──────────────────────────── web (React + TS) ───────────────────────────┐
│ Form+Presets → Verdict → Gates → Diagnosis → Chains/Pareto → Cost → Next │
│ State: Zustand · Data fetching: TanStack Query · Validation: Zod         │
└───────────────▲──────────────────────────────────────┬──────────────────┘
                │ JSON (typed)                          │ fallback: /snapshots/*.json
┌───────────────┴───────────── api (FastAPI) ───────────▼──────────────────┐
│ /analyze  /parse-text  /explain  /update-evidence  /presets  /data/*     │
└───────────────▲─────────────────────────▲────────────────────────────────┘
                │                         │ (language only)
┌───────────────┴──── engine (pure Python package `compass`) ──────────────┐   ┌──── LLM (Groq) ────┐
│ gates → diagnosis → chain enumerator → effect model → cost model →       │◄──┤ parse / explain /  │
│ Monte Carlo → EVPPI → Pareto → readiness grade → Bayesian update         │   │ draft; verifier    │
└───────────────▲──────────────────────────────────────────────────────────┘   └────────────────────┘
                │ validated at startup (Pydantic)
┌───────────────┴────────────── /data (JSON, git-versioned) ───────────────┐
│ byproducts · compounds · treatments · applications · costs · gates · tests │
│ every row: value(s), unit, tag, evidence_grade, source, applicability      │
└──────────────────────────────────────────────────────────────────────────┘
```
**Principles:** (1) the engine is a pure, unit-tested library with no web code; (2) the LLM can never write to the engine or invent numbers; (3) data is plain JSON so teammates edit it in parallel and every change is reviewable; (4) every demo path has a precomputed fallback.

---

## 10. Tech stack (exact choices and reasons)

### 10.1 Recommended stack
| Layer | Choice | Why this, and what we rejected |
|---|---|---|
| Frontend | **React 18 + TypeScript + Vite** | Fast dev loop; matches the team's MERN strength. Rejected Next.js (SSR not needed) |
| Styling | **Tailwind CSS + shadcn/ui (Radix)** | Quick, accessible, mobile-friendly components (cards, tabs, tooltips, sliders) |
| Charts | **Recharts** | Enough for: horizontal bars with error ranges, scatter (Pareto), stacked bars, tornado (sorted horizontal bars). Rejected D3 (time) |
| State/data | **Zustand + TanStack Query**; **Zod** schemas; **react-hook-form** | Small, predictable; Zod mirrors Pydantic models so type errors are caught early |
| Provenance UI | A reusable `<Num value tag source grade/>` component | Single place that renders number + chip + tooltip. **Use it for every number** |
| Export | **react-to-print** or `html2canvas + jsPDF` | One-page decision memo without a server |
| Backend | **Python 3.11 + FastAPI + Pydantic v2 + Uvicorn** | Monte Carlo and statistics are natural in NumPy/SciPy; automatic OpenAPI docs for the team. Rejected Node-only: weaker numerics/test tooling (but see 10.3) |
| Numerics | **NumPy, SciPy (`stats.qmc` Sobol/LHS sampling), pandas** | Quasi-random sampling gives stabler results at 5,000 runs |
| Graph | **networkx** (or plain DFS) | Chain enumeration with precedence DAG and pruning |
| Sensitivity | Custom **EVPPI** (Section 12.9); optional **SALib** for Sobol indices as a cross-check | EVPPI answers a decision question; Sobol only answers a variance question |
| Tests | **pytest + hypothesis** | Property tests catch impossible outputs (negative cost, protein > 100%) |
| LLM | **Groq API, a Llama-3.x 70B model** (check the current model ID in the Groq console; IDs change), fallback **Gemini free tier**, final fallback = templated text with no LLM | Free tiers; language-only tasks |
| Data store | **JSON files in `/data` validated at startup** | No database needed: small, curated, diffable, citable. Rejected MongoDB/SQL for the PoC (adds nothing for 100s of rows) |
| Deploy | **Vercel (web)** + **Render/Railway/Fly free (API)** or one Docker on **Hugging Face Spaces** | Plus **precomputed snapshots** for the 3 presets in `/web/public/snapshots` so the demo works if the free API cold-starts or venue Wi-Fi dies |
| Secrets | `.env` + `.env.example`; keys server-side only | Never in the browser, never in git |

### 10.2 Repository layout
```
upcycle-compass/
├─ README.md                # run instructions, PoC disclaimer, limitations
├─ .env.example
├─ DATA_TODO.md             # every null/assumed cell to fill from papers
├─ data/
│  ├─ byproducts.json  compounds.json  treatments.json  applications.json
│  ├─ costs.json  safety_gates.json  lab_tests.json  sources.json
│  └─ schema/*.json         # JSON-Schema or Pydantic export
├─ engine/compass/
│  ├─ models.py             # Pydantic types (Param, Dist, Tag, Grade)
│  ├─ sampling.py           # PERT/triangular/lognormal + QMC
│  ├─ gates.py  diagnosis.py  chains.py  effects.py  flavour.py
│  ├─ cost.py  pea.py  montecarlo.py  voi.py  pareto.py
│  ├─ readiness.py  update.py  plan.py
│  └─ tests/
├─ api/main.py  routers/  llm/ (client.py, prompts.py, verify.py)
├─ web/ (src/components/Num.tsx, screens/*, charts/*, snapshots/)
└─ scripts/ (extract_rows_from_abstracts.py, build_snapshots.py)
```

### 10.3 If the team is JavaScript-only
The math is simple enough to port to **TypeScript and run in the browser** (5,000 Monte Carlo runs over ~15 inputs is milliseconds). Pros: no backend failures at the demo. Cons: weaker test tooling, and the LLM call still needs a tiny serverless function to hide the API key. Default recommendation remains Python engine + React UI.

---

## 11. Data layer

### 11.1 Rules
- **Every row has:** `id`, `byproduct` (or `compound`/`treatment`), `field`, `value_low/mode/high` (or distribution), `unit`, `tag` (`measured | published | assumed | synthetic`), `evidence_grade` (A–D), `source_id`, `conditions` (species, press type, temperature, pH, time, dose), `notes`.
- **Evidence grades:** **A** measured by the user on this batch; **B** peer-reviewed quantitative result on the *same* by-product and comparable conditions; **C** peer-reviewed on a *different* species/conditions, or review/secondary citation; **D** assumption or expert guess.
- **Applicability score** `α ∈ [0,1]` for each use of a row: 1.0 same species + same conditions; 0.7 same species, different conditions; 0.4 different species, same compound and mechanism; 0.2 analogy only. **Extrapolation penalty:** widen the range around the mode by factor `1 + k·(1−α)` (default `k = 1.0`) before sampling, and display "transferred from <species>".
- Never present an unsourced number as fact. Missing data → `null` plus an entry in `DATA_TODO.md`.

### 11.2 Schema sketch (Pydantic/JSON)
```json
{
  "id": "gnc_phytate_baseline",
  "byproduct": "groundnut_cake",
  "field": "phytic_acid_pct_db",
  "dist": {"type": "pert", "low": null, "mode": null, "high": null},
  "unit": "% dry basis",
  "tag": "assumed",
  "evidence_grade": "D",
  "applicability": 1.0,
  "conditions": {"press": "cold|expeller|solvent"},
  "source_id": null,
  "notes": "FILL FROM IFCT 2017 / literature; see DATA_TODO"
}
```
```json
{
  "id": "trt_phytase_phytate_on_gnc",
  "treatment": "phytase",
  "target_compound": "phytic_acid",
  "applies_to": "groundnut_cake",
  "reduction_frac": {"type": "pert", "low": 0.75, "mode": 0.84, "high": 0.92},
  "tag": "published",
  "evidence_grade": "C",
  "applicability": 0.4,
  "conditions": {"measured_on": "sunflower_cake", "pH": 5.5, "temp_c": 50, "time_min": 120, "dose": "500 FTU/kg"},
  "source_id": "akande_2011",
  "notes": "Transferred from sunflower; widen range; verify on groundnut."
}
```

### 11.3 Seed values we already have (starting point; **verify every one**)
**Proximate (user's review Table 2, dry-matter style ranges)** `[U]`
| By-product | Moisture % | Crude protein % | Fat % | Fibre % | Ash % |
|---|---|---|---|---|---|
| Groundnut cake | 8.0–10.0 | 45.0–60.0 | 4.0–10.9 | 3.8–7.5 | 4.0–7.5 |
| Almond cake | ~ | 37.0–51.3 (plan) / 35–49 (PhD report) | 16.3–19.0 | ~5.6 | ~5.3 |
| De-oiled rice bran | `[A]` | **`[A]` 14–18 (verify with IFCT/USDA/industry spec)**; the PhD report lists "rice bran pellets 9%" (industrial sample) → conflict flagged | `[A]` low | `[A]` | `[A]` high ash/silica |

**Measured lab data in the user's PhD progress report** (moisture, ash, Kjeldahl protein 31.45–44.23%, crude fibre, crude fat, for sesame, mustard, flaxseed, almond; sesame protein-extraction yield 0.70 at pH 9 and 0.63 at pH 10, units to be confirmed). `[U]` These are a ready-made example of `measured` rows. **Use only with the owner's permission, and cite them.**

**Treatment effects from the user's review (Tables 7–8) `[U]`, each with the species it was measured on**
| Treatment | Target | Reduction | Measured on | Conditions | Transfer to our by-products |
|---|---|---|---|---|---|
| Extrusion | Trypsin inhibitor | 88.0–98.5% | Soybean | 140–160 °C, 20–25% moisture | Groundnut TI: α≈0.4 |
| Moist heat (autoclave) | Trypsin inhibitor | ~85% | Groundnut | 121 °C, 15 min (Panhwar 2005) | Same species; **verify original** |
| Phytase | Phytic acid | 75.0–92.0% | Sunflower | 500 FTU/kg, pH 5.5, 50 °C, 120 min | Groundnut/rice bran α≈0.4 |
| Phytase | Phytic acid + oxalate | 70.0–88.0% | Sesame | 45 °C, pH 5.0, 180 min | α≈0.4 |
| Soak + germination | Phytic acid, tannins | 55.0–78.0% | Groundnut | 0.1% NaHCO₃ + 48 h | Same species (α≈0.7–1.0 depending on source check) |
| SSF | Glucosinolates + tannins | 82.5–95.0% | Rapeseed | A. niger / L. plantarum, 30–37 °C, 48–72 h | Tannins on groundnut α≈0.3 |
| Isoelectric wash pH 4.5 | Chlorogenic acid | 92% | Sunflower | before extraction | Not applicable to groundnut; shows pattern |
| Ethanol/water 70:30 | Polyphenols | 82% (purity 55→84%) | Hemp | + diafiltration | Solvent; excluded if "no solvents" |
| Dehulling | Protein density | up to +15% | Mixed | | Fibre reduction lever |

**Flag to the team:** the draft review states that *electric sorting + autoclaving* brings groundnut aflatoxin B1 below 2 ppb. Other literature shows aflatoxin is highly heat-stable and heat/pressure effects are partial and condition-dependent. **Do not encode "autoclave → aflatoxin below limit". Encode the safety gate as measurement-driven and treat any reduction as a wide `assumed` range that still requires re-assay.**

**Rice bran stabilisation `[V]`:** a study using edible-acid activation of endogenous phytase followed by drying to inactivate lipase reduced phytic acid by up to **43.6%** and acid value by up to **85.2%** (Assam Agricultural University); patent literature describes antilipase-enzyme stabilisation without denaturing protein; patent claims show rice bran protein isolates at about 91% protein, 3% fat (treat as a *claim*, grade C/D).

**Economics seed `[A]` unless stated**
- Groundnut cake ₹27–30/kg; DORB ₹10.5/kg (trader listings, replace with AGMARKNET/SEA).
- Pea isolate base: **US$2.3–4.6/kg** `[V]` (China export prices 2023–24), default mode 3.2; protein 80–85%.
- USD/INR default **96** (range 90–105) `[V]` Oct 2026 quotes ≈ 95–97.
- Freight 4–14% (mode 8%). `[A]`
- Duty stack: **BCD 20% + SWS + IGST 18% = 43.96% or 49.15%** `[V]` (sources disagree). Offer 3 modes: `full_stack_44`, `full_stack_49`, `bcd_only_igst_credited_22`.
- Review's TEA cascade (for context only): feed-cake ~US$150–250/t vs isolates US$2,500–4,500/t vs bioactive extracts US$8,000–15,000/t; a model plant of 10,000 t/yr capex US$8.5–12.0M `[U]` (model-based; Sari et al. 2022). Do not use as prices without checking.

**Aflatoxin and rancidity gates `[V]`**
- Survey prior: 47.2% of 118 groundnut-cake samples ≤ 20 ppb AFB1 (Murugeswari 2023, feed-grade). So prior P(>20 ppb) ≈ **0.53** for unselected feed-grade cake.
- India limit quoted as 30 ppb (groundnut), EU 4 ppb, US 20 ppb `[V]` (verify legal basis; EU limits differ for B1 vs total).
- Rice bran: FFA > 5% = unfit for human consumption; ~6 h degradation window if unstabilised.

### 11.4 Files
`byproducts.json` (composition, variability, base compound levels, oil route variants), `compounds.json` (what each compound does: safety / bitter / beany / colour / mineral-binding / digestibility; flavour weight `w`; odour threshold θ if known; assay method), `treatments.json` (effects per compound with distributions; protein/yield loss; energy kWh/kg, water L/kg, chemicals ₹/kg, labour h/t, time, equipment, solvent flag, side effects; precedence), `applications.json` (tolerances and tier suitability), `costs.json` (utilities, wages, pea isolate inputs, depreciation assumptions), `safety_gates.json` (rules, tests, limits, priors), `lab_tests.json` (test name, what it measures, method, ₹ cost range, turnaround days, replicate guidance), `sources.json` (id, citation, DOI/URL, access date).

### 11.5 Application tolerance table (starting values, **all `assumed` until sourced**)
| Application | Min protein in ingredient | Max off-flavour index (0–10) | Max phytate (% db) | Max trypsin inhibitor (% of raw activity) | Preferred tiers | Functionality needed |
|---|---|---|---|---|---|---|
| Beverage | 60% | 3 | 1.0 | 15% | concentrate, isolate | solubility at neutral pH, low grit, colour |
| Extruded snack | 35% (as inclusion at 10–20%) | 5 | 2.0 | 20% | flour, treated flour, concentrate | expansion tolerance (review: ≤15–20% inclusion typical `[U]`) |
| Meat analogue | 55% | 4 | 1.5 | 15% | concentrate, isolate | gelation/texturisation, water holding |

Functionality fit is shown as a **qualitative flag with a reference**, not a computed score (we have no data to model it). Padma Ishwarya (GFI India) works on foams/emulsions/gels, so show you know it matters and that measuring solubility/emulsification is part of the validation plan.

### 11.6 Optional helper: abstract → candidate rows
`scripts/extract_rows_from_abstracts.py`: user pastes an abstract or table; LLM returns **candidate** rows in the schema with a quote-span and the DOI; all rows are written to `data/_staging/` with `tag: "assumed"`, `evidence_grade: "D"` until a human sets them to `published` and fills conditions. Never auto-merge.

---

## 12. The rule / recommendation engine (full specification)

### 12.0 Pipeline (one `/analyze` call)
```
input ─► normalise (dry basis, N-factor) ─► SAFETY GATES (3-state, with priors)
      ─► DIAGNOSIS (exceedance of application tolerance)
      ─► CHAIN ENUMERATION (precedence, exclusions, equipment, pruning)
      ─► for each chain: EFFECT MODEL (compound levels, protein/mass balance, flavour index)
      ─► COST MODEL (₹/kg protein, kWh/kg, L/kg)  ─► PEA ISOLATE parity + break-even
      ─► MONTE CARLO (8,192 Sobol draws) ─► P10/P50/P90, P(spec)
      ─► RANK + PARETO ─► READINESS GRADE ─► EVPPI → "test to buy first" ─► PLAN
      ─► verdict + JSON ─► (LLM explains from JSON only)
```
All randomness is seeded (`seed=42` by default) so the demo is reproducible. The engine returns **only JSON**; every numeric leaf is `{p10,p50,p90,tag,grade,source_ids,alpha}` or `{value,tag,...}`.

### 12.1 Safety gates (hard rules, evaluated first)

**Result states:** `PASS`, `TEST-FIRST` (cannot decide without a measurement), `FAIL` (hard stop for human-food use). Overall gate = worst state. **A modelled treatment can never convert FAIL to PASS**; only a *new measurement on the treated material* can.

| Gate | Applies to | Inputs | Rule | Required test (from `lab_tests.json`) | What flips it |
|---|---|---|---|---|---|
| **G1 Aflatoxin B1** | groundnut (any form) | `afb1_ppb` (measured or null), market limit `L` (domestic 30 ppb `[V, verify]`; export_EU 4 ppb total aflatoxin `[V, verify]`), `sorted_food_grade_supply` (bool) | **Measured:** `≤ 0.5·L` → PASS; `0.5·L < x ≤ L` → TEST-FIRST (confirm by HPLC; rapid kits and sampling error are large); `> L` → FAIL. **Not measured:** TEST-FIRST and show **prior P(fail)**: baseline `≈ 0.53` for unselected feed-grade cake `[V]` (47.2% of 118 samples were ≤ 20 ppb, Murugeswari 2023); if `sorted_food_grade_supply` multiply prior odds by `0.2` `[A]` | Representative composite sample (≥ 10 sub-samples from the lot `[A]`), ELISA screen then HPLC confirm | A measured value ≤ 0.5·L on a representative composite |
| **G2 Rancidity / lipase** | rice bran (and any high-fat cake in storage) | `hours_since_milling`, `ffa_pct` (measured or null), `stabilised` (bool) | `ffa > 5%` → FAIL for human food `[V]`; `3% < ffa ≤ 5%` → TEST-FIRST (stabilise immediately, retest) `[A threshold 3%]`; `ffa ≤ 3%` and (`stabilised` or `hours ≤ 6`) → PASS; not measured and `not stabilised and hours > 6` → FAIL; otherwise TEST-FIRST | Free fatty acid / acid value titration; peroxide value | FFA ≤ 3% on stabilised material |
| **G3 Heavy metals** | rice bran | `inorganic_as_ppm`, `cd_ppm` | Not measured → TEST-FIRST (rice bran can concentrate arsenic/cadmium; **add a citation before pitching**). Measured vs limit table in `safety_gates.json` (`null` until sourced) | ICP-MS | Measured ≤ limit |
| **G4 Solvent residue** | any solvent-extracted meal (incl. DORB) | `solvent_extracted`, `hexane_cert` | Solvent-extracted and no certificate → TEST-FIRST | Hexane residue GC-HS | Certificate or measurement |
| **G5 Food-grade provenance** | all | `food_grade_supply`, `storage` | If feed-grade/open storage → TEST-FIRST (microbiology: total plate count, yeast/mould, *Salmonella*) and "re-source if possible" | Micro panel | Passing micro panel + hygienic supply |
| **G6 Allergen (flag, not stop)** | groundnut, almond (tree nut), sesame, soy | `application`, `claims` | Always show `FLAG: major allergen; must be labelled; cannot support an allergen-free claim`. If user claims "allergen-free", gate → FAIL for that claim | — | — |
| **G7 Regulatory (flag)** | all | — | Show `FLAG: confirm FSSAI classification/approval route for a novel or non-standardised ingredient` `[A]` | — | — |

**Pseudo-code**
```python
def gate_aflatoxin(batch, market, sorted_supply):
    L = {"domestic": 30.0, "export_EU": 4.0}[market]
    if batch.afb1_ppb is not None:
        x = batch.afb1_ppb
        if x <= 0.5*L: return PASS
        if x <= L:     return TEST_FIRST
        return FAIL
    prior = 0.53 if not sorted_supply else odds_to_p(p_to_odds(0.53)*0.2)
    return TEST_FIRST, {"prior_p_fail": prior, "tag": "published", "source": "murugeswari_2023"}
```

**Lot-sampling note (say it in the pitch):** aflatoxin sits in a few "hot" kernels, so *sampling* error often dominates assay error. The plan must call for a composite sample.

### 12.2 Normalisation
- Convert everything to **dry basis** (`x_db = x_wb / (1 − moisture)`).
- **True protein = N × f**, where `f ~ PERT(5.45, 5.71, 6.25)` for sources whose N is not all protein, unless the user states the factor used. Report both *crude protein (N×6.25)* and *true protein*. If the user's batch protein was measured by Kjeldahl, treat N as known and let `f` vary. This stops us overstating protein (the review itself notes factors range 6.25 / 5.71 / 5.45).
- Unit sanity checks: protein + fat + fibre + ash + carbohydrate ≈ 100% ± 5 (warn if not).

### 12.3 Diagnosis: which compounds hold the by-product back
For each compound `c` relevant to the by-product and application:
```
L_c  ~ distribution (batch value if measured, else published/assumed range; widen by extrapolation penalty)
T_c  = tolerance for the application (applications.json)
ER_c = L_c / T_c                       (exceedance ratio; >1 means over the limit)
P_exceed_c = P(ER_c > 1)
severity_c = median(log10(max(ER_c, 1)))
```
**Ranking:** by `P_exceed_c × (1 + severity_c)`, with safety compounds (aflatoxin, FFA) always listed first because they are gates, not tunable. The **limiting compound** = top-ranked non-gate compound; show the top three. For compounds with no tolerance in the dataset, show "no limit available (qualitative)" rather than guessing.
Additional diagnostics that are *not* compound-removal problems (show them as separate chips):
- **Protein density gap:** `required_protein − base_protein` (rice bran: large; needs fractionation).
- **Amino-acid limitation** (e.g. groundnut and sunflower are lysine-limited; sunflower is rich in sulphur amino acids `[U]`): flag as "blend, not treatment" because processing cannot add lysine.
- **Functionality caveat** for the application.

### 12.4 Treatments, chains and their rules

**Per-treatment record (`treatments.json`)** contains: targets `{compound: reduction_dist}` with `applies_to`, evidence grade and applicability; `mass_yield m` and `protein_retention ρ` distributions (or, for fractionation steps, `purity π` and `recovery ρ`); resources (kWh/kg input, water L/kg input, chemical ₹/kg input, labour h/t, time, capex reference and reference scale); `requires_equipment`, `uses_solvent`; `side_effects` (flavour additions, colour, lysine loss); and `preconditions`.

**Precedence and compatibility rules (encode as a DAG plus a forbidden-pairs list):**
1. `stabilise` must be **first** for rice bran, and must occur before any wet step.
2. `phytase` requires an aqueous, mildly acidic step (pH ≈ 5–5.5) and is placed **before** `ae_iep` (engineering judgement `[A]`: hot alkaline conditions would inactivate the enzyme; verify against the literature before the pitch).
3. `moist_heat` (autoclave/steam) may precede `phytase` only if the slurry is cooled to enzyme temperature before the enzyme is added; forbid `phytase → moist_heat` in the same slurry (the heat would destroy the enzyme).
4. `ae_iep` is a fractionation step: it **ends the chain** for isolate tier (allow at most one fractionation step; allow `extrude` after it only for the meat analogue application).
5. `extrude` can be first (flour → textured/inclusion route) or last (texturise a concentrate). Never between `phytase` and `ae_iep`.
6. `ssf_ferment` and `soak_germinate` are alternatives for the same job; forbid combining them (assume mutual exclusion; `[A]` and note the review lists them as separate families).
7. Maximum chain length 4. Maximum one of each treatment. Exclusions (e.g. "no solvents") and missing equipment remove treatments **before** enumeration.
8. **Prune** a partial chain if (a) it already exceeds the cost cap at P10 cost or (b) protein retention P90 < required retention.

**Enumeration:** depth-first search over the allowed DAG, with the `no-op` chain (raw flour) always included as the baseline. With 7 treatments and the rules above, expect on the order of tens of chains per by-product; if more than 60, keep the 60 with the highest provisional score and say so.

**Effect of one step on a compound (first-order with a floor)**
```
L_after = floor_c + (L_before - floor_c) * (1 - r)         r ~ reduction distribution (after extrapolation penalty)
```
`floor_c` is the assay detection limit or an intrinsic residual (`assumed` if not known). **No synergy terms** are invented: effects multiply unless a source shows interaction (then add a row with its own grade). A step that does not list a compound in its `targets` leaves it unchanged. Where a compound is removed by washing in a fractionation step, the reduction is the *partition* given for that step.

### 12.5 Mass and protein balance (tiers)
Per step `i` with input mass `M` (kg per kg raw cake), protein fraction `p`:
```
non-fractionation step:   M_i = M_{i-1} * m_i              (dry-matter yield, e.g. germination loss)
                          prot_i = M_{i-1} * p_{i-1} * ρ_i   (protein retained)
                          p_i = prot_i / M_i
fractionation (AE-IEP):   π_i ~ purity distribution, ρ_i ~ recovery distribution
                          prot_i = M_{i-1} * p_{i-1} * ρ_i
                          M_i   = prot_i / π_i
```
Final: `protein_retained = prot_final / (p_0)` (per kg raw cake, using true protein), `protein_pct_final = p_final`, and the **tier** is assigned by final protein: `<45% flour/treated flour`, `45–<75% concentrate`, `≥75% isolate` (thresholds configurable). Cap `p_i ≤ 0.95`. Seed ranges for AE-IEP are `assumed` (purity 0.75–0.90, recovery 0.40–0.70) until the team sources them; the rice bran patent claim of ~91% protein isolate is grade C/D.

### 12.6 Off-flavour index (transparent, not a "taste predictor")
```
baseline contributions s_c (0–10 scale units) by compound class c:
   beany/green aldehydes (hexanal-type), bitter phenolics/saponins/tannins, rancid FFA/oxidation, roasted/Maillard, earthy/cereal
OFI_before = min(10, Σ_c s_c)
for each step i affecting class c:   s_c ← s_c * (1 - r_{i,c})   +   a_{i,c}      (a = added side-note, e.g. heat adds roasted, SSF adds fermented)
OFI_after  = min(10, Σ_c s_c)
```
- Baselines `s_c` and weights are **`assumed`** (grade D) with wide PERT ranges, until a trained panel or published sensory data replaces them.
- **Optional measured route** (only if the user supplies GC-MS concentrations): `s_c = κ_c · log10(1 + Σ_k C_k/θ_k)` where `C_k` is concentration and `θ_k` the odour threshold (odour activity value logic). Use FlavorDB/FooDB to map compounds to descriptors where available (Prof. Bagler's domain), tagged `published`.
- Display as **P10–P90 bars** and say "index, to be calibrated by a sensory panel (triangle test + scaling)". Never present it as a measured taste.

### 12.7 Cost and resource model (all per kg protein)
```
per step i, per kg of its input mass:
   energy_i  = kWh_i * tariff
   water_i   = (L_i/1000) * water_price
   chem_i    = Σ chemical_kg * price
   labour_i  = (h_per_t_i / 1000) * wage
   capital_i = capex_i(S) * CRF / (annual_throughput_kg)        with  capex_i(S) = capex_ref * (S/S_ref)^0.6   (six-tenths rule, [A])
   step_cost_i = (energy_i + water_i + chem_i + labour_i + capital_i)  * (kg input to step per kg raw cake)
total_cost_per_kg_raw = raw_price + Σ step_cost_i + QA_cost + overhead% 
cost_per_kg_product   = total_cost_per_kg_raw / M_final
cost_per_kg_protein   = cost_per_kg_product / p_final  − co_product_credit / protein_out   (credit default 0)
kWh_per_kg_protein, litres_per_kg_protein   computed from the same flows
```
`CRF` (capital recovery factor) uses discount rate 12% and life 10 years `[A]`; 300 operating days × 80% utilisation `[A]`. **Scale effect:** the user's kg/day changes capital charge per kg through the 0.6 rule, so the UI shows cost vs scale as a small curve. Everything above is `assumed` until replaced; the point is a transparent structure with ranges, not false precision.

### 12.8 Imported pea isolate: landed cost, parity and break-even
```
landed_per_kg_product = base_usd * usd_inr * (1 + freight) * (1 + duty)            # + optional clearing/holding cost [A]
landed_per_kg_protein = landed_per_kg_product / pea_protein_frac                    # 0.80–0.85 [V] range
duty modes: full_stack_44 | full_stack_49 | bcd_only_igst_credited_22               # sources disagree; user toggle
parity price  = landed_per_kg_protein                                               # what the buyer avoids paying
price_we_can_charge = parity * (1 − buyer_discount)        # buyer discount default 10% [A]
margin_vs_pea = price_we_can_charge − cost_per_kg_protein
break_even_pea_base_usd = solve base such that  landed_per_kg_protein = cost_per_kg_protein   (closed form: invert the formula)
```
Return: P(margin>0), break-even *base price in US$/kg* (distribution), and **three shock scenarios** (INR to 105; +20% freight; pea base +25% from anti-dumping diversion). The UI offers sliders for base price, FX, freight, duty mode, GST-credit toggle, and an `import-parity` line on every cost chart. **All comparisons are per kg protein, never per kg product.**

**Sanity example (illustrative defaults, not a result):** base US$3.2/kg × ₹96 = ₹307/kg; × 1.08 freight = ₹332; × 1.44 (full duty stack) = ₹478 per kg product; ÷ 0.85 protein = **≈ ₹562 per kg protein**. If IGST is creditable (duty ≈ 22%): ₹332 × 1.22 = ₹405 per kg product ≈ **₹476 per kg protein**. The gap between those two numbers is why the duty mode is a switch.

### 12.9 Monte Carlo and value of information (the centrepiece)

**Sampling:** `scipy.stats.qmc.Sobol(d=n_inputs, scramble=True, seed=42)` with `n = 2^13 = 8192` draws. Distributions: PERT(low, mode, high, λ=4) for bounded effects; lognormal for compound levels; triangular/uniform when only a range exists (grade D); correlations identity by default (list this as a limitation). Gate inputs are sampled as Bernoulli(prior) when unmeasured, so **P(GO) = P(gate pass) × P(spec | gate pass)**.

**Per draw and per chain** compute: `protein_pct_final`, `protein_retained`, `OFI`, `phytate_final`, `TIA_final`, `cost_per_kg_protein`, `kWh/kg protein`, `L/kg protein`, `margin_vs_pea`, and `spec_met = AND(all targets)`. `P(spec)` is the mean of the **joint** indicator (not the product of marginals).

**Decision utility (explicit, stated on screen):**
```
U(option) = decision_volume_kg_protein * [ margin_vs_pea ]            if spec_met
          = − failure_cost_per_kg_protein * decision_volume           if not spec_met      (failed pilot/wasted campaign, [A])
U(sell_as_feed) = 0   (reference option, always available)
```
`decision_volume_kg_protein` defaults to one pilot campaign (e.g. 10 t of cake → protein out), `failure_cost` defaults to the variable cost of that campaign. Both are visible parameters.

**EVPI and EVPPI**
```
E_now      = max_option  E[U(option)]
EVPI       = E[ max_option U(option) ] − E_now                       # value of knowing everything
EVPPI(x)   = E_x[ max_option E[U(option) | x] ] − E_now              # value of perfectly learning input x
```
**Estimator (simple, robust, already prototyped):** bin the draws of `x` into 25 equal-count bins, compute `max_option mean(U | bin)` per bin, average with weights, subtract `E_now`. Cross-check the top 3 with a regression estimator (Strong–Oakley–Brennan) or SALib if time. Inputs are grouped by test (e.g. all phytate-related inputs → "phytic-acid assay"). For an *imperfect* test use `EVSI ≈ EVPPI × R`, where reliability `R = σ²_prior / (σ²_prior + σ²_measurement)` `[A approximation; state it]`.

**Recommended next measurement**
```
for each test t in lab_tests.json:   ROI_t = EVSI_t / cost_t(₹ per batch)
recommend  argmax ROI_t  subject to EVSI_t > cost_t
if none satisfy it:  say "No test is worth its cost; decide now" (this is a valid, honest outcome)
```

**Prototype result (already run; synthetic demo numbers, not claims):** two chains for groundnut cake (A: soak+germination; B: phytase+AE-IEP) against a pea landed cost near ₹565 per kg protein. EVPI ≈ ₹99 per kg protein. The EVPPI ranking was: baseline phytate (≈52), phytate reduction of chain A (≈38), everything else ≈ 0, including price, FX, duty, cake price and yield. **Message:** the next test is a phytic-acid assay on the actual batch, *not* more price research. This is the kind of output the engine must produce. A reference implementation:
```python
def evppi(x, U, v_now, bins=25):
    qs = np.quantile(x, np.linspace(0, 1, bins+1))
    idx = np.clip(np.digitize(x, qs[1:-1]), 0, bins-1)
    cond_best = np.array([U[idx == k].mean(0).max() for k in range(bins)])
    w = np.array([(idx == k).mean() for k in range(bins)])
    return (w * cond_best).sum() - v_now          # U shape: (N draws, n_options)
```

### 12.10 Ranking and Pareto view
- Remove chains whose gate = FAIL. Compute per chain `E[U]`, `P(spec)`, `P50 cost`, `P50 OFI`, `P50 protein_retained`.
- **Three named recommendations:** *Best expected value* (max `E[U]`), *Safest* (max `P(spec)` with `P50 cost ≤ target`), *Cheapest viable* (min `P50 cost` with `P(spec) ≥ 0.5`).
- **Pareto:** objectives = maximise `protein_retained`, minimise `OFI`, minimise `cost_per_kg_protein` (medians). A chain is non-dominated if no other chain is at least as good on all three. Also compute `P(A dominates B)` by pairwise draws and label two chains "statistically tied" when neither dominates the other with probability ≥ 0.8. Chart: scatter of cost (x) vs protein retained (y), colour = OFI, marker size = P(spec), pareto front outlined, **error bars for P10–P90**.

### 12.11 Decision readiness grade (answers "when can a prediction support a reliable decision?")
```
DECISION-GRADE   if gates=PASS and P(spec) ≥ 0.80 and EVPI / |E_now| ≤ 0.15 and ≥ 70% of top-5 value drivers have grade A/B
NOT VIABLE       if any gate=FAIL, or best P(spec) < 0.20, or best margin P50 < 0
HYPOTHESIS-GRADE otherwise  (shows a "what must be demonstrated" checklist: the top EVPPI inputs, each with the lab test and acceptance criterion)
```
Thresholds are config values and must be shown on screen.

### 12.12 Learning loop (Bayesian update)
When the user enters a measurement for input `θ` (e.g. phytate % db):
- Continuous inputs: lognormal prior `(μ0, σ0)` on log scale, measurement with log-error `σm` (assay CV from `lab_tests.json`). Posterior `μ1 = (μ0/σ0² + y/σm²) / (1/σ0² + 1/σm²)`, `σ1² = 1 / (1/σ0² + 1/σm²)`. Tag becomes `measured`, grade `A`.
- Gate priors: Bayes with test sensitivity/specificity (`assumed`: ELISA screen sens 0.95 spec 0.90). `posterior_odds = prior_odds × LR`, `LR+ = sens/(1−spec)`, `LR− = (1−sens)/spec`.
- Re-run `/analyze` and show **before/after** (verdict, P(spec), EVPPI list). This is the demo moment: "enter one lab number and the recommendation sharpens."

### 12.13 Validation plan and 6-month pilot generator (rule-based, not LLM)
From the top EVPPI tests: for each, output method, replicates (n=3 minimum), sample plan, `₹` cost range, turnaround days, acceptance criterion. Then a templated 6-month timeline: Month 0–1 sourcing + gate tests; Month 1–3 bench trials of the top 2 chains; Month 3–4 sensory panel + functionality (solubility, emulsification, gelation); Month 4–5 pilot-scale run (10 t decision volume) + micro/contaminants; Month 5–6 cost validation + customer sample trials + regulatory classification check. Budget lines come from `lab_tests.json` and `costs.json` (all `assumed`, to be replaced by lab quotes). Name the first pilot partner type (feed-grade mill → food-grade line; incubator lab; named institutions only if the team has actually talked to them).

### 12.14 The recommendation rules in one list (give this to the coder as acceptance criteria)
1. If any gate is `FAIL` → verdict `NO-GO`, show reason, show "divert to feed / re-source", **do not rank chains** (but may show a "what-if gate passed" toggle clearly labelled).
2. If any gate is `TEST-FIRST` → verdict `TEST-FIRST` unless EVSI of that test is below its cost *and* prior risk is acceptable (user-set), then say so.
3. Rank chains by `E[U]`; never recommend a chain with `P(spec) < 0.2`.
4. Always compare on ₹ per kg protein; always show P10–P90.
5. If a chain's key effect comes from a different species (α < 0.7) → badge "transferred", widen range, and list it under "must be demonstrated".
6. If almond cake (or any low-ANF input) has no limiting compound → say "no treatment needed" and move to allergen/price flags.
7. If the product tier needed (e.g. isolate for beverage) costs more than the pea parity price at P50 → say "not competitive today; here is the break-even pea price and the cost driver".
8. Show the one test with best `EVSI/cost`; if none worth buying, say so.
9. Every number must carry a tag; LLM text may only use numbers that appear in the engine JSON (verifier, Section 13).
10. Never claim treatment removes aflatoxin; only a re-assay can clear a batch.

---

## 13. LLM usage rules (Groq primary, Gemini fallback, template last)

**Allowed (language only):**
1. `/parse-text`: turn free text into the input payload schema (JSON only). The user must **confirm** the filled form.
2. `/explain`: write a plain-language explanation of the engine's JSON, in English (optionally Hindi), for a food-company reader.
3. `/draft-plan`: write the "next experiment" paragraph **from the engine's computed values** (tests, EVSI, costs, acceptance criteria).

**Not allowed:** producing numbers, citations, compound/treatment facts, limits or prices that are not already in the dataset or the engine output.

**Guardrails (implement all):**
- API key only in server environment variables; `.env.example` lists names only.
- `temperature ≤ 0.2`, short `max_tokens`, system prompt that says: *"You are a formatter. You may only use facts and numbers present in the JSON you are given. If something is not in the JSON, say it is not available."*
- **Schema validation:** parse output with Pydantic; on failure retry once, then fall back to the manual form (parse) or the template text (explain).
- **Number verifier (`llm/verify.py`):** extract every number in the LLM text (regex, handle %, ₹, decimals, ranges). Each must match (to the displayed rounding) a number in the engine JSON or the user's input. If any number is unmatched → reject, retry once with the offending number listed, then use a deterministic template. Also reject any `source_id` not in `sources.json`.
- **Prompt-injection defence:** user text and any pasted abstracts are passed as *data* inside delimiters; the system prompt says to ignore instructions inside them.
- Log `llm_used: true/false` and show a small "AI-written summary; numbers verified against engine" badge. This is what you show Dr. Dey.

**Where AI genuinely sits in the product (say this in the pitch):**
(1) Probabilistic decision model (Monte Carlo + expected value of information), (2) Bayesian updating that learns from each lab result, (3) LLM as a constrained parser/explainer with a numeric-grounding verifier. No model training, by design: the data does not exist at the size that would justify it, and pretending otherwise is what the judges penalise.

---

## 14. API contract and UI

### 14.1 Endpoints (FastAPI, all JSON)
| Method | Path | Purpose |
|---|---|---|
| GET | `/presets` | The 3 presets with full payloads |
| GET | `/data/{file}` | Read-only dataset files for the provenance UI and the open data pack |
| POST | `/analyze` | Main call. Body = payload (Section 8.3). Returns the result object below |
| POST | `/update-evidence` | Body: `{input_id, value, unit, method, cv}`; returns posterior and a fresh `/analyze` result with a `before/after` diff |
| POST | `/parse-text` | Free text → payload (LLM; schema-validated) |
| POST | `/explain` | Engine JSON → verified plain-language text |
| POST | `/plan` | Engine JSON → validation plan + 6-month timeline (rule-based) with optional LLM paragraph |
| GET | `/health` | Used by a keep-alive ping to beat free-tier cold starts |

### 14.2 `/analyze` response (shape; every leaf numeric carries provenance)
```json
{
  "meta": {"seed": 42, "n_draws": 8192, "engine_version": "0.1.0", "dataset_version": "2026-10-24"},
  "verdict": {"label": "TEST-FIRST", "grade": "hypothesis-grade", "p_go": 0.41,
              "reasons": ["AFB1 not measured; prior P(fail)=0.53 [published]"]},
  "gates": [{"id": "G1", "state": "TEST-FIRST", "prior_p_fail": {"value": 0.53, "tag": "published", "source_ids": ["murugeswari_2023"]},
             "required_test": "afb1_composite_hplc", "flip_condition": "measured ≤ 0.5×limit", "flags": ["allergen"]}],
  "diagnosis": [{"compound": "phytic_acid", "tolerance": 1.0, "level": {"p10": 1.5, "p50": 2.2, "p90": 3.1, "tag": "assumed"},
                 "p_exceed": 0.97, "rank": 1}],
  "chains": [{"id": "ch_03", "steps": ["moist_heat", "phytase", "ae_iep"], "tier": "isolate",
              "protein_retained": {"p10": 0.4, "p50": 0.5, "p90": 0.6},
              "protein_pct_final": {"p10": 78, "p50": 84, "p90": 89},
              "ofi": {"p10": 1.8, "p50": 2.7, "p90": 4.0},
              "cost_inr_per_kg_protein": {"p10": 230, "p50": 280, "p90": 340},
              "kwh_per_kg_protein": {"p50": 0}, "l_water_per_kg_protein": {"p50": 0},
              "p_spec": 0.74, "e_utility": 0, "transferred": ["phytase: from sunflower, α=0.4"],
              "pareto": true, "badges": ["best_expected_value"]}],
  "pea": {"landed_inr_per_kg_protein": {"p10": 470, "p50": 565, "p90": 678}, "break_even_base_usd_per_kg": {"p10": 0, "p50": 0, "p90": 0},
          "scenarios": [{"name": "INR 105", "landed": 0}]},
  "voi": {"evpi": 0, "evppi": [{"input": "phytate_baseline", "value": 52, "test_id": "phytate_assay", "evsi": 0, "cost_inr": 0, "roi": 0}],
          "recommended_test": "phytate_assay", "note": ""},
  "plan": {"tests": [], "timeline": [], "budget_inr": {"low": 0, "high": 0, "tag": "assumed"}},
  "limitations": ["…"]
}
```
(Zeros above are placeholders in the shape example, not results.)

### 14.3 Screens
1. **Input.** Form with preset buttons; each field has a tag chip; defaults visible; collapsible "Own batch data (CSV or manual)"; free-text box (if LLM on). Disclaimer banner: *"Proof of concept. Not a substitute for laboratory validation."*
2. **Verdict + Safety gates.** Big verdict card (`GO/NO-GO/TEST-FIRST`) with decision grade, P(GO), reasons. Gate cards in traffic-light style **with icons and text** (not colour alone), required test, cost, "what flips this".
3. **Diagnosis.** Horizontal bars of compound level vs application tolerance line, P10–P90 whiskers, rank numbers, "limiting compound" highlighted. Chips for protein-density gap, amino-acid limitation (blend, not treatment), allergen.
4. **Treatment chains.** Sortable table (steps, tier, protein retained, protein %, OFI, ₹/kg protein, P(spec), badges) + Pareto scatter. Click a chain → before/after panel and "transferred evidence" warnings.
5. **Cost vs pea isolate.** Stacked bar (raw, energy, water, chemicals, labour, capital, QA, loss) vs pea landed stack (base, freight, duty, FX effect). Sliders: pea base, FX, freight, duty mode, GST-credit toggle, scale, utility prices. Break-even readout. Shock scenario buttons. A small curve of ₹/kg protein vs scale.
6. **Next step.** Tornado chart of EVPPI (top 8 inputs), recommended test with ₹ cost and "worth it?" line, **"Enter your lab result" box** that calls `/update-evidence` and shows before/after. Generated validation plan and 6-month timeline. "Export decision memo".
7. **Provenance.** Global toggle "show sources". `<Num/>` tooltips: value, range, tag, grade, α, source, conditions, link. A "Data completeness" meter (share of value-driving inputs graded A/B vs C/D).
8. **Limitations** footer on every screen.

**UX requirements:** mobile-friendly; loading skeletons; error states with the snapshot fallback ("Demo snapshot (offline)" badge); keyboard accessible; tag chips use letters M/P/A/S plus colour; units always visible; no number without a tag.

### 14.4 Reverse mode (only if time remains)
User enters target (e.g. "concentrate for beverage, ≤ ₹250/kg protein"); engine loops over all by-products × chains × tiers and returns the top 5 combinations with P(spec) and gate state. Pure reuse of the same engine.

---

## 15. Tests and acceptance criteria

**Unit and property tests (pytest + hypothesis)**
- Mass/protein balance: protein out ≤ protein in; `p ≤ 0.95`; cost ≥ raw cost; no NaN.
- Distribution samplers: PERT mean within 1% of analytic; all draws within [low, high].
- EVPPI ≥ 0 and ≤ EVPI (allow tiny numerical tolerance).
- Monotonicity: increasing pea base price never decreases `P(margin > 0)`; adding an exclusion never adds chains.
- Seeds reproduce identical outputs.
- Bayesian update: posterior variance < prior variance.

**Golden scenarios (must pass before the demo)**
| ID | Input | Expected |
|---|---|---|
| GT1 | Groundnut cake, AFB1 not measured, domestic | Gate TEST-FIRST; prior P(fail) ≈ 0.53 displayed; verdict never GO |
| GT2 | Groundnut cake, AFB1 = 60 ppb | Verdict NO-GO; chains not ranked; message "divert to feed or re-source" |
| GT3 | Rice bran, 24 h since milling, unstabilised, FFA unknown | G2 FAIL |
| GT4 | Rice bran, stabilised, FFA 2% | G2 PASS; "protein density gap" flagged; raw-flour chain has P(spec)=0 for beverage; a fractionation chain is required |
| GT5 | Almond cake → meat analogue | "No anti-nutrient treatment needed"; allergen and price flags; not an empty page |
| GT6 | "No solvents" selected | `ethanol_wash` absent from all chains |
| GT7 | Any scenario, LLM text altered to include number 777 | Verifier rejects; template used |
| GT8 | Enter measured phytate | Tag becomes `measured`, grade A, EVPPI list changes, "before/after" shown |

**Backtest for "accuracy of identified limiting compounds" (organisers' metric):** make a small table from the literature of *what authors say limits each by-product* (groundnut: aflatoxin, trypsin inhibitor, phytate/tannin; rice bran: lipase/rancidity, phytate; sunflower: chlorogenic acid; rapeseed: glucosinolates; flax: cyanogenic glycosides) and report agreement between our top-3 compounds and the literature statements for the 8–10 cases in `data/` including non-core cakes from the user's review Table 8. State the sample size honestly. For the **cost/protein** metrics, run a **prospective calibration plan**: predict P10–P90 for 3 batches, measure, report coverage.

**Definition of done for the demo:** all 3 presets run in < 3 s, offline snapshots exist, every number shows a tag, the References slide links resolve, the README states PoC limits.

---

## 16. Honesty rules (these are what scientific judges reward)
1. Label every number `measured / published / assumed / synthetic`. Show ranges, not false precision.
2. If data is missing, say so, show uncertainty and add it to `DATA_TODO.md`. **Never invent a value.**
3. State in the UI, README and pitch: *this is a proof of concept; the next step is laboratory validation.*
4. Show "transferred from another species" wherever evidence is borrowed.
5. Never imply heat or washing makes an aflatoxin-failed batch safe.
6. The off-flavour index is an index, not a taste measurement; sensory validation is in the plan.
7. Cost numbers are model estimates with wide ranges until replaced by lab/pilot quotes.
8. Do not use the user's unpublished PhD data without the owner's permission; cite it.
9. Use `synthetic` for any simulated demo batch and say so on screen.
10. Note that the oilseed review draft's figures were not independently verified; our dataset replaces them row by row with checked values.

---

## 17. Build order (about 21 working hours: 11:00 AM release to the 8:00 AM close, minus the sleep you choose)

**Roles if 3–4 people:** *Engine lead* (Python), *Data/science lead* (papers → JSON, owns `DATA_TODO`), *Frontend lead* (React; your MERN strength), *Story/pitch lead* (deck, references, Q&A, LLM prompts). If solo, follow the **priority tiers** below and stop at the first tier you can finish well.

**Priority tiers**
- **Tier 0 (must):** data files with seeds, gates, diagnosis, chain enumeration (≥ 6 chains), cost model, pea comparison with break-even, Monte Carlo, UI screens 1–5 with provenance chips, snapshots for 3 presets.
- **Tier 1 (the differentiators):** EVPPI + recommended test, Pareto, readiness grade, validation plan.
- **Tier 2:** Bayesian "enter lab result" demo, LLM parse/explain with verifier, decision memo export.
- **Tier 3:** reverse mode, guar meal, CSV upload.

| Phase | Clock (suggested) | Deliverable | Gate to move on |
|---|---|---|---|
| P0 | by 1:00 PM | **Declare PS2.** Repo, README skeleton, schemas, `.env.example`, dummy data, `DATA_TODO.md` | Declaration confirmed |
| P1 | 1:00–3:30 PM | Engine core on dummy values: distributions, effect model, cost model, Monte Carlo, unit tests. Frontend scaffold with `<Num/>`, form, presets | GT-mass-balance tests pass |
| P2 | 3:30–6:30 PM | `/analyze`, gates, diagnosis, chain enumerator, pea parity. UI screens 1–5 wired to live API. **Data lead replaces dummy rows with sourced rows continuously** | Preset 1 renders end-to-end |
| P3 | 6:30–9:30 PM | EVPPI, Pareto, readiness grade, plan generator; UI screens 6–7; snapshots script | GT1–GT6 pass |
| P4 | 9:30 PM–midnight | LLM parse/explain + verifier; Bayesian update flow; polish; error states. **Venue lock-in from 10 PM** | GT7–GT8 pass |
| P5 | midnight–3 AM | Data cleanup (every `assumed` visible and justified); backtest table; README; deploy; **sleep in shifts** | Deployed URL + offline snapshots |
| P6 | 6:00–7:30 AM | Pitch deck in the **official template**, References slide (clickable), rehearse 4-minute pitch twice, record a backup screen video | Deck uploaded **before 8:00 AM** (portal opens 6:00 AM) |

**Hard rules for the coding assistant:** state assumptions in one line; commit after each phase; never block on missing data (use `null` + TODO); keep the engine free of web imports; add a test with every new rule.

---

## 18. Pitch (4 minutes), Q&A (4 minutes) and the 6-month plan

### 18.1 Slide plan (map into the official template)
1. **Problem and stake** (30 s): ~90% of India's plant-protein ingredients are imported; India makes >25 Mt oilseed cake a year, mostly feed. Companies lack a fast way to decide.
2. **The decision and the gap** (30 s): the five gaps G1–G6, one line each; "existing AI platforms chase novel molecules; nobody tells a mill owner whether this batch is safe, what it costs per kg protein versus imported isolate, and which test to run first."
3. **Live demo (about 100 s)**, three beats: (a) Groundnut cake → *TEST-FIRST, prior risk 53%* → type one lab number → verdict sharpens (Bayesian update); (b) chain Pareto and cost vs pea isolate with break-even; (c) "the one test to buy first" tornado.
4. **How it works (40 s):** gates → chains → Monte Carlo → value of information; evidence grading; where AI is used and what it is not allowed to do.
5. **Honesty and limits (20 s):** tags, transferred-evidence badge, PoC status, what we will validate first.
6. **Six-month plan and ask (30 s):** pilot partner type, lab tests (from engine), budget range (`assumed`), what we need (a food-grade mill, a lab, a brand to test).
7. **References** (clickable).

### 18.2 Hard questions and crisp answers
| Question | Answer |
|---|---|
| Where do your numbers come from? | Every cell is tagged measured/published/assumed/synthetic with a source; assumed cells are visible and ranked by how much they matter (EVPPI) |
| Where is the AI? | A probabilistic decision engine with value-of-information and Bayesian updating, plus an LLM restricted to parsing and explaining, with a verifier that rejects any number not in the engine output |
| Why not train a model? | There is no dataset of Indian by-product treatments large enough; a fake "trained" model would hide uncertainty, which is the opposite of what a safety-critical food decision needs |
| Autoclave and aflatoxin? | We do not claim it. Aflatoxin is heat-stable; the gate is measurement-driven and a failed batch is diverted |
| Accuracy of limiting compounds? | Backtested against literature statements for N cases (state N); next step is a prospective lab check |
| Isn't pea hypoallergenic? | Yes; groundnut cannot claim allergen-free. Our route targets applications where that is acceptable, and the tool flags it |
| Rice bran has ~15% protein. How do you reach 60%? | The tool says flour cannot; it requires a fractionation step and shows its cost and yield loss |
| Is the cost real? | A transparent model with ranges and a break-even price; the six-month plan replaces assumptions with quotes and pilot data |
| How do you validate the engine? | Predict P10–P90 for three batches, measure, report calibration coverage |
| Duty ambiguity? | Two sources disagree (43.96% vs 49.15%) and GST may be creditable; we expose it as a switch and show both |
| Difference from GFI's open TEA spreadsheets or NotCo/Shiru? | Those model one process or discover new molecules. We combine safety gating, chain search, cost vs import and value of information for commodity Indian by-products |
| What if the LLM hallucinates? | It cannot change numbers; the verifier blocks unmatched numbers; a deterministic template is the fallback |

### 18.3 Six-month plan (generated by `/plan`; placeholders until quotes arrive)
| Months | Work | Output | Cost basis |
|---|---|---|---|
| 0–1 | Source 3–5 batches (food-grade mills); composite sampling; gate tests (AFB1, FFA, heavy metals, micro) | Gate decisions on real lots | `lab_tests.json` (assumed ₹) |
| 1–3 | Bench trials of the top 2 chains per by-product; assay anti-nutrients before/after | Replace transferred evidence with measured evidence (grade A) | Reagents, labour |
| 3–4 | Sensory panel (triangle + scaling), solubility/emulsification/gelation | Calibrate the off-flavour index and functionality flags | Panel cost |
| 4–5 | Pilot run (decision volume ≈ 10 t cake) with a contract processor or institute pilot plant | Real yield, energy, water | Pilot fee |
| 5–6 | Re-run engine with measured data; customer sample trials; regulatory classification check | Updated ₹/kg protein vs pea; go/no-go for a plant | Staff + trials |
Total budget: computed by the engine from the tables; show a range tagged `assumed` (order of tens of lakhs of rupees, to be replaced by quotes).

---

## 19. References (put these as clickable links on the final slide) and notes

**Organisers / jury:** Hack the Fork 2026 India Edition Problem Statements PDF (provided); jury profiles (provided).

**Evidence used in this prompt (retrieved Oct 2026):**
- Singh et al. 2022, Protein for Human Consumption From Oilseed Cakes: https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2022.856401
- Murugeswari 2023, aflatoxin B1 in feed and raw materials in India: https://agris.fao.org/search/fr/records/6851787853e52c13fc76fde0
- Dubey et al. 2019, rice bran stabilization review: https://shura.shu.ac.uk/24906/
- Rice bran processing for human food (Assam Agricultural University): https://arccjournals.com/journal/asian-journal-of-dairy-and-food-research/DR-2233
- US5753283, stabilising rice bran: https://patents.google.com/patent/US5753283
- US12285029, microbial protein isolate from oilseed meals (India cake volumes): https://patents.google.com/patent/US12285029
- El-Kady & Farghaly, aflatoxin inactivation by heat: https://archive.org/download/biostor-278424/biostor-278424.pdf
- Shriram Institute, Aflatoxin in Groundnuts: https://www.shriraminstitute.org/wp-content/uploads/2022/08/Aflatoxin-in-Groundnuts.pdf
- Nature (1966), detoxification of groundnut meals: https://www.nature.com/articles/209406a0
- PBFIA via Agron Food Processing (90% imported; ₹4,500 → ₹9,000 crore): https://agronfoodprocessing.com/?p=31333
- GFI India orphan crops whitepaper coverage: https://vegconomist.com/agriculture-agribusiness/indias-orphan-crops-could-unlock-new-plant-protein-supply-chain-gfi-india-argues/
- India import tariff HS 35040099: https://eximpe.com/hsncode-finder/35040099 and https://treayo.com/en/hs/india/35040099
- Canada CBSA pea protein measures: https://www.cbsa-asfc.gc.ca/sima-lmsi/mif-mev/hpc-eng.html
- EU provisional duties on Chinese pea protein (31 Mar 2026): https://www.wko.at/oe/aussenwirtschaft/information-at-provisional-stage-pre-disclosure-1.pdf
- Expana plant-based protein report, Mar 2026: https://www.mintecglobal.com/hubfs/Expana%20Plant-Based%20Protein%20Report%20-%20March%202026.pdf
- Pea/legume protein export prices (Tridge): https://dir.tridge.com/prices/grass-pea-protein/CN
- USD/INR: https://banklive.net/en/convert/usd-to-inr
- GFI technical reports: https://gfi.org/science/technical-analyses-and-reports/ ; open mycoprotein TEA: https://www.frontiersin.org/articles/10.3389/fsufs.2023.1204307/full
- AI food platforms: https://link.springer.com/article/10.1007/s12393-025-09413-w ; https://yespress.io/shiru ; https://www.futuremarketinsights.com/reports/ai-in-food-ingredient-innovation-market
- Upcycling case studies: https://thespoon.tech/napiferyns-technology-upcycles-post-processed-rapeseed-into-usable-protein-powder/ ; https://www.foodprocessing.com/ingredients/article/55287812/the-benefits-and-challenges-of-using-upcycled-ingredients
- Batch variability and supply: https://www.profoodworld.com/sustainability/article/22958269/scaling-upcycled-ingredients-in-food-manufacturing-challenges-and-solutions ; https://www.foodnavigator.com/Article/2023/06/20/upcycled-ingredients-challenges-and-opportunities-in-securing-side-stream-supply/ ; https://sagentia.com/insight/development-and-scale-up-challenges-in-alternative-proteins-key-takeaways-from-our-roundtable/
- Indicative trader price listing (replace with AGMARKNET): https://m.indiamart.com/mahalakshmi-oils
- Official optional data (use the clickable links in the PS PDF): IFCT 2017, USDA FoodData Central (https://fdc.nal.usda.gov/), FooDB (https://foodb.ca/), Open Food Facts, AGMARKNET, e-NAM, FAOSTAT, HESTIA.
- User's own materials, cite as such: oilseed cake review draft, research plan (5 Aug 2026), PhD progress report (20 May 2026, with owner's permission).

**Honest notes on the research behind this prompt**
- I could not retrieve posts from X itself. Market sentiment above comes from trade press and conference roundtables, which consistently report batch variability, supply security and consistency as the main scale-up problems.
- Numbers tagged `[U]` come from the user's draft documents and were not independently verified. Two need special checking before use: the groundnut aflatoxin claim after autoclaving, and the model-based TEA figures.
- Duty rates and prices change; confirm before the pitch.

### DATA_TODO.md template (the coding assistant should generate the full list from the JSON `null`s)
| Priority | Cell | Needed value | Best source to check | Owner |
|---|---|---|---|---|
| 1 | Groundnut cake phytic acid % db (baseline) | PERT low/mode/high | IFCT 2017, literature | Data lead |
| 1 | Groundnut cake trypsin inhibitor baseline and reduction by moist heat | distribution + conditions | Panhwar 2005 (original), other TIA papers | Data lead |
| 1 | Rice bran (DORB) protein %, fat %, phytate %, ash % | ranges | IFCT/USDA/industry spec | Data lead |
| 1 | AE-IEP purity and recovery for groundnut and rice bran | ranges | Groundnut and rice-bran protein isolation papers | Data lead |
| 1 | Aflatoxin limits (India/EU) legal basis | limit, matrix, B1 vs total | FSSAI regulation, EU Reg. 1881/2006 as amended | Data lead |
| 2 | Heavy-metal limits for rice bran/derived ingredients | ppm | FSSAI / Codex | Data lead |
| 2 | Lab test costs and turnaround | ₹ ranges | NABL lab quotes, NIFTEM | Story lead |
| 2 | Energy, water, chemical, labour per step; capex references | per-kg values | Process-engineering papers, supplier quotes | Engine lead |
| 2 | Off-flavour baselines and weights by class | PERT | Sensory papers; later own panel | Data lead |
| 3 | Pea isolate India landed price evidence | ₹/kg | Importer quotes, customs data | Story lead |
| 3 | Lysine/limiting amino-acid scores | per by-product | USDA/IFCT/literature | Data lead |

---
*End of master prompt. Start with Section 17, Phase P0.*

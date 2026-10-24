# Phase reports

## Phase 0: Declare, repository and contracts

**Implemented**
- Folder layout per source plan §10.2. Additions from the website plan: `web/src/locales/`, `api/llm/`, `web/public/snapshots/`. Placeholder modules for later phases (including `flavour.py`), `data/schema/`, `api/routers/`, and placeholders for `scripts/build_snapshots.py` and `scripts/extract_rows_from_abstracts.py`.
- `engine/compass/models.py`:
  - `Tag` (measured/published/assumed/synthetic) and `Grade` (A–D).
  - `Dist`: pert, triangular, uniform or lognormal, with low ≤ mode ≤ high enforced.
  - `Param`: value, dist or null (null means missing data, listed in DATA_TODO), plus unit, tag, grade, source_id, alpha, conditions and notes. It accepts the source plan's field names `evidence_grade` and `applicability`.
  - `Value` and `Range` (P10/P50/P90) for outputs, each with provenance.
- `api/schemas.py`: the request (§8.3) and `/analyze` response (§14.2) as strict Pydantic models. Unknown fields are rejected, percentages must be 0–100, and duty modes are the three from §12.8.
- `api/main.py`: `/health` and a stub `/analyze` that validates the §8.3 example payload. It returns the full §14.2 shape (meta, verdict, gates, diagnosis, chains, pea, voi, plan, limitations). Every number is a zero placeholder tagged `synthetic`, and `meta.is_stub` is true. The CORS allow-list comes from `CORS_ORIGINS`.
- `web/`: Vite + React 18 + TS + Tailwind with shadcn/ui conventions, TanStack Query and react-i18next (en; hi falls back to en). Shows "API: ok" through the `/api` dev proxy.
- `scripts/gen_types.sh` writes `web/src/api/types.ts` with openapi-typescript. The generated file is committed.
- `.env.example`, `.gitignore`, `README.md`, `DATA_TODO.md` (seeded from §19), `Makefile` (`setup api web test types snapshots lint`).

**Tested**
- pytest: 11 passing. Covers model validators, source-plan field aliases, `/health`, the §8.3 example accepted, every numeric leaf in the stub tagged `synthetic`, 422 on unknown fields and 422 on protein > 100%.
- `npm run build`, `npm run lint`, `ruff` and `black` pass.
- Playwright at 360 px: health badge reads "API: ok" (`docs/phase0-health-360.png`).

**Decisions (one line each)**
- Duty mode: the §8.3 example writes `bcd_only_igst_credited`, while §12.8 uses `bcd_only_igst_credited_22`. The §12.8 names are used.
- LLM provider: Amazon Bedrock first (website plan R1) instead of the source plan's Groq. The client sits behind one interface (Phase 6).
- Every number in the response carries a tag, so the §14.2 example's bare numbers (such as `p_go: 0.41`) become `{value, tag, …}`.

**Not done / known limits**
- Declaring Problem Statement 2 with the organisers is a manual step for the team.
- Built and tested on Python 3.13. Pins are chosen to also work on 3.11.
- Initial JS is about 80 KB gzipped (budget 250 KB).

## Phase 1: Data layer

**Implemented**
- `engine/compass/data.py`, the only place the engine reads files:
  - Strict Pydantic schema per file.
  - Cross-reference checks: source ids, compounds, species, gates, tests, equipment, tiers, precedence names and preset ids.
  - Unit bounds: `%` must be 0–100; fraction and probability must be 0–1.
  - A published or measured number must have a source.
  - Errors name the file and the row id, e.g. `byproducts.json: row 'groundnut_cake' at …`.
- Nine data files in `/data` (the eight from §11.4 plus `presets.json` for `/presets`):
  - 3 by-products, 11 compounds, 8 treatments (7 plus optional `ethanol_wash`) with the §12.4 precedence rules.
  - 3 applications with §11.5 tolerances and tier thresholds.
  - Costs: pea isolate inputs, 3 duty modes, 3 shock scenarios, capital-recovery (CRF) inputs, decision volume, engine and readiness config.
  - Gates G1–G7 with limits and priors, 13 lab tests, 30 sources, 3 presets.
- `data/schema/*.schema.json`: JSON Schema exported from the models.
- CLI:
  - `python -m compass.data --report` prints counts by tag and grade, A/B completeness, and missing inputs per preset.
  - `--todo` regenerates `DATA_TODO.md`, sorted by priority, with missing values before assumed ones.
  - `--schema` exports the schemas.
  - Makefile targets: `make data` and `make todo`.
- `/health` now reports the real dataset version. The API loads and validates `/data` at startup.
- `data/_staging/`: candidate rows for human review. The engine does not read them.
  - Desk-research candidates were removed on the team's instruction (see "Source policy" below).
  - 4 from the PhD report, tagged `measured`/B, waiting for the owner's permission. These are in `phd_pending.local.json`, which git ignores, so they never reach the repo.

**Checked against the uploaded documents (24 Oct)**
- Groundnut cake proximate composition matches the final review's Table 2 (dry-matter basis, citing Karnika & Asha 2025). The unit is now `% dry matter`.
- All Table 7/8 treatment effects match the final review. Each row now records its cited primary paper in `conditions.cites`, under the `user_review_final` source.
- Almond cake values match the research plan (5 Aug 2026).
- Groundnut limiting amino acids: lysine and threonine (final review Table 3).
- AE-IEP purity and recovery now use the final review's Table 11: 0.85–0.92 and 0.55–0.70, generic to oilseed cakes, α 0.4. They replace the source plan's assumed 0.75–0.90 and 0.40–0.70.
- The final review still says sorting plus autoclaving brings AFB1 below 2 ppb (citing Panhwar 2005). As §11.3 requires, this is not encoded; it is noted on `moist_heat`.

**Tested**
- pytest: 29 passing. Covers:
  - Every file loads, and every source id resolves.
  - Distributions are ordered and units stay within bounds.
  - Published numbers have sources, and no `measured` rows are in the main data.
  - Review-sourced rows are grade C and flagged "verify".
  - No treatment claims to remove aflatoxin.
  - Evidence transferred from another species has α < 0.7.
  - Broken rows fail with the file and row id: bad range, % out of range, unknown source, unknown compound.
  - Report totals add up. DATA_TODO skips config values.
  - Preset input lists respect exclusions and species.
  - Staging rows are valid.
  - Presets validate as API requests.
- `ruff` and `black` pass.

**Exit gate: NOT fully met.** "The three presets have every required input (real or tagged `assumed`)" fails. SR-2 forbids inventing values, so missing cells stay `null`. Current counts: groundnut_beverage 106 missing, rice_bran_snack 115, almond_meat 91. Groundnut breakdown:
- Treatment resources (energy, water, chemicals, labour, time, reference capex): 49.
- Lab test cost, turnaround and CV: 21.
- Treatment yield and protein retention: 12.
- Flavour baselines and side-notes: 8.
- Compound floors: 3.
- AE-IEP partition of compounds: 3.
- Groundnut phytate and tannin baselines: 2.
- Utilities and overheads: 5.

The gate, verdict and pea-parity paths have their inputs. The cost model and the off-flavour index do not.

**Not done / known limits**
- 25 values are flagged "verify", including the aflatoxin limits (30 ppb domestic and 4 ppb EU, both from the Shriram summary cited in the source plan).
- Which tariff site gives 43.96% and which gives 49.15% is not recorded; both sites were unreachable.
- The protein and ash tables in the PhD report are images and were not read.
- Almond cake has no anti-nutrient baselines. Literature should confirm that none exceed tolerances before GT5 is claimed.

**Source policy (team instruction, 24 Oct)**
- Use only references cited in the team's documents (source plan, website plan, review drafts, research plan, PhD report) and the organiser resource list.
- The organiser resources are now in `sources.json` as `faostat`, `ifct2017`, `usda_fdc`, `foodb`, `openfoodfacts`, `agmarknet`, `datagov_mandi_daily` and `datagov_mandi_variety`.
- All 6 desk-research sources and their 9 staged candidates were removed. Dataset version: `2026-10-24.3`.

## Phase 2: Engine core

**Implemented**
- `sampling.py`:
  - PERT (λ = 4), triangular, uniform and lognormal, sampled by inverse CDF from one seeded Sobol point set (Latin hypercube optional).
  - Extrapolation penalty: the range is widened by 1 + k(1 − α) around the mode and clipped to the unit's physical bounds.
  - Provenance propagation: a derived number takes the weakest tag and grade, the lowest α and the union of all sources.
  - P10/P50/P90 summaries returned as tagged `Range` / `Value` objects.
- `effects.py`:
  - Wet-to-dry-basis conversion and true protein = N × f.
  - Proximate-sum warning when the parts don't add up to 100 ± 5%.
  - First-order compound reduction with a floor. No synergy terms.
  - Mass and protein balance: process steps (M·m, P·ρ) and fractionation (P·ρ, M = P/π), with protein fraction capped at 0.95.
  - Tier assignment by final protein %.
- `cost.py`: energy, water, chemicals, labour and capital per step. Capital uses the six-tenths rule and CRF at 12% over 10 years, on 300 days at 80% utilisation. Adds QA and overhead, then converts to ₹/kg protein, kWh/kg protein and L/kg protein.
- `pea.py`: landed cost per kg product and per kg protein, price we can charge, margin, closed-form break-even base price, and shock scenarios (set or scale a field).
- `scripts/bench_engine.py` (`make bench`): groundnut cake → phytase → AE-IEP at 8,192 draws.

**Missing-data policy (stated assumptions)**
- A missing fraction or probability (yields, protein retention, AE-IEP partition) is sampled from its full feasible range U(0, 1) and tagged `assumed`, grade D, status `no_data`. Ranges stay wide, so value-of-information analysis will point at measuring them.
- Any other missing quantity (₹, kWh, litres, hours) is not computable. The cost model leaves it out, names it in `missing`, and the total becomes a lower bound that the API must label as such. No numbers are invented.
- A missing compound floor is treated as 0.
- Lognormal rows read low/high as P5/P95.
- Overhead is a share of processing cost, excluding raw material.

**Tested**
- pytest: 53 passing, of which 24 are new. Covers:
  - PERT mean within 1% of the analytic value, and draws within bounds (hypothesis).
  - Lognormal P5/P95, widening and clipping, and same seed → same draws.
  - Missing-data policy and provenance combination.
  - Protein out ≤ protein in; fraction ≤ 0.95; no NaN (hypothesis).
  - Reduction stays between the floor and the start level; steps compose without synergy.
  - Normalisation and tiers.
  - CRF and the six-tenths rule; cost ≥ raw cost (hypothesis); missing components named; larger scale lowers capital per kg.
  - The §12.8 sanity example: ₹562 and ₹476 per kg protein.
  - Break-even inverts landed cost; a higher pea price never lowers the margin; scenarios.
- `make bench`: 0.08–0.11 s at 8,192 draws (target < 1 s). Its process inputs are synthetic timing values defined in the script only.
- The engine imports no web or LLM code.

**Exit gate: met.** Mass-balance and pea tests pass.

**Known limits**
- Inputs are independent (identity correlation), as in §12.9; this is listed as a limitation.
- A point value with α < 1 has no range to widen, so it stays constant; the moist-heat TIA value has α = 1 anyway.

## Phase 3: Gates, diagnosis, chains and `/analyze`

**Implemented**
- `compass/contract.py`: the §8.3 request and §14.2 result as engine-side Pydantic models; `api/schemas.py` re-exports them.
  - Additions to §14.2:
    - gate `kind`, `reasons`, `measured`/`limit`, and a `FLAG` state for G6/G7;
    - diagnosis `role`/`severity`/`limiting`, plus `issues` chips;
    - per-chain `criteria` with P(pass), `cost_missing`, `margin_vs_pea`, `no_data_inputs`;
    - pea `inputs`, the B2B cross-check and the break-even note.
  - Request additions: `constraints.no_solvents` and `n_draws`.
  - `voi` and `plan` stay null until Phase 5.
- `gates.py`: G1–G7 per §12.1.
  - G1 uses measured thresholds (≤ 0.5·L / ≤ L / > L), or the prior P(fail) 0.53 with the sorted-supply odds multiplier.
  - G2 covers FFA, the 6 h window and stabilisation. G3 handles a null limit as TEST-FIRST, "no limit available". G4 checks solvent route and certificate. G5 checks provenance.
  - G6/G7 are flags; an allergen-free claim fails G6.
  - Every gate gives its reasons, required test and what flips it. Treatments never clear a gate.
- `diagnosis.py`: gate compounds are listed first. Each tunable compound gets exceedance ratio, P(exceed), severity and rank, and the top one with P(exceed) > 0 is marked limiting. A compound without a tolerance shows "no limit available (qualitative)".
  - Chips: protein density gap, amino-acid limitation ("blend, not treatment"), functionality caveat, allergen, "no treatment needed", and "diagnosis blocked" when compound data are missing.
- `chains.py`: candidates are filtered by exclusions, no-solvents, equipment and relevance (a treatment with no listed effect on the by-product is skipped unless it fractionates or extrudes). DFS then applies every §12.4 rule:
  - stabilise first for rice bran, and before wet steps;
  - phytase before AE-IEP; never phytase → moist heat;
  - SSF and soak/germinate are mutually exclusive;
  - one fractionation step, which ends the chain (extrude after it only for meat analogue);
  - extrude only first or last; length ≤ 4.
  - Raw flour is always included; the cap is 60 chains.
- `flavour.py`: the off-flavour index per §12.6. It returns "not computable" while the dataset has no sensory baselines.
- `montecarlo.py`: all chains are evaluated on the same draws. Per draw it computes final protein %, retention, compound concentrations (mass-tracked), OFI, cost (§12.7), margin vs pea, and the joint spec indicator over the criteria that can be evaluated.
- `analyze.py`:
  - Normalisation: dry basis, true protein = N × f.
  - Batch measurements override dataset values and are tagged measured, grade A.
  - Pea block with 3 shocks, the B2B cross-check and break-even.
  - Pruning rule 8a: P10 cost above the cap.
  - Ranking by P(spec), then P50 cost. Badges: highest P(spec), cheapest viable, transferred, cost lower bound, cost not computable, not recommended.
  - Verdict per §12.14 rules 1–10.
  - P(GO) = P(gates pass) × P(spec), labelled an upper bound when a TEST-FIRST gate has no prior.
- API:
  - `POST /analyze` (422 with readable messages for unknown ids);
  - `GET /presets`; `GET /data/{file}` (allow-listed) and `/data/report`;
  - 64 KB request body limit.
- `web/src/api/types.ts` regenerated; the web app builds against it. Engine version 0.2.0.

**Decisions (one line each)**
- A process step with no yield and no retention data keeps protein % unchanged (§7.3 "treated flour ~ protein as-is"); only the loss is uncertain, U(0, 1).
- A missing compound floor is 0. Compound concentrations are tracked as mass per kg raw, divided by product mass.
- Empty `equipment` means "not stated" (no filter). The rice-bran and almond presets no longer restrict equipment.
- An unknown oil route defaults to the by-product's first listed route (groundnut: cold-pressed), and the response says so.
- Ruff no longer checks line length (black owns it; long user-facing strings stay unwrapped).

**Tested**
- pytest: 68 passing.
- GT1–GT6:
  - GT1: TEST-FIRST, prior 0.53 shown, never GO.
  - GT2: NO-GO, no chains, "divert to feed or re-source".
  - GT3: G2 FAIL.
  - GT4: G2 PASS, protein gap flagged, raw flour P(spec) = 0, only AE-IEP chains viable.
  - GT5: "no treatment needed", allergen flag, price flag, chains shown.
  - GT6: no ethanol_wash.
- Also tested:
  - every numeric leaf tagged; same seed → identical result;
  - G1 pass at 10 ppb; an allergen-free claim fails;
  - a measured phytate is used and tagged;
  - chain rules hold for every by-product × application; exclusions never add chains; equipment and no-solvents filters work;
  - API: §8.3 example, readable 422s, 413 for oversized bodies, presets, data allow-list.
- Timing: all three presets < 3 s (groundnut 0.3 s at 8,192 draws; 0.27 s over HTTP).

**Preset results now (all costs are lower bounds; process-cost data missing)**
- Groundnut → beverage: TEST-FIRST (G1 prior 0.53, G5). P(GO) ≤ 0.32. Limiting compound: trypsin inhibitor. Top chain: moist_heat + ae_iep, isolate, P(spec) 0.68, transferred evidence. Pea landed ≈ ₹489/kg protein.
- Rice bran → snack: TEST-FIRST (G2–G5). Protein gap flagged; diagnosis blocked (no phytate data). Only stabilise + ae_iep chains meet spec.
- Almond → meat analogue: TEST-FIRST (G5). No treatment needed; allergen flag; cost not computable (price missing). Only ae_iep chains reach 55% protein.

**Exit gate:** GT1–GT6 pass; all three presets return valid JSON in < 3 s; types regenerated and compile. "Preset 1 renders end-to-end in the UI" needs Phase 4.

**Known limits**
- The literature backtest of limiting compounds (§15) is not done yet. It needs non-core cakes and their compounds in `/data`.
- GO is reachable only when every stop gate passes; with G5 unknown in all presets, they are TEST-FIRST.

## Phase 4: Frontend core and design system

**Implemented**
- **Design tokens:** light and dark colours as CSS variables, a visible focus ring, reduced-motion support, and focus never hidden behind the sticky header. M/P/A/S tag chips use letter plus colour, with the full word as the accessible name. Verdicts and gates use icon plus text (✓ GO, ✕ NO-GO, ⚑ TEST-FIRST, ℹ FLAG).
- **`<Num/>`:** the only way numbers are rendered.
  - Shows en-IN formatting chosen by unit (₹ grouping 1,00,000, %, probability), the P10–P90 range, the tag chip, and a "transferred" badge when α < 0.7.
  - Hover or keyboard focus shows a preview; click, tap or Enter pins it open (value, range, tag, grade, α, linked source citations); Escape closes it.
  - The global "Show sources" toggle prints source ids inline.
- **Layout:** top bar (title, API status, show sources, language switch), a desktop stepper over 6 screens, a mobile bottom tab bar (Input, Verdict, Chains, Cost, Next), a skip link, focus moved to the new screen, an "Analysis updated" live region, and a footer with disclaimer, PoC note, privacy note and limitations link.
- **Input:**
  - The 3 presets (Analyse, or edit in the form).
  - react-hook-form + Zod, with every message an i18n key. Fields: by-product, use, market, scale, price in ₹/kg, ₹/quintal or ₹/tonne (converted to ₹/kg), targets per kg protein, no-solvents, equipment and exclusions.
  - A collapsible "Own batch data" section; values entered are tagged M. Process context uses Yes / No / Not known.
  - Each field shows its tag, or "default" when empty. Data-completeness meter from `/data/report`.
- **Verdict + gates:** a large verdict card (grade, P(GO) with its "≤ upper bound" note, reasons, actions, disclaimer) and gate cards (state, prior, measured value, limit, required test, what flips it, reasons and flags).
- **Diagnosis:** a bar chart of level ÷ tolerance with P10–P90 whiskers and the tolerance line at 1, a text summary, a "show as table" toggle, and the table (role, level, tolerance or "no limit available", P(exceed), limiting badge) plus issue chips.
- **Chains:** a sortable table (rank, retained, protein %, ₹/kg protein, P(spec)) using `aria-sort`. A row opens the before/after panel (raw cake vs chain), spec criteria with P(pass), transferred evidence, inputs with no data, and missing cost parts.
- **Cost vs pea:**
  - Stacked bars of our cost breakdown vs the pea landed split (base, freight, duty), with a lower-bound warning, margin, P(margin > 0), break-even and the Indian B2B cross-check.
  - Accessible Radix sliders (pea base, USD/INR, freight, scale), a duty-mode select, a GST-credit toggle, reset, and shock-scenario buttons.
  - Slider changes re-call `/analyze` with a 400 ms debounce.
- **Next:** the tests the gates require, plus the full limitations list. The EVPPI ranking comes in Phase 5.
- **States:** loading skeletons, error card with retry, "needs input" card. If `/analyze` fails or times out (8 s) for an unmodified preset, the app loads `/snapshots/<preset>.<lang>.json` with the "Demo snapshot (offline)" badge. The snapshot files are produced in Phase 8.
- **Engine/API:**
  - New `raw_price_inr_per_kg` request field (makes almond cost computable).
  - Response models now mark defaulted fields as required (`json_schema_serialization_defaults_required`).
  - Types are generated with `--default-non-nullable false`, so request defaults stay optional.
- **Libraries added** (pinned; all in plan §8.1): zustand, react-hook-form, zod, @hookform/resolvers, Radix popover and slider. Dev: Testing Library, jsdom, axe-core.
- **Charts are plain SVG instead of Recharts.** Reasons: bundle budget (NFR-02), and the plan's own risk note about Recharts error bars and accessibility. Every chart has a text summary or table.

**Tested**
- Vitest, 9 passing:
  - `<Num/>` formats ₹1,00,000 and always shows a chip; shows P10–P90 and the transferred badge; opens on click and closes with Escape.
  - The form rejects protein > 100, needs by-product and use, converts ₹/quintal → ₹/kg, flags protein + moisture > 100, and round-trips a preset.
  - Indian formatting, including lakh and crore.
- Playwright (`npm run e2e`, all checks pass):
  - Preset 1 → TEST-FIRST, with G1 prior 53%.
  - Cost screen: the pea-base slider (keyboard) changes landed cost ₹489 → ₹614.
  - Keyboard-only: Tab to the preset, Enter runs it, stepper navigation by keyboard.
  - A chain row opens its detail; diagnosis marks the trypsin inhibitor as limiting.
  - axe-core (WCAG 2.0/2.1/2.2 A and AA): 0 serious or critical issues on Input, Verdict, Chains, Cost and Next at 360 px, and on Diagnosis, Chains and Cost at 1280 px.
  - No horizontal scroll at 1280 px; every rendered number has a chip.
- Screenshots at 360 px and 1280 px are in `docs/screenshots/`.
- Build: initial JS 143 KB gzipped (budget 250 KB). pytest: 69 passing.

**Exit gate: met.** J1 runs up to the cost screen on the real API.

**Known limits**
- Hindi strings arrive in Phase 7; the language switch exists, and Hindi falls back to English.
- The preset 1 batch values are synthetic (as the source plan §8.3 example), so every derived number in that preset is correctly tagged S.
- The chains table shows all chains (up to 60); there is no paging.
- Lighthouse mobile has not been run yet (Phase 8).

## Phase 5: Decision intelligence

**Implemented**
- **Full Monte Carlo:** 8,192 Sobol draws (seeded), joint P(spec) per chain. An unmeasured aflatoxin gate (G1) is sampled as Bernoulli(prior) on its own Sobol dimension, so P(GO) = P(gate pass) × P(spec | pass).
- **`voi.py`** (§12.9):
  - Utility per draw: campaign protein × margin vs pea if the spec is met and G1 passes; otherwise minus the campaign's variable cost. Feed = 0. Shown on screen with the 10 t campaign.
  - E_now, EVPI, and EVPPI by 25 equal-count bins (one bin per value for discrete inputs) for every uncertain input.
  - For a test that informs several inputs (e.g. proximate/Kjeldahl → protein, yields, retention): a regression estimator on a quadratic basis.
  - EVSI = EVPPI × R, with R from the assay CV. Without a CV, R = 1 and EVSI is flagged as an upper bound. ROI = EVSI / cost.
  - Recommendation: argmax ROI subject to EVSI > cost. Honest alternatives: "No test is worth its cost: decide now", "No measurement can change the decision", or, while lab costs are missing, the highest-EVSI test with "buy it if a quote is below ₹X".
- **`pareto.py`** (§12.10): non-dominated chains on median retention, cost and OFI (when computable), among viable chains only (P(spec) ≥ 0.2). P(A dominates B) is computed on common draws, and pairs are "statistically tied" below 0.8. Three named picks: best expected value, safest, cheapest viable.
- **Ranking** (rule 3): by E[U] when it is computable for every chain; never recommends a chain with P(spec) < 0.2.
- **`readiness.py`** (§12.11): decision-grade / hypothesis-grade / not viable from config thresholds, shown on screen. The checklist covers gates, P(spec) ≥ 0.80, EVPI/|E_now| ≤ 0.15 and ≥ 70% of the top-5 drivers graded A/B. "What must be demonstrated" lists the top value drivers (test + acceptance criterion) and the top chain's transferred evidence.
- **`plan.py`** (§12.13): rule-based validation plan.
  - Tests come from the top value-of-information tests and the outstanding gate tests, each with method, replicates (≥ 3), sample plan (composite of ≥ 10 sub-samples for AFB1), cost and turnaround from `lab_tests.json`, an acceptance criterion derived from targets and limits, and why it's included.
  - The 6-month timeline follows the plan's template, with a pilot-partner type.
  - Budget is "not computable" while lab costs are missing.
- **UI:**
  - Next screen: test-to-buy-first card, EVPPI tornado (top 8, with table toggle), all tests ranked (EVSI, cost, ROI), decision assumptions (campaign, E_now, EVPI), readiness grade and checklist, gate tests, validation plan, timeline, budget, partner, limitations.
  - Chains screen: Pareto scatter (cost × retention, dot size = P(spec), P10–P90 bars both ways, front outlined, ties listed), an E[U] column, and pick badges.
- **Bug fixed** (since Phase 4): table scroll wrappers weren't positioned, so screen-reader-only spans inside them widened the page to 561 px on phones. Wrappers are now positioned and keyboard-focusable (axe `scrollable-region-focusable`). The e2e test now checks there is no horizontal scroll at 360 px on every screen.
- Engine version 0.3.0.

**Preset 1 (groundnut → beverage) now says**
- TEST-FIRST, hypothesis-grade.
- Every chain has negative E[U] today, so selling as feed is best (E_now = 0).
- EVPI ≈ ₹3.15 lakh per decision.
- Top value drivers: aflatoxin status of this lot (₹1.45 lakh), then the protein retention of the first step (no data), then the AE-IEP trypsin-inhibitor partition. Pea price research ranks low (≈ ₹15,000).
- Test to buy first: proximate + Kjeldahl, i.e. bench yield and retention (EVSI ≈ ₹1.52 lakh, upper bound), narrowly ahead of AFB1 HPLC. Lab costs aren't in the dataset, so the card says to buy if a quote is below that value.

**Tested**
- pytest: 78 passing. New tests cover:
  - EVPPI ≥ 0 and ≤ EVPI (hypothesis); an informative input carries the value and pure noise ≈ 0; a binary input recovers EVPI exactly.
  - Reliability; recommendation rules, including "no test is worth its cost" and "decide now".
  - Readiness rules: decision-grade, hypothesis-grade (low P(spec), weak evidence), not viable (gate fail, P(spec) < 0.2, negative margin).
  - Preset 1 recommends a test with EVSI > 0, readiness, plan and picks.
  - Monotonicity: a higher pea price never lowers P(margin > 0).
  - Measuring AFB1 removes its value of information.
  - Regression snapshot of preset 1 (`tests/golden/preset1.json`).
- GT1–GT6 still pass.
- vitest: 9 passing. e2e: all checks pass, including the next-screen cards, no horizontal scroll at 360 px on every screen, and axe 0 serious/critical.
- `/analyze` for preset 1: about 0.5 s over HTTP at 8,192 draws (target < 3 s), so no draw reduction was needed for sliders.
- Initial JS 147 KB gzipped.

**Exit gate: met.** GT1–GT6 pass; J1 runs to "Next step" with a recommended test (₹ value), readiness label and checklist.

**Known limits**
- Test values use lower-bound costs, so margins are optimistic. Gates without a prior (G2–G5) are not in the utility.
- EVSI is an upper bound while assay CVs are missing. ROI and "worth it" need lab quotes in `lab_tests.json`.
- Almond cake has no price, so its utility and value of information are "not computable"; enter a price on the Input screen.
- Pareto colour by OFI is omitted because OFI is not computable without sensory data.

## Phase 6: AI layer (Bedrock, number verifier, Bayesian update)

**Implemented**
- **`api/llm/client.py`:**
  - Provider switch (`LLM_PROVIDER`): Amazon Bedrock `converse` (us-east-1, `BEDROCK_MODEL_ID`, temperature 0.2, 700 tokens), optional Groq (OpenAI-compatible endpoint, `GROQ_MODEL_ID`), or the template.
  - Token bucket at 1 request/s (requests queue), 20 s timeout, one retry, cache by hash(endpoint, input, language, model) in memory and `api/.cache/`.
  - Logs provider, model, latency and verifier result; never user text.
  - Gemini was not implemented; Groq covers the optional second provider.
- **`api/llm/prompts.py`:** the formatter system prompt; tasks for explain, plan and parse; user data wrapped in delimiters and marked as data.
- **`api/llm/verify.py`:** the number extractor (₹ en-IN grouping, %, decimals, ranges, lakh/crore, negatives, ids like G1/AFB1 skipped) and the matcher at displayed precision (fraction ↔ %). It also rejects unknown source ids.
- **`api/llm/service.py`:**
  - `/explain` and `/plan` run LLM → verifier → one retry naming the bad numbers → template.
  - `/parse-text` takes LLM JSON and keeps only allowed keys; its numbers must appear in the user's text, or the rule-based reader (`rules.py`, English + common Hindi words) is used. It validates against the request schema, returns the filled payload plus changed fields, and never analyses.
- **`api/llm/template.py`:** deterministic explanation and plan paragraph from engine numbers (en-IN).
- **`engine/compass/update.py` and `learning.py`** (§12.12):
  - Lognormal conjugate update with the assay CV; without a CV the value is treated as exact and the UI says so.
  - Likelihood-ratio update of the G1 prior from an ELISA screen (sensitivity 0.95, specificity 0.90, assumed). An HPLC value sets the measured AFB1.
  - The request gains `evidence` overrides (tag M, grade A, α = 1); unknown keys are rejected.
  - `/update-evidence` returns prior, measurement, posterior, a before/after snapshot (verdict, grade, P(GO), best chain, P(spec), recommended test, EVPPI) and the request to continue with.
  - The sampler now clips draws to physical unit bounds.
- **API:** `/explain`, `/plan`, `/parse-text`, `/update-evidence`; an LRU cache of analysis results; 10/min/IP rate limit on the AI endpoints. `/explain` re-runs the analysis server-side, so the verifier checks against real engine output, never client-sent numbers.
- **UI:**
  - Verdict: AI summary card (plain text; badge "AI-written summary; numbers checked against the engine" or "Template summary", plus the note).
  - Input: "Describe in words" box → "Fill the form" → filled fields highlighted, batch section opened, message "check the highlighted fields, then press Analyse".
  - Next: "Enter your lab result" (input from the value-of-information list and compounds; AFB1 as HPLC ppb or ELISA ±; optional CV and method) → prior → posterior and a before/after table with changes marked → "Keep this result".
- **Docs:** `docs/AI.md` covers what the AI does and does not do, the guardrails and how to run with Bedrock. `.env.example` adds `GROQ_MODEL_ID`. Engine version 0.4.0.

**Demo moment, tested end to end:** groundnut → beverage, enter phytic acid 1.8% (beverage limit 1.0%):
- grade hypothesis → not viable;
- P(GO) ≤ 32% → ≤ 9.4%;
- best chain extrude + AE-IEP → extrude + phytase + AE-IEP, P(spec) 68% → 20%;
- top value driver aflatoxin status → AE-IEP phytate partition.

**Tested**
- pytest: 100 passing.
  - GT7: injected ₹777 is rejected on both attempts and the template is used.
  - A verified LLM text is used; the template passes its own verifier; unknown sources are rejected.
  - Token bucket: 11 calls ≥ 1 s apart.
  - Rule parser: the J3 sentence, Hindi "मूंगफली", ₹/quintal → ₹/kg.
  - An LLM-parsed invented number falls back to rules.
  - `/parse-text` fills but never analyses; `/explain` and `/plan` work without an LLM; rate limit returns 429 on the 11th call; user text is wrapped.
  - GT8: measured phytate is M/A, and P(spec) and EVPPI change.
  - Posterior variance < prior; LR update; HPLC 60 ppb → NO-GO; ELISA negative lowers P(fail) and keeps TEST-FIRST; fraction inputs reject percentages; unknown evidence is rejected; `/update-evidence` endpoint.
- vitest: 9 passing. e2e: all checks pass, including the AI summary badge, lab result before/after, "keep this result" and J3 (filled and highlighted, nothing analysed until the user confirms). axe 0 serious/critical.

**Exit gate: met on the template path.** GT7 and GT8 pass. "Enter one lab number → recommendation sharpens" works offline (template).

**Not done / needs the team**
- Live Bedrock was not exercised: no AWS credentials or model id in this environment. On the demo laptop, set `AWS_PROFILE`, `LLM_PROVIDER=bedrock` and `BEDROCK_MODEL_ID` from the console and check the badge says "AI-written".
- Hindi explanations and voice input are Phase 7.

## Phase 7: Hindi and voice input

**Implemented**
- **`web/src/locales/hi.json`:** 330 Hindi strings covering every screen, form, error message, chart summary, AI, lab-result and voice text.
  - Safety wording is **not** in the Hindi file, so it falls back to English until a Hindi-reading reviewer writes and checks it (plan §7.2: never machine-translate safety strings silently). That covers verdict labels GO / NO-GO / TEST-FIRST, gate states, the disclaimers and the M/P/A/S letters.
  - In Hindi a note under the header says so.
  - Engine-generated reasons, limitations and acceptance criteria also stay in English.
- **`locales/review.json`:** review status. Reviewer: none yet; `ui_strings_reviewed: false`; the 14 keys kept in English are listed.
- **`scripts/check-locales.mjs`** (part of `npm test`): every English key exists in Hindi unless it is kept in English; no stale Hindi keys; `{{placeholders}}` match.
- **`locales/glossary.hi.json` + `gloss()`:** technical terms stay in English with a Hindi gloss, e.g. "Aflatoxin B1 (एफ्लाटॉक्सिन)", in diagnosis rows and gate cards.
- **Language handling:** Noto Sans Devanagari loads from Google Fonts (`display=swap`) only when Hindi is selected; `<html lang>` follows the language; the choice is stored in `localStorage` (try/catch); numbers stay `en-IN` (₹ grouping unchanged).
- **`/explain` with `lang=hi`:**
  - The Bedrock prompt asks for simple Hindi with Latin digits, English verdict labels and English technical terms with a Hindi gloss.
  - The Hindi template keeps engine reasons and the disclaimer in English.
  - The verifier converts Devanagari digits (०–९) before checking, so an invented "₹७७७" is caught.
  - The response carries `lang` and `machine_translated`. The UI shows a "machine-written Hindi; numbers checked" badge and a "Show English" toggle.
- **Voice (`useSpeechInput`):**
  - Detects `SpeechRecognition` or `webkitSpeechRecognition`; locale `en-IN` or `hi-IN` follows the UI.
  - States: requesting → listening (pulsing mic, live interim transcript) → processing → ready.
  - Errors: blocked microphone, no speech, network, stopped early, failure; each offers Try again and Type instead.
  - Privacy note next to the mic. The transcript is appended to the editable text box; nothing is submitted. The mic is hidden when unsupported (Firefox).
- **Read-aloud (`useReadAloud`, Tier 3):** reads the summary with `speechSynthesis`, offered only when a voice for the language exists (exact `-IN` voice preferred), with a stop button.
- **Docs:** `docs/voice-tests.md` lists the automated results and a manual-test table for rehearsal.

**Tested**
- vitest: 14 passing (5 new).
  - Voice states with a mocked recognizer: hi-IN, interim, final transcript handed over.
  - Error mapping (denied, no speech); mic hidden without the API.
  - Read-aloud only with a matching voice; glossary.
- Locale check: 330 strings ok, 14 kept in English.
- pytest: 102 passing, including the Hindi template passing its verifier with the disclaimer kept in English, and Devanagari 777 rejected.
- e2e: all checks pass.
  - Mic offered in Chromium.
  - Hindi: `html lang=hi`, font loaded on demand, Hindi navigation, verdict label kept in English, safety note shown.
  - Hindi summary with machine-written badge; the "Show English" toggle works; ₹ formatting unchanged.
  - axe: 0 serious/critical on the Hindi verdict screen.
- Visual check: Devanagari renders correctly (`document.fonts.check` true).

**Exit gate: partly met.**
- J6 (Hindi user) works.
- J3 by text works everywhere, and the voice path is unit-tested.
- The plan asks for "J3 works by voice on at least one browser". That needs a real microphone and was not tested here; see `docs/voice-tests.md`.
- "Reviewed flag true for all safety strings" is not met by design: no Hindi reviewer was available, so safety strings stay in English, as the plan instructs in that case.

**Not done / needs the team**
- A Hindi-reading teammate should review `hi.json` (all UI strings were drafted by the coding assistant). They should then write the 14 safety strings, add them to `hi.json` and set `reviewed` in `review.json`.
- Manual voice tests on Chrome desktop, Chrome Android and Safari iOS, in quiet and noisy rooms.
- Hindi snapshots (`<preset>.hi.json`) are produced by the Phase 8 snapshot script.

## Phase 8: Hardening, accessibility, snapshots and deployment

**Implemented**
- **Snapshots (`scripts/build_snapshots.py`, `make snapshots`):**
  - Runs `/analyze` and the template `/explain` for each preset × {en, hi}.
  - Writes `web/public/snapshots/<preset>.<lang>.json` and `.explain.json`, plus `presets.json`.
  - Writes `web/public/offline-data/`, the form options used when the API cannot be reached.
  - Every file is stamped with `engine_version` (now 0.5.0), `dataset_version` and `generated_at`.
- **Frontend fallback (`api/client.ts`, `withFallback`):**
  - If `/analyze`, `/presets`, `/data/*` or `/explain` fails or takes longer than 8 s, the app loads the matching snapshot or offline file.
  - A "Demo snapshot (offline)" badge shows the version stamp.
  - The fallback only applies to unmodified presets (`presetId` in the store), so an edited request is never answered with a preset's result.
- **Decision memo (`MemoScreen`, print CSS):**
  - One A4 page: verdict, reasons, best chain, cost compared with pea, test to buy first, sources and limitations.
  - "Print / save as PDF" button. The offline test checks that the PDF has exactly 1 page.
- **Open data pack:** `web/public/open-data-pack.zip`, linked in the footer.
  - Contents: `/data` files, `sources.json`, schemas, `DATA_TODO.md` and a README with a licence note. The team has not chosen a licence yet.
  - Unpublished team documents are cited but not included.
- **Performance:**
  - The Chains (Pareto), Cost, Diagnosis, Next (EVPPI), Memo screens and the Hindi bundle are code-split; the Devanagari font loads only in Hindi.
  - Initial JS is 143 KB gzipped.
  - Lighthouse mobile, served with compression (`docs/reports/lighthouse-mobile.report.html`):

    | Score | Result |
    |---|---|
    | Performance | 94 |
    | Accessibility | 100 |
    | Best practices | 100 |
    | Time to interactive | 2.2 s |
    | Page weight | 161 KiB |
- **Accessibility fixes:**
  - The provenance hover popover no longer blocks clicks underneath it (`pointer-events-none` while peeking).
  - Scroll wrappers can be reached by keyboard, and there is no horizontal page scroll at 360 px.
- **Security audit:**
  - `pip-audit` found 7 advisories in starlette 0.41.3. Now pinned to `fastapi==0.143.0` and `starlette==1.3.1`; `pip-audit` reports no known vulnerabilities.
  - `pip-audit==2.7.3` was added to `requirements-dev.txt`.
  - `npm audit --omit=dev` reports 1 high advisory in zod 3.24.1 (GHSA-mrhx-c7xc-m3w5). It is recorded as an accepted risk in the README, for three reasons:
    - zod runs only in the browser, on the app's own input form;
    - the form's arrays are bounded checkbox lists;
    - the fix is a breaking major released less than two weeks ago.
  - Secret scan of tracked files, the full git history, `web/public` and `docs`: no AWS, Groq, OpenAI or GitHub keys and no private keys. `.env*` (except `.env.example`) and `.aws/` are git-ignored.
- **Deployment config (`docs/DEPLOY.md`):**
  - `web/vercel.json`:
    - SPA rewrite; `/api/*` rewritten to the Render API, so the browser stays on one origin;
    - security headers, with the microphone allowed for this origin only;
    - immutable caching for hashed assets;
    - missing snapshots still return 404.
  - `render.yaml`: Python 3.11 service, `LLM_PROVIDER=template`, no LLM keys, `/health` health check.
  - `.github/workflows/keep-alive.yml`: pings `/health` every 10 minutes once the repository variable `API_HEALTH_URL` is set.
- **README:** run steps, architecture, PoC disclaimer, limitations, data labels, AI tools used, and how to regenerate snapshots.

**Tested**
- pytest: 102 passing (GT1–GT8 and the regression snapshot). ruff and black are clean.
- vitest: 14 passing. Locale check: 349 Hindi strings, 14 kept in English. ESLint is clean; the build passes.
- e2e (`npm run e2e`): all checks pass.
  - J1 by keyboard only at 1280 px; every screen at 360 px and 1280 px.
  - axe: 0 serious/critical on every screen, including Hindi and the lab-result update.
  - No horizontal scroll.
- Wi-Fi-off rehearsal (`npm run e2e:offline`, built app served with no API): all checks pass.
  - The 3 presets load from snapshots with the stamp; summaries in English and Hindi; the Next screen.
  - One-page memo PDF (`docs/screenshots/decision-memo.pdf`).
  - Offline form options; the data pack downloads.
- Timing: groundnut_beverage 834 ms, rice_bran_snack 198 ms, almond_meat 89 ms (target: under 3 s).
- The Render start command was run locally with `APP_ENV=public LLM_PROVIDER=template`: `/health` returns ok.

**Exit gate: met for the offline rehearsal; deployment is waiting on accounts.**
- The "Wi-Fi off" rehearsal passes. It was run here against the built app with no API; repeat `npm run e2e:offline` on the demo laptop.
- "Deployed URL works" needs the team's Vercel and Render accounts. The configs are ready and the steps are in `docs/DEPLOY.md`.

**Not done / needs the team**
- Deploy to Vercel and Render, set `CORS_ORIGINS` and `API_HEALTH_URL`, and record the URLs in `docs/DEPLOY.md`.
- Manual screen-reader pass (NVDA or VoiceOver) on J1. It could not be run in this environment; axe and the keyboard walk-through are automated.
- Choose a licence for the open data pack.
- Upgrade zod to 4, together with `@hookform/resolvers`, once the release is older than two weeks.
- From Phase 7: Hindi review of `hi.json` and the safety strings; manual voice tests on real devices.

## Phase 9: Pitch package

**Implemented (`docs/pitch/`)**
- **`SLIDES.md`:** the source plan §18.1 slide plan, rewritten for the current build (engine 0.8.0, dataset 2026-10-25.1).
  - On-screen text, speaker notes and timings that add up to 4:00.
  - The lead demo is sunflower cake → Protein Rich Flour (display names from `e74f6aa`).
  - Uncalibrated outputs are not promised: P(GO), Pareto break-even and the EVPPI tornado.
  - One unsourced claim (">25 Mt oilseed cake") was dropped until it is checked on FAOSTAT.
- **`REFERENCES.md`:** every source with a clickable link, labelled with the provenance tags its values actually carry in `/data` (counted from the files).
  - The organiser datasets are labelled "listed, no values drawn yet", because none supplies a value today.
  - Also lists the AI tools (Bedrock, Groq, Claude Code, Web Speech API; BHASHINI not used) and library versions.
- **`QA.md`:** the §18.2 answers updated where the build changed, for example backtesting not done, cost not calculable, feedback does not retrain.
  - Adds the plan's four extra questions (Bedrock, AWS account gone, Hindi review, voice audio) and questions grouped by judge.
- **`DEMO_SCRIPT.md`:** laptop setup with a disposable feedback database, a 1:50 video script, the 90-second live demo, a rehearsal log and a submission checklist.

**Checked**
- Demo numbers were taken from the app at this commit:
  - TEST-FIRST, hypothesis grade, 9 routes;
  - pea landed ≈ ₹518/kg protein (P10–P90 ₹431–619, assumed);
  - lead 1.6 mg/kg via `/update-evidence` → NO-GO; lead 0.4 → stays TEST-FIRST.
- UI labels in the click path match `en.json`.

**Not done / needs the team**
- Copy the content into the official template.
- Fill in the Bedrock model id.
- Record the video (before 3 AM).
- Rehearse twice and fill in the log.
- Make the repository public or remove its link.
- Click every link in the exported PDF.
- Submit by 7:30 AM.

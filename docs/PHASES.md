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

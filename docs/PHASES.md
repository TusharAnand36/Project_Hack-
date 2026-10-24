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
- `data/_staging/`: 13 candidate rows for human review. The engine does not read them.
  - 9 from desk research, tagged `assumed`/D with quote and URL.
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
- 25 values are flagged "verify", including the aflatoxin limits. The FSSAI 2015 amendment appears to set 15 µg/kg for oilseeds "for further processing", not 30 ppb; see the staged candidate.
- Which tariff site gives 43.96% and which gives 49.15% is not recorded; both sites were unreachable.
- The protein and ash tables in the PhD report are images and were not read.
- Almond cake has no anti-nutrient baselines. Literature should confirm that none exceed tolerances before GT5 is claimed.

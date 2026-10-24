# Upcycle Compass

For one food by-product batch and one target use, Upcycle Compass answers **Go / No-go / Test-first**. It also says which treatment chain to use, what a kg of protein costs compared with imported pea isolate, and which single lab test to buy first. Every number carries a provenance tag: `measured`, `published`, `assumed` or `synthetic`.

> **Proof of concept, Hack the Fork 2026 (Problem Statement 2).** Decision support only. Not a regulatory approval. Confirm FSSAI classification and limits.
> **Phase 0 status:** the `/analyze` endpoint is a **stub**. All of its numbers are placeholders tagged `synthetic`.

## Layout (source plan §10.2)

```
data/                       JSON datasets (Phase 1); schema/ for exported schemas; _staging/ for unreviewed rows
engine/compass/             pure-Python decision engine (no web/LLM imports)
  models.py                 Tag, Grade, Dist, Param, Value, Range: provenance types
  sampling.py effects.py flavour.py cost.py pea.py gates.py diagnosis.py chains.py
  montecarlo.py voi.py pareto.py readiness.py update.py plan.py   (placeholders until their phase)
  tests/
api/main.py                 FastAPI app: /health, /analyze (stub)
api/schemas.py              request (§8.3) and response (§14.2) contract
api/routers/  api/llm/      routers; Bedrock client, prompts, number verifier (Phase 6)
web/                        React 18 + TS + Vite + Tailwind (shadcn/ui conventions)
  src/api/types.ts          generated from the API's OpenAPI schema; do not edit by hand
  src/locales/              en.json, hi.json (i18n keys; no hard-coded UI strings)
  public/snapshots/         offline precomputed results (Phase 8)
scripts/                    gen_types.sh, build_snapshots.py, extract_rows_from_abstracts.py
docs/                       source plan, website plan, phase reports
```

## Run

Requirements: Python 3.11+, Node 20+.

```bash
make setup        # venv + pip install + npm ci (once)
cp .env.example .env
make api          # http://localhost:8000  (docs at /docs)
make web          # http://localhost:5173  (shows "API: ok")
make types        # regenerate web/src/api/types.ts (API must be running)
make test         # pytest + web build
make lint
make data         # dataset report: counts by tag/grade, missing inputs per preset
make todo         # regenerate DATA_TODO.md and data/schema/
```

## Data

Every number in `/data` carries `tag` (measured/published/assumed/synthetic), `evidence_grade` (A–D), `source_id` and, for transferred evidence, `applicability` (α). Missing values are `null` and listed in `DATA_TODO.md`, which is generated, not hand-edited. Candidate values that still need human review live in `data/_staging/` and are never read by the engine. Unpublished team documents (review drafts, research plan, PhD report) are cited as sources but are not committed to the repo.

## Rules for contributors

- Never commit secrets. `.env` and `.aws/` are git-ignored. Credentials come from the environment or a local AWS profile only.
- Never invent numbers. Missing data stays `null` and gets a line in `DATA_TODO.md`.
- Every numeric output carries a `tag`, plus `grade`, `source_ids` and `alpha` where they apply.
- After any API change, run `make types` and commit the regenerated `types.ts`.

The science and engine specification is `docs/Upcycle_Compass_Master_Prompt.md` (source plan v2). See `docs/Website_Development_Master_Plan.md` for the phase plan and `docs/PHASES.md` for progress.

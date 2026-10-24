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

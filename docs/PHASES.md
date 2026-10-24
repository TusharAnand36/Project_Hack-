# Phase reports

## Phase 0: Declare, repository and contracts

**Implemented**
- Folder layout: `engine/compass`, `api/llm`, `data/_staging`, `web/src/locales`, `web/public/snapshots`, `scripts`, `docs`. Placeholder modules for later phases.
- `engine/compass/models.py`: `Tag`, `Grade` (A–D), `Dist` (`type/low/mode/high`, with ordering validated), `Param` (`value|dist`, unit, tag, grade, source_id, alpha, conditions, notes), `Range` (p10/p50/p90 + provenance).
- `api/main.py`: `/health` and a stub `/analyze` returning the full response shape (verdict, gates, diagnosis, chains, pea comparison, recommended test, disclaimer). Every number is tagged `synthetic`, and the response has `is_stub: true`. Unknown request fields are rejected (422). The CORS allow-list comes from `CORS_ORIGINS`.
- `web/`: Vite + React 18 + TS + Tailwind with shadcn/ui conventions (`components.json`, `cn()`, `Badge`), TanStack Query, react-i18next (en; hi falls back to en). The page shows "API: ok" through the `/api` dev proxy.
- `scripts/gen_types.sh` writes `web/src/api/types.ts` with openapi-typescript. The generated file is committed.
- `.env.example`, `.gitignore`, `README.md`, `DATA_TODO.md`, `Makefile` (`setup api web test types snapshots lint`).
- Tooling: Ruff + Black (Python), ESLint + Prettier (TS). Versions are pinned in `requirements*.txt` and `package-lock.json`.

**Tested**
- pytest: 7 passing (model validators, /health, stub tags, 422 on unknown fields).
- `npm run build`, `npm run lint` and `ruff` all pass.
- Playwright at 360 px: health badge reads "API: ok" (`docs/phase0-health-360.png`).

**Not done / known limits**
- The source plan `Upcycle_Compass_Master_Prompt.md` (v2) was not available. The folder layout (§10.2) and the `/analyze` response shape (§14.2) are inferred from the website plan and must be reconciled with the source plan in Phase 3.
- Declaring Problem Statement 2 with the organisers is a manual step for the team.
- Built and tested on Python 3.13. Pins are chosen to also work on 3.11.
- Initial JS is about 80 KB gzipped (budget 250 KB).

# Deployment (website plan, Phase 8 task 7)

There are two ways to run the demo:

| Setup | Web | API | AI text |
|---|---|---|---|
| **Public demo** | Vercel (static build of `web/`) | Render free tier (`render.yaml`) | Template only (`LLM_PROVIDER=template`) |
| **Demo laptop** | `make web` | `make api` | Bedrock via a local AWS profile (falls back to template) |

If the API cannot be reached, or does not answer within 8 s, the web app falls back to the precomputed preset snapshots in `web/public/snapshots/`. It then shows "Demo snapshot (offline)". This is the "Wi-Fi off" path; see `npm run e2e:offline`.

## 1. API on Render

1. Sign in to Render and create a new Blueprint from this repository. Render reads `render.yaml`.
2. Render creates `upcycle-compass-api` (Python 3.11):
   - build: `pip install -r requirements.txt`
   - start: `uvicorn api.main:app` with `PYTHONPATH=engine:.`
   - health check: `/health`
3. Set `CORS_ORIGINS` to the Vercel URL, for example `https://upcycle-compass.vercel.app`.
   - The browser normally reaches the API through Vercel's same-origin `/api` rewrite, so this setting only matters for direct calls.
4. Do **not** add AWS or Groq keys to the public service. `LLM_PROVIDER=template` keeps all AI text deterministic, and the template text passes the number verifier.
5. Check that it is up: `curl https://<service>.onrender.com/health` should return `{"status":"ok","engine_version":…,"dataset_version":…}`.

The free tier sleeps after about 15 minutes idle, so the first request after a sleep can take 30–60 s. Two things cover that:

- **Keep-alive ping:** `.github/workflows/keep-alive.yml` calls `/health` every 10 minutes. To turn it on, set the repository **variable** (not a secret) `API_HEALTH_URL` to the full `/health` URL. Without it, the job exits without doing anything.
- **Snapshot fallback:** after 8 s the web app shows the preset snapshot instead of waiting.

## 2. Web on Vercel

1. Import the repository in Vercel and set **Root Directory** to `web`. Vercel reads `web/vercel.json`:
   - framework: Vite
   - build: `npm run build`
   - output: `dist`
2. In `web/vercel.json`, the first rewrite sends `/api/*` to `https://upcycle-compass-api.onrender.com/*`.
   - If Render gave the service a different hostname, edit that line and redeploy.
   - Alternatively, set the build-time variable `VITE_API_BASE` to the full API URL. The browser then calls the API directly, which needs `CORS_ORIGINS`.
3. All other paths serve `index.html` (single-page app). Missing snapshots and offline data still return 404, so the fallback logic sees a real error.
4. Headers:
   - `nosniff`
   - a strict referrer policy
   - microphone allowed for this origin only (used by voice input); camera and location off
   - year-long caching of the hashed `assets/` files
5. Check it works:
   - open the URL, run each preset, open the decision memo;
   - download the data pack from the footer;
   - then block the API in DevTools (Network → block request URL `/api`) and confirm the snapshot path still works.

## 3. Demo laptop (Bedrock)

```bash
make setup && cp .env.example .env     # set AWS_PROFILE, BEDROCK_MODEL_ID; LLM_PROVIDER=bedrock
make api                                # :8000
make web                                # :5173
```

Credentials come only from the local AWS profile or the environment. They are never written to `.env.example`, the repo, prompts or logs.

Rehearse with Wi-Fi off:

```bash
cd web && npm run e2e:offline
```

This builds the app, serves `dist` with no API, and checks the five presets, the Hindi summary, the decision memo and the data pack.

## Case feedback and lab history

Live analyses receive a fresh case ID. Case feedback and laboratory-update history use
SQLite through Python's standard library. Locally the file is
`.runtime/feedback.sqlite3`; the runtime directory is excluded from Git.

For a hosted API, set `FEEDBACK_DB_PATH` to a file on a persistent mounted disk,
for example `/var/data/upcycle-feedback.sqlite3`. An ephemeral filesystem does not
provide durable feedback. With `APP_ENV=public` and no configured path, analysis
still works and the UI reports that feedback storage is unavailable. A failed save
never displays a success message. No storage service or paid disk has been provisioned.

Feedback is scoped to material, intended use, extraction route and dataset version.
Future matching queries receive aggregated issue counts and follow-up test suggestions;
free-text notes remain private to storage. Feedback cannot clear safety gates or
rewrite scientific values. This prototype has no authenticated accounts or verified
lab submitters, so feedback is observational, not validated scientific evidence.
Do not enter personal or confidential information. Protect and back up the database
before using a shared deployment, and provide an appropriate retention process.

## 4. After changing the engine or data

```bash
make snapshots      # rewrites web/public/snapshots/, offline-data/ and open-data-pack.zip
make test
```

Commit the regenerated files. Every snapshot is stamped with `engine_version`, `dataset_version` and `generated_at`, and the offline badge shows that stamp.

## Status

Nothing has been deployed from this repository yet. Deploying needs the team's own Vercel and Render accounts. Once it is live, add the URLs here:

- Web: _not deployed_
- API: _not deployed_

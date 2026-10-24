# Upcycle Compass: Website Development Master Plan

**Hack the Fork 2026, India Edition (NIFTEM-K) · Problem Statement 2 · Plan written 24 Oct 2026, 12:30 IST**

> **How to use this file.** This plan sits *on top of* the source plan `Upcycle_Compass_Master_Prompt.md` (v2). The source plan stays the single specification for the science and the engine maths (its §11–§13). This plan turns it into a buildable website in phases.
> Give your coding agent three things for each phase: (1) the source plan, (2) **Section 10.0 Shared Rules** below, (3) the one phase prompt you are working on. Run one phase at a time and check its exit gate before moving on.

**Labels used in this document**
- **[Fact]**: checked against a source listed in Section 16.
- **[Source plan]**: taken from your master prompt. Not re-verified here.
- **[Rec]**: my recommendation. You can overrule it.
- **[Assumption]**: a working number or choice with no source. Replace it when you can.

---

## 1. Executive Summary

**What we are building.** Upcycle Compass is a web app that tells a food company, for one by-product batch and one target use: *Go / No-go / Test-first*, which treatment chain to use, the cost per kg of protein compared with imported pea isolate, and which single lab test to buy first. Every number shows where it came from. [Source plan §6]

**The real constraint.** Building started at 11:00 AM on 24 Oct. The final deck is due between 6:00 and 8:00 AM on 25 Oct. That leaves about 18 working hours. Everything after that (more languages, accounts, a production launch) belongs to the 6-month plan, not tonight. Phases 0–9 are the hackathon build. Phases 10–12 come after it.

**Key recommendations**

| # | Recommendation | Why |
|---|---|---|
| R1 | **Use Amazon Bedrock (Claude, us-east-1) as the main LLM**, with the deterministic template as the last fallback. Keep Groq/Gemini only as an optional second option. [Rec] | The organisers give every team a free Bedrock sandbox. The source plan's Groq/Gemini needs separate keys, and using the provided stack is easier to explain to the jury. |
| R2 | **Ship two delivery modes: Live and Snapshot.** Live = laptop running the API and Bedrock. Snapshot = static precomputed results that work offline. [Rec] | The AWS account is deleted when the event window closes, and venue Wi-Fi can fail. The jury may ask to see the prototype working during questions. |
| R3 | **English first. Add Hindi for the interface and the plain-language explanation during the hackathon. Add more languages after it.** [Rec] | Hindi covers the most users quickly. Safety wording must be reviewed by a person, and the team can only do that tonight for languages it reads. |
| R4 | **Voice is an optional way to fill the form, never the only way.** Use the browser Web Speech API (en-IN, hi-IN), always show an editable transcript, and require the user to confirm the filled form. [Rec] | Speech recognition makes mistakes. Firefox keeps speech recognition behind a flag, so a text path must always exist. [Fact] |
| R5 | **No user accounts and no personal data in the proof of concept.** [Rec] | This keeps the DPDP Act footprint close to zero for now. Notice and consent obligations become mandatory on 13 May 2027, so production must add them before then. [Fact] |
| R6 | **Mobile-first responsive layout, small bundle, offline snapshots.** [Rec] | Mobile is the main way Indians go online, and mill owners are likely to look on a phone. [Fact] |

---

## 2. Source Plan Analysis

### 2.1 Objectives (from the source plan)
1. Answer one industry decision: *"For this batch and this application: Go, No-go or Test-first? If Go, which treatment chain at which product tier, at what ₹ per kg protein compared with imported pea isolate, with what probability of meeting spec, and which one lab test should we run first?"* [Source plan §8.2]
2. Score well on the five judging criteria: relevance, scientific validity, functionality, 6-month feasibility, meaningful AI. [Source plan §2]
3. Be honest about uncertainty: every number is tagged `measured / published / assumed / synthetic`. [Source plan §11, §16]

### 2.2 Users
| User | Main need | Likely device | Language |
|---|---|---|---|
| Edible-oil or rice-mill owner (Rajkot, Guntur, Punjab) | "Can I sell this cake to a food company? What must I test?" | Phone | Gujarati, Telugu, Punjabi, Hindi, English [Assumption from locations in source plan] |
| R&D head at a plant-based brand | "Is there a local protein I can trust, and at what cost and risk?" | Laptop | English |
| Incubator / programme manager | "Which pilots should we fund first?" | Laptop | English |
| **Hackathon jury (the real first audience)** | "How sure are you, and why? Where is the AI?" | Organisers' laptop + your laptop during Q&A | English |

### 2.3 Core workflows
1. Pick a preset or enter a by-product, target use and targets.
2. Engine runs: safety gates → diagnosis → treatment chains → cost vs pea → Monte Carlo → value of information → verdict.
3. User reads the verdict, inspects any number's source, compares chains, adjusts cost sliders.
4. User enters one lab result → engine updates → before/after comparison.
5. User exports a one-page decision memo.

### 2.4 Constraints
- Hackathon rules: declare by 1:00 PM; venue lock 10 PM–6 AM; submit deck PDF, optional 2-minute video and a repo or live link between 6:00 and 8:00 AM; 4-minute pitch plus 4 minutes of questions; keep the prototype running on one team laptop.
- AWS: us-east-1 only; about 1 Bedrock request per second per person; GPU instances blocked; never make S3 public; never put access keys in code, prompts or repos; the account is deleted when the event window closes.
- Credits: list every AI assistant, API, library, model and data source on the References slide as clickable links.

### 2.5 Gaps, ambiguities and risks in the source plan

| # | Issue | Recommendation |
|---|---|---|
| A1 | The source plan names Groq/Gemini as the LLM. The hackathon provides Bedrock. | Use Bedrock first (R1). Keep the LLM client behind one interface so the provider can be swapped. |
| A2 | It is unclear whether the AWS account is deleted before or after the pitch slots on Sunday morning. | Ask the organisers at the 2:30 PM mentor round. Plan for the worst case: the demo laptop must work with the template fallback and snapshots and no AWS. |
| A3 | The source plan suggests deploying the API on Render/Railway. Putting the sandbox AWS keys on a third-party host is close to "pasting access keys" and the keys expire anyway. | Deploy the public API **without** Bedrock (template explanations only). Run Bedrock only from the team laptop using a local AWS profile. |
| A4 | The pea isolate price comes only from China export prices. | Add Indian B2B listings as a cross-check (roughly ₹300–450/kg of product on trade portals). [Fact, see §16] Show both. |
| A5 | Scope: 8 screens + EVPPI + Bayesian update + LLM + Hindi + voice in ~18 hours. | Follow the priority tiers strictly (Section 10.1). Hindi and voice are Tier 2. |
| A6 | Machine-translating safety wording (aflatoxin, "do not use for food") into Hindi could change its meaning. | Gate texts are fixed, pre-written strings reviewed by a Hindi-reading teammate. Only the free-form explanation is machine-translated, with a badge and an "show English" toggle. |
| A7 | The PhD measured data and the review-draft numbers have not been checked. | Keep the source plan's rule: use measured data only with the owner's permission; verify review numbers against the original papers before showing them. |
| A8 | No owner is named for the deck template (arrives at 10 PM). | Assign the story lead now (Phase 9). |

---

## 3. Research Findings and Recommendations

| Finding | Source | Decision it drives |
|---|---|---|
| India had about 958 million active internet users in 2025; about 57% (≈548 million) are rural; 18% go online through someone else's phone. [Fact] | IAMAI–Kantar "Internet in India 2025" (news coverage) | Mobile-first layout; no login required to use the tool; nothing stored on the device that a second user of a shared phone could misread as theirs. |
| Mobile is the main device for going online in both urban and rural India. [Fact] | IAMAI–Kantar 2024 report coverage | Design for 360 px width first. |
| One in five internet users used voice commands (2024 report). [Fact] | Business Standard on IAMAI–Kantar 2024 | Voice input is worth adding as an optional path (R4). |
| Web Speech API recognition: works in Chrome, Edge and Safari 14.5+ (prefixed); Firefox keeps it behind a flag; Chrome sends audio to Google's servers; Edge on Android/iOS does not expose it. [Fact] | AssemblyAI guide (Jun 2026); TestMu AI compatibility page | Feature-detect, hide the mic when unsupported, disclose that audio is processed by the browser vendor. |
| BHASHINI offers open APIs for speech recognition, translation and speech synthesis across Indian languages; developers register for credentials. A Python client exists. [Fact] | BHASHINI explainer; `bhashini-client` on PyPI | Post-hackathon path for Gujarati, Telugu, Punjabi and others (Phase 11). |
| AI4Bharat IndicTrans2 (translation, all 22 scheduled languages) and IndicConformer (speech recognition, 22 languages) are open source under MIT. [Fact] | Hugging Face paper page; AIKosh; GitHub | Self-hosted option later. Not tonight: GPU instances are blocked in the sandbox. |
| DPDP Rules notified Nov 2025; consent-manager rule from 13 Nov 2026; notice, consent and security-safeguard rules from 13 May 2027. [Fact] | Hogan Lovells summary; AZB & Partners | PoC collects no personal data. Production (Phase 10) must ship a plain-language notice and consent flow before May 2027 if accounts are added. |
| WCAG 2.2 adds criteria such as minimum target size (24×24 CSS px), focus not obscured, consistent help and accessible authentication. [Fact, standard] | W3C WCAG 2.2 | Accessibility checklist in Section 9.4. |

---

## 4. Target Audience and Indian Market Considerations

- **Two very different readers.** The mill owner wants a plain answer and the test to order. The R&D head and the jury want the uncertainty and the sources. **Design:** a plain summary on top of every screen; detail one tap away.
- **Numbers and units.** Format money as Indian Rupees with Indian digit grouping (₹1,00,000) using `Intl.NumberFormat('en-IN')`. Show budgets in lakh/crore with the full number in a tooltip. Mandi prices are quoted per quintal, so accept ₹/quintal, ₹/tonne and ₹/kg inputs and convert. Show dates as "24 Oct 2026" and times in IST.
- **Connectivity.** Snapshots load with no API. Charts render from JSON already in the page. No large images or video on core screens.
- **Trust.** Every number uses the provenance component (`<Num/>`), with a letter chip (M/P/A/S) plus colour, so meaning does not depend on colour alone.
- **Shared devices.** No login, nothing personal saved. Language choice is the only thing stored in the browser.

---

## 5. Functional and Non-Functional Requirements

### 5.1 Functional requirements
| ID | Requirement | Tier | Phase |
|---|---|---|---|
| FR-01 | Three one-click presets (groundnut → beverage, rice bran → snack, almond → meat analogue) | 0 | 4 |
| FR-02 | Input form with targets per kg **protein**, scale, constraints, optional batch data; every field tagged | 0 | 4 |
| FR-03 | Safety gates G1–G7 with PASS / TEST-FIRST / FAIL and "what flips it" | 0 | 3 |
| FR-04 | Diagnosis of limiting compounds vs application tolerance, with P10–P90 | 0 | 3 |
| FR-05 | Treatment chain enumeration with precedence rules, exclusions and equipment | 0 | 3 |
| FR-06 | Mass/protein balance and product tier per chain | 0 | 2 |
| FR-07 | Cost per kg protein, energy and water per kg protein | 0 | 2 |
| FR-08 | Pea isolate landed cost, duty-mode switch, GST-credit toggle, FX/freight sliders, break-even, shock scenarios | 0 | 2, 4 |
| FR-09 | Monte Carlo with P10/P50/P90 and P(spec) | 0 | 5 |
| FR-10 | EVPPI ranking and "one test to buy first" | 1 | 5 |
| FR-11 | Pareto chart and three named picks | 1 | 5 |
| FR-12 | Decision-readiness grade and "what must be demonstrated" list | 1 | 5 |
| FR-13 | Validation plan and 6-month pilot budget (rule-based) | 1 | 5 |
| FR-14 | Enter a lab result → Bayesian update → before/after | 2 | 6 |
| FR-15 | LLM explanation (Bedrock) with number verifier and template fallback | 2 | 6 |
| FR-16 | Free text (typed or spoken) → filled form → user confirms | 2 | 6, 7 |
| FR-17 | Hindi interface and Hindi explanation | 2 | 7 |
| FR-18 | Read-aloud of the verdict summary | 3 | 7 |
| FR-19 | Export one-page decision memo | 2 | 8 |
| FR-20 | Provenance view for every number; data-completeness meter | 0 | 4 |
| FR-21 | Offline snapshot mode with a visible badge | 0 | 8 |
| FR-22 | Open data pack (JSON + sources) downloadable | 1 | 8 |

### 5.2 Non-functional requirements
| ID | Requirement | Target |
|---|---|---|
| NFR-01 | `/analyze` response time for a preset on the demo laptop | < 3 s [Source plan §15] |
| NFR-02 | Initial JavaScript download | < 250 KB gzipped [Assumption] |
| NFR-03 | First screen usable on a mid-range Android phone on a slow 4G profile | < 4 s in Lighthouse mobile [Assumption] |
| NFR-04 | Accessibility | WCAG 2.2 AA for core screens; axe-core reports 0 serious/critical issues |
| NFR-05 | Reproducibility | Same input + seed → identical output |
| NFR-06 | Honesty | 0 numbers on screen without a tag; 0 LLM numbers not present in engine JSON |
| NFR-07 | Resilience | Every preset works with the API down (snapshot) and with Bedrock down (template) |
| NFR-08 | Security | No secrets in git or the browser bundle; CORS allow-list; request size limit |

---

## 6. Website Features and User Journeys

**J1 – Jury demo (the most important path).** Open site → tap "Groundnut cake → beverage" → verdict TEST-FIRST with prior aflatoxin risk → open diagnosis → open chains and Pareto → open cost vs pea and move the FX slider → open "Next step" and see the recommended test → enter a lab value → see before/after → (optional) read the AI summary with its "numbers verified" badge.
*Failure paths:* API down → snapshot loads with "Demo snapshot (offline)" badge; Bedrock down → template summary with "AI summary unavailable; template text" note.

**J2 – Own batch.** Choose by-product and use → enter measured protein, moisture, aflatoxin → fields switch to `measured` (M chip) → analyse.
*Failure paths:* impossible values (protein > 100%, negative) blocked with a clear message; proximate sum outside 95–105% → warning, not a block.

**J3 – Describe in words (typed or spoken).** Type or say "Groundnut cake from Rajkot, about 48% protein, for a protein drink, no solvents" → transcript shown and editable → "Fill the form" → filled form with changed fields highlighted → user confirms → analyse.
*Failure paths:* mic denied → explain how to allow it and keep the text box; LLM unavailable → "Could not read this automatically; please fill the form"; parse fails validation → same message.

**J4 – Provenance check.** Tap any number → tooltip/sheet shows value, range, tag, evidence grade, applicability, source with link, conditions. "Transferred from sunflower" badge where relevant.

**J5 – Export.** "Download decision memo" → one-page PDF/print view with verdict, top chain, cost vs pea, recommended test, limitations and sources.

**J6 – Hindi user.** Switch language → interface and fixed gate texts in Hindi; numbers keep Indian formatting; AI summary in Hindi with "machine-translated" badge and "show English" toggle.

---

## 7. Multilingual and Voice Interaction Strategy

### 7.1 Languages and phasing
| Stage | Languages | How | Why |
|---|---|---|---|
| Hackathon | English, Hindi | Static UI strings in JSON files, reviewed by a Hindi-reading teammate; Hindi explanation from Bedrock with the number verifier | Fast; one teammate can review |
| Pilot (months 1–3) | Gujarati, Telugu, Punjabi, Marathi | BHASHINI translation for drafts + human review by a native speaker; glossary of technical terms | Matches the mill regions in the personas [Assumption] |
| Later | Tamil, Kannada, Bengali, Malayalam, Odia, Assamese, Urdu (RTL) | Same process; RTL support for Urdu | Expand with users |

### 7.2 What may and may not be machine-translated
- **Never machine-translated:** safety gate verdicts, "do not use for food" warnings, allergen flags, legal/regulatory notes, disclaimers. These are fixed strings written and reviewed by a person.
- **Machine-translated with a badge:** the plain-language explanation and the draft plan paragraph. They must pass the number verifier *after* translation, and the English original is one tap away.
- **Kept in English with a local gloss:** technical terms such as aflatoxin, phytate, trypsin inhibitor. Show "aflatoxin (एफ्लाटॉक्सिन)" on first use. Keep a glossary file `glossary.hi.json`.

### 7.3 Technical approach
- `react-i18next` with resource files `web/src/locales/en.json`, `hi.json`; keys by screen (`verdict.title`, `gate.G1.fail`).
- Fonts: Noto Sans + Noto Sans Devanagari (Google Fonts, `font-display: swap`), loaded only when Hindi is selected.
- Layout: allow about 30% text expansion; no fixed-width buttons with text; use logical CSS (`ms-`, `me-`, `ps-`, `pe-`) from day one so RTL can be added later.
- Numbers: always `Intl.NumberFormat('en-IN')`, even in Hindi, so digits stay readable and match the engine output that the verifier checks.
- Language choice stored in `localStorage` (wrapped in try/catch); default from `navigator.language`, falling back to English.

### 7.4 Voice input
- Where: only the "Describe in words" box (J3). Not on numeric fields.
- How: Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`), `lang` = `en-IN` or `hi-IN` matching the UI language, `interimResults: true`.
- States: idle → requesting permission → listening (pulsing mic, "Listening… tap to stop", live transcript) → processing → transcript ready (editable) → error.
- Errors: not supported (hide mic, show text box only); permission denied (instructions); no speech detected; network error; recognition stopped early. Each with "Try again" and "Type instead".
- Privacy note next to the mic: "Your browser's speech service processes the audio. Do not say personal details." [Fact: Chrome sends audio to Google; Safari to Apple]
- Never auto-submit. The transcript goes to the parser, the parser fills the form, the user confirms.

### 7.5 Read-aloud (Tier 3)
- `speechSynthesis` reads the verdict summary. Show the button only if a voice exists for the current language (`getVoices()` includes `hi-IN` or `en-IN`). Stop button always visible while speaking.

---

## 8. Recommended Technology Stack and Architecture

### 8.1 Stack (changes from the source plan are marked)
| Layer | Choice | Note |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite; Tailwind + shadcn/ui; Recharts; Zustand; TanStack Query; react-hook-form + Zod | As source plan |
| **Types** | **`openapi-typescript` generates TS types from FastAPI's `/openapi.json`** | **Changed:** one source of truth for the API shape; Zod only for form validation |
| **i18n** | **react-i18next** | **Added** |
| **Voice** | **Web Speech API** (browser), no server audio | **Added** |
| Backend | Python 3.11, FastAPI, Pydantic v2, Uvicorn | As source plan |
| Numerics | NumPy, SciPy (`stats.qmc`), pandas; networkx optional | As source plan |
| **LLM** | **Amazon Bedrock via `boto3` `bedrock-runtime` `converse()`; region `us-east-1`; model ID copied from the Bedrock console** → optional Groq/Gemini → template | **Changed (R1)** |
| Data | JSON files in `/data`, validated at startup | As source plan |
| Tests | pytest + hypothesis; Vitest + Testing Library; Playwright + `@axe-core/playwright` | **Added** E2E and accessibility |
| Deploy | Frontend: Vercel (static + snapshots). Public API: Render/Railway **without Bedrock**. Demo: everything local on the team laptop with Bedrock via local AWS profile | **Changed (A3)** |

### 8.2 Architecture
```
Browser (React)  ──►  /api (FastAPI)  ──►  engine `compass` (pure Python)  ──►  /data JSON
   │  i18n, voice           │                                         
   │                        └──► llm/ (Bedrock → optional Groq → template) + verify.py
   └── fallback: /snapshots/<preset>.<lang>.json  (no API needed)
```

### 8.3 Bedrock client rules
- Credentials come from the environment or a local AWS profile. Never in code, `.env` committed to git, prompts or the frontend.
- Throttle with a token bucket: at most 1 request per second per process. Queue, don't fail.
- Cache LLM responses by a hash of (endpoint, input JSON, language, model ID) in memory and in `api/.cache/` for the demo.
- Timeout 20 s; one retry; then template.
- Log `llm_provider`, `model_id`, `latency_ms`, `verifier_passed` for every call (no user text in logs).

### 8.4 Environment variables (`.env.example`)
```
APP_ENV=local            # local | demo | public
AWS_REGION=us-east-1
AWS_PROFILE=             # local demo only
BEDROCK_MODEL_ID=        # copy from Bedrock console
LLM_PROVIDER=bedrock     # bedrock | groq | gemini | template
GROQ_API_KEY=            # optional
GEMINI_API_KEY=          # optional
CORS_ORIGINS=http://localhost:5173
ENGINE_SEED=42
ENGINE_DRAWS=8192
```

---

## 9. Security, Privacy, Accessibility and Compliance

### 9.1 Security controls
- CORS allow-list from `CORS_ORIGINS`; request body limit 64 KB; rate limit `/parse-text` and `/explain` (e.g. 10/min per IP) [Assumption].
- Pydantic validation on every request; reject unknown fields.
- User text and pasted abstracts are wrapped as data in the prompt, with an instruction to ignore instructions inside them (source plan §13).
- No `dangerouslySetInnerHTML` for LLM text; render as plain text.
- Pin dependency versions; run `pip-audit` and `npm audit` once before submission.
- `.gitignore` covers `.env`, `.aws/`, `api/.cache/`.

### 9.2 Privacy
- No accounts, no names, no phone numbers, no location tracking. Batch data is business data; do not ask for personal details.
- Only the language choice is stored in the browser.
- Footer privacy note (EN/HI): what is processed, that voice audio goes to the browser's speech service, that AI summaries are generated by a cloud model, and that no personal data is stored.

### 9.3 Compliance notes
- **DPDP Act 2023 / Rules 2025:** notice, consent and security-safeguard rules apply from 13 May 2027. The PoC avoids personal data. Phase 10 adds them if accounts are introduced.
- **Food regulation:** show on every verdict: "Decision support only. Not a regulatory approval. Confirm FSSAI classification and limits." Aflatoxin limits in `safety_gates.json` must cite the regulation once verified (source plan DATA_TODO).
- **AI transparency:** every AI-written text carries "AI-written summary; numbers checked against the engine" or the template notice.

### 9.4 Accessibility checklist (WCAG 2.2 AA)
- Colour is never the only signal: verdict, gate state and tags have text and icons.
- Contrast ≥ 4.5:1 for text, 3:1 for chart lines and UI parts.
- Targets ≥ 24×24 px (aim for 44×44 on mobile).
- Full keyboard use; visible focus not hidden behind sticky headers; logical tab order; skip link.
- Every chart has a text summary and a "show as table" toggle.
- Sliders have labels, current value text and keyboard steps.
- Tooltips also open on tap and focus; dismiss with Escape.
- Live regions announce "Analysis updated" and voice states.
- `lang` attribute switches with the UI language.
- Respect `prefers-reduced-motion`.

---

## 10. Phase-Wise Development Roadmap

### 10.0 Shared Rules (every phase prompt includes these by reference)

> **SR-1 Inspect first.** Read the repo, the source plan and this file before changing anything. Reuse existing conventions.
> **SR-2 No fabrication.** Never invent numbers, citations, API responses, model IDs, credentials or test results. Missing data → `null` + a line in `DATA_TODO.md`.
> **SR-3 Tags everywhere.** Every numeric value shown or returned carries `tag` (`measured|published|assumed|synthetic`) and, where relevant, `grade`, `source_ids`, `alpha`.
> **SR-4 Engine purity.** `engine/compass` has no web, LLM or file-system imports except loading `/data` through one loader.
> **SR-5 LLM limits.** The LLM may only parse and explain. Every LLM output passes schema validation and the number verifier, or falls back to the template.
> **SR-6 Secrets.** No keys in code, git, prompts, logs or the browser bundle.
> **SR-7 Fallbacks.** Every user-facing feature has a working fallback (snapshot, template, manual form).
> **SR-8 Tests with every rule.** Each new rule or formula gets a test. Run all tests before reporting done.
> **SR-9 Accessibility and i18n.** No hard-coded user-facing strings in components (use i18n keys). Meet Section 9.4.
> **SR-10 Indian formats.** Money via `Intl.NumberFormat('en-IN')`; per-kg-protein basis for every cost comparison.
> **SR-11 One-line assumptions.** If something is unclear, state the assumption in one line in the commit message and continue, unless it touches safety, secrets or deletion.
> **SR-12 Report honestly.** End each phase with: implemented / tested / failed / not done / known limits.
> **SR-13 Commit and push** at least hourly with a clear message (hackathon rule).
> **SR-14 Time box.** If a phase overruns by more than 30 minutes, drop its lowest-tier items and move on.

### 10.1 Timeline and tiers (IST, 24–25 Oct)

| Phase | Time box | Owner | Tier |
|---|---|---|---|
| 0 Declare + repo + contracts | 12:30–1:00 PM | Engine lead | 0 |
| 1 Data layer (runs in parallel all day) | 1:00 PM → 3:00 AM | Data lead | 0 |
| 2 Engine core | 1:00–3:30 PM | Engine lead | 0 |
| 3 Gates, diagnosis, chains, `/analyze` | 3:30–6:30 PM | Engine lead | 0 |
| 4 Frontend core + design system | 1:00–6:30 PM | Frontend lead | 0 |
| 5 Decision intelligence (MC, EVPPI, Pareto, readiness, plan) | 6:30–9:30 PM | Engine + Frontend | 1 |
| 6 AI layer (Bedrock, verifier, Bayesian update) | 8:00–11:00 PM | Story lead + Engine | 2 |
| 7 Hindi + voice | 9:30 PM–12:30 AM | Frontend lead | 2/3 |
| 8 Hardening, accessibility, snapshots, deploy | 12:30–3:30 AM | All | 0 |
| 9 Pitch package | 10:00 PM–7:30 AM | Story lead | 0 |
| 10 Post-hackathon: accounts, privacy, persistence | Month 1–2 | — | — |
| 11 Post-hackathon: languages via BHASHINI | Month 1–3 | — | — |
| 12 Post-hackathon: pilot loop and production | Month 2–6 | — | — |

Mentor rounds (2:30–4:30 PM, 6:00–8:00 PM) fall inside Phases 3–5: bring a running screen to each.

---

### Phase 0 — Declare, repository and contracts

**Overview.** Create the skeleton every teammate can work in at once. **Requirements:** rules (declare, push hourly, no keys). **Dependencies:** none. **Time box:** 30 min.

#### Master prompt — Phase 0
**A. Objective.** Create the repo `upcycle-compass` with the folder layout of source plan §10.2 plus `web/src/locales/`, `api/llm/`, `web/public/snapshots/`. Out of scope: any engine maths or UI screens.
**B. Prerequisites.** Python 3.11, Node 20, Git, team GitHub repo. Problem statement declared through the organisers' form by 1:00 PM (a person does this, not the agent).
**C. Tasks.**
1. Create folders and empty modules from source plan §10.2.
2. `engine/compass/models.py`: Pydantic types `Tag` (enum), `Grade` (A–D), `Dist` (`type`, `low`, `mode`, `high`), `Param` (`value|dist`, `unit`, `tag`, `grade`, `source_id`, `alpha`, `conditions`, `notes`), `Range` (`p10`, `p50`, `p90`, `tag`, `grade`, `source_ids`, `alpha`).
3. `api/main.py`: FastAPI app with `/health` and a stub `/analyze` that returns the response shape from source plan §14.2 filled with clearly marked placeholder values (`tag: "synthetic"`).
4. `web/`: Vite + React + TS + Tailwind + shadcn/ui; one page that calls `/health`.
5. Script `scripts/gen_types.sh` that runs `openapi-typescript http://localhost:8000/openapi.json -o web/src/api/types.ts`.
6. `.env.example` (Section 8.4), `.gitignore`, `README.md` with run commands and the PoC disclaimer, `DATA_TODO.md` header.
7. CI-free `Makefile` targets: `make api`, `make web`, `make test`, `make snapshots`.
**D. Technical.** Ruff + Black for Python, ESLint + Prettier for TS. Conventional commits.
**E. UX.** Not applicable beyond a working health indicator.
**F. Testing.** `pytest` runs (one smoke test). `npm run build` succeeds.
**G. Acceptance.** `make api` and `make web` both start; the web page shows "API: ok"; types generate; repo pushed.
**H. Deliverables.** Repo skeleton, README, `.env.example`, generated `types.ts`.
**I. Agent instructions.** Follow SR-1…SR-14. Do not add libraries beyond Section 8.1 without saying why.

**Exit gate.** Declaration submitted; repo pushed; every teammate can run it.
**Risks.** Version conflicts on laptops → pin versions in `requirements.txt` and `package-lock.json`.

---

### Phase 1 — Data layer (parallel track, all day)

**Overview.** Fill `/data/*.json` with sourced, tagged rows so the engine has real inputs. **Requirements:** FR-03…FR-08 inputs; honesty rules. **Dependencies:** Phase 0 schemas. **Owner:** Data lead.

#### Master prompt — Phase 1
**A. Objective.** Create and validate `byproducts.json`, `compounds.json`, `treatments.json`, `applications.json`, `costs.json`, `safety_gates.json`, `lab_tests.json`, `sources.json` per source plan §11. Out of scope: engine logic.
**B. Prerequisites.** Source plan §11.3 seed tables; `evidence_seed.csv` and `composition_seed.csv` from earlier work; owner permission for any PhD measured data.
**C. Tasks.**
1. Write a loader `engine/compass/data.py` that reads all files, validates them with Pydantic, and fails loudly with the file and row id on error.
2. Convert seed rows into the schema. Each row: `id`, value or distribution, `unit`, `tag`, `grade`, `alpha`, `conditions`, `source_id`, `notes`.
3. For every value that came from the review draft, set `grade: "C"` and `notes: "from review draft; verify"` until a person checks the original paper; then update.
4. Fill `sources.json` with id, full citation, DOI/URL, access date. Every `source_id` used must exist here.
5. Generate `DATA_TODO.md` automatically from all `null` cells and all `tag: "assumed"` rows, sorted by priority (source plan §19 template).
6. Add a CLI `python -m compass.data --report` that prints counts by tag and grade (feeds the data-completeness meter).
**D. Technical.** One file per type; ids in `snake_case`; units spelled out (`"% dry basis"`, `"ppb"`, `"INR/kg"`).
**F. Testing.** Loader tests: every file validates; every `source_id` resolves; no distribution has `low > mode > high` violations; percentages within 0–100.
**G. Acceptance.** All files load; report shows counts; `DATA_TODO.md` exists; every seed row has a source or is tagged `assumed`.
**H. Deliverables.** JSON files, loader, report CLI, `DATA_TODO.md`.
**I. Agent instructions.** SR-2 is critical here: never fill a value from memory. If the agent drafts candidate rows from an abstract, write them to `data/_staging/` with `tag: "assumed"`, `grade: "D"` for human review (source plan §11.6).

**Exit gate.** Loader green; the three presets have every required input (real or tagged `assumed`).
**Risks.** Unverified aflatoxin claim from the review → encode as source plan §11.3 says (measurement-driven gate, no "autoclave fixes it").

---

### Phase 2 — Engine core

**Overview.** Pure Python maths for sampling, step effects, mass/protein balance, cost and pea parity. **Requirements:** FR-06, FR-07, FR-08. **Dependencies:** Phase 0 models; Phase 1 loader (dummy rows are fine to start).

#### Master prompt — Phase 2
**A. Objective.** Implement `sampling.py`, `effects.py`, `cost.py`, `pea.py` exactly as source plan §12.2, §12.4 (effect formula), §12.5, §12.7, §12.8. Out of scope: gates, chains, EVPPI.
**B. Prerequisites.** Phase 0 models; loader.
**C. Tasks.**
1. `sampling.py`: PERT (λ=4), triangular, uniform, lognormal; Sobol/LHS via `scipy.stats.qmc` with seed; extrapolation penalty `1 + k·(1−α)`.
2. `effects.py`: per-step compound update with floor; mass and protein balance for normal and fractionation steps; cap protein fraction at 0.95; tier assignment.
3. Normalisation: wet → dry basis; true protein = N × f with f ~ PERT(5.45, 5.71, 6.25) unless stated.
4. `cost.py`: per-step energy, water, chemicals, labour, capital (six-tenths rule, CRF at 12%/10 years) → ₹/kg product → ₹/kg protein; kWh and litres per kg protein.
5. `pea.py`: landed cost per kg product and per kg protein; duty modes `full_stack_44`, `full_stack_49`, `bcd_only_igst_credited_22`; closed-form break-even base price; three shock scenarios.
6. All functions are vectorised over draws (NumPy arrays).
**D. Technical.** Type hints everywhere; no global state; seed passed explicitly.
**F. Testing.** Property tests (hypothesis): protein out ≤ protein in; fraction ≤ 0.95; cost ≥ raw cost; no NaN; PERT mean within 1% of analytic; same seed → same output. Unit test the source plan §12.8 sanity example (≈ ₹562 and ≈ ₹476 per kg protein at the stated defaults).
**G. Acceptance.** All tests pass; a script prints P10/P50/P90 cost for one dummy chain in < 1 s for 8,192 draws.
**H. Deliverables.** Four modules + tests.
**I. Agent instructions.** SR-4 (no web imports). Do not add synergy terms (source plan §12.4).

**Exit gate.** Mass-balance and pea tests green.
**Risks.** Unit confusion (% vs fraction) → store fractions internally; convert only at the API edge.

---

### Phase 3 — Gates, diagnosis, chains and the `/analyze` API

**Overview.** Turn the engine into a decision. **Requirements:** FR-03, FR-04, FR-05. **Dependencies:** Phase 2.

#### Master prompt — Phase 3
**A. Objective.** Implement `gates.py` (G1–G7), `diagnosis.py`, `chains.py` and the full `/analyze` endpoint as source plan §12.1, §12.3, §12.4 and §14. Out of scope: EVPPI, Pareto, LLM.
**B. Prerequisites.** Phase 2 modules; `safety_gates.json`, `applications.json`, `treatments.json`.
**C. Tasks.**
1. Gates with three states and "what flips it". A modelled treatment can never turn FAIL into PASS.
2. Diagnosis: exceedance ratio, P(exceed), severity, ranking; non-removal chips (protein density gap, amino-acid limitation, functionality caveat, allergen).
3. Chains: DFS over the precedence DAG with forbidden pairs, max length 4, exclusions and equipment removed first, pruning rules, raw-flour baseline always included, cap 60 chains.
4. `/analyze`: validate input (source plan §8.3 payload), run the pipeline with P10/P50/P90 from a first Monte Carlo pass (full MC comes in Phase 5), return the §14.2 shape. Every numeric leaf carries provenance.
5. `/presets`, `/data/{file}` (read-only, allow-listed file names only).
**F. Testing.** Golden tests GT1–GT6 from source plan §15. API test: invalid payload → 422 with readable messages.
**G. Acceptance.** All three presets return valid JSON in < 3 s; GT1–GT6 pass; regenerated TS types compile in `web/`.
**H. Deliverables.** Modules, endpoints, tests, regenerated `types.ts`.
**I. Agent instructions.** SR-3 (tags on every leaf). If a tolerance is missing, return "no limit available (qualitative)", never a guess.

**Exit gate.** Preset 1 renders end-to-end in the UI (with Phase 4).
**Risks.** Chain explosion → enforce the cap and say "showing top 60" in the response.

---

### Phase 4 — Frontend core and design system

**Overview.** The screens the jury will see. Built in parallel with Phases 2–3 against the stub, then wired to the real API. **Requirements:** FR-01, FR-02, FR-08 (UI), FR-20. **Dependencies:** Phase 0 types.

#### Master prompt — Phase 4
**A. Objective.** Build screens 1–5 and 7 from source plan §14.3 (Input, Verdict + Gates, Diagnosis, Chains, Cost vs pea, Provenance) mobile-first, with the `<Num/>` component used for every number. Out of scope: EVPPI screen, LLM, Hindi content (but all strings go through i18n keys now).
**B. Prerequisites.** Generated `types.ts`; stub or real `/analyze`.
**C. Tasks.**
1. **Design tokens:** colours as CSS variables with light/dark; tag colours M/P/A/S with letter chips; verdict colours paired with icons (✓ GO, ✕ NO-GO, ⚑ TEST-FIRST).
2. **`<Num value range tag grade sourceIds alpha unit/>`:** renders formatted value (`en-IN`), optional P10–P90, chip; tooltip on hover/focus, bottom sheet on tap (mobile); "transferred from …" badge when α < 0.7.
3. **Layout:** top bar (logo, language switch, "show sources" toggle), stepper of screens on desktop, bottom tab bar on mobile (Input, Verdict, Chains, Cost, Next).
4. **Input screen:** three preset buttons; form with react-hook-form + Zod; units selectable (₹/kg, ₹/quintal, ₹/tonne); collapsible "Own batch data"; every field shows its tag; inline validation messages via i18n keys.
5. **Verdict + gates:** big verdict card (label, decision grade, P(GO), reasons); gate cards with state, required test, cost, "what flips this".
6. **Diagnosis:** horizontal bars with whiskers and tolerance line; chips for non-removal issues.
7. **Chains:** sortable table (steps, tier, protein retained, protein %, off-flavour index, ₹/kg protein, P(spec), badges); click → before/after panel.
8. **Cost vs pea:** stacked bars (ours vs pea landed), sliders (pea base US$/kg, FX, freight, duty mode, GST credit, scale), break-even readout, shock-scenario buttons. Slider changes re-call `/analyze` with debounce 400 ms.
9. **Provenance:** global "show sources" toggle; data-completeness meter from `/data` report.
10. States: loading skeletons, empty, error ("Could not analyse. Showing demo snapshot." if a snapshot exists).
11. Footer: disclaimer, limitations link, privacy note.
**D. Technical.** Server state in TanStack Query; UI state in Zustand; no `any`; components in `components/`, screens in `screens/`, charts in `charts/`.
**E. UX.** Plain-language summary line at the top of each screen; detail below. Charts have "show as table".
**F. Testing.** Vitest: `<Num/>` formats ₹ with Indian grouping and always shows a chip; form rejects protein > 100. Playwright: preset 1 → verdict visible → cost screen → slider changes result. axe-core: 0 serious/critical.
**G. Acceptance.** Works at 360 px and 1280 px; keyboard-only path through J1; no number without a chip.
**H. Deliverables.** Screens, components, tests, screenshots at 360 and 1280 px.
**I. Agent instructions.** SR-9 and SR-10. No hard-coded strings in JSX.

**Exit gate.** J1 up to the cost screen works on the real API.
**Risks.** Recharts error bars and accessibility → add the table view for every chart.

---

### Phase 5 — Decision intelligence

**Overview.** The differentiators. **Requirements:** FR-09…FR-13. **Dependencies:** Phases 2–4.

#### Master prompt — Phase 5
**A. Objective.** Implement `montecarlo.py`, `voi.py`, `pareto.py`, `readiness.py`, `plan.py` per source plan §12.9–§12.13 and §12.14, and build screen 6 ("Next step"). Out of scope: Bayesian update (Phase 6).
**B. Prerequisites.** Phase 3 pipeline; `lab_tests.json`.
**C. Tasks.**
1. Full Monte Carlo (8,192 Sobol draws, seeded); joint P(spec); gate inputs as Bernoulli(prior) when unmeasured.
2. Utility with visible parameters (decision volume, failure cost); EVPI; EVPPI by binning (25 bins) grouped by test; EVSI ≈ EVPPI × R; ROI per test; "No test is worth its cost" when true.
3. Pareto on medians + pairwise dominance probability; three named picks.
4. Readiness grade with thresholds from config, shown on screen.
5. Plan generator: tests with method, replicates, cost range, turnaround, acceptance criterion; 6-month timeline and budget tagged `assumed`.
6. UI: Pareto scatter (cost x, protein retained y, colour = off-flavour index, size = P(spec), P10–P90 error bars); EVPPI tornado (top 8); recommended test card; plan table and timeline.
**F. Testing.** EVPPI ≥ 0 and ≤ EVPI; monotonicity (higher pea price never lowers P(margin>0)); readiness rules unit-tested; snapshot of preset 1 values stored for regression.
**G. Acceptance.** Preset 1 shows a recommended test with ₹ cost and EVSI; readiness label with its checklist; `/analyze` still < 3 s on the demo laptop (reduce draws to 4,096 for slider calls if needed and say so).
**H. Deliverables.** Modules, screen 6, tests.
**I. Agent instructions.** Show the utility assumptions on screen. Do not hide a "No test worth buying" result.

**Exit gate.** GT1–GT6 still pass; J1 complete up to "Next step".
**Risks.** Slow MC on the laptop → cache by input hash; precompute presets.

---

### Phase 6 — AI layer: Bedrock, number verifier, Bayesian update

**Overview.** Meaningful AI, safely. **Requirements:** FR-14, FR-15, FR-16 (text). **Dependencies:** Phase 5 JSON.

#### Master prompt — Phase 6
**A. Objective.** Implement `api/llm/client.py` (Bedrock primary, optional Groq/Gemini, template), `prompts.py`, `verify.py`, endpoints `/parse-text`, `/explain`, `/plan` paragraph, and `/update-evidence` with `engine/compass/update.py` per source plan §12.12 and §13. Out of scope: Hindi (Phase 7).
**B. Prerequisites.** Bedrock access in us-east-1; model ID from the console placed in `BEDROCK_MODEL_ID`; local AWS profile on the demo laptop.
**C. Tasks.**
1. `client.py`: `boto3.client("bedrock-runtime", region_name=AWS_REGION).converse(modelId=..., system=[{"text": SYSTEM}], messages=[...], inferenceConfig={"temperature": 0.2, "maxTokens": 700})`; token-bucket throttle (1 req/s); 20 s timeout; one retry; response cache (Section 8.3); provider switch by `LLM_PROVIDER`.
2. `prompts.py`: system prompt "You are a formatter. Use only facts and numbers in the JSON. If something is missing, say it is not available." User data wrapped in delimiters and marked as data.
3. `verify.py`: extract all numbers (handles %, ₹, commas in `en-IN`, decimals, ranges, lakh/crore words); each must match a number in the engine JSON or user input at display rounding; reject unknown `source_id`s; on failure retry once naming the bad numbers, then template.
4. `/parse-text`: text → payload schema; Pydantic validation; return the filled payload plus a list of changed fields; never call `/analyze` automatically.
5. `/explain`: engine JSON → 120–180 word explanation for a food-company reader; returns `{text, llm_used, provider, verifier_passed}`.
6. `update.py` + `/update-evidence`: lognormal conjugate update for continuous inputs; likelihood-ratio update for gate priors; return before/after diff of verdict, P(spec) and EVPPI list.
7. UI: "AI summary" card with badge; "Describe in words" box (text only in this phase) with a confirm step; "Enter your lab result" form on screen 6 with before/after view.
**F. Testing.** GT7 (inject "777" → verifier rejects → template). GT8 (measured phytate → tag M, grade A, EVPPI changes). Unit tests for the number extractor (₹1,00,000; 12.5%; 3–5; "2 lakh"). Throttle test (11 calls → spaced ≥ 1 s).
**G. Acceptance.** With Bedrock off (`LLM_PROVIDER=template`), every AI feature still returns useful text. With Bedrock on, the badge shows "numbers checked".
**H. Deliverables.** LLM package, endpoints, update module, UI cards, tests, a short `docs/AI.md` explaining what the AI does and does not do (for the pitch and Dr. Dey's questions).
**I. Agent instructions.** SR-5 and SR-6 are absolute. Never log user text. Never put the model ID or keys in the frontend.

**Exit gate.** GT7 and GT8 pass; demo of "enter one lab number → recommendation sharpens" works offline (template) and online (Bedrock).
**Risks.** Sandbox deleted before the pitch → the template path and cached responses must be enough for the live demo.

---

### Phase 7 — Hindi and voice input

**Overview.** India-specific access, time-boxed. **Requirements:** FR-16 (voice), FR-17, FR-18. **Dependencies:** Phase 4 i18n keys; Phase 6 parser.

#### Master prompt — Phase 7
**A. Objective.** Add Hindi UI, Hindi explanation, voice input for the "Describe in words" box, and (Tier 3) read-aloud. Out of scope: other languages, server-side speech.
**B. Prerequisites.** All UI strings already behind i18n keys; a Hindi-reading teammate available for 30 minutes of review.
**C. Tasks.**
1. `hi.json` for all keys. Gate texts, warnings, allergen and disclaimer strings written by hand (or drafted then corrected by the reviewer) and marked `"reviewed": true` in a side file `locales/review.json`.
2. `glossary.hi.json` for technical terms; show English term + Hindi gloss on first use per screen.
3. Load Noto Sans Devanagari only when Hindi is active; set `<html lang>`.
4. `/explain?lang=hi`: ask Bedrock for Hindi using only JSON numbers; run the verifier on the Hindi text; show "machine-translated" badge and "show English" toggle.
5. Voice: `useSpeechInput(lang)` hook with feature detection (`SpeechRecognition || webkitSpeechRecognition`), states and errors from Section 7.4, interim transcript, stop button, privacy note, "Type instead". Transcript is editable and goes to `/parse-text`.
6. Read-aloud (Tier 3): `speechSynthesis` for the verdict summary when a matching voice exists.
7. Snapshots generated for both languages (`<preset>.en.json`, `<preset>.hi.json`).
**F. Testing.** Missing-key check script (every key in `en.json` exists in `hi.json`). Playwright: switch to Hindi → verdict and gate texts in Hindi, ₹ formatting unchanged. Manual voice tests on Chrome desktop, Chrome Android and Safari iOS with en-IN and hi-IN, in a quiet room and with background noise; record results in `docs/voice-tests.md`. Firefox: mic hidden, text works.
**G. Acceptance.** No untranslated strings on core screens; reviewed flag true for all safety strings; voice fills the form in at least Chrome desktop and one phone browser; unsupported browsers degrade cleanly.
**H. Deliverables.** Locale files, glossary, hook, UI changes, voice test notes.
**I. Agent instructions.** Do not machine-translate safety strings silently. If the reviewer is not available, keep those strings in English with a note.

**Exit gate.** J6 works; J3 works by voice on at least one browser and by text everywhere.
**Risks.** Venue noise makes voice demo flaky → demo voice only if it worked in rehearsal; otherwise show the text path.

---

### Phase 8 — Hardening, accessibility, snapshots and deployment

**Overview.** Make the demo impossible to break. **Requirements:** NFR-01…NFR-08, FR-19, FR-21, FR-22. **Dependencies:** Phases 2–7 (whatever is finished).

#### Master prompt — Phase 8
**A. Objective.** Snapshots, export, accessibility and performance fixes, open data pack, deployment, README. Out of scope: new features.
**C. Tasks.**
1. `scripts/build_snapshots.py`: run `/analyze` (and template `/explain`) for each preset × language; write to `web/public/snapshots/`; stamp `engine_version`, `dataset_version`, `generated_at`.
2. Frontend fallback: if `/analyze` fails or times out (8 s), load the snapshot and show "Demo snapshot (offline)".
3. Decision memo: print stylesheet or `react-to-print`; one A4 page; includes sources and limitations.
4. Open data pack: zip of `/data` + `sources.json` + `LICENSE` note; link in footer.
5. Accessibility pass with axe + manual keyboard and screen reader (NVDA or VoiceOver) on J1.
6. Performance: code-split Pareto/EVPPI charts and Devanagari font; check bundle size; Lighthouse mobile.
7. Deploy: frontend to Vercel; public API to Render/Railway with `LLM_PROVIDER=template`; `/health` keep-alive ping. Demo laptop runs local API + web with Bedrock.
8. README: run steps, architecture, PoC disclaimer, limitations, data labels, AI tools used, how to regenerate snapshots.
**F. Testing.** Full test suite; GT1–GT8; Playwright J1 with API stopped (snapshot path); Lighthouse mobile report saved.
**G. Acceptance.** All presets run < 3 s locally; snapshot path works with Wi-Fi off; axe 0 serious/critical; deployed URL works; README complete.
**H. Deliverables.** Snapshots, memo export, data pack, deployment URLs, reports in `docs/`.

**Exit gate.** "Wi-Fi off" rehearsal passes on the demo laptop.
**Risks.** Free-tier cold start → keep-alive ping and snapshot fallback.

---

### Phase 9 — Pitch package (story lead; runs alongside Phases 6–8)

**Overview.** The jury scores only the final presentation and answers. **Dependencies:** official template (by 10 PM), working J1.

#### Master prompt — Phase 9
**A. Objective.** Deck on the official template, References slide, 2-minute demo video, rehearsed 4-minute pitch and Q&A answers (source plan §18).
**C. Tasks.**
1. Slides per source plan §18.1 (problem, decision and gap, demo, how it works, honesty, 6-month plan, references).
2. References slide: every dataset, paper, model, library and AI tool (Amazon Bedrock + model name, coding assistant, BHASHINI if used, Web Speech API) as clickable links; label each data source measured/published/assumed/synthetic.
3. Record the ≤ 2-minute screen video of J1 early (before 3 AM) and attach it in the deck slide; re-record only if time allows.
4. Q&A sheet from source plan §18.2 plus: "Why Bedrock?", "What happens when the AWS account is gone?" (snapshots + template), "Is the Hindi reviewed?", "Does voice send audio anywhere?".
5. Rehearse twice with a timer; one person drives the demo, one speaks.
**G. Acceptance.** Deck PDF submitted by 7:30 AM; video attached; links tested; demo laptop charged with offline snapshots ready.

**Exit gate.** Submission confirmed before 8:00 AM.

---

### Phase 10 — After the hackathon: accounts, persistence and privacy (Month 1–2)

**Overview.** Let companies save batches and lab results. **Dependencies:** pilot partner interest.

#### Master prompt — Phase 10
**A. Objective.** Add organisation accounts, saved batches, lab-result history and audit trail, while meeting DPDP obligations. Out of scope: payments.
**C. Tasks.**
1. Database: PostgreSQL (managed, Indian region where available) [Rec]; tables `organisations`, `users`, `batches`, `measurements`, `analyses`, `consents`, `audit_log`; migrations with Alembic.
2. Auth: email OTP or SSO; role-based access (owner, analyst, viewer); sessions with HTTP-only cookies.
3. DPDP: plain-language notice in each supported language listing data, purpose, withdrawal and complaint route; consent records; data-retention schedule; deletion on request; breach-response runbook. Get legal review before launch.
4. Security: OWASP ASVS level 1 checklist, secrets manager, backups with restore tests, encryption at rest and in transit.
**G. Acceptance.** Legal sign-off on notice and consent; restore test passes; penetration test findings fixed.

---

### Phase 11 — After the hackathon: more Indian languages (Month 1–3)

#### Master prompt — Phase 11
**A. Objective.** Add Gujarati, Telugu, Punjabi and Marathi, then more languages, with human-reviewed safety text.
**C. Tasks.**
1. Use BHASHINI translation (API credentials from the platform) to draft locale files; native-speaker review for every safety, legal and allergen string.
2. Optional: BHASHINI or IndicConformer speech recognition for languages the browser handles poorly; measure word error rate on 50 recorded domain phrases per language before enabling.
3. RTL support and Urdu after layout checks.
**G. Acceptance.** Per-language review sign-off; transcription accuracy recorded; no untranslated core strings.

---

### Phase 12 — After the hackathon: pilot loop and production (Month 2–6)

#### Master prompt — Phase 12
**A. Objective.** Connect the tool to real lab and pilot data (source plan §18.3) and run it as a reliable service.
**C. Tasks.**
1. Import lab results by CSV from partner labs; each becomes a `measured` row with method and CV.
2. Calibration report: predicted P10–P90 vs measured outcomes for at least 3 batches; coverage published in the app.
3. Monitoring: uptime checks, error tracking, LLM verifier failure rate, latency dashboards; alerts to the team.
4. Release process: staging environment, versioned dataset releases, changelog shown in the app.
**G. Acceptance.** Calibration coverage reported; 99% monthly uptime target [Assumption]; incident runbook tested.

---

## 11. Cross-Phase Integration and Compatibility

- **One API contract.** Pydantic models are the source of truth; regenerate `web/src/api/types.ts` after every API change (`make types`). The frontend build fails if types are stale.
- **Dataset versioning.** `dataset_version` in every response and snapshot; bump it when `/data` changes; regenerate snapshots before submission.
- **Engine version.** Semantic version in `engine/compass/__init__.py`; snapshots record it.
- **Branching.** `main` always runs. Feature branches per phase; merge after the phase's tests pass.
- **Merge order on the night.** Data rows can merge any time (loader validates). Engine changes merge before UI changes that depend on them.
- **i18n keys.** New UI strings need an English key immediately and a Hindi entry before Phase 7's exit gate.

---

## 12. Deployment and Launch Strategy

### 12.1 Demo-day runbook (25 Oct)
1. 6:00 AM: final `make test`; rebuild snapshots; push; submit deck, video link and repo/live link.
2. Demo laptop: local API + web running; Bedrock profile valid (if the account still exists); browser zoom 110%; notifications off; second tab with the snapshot version open.
3. Phone hotspot as backup network.
4. If anything fails on stage: switch to the snapshot tab and say "this is the same engine output, precomputed".
5. Be at the venue 15 minutes before your slot.

### 12.2 Post-hackathon launch
Staging → closed pilot with one mill and one brand → public beta with English and Hindi → add languages (Phase 11).

---

## 13. Post-Launch Maintenance and Improvement
- Monthly dataset release: new verified rows, retired assumptions, updated prices (AGMARKNET/SEA), changelog.
- Track verifier failure rate and model changes; re-run GT7 on every model update.
- Quarterly accessibility audit and language review.
- Feedback button on the verdict screen: "Was this useful?" + optional comment (no personal data).

---

## 14. Success Metrics and Validation

| Metric | Hackathon target | Pilot target |
|---|---|---|
| Presets that run end-to-end live | 3 of 3 | — |
| Presets that run offline | 3 of 3 | — |
| Numbers without a tag | 0 | 0 |
| LLM outputs passing the verifier (after one retry) | 100% shown text verified or template | ≥ 95% [Assumption] |
| `/analyze` time (preset, laptop) | < 3 s | < 3 s p95 |
| axe serious/critical issues on core screens | 0 | 0 |
| Golden scenarios GT1–GT8 | 8 of 8 | — |
| Literature backtest of limiting compounds | Report N and agreement honestly | Expand N |
| Calibration coverage of P10–P90 | — | 80% ± 10% of outcomes inside the band [Assumption] |
| Voice transcription usable (no edits needed) | Recorded in `docs/voice-tests.md` | Measured per language |
| Pilot partners | — | 1 mill + 1 brand [Source plan] |

---

## 15. Risk Register and Mitigation Plan

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AWS sandbox deleted before pitch | Medium | High | Template + cached responses + snapshots; ask organisers (A2) |
| Venue Wi-Fi fails | Medium | High | Snapshots; phone hotspot; local API |
| Bedrock throttling (1 req/s) | High | Medium | Token bucket, cache, precompute preset explanations |
| Scope overrun | High | High | Tiers; time boxes; SR-14 |
| Wrong science number on a slide | Medium | High | Verify review numbers against originals; tag grade C until checked |
| Aflatoxin misstatement | Low | Very high | Gate is measurement-driven; no treatment clears FAIL |
| Unreviewed Hindi safety text | Medium | High | Fixed reviewed strings; otherwise keep English |
| Voice demo fails in noisy hall | High | Low | Show text path; voice only if rehearsed |
| PhD data used without permission | Low | High | Get permission in writing (message is fine) or leave it out |
| Keys leaked to git | Low | High | `.gitignore`, pre-commit secret scan (e.g. `gitleaks`) |
| Free-tier API cold start | Medium | Medium | Keep-alive ping; snapshot fallback |

---

## 16. Research Sources and References

**India users and devices**
- IAMAI–Kantar Internet in India 2025 (coverage): https://www.communicationstoday.co.in/?p=392523 and https://www.ap7am.com/en/119335/indias-internet-user-base-crosses-950-million-in-2025
- IAMAI–Kantar 2024 (voice use, mobile): https://www.business-standard.com/industry/news/india-to-exceed-900mn-internet-users-by-2025-125011600669_1.html

**Privacy law**
- DPDP Rules 2025 phased timeline: https://www.hlc.com/en/publications/indias-digital-personal-data-protection-act-2023-brought-into-force-
- AZB & Partners summary: https://www.azbpartners.com/bank/indias-digital-personal-data-protection-act-phased-rollout-and-key-compliance-milestones/

**Languages and speech**
- BHASHINI overview: https://anantamias.com/bhashini-bhasha-interface-for-india/
- `bhashini-client` (Python): https://pypi.org/project/bhashini-client/
- IndicTrans2 paper: https://huggingface.co/papers/2305.16307 ; repo: https://github.com/AI4Bharat/IndicTrans2
- IndicConformer ASR: https://github.com/AI4Bharat/IndicConformerASR
- Web Speech API support: https://www.assemblyai.com/blog/speech-recognition-javascript-web-speech-api and https://www.testmuai.com/learning-hub/speech-recognition-api-browser-support/

**Accessibility**
- WCAG 2.2: https://www.w3.org/TR/WCAG22/

**Pea isolate price cross-check (Indian B2B listings)**
- https://www.indiamart.com/proddetail/pea-protein-isolate-23662128530.html
- https://www.tradeindia.com/manufacturers/pea-protein.html

**Hackathon and science**
- Hack the Fork 2026 Participant Guide and Problem Statements (provided by organisers)
- All science and market references: source plan §19

---

## 17. Final Implementation Checklist

**Before 1:00 PM**
- [ ] Problem Statement 2 declared
- [ ] Repo created and pushed; everyone can run it
- [ ] Owner permission asked for PhD measured data

**Before the 2:30 PM mentor round**
- [ ] Engine core tests green
- [ ] Input screen and one preset visible
- [ ] Questions ready: account deletion timing (A2), aflatoxin limit to use, which application matters most to brands

**Before the 6:00 PM mentor round**
- [ ] `/analyze` with gates, diagnosis, chains, cost vs pea
- [ ] Screens 1–5 on the real API

**Before 10:00 PM (lockdown)**
- [ ] EVPPI + recommended test working
- [ ] Bedrock explain with verifier (or template)
- [ ] Anything needed from the hostel collected

**Before 3:30 AM**
- [ ] GT1–GT8 pass
- [ ] Snapshots in English (and Hindi if done)
- [ ] Deployed URL + offline rehearsal passed
- [ ] Demo video recorded

**Before 7:30 AM**
- [ ] Deck on official template, References slide with clickable links and data labels
- [ ] Every AI tool named
- [ ] Submission confirmed (closes 8:00 AM)
- [ ] Laptop charged, snapshot tab open, hotspot ready

# Where AI is used in Upcycle Compass, and where it is not

This page answers Dr. Dey's questions: what the AI does, what it is not allowed to do, and how we stop it from inventing numbers.

## 1. The decision itself is not an LLM

The verdict, the treatment chains, cost vs pea isolate, P(spec) and the test to buy first come from a **probabilistic decision engine** (`engine/compass`):

- **Monte Carlo over every uncertain input:** 8,192 seeded Sobol draws. Distributions are tagged measured / published / assumed / synthetic. Ranges widen automatically when evidence is borrowed from another species.
- **Expected value of information (EVPI / EVPPI / EVSI):** which single measurement would most improve the decision, compared with its cost. "No test is worth its cost: decide now" is a possible, honest answer.
- **Bayesian updating (the learning loop):** enter one lab result and the input's distribution becomes the posterior (lognormal update with the assay CV). For the aflatoxin screen, a likelihood-ratio update with ELISA sensitivity and specificity is used. The analysis re-runs and shows before and after.

No model is trained. There is no dataset of Indian by-product treatments large enough to justify one, and a fake "trained" model would hide uncertainty.

## 2. What the LLM may do (language only)

| Endpoint | What it does | Fallback |
|---|---|---|
| `POST /explain` | 120–180 word plain-language summary of the engine JSON | deterministic template built from the same JSON |
| `POST /plan` | one paragraph on the next experiment, from the computed plan and test values | template paragraph |
| `POST /parse-text` | free text (typed or, in Phase 7, spoken) → form fields. The user checks the highlighted fields and presses Analyse; it **never** analyses by itself | rule-based reader (English and common Hindi words), then "please fill the form" |

The LLM may **not** produce numbers, citations, compound or treatment facts, limits or prices that are not already in the engine output or the user's input.

## 3. Guardrails (all implemented and tested)

- **Provider order:** Amazon Bedrock (`converse`, us-east-1, model id from `BEDROCK_MODEL_ID`) → optional Groq → template. Set by `LLM_PROVIDER`.
- **Secrets:** credentials come only from the environment or a local AWS profile, never from code, git, prompts, logs or the browser. The model id is never sent to the frontend.
- **Settings:** temperature 0.2, at most 700 tokens, a 20 s timeout, one retry, and at most 1 request per second per process (token bucket; requests queue rather than fail).
- **System prompt:** "You are a formatter. You may only use facts and numbers present in the JSON you are given…"
- **Prompt-injection defence:** user text is wrapped in `<user_text>` delimiters and marked as data whose instructions must be ignored.
- **Number verifier** (`api/llm/verify.py`):
  - It extracts every number as an Indian reader writes it (₹1,00,000; 12.5%; 3–5; "2 lakh"; "1.5 crore"; −4,075).
  - Each must match a number in the engine JSON or the user's input at the precision shown; probabilities may appear as %.
  - Source ids not in `sources.json` are rejected.
  - On failure the request is retried once, naming the bad numbers, and then the template is used.
- **Parsing check:** numbers in a parsed form must appear in the user's text (per-quintal and per-tonne conversions allowed). Otherwise the rule-based reader is used.
- **Display:** a badge says "AI-written summary; numbers checked against the engine" or "Template summary". Text is rendered as plain text, never HTML.
- **Logging:** each call records provider, model id, latency and verifier result. User text is never logged.
- **Caching:** LLM responses are cached by hash(endpoint, input, language, model) in memory and in `api/.cache/` (git-ignored), so the demo works offline after a dry run.
- **Rate limit:** 10 requests per minute per IP on `/explain`, `/plan` and `/parse-text`.

## 4. Tests

- **GT7:** an LLM reply containing ₹777 is rejected twice and the template is shown (`api/tests/test_ai.py`).
- **Verifier:** the extractor handles ₹1,00,000, 12.5%, 3–5, "2 lakh" and "1.5 crore"; unknown sources are rejected; the template passes its own verifier.
- **Throttle:** 11 calls are spaced at least 1 s apart.
- **GT8:** a measured phytate value becomes tag M, grade A, and the value-of-information ranking and P(spec) change (`engine/compass/tests/test_update.py`).
- **Bayesian maths:** posterior variance is smaller than prior variance. A negative ELISA lowers P(fail) but keeps G1 TEST-FIRST, and an HPLC value of 60 ppb flips the verdict to NO-GO.

## 5. Running with Bedrock (demo laptop only)

```bash
export AWS_PROFILE=<your sandbox profile>
export AWS_REGION=us-east-1
export LLM_PROVIDER=bedrock
export BEDROCK_MODEL_ID=<copy from the Bedrock console>
make api
```

The public deployment runs with `LLM_PROVIDER=template` (website plan A3). If the AWS sandbox is deleted before the pitch, every feature still works on the template path.

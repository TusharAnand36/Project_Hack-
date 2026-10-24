# Q&A sheet: 4 minutes of questions

Answer in one or two sentences, then offer to show the screen. Questions are grouped by the judge most likely to ask (source plan §3).

Where the source plan's §18.2 answer no longer matches the build, the answer here has been corrected. Those answers are marked **(updated)**.

## Data and evidence (any judge)

| Question | Answer |
|---|---|
| Where do your numbers come from? | Every number is tagged measured, published, assumed or synthetic, with a source and an evidence grade. The ledger is public: 161 missing, 41 assumed, 37 still to verify. Missing values stay empty; we never fill them with a guess. |
| Why is almost everything TEST-FIRST? **(updated)** | Because the key lot assays (aflatoxin, metals, hexane) and food-grade records are not measured yet. Saying GO on literature ranges would be false precision. One real lab result can change the verdict, which is what the demo shows. |
| Did you use the organiser datasets (FAOSTAT, IFCT, USDA, FooDB, Open Food Facts, AGMARKNET, data.gov.in)? **(updated)** | They are listed as sources and fit our data model. In this version no value has been drawn from them yet. Our values come from the team's review, the pea paper and cited trade sources. Pulling AGMARKNET cake prices and IFCT composition in is the next data task. |
| Accuracy of the limiting-compound diagnosis? **(updated)** | We have not backtested yet. Our 170 automated tests check that the rules work as written, not that predictions are accurate. Accuracy is the first thing the six-month plan measures: predict for 3–5 real lots, then assay them. |
| Is the cost real? **(updated)** | The pea side is a transparent scenario: about ₹518 per kg protein landed (₹431–619), tagged assumed. Our own route cost shows "not calculable" until yield and process costs are measured. We do not claim a saving. |
| Duty ambiguity? | The two tariff sources disagree (43.96% vs 49.15%), and IGST may be creditable for a GST-registered buyer. The tool exposes this as a duty-mode switch rather than picking one silently. |

## Food science (Dr. Padma Ishwarya S.)

| Question | Answer |
|---|---|
| Autoclaving and aflatoxin? | We do not claim it. Aflatoxin is heat-stable. The gate depends on measurement, and a failing lot is diverted, not "treated". |
| Why sunflower for a protein-rich flour? **(updated)** | Our dataset does not flag sunflower as a major allergen, unlike groundnut, soy and almond. Flour is the least-processed of the three targets, so it is a practical first trial; if the batch falls short on protein, the tool says a concentration step must be tested. The tool still flags lysine as the limiting amino acid and asks for a batch profile. |
| How do you handle the nitrogen-to-protein factor? | We keep crude protein with the lab's recorded factor. We do not apply a generic oilseed factor to claim true or digestible protein. |
| Functionality? | The tool shows 8 properties side by side (cake flour, extracted isolate, the pea study) with assay conditions. It declares no winner, because the studies are not head-to-head. It proposes matched assays for the target product. |
| Isn't pea hypoallergenic? | Yes, and groundnut can never claim allergen-free; the tool flags it. That is one reason the lead demo is sunflower. |
| How does a flour reach a high-protein target? | The tool separates flour from concentrate and isolate. If the reference composition suggests a protein gap, it says the batch must be assayed and a concentration step (for example alkaline extraction with isoelectric precipitation) tested. It never relabels raw flour as a concentrate. |

## AI (Dr. Lipika Dey)

| Question | Answer |
|---|---|
| Where is the AI? **(updated)** | It has two parts. First, a probabilistic decision engine: gates, uncertainty ranges, value-of-information and Bayesian updating, which switch on only where calibrated inputs exist. Second, an LLM restricted to parsing text and explaining results, with a verifier that rejects any number not in the engine output. |
| Why not train a model? | There is no dataset of Indian by-product treatments large enough. A "trained" model would hide uncertainty, the opposite of what a food-safety decision needs. The case-feedback store is how we would collect that data. |
| What if the LLM hallucinates? | It cannot change engine numbers. The verifier blocks sentences with unmatched numbers (including lakh/crore and Devanagari digits), and a deterministic template is the fallback. |
| Does the feedback loop learn? **(updated)** | It stores case feedback and shows matching future cases the aggregate counts and suggested checks. It does **not** retrain anything or change safety limits, and private notes are never shown to other cases. |
| Why Bedrock? | The organisers provided a Bedrock sandbox, and keeping the LLM behind one interface lets us swap providers. Credentials stay on the demo laptop's local profile, never in code or on the public server. |
| What happens when the AWS account is gone? | Nothing breaks. The public server already runs template-only, and the app falls back to stamped offline snapshots for all five presets, in English and Hindi. |

## Decision support and readiness (Prof. Kavya Dashora)

| Question | Answer |
|---|---|
| When can a prediction support a reliable decision? | When the gating evidence is measured on the lot, not borrowed. The verdict shows a decision grade and the readiness checks that must pass first. Uncalibrated probabilities are withheld rather than shown. |
| How do you validate the engine? | Predict ranges for 3–5 real lots, measure them, and report how often the measurement falls inside the predicted range (calibration coverage). |
| What must be shown before scaling? | Safety assays on real lots, measured yield and protein recovery, matched functional and sensory tests, then a pilot run with real energy, water and cost (the six-month plan). |

## Data model and openness (Prof. Ganesh Bagler)

| Question | Answer |
|---|---|
| Is the knowledge computable and open? | Yes. It is versioned JSON with JSON Schemas, a source on every value, a REST API (`/data/*`, `/analyze`) and a downloadable open-data pack. The licence is still to be chosen by the team. |
| Flavour-compound grounding? | Off-flavour drivers are modelled where the evidence exists. Sensory acceptance is left to a measured panel, not a score we can't defend. |

## Language and voice

| Question | Answer |
|---|---|
| Is the Hindi reviewed? | Not yet. The UI strings are machine-drafted. Safety wording (verdict labels, gate states, disclaimers) stays in English until a Hindi-reading reviewer checks it, and Hindi AI summaries carry a "machine-written" badge. |
| Does voice send audio anywhere? | The app doesn't upload audio. The browser's speech service does the recognition (Chrome: Google; Safari: Apple), and the screen says so. The transcript fills an editable box; nothing is submitted until you press Analyse. |

## Competition and positioning

| Question | Answer |
|---|---|
| How is this different from GFI's TEA spreadsheets, NotCo or Shiru? | Those model one process or discover new molecules. We combine safety gating, treatment-route evidence, cost per kg protein against imported pea, and "what to test first" for commodity Indian by-products. |
| Who pays? | First users are mills that sell cake at feed prices, plant-protein brands hedging pea imports, and incubators choosing pilots. For now our ask is partners, not revenue: a food-grade mill, a lab and a brand. |

## If something goes wrong

- **Wi-Fi fails or the API is down:** keep going. The app loads the stamped offline snapshot ("Demo snapshot (offline)"). Say: "This is the offline snapshot, same engine, precomputed."
- **A question we can't answer:** "We don't know yet. That is exactly the kind of gap the tool lists; it's on our validation plan."

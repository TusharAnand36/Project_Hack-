# Final workflow audit — 25 October 2026

Engine **0.8.0**, dataset **2026-10-25.1**. This is an evidence-aware prototype;
the six-month laboratory/pilot programme is proposed future work.

## Reviewed inputs

The implementation was checked against the supplied Final Coding Agent Handoff,
Final Build and Presentation Playbook, Research Evidence Matrix, final oilseed
review, both review drafts, August research plan, preliminary LoR/proximate report,
and Qi et al. (2025), *Modulating the functional properties of pea protein isolate*
([paper](https://doi.org/10.1016/j.fochx.2025.102898)). The handoff is a project
specification, not proof of laboratory validation. Original unpublished documents
and full paper text are not copied into the repository.

## Implemented behaviour and principal files

| Area | Files | Result |
|---|---|---|
| Input/traceability | `engine/compass/contract.py`, `web/src/forms/schema.ts`, `web/src/screens/InputScreen.tsx` | Lot, supplier, origin, material form, dehulling, route records, price source/date/boundary, assay basis/method/lab/report metadata; parsed text requires review. Plain form labels retained. |
| Decision and safety | `engine/compass/workflow.py`, `gates.py`, `data/safety_gates.json`, `WorkflowDimensions.tsx` | Safety, technical feasibility, economics and evidence shown separately. Unknown safety/route/category evidence cannot clear a final GO. All seven project contaminant thresholds retained. |
| Diagnosis | `diagnosis.py`, `workflow.py`, `DiagnosisScreen.tsx`, `ExceedanceBars.tsx` | Ratios require compatible measured values and a positive justified threshold. TIA raw=100 is illustrative, not an assay. Point comparisons are not 0%/100% probabilities. Incompatible assay basis is explicitly blocked. |
| Treatment candidates | `analyze.py`, `montecarlo.py`, `ChainsScreen.tsx`, `data/treatments.json` | Unsupported mass-yield/recovery inputs stay missing. Research candidates show study scope/conditions and missing inputs, with no fabricated yields, success probabilities, ranking or Pareto optimum. |
| Protein and costs | `analyze.py`, `workflow.py`, `CostScreen.tsx` | Crude protein retains its recorded factor; no generic true-protein correction. Ingredient mass, initial/recovered protein, retention and concentration stay separate. Dry-basis input needs moisture conversion. Incomplete cost boundaries are partial/lower bounds. |
| Commercial targets | `workflow.py`, `contract.py`, form and Cost screen | Manual cap, pea benchmark minus discount, or finished-product budget divided by required protein. Cap changes economics independently of safety/compound diagnosis. |
| Functional comparison | `data/functional_evidence.json`, `data/research_evidence.json`, `FunctionalComparison.tsx`, `EvidenceExplorer.tsx` | Eight properties per material, separate whole-cake flour/extracted isolate/pea study, source conditions and matched next tests. Research matrix has 75 contextual records. |
| Next/lab update | `plan.py`, `learning.py`, `LabResult.tsx`, `NextScreen.tsx` | Critical tests precede economic VOI. Unit/lot validation, report metadata, before/after results and proposed six-month phase gates. VOI is not estimated without calibrated inputs. |
| Feedback | `api/feedback.py`, `api/main.py`, `FeedbackForm.tsx`, hooks/store | New case ID per live query, case/chain validation, one feedback receipt per case, on-disk SQLite, private notes, scoped aggregate follow-up suggestions for future queries. Storage failures never claim success. |
| Memo/offline | `MemoScreen.tsx`, `scripts/build_snapshots.py`, public snapshots/data | Same analysis object drives screens, memo and case JSON. Memo includes case/version/time, lot, decision dimensions, target formula, critical test, sources and limitations. Five bilingual preset snapshots and data pack regenerated. |

Generated API types, JSON schemas, regression fixture, locale keys and tests were
updated with the contract. `.runtime/` and SQLite files are excluded from Git.
See the commit file list for the full generated-artifact manifest.

## Scientific assumptions corrected

- Missing data is neither zero nor a favourable PASS. Missing treatment mass yield
  or protein recovery no longer becomes a uniform 0–1 simulated prediction.
- Published material ranges are references, not assays of the selected batch.
  Synthetic preset measurements and user assumptions are visibly distinct.
- Unknown extraction history requires evidence. A declared non-solvent route needs
  a supporting record; a certificate checkbox is not a quantitative residue result.
- Supply provenance needs lot/supplier/handling records. A microbiological panel
  alone cannot establish food-grade provenance. Regulatory/intended-use review is
  separate and precedes a pilot GO.
- The contaminant values are **user-specified internal project thresholds**, with
  unit, scope, as-received basis and effective-date metadata. They are not described
  as independently established legal limits. Assumed/demo assays cannot clear gates.
- TIA percentages normalised to raw activity cannot be compared with arbitrary
  assay thresholds. Phytate needs an explicit internal dry-basis target.
- P(GO), P(spec), P(margin>0), EVPI and EVPPI are not calibrated by the supplied
  sources and remain unestimated. A deterministic threshold check is not a
  probability. Critical testing remains necessary independently of economic VOI.
- Raw material/flour is not a concentrate. Unmeasured extracted purity is an
  unclassified fraction. Application fit needs functional/sensory validation.
- Cost uses recovered protein mass and a declared boundary. Dry matter and
  as-received material cannot be mixed without moisture data. Unsupplied drying,
  separation, logistics, QA, waste and other costs cannot support a profit claim.
- Pea ingredient price and protein cost are different. Shared import-price/duty
  scenarios are illustrative; freight +20% is relative to baseline freight.
  The +25% base-price scenario makes no unsupported anti-dumping-policy claim.
- Discount-adjusted benchmark difference is benchmark × (1 − discount) − our
  cost; it is not validated profit. The historic ₹124/₹605/₹420 claim is not retained
  as an established saving.

## Research records and comparison scope

Final review Tables 9 and 10 inform whole-cake-flour and extracted-isolate
references respectively. These are secondary/review-reported values; primary
papers, methods and material forms need checking before numeric prediction.
Drafts overlap and do not count as independent studies. Treatment effects retain
applicable material, reported conditions and sources. Preliminary LoR values are
withheld from production predictions pending sample identity, basis and permission.

The pea paper supplies the commercial isolate composition **80.2% protein** and
formulation context, not a supplier price. It studies gellan gum/salt modification,
not oil-cake extraction or detoxification. Solubility, foaming, emulsion and gel
conditions remain explicit. For example, the reported 25.08% EAI increase is a
relative change, not an absolute EAI; the reported 36.07% foam-capacity decrease is
relative to its own control. Pea emulsion stability at 30 minutes is not directly
comparable to a review value at 24 hours. Water/oil absorption and least gelation
concentration are marked not reported where absent. No head-to-head winner is
claimed. Sunflower, soy and groundnut reference ranges are separated; almond
functional data remains unknown where unsupported.

Rice bran remains unavailable for analysis. Sunflower snack is first, with
groundnut beverage, soybean meat analogue, almond meat analogue and pea beverage
as secondary presets. All use the same shared pea pricing assumptions.

## Feedback and future-query use

Each live HTTP analysis creates an immutable request snapshot and fresh UUID,
even if the science calculation is cached. Feedback validates the case and optional
candidate ID and persists useful/not-useful, trial outcome, issue category, private
notes and time. A new API/store instance can read the same database.

Future queries matching material, intended application, declared extraction route
and dataset version receive aggregate counts and issue-specific follow-up actions
(such as matched texture, yield or solubility tests). Notes are not returned to
other cases. These self-reported observations are unverified and never overwrite
scientific parameters, safety thresholds, assays or verdicts. This is a transparent
feedback loop, not an automatically trained predictive model.

The local database is `.runtime/feedback.sqlite3`. A public deployment must set
`FEEDBACK_DB_PATH` on persistent storage. With public storage unconfigured, analysis
continues but case feedback cannot be saved. Offline snapshots have no live case ID
and cannot accept feedback. No hosted database, paid disk, user authentication or
production retention service was provisioned by this change.

## Exact demo and expected result

1. Open `/#/compass` and choose **Sunflower cake → high-protein / fibre snack**
   (`sunflower_snack`), the first preset.
2. Expected verdict: **TEST-FIRST**, hypothesis grade. Critical aflatoxin, metals,
   route/residue, food-grade documentation and regulatory review remain unresolved.
3. Four dimensions: safety needs verification; technical needs validation;
   economics not calculable; evidence hypothesis grade. P(GO) is not estimated.
4. Diagnosis shows all seven project thresholds. Unmeasured assays do not generate
   exceedance bars. The eight-row functional table separates cake flour, extracted
   isolate and pea-study conditions, with no unsupported winner.
5. Nine supported baseline/candidate routes are shown, unranked. With this preset's
   missing batch basis and recovery, predicted protein/yield/cost and P(spec) remain
   null. These are experimental hypotheses, not validated optimised chains.
6. Cost shows a shared illustrative pea benchmark, distinct ingredient/protein
   units and a target formula. Blank manual target means no cap.
7. Next puts critical tests first (the aflatoxin ELISA screen, followed by required
   confirmation/other checks), economic VOI unestimated, and a proposed six-month
   validation plan. ELISA alone does not establish total-aflatoxin compliance.
8. A live case has a feedback form. A subsequent matching live analysis receives
   aggregate follow-up observations after feedback is saved. For a clean demo,
   do not seed synthetic feedback into the real database.
9. Lab update can show a measured lead exceedance causing NO-GO, with before/after
   results and metadata. Use a disposable database for synthetic demonstrations.
10. Memo and downloaded case JSON carry the same decision data. Switching off the
    API loads a stamped offline preset; offline feedback is unavailable.

## Verification and remaining work

Verification on this change:

- Backend: **144 passed** (`pytest -q`). Black and Ruff pass. Two upstream
  Starlette/httpx/anyio deprecation warnings remain; no test failures.
- Frontend: **26 passed** across 11 files; locale validation passes. The added
  case-switch regression verifies that a previous case is withheld during the
  new request's debounce and network response, keeping feedback/memo/export aligned.
- Production TypeScript/Vite build and ESLint pass. Vite reports a non-blocking
  main-chunk size warning (about 506 kB uncompressed); no build error.
- Live HTTP smoke: all five presets, fresh distinct case IDs, seven contaminant
  checks, eight functional rows, evidence endpoints, ten en/hi snapshots and ZIP
  integrity pass. No synthetic feedback was inserted into the normal local DB.
- Database tests use temporary SQLite files: persistence across store instances,
  similar-case follow-ups, private-note isolation, unchanged safety, case/chain
  validation, duplicate rejection, unavailable hosted storage and lab history pass.
- Browser: live sunflower verdict/diagnosis/candidate/Next flow inspected; mobile
  layout checked at 360×800 with no document horizontal overflow. Five production
  presets load stamped offline snapshots; Hindi template summary and disabled
  offline feedback inspected. Functional comparison screenshot saved in
  `docs/screenshots/functional-comparison-2026-10-25.jpg`.
- Generated schemas, OpenAPI TypeScript types, DATA_TODO, regression fixture,
  bilingual snapshots, offline evidence files and ZIP regenerated. Obsolete
  sunflower-beverage snapshots removed. Encoding scan and Git whitespace check pass.

The legacy raw-Playwright CLI scripts were not used for the browser check;
verification used the available browser automation interface. Arbitrary-case print
pagination, voice/microphone hardware, hosted deployment and primary scientific
validation have not been independently tested by this change.

Outstanding research/deployment work is explicitly outside what code alone can
complete: primary-paper verification of the full treatment database, independent
lot assays, matched pea/cake experiments, real supplier/process/lab quotes, validated
yield/recovery and sensory distributions, pilot measurements, calibrated VOI,
techno-economic analysis, life-cycle analysis, qualified regulatory review and
authenticated production data governance. Full Hindi scientific copy needs a
qualified reviewer; unreviewed safety/scientific wording remains in English.

The prototype has not established an industrial optimum, food safety approval,
health benefit, sustainability advantage or proven cost saving. Deployment and
persistent hosted storage remain separate operational setup work.

## Differences from earlier screenshots and documentation

The old screenshots' single-letter/default form badges are absent. Results retain
full-word provenance and source details. The homepage's ivory/forest visual system
is preserved. Sunflower snack replaces the older sunflower beverage demo. Missing
process predictions, 100% success displays, zero-valued uncomputed VOI and implicit
no-treatment-needed claims are replaced with explicit evidence gaps. The updated
README reflects these behaviours; `docs/PHASES.md` is historical. The memo contains
more traceability than the original screenshot; automatic one-page printing must
not be assumed for arbitrary long case notes or citations.

# References slide

Paste this into the template's References slide, splitting it over two slides if needed, and keep every link clickable.

**Labels.** Each row carries the provenance labels its values have in `/data` (dataset 2026-10-25.1):

- **P** published
- **A** assumed
- **M** measured
- **S** synthetic

"Cited" means the source supports notes, conditions or comparison rows rather than an engine input.

- **Regenerating the labels.** They were counted from `data/*.json`. Recount them after any data change.
- **Organiser datasets.** These are listed in `sources.json` but **no value has been drawn from them yet**. Say so if asked; do not present them as used.

## Team documents (unpublished; cited, not distributed)

| Source | Labels | Note |
|---|---|---|
| Team review, *From By-Product to Functional Food: Valorization of Cold-Pressed Oilseed Cakes* (final draft) | P (30 values), cited in 40 comparison rows | Review-reported (secondary) where primary papers are not yet checked |
| Team research plan, 5 Aug 2026 | P (4) | |
| Team research evidence matrix, 25 Oct 2026 (75 records) | cited | Context records; overlapping drafts not counted as independent |
| Project contaminant acceptance limits, 24 Oct 2026 | A (8) | Internal project settings, not verified legal limits |
| Earlier review drafts; R. O. Mathur PhD progress report (LoR and proximate) | not used | Report withheld from calculations pending sample identity, basis and permission |

## Peer-reviewed papers and reviews

| Source | Labels |
|---|---|
| Qi X. et al. (2025). Modulating the functional properties of pea protein isolate. *Food Chemistry: X*. [doi.org/10.1016/j.fochx.2025.102898](https://doi.org/10.1016/j.fochx.2025.102898) | P (2), cited in 40 comparison rows |
| Murugeswari (2023). Aflatoxin B1 in feed and feed raw materials in India: 5-year survey, 118 groundnut-cake samples. [agris.fao.org](https://agris.fao.org/search/fr/records/6851787853e52c13fc76fde0) | P (1) |
| Singh et al. (2022). Protein for human consumption from oilseed cakes. *Front. Sustain. Food Syst.* [frontiersin.org](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2022.856401) | background |
| Detoxification of groundnut meals. *Nature* 209, 406 (1966). [nature.com](https://www.nature.com/articles/209406a0) | background (aflatoxin is heat-stable) |
| El-Kady & Farghaly. Aflatoxin inactivation by heat. [archive.org](https://archive.org/download/biostor-278424/biostor-278424.pdf) | background |

## Market, trade and price sources

| Source | Labels |
|---|---|
| PBFIA via Agron Food Processing: ~90% of plant-protein ingredients imported; ₹4,500 → 9,000 crore. [agronfoodprocessing.com](https://agronfoodprocessing.com/?p=31333) | slide 1 claim |
| GFI India orphan-crops whitepaper (coverage). [vegconomist.com](https://vegconomist.com/agriculture-agribusiness/indias-orphan-crops-could-unlock-new-plant-protein-supply-chain-gfi-india-argues/) | slide 1 context |
| Tridge: pea protein (80–85%) export prices, China. [tridge.com](https://dir.tridge.com/prices/grass-pea-protein/CN) | P (1) |
| USD/INR quotes, Sep–Oct 2026. [banklive.net](https://banklive.net/en/convert/usd-to-inr) | P (1) |
| India import tariff HS 35040099 (two sources disagree: 43.96% vs 49.15%). [eximpe.com](https://eximpe.com/hsncode-finder/35040099) | P (2) |
| IndiaMART / TradeIndia pea protein isolate B2B listings. [indiamart.com](https://www.indiamart.com/proddetail/pea-protein-isolate-23662128530.html) | P (1), B2B cross-check |
| IndiaMART trader listing (oilseed-cake prices). [m.indiamart.com](https://m.indiamart.com/mahalakshmi-oils) | A (1) |
| EU provisional anti-dumping duties on Chinese pea protein (31 Mar 2026). [wko.at](https://www.wko.at/oe/aussenwirtschaft/information-at-provisional-stage-pre-disclosure-1.pdf) | cited |
| Canada CBSA pea protein measures. [cbsa-asfc.gc.ca](https://www.cbsa-asfc.gc.ca/sima-lmsi/mif-mev/hpc-eng.html) | context |
| Expana Plant-Based Protein Report, March 2026. [mintecglobal.com](https://www.mintecglobal.com/hubfs/Expana%20Plant-Based%20Protein%20Report%20-%20March%202026.pdf) | context |

## Organiser-provided open datasets (listed; no values drawn yet)

- [FAOSTAT](https://www.fao.org/faostat/en/#home)
- [IFCT 2017 via @nodef/ifct2017](https://jsr.io/@nodef/ifct2017)
- [USDA FoodData Central](https://fdc.nal.usda.gov) ([downloads](https://fdc.nal.usda.gov/download-datasets))
- [FooDB](https://foodb.ca)
- [Open Food Facts](https://world.openfoodfacts.org)
- [AGMARKNET](https://agmarknet.gov.in/home)
- [data.gov.in mandi daily prices](https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi)
- [data.gov.in variety-wise daily prices](https://www.data.gov.in/resource/variety-wise-daily-market-prices-data-commodity)

## AI tools

| Tool | Use |
|---|---|
| [Amazon Bedrock](https://aws.amazon.com/bedrock/), model: **fill in the exact model id from `BEDROCK_MODEL_ID` on the demo laptop** | Optional runtime: parses text and writes summaries; every number is verified against the engine. The public demo uses the template only. |
| [Groq](https://groq.com) | Optional alternative provider (not used in the demo unless configured) |
| [Claude Code](https://claude.com/claude-code) (Anthropic) | AI coding assistant that wrote and tested the code from the team's plans; the team reviewed and committed it |
| [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) | Browser speech input and read-aloud; audio is processed by the browser's speech service (Chrome: Google; Safari: Apple) |
| BHASHINI | Not used |

## Software libraries

- **Python:**
  - [FastAPI](https://fastapi.tiangolo.com) 0.143.0
  - [Starlette](https://www.starlette.io) 1.3.1
  - [Uvicorn](https://www.uvicorn.org) 0.34.0
  - [Pydantic](https://docs.pydantic.dev) 2.10.4
  - [NumPy](https://numpy.org) 2.2.1
  - [SciPy](https://scipy.org) 1.15.0
  - [pandas](https://pandas.pydata.org) 2.2.3
  - [boto3](https://github.com/boto/boto3) 1.35.90
  - SQLite (standard library)
  - Tests: [pytest](https://pytest.org) and [Hypothesis](https://hypothesis.works)
- **Web:**
  - [React](https://react.dev) 18.3.1
  - [Vite](https://vite.dev)
  - [TypeScript](https://www.typescriptlang.org)
  - [Tailwind CSS](https://tailwindcss.com)
  - [TanStack Query](https://tanstack.com/query) 5.62.11
  - [Zustand](https://zustand.docs.pmnd.rs) 5.0.2
  - [React Hook Form](https://react-hook-form.com) 7.54.2
  - [Zod](https://zod.dev) 3.24.1
  - [Radix UI](https://www.radix-ui.com)
  - [i18next](https://www.i18next.com) 24.2.0 / react-i18next 15.4.0
  - Tests: [Vitest](https://vitest.dev), [Playwright](https://playwright.dev) and [axe-core](https://github.com/dequelabs/axe-core)
- **Code and data:** repository [github.com/TusharAnand36/Project_Hack-](https://github.com/TusharAnand36/Project_Hack-). The open data pack is linked in the app footer.

**Before export:** click every link in the exported PDF (task 2 of the plan's acceptance criteria).

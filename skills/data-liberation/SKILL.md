---
name: data-liberation
description: Build Python data pipelines that liberate structured data from unstructured and semi-structured sources — government PDFs, FOIA releases, scanned reports, scraped HTML, panel-format spreadsheets — into tidy, documented, reproducible civic datasets. Works at six escalating levels, from a one-shot "just give me the CSV" extraction (L0) up to a fully published, governed, multi-source pipeline (L5) — start low and climb only as far as the task needs. Use whenever the user wants to extract tables or data from PDFs, get a CSV out of a document, scrape a government or institutional site for tabular data, scaffold a reproducible data project, harmonize records across multiple sources, write a data dictionary or crosswalk, audit data against originals, publish a dataset, or wrangle messy historical data. Trigger on phrases like "data liberation," "PDF extraction," "get the data out," "tidy data," "data dictionary," "crosswalk," "provenance," "reconcile," "scrape this site," even when the user does not name the skill explicitly; if the request involves turning a document into a dataset someone else could reuse, this skill applies. Do not trigger for pure ML model training or generic Python tutoring unrelated to data extraction.
---

# Data Liberation

A skill for turning documents — PDFs, scraped pages, panel-format spreadsheets, scanned archives — into tidy, documented, reproducible datasets in the civic-data tradition. It operates at **six increasing levels of complexity**: getting a CSV out of a PDF is one command and one level; a fully published, governed, multi-source pipeline is the same skill, five levels up. Start at the lowest level that satisfies the request and offer to climb — never make a user buy the whole apparatus to get a table out of a PDF.

## The six levels

Each level *adds* to the one before. The levels describe **how far** a given engagement goes; the [six-phase workflow](#the-six-phase-workflow) below describes **how** the work gets done within a project.

| Level | Name | The "___ path" | What it adds | Primary reference |
|---|---|---|---|---|
| **L0** | Extract | "just the data" | The CSV(s). **No scaffold, no project** — read the source, emit the table, done. | [`extract-*` family](references/extract-pdf.md) (pdf · tabular · documents · web · images) |
| **L1** | + Documentation | "make it citable" | A data dictionary, a per-extract `provenance.csv`, a short README / Survey note, a one-line ethics note | [`data-modeling.md`](references/data-modeling.md#data-dictionary), [`context.md`](references/context.md) |
| **L2** | + Pipeline & Audit | "someone can re-run this" | A scaffolded project, `pipeline.py`, a pandera schema contract, `audit.py`, `reconcile.py`, the reject port | [`project-template.md`](references/project-template.md), [`pipeline.md`](references/pipeline.md) |
| **L3** | + Harmonization | "the multi-source path" | A concept catalog / crosswalk (`concepts.py`) with caveats — the cross-source-equivalence contract | [`data-modeling.md`](references/data-modeling.md#concept-catalogs) |
| **L4** | + Standards & Governance | "publishable, responsibly" | DCAT / PROV / DQV / FAIR naming (optional, never a gate); a full governance section | [`context.md`](references/context.md), [`project-template.md`](references/project-template.md#governance) |
| **L5** | + Publishing | "queryable, documented, distributed" | Datasette, a Quarto docs site, Git LFS, DocumentCloud | [`publishing.md`](references/publishing.md) |

**Guardrail: L0 and L1 must NOT scaffold a project.** Getting to a CSV is frictionless by design; the scaffold is an L2+ commitment. Emitting a stray project skeleton for a one-shot extraction is the single most common way this skill becomes an adoption blocker.

### How to surface levels — infer, confirm, climb

Do not ask the user to read this table. Instead:

1. **Infer** the *lowest* level that satisfies the request, from the phrasing (table below).
2. **State the assumption and offer a redirect**, in one sentence: *"This reads like **L0** — just the data. I'll start there unless you want the reproducible-pipeline path (L2)."*
3. **Execute** that level fully.
4. **Offer the next rung** at the end: *"Done — here's `data.csv`. Want me to go to **L1** and add a data dictionary + provenance so this is citable?"*

When the user names a level, jump straight to it. When signals span levels, infer the highest explicitly named level but **start at the lowest prerequisite and climb**, confirming at each rung.

| User phrasing signals | Infer |
|---|---|
| "get the data out," "give me a CSV," "extract the table from this PDF," "what's in this spreadsheet," "scrape this page into a table" | **L0** |
| "so I can cite it," "document this," "data dictionary," "what do the columns mean," "make this reusable," "where did this come from," "provenance" | **L1** |
| "reproducible," "pipeline," "so someone can re-run it," "audit," "validate against the original," "reconcile," "schema," "add tests" | **L2** |
| "harmonize," "crosswalk," "combine these two sources," "compare across years/agencies," "concept catalog," "make them comparable" | **L3** |
| "standards," "DCAT / FAIR / PROV," "governance," "license," "PII / privacy," "CARE," "is it OK to publish," "FOIA redactions" | **L4** |
| "publish," "Datasette," "queryable," "put it online," "documentation site," "Quarto," "Git LFS / large files," "DocumentCloud," "embed the source docs" | **L5** |
| "scaffold a new civic data project," "set up a data liberation project" | **L2** (the full scaffold is the explicit ask) |

The level menu, if a user asks what the skill can do:

```
Data-liberation has six levels, each adding to the one before:
  L0  Extract            → source to CSV. No setup. "Just the data."
  L1  + Documentation    → data dictionary, provenance, README note. Now citable.
  L2  + Pipeline & Audit → scaffolded, reproducible, validated. "Someone can re-run this."
  L3  + Harmonization    → crosswalks across sources, with caveats. Multi-source.
  L4  + Standards & Gov  → DCAT/PROV/FAIR naming + governance/ethics. Publishable responsibly.
  L5  + Publishing       → Datasette, Quarto site, Git LFS, DocumentCloud.
I'll start at the lowest level that fits your ask and offer to climb. Say a level to jump there.
```

## How levels and phases relate

A project does its work in six phases. A *level* is how many of those phases (and which artifacts) a given engagement actually reaches.

```
┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────┐  ┌───────┐  ┌─────────┐
│ Survey  │->│ Scaffold │->│ Extract │->│ Tidy │->│ Audit │->│ Publish │
└─────────┘  └──────────┘  └─────────┘  └──────┘  └───────┘  └─────────┘
  understand   set up        pull text     reshape +  verify     serve via
  the source   the project   + tables out  document   vs. truth  Datasette
```

| Level | Phases it reaches |
|---|---|
| **L0** | Extract |
| **L1** | (light Survey) + Extract + Tidy's *documentation* artifacts |
| **L2** | Survey + Scaffold + Extract + Tidy + Audit |
| **L3** | adds the multi-source harmonization part of Tidy |
| **L4** | adds the cross-cutting governance/standards pass |
| **L5** | adds Publish |

## When to use this skill

Trigger when the user is:
- starting a new data liberation project from a PDF, FOIA release, scraped site, panel-format Excel, or other unstructured source
- asking how to extract tables from a specific document, or just wanting the data out of one
- adding a new source or vintage to an existing liberation pipeline
- asking how to scaffold, document, audit, harmonize, or publish a reproducible civic data project
- wrangling messy historical data (mixed formats across years, mid-period schema changes, OCR-only old vintages)

Hand off when:
- the task is a genuine one-liner ("read this PDF and tell me what it says") — answer directly (that *is* L0); mention the skill can go further if they'll do this more than once
- the user wants ML modeling on already-clean data — out of scope; this skill ends where modeling begins
- the user wants generic Python help unrelated to data extraction

## The six-phase workflow

This skill maps to the CRISP-DM phases of **data understanding → preparation → deployment**, deliberately stopping before modeling and evaluation (the analyst's domain after liberation is done). The framing is distilled from PUDL, the Boulder Public Data repos, and the IPEDS pipeline; the academic grounding is in [`context.md`](references/context.md#academic-framing).

**Vocabulary alignment with industry frameworks.** The six phases map onto the steps named by mainstream data-workflow frameworks (Monte Carlo's 8-step model, adjacent dbt / observability vocabularies). Use these as searchable synonyms — the names differ; the work is the same:

| Industry term | This skill's phase | What's named |
|---|---|---|
| **Goal Planning / Data Identification** | Survey | `discover.py` + Survey notes; unit-of-observation choice; codebook hunt |
| **Data Extraction** | Extract | `fetch.py` + per-vintage parsers' `read_*` calls |
| **Data Cleaning and Transformation** | Tidy (+ the cleaning pipeline) | 9-step parser-time pipeline in [`pipeline.md`](references/pipeline.md#the-cleaning-pipeline) |
| **Data Loading** | end of Tidy / start of Publish | `clean.py` writing the canonical CSV; `publish.py build` materializing SQLite |
| **Data Validation** | Audit | `pandera` schema at the boundary; `audit.py`; `reconcile.py`; the reject port |
| **Data Lineage** | (within Audit) | `provenance.csv` per-extract sidecar joined by `(source, vintage)` |
| **Data Observability** | (within Audit) | The diff-able `data/audit/summary-*.md` reviewed on every refresh PR |
| **Data Governance** | (cross-cutting, L4) | License inheritance, PII policy, data-subject considerations — see [`project-template.md`](references/project-template.md#governance) |
| **Data Analysis and Modeling** | **Out of scope** | The skill stops at the deployment phase of CRISP-DM |
| **Data Maintenance** | recurring-refresh pattern | Cron-driven `discover → fetch → clean → audit` opening a reviewable PR; see [`pipeline.md`](references/pipeline.md#the-recurring-refresh-pattern-cron--pr) |

### 1. Survey — understand the source before touching code (L1+)

Before opening a Python file, answer: **What is this document?** (born-digital PDF, scanned PDF, HTML, panel-format XLSX, CSV, JSON, database export?) **What is the unit of observation?** (one row per ballot? per precinct × contest × candidate? per institution × year × variable? — the most consequential, hard-to-reverse decision). **What are the structural quirks?** (merged headers, tables split across pages, footnotes that change column meaning, mid-period schema changes). **What is the public-interest stake, and what history of access does the source have?** (FOIA / MuckRock / CORA requests, prior journalism — cite in the README.)

**Ask before assuming.** Before writing code, ask the user what *documentation* exists (codebooks, the publisher's own dictionary, the mandating statute — almost always more reliable than reverse-engineering), what *prior work* has touched the data (journalism, papers, FOIA logs, past GitHub repos), the *canonical contact* (records officer, the journalist who last covered it), and what *corroborating source* could turn reconciliation from "compare to the source's own total" into "compare to an independent count." If the user supplies a URL, FOIA ID, prior repo, or paper, read it first. The full bulletproofing checklist is in [`pipeline.md`](references/pipeline.md#pre-extraction-bulletproofing); the FOIA / records-request process and the standards-registry check are background in [`context.md`](references/context.md). Background, not a gate.

Write a one-page Survey note (it seeds the README). Decide whether this is **bespoke** (one-time, single source — often L0/L1) or **infrastructural** (recurring, multi-source, harmonized — L2+). The two share scaffolding; the second invests more upfront in `discover.py`, the concept catalog, and CI.

### 2. Scaffold — set up the project (L2+)

**Skip this entire phase at L0 and L1** — emit the data and its documentation directly to the user's working directory; do not generate a project skeleton.

**New project (L2+):** Scaffold from the **bundled template** at [`templates/project/`](templates/project/) — render it into the user's working directory: for each file, strip a trailing `.tmpl` to get the output path, substitute the `{{UPPER_SNAKE}}` slot-fills (`PROJECT_NAME`, `PROJECT_SLUG`, `DESCRIPTION`, `AUTHOR`, `OWNER`, `CONSUMER_STACK`), and strip any `<!-- IF:FLAG -->…<!-- /IF -->` block whose flag is off. Read [`references/project-template.md`](references/project-template.md) for what each file does and why, and for the full slot-fill table. Write only into the user's directory, never into this skill's; leftover `{{ }}` is a bug. Do not invent a parallel structure. The skeleton, abbreviated:

```
project-name/
├── data/{original,processed,audit,lookups}/   <- immutable raw → tidy → reports → crosswalks
├── scripts/{schema,sources,config,fetch,clean,audit,pipeline}.py + parsers/
├── tests/                                      <- pytest: schema contracts, parser fixtures
├── docs/{data-dictionary.md, filter-pivot-recipes.md}
├── AGENTS.md  README.md  pyproject.toml  .github/workflows/
```

The full annotated tree is in [`project-template.md`](references/project-template.md#the-skeleton). Bootstrap from single-source but keep the multi-source-ready layout (`scripts/parsers/<source>_<vintage>.py`, `data/original/<source>/<vintage>/`) from day one so a second source is a parser file, not a refactor.

**Existing project:** Read the project's `AGENTS.md` for conventions, identify where the new source fits in the Source registry, then implement the `Source` contract in a new module under `scripts/parsers/`.

### 3. Extract — pull text and tables out (L0+)

Match the input type to the toolchain, then open **only the extraction reference for the input you have** — the L0 toolchain is split by input so an agent extracting a PDF never loads the scraping or OCR material. Per-tool guidance, decision trees, and gotchas live in each file:

| Input | Default → fallback | Reference |
|---|---|---|
| Born-digital PDF (text) / ruled grid | `pdfplumber` / `camelot` (lattice) | [`extract-pdf.md`](references/extract-pdf.md) |
| Scanned / image-only PDF, photos, image files, maps | `tesseract` → PaddleOCR / Surya / docling VLM | [`extract-images.md`](references/extract-images.md) |
| XLSX (clean / panel-format), CSV, Parquet, database | `read_excel` / `openpyxl` / `read_csv` (explicit dtypes) / `read_parquet` / `sqlalchemy` + `duckdb` | [`extract-tabular.md`](references/extract-tabular.md) |
| HTML (table / layout), XML, JSON | `read_html` / `selectolax` / `lxml` + XPath / `json_normalize` | [`extract-documents.md`](references/extract-documents.md) |
| Web scrape (dynamic / recurring) | `requests` + cache / `playwright`; Wayback fallback | [`extract-web.md`](references/extract-web.md) |
| Multi-format corpus, end-to-end | `docling` / `kreuzberg` | [`extract-documents.md`](references/extract-documents.md#modern-unified-extractors--when-one-tool-is-enough) |

At **L1+**, capture a per-extract manifest entry (input SHA256, page range or URL, tool + version, timestamp, row count) appended to `data/processed/provenance.csv` — the sidecar, joined by `(source, vintage)`, not carried on every row. See [`data-modeling.md`](references/data-modeling.md#provenance).

At **L2+**, within each per-vintage parser run the cleaning pipeline in order: **profile → structural fixes → deduplication → missing-value treatment → outlier detection → normalization → validation + reject port → PII redaction → log**. Each step has concrete tooling. See [`pipeline.md`](references/pipeline.md#the-cleaning-pipeline). Malformed rows go to a reject port (`data/audit/rejected.csv`) — errors are durable, not fatal.

### 4. Tidy — reshape and document (L1+ docs, L3 harmonization)

Default to **Wickham-tidy long format**: one row per observation, one column per variable, one cell per value. The rationale, and the few wide-as-primary exceptions (e.g. Cast-Vote-Records), are in [`data-modeling.md`](references/data-modeling.md#wickham-tidy-as-the-storage-shape).

At **L1+**, generate `docs/data-dictionary.md` by hand (one row per column with type, units, source vocabulary, caveats) and ship `docs/filter-pivot-recipes.md` with side-by-side **pandas / tidyverse / DuckDB** recipes so readers recover wide views. See [`data-modeling.md`](references/data-modeling.md#filter-pivot-recipes).

At **L3**, for multi-source projects maintain a **concept catalog** — a harmonization crosswalk mapping source-specific codes (IPEDS `EFTOTLT`, CDHE `TOTAL_HEADCOUNT`) to source-neutral concepts (`enrollment.headcount_fall_total`), where concepts carry not just labels but **caveats** explaining what is and isn't comparable. See [`data-modeling.md`](references/data-modeling.md#concept-catalogs).

At **L2+**, validate the output with **pandera** schemas at the pipeline boundary plus **pytest** on parser behavior. See [`data-modeling.md`](references/data-modeling.md#validation).

### 5. Audit — verify against the truth (L2+)

Once the pipeline runs end-to-end:

- **`scripts/audit.py`** — per-source row counts, dtype conformance, NA rates, unique-key constraints, year coverage → `data/audit/summary.md`. Always include. See [`pipeline.md`](references/pipeline.md#audit-what-came-in).
- **`scripts/reconcile.py` (optional)** — re-opens each original, sums top-line totals (votes per contest, enrollment per institution), compares to the processed CSV; any new mismatch is a regression. Recommended whenever the originals carry an authoritative total. See [`pipeline.md`](references/pipeline.md#reconciliation).
- **`scripts/discover.py` (optional)** — scrapes upstream pages for newly-published files not yet in the registry; pair with a scheduled Action for self-refreshing pipelines. See [`pipeline.md`](references/pipeline.md#discovery).

### 6. Publish — make the dataset usable (L5)

The processed CSV is the deliverable; **L5 adds up to four deployment surfaces**, split so an agent working in one layer only pays the context cost for that one. All four are in [`publishing.md`](references/publishing.md):

- **Datasette** (`scripts/publish.py build` / `deploy`) — the processed CSV + `provenance.csv` become a single SQLite via `sqlite-utils` (composite key, indexed facets, optional FTS), shipped as a public read-only [Datasette](https://datasette.io/) with SQL editor, faceting, and JSON API. `metadata.yaml` is generated from the data dictionary. The "Baked Data" architecture (DB rebuilt on every deploy) is the canonical civic shape.
- **Quarto on GitHub Pages** — `.qmd` files in `docs/` become the methodology, tutorials, and long-form dictionary site. Datasette serves the *data interface*; Quarto serves the *prose about how to use it*.
- **Git LFS** — multi-gigabyte source PDFs, archives, and large Parquet sit in LFS via `.gitattributes`. **Architectural constraint: LFS does not work with GitHub Pages**, so the Quarto site links out to Datasette and GitHub Releases rather than embedding LFS-tracked data.
- **DocumentCloud** — the source-document layer: upload the underlying PDFs / FOIA responses with reader-facing OCR, annotations, page-level permalinks, and embed iframes for the Quarto site.

At **L4**, an optional standards pass: the published `metadata.yaml` is already a **DCAT**-shaped record, a `dcat-us.jsonld` can be emitted for catalog federation, and a quick **FAIR / DWBP** self-check ("did we miss a license / stable identifier / provenance link?") is useful before announcing. Background and entirely optional — see [`context.md`](references/context.md). Never block shipping on it.

The recurring-refresh pattern extends naturally: the cron-driven `discover → fetch → clean → audit` PR, when merged, triggers `publish.yml` and `gh-pages.yml`. Anyone who clones can run `uv sync && uv run python -m scripts.pipeline` to regenerate `data/processed/` from `data/original/`.

## Bootstrap quickstart

**L0 / L1 skip the scaffold** — read the source, emit the CSV (and, at L1, the data dictionary + `provenance.csv` + a Survey/README note) straight to the user's working directory, then offer to climb. The steps below are for **L2+**:

1. Produce the Survey notes inline from the user's source.
2. Render the bundled template at [`templates/project/`](templates/project/) into the user's working directory: strip each `.tmpl` suffix, substitute the `{{UPPER_SNAKE}}` slot-fills (`PROJECT_NAME`, `PROJECT_SLUG` — a snake_case identifier derived from the name, `DESCRIPTION`, `AUTHOR`, `OWNER`, `CONSUMER_STACK`), and strip any off-flag `<!-- IF:FLAG -->…<!-- /IF -->` block. Read [`references/project-template.md`](references/project-template.md) for the per-file rationale and the full slot-fill table.
3. Write the rendered files to the user's working directory — not to this skill's directory. Confirm no literal `{{ }}` survived.
4. Suggest `uv sync && uv run pytest` to verify the scaffold; then `uv run python -m scripts.pipeline` for a first end-to-end run on a sample file.
5. Iterate: each new vintage or quirk becomes a new parser file or test case.

## Adding a source to an existing project

1. Read the project's `AGENTS.md` first — it answers the architecture questions.
2. Add the `Source` subclass in `scripts/sources.py` (or a dedicated module) and register it in `scripts/config.py::SOURCES`.
3. Add a parser module under `scripts/parsers/`.
4. Add fixtures + a test under `tests/` — at minimum one fixture per source vintage exercising the parser end-to-end.
5. If the project has a concept catalog, add the new source's variable codes to existing concepts (or add new concepts with caveats explaining what's not comparable).
6. Run `audit.py` and `reconcile.py`. If reconciliation introduces a mismatch, investigate before merging.

## Adding a new vintage to an existing source

1. Add the new year's URL to the source registry.
2. Run `discover.py` — does it pick up the new file automatically?
3. Run `fetch.py` to pull it into `data/original/`.
4. Run `clean.py`. If it crashes, identify whether (a) the schema changed mid-period (add a vintage-specific branch) or (b) a structural quirk needs handling (merged cells, new columns).
5. Re-run audit and reconciliation. Update `docs/data-dictionary.md` with any new caveats.
6. Commit, preferably via PR with the audit + reconciliation diffs visible.

## Reference index

Ten references, grouped by the level each primarily serves and loaded on demand. The five `extract-*` files are the L0 toolchain (open only the input you have); the rest serve L1–L5.

- **L0 — the extraction toolchain, split by input type** (open only the one you have; the routing table is in the [Extract phase](#3-extract--pull-text-and-tables-out-l0) above):
  - [`references/extract-pdf.md`](references/extract-pdf.md) — born-digital PDFs: pdfplumber, camelot, the working parser skeleton.
  - [`references/extract-tabular.md`](references/extract-tabular.md) — XLSX (incl. panel-format), CSV, Parquet, databases; dtype hygiene.
  - [`references/extract-documents.md`](references/extract-documents.md) — HTML, XML, JSON, DOCX; the unified extractors (docling / kreuzberg).
  - [`references/extract-web.md`](references/extract-web.md) — web scraping: ethics, archives, protocols, dynamic pages.
  - [`references/extract-images.md`](references/extract-images.md) — images, OCR (tesseract / PaddleOCR / Surya), preprocessing, and computer-vision layout analysis.
- [`references/data-modeling.md`](references/data-modeling.md) — **L1–L3.** What to produce: Wickham-tidy shape, schema-as-contract, the data dictionary, concept catalogs / crosswalks, provenance, pandera validation, filter-pivot recipes, and the five-dimension quality framework (the canonical definition).
- [`references/pipeline.md`](references/pipeline.md) — **L2.** How to process and verify: the 9-step parser-time cleaning pipeline (the canonical definition), plus discovery, audit, reconciliation, pre-extraction bulletproofing, and the recurring-refresh PR pattern.
- [`references/project-template.md`](references/project-template.md) — **L2 / L4.** The full project skeleton spec — what each file does and why — plus the governance section (the L4 anchor).
- [`references/publishing.md`](references/publishing.md) — **L5.** The four deployment surfaces: Datasette (queryable interface), Quarto (docs site), Git LFS (bulk distribution), DocumentCloud (source documents).
- [`references/context.md`](references/context.md) — **L4 background, not a gate.** The civic-data movement and its critical perspectives, the open-data standards the artifacts already informally implement (DCAT / PROV / DQV / FAIR / DWBP + registries), and the open-government landscape (FOIA, federal mandates, civic tech, portals, the international frame). The only real gates here are privacy law and the CARE principles.

## The bundled template

The project template ships **in this repo** at [`templates/project/`](templates/project/) — no separate repo, no fetch, no version pin. It contains the `pyproject.toml` (uv-managed, Python 3.11+), the one-responsibility `scripts/*.py` modules connected by `pipeline.py`'s argparse CLI, the optional `scripts/concepts.py`, the `_quarto.yml` + `docs/*.qmd` seed, `.gitattributes` LFS rules, `AGENTS.md` / `README.md` / dictionaries, baseline schema-drift tests, and `.github/workflows/` (tests on by default; refresh / publish / gh-pages opt-in via `*.yml.disabled`).

Token-bearing files carry a `.tmpl` suffix and `{{UPPER_SNAKE}}` slot-fills; everything else renders verbatim. **Do not read `templates/` unless you are scaffolding (L2+)** — it is rendered, not reference material; for why each piece is shaped this way, read [`references/project-template.md`](references/project-template.md) instead. `scripts/validate.py` lints the templates and renders them to a temp dir (with `--smoke`, runs `uv sync && pytest` on the result), so a template edit that breaks the scaffold is caught in CI.

## Conventions worth defending

A few that are easy to get wrong:

- **Immutable originals.** Files in `data/original/` are never edited in place after the first commit. Cleaning lives in `scripts/parsers/` and produces `data/processed/`. The hash manifest in `data/original/manifest.json` enforces it. This is what makes the pipeline reproducible.
- **Per-extract provenance, not per-row.** Sidecar `provenance.csv` keyed on `(source, vintage)`, joined when needed. (Per-cell provenance is a different beast — opt-in for audit-grade work.)
- **Concepts carry caveats.** A catalog that just renames variables across sources is a foot-gun. Every concept entry documents what is and is not comparable.
- **Tidy long is the storage shape, wide is the analysis shape.** The filter-pivot recipes in `docs/` are how readers recover human-readable wide views. The trade is worth it for cross-source analysis.
- **AGENTS.md before code.** A new contributor (or future Claude) should read AGENTS.md and know enough to add a source without re-reading the codebase. If it's missing or stale, the architecture is undocumented; fix it.

# Project template: layout, file groups, and the generated scaffold

This reference specifies what a data-liberation project's source tree looks like, which files a project gets and when, what each one does, and the conventions worth defending. The working template is bundled at [`templates/project/`](../templates/project/); this document explains it. Read it before scaffolding, then read only the template files in the groups that are in scope.

## Contents

- [The skeleton](#the-skeleton)
- [File groups](#file-groups)
- [Slot-fills and the render recipe](#slot-fills-and-the-render-recipe)
- [The five working files](#the-five-working-files)
- [Pipeline modules](#pipeline-modules)
- [Tests](#tests)
- [Generated numbers in docs](#generated-numbers-in-docs)
- [Storage budget](#storage-budget)
- [CI workflows](#ci-workflows)
- [The `data/` directories](#the-data-directories)
- [Adding a second source](#adding-a-second-source)
- [Governance](#governance)
- [Architectural principles](#architectural-principles)
- [Conventions worth defending](#conventions-worth-defending)

## The skeleton

The core project, for one source. Files marked *(publish)*, *(refresh)* or *(multi-source)* are generated only when that group is in scope.

```
project-slug/
├── README.md               <- for people using the data; generated headline numbers
├── AGENTS.md               <- how to work here; CLAUDE.md is the one line `@AGENTS.md`
├── CLAUDE.md
├── ROADMAP.md              <- the ten Outline sections: now / later / skip
├── decision-log.md         <- dated decisions and why
├── CHANGELOG.md            <- data and schema changes users need to know
├── LICENSE                 <- MIT for the code
├── pyproject.toml          <- uv-managed, Python >=3.12
├── .gitignore  .gitattributes
├── data/
│   ├── original/           <- immutable, as fetched: <source>/<vintage>/<file>
│   │   └── manifest.json   <- url, sha256, size, fetch time per file (committed)
│   ├── processed/          <- <pkg_name>.csv (+ .parquet) and provenance.csv
│   ├── audit/              <- summary.md, headline.json (committed); per-run logs (ignored)
│   └── lookups/            <- hand-kept vocabularies and crosswalks
├── scripts/
│   ├── pipeline.py         <- the command line: run | fetch | clean | audit | reconcile
│   ├── config.py           <- paths, HTTP defaults, the source's slug/label/license
│   ├── source.py           <- artifacts() and parser_for(): the one source
│   ├── parsers/            <- one module per layout era
│   ├── fetch.py            <- idempotent download, manifest, --fresh
│   ├── clean.py            <- parse → dedupe → validate → conservation check → write
│   ├── schema.py           <- LONG_COLUMNS, KEY_COLUMNS, the pandera contract
│   ├── provenance.py       <- provenance.csv columns and the extraction_method vocabulary
│   ├── runlog.py           <- progress lines and the fresh per-run error log
│   ├── audit.py            <- summary.md, headline.json, variables, generated doc numbers
│   ├── reconcile.py        <- compare against the source's printed totals (opt-in)
│   ├── discover.py         <- (refresh) what is upstream, what is new
│   ├── concepts.py         <- (multi-source) the concept catalog
│   ├── publish.py          <- (publish) SQLite + Datasette metadata
│   └── upload_documentcloud.py  <- (publish) source documents to DocumentCloud
├── tests/                  <- schema, build checks, vintage keys, generated numbers, vocabularies
├── docs/
│   ├── data-dictionary.md  <- one entry per column, hand-kept
│   ├── filter-pivot-recipes.md
│   ├── variables.md/.csv   <- generated column profile
│   └── index.qmd  methodology.qmd   <- (publish) Quarto site, with _quarto.yml at the root
└── .github/
    ├── workflows/tests.yml <- lint, tests, CLI check, storage budget
    ├── workflows/refresh.yml.disabled                     <- (refresh)
    ├── workflows/publish.yml.disabled, gh-pages.yml.disabled  <- (publish)
    └── ISSUE_TEMPLATE/data-correction.yml                 <- (publish)
```

The layout matches what mature civic pipelines converged on (PUDL, BoulderPublicData/Election-Results, the IPEDS pipeline), so a contributor moving between projects finds the same directory doing the same thing.

## File groups

A project starts with `core` and nothing else. Every other group is generated when the Outline section that needs it is reached, and a project's `ROADMAP.md` records which sections are now, later or skip. Generate a group's files together with its flag: the flag keeps the matching `<!-- IF:FLAG -->` blocks in README, AGENTS and the docs, and strips them otherwise. Paths are relative to `templates/project/`. `tools/validate_data_liberation.py` reads this table, renders a minimal (`core`) and a full (every group) project, and tests both.

<!-- BEGIN file-groups -->
| Group | Flag | Generate when | Files |
| --- | --- | --- | --- |
| `core` | — | always: any project (sections 2–6) | every file not listed below: the five working files (`README.md.tmpl`, `AGENTS.md.tmpl` with `CLAUDE.md`, `ROADMAP.md.tmpl`, `decision-log.md.tmpl`, `CHANGELOG.md.tmpl`), `LICENSE.tmpl`, `pyproject.toml.tmpl`, `.gitignore`, `.gitattributes.tmpl`, `data/*/.gitkeep`, the pipeline core in `scripts/`, `tests/`, `docs/data-dictionary.md.tmpl`, `docs/filter-pivot-recipes.md.tmpl`, `.github/workflows/tests.yml` |
| `publish` | `PUBLISH` | section 8 is in scope (visibility is public or embargoed) | `scripts/publish.py.tmpl`, `scripts/upload_documentcloud.py`, `_quarto.yml.tmpl`, `docs/*.qmd.tmpl`, `.github/workflows/publish.yml.disabled.tmpl`, `.github/workflows/gh-pages.yml.disabled`, `.github/ISSUE_TEMPLATE/data-correction.yml` |
| `multi-source` | `MULTI_SOURCE` | a second source arrives (see [Adding a second source](#adding-a-second-source)) | `scripts/concepts.py`, `data/lookups/concepts.yaml`, `tests/test_concepts.py` |
| `refresh` | `REFRESH` | the source publishes new vintages on a cadence (section 10) | `scripts/discover.py`, `.github/workflows/refresh.yml.disabled` |
<!-- END file-groups -->

Two independent questions decide the groups, and they call for different scaffolding: how many sources (a second source justifies the registry and concept catalog) and whether vintages recur (recurrence justifies `discover.py` and the refresh workflow). A single agency's quarterly file needs `refresh` but not `multi-source`; a one-time harmonization of three agencies is the reverse. Don't let "recurring" pull in the multi-source machinery. The `pipeline` command offers `discover` and `publish` only when their modules exist, so a minimal project has no dead commands.

When a group arrives later in an existing project, copy its files, turn its flag's blocks on by hand in README, AGENTS and the docs, and record the change in the decision-log.

## Slot-fills and the render recipe

Scaffolding is agent-driven; there is no scaffold script. For each file in the groups in scope:

1. **Output path:** strip a trailing `.tmpl` (`pyproject.toml.tmpl` → `pyproject.toml`).
2. **Substitute** every `{{UPPER_SNAKE}}` token from the table below.
3. **Conditionals:** keep the contents of `<!-- IF:FLAG -->…<!-- /IF -->` blocks whose group is in scope, drop the others, and remove the markers.
4. **Write** into the user's working directory, never into this skill's folder. A leftover `{{ }}` or `IF` marker is a bug. Never overwrite an existing file without asking.

| Token | What it is | Example |
| --- | --- | --- |
| `{{PROJECT_NAME}}` | the human-readable project name | `Boulder Election Results` |
| `{{PROJECT_SLUG}}` | kebab-case: the repository, distribution and command name | `boulder-election-results` |
| `{{PKG_NAME}}` | snake_case: file stems, SQL table, BibTeX key (anything an import or a query names) | `boulder_election_results` |
| `{{DESCRIPTION}}` | one line on what the project liberates | `Boulder County election results, 1980 to the present` |
| `{{AUTHOR}}` | author string (fall back to `git config user.name <user.email>`) | `Brian Keegan <bkeegan@…>` |
| `{{OWNER}}` | GitHub owner the repository will live under | `BoulderPublicData` |
| `{{CONSUMER_STACK}}` | the users' main tools, comma-separated | `pandas,R` |

The code package is always `scripts/` (run as `python -m scripts.pipeline`), so `PKG_NAME` names data files and tables rather than a Python package. The validator enforces the contract: every token used appears in this table and in its `DOCUMENTED_TOKENS`, `.tmpl` suffixes and tokens agree, every `IF` flag belongs to a group, and both renders pass `uv sync`, ruff and pytest under `--smoke`. When you add a token or a flag, add it here and in the validator in the same change.

## The five working files

These are the files people keep current; every project starts with them (the Outline's "five working files").

- **`README.md`**, for people using the data: "What & why" (filled during scoping: the question, what one row means, the source, who the data is for, what the project won't extract or publish), the data at a glance (generated), how to load it in pandas, R and DuckDB, how to reproduce it, how to report a correction, how to cite a release, and the licenses (code MIT; data CC-BY-4.0 for the project's transformations, with the publisher's terms recorded per source in `provenance.csv`) and disavowed uses.
- **`AGENTS.md`**, how to work here, kept short (about a screen or two): where to start, the commands, where things are, the current state (generated), dated project rules, the pull-request convention (what changed, why, what I checked, what I left alone on purpose), links to this skill's references on GitHub, and the end-of-sprint instruction to file feedback. `CLAUDE.md` contains exactly `@AGENTS.md`; never let a second copy of the rules grow there.
- **`ROADMAP.md`** and **`decision-log.md`** are vendored from the shared templates: the ten Outline sections marked now, later or skip, and dated decisions tagged *Assumed* or *Private* where they apply. Record probe findings, the storage budget and the sensitivity and visibility decisions in the decision-log.
- **`CHANGELOG.md`** records what users of the data need to know: new vintages and sources, corrections (with the affected vintages), and schema changes (with what breaks).

## Pipeline modules

The pipeline is a small package in `scripts/`, one responsibility per module, run as `uv run python -m scripts.pipeline run`. That command runs fetch, clean, audit and reconcile (with discover first when the refresh group is present) and stops at the first non-zero exit.

- **`config.py`:** paths, the processed-file names (`data/processed/<pkg_name>.csv`), the audit outputs, HTTP defaults (a user agent with a contact), and the source's `SOURCE_SLUG`, `SOURCE_LABEL` and `SOURCE_LICENSE`.
- **`source.py`:** the one source. `artifacts()` lists every file upstream as an `Artifact` (source, vintage, URL, local path), cheaply and without downloading: a static list for predictable URLs, or a scrape of the index page. `parser_for(artifact)` returns the parser module by an explicit condition on the vintage; no registry and no dynamic import dispatch. `vintage_from_filename()` reads the period from the file's own name, never from the publish directory (a Q4 file posted in next February's folder is still Q4), and a test pins that case.
- **`parsers/`:** one module per layout era, `parse(path) -> DataFrame`, plus `METHOD` (a canonical `extraction_method`), `TOOLS` (distributions whose versions are recorded) and optionally `QUALITY` and `NOTES`. Keep text extraction separate from line parsing so the PDF engine can change without touching the parser. Per-era modules beat one function full of `if vintage < 2015` branches.
- **`fetch.py`:** downloads what is missing into `data/original/<source>/<vintage>/` and records it in `data/original/manifest.json`. Idempotent; retries with backoff on connection errors and 429/5xx only; rejects an empty body or an HTML error page served for a PDF; prints throttled progress. `--fresh` bypasses the HTTP cache and re-downloads everything; changed bytes replace the file, keep the old hash in `previous_sha256`, and are reported. A file listed in the manifest but missing from disk (kept outside git) is re-downloaded and checked against its recorded sha256. Failures go to a fresh `data/audit/fetch_errors.json` and exit 1; nothing ever substitutes sample, synthetic or stale data.
- **`clean.py`:** for each artifact, parse, tag `source` and `vintage`, and fail loudly on empty output, missing columns, or rows whose key columns are all empty; then deduplicate on the natural key, validate, and set failing rows aside in `data/audit/rejected.csv` with a reason. A conservation ledger (`parsed = duplicates_dropped + rejected + written`) must balance or the build fails. If no rows survive, nothing is written over the previous outputs and the command exits 2. Errors go to a fresh `data/audit/extraction_errors.json`; `--strict` turns any error or reject into a non-zero exit for CI. The CSV is sorted by the key and `provenance.csv` by source, vintage and artifact, so a re-run on the same originals is byte-identical.
- **`schema.py`:** `LONG_COLUMNS`, `KEY_COLUMNS` and the pandera `CanonicalLong` model (`strict`, `coerce`, `unique` on the key), plus `normalize_long`, `dedupe` and `split_valid`. See `data-modeling.md` for the contract.
- **`provenance.py`:** the `provenance.csv` columns (one row per artifact and parser run), the canonical `extraction_method` and `extraction_quality` vocabularies, which `clean` enforces, and tool-version capture. `retrieved_at` comes from the manifest, not the clock, so cleaning is deterministic.
- **`runlog.py`:** throttled progress lines and the error log that starts empty every run.
- **`audit.py`:** reads the processed CSV, checks it holds exactly the rows `clean` wrote, and writes `data/audit/summary.md` (headline, ledger, coverage, artifacts with no rows, extraction methods, null rates, small vocabularies, errors, rejects, and a spot-check sample drawn by hashing the natural key), `data/audit/headline.json`, `docs/variables.{md,csv}`, and the generated blocks in README and AGENTS. None of these contain a timestamp, so an unchanged refresh changes nothing.
- **`reconcile.py`:** opt-in reconcilers that recompute the source's printed totals from the processed rows; `compare_totals` compares the finest grain both sides share and reports one-sided keys as scope differences, not mismatches. Writes `data/audit/reconcile.md` and exits 2 on a mismatch. See `pipeline.md`.
- **`pipeline.py`:** argparse subcommands; `-q` hides progress.
- **`discover.py`** *(refresh):* lists the artifacts upstream, flags the new ones, and writes `data/audit/discovery.md`.
- **`concepts.py`** *(multi-source):* loads `data/lookups/concepts.yaml`; `concept_for()` and `caveats_for()`.
- **`publish.py`** and **`upload_documentcloud.py`** *(publish):* see `publishing.md`. `pipeline publish build|serve|deploy` delegates to `publish.py`.

## Tests

The core tests check the machinery, not any particular source, so they pass on a fresh scaffold:

- `test_schema.py`: good frames validate, missing and unknown columns fail, vintages coerce to strings, `dedupe` keeps the last reading, `split_valid` routes bad rows to the reject file. It imports `pandera.pandas as pa` (pandera 0.24 or later).
- `test_clean.py`: drives `clean.build` with a stand-in parser: the ledger balances with duplicates and rejects, an empty extraction is an error, all-empty keys are degenerate, provenance is deterministic, and an unknown `extraction_method` fails the artifact.
- `test_source.py`: vintage keys come from file names, including the publish-directory trap.
- `test_reconcile.py`: one-sided keys are scope differences; differences beyond the tolerance are mismatches.
- `test_generated_docs.py`: the generated blocks in README and AGENTS match `headline.json`, and `headline.json` matches the processed data.
- `test_lookups.py`: each `data/lookups/vocab_<column>.csv` matches the dictionary's vocabulary line for that column, and observed values stay inside it.
- `test_concepts.py` *(multi-source)*: every concept that maps more than one source has caveats.

Add one `tests/test_<source>_<era>.py` per parser with a small real fixture in `tests/fixtures/` and an assertion against a total printed in that fixture; that is reconciliation at fixture scale, and it runs in milliseconds. Validate a parser on every structural cohort of the corpus (each era, each file-format variant), not on one convenient specimen: a reconcile gate that only ever ran on one file can't catch the file it never saw.

## Generated numbers in docs

Every number quoted in prose (rows, sources, vintages, rejected rows) is generated. `audit` writes `data/audit/headline.json` and rewrites whatever sits between `<!-- BEGIN generated:headline -->` and `<!-- END generated -->` in the files listed in `GENERATED_DOCS` (README and AGENTS by default). `tests/test_generated_docs.py` fails when a block differs from what `headline.json` renders to, so a hand edit or a forgotten audit run fails CI, and the refresh PR carries the updated blocks.

To quote a number elsewhere (a methodology page, a data card, a manuscript), add the file to `GENERATED_DOCS` and give it the same markers, or add a key to `headline_numbers()` and a line to `render_generated()`. A number that can't be generated (a figure from a partner's report) is cited with its source and date beside it. Hand-typed counts drifted in four of nine projects reviewed; generated ones stayed current.

## Storage budget

Decide per source, during section 2, where the originals live, and record it in the decision-log:

| Originals | Where | How |
| --- | --- | --- |
| Small text and tabular files (the usual case) | committed to git | nothing to do |
| Large binaries (PDF volumes, scans, archives) or many of them | Git LFS | uncomment the patterns in `.gitattributes`; `git lfs install` once per machine; LFS bandwidth is metered and LFS files can't be served by GitHub Pages (see `publishing.md`) |
| Too large or too many for LFS, or restricted from redistribution | outside git | uncomment the source's lines in `.gitignore`; the committed `manifest.json` keeps each file's URL and sha256, and `fetch` re-downloads and verifies them; keep a copy in durable storage (an institutional drive, a release asset, a deposit) when the source could disappear |

The processed CSV is committed by default and the Parquet and SQLite copies are rebuilt from it. CI's storage-budget step fails on any committed file over 95 MiB, short of GitHub's 100 MB hard limit, because a file over the limit can't be pushed and removing it means rewriting history. When the processed data is too large to commit, the committed audit reports and `headline.json` are the shared record, and regenerating must reproduce them.

## CI workflows

- **`tests.yml`** *(core, on):* `uv sync`, ruff check and format, mypy (advisory), pytest, `pipeline --help` and `run --help`, and the storage-budget check. Python 3.13 via `astral-sh/setup-uv@v7`; `actions/checkout@v7` without LFS, since tests use committed fixtures.
- **`refresh.yml.disabled`** *(refresh):* rename to enable once the pipeline runs cleanly by hand. On a schedule it runs `pipeline run` and opens a pull request with `peter-evans/create-pull-request@v8` whose diff holds the data, `manifest.json`, `data/audit/*.md`, `headline.json`, `docs/variables.*` and the regenerated README and AGENTS blocks, plus a review checklist. A failed stage fails the job, so no PR opens on bad data. See `pipeline.md` for cadence and ephemeral sources.
- **`publish.yml.disabled`** and **`gh-pages.yml.disabled`** *(publish):* deploy Datasette and render the Quarto site after a merge; see `publishing.md`.

## The `data/` directories

- **`data/original/`:** immutable. `<source>/<vintage>/<file>`, written only by `fetch.py`, plus `manifest.json`. Line endings are never normalized (`.gitattributes` marks the tree `-text`), so hashes keep matching.
- **`data/processed/`:** the deliverable: `<pkg_name>.csv` (and `.parquet`) and `provenance.csv`.
- **`data/audit/`:** generated. Committed: `summary.md`, `headline.json`, `reconcile.md`, `discovery.md`. Ignored, rewritten every run: `extraction_errors.json`, `fetch_errors.json`, `rejected.csv` (it can hold personal data, and its counts are in the summary), `run.json` (timestamps and the ledger), `reconcile.json`.
- **`data/lookups/`:** hand-kept tables: `vocab_<column>.csv` vocabularies (tested against the dictionary), crosswalks such as FIPS codes, entity seeds (a reference list of the stations, offices or facilities the data describes, regenerated by a small script from the publisher's own listing and committed, so joins and referential checks have a fixed target), and `concepts.yaml` once there are two sources.

## Adding a second source

Single-source is the default because building a source registry, an abstract base class and dynamic dispatch on day one produced abstraction that projects later paid to remove. The cheap seams (`data/original/<source>/`, the `source` column, per-era parser modules) are there from the start; the machinery arrives in the same change as the second source:

1. **Probe the new source** as you did the first: real files from every era, and the unit of observation it actually reports. Record the findings in the decision-log.
2. **Move the source code:** `scripts/source.py` becomes `scripts/sources/<first_slug>.py`; write `scripts/sources/<second_slug>.py` with the same two functions; move `SOURCE_SLUG`, `SOURCE_LABEL` and `SOURCE_LICENSE` into each module.
3. **Add the registry** in `scripts/sources/__init__.py`: `SOURCES = {"first_slug": first, "second_slug": second}` (modules, imported explicitly), and make `fetch.py`, `clean.py` and `discover.py` loop over it, passing each module's `artifacts()` and `parser_for`. `clean.build` already accepts both as arguments.
4. **Generate the `multi-source` group:** `scripts/concepts.py`, `data/lookups/concepts.yaml`, `tests/test_concepts.py`, and turn on the `MULTI_SOURCE` blocks. Add a nullable `concept` column to `LONG_COLUMNS` and the schema, and fill it in `clean` with `concept_for(source, vintage, variable)`. Each concept that maps more than one source carries caveats (`data-modeling.md`, "Concept catalogs").
5. **Reconcile across sources at their finest shared grain**, and document scope differences as caveats rather than forcing agreement.
6. Update the dictionary (the `source` vocabulary, new columns, caveats), add a `CHANGELOG.md` entry, and record the change in the decision-log.

A third or fourth source is then a module and a registry entry. When several sources become separate pipelines in one repository (`pipelines/<name>/`, each shaped like this template, with shared plumbing in `pipelines/_core/`), follow the data-project skill's `multi-pipeline.md`.

## Governance

Governance decisions are shared with the data-project skill: [`_shared/governance.md`](_shared/governance.md) covers license inheritance, data subjects, correction and remedy paths, project-internal governance and where each decision lands, and [`_shared/values-and-gates.md`](_shared/values-and-gates.md) has the hard gates (the privacy-law screen and the CARE check) that can mean *do not publish, or publish differently*. In this template they land as follows: the source's license in `SOURCE_LICENSE` and `provenance.csv`, the project's licenses and disavowed uses in the README, PII decisions in the parser or publish code and the dictionary's per-column caveats, the correction path in the README, `CHANGELOG.md` and (when publishing) the *Data correction* issue form, and schema and refresh-review rules in AGENTS. A solo project says so plainly; review rules such as "maintainers approve by PR" ship only with the branch protection that enforces them.

## Architectural principles

The vocabulary is borrowed from [GROBID's design principles](https://grobid.readthedocs.io/en/latest/Principles/); each names a stance this template already takes.

- **A cascade of specialized stages, not a monolithic extractor.** Per-era parsers, then the cleaning steps in `pipeline.md`, then validation and publication. Diagnosis by stage is what the cascade buys.
- **Work with layout, not raw text.** Keep positions, rulings, page numbers and selectors where the source's visual structure carries meaning; throwing layout away to recover plain text first is the failure mode.
- **Small, real fixtures beat large synthetic ones.** One hand-picked fixture per era with an assertion against its printed total catches regressions that ten times the synthetic volume misses.
- **Evaluate on the real distribution.** `reconcile.py` re-reads the original, independently of the parser's path through it, and each refresh is checked against the source as it is now.
- **Default fast, opt into precision.** Text layer first (PDFium via `pypdfium2`), then table tools, then OCR, layout models or vision models for the pages that need them, each with a parser manifest (see the `extract-*.md` references).

## Conventions worth defending

- **`scripts/`, not `src/` or `pipeline/`,** and one command: `python -m scripts.pipeline run`. Predictability across projects is the point. Notebooks, when a project wants them, are thin drivers over `scripts/`, with outputs stripped by `nbstripout`.
- **Immutable originals.** `data/original/` is written only by `fetch.py`; re-fetching is explicit (`--fresh`) and every change of bytes is recorded in the manifest.
- **Probe the live source before writing a parser.** A description of the source (a paper, a notebook, an older pipeline) describes it as it was; one download per claimed era is cheaper than one parser per claimed era.
- **One source until there are two.** The registry arrives with the second source.
- **Per-era parsers, not nested conditionals.**
- **Per-extract provenance, not per-row.** `provenance.csv` has one row per artifact and parser run; data rows carry only `source` and `vintage` (plus a `page` or selector where values must trace to a region).
- **Fail loudly.** Empty and degenerate output is an error, rows lost between stages fail the build, and the error log starts fresh every run.
- **Generated numbers, never typed ones.**
- **AGENTS.md before code.** Someone new should be able to read it and add a parser without reading the codebase; if it is stale, the architecture is undocumented.

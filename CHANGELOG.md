# Changelog

Changes to the skills in this repository, recorded per skill. The format follows [Keep a Changelog](https://keepachangelog.com/); each skill follows semantic versioning on its own line and is tagged `<skill>--v<version>`.

Pre-monorepo history: [`data-project`](history/data-project/CHANGELOG.md) (through 0.10.0) and [`data-liberation`](history/data-liberation/CHANGELOG.md) (through 0.4.0).

## Repository

### [Unreleased]

#### Added
- **One repository for both skills** (`skills/data-project/`, `skills/data-liberation/`), with `data-liberation`'s history imported from `CUPIDS-Lab/data-liberation-skill`. Repository files (CI, evals, changelog, retros) live at the root so installs stay clean.
- **The Outline** (`OUTLINE.md`, source `shared/OUTLINE.md`): ten sections, each with an outcome and a "done when" test, replacing both skills' L0–L5 ladders. `shared/outline.yaml` maps every reference and template to the section that owns it.
- **`shared/`** content vendored into both skills by `tools/vendor.py`, with a CI drift check.
- **`tools/validate.py`**, the single CI gate: layout, Agent Skills spec (also via the official `agentskills validate`), links, section ownership, vendoring, both skills' template validators, and a per-skill version-bump check on pull requests.
- **Feedback intake:** a sprint-feedback issue form keyed to the Outline's sections, a bug form, labels (`skill:*`, `section:*`, `cause:*`, `severity:*`, `status:*`), and a workflow that labels issues from their form answers. `CONTRIBUTING.md` documents triage.
- **Evals** for both skills under `evals/` (behavior cases and trigger queries, including near-misses between the two skills).
- **Releases:** `release.yml` builds an upload-ready zip per skill on `<skill>--v*` tags and attaches it to the GitHub release; `tools/build_zips.py` builds them locally.

## data-project

### [0.11.0] — Unreleased

#### Changed
- **Outline instead of levels.** `SKILL.md` is a router over the Outline's sections, with the hard rules first. Projects start with five working files (README, AGENTS.md + `CLAUDE.md`, ROADMAP, decision-log, CHANGELOG); every other artifact is generated only when its section is in scope. ROADMAP tracks the ten sections as now/later/skip.
- **Agents became procedures.** `references/procedures/` holds `scope.md` (from the interviewer), `scaffold.md`, `tracking.md` (from the tracker), `deposit.md` (from the depositor) and `audit.md`. The indexer and synthesizer are removed; they only selected artifacts by level.
- **Visibility and honest governance.** Scoping decides private, embargoed or public. Review gates ship only with a branch-protection step, and solo projects get a single-steward variant (`SOLO` flag).
- **One project shape.** Pipelines use `data-liberation`'s template (uv, `pyproject.toml`, `scripts/`); Snakemake is an optional wrapper. Multi-pipeline CI discovers `pipelines/*/pyproject.toml` (it previously looked for a `Snakefile` no pipeline had, so nothing was tested). `references/multi-pipeline.md` replaces the landing and stamping references.
- **Deposit kit:** finds the project root correctly (it previously looked for `data/processed` inside `dataverse/`), maps `scripts/` and `docs/data-dictionary.md`, and versions refreshes as major the first time and minor after.
- **Consolidated references.** The values spine, responsible data, governance, FAIR and standards, quality and bulletproofing, and the nine practice digests moved to shared references (substance kept). Tokens `LEVEL`, `ROADMAP_ROWS`, `TRACKING_ROWS`, `MILESTONE_TITLE` and flags `NESTED_SKILLS`, `WIKI`, `WHY` are removed; `DATE`, `SKILL_VERSION`, `VISIBILITY` and `SOLO` are added.
- Frontmatter fits the Agent Skills spec (the `argument-hint` key, rejected by claude.ai uploads, is removed) and the description no longer competes with `data-liberation` for "data dictionary."

#### Removed
- `references/INDEX.md`, `references/escalation-levels.md`, `agents/`, nested-skill templates, wiki seeds, `NEXT-STEPS`, `LICENSE-NOTE`, `environment.yml`, and the separate Python `pyproject.toml` template. Two checklists and two canvases were merged into `pre-release-checklist` and `scope-canvas`.

## data-liberation

### [0.5.0] — Unreleased

#### Changed
- **Outline instead of levels.** `SKILL.md` is a router with non-negotiables first; a one-off extraction still generates nothing but the data. The description fits the spec's 1,024-character limit (it was 1,237).
- **Single-source by default.** The source registry and concept catalog arrive with the second source, not on day one.
- **Lessons from real projects:** probe the live source before writing parsers, a fresh per-run error log, `--fresh` refetch, deduplication before validation, a row-count conservation check at every stage, loud failure on empty output (never substituting synthetic data), samples on stable keys, lookup-vocabulary tests, a storage budget with a CI file-size check, generated numbers in docs with a staleness test, and reconciliation at the finest shared grain.
- **Extraction guidance rewritten** for 2026: PDFium-first for born-digital PDFs, tested trust of embedded OCR layers, a dated comparison of OCR, layout and vision-model parsers and hosted APIs with benchmark caveats, parser manifests and audit sampling for model-based extraction, hosted-OCR cost and agreement guardrails, and the sensitivity gate before any upload. New `extract-api.md` (REST APIs, BI dashboards, ArcGIS layers) and an ephemeral-sources section in `extract-web.md`.
- **Provenance vocabulary:** `extraction_method` and `extraction_quality` are separate columns, one row per extract, deterministic.
- **Template:** `PROJECT_SLUG` is now kebab-case and `PKG_NAME` (new) is snake_case; Python ≥ 3.12 with CI on 3.13; pandera ≥ 0.24; current GitHub Actions; publishing files generated only when publishing is in scope (file groups in `references/project-template.md`); a data-correction issue form and a real reject file; `.gitignore`, the refresh workflow and the docs agree on which audit files are committed.
- `references/context.md` split into `lineage-and-landscape.md` and the shared values and standards references.

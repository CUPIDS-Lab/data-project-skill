---
type: Reference
title: Multi-pipeline repositories
description: How one repository hosts several data-liberation-shaped pipelines under pipelines/<name>/, when and how to factor shared plumbing into a pipelines/_core/ package, how CI discovers every pipeline by its pyproject.toml, and the ordered procedure for landing a new pipeline so the repository never undercounts itself.
tags: [pipelines, monorepo, shared-core, ci, section-5, landing]
---

# Multi-pipeline repositories

Read this when one repository holds, or is about to hold, more than one pipeline: several sources with different owners, cadences or failure modes that are worth building and testing separately. It belongs to Outline section 5 (Pipeline & audit).

## Contents

- [Do you need this?](#do-you-need-this)
- [Layout](#layout)
- [CI discovers pipelines by pyproject.toml](#ci-discovers-pipelines-by-pyprojecttoml)
- [The shared core](#the-shared-core)
- [Landing a pipeline](#landing-a-pipeline)
- [Keeping the repository's account of itself true](#keeping-the-repositorys-account-of-itself-true)

## Do you need this?

Usually not at first. A `data-liberation` project handles several sources in one pipeline: a second source is a new parser module, and the source registry and cross-source concepts arrive with the second source. Split into separate pipelines when the sources are genuinely independent, for example different domains, owners, refresh schedules or dependency stacks, or when one source's failures should not block the others. When a single-pipeline project grows its second independent pipeline, move the first into `pipelines/<name>/` in the same change that adds the second.

## Layout

```
<repo>/
├── README.md  AGENTS.md  CLAUDE.md  ROADMAP.md  decision-log.md  CHANGELOG.md   # repository-wide working files
├── docs/governance/ …                                  # governance covers the whole repository
├── .github/workflows/pipelines-ci.yml                  # discovers pipelines/*/pyproject.toml
└── pipelines/
    ├── _core/                                          # shared package (optional; see below)
    │   ├── pyproject.toml                              # e.g. name = "<project>-core"
    │   ├── src/<pkg>_core/
    │   └── tests/
    ├── <name-a>/                                       # one data-liberation project each
    │   ├── pyproject.toml  uv.lock  README.md  AGENTS.md
    │   ├── scripts/  tests/
    │   ├── data/{original,processed,audit,lookups}/
    │   └── docs/data-dictionary.md
    └── <name-b>/ …
```

Each `pipelines/<name>/` is a complete project rendered from `data-liberation`'s project template: it installs with `uv sync`, tests with `uv run pytest`, and runs with `uv run python -m scripts.pipeline run` from its own directory. Its `AGENTS.md` covers that pipeline only and points up to the root `AGENTS.md` for repository rules. Cross-pipeline harmonization (shared concepts, crosswalks used by more than one pipeline) lives in `pipelines/_core/` lookups or a root `data/lookups/`, decided once and recorded in the decision-log.

## CI discovers pipelines by pyproject.toml

`templates/ci/pipelines-ci.yml.tmpl` (rendered to `.github/workflows/pipelines-ci.yml`) has a `discover` job that lists every `pipelines/*/pyproject.toml`, and a `test` job that fans out over the result, running `uv sync` and `uv run pytest` in each pipeline directory on Python 3.13. Adding a pipeline needs no workflow edit. The underscore-prefixed `_core/` is tested by its own job and excluded from the pipeline matrix.

The discovery key is `pyproject.toml` because that is what every data-liberation pipeline has. Never key discovery on an optional file such as a `Snakefile`: a pipeline without one is then silently untested. The workflow also fails when a directory under `pipelines/` lacks `pyproject.toml`, so a half-landed pipeline is caught instead of skipped.

A pipeline's own `.github/workflows/tests.yml` from the template does nothing inside `pipelines/<name>/` (GitHub only reads the root `.github/`); delete it when landing the pipeline.

## The shared core

- **One or two pipelines:** don't abstract. Let the second copy from the first; you don't yet know which parts are common.
- **About three:** the common shape is visible. Factor domain-agnostic plumbing into `pipelines/_core/` before the fourth multiplies the copies.
- **Four or more:** each new pipeline is a thin domain layer over the core.

Split on whether a fix would have to be made identically everywhere:

| `pipelines/_core/` (shared) | `pipelines/<name>/` (per pipeline) |
| --- | --- |
| provenance recording, hashing, the original-file manifest | the source list, URLs, access notes |
| the fetch engine (HTTP, retry, caching, rate limits, `--fresh` refetch) | per-source parsers |
| the long-format shaper and dedup-before-validate step | entity lists, schema vocabulary, units |
| a fresh per-run error log; progress reporting | this source's reconciliation totals and known issues |
| CLI skeleton, logging, config loading, shared validators | `scripts/pipeline.py` wiring for this source |

Each pipeline depends on the core as a path dependency in its `pyproject.toml`, for example `[tool.uv.sources] <project>-core = { path = "../_core", editable = true }` with `<project>-core` in `dependencies`. Keep the core versioned and tested; a careless change to it can break every pipeline at once, which is the price of fixing things once. Record the decision to create the core in the decision-log.

## Landing a pipeline

Land every pipeline the same way, in this order, so `main` stays green and the history stays readable:

1. **Isolate.** Work on a branch in its own git worktree (`git worktree add ../wt-<name> -b add-<name>-pipeline origin/<default-branch>` after a `git fetch`). Concurrent agents never share a checkout, and stage explicit paths, never `git add -A`.
2. **Scaffold** `pipelines/<name>/` from `data-liberation`'s project template. Once a core exists, copy a sibling's thin shell (its `pyproject.toml`, `scripts/pipeline.py`, `README.md`, `AGENTS.md`), rename the domain parts, and import the plumbing from the core rather than copying it.
3. **Test it from its own directory:** `cd pipelines/<name> && uv sync && uv run pytest`. CI will discover it from its `pyproject.toml`.
4. **Register it** in the repository's documents (next section) and add the hidden marker `<!-- data-project:pipeline=<name> -->` next to each mention.
5. **Deposit kit,** if the project deposits: make sure the deposit's Code and Data folders include the new pipeline.
6. **One PR, one concern:** title it `Add <name> pipeline (#NN)`, put `Closes #NN` in the body, and include nothing else (no unrelated docs or governance changes).
7. **Merge when CI is green,** then `git fetch` and confirm you are level with `origin/<default-branch>` before landing the next pipeline or running an audit.

## Keeping the repository's account of itself true

A multi-pipeline repository describes its pipelines in several places, and those descriptions drift ("the README says three, the directory has four"). Keep the number of places small and checkable:

- The README carries the one pipeline table. Other documents link to it instead of restating the list.
- `ROADMAP.md` tracks the work, the CHANGELOG records the landing, and the decision-log records any source caveat.
- Generate the table, or test it: a CI step that compares the README's pipeline table with `pipelines/*/pyproject.toml` turns drift into a failing check.
- On every tracking sync (`procedures/tracking.md`), compare the markers and pipeline issues with the directories on the default branch and report both kinds of drift for a human to fix.

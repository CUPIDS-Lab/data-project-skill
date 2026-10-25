---
type: Reference
title: Cookiecutter Data Science
description: Opinionated, standardized-but-flexible project structure for doing and sharing data-science work.
resource: https://cookiecutter-data-science.drivendata.org/
tags: [structure, reproducible, documented]
---

# Cookiecutter Data Science

A logical, reasonably standardized but flexible project structure for doing and sharing data science work. Source: https://cookiecutter-data-science.drivendata.org/

## In one paragraph

Cookiecutter Data Science (CCDS) is a conventional directory layout plus a short set of opinions about how analysis projects should be organized so that anyone can clone the repo and find their way around. Its core claim is that consistency and a few firm rules (raw data is immutable; data is not in version control; notebooks explore while source code reproduces) buy you reproducibility and shareability cheaply.

## Key practices (sampleable units)

- **Standard directory tree** [reproducible, documented] — `data/{raw,interim,processed,external}`, `notebooks/`, `<module>/` source package, `reports/figures/`, `references/`, `models/`, `docs/`. Predictable layout means low onboarding cost.
- **Treat the analysis as a DAG** [reproducible] — outputs trace back to inputs through versioned steps; you can recreate any product from raw.
- **Raw data is immutable** [reproducible, transparent] — never edit raw in place; read it, copy to `interim`/`processed`. Originals can always regenerate derived data.
- **Data is excluded from version control** [reproducible] — `.gitignore` blocks `data/`; large data lives in object storage or Git LFS, not the repo.
- **Notebooks explore, source code reproduces** [reproducible, documented] — refactor reusable logic out of notebooks into a tested, importable package; notebooks are numbered and exploratory.
- **Environment reproducibility** [reproducible] — pin dependencies (conda/`environment.yml` or `requirements.txt`); consider containers for complex needs.
- **Secrets in `.env`, never in code** [transparent] — load via `python-dotenv`; `.env` is git-ignored.

## Artifacts it implies

- The canonical layout → `templates/directory-tree.md`.
- Data-aware ignore rules → `templates/gitignore.tmpl`.
- Pinned environment → `templates/python/environment.yml.tmpl`, `templates/python/pyproject.toml.tmpl`.
- Numbered exploratory notebooks → `exploratory/` in the tree.

## When most relevant

Any Python-leaning project; the default structural backbone for L0–L2. Strong signal when the user says "set up a repo," "project structure," or "make this shareable."

## Caveats / conflicts

CCDS prescribes a fairly fixed tree; The Turing Way emphasizes flexibility. Resolve by treating the tree as a sensible default to prune/extend per project, not a mandate. CCDS is Python/notebook-centric; for R projects prefer the OUHSC layout.

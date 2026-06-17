---
type: Reference
title: OUHSC BBMC Data Science Practices
description: Concrete, battle-tested conventions for repo structure, file/variable naming, coding style, data handling, sensitive-data separation, and team collaboration norms.
resource: https://ouhscbbmc.github.io/data-science-practices-1/
tags: [structure, naming, coding, sensitive-data, collaboration, documented]
---

# OUHSC BBMC Data Science Practices

A detailed, opinionated practices guide from the OUHSC Biomedical & Behavioral Methodology Core, strong on naming, coding discipline, sensitive-data handling, and team norms (R/SQL-leaning but language-agnostic in spirit). Source: https://ouhscbbmc.github.io/data-science-practices-1/

## In one paragraph

OUHSC encodes how a careful research-data team actually works day to day: a public/unshared data split that prevents leakage, exact naming conventions that make joins and reviews legible, a linear file structure that keeps scripts predictable, defensive validation as you go, and review/collaboration norms that catch problems early. It is the best source for the *concrete* conventions the other frameworks gesture at.

## Key practices (sampleable units)

- **Public vs. unshared data separation** [transparent, inclusive, reproducible] — `data-public/` for non-sensitive and `data-unshared/` for sensitive/local-only data, with a committed `contents.md` manifest (commit the manifest, never the sensitive data). Prevents accidental leakage.
- **Stable naming conventions** [documented, collaborative] — snake_case variables; kebab-case files; dataset prefixes (`ds_` file-scope, `d_` function-local) that express the grain (`ds_pt_visit`); ISO-8601 dates; repo names as `[pi]-[topic]-[index]`.
- **Linear, predictable script structure** [reproducible, documented] — clear-memory → load sources → load packages → declare globals → load data → tweak → analyze → verify → select outputs → save; a single orchestration file (`flow.R`) runs the stages.
- **Defensive validation as you go** [transparent, reproducible] — assertions on types/ranges/keys (e.g. `checkmate`); document constraints to future readers; error/warning thresholds prevent silent failures.
- **Data dictionaries with grain, sources, constraints** [documented] — per-table: grain, provenance, each variable's type/description/constraints/units.
- **Collaboration norms** [collaborative, inclusive] — daily PR review; read the diff before committing; announce breaking changes via issues; run downstream dependencies before committing shared files; document workstation setup for fast onboarding.

## Artifacts it implies

- Naming/grain + provenance → `templates/data-dictionary.md.tmpl`.
- Public/unshared split → `templates/directory-tree.md` and `templates/gitignore.tmpl`.
- Orchestration file → `templates/python/Snakefile.tmpl` (Python) / `_targets.R` (R, roadmap).
- Review/onboarding norms → `templates/CONTRIBUTING.md.tmpl` (roadmap).

## When most relevant

Sensitive or human-subjects data; R-leaning teams; any project that needs concrete naming/coding conventions. Strong signal on "sensitive," "PII," "naming," "data dictionary," "team norms."

## Caveats / conflicts

R/SQL idioms need translation for Python projects (the principles transfer; the syntax does not). The full convention set can feel heavy for a one-off analysis — pull only the conventions the project needs.

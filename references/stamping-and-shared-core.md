---
type: Reference
title: Stamping Siblings and the Shared Core
description: When a monorepo crosses ~3 pipelines, where shared plumbing should live (a shared core package) versus what stays domain-specific per pipeline, and how to "stamp" a new sibling pipeline from the pattern instead of copy-pasting the whole thing.
tags: [reproducible, documented, monorepo, pipelines, refactoring, shared-code]
---

# Stamping Siblings and the Shared Core

`references/context.md` states the rule — *"shared code belongs in `src/<pkg>/`"* — but a rule without a
mechanism loses to the path of least resistance, which is copy-paste. When the second pipeline is stamped
from the first by duplicating its whole directory, and the third from the second, the repo ends up with N
near-identical copies of the same fetch/clean/provenance plumbing, and a one-line fix to that plumbing
becomes an N-place edit nobody makes consistently. This digest says *what* to share and *when*, so siblings
are stamped from a thin pattern over a shared core rather than cloned wholesale.

## The threshold

- **1–2 pipelines:** don't pre-abstract. Let the second pipeline copy from the first; duplication is cheaper
  than the wrong abstraction this early, and you don't yet know which parts are truly common.
- **~3 pipelines:** the inflection point. Once a third sibling needs the same plumbing, the common shape is
  visible and real — factor it into a **shared core** now, before the fourth multiplies the copy.
- **4+:** every new pipeline should be a thin domain layer over the core; copy-paste of core plumbing at
  this point is debt, not speed.

## What is shared vs. what is per-pipeline

Split on **domain-agnostic plumbing** (shared) vs. **domain logic** (per-pipeline):

| Shared core (factor out at ~3) | Per pipeline (stays in `pipelines/<name>/`) |
| --- | --- |
| provenance / chain-of-custody recording | the source list, URLs, credentials-of-record |
| the fetch engine (HTTP, retry, caching, rate-limit) | per-source parsers / extractors |
| clean / normalize orchestration (the `normalize_long` long-format shaper) | station/entity lists, schema vocabulary, units |
| the CLI skeleton / entrypoint scaffold | this source's `config.yaml` values |
| shared validation and bulletproofing helpers | this source's known-issues and reconciliation totals |
| logging, config loading, common types | the `Snakefile` DAG wiring for this source |

The test is simple: *if a fix to this code would need to be made identically in every pipeline, it belongs
in the core.* If it encodes how one specific source behaves, it stays local.

## Where the core lives

Two shapes, both consistent with the canonical tree:

- **Repo-wide package — `src/<pkg>/`** (default; `references/context.md`, `templates/directory-tree.md`).
  Importable, tested, installed with `pip install -e .`; pipelines `import <pkg>` and call into it. Prefer
  this when the core is genuinely project-wide.
- **`pipelines/_core/`** — a sibling "pipeline-shaped" shared package living alongside the others, when you
  want the shared code to sit inside the `pipelines/` tree next to its consumers. (Underscore-prefixed so
  the CI discovery glob, which keys on `pipelines/*/Snakefile`, never mistakes it for a runnable pipeline.)

Pick one and state it in `decision-log.md`; don't run both.

## Stamping a sibling

To add pipeline `<new>` once a shared core exists:

1. **Copy the thin shell, not the plumbing.** Start from a sibling's `pipelines/<name>/` but keep only the
   per-pipeline files (`Snakefile`, `config.yaml`, `environment.yml`, `README.md`) and the domain modules.
2. **Rename, don't fork.** Rename the source list, parsers, station/schema vocab for `<new>`; delete any
   plumbing that the core already provides and replace it with imports from the core.
3. **Honor the contract.** Each pipeline exposes the same small contract the core expects — typically a
   fetch step, a clean/normalize step producing the shared long format, and tidy output under
   `data/processed/`. Keep the entrypoint and output shape identical across siblings so the core and CI
   treat every pipeline the same.
4. **Land it** via the ordered procedure in `references/landing-a-pipeline.md`.

## Trade-off (name it, don't bury it)

A shared core trades **per-pipeline independence** for **single-point maintenance**: one fix propagates to
every pipeline, but a careless change to the core can break all of them at once, and a pipeline can no
longer quietly diverge. That trade is worth it at ~3+ siblings and premature below it. Pin the core's own
version, test it, and let pipelines depend on it like any other dependency — coupling you chose and can see
beats coupling you got by accident through copy-paste.

## When most relevant

A monorepo (`PIPELINES`) heading past two pipelines, or any repo where you notice the same plumbing being
pasted into a new `pipelines/<name>/`. Below ~3 pipelines, point the user back at "don't pre-abstract."

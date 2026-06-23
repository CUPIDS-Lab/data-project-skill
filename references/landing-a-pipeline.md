---
type: Reference
title: Landing a Pipeline in a Multi-Pipeline Monorepo
description: The ordered, repeatable procedure for adding one self-contained data-liberation pipeline to a data-project monorepo — isolated worktree, scaffold, auto-discovered CI, repo-doc registration, single issue-closing PR — so every pipeline lands the same way instead of being improvised N different times.
tags: [collaborative, reproducible, documented, monorepo, pipelines, landing, ci]
---

# Landing a Pipeline (multi-pipeline monorepo)

A `data-project` repo is, in practice, a **monorepo of pipelines**: one self-contained `data-liberation`
pipeline per liberated source under `pipelines/<name>/`, each mapped 1:1 to a tracked issue (see
`references/context.md` and `templates/directory-tree.md`). The skill models how to *build* a pipeline and
how to *track* the work; this digest models the third verb — how to **land** one. Without a single
procedure, the second, third, and fourth pipelines each get added a slightly different way: a CI matrix
row merged before the directory it names (red `main`), a pipeline bundled into an unrelated governance PR,
a repo whose docs advertise three pipelines while `pipelines/` holds four. Land every pipeline the same
way and those frictions disappear.

## The per-pipeline file set (self-contained)

Each `pipelines/<name>/` is self-contained so CI can discover and build it in isolation:

- `Snakefile` — this pipeline's own DAG (the **discovery marker** CI keys on; R variant: `_targets.R`).
- `config.yaml` — its parameters and paths.
- `environment.yml` — its pinned environment (or point CI at a shared root env; see below).
- `README.md` — what it liberates, its sources, and its tidy output.
- tidy output under `data/processed/` (domain logic — sources, parsers, station lists, schema vocab —
  lives here; domain-agnostic plumbing belongs in the shared core, see `references/stamping-and-shared-core.md`).

## The landing sequence (ordered)

Do these in order; the order is what keeps `main` green and the history legible.

1. **Isolate.** Work in a dedicated **git worktree / branch** for this pipeline so a shared checkout is
   never the staging area for concurrent agents (see the worktree-isolation guidance in
   `references/github.md`). `git fetch` and branch from an up-to-date `origin/<default-branch>`.
2. **Scaffold** `pipelines/<name>/` with the per-pipeline file set above (stamp it from a sibling per
   `references/stamping-and-shared-core.md` once the repo has a shared core).
3. **Wire CI in the same change.** The monorepo workflow (`templates/ci/pipelines-ci.yml.tmpl`)
   **auto-discovers** `pipelines/*/Snakefile`, so a new directory needs **no** workflow edit. If the repo
   instead pins a **static matrix**, add the pipeline's matrix row **in the same PR** as its directory —
   never land a matrix row before the code it points at.
4. **Register** the pipeline across the repo docs (the checklist below) and drop the pipeline marker.
5. **Deposit kit** (only if the project deposits): add/refresh the `dataverse/` entry for this pipeline's
   processed data; the scheduled re-deposit workflow rebuilds every pipeline before depositing.
6. **One PR, one concern.** Open a single PR titled `Add <name> pipeline (#NN)` that carries the directory,
   the registration edits, and (if static) the matrix row — and **nothing else**. Put `Closes #NN` in the
   body so merging closes the tracked issue (see Track mode + `references/github.md`). Never fold a pipeline
   into a docs-only or governance PR.
7. **Green, then merge.** Let the auto-discovered CI build the new pipeline; merge only when it is green.
8. **Resync.** After merge, `git fetch` and verify `origin/<default-branch>` locally before the next
   pipeline or any audit — a stale checkout produces false "missing pipeline" findings.

## Registration checklist (a pipeline is a projection across surfaces)

"Registering" a finished pipeline means updating every surface that should know it exists. Treat this as a
projection of one fact ("`<name>` is built and landed") onto the repo, the same way GitHub issues are a
projection of `ROADMAP.md`. Update (or verifiably account for) each surface, and drop the marker so the
tracker can reconcile:

- `README.md` — pipeline list / table.
- `ROADMAP.md` — move the pipeline's row from deferred/now to done; check its tracking box.
- `CHANGELOG.md` — an entry for the landed pipeline.
- `AGENTS.md` — if the pipeline changes how an agent runs the repo.
- `decision-log.md` — the dated decision and any source caveats.
- `docs/governance/data-management-plan.md` and the dataset `docs/data-card.md` (L4+) — the new source's storage/retention and provenance.
- the GitHub **wiki** (L4, if enabled) — narrative/how-to.
- both CI workflows — the test workflow (auto or static row) and, if depositing, the scheduled re-deposit.
- `.github/engagement-sync.json` — the tracker keeps the task↔issue map; landing closes the issue.

**Marker convention.** Drop a hidden `<!-- data-project:pipeline=<name> -->` HTML comment into the
registration surfaces (parallel to the existing `<!-- data-project:task=<id> -->` issue marker). It is
invisible in rendered Markdown and lets `data-project-tracker` reconcile what the docs claim against what
`pipelines/` actually contains — flagging the "docs say three, disk has four" drift.

## When most relevant

Any repo that has, or is about to have, **more than one** `pipelines/<name>/` (the `PIPELINES` profile
flag). A genuinely single-pipeline project keeps `Snakefile`/`config.yaml` at the repo root and never needs
this — don't impose the monorepo seam on a one-source project.

## Caveats

The auto-discovered matrix is the lean default; the static fallback exists only for harnesses that forbid
dynamic matrices. Keep the per-pipeline file set minimal — shared plumbing is factored into the core, not
copied into every pipeline (`references/stamping-and-shared-core.md`). The registration checklist is a
checklist, not a generator: the tracker *reconciles and flags*, it does not silently rewrite nine docs.

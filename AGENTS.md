# AGENTS.md — using this skill from any harness

This repository is a portable **Agent Skill**. Its entry point is `SKILL.md` at the root; everything else loads on demand. This file describes the skill for an agent harness that is browsing the repo rather than loading `SKILL.md` directly.

## What it does

It scaffolds right-sized, public-interest data-collaboration projects: it interviews the user, samples a bundled best-practice corpus, proposes a plan the user approves, and writes a small set of project files plus a `ROADMAP.md` of deferred work. It optimizes for accessible, documented, transparent, and inclusive collaborative data projects, and it is deliberately lean by default — it builds only what the chosen complexity level needs. At its top rung (L5) it can also publish and share outputs — an OKF knowledge bundle, an ARD agent-discovery catalog, a Harvard Dataverse deposit (citable DOI), and an OpenSharing zero-copy share kit — each gated by the project's governance and sensitivity rules.

## How to run it

Read `SKILL.md` and follow it. The workflow is: **Interview → Sample → Synthesize → Approve → Scaffold (now) + Roadmap (later) → Verify → Offer next rung**, governed by the entry protocol in `references/escalation-levels.md` (infer the lowest level that fits, state the assumption, execute it, offer the next rung).

The first three phases are defined as agent role files in `agents/`:

- `agents/data-project-interviewer.md` — elicits the Project Context Profile.
- `agents/data-project-indexer.md` — samples `references/` into a cited Practice Selection.
- `agents/data-project-synthesizer.md` — proposes a right-sized Synthesis Plan plus a roadmap.

If your harness supports named sub-agents or tasks, dispatch each phase to the matching file. If it does not, read the file and perform that role inline as that phase. The skill (the main thread) is the memory that passes each phase's output to the next.

## Where things are

- `references/` — the on-demand corpus and the `INDEX.md` crosswalk the indexer samples; `context.md` holds the values and the hard gates (privacy law + CARE Principles).
- `templates/` — placeholder-driven scaffolding artifacts; `directory-tree.md` is the structural source of truth.
- `agents/` — role definitions: the three interview→sample→synthesize phases above, plus `data-project-tracker` (GitHub Issues/Project sync, Track mode) and `data-project-depositor` (Dataverse deposit, Deposit mode).

## Non-negotiables

Write generated files only into the user's working directory, never into this skill's directory. Keep L0/L1 lightweight. Prefer a `ROADMAP.md` entry over a generated file when unsure. When data is sensitive-human, regulated, or implicates Indigenous data (CARE), couple every identifier/retention/audit affordance with access tiers and contestable governance — see `references/installed-base.md`.

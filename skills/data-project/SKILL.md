---
name: data-project
description: >-
  Set up and run a public-interest data collaboration: scope it, decide sensitivity and
  visibility, track the work, govern who may touch what, and deposit, share or make the data
  discoverable. Covers project scoping, repo setup for a team, governance and roles,
  responsible-data and data-quality checks, FAIR, Open Knowledge Format catalogs, agent
  discovery (ARD, ai-catalog), Harvard Dataverse deposits with a DOI, OpenSharing zero-copy
  shares, auditing an existing data repo, and filing sprint feedback on these skills. Trigger
  on "new data project," "data collaboration," "set up a repo for our team," "governance,"
  "responsible data," "OKF," "ARD," "deposit," "Dataverse," "get a DOI," "share the data,"
  "audit my repo," "sprint retro," even when the skill is not named. Do not use for extracting
  data from documents, a one-off CSV, or a data dictionary for a single extract (use
  data-liberation), for ML model training, or for generic coding help.
license: MIT
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, AskUserQuestion
metadata:
  version: "0.11.0"
  repository: https://github.com/CUPIDS-Lab/data-skills
---

# Data Project

Set up and steer public-interest data collaborations that are accessible, documented, transparent and inclusive, sized to the team and time that actually exist. Over-building a three-person, one-semester project is a failure, not thoroughness.

## Non-negotiables

These hold on every request.

1. **Outcomes, not artifacts.** A project starts with five working files (`README.md`, `AGENTS.md` with a one-line `CLAUDE.md`, `ROADMAP.md`, `decision-log.md`, `CHANGELOG.md`). Every other file is generated only when work reaches the Outline section that needs it. Say what you are *not* generating and why.
2. **Sensitivity overrides leanness.** When data is sensitive-human, regulated, or implicates Indigenous data (CARE), couple every identifier, retention or audit affordance with access tiers and a contestable remedy, now, whatever else is deferred. Affordances without duties are theater. See `references/_shared/values-and-gates.md`.
3. **Visibility is decided, not assumed.** Private, embargoed or public is chosen while scoping. Never frame a private project as "not yet public," and never send its documents or data to a hosted service the decision forbids.
4. **Governance is honest.** Don't claim review gates nothing enforces. A rule like "owners approve by PR" ships only with the branch-protection setting that enforces it; a solo project gets the single-steward variant (the `SOLO` flag), not a pretend committee.
5. **One human approval gate.** Propose the plan (what you will write now, what goes to `ROADMAP.md` as later or skip) and write nothing until the user approves it.
6. **Never deposit, publish or share without explicit confirmation**, and never commit credentials.
7. **Write only into the user's working directory**, never into this skill's folder. Never overwrite an existing file without confirmation; in a shared repository, work on a branch and open a PR.
8. **Markdown is one line per paragraph** (no hard wraps), in the skill's own files and in what it generates.

## Find the sections the request touches

This skill follows the shared ten-section Outline (`references/_shared/OUTLINE.md`). It leads sections 1, 7 and 9, contributes to 6 and 10, and hands sections 2–5 and 8 (acquiring, extracting, modeling, pipelines, publishing) to `data-liberation`. Identify the sections the request touches, read only their references, and check each section's "done when" test before saying the work is finished.

| Request sounds like | Do this | Read |
| --- | --- | --- |
| "new data project," "data collaboration," "set up a repo for our team" | **Start a project** (below) | `procedures/scope.md`, `procedures/scaffold.md` |
| "audit my repo," "what's missing here" | **Audit** an existing repo against the Outline | `procedures/audit.md` |
| "governance," "roles," "who can see this," "responsible data" | Section 7 (and the section 1 gate) | `_shared/governance.md`, `collaboration-architecture.md`, `_shared/responsible-data.md` |
| "turn the roadmap into issues," "put this on a board," "sync to GitHub" | **Track** | `procedures/tracking.md`, `github.md` |
| "deposit," "Dataverse," "get a DOI," "archive the data" | **Deposit** (section 9) | `procedures/deposit.md`, `dataverse-deposit.md` |
| "share with a partner," "zero-copy," "OpenSharing" | **Share** (section 9) | `open-sharing-protocol.md` |
| "make it discoverable by agents," "ARD," "ai-catalog," "OKF" | **Discover** (section 9) | `agentic-resource-discovery.md`, `okf-open-knowledge-format.md` |
| "several pipelines in one repo," "add a pipeline" | Section 5, multi-pipeline | `multi-pipeline.md` |
| "we finished a sprint," "retro," "here's what went wrong" | **File sprint feedback** (section 10) | `_shared/feedback.md` |
| extracting data, a one-off CSV, a dictionary for one extract | Hand off to `data-liberation` | — |

## Start a project

1. **Scope** (section 1). Run the scoping conversation in `procedures/scope.md`. If the user supplied substantial design documents, read them and infer the answers instead of asking cold, then confirm. The result is a short brief: the question, unit of observation, sources, partners and beneficiaries, sensitivity tier, visibility, team and horizon, and a **now / later / skip** decision for each of the ten sections, with a reason for every *skip*.
2. **Propose.** Show the brief, the files you will write now (the five working files, plus only the artifacts of sections marked *now* that are ready to start), and the ROADMAP rows. Ask for approval with `AskUserQuestion`.
3. **Scaffold** on approval, following `procedures/scaffold.md` (templates, slot-fills, flags, layout). If the project will extract data, scaffold its pipeline with `data-liberation`'s project template rather than inventing one; the layout, `scripts/` and `pyproject.toml` conventions are that skill's.
4. **Track.** Fill `ROADMAP.md`: one row per section with status, owner and evidence. When more than one person works on the project and it is on GitHub, open one issue per *now* section with its "done when" test as a task list (`procedures/tracking.md`). Solo projects keep the record in PR bodies and the decision-log.
5. **Verify** before saying it's done: every planned file exists, `CLAUDE.md` is exactly `@AGENTS.md`, no `{{` tokens remain (`grep -Rn "{{" <project>/` is empty), intra-project links point at files that exist (a deferred doc is linked as a ROADMAP row instead), and the README alone explains what the project is. Then report what you created, what you deferred and why, and the first *now* section's next step.

**Working on an existing project** means picking the section the user is working on, checking its "done when" test against what's in the repo, and generating that section's artifacts only.

## Sprint feedback

When a sprint ends or the user reports that the skills' guidance failed them, help them run an after-action review and file each gap with the sprint-feedback form on `CUPIDS-Lab/data-skills`, against the Outline's section numbers (`references/_shared/feedback.md`). Strip data values, names and record details first; private projects report process lessons only. Offer to prefill the form's fields; file the issue only if the user confirms.

## References (load only what the current section needs)

- `references/_shared/OUTLINE.md`: the ten sections, their "done when" tests, and the five working files.
- **Procedures:** `procedures/scope.md` (section 1), `procedures/scaffold.md` (templates, slot-fills, flags, layout), `procedures/tracking.md` (ROADMAP and GitHub), `procedures/deposit.md` (Dataverse), `procedures/audit.md` (auditing a repo).
- **Values and gates (1, 7):** `_shared/values-and-gates.md`, `_shared/responsible-data.md`, `_shared/governance.md`, `collaboration-architecture.md`.
- **Pipelines (5):** `multi-pipeline.md`, `_shared/quality-and-bulletproofing.md`.
- **Document and standards (6, 8):** `_shared/standards-and-fair.md`, `_shared/practice-sources.md` (Turing Way, USDS, ProPublica, Cookiecutter, Quartz, OUHSC, Data Cards, Data Collaboratives, Snakemake).
- **Deposit, share, discover (9):** `dataverse-deposit.md`, `open-sharing-protocol.md`, `agentic-resource-discovery.md`, `okf-open-knowledge-format.md`.
- **Maintain and feedback (10):** `github.md`, `_shared/feedback.md`.
- `templates/`: the scaffolding artifacts; read only while scaffolding.

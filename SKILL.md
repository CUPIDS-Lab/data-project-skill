---
name: data-project
description: >-
  Scaffold a public-interest data collaboration — repo skeleton, documentation, reproducible pipeline,
  governance/roles, responsible-data & data-quality artifacts, and an Open-Knowledge-Format catalog.
  Works at six escalating levels (L0 a sane repo skeleton → L5 a governed, FAIR, published OKF bundle):
  start low and climb only as far as the task needs; build the essentials now and DOCUMENT the rest in a
  roadmap. Use whenever someone is starting, restructuring, or onboarding collaborators to a data project,
  lab repo, data archive, civic-data effort, or shared-data initiative — even "set up a repo for X data"
  or "help me start a project around this dataset" — or wants to audit an existing repo against open,
  inclusive, reproducible standards. Trigger on "new data project," "set up a repo," "data collaboration,"
  "data dictionary," "governance," "responsible data," "open knowledge," "OKF," "audit my repo," even when
  the skill is not named. Do not trigger for pure ML model training, generic coding help, or raw
  document→data extraction (use the data-liberation skill for that).
argument-hint: "[project name / one-line description, or 'audit <path>']"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, AskUserQuestion
---

# Data Project

Scaffold accessible, documented, transparent, and inclusive collaborative data projects — right-sized to the team and horizon that actually exist. This skill interviews the user, samples best practices from a bundled corpus of frameworks, proposes a plan, and generates only the files the chosen complexity needs, documenting the rest in a `ROADMAP.md`. The goals it serves are accessible, documented, transparent, inclusive, with collaborative and reproducible as enablers. Read `references/context.md` for the why and the values; this body is the how.

## Core stance: lean by default

The corpus and templates are a menu, not a default output. Over-engineering a three-person, one-semester project is a failure mode, not thoroughness. Two dials keep every run small: the **level** (L0–L5, how much to build now) and the **now/later/skip** disposition for each concern above that level (deferred concerns go into `ROADMAP.md`, never silently generated). The one place you override leanness is **sensitivity**: when data is sensitive-human, regulated, or implicates Indigenous data (CARE), couple every identifier/retention/audit affordance with access tiers and contestable governance — affordances without duties are theater (see `references/installed-base.md`).

## Workflow

Elicit before you scaffold; never skip to file generation. Follow the entry protocol from `references/escalation-levels.md`: **Infer** the lowest level that meets the need → **State** the assumption and offer a one-sentence redirect → **Execute** that level fully → **Offer** the next rung on completion. Then run the phases below. If the user's argument is `audit <path>`, jump to Audit mode.

The three phases below are delegated. **If your harness supports named sub-agents or tasks (e.g. Claude Code's Agent tool), invoke the matching file in `agents/`. Otherwise, read `agents/<name>.md` and perform that role inline as this phase.** Pass the previous phase's output block forward — you are the memory between phases.

### Step 1 — Resolve materials

Find this skill's directory; `references/` and `templates/` are siblings of `SKILL.md`. In Claude Code, `${CLAUDE_PLUGIN_ROOT}` points at the skill root. Confirm by listing `references/`. Read templates from here; **write generated files only into the user's working directory.**

### Step 2 — Interview (`data-project-interviewer`)

Produce a **Project Context Profile** (level, collaboratory type, now/later dispositions, data sensitivity and whether contributed, design partners vs. beneficiaries and role gaps, governance posture, maintenance horizon, tooling, openness/license, accessibility, publish-as-OKF). Echo the captured answers and let the user correct before continuing.

### Step 3 — Sample (`data-project-indexer`)

Pass the Profile; get back a cited **Practice Selection** keyed to the six goals, plus what to skip and why, and anything the sensitivity coupling forces regardless of level. The indexer reads `references/INDEX.md`.

### Step 4 — Synthesize (`data-project-synthesizer`)

Pass the Profile + Practice Selection; get back a **Synthesis Plan**: the target tree, the *now* file manifest (`template → output path` for templates that exist, with a placeholder fill-map), the **ROADMAP** of deferred concerns, gated governance/ethics inclusions, the pipeline approach, and open questions. The synthesizer right-sizes and only names templates that exist.

### Step 5 — Approve (single human gate)

Present the Synthesis Plan concisely — the tree, the files to create now, the roadmap items, and the key decisions. Ask for approval or edits with `AskUserQuestion`. Write nothing until approved.

### Step 6 — Scaffold (now) + ROADMAP (later)

On approval, for each file in the manifest: read its template from `templates/…`, substitute `{{TOKENS}}` from the fill-map, include or strip `<!-- IF:FLAG -->…<!-- /IF -->` blocks per the Profile, and write it into the target directory with the `.tmpl` suffix removed. Create directories per `templates/directory-tree.md`, adding `.gitkeep` to empty `data/` dirs and documenting `data/raw` as immutable. Fill `ROADMAP.md`'s `{{ROADMAP_ROWS}}` from the synthesizer's roadmap (one row per deferred concern; mark coupling-forced items **blocking**). At L5, emit the `knowledge/` OKF bundle from the data dictionary (see `references/okf-open-knowledge-format.md`). Adjust any intra-project link inside a template so it points to a file you actually generated — if a referenced doc (e.g. `GOVERNANCE.md`) was deferred, point the reader to `ROADMAP.md` instead, so the scaffold never ships a dangling link. Default to creating a new `./<project-slug>/` unless the user is scaffolding into an existing repo; never overwrite an existing file without confirmation.

### Step 7 — Verify & offer next

Confirm every planned file exists and that no unfilled `{{` tokens remain (`grep -Rn "{{" <project>/` should return nothing). If the user opts in and the toolchain is present, `git init` and run a pipeline dry-run (`snakemake -n`). Print a short "Created N files" summary with next steps (e.g. "fill the data dictionary before ingesting; complete the responsible-data checklist before sharing"), then offer the next rung.

## Placeholders & conditionals

Templates use `{{UPPER_SNAKE}}` tokens and `<!-- IF:FLAG -->…<!-- /IF -->` blocks. Core tokens: `PROJECT_NAME`, `PROJECT_SLUG` (kebab-case), `PKG_NAME` (the slug with hyphens→underscores — a valid Python module/package name), `DESCRIPTION`, `PI_NAME`, `LAB_NAME` (default "CUPIDS Lab"), `YEAR`, `LICENSE`, `LEVEL`, `SENSITIVITY_TIER`, `OPENNESS`, `CONTACT_EMAIL`, `TOOLING`, `REPO_URL`, `RAW_FILE`, `ROADMAP_ROWS`. Conditional flags, set from the Profile: `WHY` (include narrative), `PIPELINE` (L2+), `SENSITIVE` (sensitivity above public), `OPEN` (openness is open or open-on-publication), `COLLAB` (L3+), `NESTED_SKILLS` (nested `.skills/` emitted), `OKF` (publishing an OKF bundle). Strip any block whose flag is off; substitute every token (leftover `{{ }}` is a bug).

## Audit mode

When asked to audit `<path>`: glob the target repo (read-only), load `references/INDEX.md` via the indexer, and score what exists against each level and the six goals. Print a prioritized gap table — `Goal / Level → Found? → Recommended template or practice → Source`. If a `knowledge/`-style bundle exists, check OKF conformance (every non-reserved `.md` has parseable frontmatter with a non-empty `type`; bundle-root declares `okf_version`). Then offer to scaffold the missing rungs. Do not modify the repo until the user approves remediation.

## Guardrails

Write only into the user's working directory, never the skill's. Keep L0/L1 genuinely lightweight — no pipeline, governance, or knowledge-bundle bloat there. Prefer a `ROADMAP.md` entry over a generated file when unsure. Apply the sensitivity coupling automatically. Don't install packages or run network commands without asking. If a template the plan names is missing, report it rather than inventing its contents.

## What's built vs. roadmap

This skill is built out for **L0–L2** (structure, documentation, the Python reproducible stack) plus full interview/sample/synthesize/audit. **L3–L5** artifacts (governance, roles, charter, nested skills, responsible-data and data-quality checklists, accessibility, the R variant, CI, and the OKF bundle templates) are on the corpus roadmap: `references/INDEX.md` marks each template ⭐ built or ○ roadmap. For ○ items, route the concern into the project's `ROADMAP.md` rather than generating a file — and surface the same to the user. As those templates land, they become available with no change to this workflow.

## Reference map

- `references/context.md` — mission, design principles, hard gates (privacy law + CARE), relationship to the `data-liberation` skill, CUPIDS infra profile.
- `references/escalation-levels.md` — the L0–L5 ladder, entry protocol, and now/later mechanism.
- `references/installed-base.md` — the values spine and the affordance↔duty coupling.
- `references/collaboration-architecture.md` — typology, roles, team-data-science practices, charter, anti-patterns.
- `references/INDEX.md` — the crosswalk the indexer samples (goal/level/signal → practice → template, with build status).
- `references/*.md` — per-framework digests (Cookiecutter, OUHSC, Snakemake, Git/GitHub, Turing Way, Responsible Data, Data Collaboratives; OKF and others on the roadmap).
- `agents/*.md` — the interviewer, indexer, and synthesizer role definitions.
- `templates/` — the scaffolding artifacts; `templates/directory-tree.md` is the structural source of truth.

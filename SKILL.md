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
  "data dictionary," "governance," "responsible data," "open knowledge," "OKF," "agent discovery," "ARD,"
  "ai-catalog," "make it discoverable by agents," "deposit," "Dataverse," "get a DOI," "archive the data,"
  "audit my repo," even when
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

On approval, for each file in the manifest: read its template from `templates/…`, substitute `{{TOKENS}}` from the fill-map, include or strip `<!-- IF:FLAG -->…<!-- /IF -->` blocks per the Profile, and write it into the target directory with the `.tmpl` suffix removed. Create directories per `templates/directory-tree.md`, adding `.gitkeep` to empty `data/` dirs and documenting `data/raw` as immutable. Fill `ROADMAP.md`'s `{{ROADMAP_ROWS}}` from the synthesizer's roadmap (one row per deferred concern; mark coupling-forced items **blocking**). At L5, emit the `knowledge/` OKF bundle from the data dictionary (see `references/okf-open-knowledge-format.md`); when the `ARD` flag is set (the project exposes agentic resources — nested `.skills/`, a published dataset, an MCP/A2A service), also emit the repo-scope `ai-catalog.json` + `DISCOVERY.md` agent-discovery layer (see `references/agentic-resource-discovery.md`) and record serving it at the host `.well-known/` path and registering it with a registry as `ROADMAP.md` items. When the `DATAVERSE` flag is set, also emit the `dataverse/` deposit kit (`dataset.json`, `deposit-dataverse.sh`, `deposit_dataverse.py`, `DEPOSIT.md`) that archives processed data, code, and documentation to a Dataverse repository for a citable DOI (see `references/dataverse-deposit.md`); **generating the kit never deposits or publishes** — depositing runs through Deposit mode with explicit confirmation. Adjust any intra-project link inside a template so it points to a file you actually generated — if a referenced doc (e.g. `GOVERNANCE.md`) was deferred, point the reader to `ROADMAP.md` instead, so the scaffold never ships a dangling link. Default to creating a new `./<project-slug>/` unless the user is scaffolding into an existing repo; never overwrite an existing file without confirmation.

### Step 6.5 — Handoff & tracking

Turn the synthesizer's **Engagement TODOs** into a shared, assignable work record. Write the Markdown layer first, always: render `ROADMAP.md`'s `{{TRACKING_ROWS}}` (this level's assignable checklist) and `NEXT-STEPS.md` (the handoff memo). Then, if the project is on GitHub at L3+, project the same TODOs onto GitHub — delegate to `data-project-tracker` (it uses `gh` when authed, the GitHub MCP otherwise) to create-or-update labels, a per-level milestone, and one issue per TODO, and — when permitted — a Project with standardized fields/views/built-in workflows, linking each issue to its checklist row and posting a status update. Follow the capability/degradation chain in `references/github-project-management.md` (GitHub remote? → `gh auth status` + scopes? → Project permission?), landing at the richest tier available; when `gh`/auth/permission is missing, stop at the Markdown layer plus the unrun `seed-github.sh` + paste-able `engagement-issues.md`, and tell the user the one command to finish later. The sync is **idempotent** — match by `.github/engagement-sync.json`, then by the `<!-- data-project:task=… -->` issue marker; update, never duplicate. The Markdown checklist is the source of truth; GitHub is a projection of it. Never fail the scaffold because GitHub is unavailable.

### Step 7 — Verify & offer next

Confirm every planned file exists and that no unfilled `{{` tokens remain (`grep -Rn "{{" <project>/` should return nothing). If the user opts in and the toolchain is present, `git init` and run a pipeline dry-run (`snakemake -n`). Print a short "Created N files" summary with next steps (e.g. "fill the data dictionary before ingesting; complete the responsible-data checklist before sharing"), then offer the next rung. **Gate the offer on tracking:** before offering to climb, confirm this level's TODOs are in the `ROADMAP.md` checklist and — if the project is on GitHub — filed as issues / on the Project, and that **blocking** items are closed or explicitly acknowledged; state the tracking status in the offer (e.g. "L3 scaffolded; its 6 tasks are filed as issues, 2 blocking still open — resolve those or climb to L4?"). Don't climb past unaddressed blocking items without explicit acknowledgement.

## Placeholders & conditionals

Templates use `{{UPPER_SNAKE}}` tokens and `<!-- IF:FLAG -->…<!-- /IF -->` blocks. Core tokens: `PROJECT_NAME`, `PROJECT_SLUG` (kebab-case), `PKG_NAME` (the slug with hyphens→underscores — a valid Python module/package name), `DESCRIPTION`, `PI_NAME`, `LAB_NAME` (default "CUPIDS Lab"), `YEAR`, `LICENSE`, `LEVEL`, `SENSITIVITY_TIER`, `OPENNESS`, `CONTACT_EMAIL`, `TOOLING`, `REPO_URL`, `RAW_FILE`, `ROADMAP_ROWS`. GitHub project-management tokens (Step 6.5 / Track mode): `REPO_SLUG` (owner/repo), `DEFAULT_BRANCH` (default `main`), `MILESTONE_TITLE`, `PROJECT_TITLE`, `TRACKING_ROWS` (this-level assignable checklist rows), `ISSUE_SEED_ROWS` (issue title/body/labels rows), `OWNER_DEFAULT` (default assignee/role). ARD discovery tokens (Step 6 / L5 `ai-catalog.json`): `ARD_SPEC_VERSION` (manifest `specVersion`, currently `1.0`), `ARD_HOST_DOMAIN` (the domain that anchors the resource URNs and host identity, e.g. `evictions.example.org`), `ARD_HOST_IDENTIFIER` (host identity, conventionally `did:web:<domain>`). Dataverse deposit tokens (Step 6 / L5 + Deposit mode): `DATAVERSE_URL` (default `https://dataverse.harvard.edu`), `DATAVERSE_COLLECTION` (target collection alias), `DATASET_SUBJECT` (one of Dataverse's controlled subjects, e.g. `Social Sciences`). Conditional flags, set from the Profile: `WHY` (include narrative), `PIPELINE` (L2+), `SENSITIVE` (sensitivity above public), `OPEN` (openness is open or open-on-publication), `COLLAB` (L3+), `NESTED_SKILLS` (nested `.skills/` emitted), `OKF` (publishing an OKF bundle), `GH` (repo is on GitHub / GitHub PM scaffolds emitted), `PROJECT` (a GitHub Project is in scope), `WIKI` (wiki seeds emitted), `ARD` (emit the L5 ARD `ai-catalog.json` + `DISCOVERY.md` agent-discovery layer), `DATAVERSE` (emit the L5 Dataverse deposit kit). Strip any block whose flag is off; substitute every token (leftover `{{ }}` is a bug). Note: never put a literal GitHub Actions `${{ … }}` expression in a template — write the `secrets.NAME` reference in prose instead, so it isn't mistaken for an unfilled token.

## Audit mode

When asked to audit `<path>`: glob the target repo (read-only), load `references/INDEX.md` via the indexer, and score what exists against each level and the six goals. Print a prioritized gap table — `Goal / Level → Found? → Recommended template or practice → Source`. If a `knowledge/`-style bundle exists, check OKF conformance (every non-reserved `.md` has parseable frontmatter with a non-empty `type`; bundle-root declares `okf_version`). Then offer to scaffold the missing rungs. Do not modify the repo until the user approves remediation.

## Track mode

When asked to track or sync a plan, roadmap, or to-do to GitHub (e.g. `/data-project track [path]`, or "turn my roadmap into issues," "put these on a board," "update the project from the roadmap"): read the source — the project's `ROADMAP.md` checklist by default, or a path/pasted text the user gives — normalize it to the Engagement TODO schema, and run the same **idempotent** sync as Step 6.5 via `data-project-tracker`: create-or-update Issues, the Project (fields/views/workflows + status update), and — if `WIKI` — wiki pages, with the same capability fall-backs. It is re-runnable: run it again after editing the roadmap and it updates the existing issues/items instead of duplicating them. Confirm access first against the checklist in `references/github-project-management.md` and report exactly what scope is missing (and how to grant it) if a step can't run; degrade to the script + paste-list rather than failing.

## Deposit mode

When asked to deposit, archive, or publish the project's outputs to a data repository for a DOI (e.g. `/data-project deposit [path]`, "deposit this to Harvard Dataverse," "archive the data and get a DOI," "submit data/code/docs to Dataverse"): delegate to `data-project-depositor`, following `references/dataverse-deposit.md`. It builds the citation `dataset.json`, then runs the **capability chain** — pyDataverse if importable → the `deposit-dataverse.sh` curl script → otherwise emit the deposit kit and hand back the one command plus the `DATAVERSE_API_TOKEN`/collection to set. It maps `data/processed`→**Data**, `src/`+pipeline→**Code**, and `README`/`DATA-DICTIONARY`/`data-card`/`knowledge/`→**Documentation** (Dataverse file `categories` + `directoryLabel`), and is **idempotent** via `dataverse/.dataverse-deposit.json` (update files, never duplicate the dataset). Two hard rules: **gate on sensitivity first** — never deposit identifiable or restricted traces openly; apply `GOVERNANCE.md` access tiers (restrict, desensitize, or withhold) and finish the bulletproofing/responsible-data checks — and **a deposit stops at a draft and only publishes (mints the DOI) on explicit confirmation**. Recommend a `DRY_RUN=1` run against `demo.dataverse.org` first. Never commit the token; never fail the scaffold because credentials are missing — degrade to the kit + instructions.

## Guardrails

Write only into the user's working directory, never the skill's. Keep L0/L1 genuinely lightweight — no pipeline, governance, or knowledge-bundle bloat there. Prefer a `ROADMAP.md` entry over a generated file when unsure. Apply the sensitivity coupling automatically. Don't install packages or run network commands without asking. If a template the plan names is missing, report it rather than inventing its contents.

## What's built vs. roadmap

This skill is built out across **all levels L0–L5**: structure and documentation; the Python (conda + Snakemake) and R (renv + targets) reproducible stacks plus CI; collaboration and governance (contributing, code of conduct, roles + CODEOWNERS, governance, charter, collaboration protocol, contributed-data intake, and nested `.skills/`); the responsible-data, data-management, bulletproofing, data-quality, and accessibility artifacts plus the installed-base values spine and the Data Card; and the L5 licensing, canvases, OKF knowledge bundle, the ARD `ai-catalog.json` agent-discovery layer, and the Harvard Dataverse deposit kit. `references/INDEX.md` records each template's build status. Having the full menu does not change the lean-by-default stance: the now/later mechanism still defers anything above the chosen level into the project's `ROADMAP.md` by the user's choice. If a template the plan names is ever missing, route the concern to `ROADMAP.md` rather than inventing content.

## Reference map

- `references/context.md` — mission, design principles, hard gates (privacy law + CARE), relationship to the `data-liberation` skill, CUPIDS infra profile.
- `references/escalation-levels.md` — the L0–L5 ladder, entry protocol, and now/later mechanism.
- `references/installed-base.md` — the values spine and the affordance↔duty coupling.
- `references/collaboration-architecture.md` — typology, roles, team-data-science practices, charter, anti-patterns.
- `references/INDEX.md` — the crosswalk the indexer samples (goal/level/signal → practice → template, with build status).
- `references/*.md` — per-framework digests (Cookiecutter, OUHSC, Snakemake, Git/GitHub, GitHub Project Management, Turing Way, Responsible Data, Data Collaboratives, Data Cards Playbook, USDS Playbook, ProPublica Bulletproofing/Collaborative/Collaborate, Quartz Bad Data, OKF, Agentic Resource Discovery, Harvard Dataverse Deposit).
- `agents/*.md` — the interviewer, indexer, synthesizer, tracker, and depositor role definitions.
- `templates/` — the scaffolding artifacts; `templates/directory-tree.md` is the structural source of truth.

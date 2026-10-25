---
type: Procedure
title: Scaffold a data project from the templates
description: How to turn an approved project brief into files. Which templates belong to which Outline section, the token and flag tables, the layout under docs/, how the data-liberation project template fits in, link adjustment, never overwriting, the curated-source carve-out, and the honest single-steward variant.
tags: [scaffold, templates, tokens, flags, layout, sections]
---

# Scaffold a data project from the templates

Run this only after the user approved the plan (SKILL.md "Start a project", step 2). It says which templates to render for which Outline section, how to fill them, and where the output goes.

## Contents

- [The rule: five files, then sections on arrival](#the-rule-five-files-then-sections-on-arrival)
- [Templates by Outline section](#templates-by-outline-section)
- [Projects that extract data: use data-liberation's template](#projects-that-extract-data-use-data-liberations-template)
- [Rendering: tokens, flags, file names](#rendering-tokens-flags-file-names)
- [Tokens](#tokens)
- [Flags](#flags)
- [Layout](#layout)
- [Rules while writing](#rules-while-writing)
- [Verify](#verify)

## The rule: five files, then sections on arrival

Every project starts with the five working files and nothing else that nobody will maintain: `README.md`, `AGENTS.md` (plus a `CLAUDE.md` whose whole content is the line `@AGENTS.md`), `ROADMAP.md`, `decision-log.md` and `CHANGELOG.md`, plus `LICENSE`, `.gitignore` and `.gitattributes`. Every other template is rendered only when work reaches the section that owns it and that section is *now* in the brief. Say in the plan what you are not generating and why ("no CHARTER: solo project; no FAIR checklist: visibility is private").

Checklists default to an **issue task list** at the gate they govern (paste the checklist items into the section issue, with a named signer). Render a checklist as a file only when it must ship with a release or a deposit, or when the project has no issue tracker.

## Templates by Outline section

Paths are relative to this skill's `templates/` folder; output paths are relative to the project root.

| Section | Template | Output | Render when |
| --- | --- | --- | --- |
| always | `README.md.tmpl` | `README.md` | every project |
| always | `AGENTS.md.tmpl` | `AGENTS.md` | every project; also write `CLAUDE.md` (see below) |
| always | `ROADMAP.md.tmpl` (vendored) | `ROADMAP.md` | every project; fill the Status/Notes columns from the brief |
| always | `decision-log.md.tmpl` (vendored) | `decision-log.md` | every project; first entries record sensitivity, visibility and exclusions |
| always | `CHANGELOG.md.tmpl` | `CHANGELOG.md` | every project |
| always | `gitignore.tmpl`, `gitattributes.tmpl` | `.gitignore`, `.gitattributes` | every project not using data-liberation's template (which ships its own) |
| 1 Scope & gate | `scope-canvas.md.tmpl` | `docs/scope-canvas.md` | multi-partner collaborations or when the user asks for a design canvas |
| 1 Scope & gate | `responsible-data-checklist.md.tmpl` | `docs/checklists/responsible-data-checklist.md` | data is sensitive or CARE-implicated; fill it from the scoping answers now |
| 1 Scope & gate | `GOVERNANCE.md.tmpl` (stub) | `docs/governance/GOVERNANCE.md` | data is sensitive (the access tiers and remedy must exist before sensitive features do) |
| 2–4 Acquire, Extract, Model | data-liberation's `templates/project/` | project root or `pipelines/<name>/` | the project extracts data (see the next section) |
| 4 Model & tidy | `data-dictionary.md.tmpl` | `docs/data-dictionary.md` | only when there is no data-liberation pipeline (R variant, hand-curated dataset) |
| 5 Pipeline & audit | `ci/github-actions-ci.yml.tmpl` | `.github/workflows/ci.yml` | Python projects without data-liberation's `tests.yml`, and R projects |
| 5 Pipeline & audit | `ci/pipelines-ci.yml.tmpl` | `.github/workflows/pipelines-ci.yml` | multi-pipeline repos (`PIPELINES`), instead of the single-project CI |
| 5 Pipeline & audit | `python/pre-commit-config.yaml.tmpl` | `.pre-commit-config.yaml` | the team uses pre-commit (always with `NOTEBOOKS`) |
| 5 Pipeline & audit | `python/Snakefile.tmpl`, `python/config.yaml.tmpl` | `Snakefile`, `config.yaml` | optional wrapper only, when the user wants Snakemake; it calls `python -m scripts.pipeline run` and CI never depends on it |
| 5 Pipeline & audit | `r/DESCRIPTION.tmpl`, `r/_targets.R.tmpl`, `r/Makefile.tmpl`, `r/renv-note.md.tmpl` | `DESCRIPTION`, `_targets.R`, `Makefile`, `docs/renv.md` | R projects (the maintained R variant) |
| 5 Pipeline & audit | `pre-release-checklist.md.tmpl` | `docs/checklists/pre-release-checklist.md` | a release, publication or deposit is planned |
| 6 Document & cite | `CITATION.cff.tmpl` | `CITATION.cff` | the data or code will be cited |
| 6 Document & cite | `data-card.md.tmpl` | `docs/data-card.md` | publishing or depositing |
| 6 Document & cite | `codemeta.json.tmpl` | `codemeta.json` | only when releasing a software package |
| 7 Govern & collaborate | `GOVERNANCE.md.tmpl` | `docs/governance/GOVERNANCE.md` | collaborators or sensitive data |
| 7 Govern & collaborate | `CHARTER.md.tmpl` | `docs/governance/CHARTER.md` | more than one person or partner organization |
| 7 Govern & collaborate | `data-management-plan.md.tmpl` | `docs/governance/data-management-plan.md` | sensitive or contributed data, or a funder requires a plan |
| 7 Govern & collaborate | `CONTRIBUTING.md.tmpl`, `CODE_OF_CONDUCT.md.tmpl`, `CODEOWNERS.tmpl` | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CODEOWNERS` | collaborators (root, where GitHub detects them) |
| 7 Govern & collaborate | `github/PULL_REQUEST_TEMPLATE.md.tmpl` | `.github/PULL_REQUEST_TEMPLATE.md` | the project is on GitHub |
| 8 Publish | `FAIR-CHECKLIST.md.tmpl`, `accessibility-checklist.md.tmpl` | `docs/checklists/` | visibility is public or embargoed and section 8 is *now* (publishing surfaces come from data-liberation) |
| 9 Deposit | `dataverse/*.tmpl` | `dataverse/` | `DATAVERSE`; see `deposit.md` |
| 9 Deposit | `ci/dataverse-deposit.yml.tmpl` | `.github/workflows/dataverse-deposit.yml` | `DATAVERSE` and `UPDATING` |
| 9 Share | `opensharing/*.tmpl` | `opensharing/` | `OPENSHARING`; see `../open-sharing-protocol.md` |
| 9 Discover | `ard/ai-catalog.json.tmpl`, `ard/DISCOVERY.md.tmpl` | `ai-catalog.json`, `DISCOVERY.md` | `ARD`; see `../agentic-resource-discovery.md` |
| 9 Discover | `okf/*.tmpl` | `knowledge/` | `OKF`; see `../okf-open-knowledge-format.md` |
| 10 Maintain & feedback | `github/ISSUE_TEMPLATE/{config,task,data-issue}.yml.tmpl` | `.github/ISSUE_TEMPLATE/` | a team on GitHub (`GH`) |
| 10 Maintain & feedback | `github/labels.yml.tmpl`, `github/seed-github.sh.tmpl` | `.github/labels.yml`, `.github/seed-github.sh` | a team on GitHub; see `tracking.md` |

`templates/directory-tree.md` shows the resulting layout and is read, not copied.

## Projects that extract data: use data-liberation's template

If the project will acquire or extract data with code, render `data-liberation`'s project template for the pipeline instead of inventing one. That template owns the canonical project shape: uv and `pyproject.toml`, Python `>=3.12` with CI on 3.13, code in `scripts/` (run with `uv run python -m scripts.pipeline run`), immutable originals in `data/original/`, outputs in `data/processed/`, audit reports in `data/audit/`, lookups in `data/lookups/`, and the dictionary at `docs/data-dictionary.md`. Follow that skill's instructions for rendering it.

- **Single pipeline:** render it at the project root. Where both skills supply a file (`README.md`, `AGENTS.md`, `ROADMAP.md`, `decision-log.md`, `.gitignore`, `.gitattributes`), write one file: start from data-liberation's and add this skill's sections it lacks (the README's "What & why" fields, Visibility and License by layer; the AGENTS.md start-here, project rules and sprint-end lines). Never write two copies. Add this skill's token guard step to data-liberation's `tests.yml` rather than adding a second CI workflow.
- **Several pipelines:** render each under `pipelines/<name>/`, keep this skill's five working files and governance at the root, and follow `../multi-pipeline.md`.
- **No pipeline** (a hand-curated dataset, an R project, a collaboration that only governs and deposits): use this skill's `gitignore.tmpl`, `gitattributes.tmpl` and `data-dictionary.md.tmpl`, and the same `data/original/`, `data/processed/` layout.

## Rendering: tokens, flags, file names

For each file in the approved plan: read the template, substitute every `{{TOKEN}}`, keep or drop each `<!-- IF:FLAG -->…<!-- /IF -->` block according to the flag (drop the markers either way), and write the result with the `.tmpl` suffix removed. A leftover `{{` is a bug. GitHub Actions expressions (the `$`-prefixed double-brace form) are not tokens; leave them alone. Never write a bare double-brace expression that is not a documented token.

`CLAUDE.md` has no template: write a file containing exactly `@AGENTS.md`. If the team uses agent tools that do not read `AGENTS.md` on their own, add thin pointer files for them (for example `.github/copilot-instructions.md` or `GEMINI.md`), each a single line pointing to `AGENTS.md`; `AGENTS.md` wins any disagreement. Warn the user that a `CLAUDE.local.md` can stop Claude Code from loading `AGENTS.md` under its default setting.

## Tokens

| Token | Meaning | Default or source |
| --- | --- | --- |
| `PROJECT_NAME` | human-readable project name | brief |
| `PROJECT_SLUG` | kebab-case repository and distribution name | derived from the name |
| `PKG_NAME` | snake_case import name (`PROJECT_SLUG` with hyphens as underscores) | derived |
| `DESCRIPTION` | one-sentence description | brief |
| `PI_NAME` | the responsible person (principal investigator or steward) | brief |
| `LAB_NAME` | lab or organization | "CUPIDS Lab" |
| `CONTACT_EMAIL` | contact for questions, corrections and conduct reports | brief |
| `YEAR` | four-digit year of scaffolding | today |
| `DATE` | ISO date of scaffolding (`YYYY-MM-DD`); used wherever a real date is needed | today |
| `SKILL_VERSION` | this skill's `metadata.version` from SKILL.md, stamped into `AGENTS.md` | SKILL.md |
| `LICENSE` | SPDX identifier of the code license | `MIT` |
| `SENSITIVITY_TIER` | `public`, `de-identified`, `sensitive-human` or `regulated` | brief (most protective if unknown) |
| `VISIBILITY` | `private`, `embargoed` or `public` | brief (`private` if unknown) |
| `TOOLING` | `Python` or `R` | `Python` |
| `REPO_URL` | the repository URL | brief, or `https://github.com/<owner>/<slug>` |
| `RAW_FILE` | file name of the first original under `data/original/` (R pipeline input) | brief |
| `REPO_SLUG` | `owner/repo` on GitHub | brief |
| `DEFAULT_BRANCH` | the default branch | `main` |
| `PROJECT_TITLE` | GitHub Project board title (`PROJECT` flag) | `<PROJECT_NAME> work` |
| `OWNER_DEFAULT` | default assignee (a GitHub handle) for seeded issues | the PI's handle |
| `ISSUE_SEED_ROWS` | one `seed_issue …` line per *now* section, built as in `tracking.md` | ROADMAP |
| `ARD_SPEC_VERSION` | ARD manifest `specVersion` | `1.0` |
| `ARD_HOST_DOMAIN` | domain that anchors the resource URNs | brief |
| `ARD_HOST_IDENTIFIER` | host identity, conventionally `did:web:<domain>` | derived |
| `DATAVERSE_URL` | production Dataverse installation | `https://dataverse.harvard.edu` |
| `DATAVERSE_COLLECTION` | target collection alias (must exist and be published) | brief |
| `DATASET_SUBJECT` | one of Dataverse's controlled subjects | `Social Sciences` |
| `UPDATE_FREQUENCY` | refresh cadence in words (`Quarterly`) | brief |
| `DEPOSIT_CRON` | cron schedule for that cadence | derived |
| `OPENSHARING_ENDPOINT` | sharing server URL | brief or a marked placeholder |
| `SHARE_STORAGE_BASE` | object-storage root for shared assets | brief or a marked placeholder |

## Flags

| Flag | Set when | Effect |
| --- | --- | --- |
| `PIPELINE` | the project has a reproducible pipeline at its root | README and CONTRIBUTING show the run commands |
| `PIPELINES` | several pipelines under `pipelines/<name>/` | multi-pipeline notes; `pipelines-ci.yml` replaces the single-project CI |
| `SENSITIVE` | sensitivity is above `public`, or CARE applies | access-tier, remedy and do-not-deposit-openly text everywhere |
| `OPEN` | visibility is `public` or `embargoed` and outputs will be released openly | open-data sentences in README and FAIR checklist |
| `COLLAB` | more than one person works on the project | review-by-PR rules, CODEOWNERS routing, branch-protection step |
| `SOLO` | exactly one person works on the project | single-steward statements instead of review gates; never set together with `COLLAB` |
| `GH` | the repository is on GitHub | tracking and issue-form text |
| `PROJECT` | a GitHub Project board is in scope | board steps in the seed script and CONTRIBUTING |
| `NOTEBOOKS` | the project keeps Jupyter notebooks | `nbstripout` filter, hook and one-time install note |
| `OKF` | an OKF `knowledge/` bundle is in scope | OKF mapping text |
| `ARD` | an ARD catalog is in scope | discovery text |
| `DATAVERSE` | a Dataverse deposit kit is in scope | deposit text |
| `UPDATING` | the deposited data is refreshed on a cadence | scheduled re-deposit workflow and version metadata |
| `OPENSHARING` | an OpenSharing share kit is in scope | sharing text |

**Honest governance.** `COLLAB` blocks claim review gates ("a PR needs an approving review"), so every template that has one also carries the branch-protection step that enforces it; run or hand over that step when you scaffold (`../github.md`). `SOLO` blocks say plainly that one steward makes and records decisions, with no pretend review. `tools/validate_data_project.py` checks that both variants exist in the governance templates and that approval language never appears without branch protection.

## Layout

```
<project-slug>/
├── README.md  AGENTS.md  CLAUDE.md  ROADMAP.md  decision-log.md  CHANGELOG.md   # the five working files
├── LICENSE  .gitignore  .gitattributes  CITATION.cff
├── pyproject.toml  scripts/  tests/  data/{original,processed,audit,lookups}/  # from data-liberation
├── docs/
│   ├── data-dictionary.md  data-card.md  scope-canvas.md
│   ├── governance/   GOVERNANCE.md  CHARTER.md  data-management-plan.md
│   └── checklists/   responsible-data-checklist.md  pre-release-checklist.md  FAIR-CHECKLIST.md  accessibility-checklist.md
├── CONTRIBUTING.md  CODE_OF_CONDUCT.md  CODEOWNERS
├── .github/  PULL_REQUEST_TEMPLATE.md  ISSUE_TEMPLATE/  labels.yml  seed-github.sh  workflows/
└── dataverse/  opensharing/  ai-catalog.json  DISCOVERY.md  knowledge/          # section 9, only if in scope
```

Only files whose section is *now* exist on disk; `templates/directory-tree.md` annotates each path with its section.

## Rules while writing

- **Write only into the user's project**, never into this skill's folder. Default to a new `./<project-slug>/` unless the user is working in an existing repository.
- **Never overwrite** an existing file without confirmation. In an existing project, merge new sections into existing files instead of replacing them, and in a shared repository work on a branch and open a PR.
- **Adjust links to what exists.** Templates link to documents of other sections (for example `docs/governance/GOVERNANCE.md`). If that document was not generated, point the reader to its `ROADMAP.md` row instead, so the scaffold never ships a dangling link.
- **Curated sources are committed.** The `.gitignore` ignores bulk originals by default. When an original is a small, hand-made source of record (the project's actual asset), add a carve-out (`!data/original/<file>`, plus `!data/original/<dir>/` for each parent directory) so it is tracked, and record it as immutable in the data dictionary and the decision-log. Where originals live (committed, Git LFS, or external storage with hash and URL in provenance) is section 2's storage-budget decision.
- **Fill from the brief, don't invent.** If a value is unknown, use a clearly marked placeholder in angle brackets (`<who reviews corrections>`) and add a ROADMAP note, rather than a plausible fake. Never write fake dates.
- **Missing template:** if a template the plan names does not exist, say so and record the need in `ROADMAP.md`; don't improvise its contents.

## Verify

Before reporting done: every planned file exists; `grep -Rn "{{" <project>/` finds nothing except GitHub Actions expressions; every intra-project link resolves (or points at a ROADMAP row); `CLAUDE.md` is exactly `@AGENTS.md`; and the README alone explains what the project is and how to use it. If the user opts in and the toolchain is present, `git init` and run the pipeline's tests once (`uv sync && uv run pytest`, or `make dryrun` for R). Then report what you created, what you deferred and why, and the first *now* section's next step.

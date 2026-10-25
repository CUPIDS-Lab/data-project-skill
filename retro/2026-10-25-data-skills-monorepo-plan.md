# Plan — merge `data-project` and `data-liberation` into one monorepo (`cupids-lab/data-skills`)

**Status:** proposed, awaiting maintainer approval. Nothing below has been executed.
**Baselines:** `data-project` 0.10.0 (this repo, `636c930`); `data-liberation` 0.4.0 (`CUPIDS-Lab/data-liberation-skill`, `acb59c9`); `CUPIDS-Lab/data-liberation-template` (already folded into `data-liberation` by its PR #27 but never archived).
**Goals, in the maintainer's words:** prevent drift between the skills; give project sprints a single input for feedback; refresh both skills to current best practices after several months; fix an onboarding experience with "no central outline and guide about what to do."
**Evidence base:** an audit of both skills; nine downstream project repos built with them (deliberately not named here); the Agent Skills spec and Anthropic authoring guidance as of October 2026, including a prototype monorepo tested against `skills-ref`, `npx skills` and `claude plugin details`; SoMarkAI's skills collection and sibling repos; and a 2026 survey of document-parsing tools (OXR, Awesome-Document-Understanding, benchmarks).

---

## 0. Decisions at a glance

| # | Decision | Choice |
|---|---|---|
| D1 | Repo shape | **One repo, two skills.** `skills/data-project/` and `skills/data-liberation/`, each self-contained and separately triggered and versioned. Not one merged skill; not two repos. |
| D2 | Home | **This repo**, restructured and renamed `cupids-lab/data-skills` (GitHub redirects the old URL). `data-liberation` history is imported with `git subtree`. |
| D3 | Shared content | **`shared/` is the source of truth**, copied into each skill by `tools/vendor.py`; CI fails if any copy drifts. No symlinks and no `../` paths, because installed skills must be self-contained. |
| D4 | Ladders | **Both L0–L5 ladders are removed.** One outcome-based **Outline** of ten sections with "done when" tests replaces them, shared by both skills, the README, the project scaffold and the feedback form. |
| D5 | Artifacts | **Outcomes first.** A project starts with five maintained files (README, AGENTS.md, ROADMAP, decision-log, CHANGELOG) plus one issue per in-scope outline section. Every other artifact is generated only when the section that needs it is reached. |
| D6 | Feedback | **One GitHub issue form** (`sprint-feedback.yml`) on `data-skills`. Its section dropdown is the Outline, so every lesson lands on a named section and the file that owns it. Triage labels encode skill, section and root cause. |
| D7 | Refresh depth | **Aggressive.** Consolidate references (substance of the values spine, deposit/sharing kits and source digests is protected), cut agents that only existed to pick artifacts by level, fix the seam between the skills, repair `data-liberation` debt, update tooling. |
| D8 | Extraction | **Survey plus rewritten guidance; no new template code.** Text layer first for born-digital PDFs; VLM parsers (OXR and peers) as an audited option with a parser manifest and page-plus-bounding-box provenance. |
| D9 | Distribution | Supports all three install paths in use: claude.ai org skills (per-skill zips attached to each release), `npx skills add cupids-lab/data-skills`, and manual copy. A Claude Code plugin marketplace is an optional extra, never a dependency. |
| D10 | Versioning | Per-skill semver in `metadata.version`, tags `data-project--vX.Y.Z` / `data-liberation--vX.Y.Z`, one root CHANGELOG with per-skill sections. Both skills start the monorepo at **1.0.0**. |

---

## 1. Why: what the evidence shows

**Drift is real and already costly.** The two `validate.py` files differ by about 300 lines and check different things; the CI workflows differ; both trigger descriptions claim "data dictionary." The worst break is at the seam: `data-project`'s multi-pipeline CI discovers pipelines by globbing `pipelines/*/Snakefile` (`templates/ci/pipelines-ci.yml.tmpl:55`), but `data-liberation`'s template and every real pipeline lack a Snakefile, so a repo built to spec silently tests nothing. The Dataverse deposit kit expects `src/` and a root `DATA-DICTIONARY.md`, while `data-liberation` projects use `scripts/` and `docs/data-dictionary.md`. The skills also disagree on `data/raw` vs `data/original`, uv/pyproject vs conda/Snakefile, Python 3.12 vs 3.11, and `PROJECT_SLUG` casing.

**Feedback reached only one skill.** `data-project` absorbed two rounds of after-action reports (0.4.0 → 0.8.0, 0.10.0). `data-liberation`'s revision plan (`retro/data-liberation-skill-revision-plan.md`) has been "proposed" since June and was never executed, and `data-project` 0.10.0 explicitly declared its liberation findings "out of scope." Neither repo has any issues or an issue form; the only feedback record is hand-carried `audits/` folders in project repos.

**The two ladders contradict each other.** The same numbers mean different things: L0 scaffolds a repo in one skill and forbids a scaffold in the other; L3 is "Collaborate" in one and "Harmonization" in the other; governance is L3 in one and L4 in the other. One private project ended up with four numbering schemes in one repo. Above L2, `data-liberation`'s levels gate nothing, because its L2 template already ships the L3 and L5 files.

**Artifacts over outcomes, measured.** In one multi-pipeline project, one PR jumped from L1 to L4 (78 files, 19 governance docs); none of those docs was ever edited for content afterward. The four L4 checklists sit at 0 of 65 boxes checked, the onboarding issue has been open four months, and CODEOWNERS still carries placeholders, while the gating outcome (the first publish) never happened. A full `data-project` L5 run emits about 65–70 files, of which roughly 15 do real work on day one. The documents people actually keep current across projects are README, AGENTS, ROADMAP, decision-log and CHANGELOG.

**People work in issues.** In a private project's first two-person sprint, every decision happened in issue comments; none reached the CHARTER, GOVERNANCE, checklists or decision-log that `data-project` calls the source of truth. This supports making issues the working surface and keeping Markdown for what must outlive the sprint.

**Onboarding has no front door.** One project's root `AGENTS.md` links about 22 docs plus 3 nested skills, 4 pipeline `AGENTS.md` files and about 930 lines of `context/`; five documents each partly answer "where do I start?" (README, AGENTS, NEXT-STEPS, ROADMAP, CONTRIBUTING). Neither skill triggers on "sprint," "retro" or "feedback."

**Projects already fixed what the skills get wrong.** One project's shared `pipelines/_core/` has a fresh-per-run error log, a `--fresh` refetch, progress reporting, dedup-before-validate, entity seeds and `nbstripout`; the `data-liberation` template still appends to its error log. All three projects in the first pass hit sources the skills don't cover (APIs, BI dashboards, ArcGIS layers), plus ephemeral sources that show only the current day and sampled keys that changed when an agency renumbered records.

**Both skills fail the current spec.** `data-liberation`'s description is 1,237 characters (limit 1,024); `data-project`'s `argument-hint` frontmatter key is rejected by claude.ai uploads and the Skills API. Both SKILL.md bodies exceed the ~5,000-token target (about 8.9k and 10k), which matters because Claude Code keeps only the first 5,000 tokens of a skill after compaction.

### Counterarguments considered

- **"Keep two repos; add a sync check."** This keeps separate install URLs and stars, but the coupling is one-way and tight (a `data-project` repo *is* a monorepo of `data-liberation` pipelines), every seam fix becomes two coordinated PRs, and the feedback-routing failure above is precisely a two-repo failure. `npx skills` and claude.ai both handle multi-skill repos, and per-skill versions don't need separate repos. Rejected.
- **"Merge into one skill."** `data-liberation`'s value is that "just give me the CSV" loads nothing about governance, OKF or Dataverse. One merged skill would load that context for every PDF request and blur the trigger. Two skills keep progressive disclosure and sharp triggers. Rejected.
- **"A monorepo copies everything into installs."** `npx skills` copies the whole skill folder, so repo-maintenance files (CI, evals, CONTRIBUTING, retros) must live at the repo root, not under `skills/<name>/`. That is the layout below, and it also resolves open PR #26 on `data-liberation-skill`, which proposed exactly this to stop "extra files polluting context."
- **Real cost of the merge:** installed users' URLs change. Mitigated by GitHub's rename redirect, tombstone READMEs in the archived repos, and identical skill `name`s so claude.ai org skills keep working.

---

## 2. Target architecture

```
data-skills/
├── README.md                 # front door: what each skill is for, the Outline, install (3 paths), feedback link
├── OUTLINE.md                # the central guide: 10 sections × outcome × "done when" × owning skill × references
├── AGENTS.md                 # repo-maintenance guide for agents; CLAUDE.md is one line: @AGENTS.md
├── CONTRIBUTING.md  CHANGELOG.md  RELEASING.md  CITATION.cff  LICENSE
├── .github/
│   ├── ISSUE_TEMPLATE/       # sprint-feedback.yml, bug.yml, config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/            # validate.yml (every PR), evals.yml (dispatch/label), release.yml (tags)
├── .claude-plugin/marketplace.json   # optional: exposes each skill (and data-project's procedures) as a plugin
├── shared/                   # SOURCE OF TRUTH for content vendored into both skills
│   ├── OUTLINE.md            # vendored copy of the root guide's machine-readable core
│   ├── outline.yaml          # section manifest: every reference/template → exactly one section
│   ├── references/           # values-and-gates, responsible-data, governance, standards-and-fair,
│   │                         # quality-and-bulletproofing, practice-sources
│   └── templates/            # README/AGENTS cores, data-dictionary, gitignore, gitattributes, CITATION, ROADMAP
├── skills/
│   ├── data-liberation/      # SKILL.md, references/ (incl. vendored _shared/), templates/project/
│   └── data-project/         # SKILL.md, references/ (incl. procedures/), templates/
├── tools/                    # validate.py, vendor.py, build_zips.py — CI only, never installed
├── evals/
│   ├── data-liberation/      # trigger queries + behavior cases
│   └── data-project/
└── history/                  # archived retros and plans from both predecessor repos (this file moves here)
```

Vendored copies land under each skill's `references/_shared/` and `templates/_shared/` with a header line (`<!-- vendored from shared/…; edit there, run tools/vendor.py -->`). `tools/validate.py` hashes `shared/**` against every copy and fails with the exact command to run.

---

## 3. The Outline (the front door)

One page that a newcomer, human or agent, reads first. Each section states an outcome, a "done when" test anyone can check, which skill leads, and what gets generated only if that section is in scope. The same ten names are the feedback form's dropdown, the project's ROADMAP rows and the `section:*` labels on project issues, so onboarding, tracking and feedback share one map.

| # | Section | Done when… | Leads | Generated only if in scope |
|---|---|---|---|---|
| 1 | **Scope & gate** | The question, unit of observation, sources, partners and beneficiaries are written down; sensitivity tier, privacy-law screen and CARE check are decided; "what we won't liberate or publish" is stated; deferred outcomes are listed | data-project (data-liberation for one-shot) | README "What & why"; GOVERNANCE stub only if sensitive |
| 2 | **Acquire** | Every source's original is fetched reproducibly, hashed, licensed and has a provenance row; access path (download, API, FOIA, snapshot cadence for ephemeral sources) is recorded | data-liberation | `scripts/{sources,config,fetch,discover}.py` |
| 3 | **Extract** | Rows out reconcile with the source on a spot-check and on its own totals; every value traces to page and region; failures land in a per-run error log, never silence | data-liberation | the CSV (one-shot) or parser modules |
| 4 | **Model & tidy** | The tidy long table validates against the schema contract; the dictionary covers every column (units, missingness); multi-source concepts carry caveats | data-liberation | `schema.py`, data dictionary, `concepts.yaml` (multi-source only) |
| 5 | **Pipeline & audit** | A clean clone regenerates `data/processed/` with one command; CI runs tests and audit; reconcile passes or mismatches are documented; pre-release bulletproofing is done | data-liberation | pipeline, tests, CI, `reconcile.py`, one pre-release checklist |
| 6 | **Document & cite** | A newcomer can load and correctly interpret the data from the README alone; citation and license are clear; decisions are recorded | both | CITATION.cff, LICENSE, methodology, data card (if publishing) |
| 7 | **Govern & collaborate** | Who may touch what is decided and named; a correction path exists; the affordance↔duty coupling is satisfied | data-project | GOVERNANCE, CHARTER, CODEOWNERS, CONTRIBUTING, DMP (only with collaborators or sensitive data) |
| 8 | **Publish** | A stranger can query or read it on the chosen surface; FAIR self-check and accessibility check are done for public outputs | data-liberation | Datasette/Quarto/LFS/DocumentCloud files, FAIR and accessibility checklists |
| 9 | **Deposit, share & discover** | A DOI is minted (or a reviewed draft exists); partner access is declared under the access tiers; agent discovery is published if intended | data-project | Dataverse kit, OpenSharing kit, ARD catalog, OKF bundle |
| 10 | **Maintain & feedback** | Refresh runs on its cadence with PR review; work is tracked in issues; each sprint's retro is filed to `data-skills` against these sections | both | refresh workflow, issue forms, seed script |

**What replaces the ladder's useful parts.** Right-sizing survives as an explicit "now / later / skip" choice per section, recorded in ROADMAP as **deferred outcomes** with blocking rows, which projects found genuinely useful. The sensitivity coupling survives as a gate in section 1 that forces section 7's minimum safeguards regardless of how little else is in scope. The anti-bloat rule ("say what you are *not* generating and why") becomes a SKILL.md rule.

**How each skill uses it.** Each SKILL.md opens with a one-screen router: identify which sections the request touches, read only that section's references, check its "done when" test before claiming completion. `data-liberation`'s "just the CSV" path is sections 3–4 with nothing generated; `data-project`'s "start a collaboration" path is section 1 first, then issues for the in-scope sections.

---

## 4. Onboarding flow for a new project

1. **Scope conversation** (the former `data-project-interviewer`, now `references/procedures/scope.md`) produces the README "What & why," the sensitivity decision and a now/later/skip choice for each of the ten sections.
2. **Five files plus issues.** The scaffold writes README, AGENTS.md (with `CLAUDE.md` = `@AGENTS.md`), ROADMAP (the ten sections, now/later/skip, linked to issues), decision-log and CHANGELOG, and opens **one issue per "now" section** whose body is that section's "done when" test as a task list. GitHub is the working surface.
3. **Artifacts on arrival.** When work on a section starts, the agent generates that section's artifacts, and only those. Checklists are offered as issue task lists first and as files only when they must ship with a release or deposit.
4. **AGENTS.md stays short.** It points at the Outline, the five files and the open section issues, plus dated project rules (one project's 60-line AGENTS.md of dated rules is the model). Nested `.skills/` are cut; their content folds into AGENTS.md task notes.
5. **Sprint end.** AGENTS.md carries one instruction: run an after-action review and file it with the `data-skills` sprint-feedback form (a prefilled link).

---

## 5. The feedback loop

**Intake.** `.github/ISSUE_TEMPLATE/sprint-feedback.yml` on `data-skills`:

- dropdown **skill**: data-liberation / data-project / both / not sure
- dropdown **outline section** (multiple): the ten sections, plus "the Outline or onboarding itself"
- dropdown **harness**: Claude Code / claude.ai / Cowork / other agent
- input **project**: repo URL, or "private (process lessons only)"
- textarea **outcome attempted** and **the "done when" test that failed or was unclear**
- textarea **what happened** (facts first), **what you did instead** (local fixes are the most valuable signal), **files or commands involved**
- dropdown **severity**: blocked / cost rework / friction / suggestion
- checkbox: "I removed sensitive data, names and record details"

A companion `bug.yml` covers defects in templates or scripts. `config.yml` disables blank issues and links CONTRIBUTING.

**Triage.** Labels `skill:*`, `section:*`, `cause:missing|ambiguous|contradictory|buried|novel` (the root-cause taxonomy the AARs already use), and `status:needs-repro|accepted|wontfix`. "Novel" one-offs default to no rule change, to avoid over-fitting. CONTRIBUTING documents the rule that an accepted finding is fixed in the file that the section manifest says owns it, and `tools/validate.py` enforces that every reference and template is owned by exactly one section.

**Cadence.** After each sprint: file the feedback. Batch triage before each release; the release notes list the issues closed per section, so the project that filed a finding can see where it went.

**Seed backlog.** On day one, file as issues: every unexecuted work stream from `data-liberation`'s revision plan, the `data-project` 0.10.0 liberation notes, and the recurring frictions from the nine-repo review (section 11), each labeled by section and cause.

---

## 6. Content refresh

### Shared (`shared/references/`, vendored into both)

| New file | Absorbs | Protected substance |
|---|---|---|
| `values-and-gates.md` | DP `context.md`, DP `installed-base.md`, the gates from DL `context.md` | values spine: three pressures/counter-values, six installed-base elements, minimum-viable-safeguards coupling |
| `responsible-data.md` | DP `responsible-data-handbook.md`, responsible-data checklist | yes |
| `governance.md` | DL `project-template.md` governance section, DP governance text | — |
| `standards-and-fair.md` | DP `fair-maturity.md`, DL `context.md` Part 2 | — |
| `quality-and-bulletproofing.md` | bulletproofing + data-quality checklists, Quartz/ProPublica bulletproofing | — |
| `practice-sources.md` | Turing Way, USDS, ProPublica, Cookiecutter, Quartz, OUHSC, Data Cards, Data Collaboratives Canvas, Snakemake digests | yes: each source keeps its own section, tagged with the Outline sections it informs |

### `data-project`

- SKILL.md rewritten around the Outline router; under 5k tokens with the hard rules first; spec-valid frontmatter (drop `argument-hint`; `metadata.version`); description sharpened to "collaboration, governance, deposit, sharing, discovery" and explicitly deferring extraction and dictionaries-for-a-single-extract to `data-liberation`.
- Agents: `interviewer` → `references/procedures/scope.md`; `tracker` → `procedures/tracking.md` (labels move from `level:*` to `section:*`); `depositor` → `procedures/deposit.md`; `indexer` and `synthesizer` are cut (they only chose artifacts by level). The marketplace extra can still expose the procedures as Claude Code subagents.
- `${CLAUDE_PLUGIN_ROOT}` references → `${CLAUDE_SKILL_DIR}` (or relative paths); nested-skill templates cut; `.skills/` paths gone.
- Kits stay (protected): Dataverse, OpenSharing, OKF, ARD. Deposit kit paths fixed for `data-liberation`-shaped projects; ARD version text matches the template's `specVersion`.
- `landing-a-pipeline.md` + `stamping-and-shared-core.md` → one `multi-pipeline.md`, rewritten for `data-liberation`-shaped pipelines with a `pipelines/_core/` shared package (as one project already did); pipeline CI discovers `pipelines/*/pyproject.toml`.
- Template cuts and merges per the audit: environment.yml and DP pyproject (use DL's), NEXT-STEPS (into ROADMAP), codemeta (only when releasing a package), wiki seeds, two canvases merged into one Scope canvas, `{{YEAR}}-01-01` fake dates removed.

### `data-liberation`

- SKILL.md rewritten around the Outline router; description cut under 1,024 characters and disambiguated from `data-project`; levels table removed; first 5k tokens carry the non-negotiables (immutable originals with checksums, provenance, tidy-long, caveats, probe then extract).
- Debt repaired: about 20 pointers to reference files retired in 0.4.0; the documented first command (`python -m scripts.pipeline` needs `run`); documented-but-missing features (reject file, cleaning log, `validators.py`, `_normalize.py`, data-correction issue form): implement the cheap ones, delete the claims for the rest; refresh workflow commits audit files that `.gitignore` excludes; section 8 publishing files generated only when publishing is in scope.
- Absorb project fixes: fresh-per-run error log, `--fresh` refetch, progress reporting, dedup-before-validate, entity seeds, `nbstripout`, stable sample keys.
- New coverage: `extract-api.md` (REST, BI dashboards, ArcGIS FeatureServer layers) and an "ephemeral sources" section in Acquire (snapshot cadence, gap detection, never-backfillable warnings).
- Every reference over 100 lines gets a table of contents; chains of references are flattened to one level from SKILL.md; `extraction_quality` vocabulary unified between `data-modeling.md` and `extract-images.md`; per-row `extracted_at` contradiction resolved in favor of per-extract provenance.

### Generated projects (both skills)

- Emit `AGENTS.md` with a one-line `CLAUDE.md` (`@AGENTS.md`); Claude Code reads AGENTS.md natively as of September 2026.
- One canonical project shape (DL's): uv + `pyproject.toml`, Python `>=3.12` with CI on 3.13, `data/original/` immutable, one shared token set (`PROJECT_SLUG` kebab for the repo, `PKG_NAME` snake for imports).
- Actions on current majors (`checkout@v5`, `setup-python@v6`, current `setup-uv`, `setup-micromamba@v2`, `create-pull-request@v7`); pandera floor raised to the version that provides `pandera.pandas`; camelot advice updated (pdfium backend, no Ghostscript, no `[cv]` extra); one ruff version; dead links fixed (`playbook.cio.gov`, the course link).

---

## 7. Extraction rewrite (`extract-pdf.md`, `extract-documents.md`, `extract-images.md`)

- **Triage every page, not page one:** born-digital text layer, scanned, mixed; tables, forms, multi-page tables.
- **Born-digital first:** the text layer is ground truth. Use pdfplumber/PyMuPDF/camelot for tables; layout pipelines (Docling, Marker, MinerU) when structure is complex. Note that OXR and most VLM parsers rasterize every page and ignore the text layer.
- **Scans and hard layouts:** VLM/end-to-end parsers (OXR, olmOCR, dots.ocr, MonkeyOCR and peers) or hosted APIs, chosen with a table of license, local/GPU needs, outputs, bounding-box granularity, determinism and cost. Benchmark claims are reported with their caveats: most are self-reported, DocParsingBench is published by OXR's own vendor, no benchmark scores page-region provenance, and the "old scans" category closest to FOIA material tops out near 59%.
- **Provenance:** every value cites source hash + page + bounding box, normalized to PDF points with a top-left origin.
- **Audit discipline for model-based extraction:** cache parser output as an immutable, hashed artifact; record a parser manifest (model revision, engine version, sampling settings, render DPI, batch invariance); cross-check against the text layer or a second reader; sample cells for human audit (rule of three: 60 clean cells bounds the error rate near 5%); keep 20–50 hand-keyed golden pages as a regression set.
- **Sensitivity gate:** no hosted upload of documents from a project whose section 1 tier forbids it; record model and API license limits. (SoMark's skills default uploads to an overseas endpoint without saying documents leave the machine, a pattern to avoid.)

**Lessons taken from SoMarkAI's collection:** copy the small router SKILL.md over per-platform adapters, the "parse once, reuse that exact output" rule, the versioned and redacted run manifest that records content loss and stages, output contracts that keep page and block indexes, and "do not use for…" clauses. Avoid what drifted there: a client copy-pasted into nine skills, CI that swallows publish failures, versions not bumped when code changed, duplicated AGENTS.md/CLAUDE.md, promotional over-broad triggers, and "When to trigger" text placed in the body where it can't affect triggering.

---

## 8. Packaging, validation, evals, releases

- **Spec compliance:** `name` equals its directory; description ≤1,024 characters; only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` in frontmatter (no Claude Code-only keys such as `when_to_use`, `context`, `hooks`, `paths`, `argument-hint`); no `SKILL.md` at the repo root or inside `templates/`.
- **One validator** (`tools/validate.py`) merging both: frontmatter and spec limits, also running `agentskills validate` and parsing its output (its exit code is unreliable); tokens and `IF` blocks; `.tmpl` rules; outline-manifest ownership; dead links and retired names across references and templates; vendored-copy drift; issue-form YAML; render both skills' templates with flags on and off and run the `data-liberation` smoke (uv sync, ruff, pytest).
- **CI:** `validate.yml` on every PR with jobs lint, drift, smoke-liberation, smoke-project; a check that any change under `skills/<name>/` bumps that skill's version. `evals.yml` runs on `workflow_dispatch` or a label, never on every push, because each run costs real model calls.
- **Evals** (outside the skill folders, so installs stay clean): per skill, ~20 trigger queries including near-misses between the two skills ("data dictionary" both ways, "make a CSV" vs "start a collaboration"), plus at least three behavior cases each (one-shot CSV, add a vintage, multi-source harmonize; new collaboration with a sensitive source, deposit, file sprint feedback). `data-project`'s existing 11 cases are de-leveled and given graders. Use the `claude plugin eval` format with `--eval-dir` to avoid the `evals/` name clash with skill-creator.
- **Releases:** `release.yml` on `<skill>--v*` tags builds `<skill>.zip` (top-level folder = skill name), runs `unzip -l` checks and attaches it to the GitHub release for claude.ai org upload. Optional: a small private marketplace repo pointing at `data-skills` enables claude.ai org auto-sync, which only works from private repos.
- **Duplicate listings:** document that a skill installed both as a claude.ai org skill (`anthropic-skills:<name>`) and locally appears twice and competes for triggers; pick one per machine.
- **History:** one root CITATION.cff for `data-skills` crediting both predecessors; one CHANGELOG with "Pre-monorepo history" for each skill (backfilling `data-liberation` 0.2–0.4 from commits); tags `data-project--v0.10.0` and `data-liberation--v0.4.0` on the imported history for provenance.

---

## 9. Migration sequence (one PR each, CI green at every step)

| PR | Scope | Acceptance |
|---|---|---|
| 1 | This plan | Maintainer approves or amends decisions D1–D10 |
| 2 | **Restructure only.** Move this repo's skill into `skills/data-project/`; `git subtree add` `data-liberation-skill` into `skills/data-liberation/`; lift repo-maintenance files (CI, evals, CONTRIBUTING, CHANGELOGs, retros, validators) to the root; no content changes | Both skills install via `npx skills add <branch> --list`; both old validators pass from their new paths |
| 3 | **Shared core and validator.** `shared/`, `tools/vendor.py`, unified `tools/validate.py`, unified `validate.yml`; spec fixes (description length, `argument-hint`) | Drift check fails on a hand-edited copy and passes after `vendor.py`; `agentskills validate` clean for both skills |
| 4 | **Outline and SKILL.md rewrites.** `OUTLINE.md`, `shared/outline.yaml`, both SKILL.md files rebuilt as routers, ladders removed, artifact generation gated by section, agents converted to procedures | Every reference and template owned by exactly one section; both SKILL.md bodies under ~5k tokens |
| 5 | **Seam and debt.** One project shape, multi-pipeline CI on `pyproject.toml`, deposit-kit paths, token unification, `data-liberation` debt and absorbed project fixes, tooling updates, reference consolidation | Rendering a multi-pipeline `data-project` with two `data-liberation` pipelines runs both pipelines' tests in CI |
| 6 | **Extraction and new coverage.** Rewritten extract references, `extract-api.md`, ephemeral sources | Every tool claim carries a dated source; stale items from the landscape survey resolved |
| 7 | **Feedback intake.** Issue forms, labels, CONTRIBUTING triage rules, seeded backlog issues, the sprint-end line in generated AGENTS.md | A test issue filed through the form gets `skill:*`/`section:*` labels; the seeded backlog is visible |
| 8 | **Evals and release.** Eval suites, `evals.yml`, `release.yml`, README install docs, CITATION; tag both skills `--v1.0.0` | Release attaches two zips that upload cleanly to claude.ai |

**Maintainer actions outside PRs:** rename this repo to `data-skills`; archive `data-liberation-skill` and `data-liberation-template` with tombstone READMEs pointing to `data-skills`; close `data-liberation-skill` PR #26 with credit (its proposal is adopted in PR 2); re-upload the two org skills from the 1.0.0 zips.

---

## 10. Open decisions for the maintainer

1. **Code directory name in projects:** `scripts/` (current `data-liberation`, all its projects) or `src/` (current `data-project`). The plan recommends keeping `scripts/` to avoid migrating existing pipelines, and fixing `data-project`'s templates to match.
2. **Snakemake:** drop it, or keep it as an optional wrapper over `pipeline.py` for projects that want it. The plan recommends optional.
3. **R variant:** `data-project` ships R templates. Keep them as a maintained variant or move them to a "community-maintained" note.
4. **Version line:** start both skills at 1.0.0 (recommended, marking the breaking removal of the ladders) or continue 0.11 / 0.5.
5. **Private marketplace repo** for claude.ai org auto-sync: create one, or keep manual zip uploads.

---

## 11. Seed backlog from the project review

Recurring frictions found across the project repos, to be filed as labeled issues in PR 7. A second review pass over six more project repos is in progress; its findings will be merged into this table before approval.

| Friction | Section | Cause | Fix direction |
|---|---|---|---|
| Multi-pipeline CI discovers `Snakefile`, which no `data-liberation` pipeline has, so pipelines go untested | 5 | contradictory | discover `pipelines/*/pyproject.toml` |
| Error log appends across runs, so old failures mask new ones | 3 | missing | fresh per-run error log (as one project's shared core already does) |
| No forced refetch when a cached original is stale | 2 | missing | `--fresh` flag and cache-invalidation rule |
| Duplicates fail validation before they can be dropped | 4 | missing | dedup before validate |
| APIs, BI dashboards and ArcGIS layers have no guidance | 2–3 | missing | `extract-api.md` |
| Ephemeral sources (current-day only) lose missed scrapes for good | 2 | novel → recurring | snapshot cadence and gap detection |
| Seeded audit samples change when an agency renumbers records | 5 | missing | sample on a stable key |
| Governance docs and checklists generated and never maintained | 7 | contradictory (lean-by-default vs level bundles) | generate per section on arrival; checklists as issue task lists |
| Decisions made in issues never reach the documented source of truth | 6, 10 | buried | issues are the working surface; decision-log entries link issues |
| Controlled vocabularies in lookup files edited without enforcement | 4 | missing | test that lookup values match the dictionary |
| Five documents each partly answer "where do I start?" | Outline | missing | `OUTLINE.md` front door; short AGENTS.md |
| `data-liberation` revision plan work streams never executed | all | buried (no intake) | file each work stream as an issue |

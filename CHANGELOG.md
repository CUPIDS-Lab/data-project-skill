# Changelog

All notable changes to the `data-project` skill are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/); the skill aims at semantic versioning.

## [0.7.0] — 2026-06-23

Revisions from the **second** real build's after-action report (Colorado Environmental Data Hub), which exercised the skill across **four** `data-liberation` pipelines in one repo. The `pipelines/<name>/` monorepo layout has existed since 0.4.0 but was never made *operational* — every new friction clustered at that seam. This release closes it, opt-in and lean-by-default.

### Added
- **Auto-discovered multi-pipeline CI.** New `templates/ci/pipelines-ci.yml.tmpl`: a `discover` job globs `pipelines/*/Snakefile` into a JSON array and a `test` job fans out over it via a build matrix (`fail-fast: false`), so adding a pipeline needs **no** workflow edit — with a documented static-matrix fallback ("land the matrix row in the same PR as the directory"). New `PIPELINES` flag (multi-pipeline monorepo; distinct from the singular `PIPELINE`), documented in `SKILL.md` and guarded by `scripts/validate.py`; emitted **instead of** the single-project `github-actions-ci.yml`. The scheduled `dataverse-deposit.yml` rebuilds every pipeline before its one versioned deposit when `PIPELINES` is set.
- **First-class "land a pipeline" sub-flow.** New `references/landing-a-pipeline.md`: the ordered procedure (isolated worktree → scaffold a self-contained `pipelines/<name>/` → auto-discovered CI → repo-doc registration → one PR `Add <name> pipeline (#NN)` with `Closes #NN` → green → merge → verify `origin`), a **registration checklist** naming every surface a landed pipeline must update, and a `<!-- data-project:pipeline=<name> -->` marker convention.
- **Shared-core stance.** New `references/stamping-and-shared-core.md`: when (~3 pipelines) and how to factor domain-agnostic plumbing into a shared core (`src/<pkg>/` or `pipelines/_core/`) versus keep domain logic per pipeline, and how to **stamp a sibling** instead of copy-pasting. Wired from `references/context.md`.
- **Two evals** (multi-pipeline CI scaffold; land-a-pipeline) in `evals/evals.json`.

### Changed
- **Multi-agent / shared-working-tree isolation.** `SKILL.md` Guardrails and `references/github.md` now prescribe a **git worktree per agent**, **explicit-path staging (never `git add -A`/`.`)** in a shared dirty tree, and `git fetch` + verify `origin/<default-branch>` before merging or auditing; Audit mode fetches/verifies first; `README.md`'s scaffold example no longer models `git add -A`.
- **Close issues on landing, and reconcile the monorepo.** `data-project-tracker` closes a pipeline/task issue from its merged landing PR (`Closes #N`) rather than a roadmap diff, flags **built-but-open / closed-but-unbuilt** issues, and reconciles `pipelines/*` against the repo's documented pipelines (the marker surfaces), flagging under-registration.
- **Novice-legibility pass finished.** Rewrote the L4 `accessibility-checklist` and `data-dictionary` templates so each item/column is self-contained (what / where / how / pass-vs-fail; allowed-values and missingness-encoding examples) and prompts filling one pass per output / per dataset / per pipeline.
- **Housekeeping.** Corrected the stale framework-digest count in `references/INDEX.md` (~14 → ~15) and wired the two new references into INDEX §B/§C, `SKILL.md`'s reference map + "what's built", and `templates/directory-tree.md` (per-pipeline `environment.yml` + landing/shared-core pointers).

## [0.6.1] — 2026-06-22

### Changed
- **Consolidated the `references/` corpus (23 → 20 digests).** Merged the two same-source clusters into multi-section digests: the git/GitHub code-review and project-management digests → `references/github.md`, and the three ProPublica guides (collaborative · contributed-data · bulletproofing) → `references/propublica.md`. Repointed every citation (INDEX §A/§B, `SKILL.md`, the `data-project-tracker` binding, README "draws on") and normalized the `quartz-bad-data-guide` heading. No content was dropped — each merged source survives as a labelled section keeping its goal-tagged practices and its own artifact mapping.
- **Validator: digests must stay sampleable.** `scripts/validate.py` now checks that every non-spine `references/*.md` is cited as a bare `` `slug` `` in `INDEX.md` — catching an orphaned digest or rename drift (e.g. a merged file whose new slug was never wired in).

## [0.6.0] — 2026-06-22

### Added
- **L5 OpenSharing zero-copy sharing.** New `references/open-sharing-protocol.md` digest and a `templates/opensharing/` kit (`share.json` Share→Schema→Asset declaration, `share-profile.example.json` recipient profile, `SHARING.md` serve/consume guide). When the `OPENSHARING` flag is set, the skill maps the project's processed tables (**Table**), file/doc directories (**Volume**), and `.skills/` (**AgentSkill**) onto the [OpenSharing](https://github.com/OpenSharing-IO/OpenSharing) protocol (Linux Foundation; Delta-Sharing-compatible), so the project can be shared across organizations **in place** via temporary, scoped credentials instead of by copying. The skill emits only the declaration — it never runs a sharing server or vends credentials — and what enters a share is gated by the `GOVERNANCE.md` access tiers; the filled recipient profile (which holds a bearer token) is gitignored.
- New `OPENSHARING` flag and `OPENSHARING_ENDPOINT` / `SHARE_STORAGE_BASE` tokens, documented in `SKILL.md` and guarded by `scripts/validate.py` (the JSON-template check already covers `templates/opensharing/`). Wired into `references/INDEX.md` (§A/§B/§C), `references/escalation-levels.md`, `templates/directory-tree.md`, the L4 `data-management-plan`, the L3 `release-and-share` nested skill, the project `AGENTS.md`, and `.gitignore`.

### Changed
- Refreshed `references/okf-open-knowledge-format.md` to position OpenSharing alongside OKF (OKF shares the understanding; OpenSharing shares the assets, and an OKF bundle can itself be shared as a Volume), and updated the top-level `AGENTS.md` to describe the L5 publish/share surfaces and the current agent roster.
- Audit pass: bumped the scaffold's `ruff-pre-commit` pin (`v0.6.9` → `v0.15.18`), annotated the now-archived Data Cards Playbook code repo, and named OpenSharing as the fourth L5 surface in the Dataverse and ARD digests.

## [0.5.0] — 2026-06-20

### Added
- **Periodically-updated ("streaming") Dataverse deposits.** A menu option (an interview cadence question → the `UPDATING` flag) for data refreshed monthly/quarterly/annually. Per the Dataverse data-citation best practices, each refresh is published as a **new version under one DOI** (cited by version + UNF), not a new dataset. New `templates/ci/dataverse-deposit.yml.tmpl` scheduled workflow re-deposits a **draft** new version on the cadence (`DEPOSIT_CRON`), then opens a review issue — it never auto-publishes (minting a version stays a human decision). `dataset.json` gains version/frequency/time-period metadata (`notesText`, `timePeriodCovered`); `DEPOSIT.md` and the L4 `data-management-plan` document the versioning + citation policy. New `UPDATE_FREQUENCY` / `DEPOSIT_CRON` tokens and `UPDATING` flag, wired into `SKILL.md`, the interviewer / synthesizer / depositor agents, `references/dataverse-deposit.md`, `references/INDEX.md`, and `references/escalation-levels.md`.

### Changed
- **Workflow templates may use GitHub Actions `${{ … }}` secrets/inputs.** `scripts/validate.py` and the scaffolded-repo CI token-guard now ignore the `$`-prefixed brace form (only a bare `{{ … }}` is treated as an unfilled skill token), so deposit/CI workflow templates can reference repository secrets.

## [0.4.0] — 2026-06-19

A combined release: the **L5 Harvard Dataverse deposit** capability, plus revisions from the first real build's after-action report (Colorado Environmental Data Hub). GitHub "Track mode" and the external-prerequisite preflight/degradation chain were already in place (`SKILL.md` Track mode + Step 6.5, the `data-project-tracker` agent, `references/github-project-management.md`); the AAR work closes the remaining gaps that build had to improvise, keeping every addition opt-in and lean-by-default.

### Added
- **L5 Harvard Dataverse deposit.** New `references/dataverse-deposit.md` digest, a `templates/dataverse/` kit (`dataset.json` citation manifest, `deposit-dataverse.sh` curl + `deposit_dataverse.py` pyDataverse deposit scripts, `DEPOSIT.md` guide), and a `data-project-depositor` agent. At L5 the skill can archive a project's processed data (category **Data**), code (**Code**), and documentation (**Documentation**) to a Dataverse repository for a citable DOI, mapping project metadata to the Native API citation block. A new **Deposit mode** (`/data-project deposit`) runs the capability chain (pyDataverse → curl → emit-and-hand-off), is idempotent via `.dataverse-deposit.json`, gates sensitive data through `GOVERNANCE.md` access tiers, and stops at a reviewable draft — publishing (which mints the DOI) only on explicit confirmation.
- New `DATAVERSE` flag and `DATAVERSE_URL` / `DATAVERSE_COLLECTION` / `DATASET_SUBJECT` tokens, documented in `SKILL.md` and guarded by `scripts/validate.py` (the JSON-template check now also covers `templates/dataverse/`). Wired into `references/INDEX.md` (§A/§B/§C), `references/escalation-levels.md`, `templates/directory-tree.md`, the L4 `data-management-plan`, and the L3 `release-and-share` nested skill.
- **Notebook hygiene (`NOTEBOOKS` flag).** When a project uses notebooks, the scaffold wires up output-stripping as a git filter: `*.ipynb filter=nbstripout diff=ipynb` in `.gitattributes`, a one-time `nbstripout --install` note in `AGENTS.md`, and `nbstripout` in the conda environment — complementing the existing pre-commit hook so outputs never land in history. Clones without the filter degrade gracefully. Documented in `SKILL.md` and guarded by `scripts/validate.py`.
- **Multi-pipeline monorepo shape.** `templates/directory-tree.md` and `references/context.md` now specify the `data-liberation` hand-off: a `data-project` repo hosts *N* pipelines under `pipelines/<name>/`, each mapped 1:1 to a tracked issue/sub-issue under the umbrella `ROADMAP.md`/board.
- **Conditional ("becomes-sensitive-when") sensitivity.** A first-class disposition for data that is public now but becomes sensitive when a named event occurs: the interviewer captures the trigger, the synthesizer emits it as a **blocking** ROADMAP item gating the sensitive build, and `installed-base.md` / `escalation-levels.md` / `ROADMAP.md.tmpl` document the deferred-but-enforced coupling.
- **Context-rich fast path.** `SKILL.md` and the interviewer now infer the full Project Context Profile from supplied design docs (a `/context/` dump) and present it for confirmation instead of running a cold-start questionnaire; the single human approval gate is unchanged.

### Changed
- **Curated vs. bulk raw data.** The "raw is immutable + git-ignored" convention now distinguishes **bulk/external/re-downloadable** raw (git-ignored) from a small **curated source-of-record** (tracked via a `.gitignore` carve-out, documented immutable). Updated `gitignore.tmpl` (carve-out idiom), `context.md`, `AGENTS.md.tmpl`, `README.md.tmpl`, `directory-tree.md`, the interviewer, and `SKILL.md` Step 6.
- **Resolved `src/` vs `scripts/` divergence.** `src/<pkg>/` is stated as the repo-wide package location; a nested `data-liberation` pipeline's own `scripts/` may stay local to its `pipelines/<name>/`. Aligned `collaboration-architecture.md` and `directory-tree.md`, and corrected the stale `pipelines/Snakefile` reference in `evals.json` to the root single-pipeline default.
- **Guardrails.** `SKILL.md` now recommends branch → PR → merge when scaffolding into a shared repo, and adds a template-authoring rule (instructions written for the newcomer who executes them). `escalation-levels.md` notes that CI first appears at L2+.

## [0.3.0] — 2026-06-18

### Added
- **L5 agent discovery (Agentic Resource Discovery / ARD).** New `references/agentic-resource-discovery.md` digest and `templates/ard/{ai-catalog.json,DISCOVERY.md}.tmpl`: at L5, when a project exposes agentic resources (nested `.skills/`, a published dataset, an MCP/A2A service), the skill emits a repo-scope `ai-catalog.json` manifest advertising them, plus a `DISCOVERY.md` companion documenting the entries and the checklist to promote the catalog to the host `.well-known/` path and an org/ecosystem registry (those higher deployment scopes are deferred to `ROADMAP.md`). Pairs with the OKF bundle as the publish layer.
- New `ARD` flag and `ARD_SPEC_VERSION` / `ARD_HOST_DOMAIN` / `ARD_HOST_IDENTIFIER` tokens, documented in `SKILL.md` and guarded by `scripts/validate.py` — which now also checks that the ARD JSON template stays valid JSON when rendered with conditionals on and off. Wired into `references/INDEX.md` (§A/§B/§C), `references/escalation-levels.md`, `templates/directory-tree.md`, `templates/README.md.tmpl`, and the synthesizer.

## [0.2.1] — 2026-06-17

### Fixed
- Python pipeline correctness: the `Snakefile` now invokes `python -m {{PKG_NAME}}.…` (the installed package) instead of the non-importable `src.{{PKG_NAME}}.…`, and `pip install -e .` is part of setup.
- Standardized the reproducible workflow and its config at the repo root (`Snakefile`, `config.yaml`, `_targets.R`) so the documented `snakemake -n` from the project root resolves the workflow and its `configfile`.
- Added an `R/` source directory to the canonical tree for the R variant (the place `_targets.R` sources its stage functions), and generalized the `PKG_NAME` note for both stacks.
- Aligned the Python version across `environment.yml` and `pyproject.toml`/ruff (3.12).
- README/AGENTS/CONTRIBUTING templates now self-document the `ROADMAP.md` fallback for not-yet-generated governance/collaboration docs, and the contributor environment setup is toolchain-gated (Python or R).
- Standardized `CODEOWNERS` role handles to match `ROLES.md`.
- Removed stale "MVP/roadmap" markers left over from the L0–L2 milestone (eval #3, six reference digests, INDEX wording) now that every template is built.
- Corrected the OKF reference's `resource:` URL, wired the previously-orphaned USDS Playbook digest into the INDEX crosswalk, and clarified the Data Cards license phrasing.

### Added
- Repo-level `CHANGELOG.md`, `CITATION.cff`, and `CONTRIBUTING.md`.
- `scripts/validate.py` and a `validate` GitHub Actions workflow that check OKF `type` frontmatter, template conditional/token consistency, and INDEX path resolution on every change.

## [0.2.0] — 2026-06-17

### Added
- Full **L0–L5** template coverage: the R (renv + targets) variant and CI; the L3 collaboration/governance set (`CONTRIBUTING`, `CODE_OF_CONDUCT`, `ROLES`, `CODEOWNERS`, `GOVERNANCE`, `CHARTER`, `collaboration-protocol`, `contributed-data-intake`) and nested `.skills/`; the L4 responsible-data/QA/accessibility set plus the `INSTALLED-BASE` values spine and a `data-card`; and the L5 OKF knowledge bundle, `LICENSE-NOTE`, and canvases.
- Six remaining reference digests (USDS, ProPublica Bulletproofing/Collaborative/Collaborate, Quartz Bad Data, OKF), completing the 14-framework corpus, plus the Data Cards Playbook.

## [0.1.0] — 2026-06-17

### Added
- Initial release: the `data-project` orchestrator `SKILL.md`; the interviewer, indexer, and synthesizer agents; the L0–L2 templates (structure, documentation, the Python conda + Snakemake stack); the reference corpus and the `INDEX.md` crosswalk; the lean-by-default, graded (L0–L5), right-sized workflow with a `ROADMAP.md` now/later mechanism.

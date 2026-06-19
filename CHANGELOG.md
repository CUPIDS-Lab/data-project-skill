# Changelog

All notable changes to the `data-project` skill are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/); the skill aims at semantic versioning.

## [0.4.0] — 2026-06-19

Revisions from the first real build's after-action report (Colorado Environmental Data Hub). GitHub "Track mode" and the external-prerequisite preflight/degradation chain were already in place (`SKILL.md` Track mode + Step 6.5, the `data-project-tracker` agent, `references/github-project-management.md`); this release closes the remaining gaps that build had to improvise, keeping every addition opt-in and lean-by-default.

### Added
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

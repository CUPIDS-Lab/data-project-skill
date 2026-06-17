# Changelog

All notable changes to the `data-project` skill are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/); the skill aims at semantic versioning.

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

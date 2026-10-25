# AGENTS.md — maintaining the data-skills repository

This repository holds two Agent Skills. It is not itself a skill: never add a `SKILL.md` at the root.

- `skills/data-liberation/` turns documents and messy sources into tidy, provenance-tracked datasets and pipelines.
- `skills/data-project/` scopes, governs, tracks, deposits and shares a public-interest data collaboration.

To *use* a skill, read its `SKILL.md`. This file is for changing the repository.

## Rules

- **Each skill folder is installed as-is** by claude.ai uploads, `npx skills` and manual copies, so it must be self-contained and must not hold repository files (README, CHANGELOG, CI, evals, retros). Those live at the root.
- **Shared content is edited in `shared/` only.** `tools/vendor.py` copies it into each skill at the paths in `shared/vendor.toml`; never edit a vendored copy (it carries a header saying so).
- **Frontmatter stays inside the Agent Skills spec:** only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`; description ≤ 1,024 characters; `metadata.version` in semver. Claude Code-only keys break claude.ai uploads.
- **Any change under `skills/<name>/` bumps that skill's `metadata.version`** and adds a line under that skill in `CHANGELOG.md`.
- **Markdown prose is one line per paragraph** (no hard wraps), in American English.

## Checks

```sh
uv run --no-project --with pyyaml python tools/validate.py            # everything except the smoke test
uv run --no-project --with pyyaml python tools/validate.py --smoke    # also render + test the data-liberation project
python tools/vendor.py                                                # after editing shared/
```

CI runs `tools/validate.py --smoke --spec-tool` on every push and pull request, and the version-bump check on pull requests.

## Where things are

- `shared/` — source of truth for content both skills vendor; `shared/outline.yaml` maps every reference and template to its Outline section.
- `tools/` — `validate.py` (the CI entry point), `vendor.py`, and each skill's template validator.
- `evals/<skill>/` — evaluation cases, kept outside the skill folders so installs stay clean.
- `history/` — the predecessor repositories' changelogs, plans and retrospectives, plus the monorepo plan.

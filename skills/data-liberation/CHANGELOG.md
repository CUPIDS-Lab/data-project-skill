# Changelog

All notable changes to the `data-liberation` skill.

## Unreleased

### Changed
- **Folded the project template into this repo.** The skeleton previously hosted in the separate
  `data-liberation-template` repo (fetched at a pinned SHA by `scripts/scaffold.py`) now ships
  in-repo at `templates/project/`. Scaffolding is **agent-driven** — the agent renders the
  templates per `SKILL.md` and `references/project-template.md`; there is no scaffold CLI.
  Token-bearing files use a `.tmpl` suffix and `{{UPPER_SNAKE}}` slot-fills, matching
  `data-project-skill`.
- **Single-repo release process.** Removed the two-repo lockstep machinery (SHA-pinning,
  `RELEASING.md`'s cross-repo dance, the `dispatch-to-template` / cross-repo `scaffold-e2e`
  workflows). What gets scaffolded is whatever is in `templates/project/` at the released commit.

### Added
- `scripts/validate.py` — lints the bundled templates (documented tokens, balanced `IF` blocks,
  `.tmpl`/token agreement) and renders them to a temp dir; with `--smoke`, runs `uv sync` + ruff +
  pytest on the rendered project so a template edit that breaks the scaffold fails in CI.
- `.github/workflows/validate.yml` — single-repo CI running `validate.py --smoke`.

### Removed
- `scripts/scaffold.py` (replaced by agent-driven rendering + `validate.py`).
- `.github/workflows/scaffold-e2e.yml` and `.github/workflows/dispatch-to-template.yml`.

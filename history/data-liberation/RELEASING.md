# Releasing

`data-liberation` ships as a **single repo**: `SKILL.md`, `references/`, `scripts/`, and the
bundled project template at `templates/project/`. There is no separate template repo and no
cross-repo version pin — what gets scaffolded is whatever is in `templates/project/` at the
released commit, so a release is reproducible by construction.

## Cutting a release

1. Confirm the `validate` workflow is green on `main` (it lints the templates and smoke-tests a
   render: `uv sync` + ruff + pytest on the rendered project).
2. Update `CHANGELOG.md`.
3. Tag and release:
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z — <one-liner>"
   git push origin main vX.Y.Z
   gh release create vX.Y.Z --title "vX.Y.Z — <one-liner>" --notes "…"
   ```

No SHA to keep in sync, no `repository_dispatch` pairing, no lockstep bump.

## Changing the template

Edits under `templates/project/` are ordinary changes in this repo. Before pushing:

```bash
python scripts/validate.py --smoke   # lint + render + uv sync + ruff + pytest
```

CI runs the same on every push and PR via `.github/workflows/validate.yml`.

## Adding a new `{{TOKEN}}`

When a template file needs a new slot-fill:

1. Use `{{NEW_TOKEN}}` (UPPER_SNAKE) where you need it, and give the file a `.tmpl` suffix if it
   doesn't already have one.
2. Add `NEW_TOKEN` to `DOCUMENTED_TOKENS` **and** `RENDER_VALUES` (a test value) in
   `scripts/validate.py`.
3. Add a row to the slot-fill table in `references/project-template.md`.

`validate.py` fails if a token is undocumented, if a `.tmpl` file has no token, or if a
token-bearing file lacks the `.tmpl` suffix.

## Conditional surfaces (`<!-- IF:FLAG -->`)

The render recipe supports `<!-- IF:FLAG -->…<!-- /IF -->` blocks (matching `data-project-skill`).
None are used yet — optional surfaces (`refresh` / `publish` / `gh-pages`) ship as `*.yml.disabled`
for the operator to rename. To gate a surface on a flag instead, wrap it in an `IF` block and add
the flag to `DOCUMENTED_FLAGS` in `validate.py`; the validator checks that blocks are balanced and
that the flags-on and flags-off renders both pass.

## Migrated from a two-repo layout

`data-liberation` previously kept its template in a separate `data-liberation-template` repo,
fetched by a `scripts/scaffold.py` at a pinned SHA. That repo is archived; the template now lives
here under `templates/project/`, rendered agent-driven per `SKILL.md`. See
[`retro/fold-template-into-skill-plan.md`](retro/fold-template-into-skill-plan.md) for the migration
rationale.

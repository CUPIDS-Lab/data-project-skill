# Releasing

Each skill is released on its own version line and tagged `<skill>--v<version>` (for example `data-liberation--v0.5.0`). Releases are cheap; cut one whenever a skill's changes are worth re-uploading to claude.ai.

## Steps

1. **Triage** the open feedback and bug issues for the skill (see `CONTRIBUTING.md`), and make sure every merged fix is under that skill's `[Unreleased]` heading in `CHANGELOG.md`.
2. **Run the evals** for the sections the release touches (`evals/README.md`), and the full set for a minor or major version.
3. **Bump** `metadata.version` in `skills/<skill>/SKILL.md` (patch: fixes and wording; minor: new guidance or templates; major: changes that alter what existing projects must do), and rename that skill's `[Unreleased]` heading in `CHANGELOG.md` to `[<version>] — <YYYY-MM-DD>`, listing the issues it closes.
4. **Validate:** `uv run --no-project --with pyyaml python tools/validate.py --smoke --spec-tool`.
5. **Merge to `main`, then tag** the merge commit: `git tag <skill>--v<version> && git push origin <skill>--v<version>`.
6. The `release` workflow checks that the tag matches `metadata.version`, validates again, builds `<skill>.zip` (top-level folder named after the skill), and attaches it to a GitHub release whose notes are that version's CHANGELOG section.
7. **Update installs:** upload the zip to claude.ai organization skills (replacing the previous version). `npx skills update` users pick up the change automatically.

## Changing shared content

Edit the file under `shared/`, run `python tools/vendor.py`, and commit the source and every copy together. A change to shared content is a change to both skills, so bump both versions.

## Adding a slot-fill token or flag

Document it where the skill's templates are documented (`data-project`: `references/procedures/scaffold.md`; `data-liberation`: `references/project-template.md`) and in that skill's validator (`tools/validate_<skill>.py`), in the same PR.

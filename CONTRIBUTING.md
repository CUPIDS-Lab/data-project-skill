# Contributing to data-skills

Thanks for improving these skills. They are plain Markdown, templates and a few scripts, so contributing is mostly writing clear guidance and keeping the two skills consistent. Read [`OUTLINE.md`](OUTLINE.md) first: every reference, template and piece of feedback belongs to one of its ten sections.

## Feedback and triage

Most improvements start as **sprint feedback** from a project that used the skills. File it with the [sprint-feedback form](https://github.com/CUPIDS-Lab/data-skills/issues/new?template=sprint-feedback.yml), one issue per distinct gap; broken templates or scripts go to the [bug form](https://github.com/CUPIDS-Lab/data-skills/issues/new?template=bug.yml). Private projects report process lessons only.

When an issue arrives, the `triage` workflow labels it from the form (`skill:*`, `section:*`, `cause:*`, `severity:*`). A maintainer then:

1. **Checks it isn't already covered.** Before treating a gap as *missing*, search the skill for guidance that exists but wasn't followed; that is *ambiguous* or *buried*, and the fix is to sharpen or move it, not to add a second copy.
2. **Decides** `status:accepted`, `status:needs-repro` or `status:wontfix`. A *novel* one-off usually changes nothing: a rule that helps one project and burdens every other makes the skill worse.
3. **Fixes accepted findings in the owning file**, which is the file the Outline section points to, and in `shared/` when the content is shared. The PR closes the issue and adds a CHANGELOG line under the affected skill.

Before each release, triage everything open; the release notes list the issues closed per section, so the project that filed a finding can see where it went.

## Conventions

- **Each skill folder is installed as-is**, so it must be self-contained and hold no repository files (README, CHANGELOG, CI, evals). Those live at the root; `tools/validate.py` enforces it.
- **Shared content is edited in `shared/` only**, then copied into each skill with `python tools/vendor.py`. Never edit a vendored copy.
- **Frontmatter stays inside the Agent Skills spec** (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`; description ≤ 1,024 characters).
- **Prose is one line per paragraph** (no hard wraps), in American English. Write for the person who has to act on it: what to do, where, and what success looks like. Explain why rather than stacking "always" and "never."
- **Outcomes over artifacts.** Prefer sharpening a section's "done when" test over adding a file the scaffold generates. A new template must belong to one Outline section and be generated only when that section is in scope.

## Adding or changing content

- **A reference:** put it in the skill that leads its Outline section (or `shared/references/` if both skills need it), add it to `shared/outline.yaml`, and link it from that skill's `SKILL.md` reference list. References over 100 lines start with a table of contents; references are read one level deep from `SKILL.md`, so don't make one depend on reading another first. `data-project` references carry OKF frontmatter (`type`, `title`, `description`, `tags`).
- **A template:** use only the documented slot-fills and flags (`data-project`: `references/procedures/scaffold.md`; `data-liberation`: `references/project-template.md`), give token-bearing files a `.tmpl` suffix, and add it to `shared/outline.yaml`.
- **A version bump:** any change under `skills/<name>/` bumps that skill's `metadata.version` (patch for fixes and wording, minor for new guidance or templates, major for changes that alter what existing projects must do) and adds a CHANGELOG line.

## Before you open a PR

```sh
uv run --no-project --with pyyaml python tools/validate.py --smoke
```

CI runs the same checks plus the official spec validator, and on pull requests requires a version bump for every changed skill. For behavior changes, run the relevant cases in `evals/<skill>/` (see `evals/README.md`) and say in the PR which you ran.

Pull request bodies use four headings: **What changed**, **Why** (link the feedback issue), **What I checked**, **Left alone on purpose**.

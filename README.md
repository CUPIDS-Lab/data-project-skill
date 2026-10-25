# data-skills

Two [Agent Skills](https://agentskills.io) from CUPIDS, the University of Colorado Public Interest Data Science Lab, for turning public documents into trustworthy, reusable data and running the collaborations around it.

| Skill | Use it to | Leads Outline sections |
| --- | --- | --- |
| [`data-liberation`](skills/data-liberation/SKILL.md) | get tables out of PDFs, scans, spreadsheets, web pages, APIs and dashboards; model them as tidy, documented data; build a re-runnable, audited pipeline; publish it | 2 Acquire, 3 Extract, 4 Model & tidy, 5 Pipeline & audit, 8 Publish |
| [`data-project`](skills/data-project/SKILL.md) | scope a data collaboration, decide sensitivity and visibility, govern who may touch what, track the work, deposit it for a DOI, share it, make it discoverable, and file sprint feedback | 1 Scope & gate, 7 Govern & collaborate, 9 Deposit, share & discover |

Both skills share sections 6 (Document & cite) and 10 (Maintain & feedback). You don't have to choose: install both, describe what you want, and the right one loads.

## Start here: the Outline

[`OUTLINE.md`](OUTLINE.md) is the one map for everything: ten sections from scoping a question to maintaining a dataset, each with an outcome and a **done when** test anyone can check. Projects track themselves in a `ROADMAP.md` with one row per section, marked now, later or skip. The same section numbers label issues and sprint feedback, so onboarding, tracking and feedback all use one map.

Common starting points:

- **"Get the table out of this PDF."** `data-liberation` extracts it, reconciles it against the printed totals, and gives you a CSV. Nothing else is created.
- **"Make this re-runnable."** `data-liberation` scaffolds a small project (five working files plus the pipeline) and verifies it runs.
- **"We're starting a data collaboration."** `data-project` asks a few scoping questions, proposes what to create now and what to defer, and waits for your approval.
- **"We finished a sprint."** `data-project` helps you write an after-action review and file it as feedback (below).

## Install

Pick one per machine. If the same skill is installed twice (for example as a claude.ai organization skill and again locally), it appears twice and the copies compete.

- **claude.ai (organization skills):** download `data-liberation.zip` and `data-project.zip` from the latest [release](https://github.com/CUPIDS-Lab/data-skills/releases) and upload each under organization skills. Re-upload when a new release comes out.
- **Any agent, via [`npx skills`](https://github.com/vercel-labs/skills):** `npx skills add CUPIDS-Lab/data-skills` installs both; add `--skill data-liberation` for one. `npx skills update` picks up changes per skill.
- **Manual copy:** clone this repository and copy (or symlink) `skills/data-liberation/` and `skills/data-project/` into your agent's skills folder, for example `~/.claude/skills/`. Copy the skill folders, not the repository root.

## Feedback

At the end of each sprint, file what you learned with the [sprint-feedback form](https://github.com/CUPIDS-Lab/data-skills/issues/new?template=sprint-feedback.yml), one issue per gap, against the Outline section where the guidance failed. Private projects report process lessons only. [`CONTRIBUTING.md`](CONTRIBUTING.md) explains how feedback is triaged and fixed.

## Repository layout

```
OUTLINE.md            the ten-section map (vendored from shared/OUTLINE.md)
skills/<name>/        each skill, exactly as it is installed
shared/               content both skills need, vendored into each by tools/vendor.py
tools/                validate.py (the CI gate), vendor.py, build_zips.py, per-skill template validators
evals/<name>/         behavior and trigger evaluations, outside the installed folders
history/              the predecessor repositories' changelogs, plans and retrospectives
```

This repository merges the former `CUPIDS-Lab/data-project-skill` and `CUPIDS-Lab/data-liberation-skill` (which had already absorbed `data-liberation-template`); their history is preserved here. See [`history/2026-10-25-data-skills-monorepo-plan.md`](history/2026-10-25-data-skills-monorepo-plan.md) for why.

## License

MIT. `data-project` is © the University of Colorado Public Interest Data Science Lab and `data-liberation` is © Brian C. Keegan; each skill folder carries its own `LICENSE`.

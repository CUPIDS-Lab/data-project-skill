---
type: Reference
title: Git/GitHub for Collaborative Data Science
description: A concrete git and GitHub collaboration workflow for data teams — branching, pull requests, commit hygiene, data-aware ignores, large/sensitive-data handling, and CI.
resource: https://arounddatascience.com/blog/coding/how-to-use-github-and-git-for-collaborative-data-science-projects-a-complete-guide-for-algerian-data-scientists/
tags: [collaborative, reproducible, transparent, git]
---

# Git/GitHub for Collaborative Data Science

A practical end-to-end guide to using git and GitHub on data-science teams. Source: https://arounddatascience.com/blog/coding/how-to-use-github-and-git-for-collaborative-data-science-projects-a-complete-guide-for-algerian-data-scientists/

## In one paragraph

This guide translates general git collaboration into data-science specifics: descriptive branches, pull requests with real descriptions, commit messages that explain *why*, data-aware `.gitignore`/LFS so datasets never bloat history, and CI that lints and validates before human review. It is the operational backbone for the "collaborative" goal at L2–L3.

## Key practices (sampleable units)

- **Feature-branch workflow** [collaborative] — branch per unit of work with descriptive prefixes (`feature/…`, `bugfix/…`, `experiment/…`); merge back via PR; delete on merge. Git-flow or trunk-based for larger teams.
- **Pull requests with substance** [collaborative, transparent] — state the problem, the approach, and expected outcomes; link issues with `Closes #N`; reviewers check methodology and assumptions, not just style; balance critique with recognition.
- **Commit messages explain why** [documented, transparent] — imperative subject; body explains the analytical decision, not just the diff.
- **Data-aware ignore + LFS** [reproducible] — ignore `data/raw`, large binaries, secrets, notebook checkpoints; large datasets go to external storage or Git LFS, never directly into history.
- **Clear notebook outputs before committing** [reproducible] — strip outputs to reduce diff noise; ensure top-to-bottom execution.
- **CI on pull request** [reproducible, transparent] — automate linting, tests, and data validation before review.

## Artifacts it implies

- Ignore + attributes → `templates/gitignore.tmpl`, `templates/gitattributes.tmpl`.
- Workflow + review norms → `templates/CONTRIBUTING.md.tmpl` (roadmap).
- CI → `templates/ci/github-actions-ci.yml.tmpl` (roadmap).

## When most relevant

Any multi-person project; whenever the user mentions collaborators, pull requests, review, or "how do we work together." L2 (CI) and L3 (workflow norms).

## Caveats / conflicts

Open-source patterns were built for code, not data — treat them as good-enough, not ideal, and pair them with data-specific practices (pipeline-as-code as the shared artifact, immutable raw data). See `collaboration-architecture.md` anti-patterns.

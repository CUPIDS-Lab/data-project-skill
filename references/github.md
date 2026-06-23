---
type: Reference
title: Git & GitHub for Collaborative Data Science
description: The git/GitHub backbone for data teams — the code-review loop (branches, pull requests, commit hygiene, data-aware ignores, CI) and work planning/tracking (issues, Projects, wikis), plus the exact access/scopes an automating agent needs and the capability-degradation chain.
resource: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects
tags: [collaborative, documented, transparent, reproducible, git, github, project-management]
---

# Git & GitHub for Collaborative Data Science

The two halves of working together on GitHub: the **code-review loop** (how changes get made and merged) and **work planning/tracking** (how tasks get assigned and shipped). Sources: a practical [git/GitHub-for-data-science guide](https://arounddatascience.com/blog/coding/how-to-use-github-and-git-for-collaborative-data-science-projects-a-complete-guide-for-algerian-data-scientists/); GitHub's [Best practices for Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects), the [Planning & tracking with Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects) and [Wikis](https://docs.github.com/en/communities/documenting-your-project-with-wikis) docs, and the GitHub blog on [standardizing workflows with Projects](https://github.blog/developer-skills/github/how-were-using-github-projects-to-standardize-our-workflows-and-stay-aligned/) and [lesser-known Projects features](https://github.blog/developer-skills/github/insider-newsletter-digest-4-things-you-didnt-know-you-could-do-with-github-projects/).

## In one paragraph

The code-review loop translates general git collaboration into data-science specifics: descriptive branches, pull requests with real descriptions, commit messages that explain *why*, data-aware `.gitignore`/LFS so datasets never bloat history, and CI that lints and validates before human review — the operational backbone for the "collaborative" goal at L2–L3. The planning loop is what the tracker and seed script read: the skill's `ROADMAP.md` checklist and `NEXT-STEPS.md` memo are the portable, always-present record of an engagement's work, and GitHub is the *shared, assignable projection* of that record — issues, Projects, and wikis — with the access/scopes that make automation possible (and the one gotcha that breaks it) and a deterministic mapping from a roadmap TODO to a GitHub issue and Project field. The Markdown stays the source of truth; GitHub never becomes the only copy.

## Key practices (sampleable units)

**Code-review loop**

- **Feature-branch workflow** [collaborative] — branch per unit of work with descriptive prefixes (`feature/…`, `bugfix/…`, `experiment/…`); merge back via PR; delete on merge. Git-flow or trunk-based for larger teams.
- **Worktree isolation for concurrent agents** [collaborative, reproducible] — when several agents (or people) work the same repo at once, give each its own **git worktree** (`git worktree add ../wt-<task> <branch>`) so they are not staging into one shared checkout; **stage explicit paths — never `git add -A` or `git add .`** in a dirty shared tree, since an indiscriminate add sweeps another worker's in-progress untracked files into your commit; and `git fetch` + confirm you are level with `origin/<default-branch>` **before you merge or audit**, so a stale checkout never drives a false "missing file" conclusion.
- **Pull requests with substance** [collaborative, transparent] — state the problem, the approach, and expected outcomes; link issues with `Closes #N`; reviewers check methodology and assumptions, not just style; balance critique with recognition.
- **Commit messages explain why** [documented, transparent] — imperative subject; body explains the analytical decision, not just the diff.
- **Data-aware ignore + LFS** [reproducible] — ignore `data/raw`, large binaries, secrets, notebook checkpoints; large datasets go to external storage or Git LFS, never directly into history.
- **Clear notebook outputs before committing** [reproducible] — strip outputs to reduce diff noise; ensure top-to-bottom execution.
- **CI on pull request** [reproducible, transparent] — automate linting, tests, and data validation before review.

**Plan & track work**

- **Issues are the unit of work** [collaborative, documented] — one issue per task; standardize creation with **issue forms** (`.github/ISSUE_TEMPLATE/*.yml` + `config.yml`); use labels, **milestones** (one per level/release), assignees, and task lists; model breakdown and blockers with **sub-issues** and **issue dependencies** (blocked-by/blocking), not a label alone; link issues↔PRs with `Closes #N`.
- **Landing a pipeline = one issue-closing PR** [collaborative, reproducible] — in a multi-pipeline monorepo, add each `pipelines/<name>/` in a single PR titled `Add <name> pipeline (#NN)` with `Closes #NN`, carrying the directory + its CI matrix row (only if the matrix is static; the monorepo CI auto-discovers) + the repo-doc registration, and **nothing else** — never bundle a pipeline into a docs/governance PR. Close the issue from the merged PR (not from a roadmap edit), and reconcile the documented pipelines against `pipelines/*` so the repo never undercounts itself. Full procedure + registration checklist: `references/landing-a-pipeline.md`.
- **Projects plan *and* track** [collaborative, transparent] — adaptable **Board / Table / Roadmap** views over issues, PRs, and draft issues, with custom fields (**Status**; **Priority** single-select; **Iteration** for week-by-week cadence, breaks, and velocity; **number** for size/estimate; **date** for target ship); group/filter/sort/slice and limit columns; **built-in workflows** (auto-add matching repo items, set Status→Done when an issue closes, auto-archive) plus GitHub Actions / GraphQL API; post **status updates** (On track / At risk + start/target dates + context); generate **charts/insights**.
- **Standardize with templates** [collaborative] — save a Project as an **org template** ("Make template" → "Use this template") carrying preconfigured views, fields, and workflows; standardize field *definitions* across teams; recommend org-wide while allowing per-team tweaks.
- **Single source of truth** [transparent, documented] — track each value in exactly one place and let Projects **auto-sync** assignees, labels, and milestones from the issues; don't duplicate metadata across fields (avoid drift). The skill's manifest stores only the task-id↔issue mapping + a content hash — never values Projects already syncs.
- **Wikis for long-form docs** [documented, accessible] — a wiki is a **separate git repo** (`<repo>.wiki.git`) with a **Home** page and a custom **`_Sidebar`/`_Footer`**; use it for narrative/how-to that outgrows the README; by default only repo collaborators can edit, and a wiki can be disabled.
- **Power-user tips** [collaborative] — manage/automate from the CLI with `gh project`; bulk-edit on the table view (set one cell, copy, paste across a selection); add issues from any org by pasting issue links / searching with `#`.

## Capability & degradation chain (what the tracker does)

GitHub remote present? → `gh auth status` + required scopes? → Project-create permission? Land at the richest available tier; never fail the scaffold.
- **A — Issues + Project:** labels + per-level milestone + one issue per TODO, added to a Project with standardized fields/views/workflows and a status update.
- **B — Issues + milestones + labels** (no Project permission).
- **C — Seed script + paste-able list:** write `.github/seed-github.sh` (unrun) + `.github/engagement-issues.md`; tell the user the one command to finish later.
- **D — Markdown only (always written first):** the `ROADMAP.md` assignable checklist + `NEXT-STEPS.md` memo — works off GitHub entirely.
- **E — Wiki (opt-in, L4):** seed `Home`/`_Sidebar`, pushed to `<repo>.wiki.git` when enabled.
An authenticated **GitHub MCP** is an alternate path to A/B when `gh` is absent.

## Access & scopes — make sure the agent can actually do this

- **Repo settings:** enable **Issues**; enable the **Wiki** (Settings → Features) and create its first page *before* any `git push` to `<repo>.wiki.git`; for CI automation set Actions → Workflow permissions = *Read and write* (+ "Allow GitHub Actions to create and approve pull requests").
- **`gh` CLI:** `gh auth login`; add the Projects scope with `gh auth refresh -s project,read:project,repo`; verify with `gh auth status`. A `repo`-scoped classic token can push the wiki.
- **The Projects-v2 gotcha (most common failure):** Projects v2 live at **org/user scope, not repo scope**. A **classic PAT** needs `repo` (issues + wiki) **+ `project`** (+ `workflow` to edit Actions files). A **fine-grained PAT** needs repo **Issues: RW, Contents: RW, Pull requests: RW, Metadata: R**, **plus the organization permission "Projects: Read and write"** for org Projects — and fine-grained PATs **cannot push wikis**, so use a classic PAT or `gh` for wiki edits. A **GitHub App** needs Issues/Contents/Pull-requests RW **and Organization Projects RW**, installed on the repo/org.
- **Actions `GITHUB_TOKEN` limits:** with a `permissions:` block it can open issues/PRs, but it **cannot modify org Projects v2 or push the wiki** — supply a PAT/App token as a secret (referenced as the `secrets.PROJECTS_TOKEN` Actions expression) for those steps.
- **Preflight (run before mutating):** `gh auth status` (and confirm the `project` scope), `gh repo view --json hasIssuesEnabled,hasWikiEnabled`, and attempt `gh project list`; on any gap, print exactly "missing X → grant it via Y" and **downgrade a tier** rather than aborting.

## Engagement TODO → issue → Project field mapping

| TODO field | GitHub issue | Project field |
| --- | --- | --- |
| Title | issue title | item title |
| Owner/role | assignee (default: the `ROLES.md` role) | (synced) |
| Priority | `priority:{high,med,low}` label | **Priority** (single-select) |
| Size | `size:{s,m,l}` label | **Size** (single-select/number) |
| Level | `level:{L0..L5}` label + milestone | **Level** (single-select) |
| Blocking? | `blocking` label + issue **dependency**/sub-issue | (filter) |
| Definition-of-done | issue body checklist | — |
| Links | issue body | — |
| task-id | hidden `<!-- data-project:task=… -->` marker | (via linked issue) |

## Artifacts it implies

- Ignore + attributes → `templates/gitignore.tmpl`, `templates/gitattributes.tmpl`; workflow + review norms → `templates/CONTRIBUTING.md.tmpl`; CI → `templates/ci/github-actions-ci.yml.tmpl`.
- Planning/tracking → `templates/github/ISSUE_TEMPLATE/{task,data-issue,config}.yml.tmpl`, `templates/github/PULL_REQUEST_TEMPLATE.md.tmpl`, `templates/github/labels.yml.tmpl`, `templates/github/seed-github.sh.tmpl`, `templates/github/engagement-issues.md.tmpl`, `templates/github/project-template.md.tmpl`, `templates/github/ACCESS.md.tmpl`, `templates/github/wiki-seeds/{Home,_Sidebar}.md.tmpl`, `templates/PROJECT-MANAGEMENT.md.tmpl`; the assignable checklist in `templates/ROADMAP.md.tmpl` + `templates/NEXT-STEPS.md.tmpl`; and the `data-project-tracker` agent.

## When most relevant

The code-review loop: any multi-person project — whenever the user mentions collaborators, pull requests, review, or "how do we work together" (CI at L2, workflow norms at L3). The planning loop: L3+ collaborative projects hosted on GitHub — strong signal on "track work," "issues," "board," "project," "milestones," "wiki," "assign," "who's doing what." Below L3 or off GitHub, keep to the `ROADMAP.md` checklist + `NEXT-STEPS.md` memo.

## Caveats / conflicts

Open-source patterns were built for code, not data — treat them as good-enough, not ideal, and pair them with data-specific practices (pipeline-as-code as the shared artifact, immutable raw data); see `collaboration-architecture.md` anti-patterns. The Projects-v2 org scope is the main operational friction — handle it with the preflight + graceful downgrade above. Wikis are a separate, collaborator-edit-only repo, so they stay opt-in. Keep the Markdown the source of truth and GitHub a projection; and hold the lean line — a solo L0–L2 project needs no issues or board, only the checklist and memo.

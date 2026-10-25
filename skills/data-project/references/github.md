---
type: Reference
title: Git and GitHub for collaborative data work
description: The GitHub backbone for data teams. The code-review loop (branches, pull requests, commit messages, data-aware ignores, CI, branch protection), work tracking (issues, labels, optional Projects), the exact access and token scopes an automating agent needs, and the standardized Project board setup.
resource: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects
tags: [github, collaboration, review, branch-protection, issues, projects, section-7, section-10]
---

# Git and GitHub for collaborative data work

How changes get made and merged (the code-review loop, Outline section 7) and how work gets tracked (issues and boards, section 10), plus the access an agent needs to automate either. The tracking procedure itself is `procedures/tracking.md`. Sources: GitHub's documentation on [Projects best practices](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects), [planning and tracking with Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects) and [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches); the GitHub blog on [standardizing workflows with Projects](https://github.blog/developer-skills/github/how-were-using-github-projects-to-standardize-our-workflows-and-stay-aligned/); and a practical [git and GitHub guide for data science](https://arounddatascience.com/blog/coding/how-to-use-github-and-git-for-collaborative-data-science-projects-a-complete-guide-for-algerian-data-scientists/).

## Contents

- [The code-review loop](#the-code-review-loop)
- [Review gates that are real](#review-gates-that-are-real)
- [Concurrent agents](#concurrent-agents)
- [Tracking work](#tracking-work)
- [Access and scopes](#access-and-scopes)
- [The optional Project board](#the-optional-project-board)
- [Caveats](#caveats)

## The code-review loop

- **Branch per unit of work** with a descriptive name (`fix/reconcile-totals`, `source/2026-release`); merge back by pull request; delete the branch on merge.
- **Pull requests carry evidence.** The body says *What changed / Why / What I checked / Left alone on purpose*, links the issue with `Closes #N`, and lists the commands run and their results. Projects found that agents ignore checkbox templates but reliably fill evidence sections, and that these PR bodies became the real review record.
- **Commit messages explain why.** Imperative subject; the body explains the analytical decision, not the diff.
- **Data-aware ignores and storage.** Large or bulk originals go to Git LFS or external storage with hash and URL in provenance, never into history directly; GitHub rejects files over 100 MB, and unattended workflows that rebuild binaries should batch commits and check sizes. Secrets and notebook outputs never land in the repository.
- **CI on every pull request:** lint, tests, the audit and a conservation check before human review, plus the token guard in scaffolded repositories.

## Review gates that are real

A rule such as "every change needs an approving review" or "owners approve by PR" is honest only when the repository enforces it. Most projects that wrote such rules merged PRs with zero reviews, because nothing stopped them and often no second reviewer existed.

- **With collaborators:** turn on branch protection when the rule is written, and keep the command in `docs/governance/GOVERNANCE.md`:

  ```sh
  gh api -X PUT repos/<owner>/<repo>/branches/<default-branch>/protection --input - <<'JSON'
  {"required_status_checks": null, "enforce_admins": true,
   "required_pull_request_reviews": {"required_approving_review_count": 1, "require_code_owner_reviews": true},
   "restrictions": null}
  JSON
  ```

  Verify with `gh api repos/<owner>/<repo>/branches/<default-branch>/protection`. `CODEOWNERS` only *requests* reviewers; `require_code_owner_reviews` is what makes their approval required. Rulesets are an alternative with the same effect.
- **Private repositories** need a paid GitHub plan for branch protection and rulesets. Without one, write review as a practice ("we ask for review") rather than a gate.
- **Solo projects** say so: one steward decides and records decisions in PR bodies and the decision-log. No pretend committee.
- **Consent steps** ("all owners must agree before X") need the same treatment: require that many approving reviews, or record each approver explicitly in the PR.

## Concurrent agents

When several agents or people work in the same repository at once:

- Give each its own **git worktree** (`git worktree add ../wt-<task> -b <branch> origin/<default-branch>`), never a shared checkout.
- **Stage explicit paths.** Never `git add -A` or `git add .` in a dirty shared tree; it sweeps another worker's untracked files into your commit.
- **`git fetch` and confirm you are level with `origin/<default-branch>` before merging or auditing.** A stale checkout produces false "missing file" findings.

## Tracking work

- **Issues are the unit of work.** One issue per task; issue forms (`.github/ISSUE_TEMPLATE/*.yml` plus `config.yml` disabling blank issues) keep them consistent; model breakdown and blockers with sub-issues and issue dependencies rather than a label alone; link PRs with `Closes #N`.
- **Labels stay few:** `section:1` … `section:10` for the Outline section, a handful of `type:*` labels, and `blocking`. Priority and size belong in the issue body or Project fields; label taxonomies for them mostly went unused.
- **Issues are where work happens; durable decisions go to the decision-log** with a link back to the issue, and ROADMAP rows link the issue as evidence. Keep each fact in one place.
- **Capability chain** for automation: `gh` CLI, then the GitHub MCP tools, then the unrun seed script (`PRINT=1` gives paste-able issue text). Never fail a scaffold because GitHub is unavailable. Details: `procedures/tracking.md`.

| Task field | GitHub issue | Project field (if a board exists) |
| --- | --- | --- |
| title | issue title | item title |
| owner | assignee | synced |
| section | `section:N` label | synced from the label |
| priority | body line | **Priority** (single select) |
| size | body line | **Size** (single select) |
| blocking | `blocking` label + dependency or sub-issue | filter |
| done-when | body task list | — |
| links | body | — |
| task-id | hidden `<!-- data-project:task=<id> -->` marker | via the issue |

## Access and scopes

Confirm access before mutating anything; on a gap, print exactly what is missing and how to grant it, then drop a tier rather than stopping.

**Repository settings.** Issues enabled (Settings → General → Features). For workflow-driven automation: Settings → Actions → General → Workflow permissions = *Read and write*, and tick *Allow GitHub Actions to create and approve pull requests* if a workflow opens PRs.

**`gh` CLI** (simplest): `gh auth login`, then `gh auth refresh -s project,read:project` if a board is wanted; `gh auth status` should list the scopes. Preflight:

```sh
gh auth status                                         # is the 'project' scope present (boards only)?
gh repo view <owner>/<repo> --json hasIssuesEnabled    # are issues on?
gh project list --owner <owner>                        # can you see Projects (boards only)?
```

**Projects live at organization or user scope, not repository scope.** This is the most common failure: a token that can create issues all day still cannot touch a board.

- **Classic personal access token:** `repo` (issues), plus `project` for boards, plus `workflow` to edit files under `.github/workflows/`.
- **Fine-grained token:** repository *Issues*, *Contents* and *Pull requests* read and write, *Metadata* read, plus the organization permission *Projects: read and write* for org boards.
- **GitHub App:** Issues, Contents and Pull requests read and write, and Organization Projects read and write, installed on the repository or organization. Best for shared automation not tied to one person.
- **In GitHub Actions:** the default `GITHUB_TOKEN`, with a `permissions:` block, can open issues and PRs but **cannot modify organization Projects**. Store a classic token or App token as a repository secret (for example `PROJECTS_TOKEN`) and use it only for board steps.

## The optional Project board

A board helps a team that plans by iteration; a small team is fine with issues alone. When one is in scope:

- **Fields:** *Status* (Todo / In progress / Done), *Priority* (High / Medium / Low), *Size* (S / M / L), *Section* (1–10, or use the label), and optionally *Iteration* for week-by-week planning. Don't duplicate assignees, labels or milestones as custom fields; Projects syncs those from the issues.
- **Views:** a Board grouped by Status for daily flow, a Table grouped by Section for planning and bulk edits, and a Roadmap over iterations or target dates.
- **Built-in workflows:** auto-add matching repository issues, set Status to Done when an issue closes, and auto-archive old Done items.
- **Status updates** (On track / At risk, with dates) give stakeholders a summary without reading every issue.
- **Reuse across teams:** once the layout works, *Make template* in the Project settings, and other teams start from *Use this template* with the same fields, views and workflows.

## Caveats

Open-source practices were built for code, not data: pair them with data-specific ones (the pipeline is the shared artifact; originals are immutable; numbers in prose are generated). Wikis are a separate repository editable only by collaborators, cannot be pushed with fine-grained tokens, and in practice went unmaintained; keep long-form docs in `docs/` instead. A solo project needs no issues or board: ROADMAP rows, PR bodies and the decision-log are enough.

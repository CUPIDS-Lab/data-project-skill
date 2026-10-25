---
type: Procedure
title: Track the work (ROADMAP rows and GitHub issues)
description: How a project records and syncs its work. ROADMAP rows are the source of truth for section status; when there is a team on GitHub, each now section gets one issue with its done-when test as a task list, labeled section:N, synced idempotently through gh, the GitHub MCP, or the seed script.
tags: [tracking, roadmap, github, issues, labels, section-10]
---

# Track the work (ROADMAP rows and GitHub issues)

Use this at the end of scaffolding (SKILL.md "Start a project", step 4) and whenever the user asks to "turn the roadmap into issues," "put this on a board," or "sync to GitHub." It covers the tracking half of Outline section 10; `../github.md` has the GitHub mechanics, scopes and board setup.

## Contents

- [What is the source of truth](#what-is-the-source-of-truth)
- [When to open issues](#when-to-open-issues)
- [The task schema](#the-task-schema)
- [Labels](#labels)
- [The sync, step by step](#the-sync-step-by-step)
- [Capability chain](#capability-chain)
- [Multi-pipeline repos](#multi-pipeline-repos)
- [Report](#report)

## What is the source of truth

- **`ROADMAP.md` rows** are the source of truth for *where each section stands*: one row per Outline section with status (now, later, skip, done), owner, the "done when" test, and evidence (the issue or PR that shows it). The Blocking items table lists every gate and the action it guards.
- **Issues** are where the work on a section actually happens: discussion, task lists, linked PRs. Decisions made in an issue are copied to `decision-log.md` with a link back, because a decision buried in an issue thread is lost to the next person.
- Keep each fact in one place. The ROADMAP row links the issue; the issue body links the ROADMAP row; neither restates the other's details.

## When to open issues

- **Team on GitHub:** open **one issue per *now* section**, titled `Section N: <name>`, whose body is that section's "done when" test from `../_shared/OUTLINE.md` as a task list, plus any checklist items that gate it (for example the responsible-data checklist under section 1 for sensitive data). Add issues for *later* sections only when they become *now*.
- **Blocking items** get their own issue each, labeled `blocking`, linked from the section issue as a sub-issue or dependency where the repository supports it.
- **Solo project, or not on GitHub:** do not open issues. The ROADMAP rows, PR bodies (*What changed / Why / What I checked / Left alone on purpose*) and the decision-log are the record.

## The task schema

Every tracked item, whether it comes from a ROADMAP row or a pasted to-do list, is normalized to these fields before syncing:

| Field | Meaning | On GitHub |
| --- | --- | --- |
| `task-id` | stable slug, e.g. `section-1` or `blocking-consent-basis` | hidden marker `<!-- data-project:task=<id> -->` in the body |
| title | outcome-phrased title | issue title |
| owner | a person or role (default: the role from `docs/governance/CHARTER.md`, else the PI) | assignee |
| priority | high, med or low | body line; Project **Priority** field when a board exists |
| size | S, M or L | body line; Project **Size** field when a board exists |
| done-when | observable checks, as a task list | body task list |
| section | Outline section number | `section:N` label |
| blocking | yes or no, and what it guards | `blocking` label plus a dependency or sub-issue |
| links | ROADMAP row, sources, prior PRs, decision-log entries | body |

## Labels

The label set lives in `.github/labels.yml` (from `templates/github/labels.yml.tmpl`): `section:1` … `section:10` (one per Outline section, named in the description), a few `type:*` labels (`type:data`, `type:docs`, `type:pipeline`, `type:governance`, `type:infra`), `blocking`, `good-first-issue` and `help-wanted`. Priority and size are not labels; they live in the issue body and, when a board exists, in Project fields. There are no milestones per section; use milestones only for real releases if the team wants them.

## The sync, step by step

The sync is **idempotent**: running it again after editing the ROADMAP updates the same issues instead of duplicating them.

1. **Preflight.** Detect a GitHub remote; run `gh auth status` (and check for the `project` scope if a board is wanted); `gh repo view --json hasIssuesEnabled`; `gh project list --owner <owner>` if a board is wanted. On any gap, print exactly what is missing and how to grant it (`../github.md`, "Access and scopes"), then drop to the next tier instead of stopping.
2. **Normalize** the ROADMAP rows (or the supplied list) to the task schema, deriving stable `task-id`s.
3. **Match before you create.** Load `.github/engagement-sync.json` (`task-id` → issue number and a content hash). If an id is not there, search issue bodies for its marker. Found and changed: update title, body, labels and assignee. Not found: create it and record the mapping. A task no longer in the source: close its issue with a comment explaining why; never delete.
4. **Close from merged work, not from roadmap edits.** A section issue closes when the PR that satisfies its "done when" test merges (`Closes #N` in the PR body). On every run, flag mismatches: an issue still open although its work is merged, and an issue closed with no merged work behind it.
5. **Board (optional).** When a Project is in scope and the token allows it, add each issue as an item and set Status, Priority and Size. Don't duplicate what Projects already syncs from issues (assignees, labels).
6. **Persist** `.github/engagement-sync.json` so the next run converges. It stores only the id-to-issue mapping and a hash.
7. **Update the ROADMAP evidence column** with the issue links, in a PR.

## Capability chain

Land at the richest tier available and never fail the scaffold because GitHub is unavailable:

1. **`gh` CLI**, authenticated: run the sync directly, or run `.github/seed-github.sh`, which encodes the same steps.
2. **GitHub MCP tools** (`issue_write`, `issue_read`, `list_issues`, `sub_issue_write`, `add_issue_comment`) when `gh` is missing but an authenticated GitHub MCP server is connected. Same matching rules; boards may not be reachable this way.
3. **Seed script, unrun.** Write `.github/seed-github.sh` and `.github/labels.yml` and tell the user the one command to finish later (`./.github/seed-github.sh`, or `DRY_RUN=1` to preview). Without `gh`, `PRINT=1 ./.github/seed-github.sh` prints each issue as a paste-able Markdown block for filing by hand.

The `ISSUE_SEED_ROWS` token in the seed script is filled with one line per task: `seed_issue "<task-id>" "<title>" "<labels>" "<priority>" "<size>" "<body>"`, where labels are comma-separated (`section:1,type:governance`).

## Multi-pipeline repos

Each pipeline is tracked by one issue, closed by the PR that lands its `pipelines/<name>/` directory. On every sync, compare the pipelines on the default branch with what the repository documents (the README pipeline table, the ROADMAP, the `<!-- data-project:pipeline=<name> -->` markers) and the pipeline issues, and report both directions of drift: a directory nobody documents, and a documented pipeline with no directory. Report the gap as a checklist for a human; never rewrite the documents silently. See `../multi-pipeline.md`.

## Report

Tell the user the tier reached, what was created or updated (with URLs), which blocking items are still open, any open-but-merged or closed-but-unbuilt mismatches, and, if you degraded, the exact command and the missing scope needed to finish.

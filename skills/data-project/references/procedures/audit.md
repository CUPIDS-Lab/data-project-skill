---
type: Procedure
title: Audit an existing data repository against the Outline
description: How to score an existing data repository section by section against the Outline's done-when tests, after verifying the checkout is level with its remote, and report a prioritized gap table without changing anything until the user approves remediation.
tags: [audit, outline, review, gaps]
---

# Audit an existing data repository against the Outline

Use this when the user asks to "audit my repo," "what's missing here," or "how far along is this project." The audit is **read-only** until the user approves remediation.

## 1. Make sure you are auditing the real repository

If the target is a git repository, run `git fetch` and confirm the checkout is level with `origin/<default-branch>` (`git status -sb`, `git rev-list --left-right --count HEAD...origin/<default-branch>`). A stale or diverged working tree reports files as "missing" that are already merged on the remote. If it is behind, say so and audit the remote state (`git worktree add` a clean checkout of `origin/<default-branch>`), or ask the user which state to audit.

## 2. Read the project's own plan

Read `README.md`, `AGENTS.md`, `ROADMAP.md` and `decision-log.md` if they exist. The ROADMAP's now, later and skip marks are the project's own claims: a section marked *skip* with a reason is not a gap, and a *later* section is a gap only if something now depends on it. Note the sensitivity tier and visibility; they decide which gates apply (a private project has no section 8 to audit; a sensitive one must satisfy section 7's safeguards whatever else is deferred).

## 3. Score each section against its "done when" test

For each of the ten sections in `../_shared/OUTLINE.md`, check every "done when" item against evidence in the repository, not against file names alone:

- **Met:** the evidence exists and works (the command regenerates the data; the CI job runs and is green; the README actually explains the unit of observation).
- **Partly met:** the artifact exists but does not do what the test asks (a GOVERNANCE file claiming "owners approve by PR" with no branch protection; a dictionary missing columns; quoted numbers typed by hand).
- **Not met:** nothing satisfies it.
- **Not applicable:** the project's recorded scope excludes it, with a reason.

Useful checks: `grep -Rn "{{" .` for unfilled tokens; dead intra-repo links; whether CI discovers every pipeline (a multi-pipeline repo must find each `pipelines/*/pyproject.toml`; see `../multi-pipeline.md`); `gh api repos/<owner>/<repo>/branches/<branch>/protection` when the docs claim review gates; whether the ROADMAP rows agree with the issues and the directories on disk; files near GitHub's 100 MB limit.

If a `knowledge/` bundle exists, check OKF conformance: every non-reserved `.md` has parseable frontmatter with a non-empty `type`, and the bundle-root `index.md` declares `okf_version` (`../okf-open-knowledge-format.md`). If an `ai-catalog.json` exists, check it parses and its `specVersion` matches the spec it claims (`../agentic-resource-discovery.md`).

## 4. Report a prioritized gap table

Print one table, ordered by priority: gate failures first (sensitivity safeguards, claimed-but-unenforced review gates, visibility violations), then anything that makes the data wrong or unreproducible (sections 3–5), then documentation and maintenance gaps.

| Priority | Section | "Done when" item | Status | Evidence | Recommended fix | Reference |
| --- | --- | --- | --- | --- | --- | --- |

Name the fix concretely (the template from `scaffold.md`, the command, or the procedure) and the reference that explains it. Say what you are not recommending and why ("no CHARTER: solo project"). Then offer to fix the gaps, section by section, starting with the highest priority; make no change until the user approves, and in a shared repository make it on a branch with a PR.

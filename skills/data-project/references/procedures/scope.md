---
type: Procedure
title: Scope a data project (section 1)
description: The scoping conversation that opens every new data collaboration. It elicits the question, unit of observation, sources, partners and beneficiaries, sensitivity tier, visibility, team and horizon, and a now/later/skip decision for each Outline section, then hands a short brief to the approval step.
tags: [scope, section-1, interview, sensitivity, visibility, roadmap]
---

# Scope a data project (section 1)

Run this before writing any file. Scaffolding before scoping is the failure this procedure exists to prevent: the brief it produces decides what gets built now, what waits in `ROADMAP.md`, and which safeguards are mandatory. It covers Outline section 1 (Scope & gate); read `../_shared/values-and-gates.md` and `../_shared/responsible-data.md` alongside it when the data involves people.

## How to ask

- **Small, branching rounds.** Ask a handful of questions at a time, never a twenty-question wall. Each answer decides what to ask next: a solo, public, one-semester project needs four or five questions; a multi-partner sensitive project needs more.
- **Infer, then confirm.** Use what the conversation and the working directory already say. Ask only what would change the output, and offer concrete options with a default so the user can accept quickly. If the user is in a hurry, infer aggressively and confirm every assumption in one message.
- **Context-rich fast path.** When the user has supplied substantial design material (a `context/` folder, a methodology memo, an architecture note, a source catalog, an existing README), read it first, infer the whole brief from it, and present the brief for correction instead of interviewing cold. Ask only about gaps the documents leave open and anything on the "must confirm" list. A rich-context request should reach a confirmable brief in one pass.
- **Use `AskUserQuestion`** where the harness has it, so options are clickable; otherwise ask in plain text with lettered options.

## What to find out

Cover these, skipping anything already known.

1. **Basics.** Project name, one-line description, the person responsible (`PI_NAME`), the lab or organization (default "CUPIDS Lab"), and a contact email.
2. **The question.** What question the data answers, in one or two sentences a newcomer would understand, and what it will *not* be used for.
3. **Unit of observation.** What one row means (one row per county-month, per contract, per inspection). If the user can't say yet, record that as the first *now* task; nothing downstream is stable without it.
4. **Sources.** Each source, its access path (download, API, dashboard, FOIA request, archive, contributed by people), whether it is re-released or ephemeral, its license or terms, and whether the publisher is reachable. Note whether an input is a **curated source of record** (small, hand-made, the project's actual asset, so it is committed) or **bulk and re-downloadable** (fetched by code, so it need not be committed). Note contributed or crowdsourced data explicitly; it carries intake duties.
5. **Partners versus beneficiaries.** Name the design partners (who does the work) separately from the beneficiaries (who the work is for), and whose risks are centered. Note which core roles are filled and which are gaps (data engineer, software developer, subject-matter expert, mediator, project manager; see `../collaboration-architecture.md`).
6. **Sensitivity tier.** One of `public`, `de-identified`, `sensitive-human`, `regulated`; whether Indigenous data is implicated (CARE); which privacy laws apply (for example FERPA, HIPAA, state privacy law, GDPR). Record **conditional sensitivity** too: data that is public now but becomes sensitive when a named event happens (ingesting article text with personal data, joining to a person-level file). The event becomes a blocking ROADMAP row.
7. **Visibility.** One of `private` (never published; the repository and data stay restricted), `embargoed` (published after a date or condition), or `public`. Never describe a private project as "not yet public." Visibility also decides which hosted services (OCR, LLM, publishing) may receive the project's documents.
8. **Team and horizon.** How many people, solo or team, on GitHub or not, the time available (a sprint, a semester, ongoing), and who keeps it running afterward. A solo project gets a single-steward governance statement, not a committee.
9. **Tooling.** Python (default; data-liberation's uv project shape) or R (the maintained `targets` + `renv` variant); one pipeline or several (a multi-pipeline repo, `../multi-pipeline.md`); notebooks or not.
10. **Release intent.** Whether the data will be deposited for a DOI (section 9), shared with partners in place, published on a surface (section 8), or made discoverable to agents. For a deposit, whether the data is one-off or refreshed, and the cadence (monthly, quarterly, annually).
11. **Accessibility needs** for anything public: plain-language summary, alt text, colorblind-safe figures, screen-reader-friendly documents.

## Protective defaults

Never invent the user's compliance posture. If IRB status, consent, the legal basis or the sensitivity tier is unknown, mark it **must confirm** and default to the more protective option until it is confirmed. Privacy law and the CARE Principles are hard gates, not preferences. When sensitivity is `sensitive-human`, `regulated` or CARE-implicated, section 7's minimum safeguards are *now* regardless of what else is deferred: every identifier, retention or audit affordance ships with access tiers and a contestable remedy (`../_shared/values-and-gates.md`). Visibility defaults to `private` until the user chooses otherwise.

## Decide now, later or skip for each section

Walk the ten Outline sections (`../_shared/OUTLINE.md`) and mark each one:

- **now**: work starts this sprint; its artifacts are generated when the work reaches it.
- **later**: real and wanted, deferred on purpose; it goes in `ROADMAP.md` with the reason.
- **skip**: out of scope; give the reason (for example "section 8 skip: visibility is private").

Defaults: section 1 is always *now*. Section 8 is *skip* when visibility is private. Section 7 is *now* when data is sensitive or there is more than one person, otherwise a single-steward line in the README. Section 10's feedback step is always on. When unsure, choose *later*: a named deferred section is worth more than an unmaintained file.

Record **blocking items** separately: anything that must be resolved before the action it guards (before ingesting personal data, before publishing, before depositing). A conditional-sensitivity trigger is always a blocking item.

## Output: the brief

Return one block titled **Project brief**, short enough to read in a minute. It is what the SKILL.md "Start a project" step 2 shows the user for approval.

- **Name, description, PI, lab, contact.**
- **Question** and **what we won't liberate or publish.**
- **Unit of observation.**
- **Sources** (one line each: access path, license, re-released or ephemeral, curated or bulk).
- **Partners** and **beneficiaries**, and any **role gaps**.
- **Sensitivity tier**, privacy-law screen, CARE check, and any conditional trigger.
- **Visibility:** private, embargoed (with the date or condition) or public.
- **Team and horizon:** solo or team, on GitHub or not, time available, custodian afterward.
- **Tooling:** Python or R; single or multi-pipeline; notebooks.
- **Sections:** a ten-row table, `# · section · now/later/skip · reason`.
- **Blocking items** with the action each guards.
- **Assumptions and defaults applied**, and **Must confirm**.

The brief's values fill the scaffold's tokens and flags (`scaffold.md`), the README's "What & why", the decision-log's first entries (sensitivity, visibility, exclusions; tag anything inferred **Assumed**), and the ROADMAP rows.

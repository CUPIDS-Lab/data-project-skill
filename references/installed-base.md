---
type: Reference
title: Installed-Base Values Spine
description: The values framework that the synthesizer applies as a guardrail — three pressures answered by three counter-values, six installed-base elements rendered as repo requirements, and the minimum-viable-safeguards coupling that fires on sensitive data.
tags: [values, governance, ethics, safeguards, sensitive-data]
---

# Installed-Base Values Spine

Read this when shaping anything that touches identifiers, retention, access, audit, or publication — and always when data is sensitive. This is the skill's value spine: it is what prevents affordances from becoming surveillance or theater. It is applied as a *guardrail by the synthesizer*, not as a pile of extra files; it only becomes new artifacts (a `GOVERNANCE.md`, an access-tier table, an `INSTALLED-BASE.md`) when the project's type and sensitivity warrant them.

## Three pressures, three counter-values

Public-interest data infrastructure sits under three chronic pressures; the skill answers each with a counter-value that the scaffold operationalizes.

- **Enclosure → Openness.** Public evidence keeps getting locked into formats and platforms that are technically open but practically closed. Counter it with durable, legible openness: plain-text version-controllable formats, exportable everything, no vendor-locked required dependency.
- **Exemption → Oversight.** Powerful actors carve out exemptions from scrutiny. Counter it with routinized, *testable* oversight: logging, reporting cadences, and a role with recognized authority to interpret and contest the evidence.
- **Erosion → Ownership.** These projects quietly erode when grants, pilots, semesters, or administrations end. Counter it with stewardship obligations and collective governance: named custodians, retention schedules, and migration plans that survive turnover.

## Six installed-base elements, as repo requirements

Render each element as something the repository must *contain* (at the appropriate level), not as an aspiration.

1. **Jurisdictional linkability** — stable, persistent identifiers and crosswalks so records join across sources, decisions, and time; name who owns the reference data. (Surfaces in the data dictionary and, at L5, OKF concept `resource` URIs.)
2. **Provenance-in-practice** — documentation, change logs, and version histories that are expected and reviewable, legible to affected parties and not only to builders. (Decision log, `CHANGELOG`, provenance fields in the data dictionary.)
3. **Stewardship continuity** — retention schedules, redundancy/mirroring, migration plans, and *named custodians* who outlast budget cycles. (Charter "what survives the pilot"; governance retention section.)
4. **Legitimate visibility / tiered access** — documented decision rules for what is public, what is restricted, and which accountable intermediaries may touch sensitive traces. (Governance access tiers.)
5. **Contestable oversight** — logging and audit rights, reporting cadence, and a role authorized to interpret and contest the evidence. (Roles + governance.)
6. **Remedy / escalation** — accessible, protective, consequential pathways that convert a documented problem into review and correction, with transparency about outcomes. (Governance escalation section.)

## Minimum viable safeguards (the load-bearing coupling)

Identifiers and retention are not neutral goods. **Wherever vulnerable populations are implicated, pair every linkability and retention affordance with access tiers and contestable governance** over what is linkable, what is preserved, who can reach sensitive traces, and how those decisions are challenged. This coupling is automatic: when the interview marks data as sensitive-human, regulated, or implicating Indigenous data (CARE), the synthesizer must not scaffold an identifier scheme, a retention policy, or an audit log without also scaffolding the corresponding access-tier and remedy/escalation language — or, if the project is too shallow to carry a full `GOVERNANCE.md`, without writing the coupling obligation explicitly into `ROADMAP.md` as a blocking item. Affordances without duties are theater; the skill refuses to ship the theater.

**Deferred-but-enforced (conditional sensitivity).** Some projects are public and low-risk *now* but **become sensitive when** a future step happens — the corpus ingests article text plus journalist PII, or copyrighted source material, or links to individuals. Don't fire heavy governance now, and don't waive the duty either: record the coupling as **blocking** `ROADMAP.md` rows that *name the trigger event* and gate the sensitive build, so the affordance↔duty pairing is enforced exactly when it becomes real. The coupling is deferred in time, never dropped.

## How this interacts with right-sizing

This spine is not a license to over-build. For a public, non-sensitive teaching dataset, most of these elements collapse to a sentence in the README and a line or two in `ROADMAP.md`. The weight scales with sensitivity and collaboratory type (see `collaboration-architecture.md`), and the default for a low-sensitivity, small-team project is light. The coupling rule is the one place where sensitivity overrides leanness — there, the duty ships with the affordance no matter how small the project.

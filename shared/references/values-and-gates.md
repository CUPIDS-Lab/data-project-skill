---
type: Reference
title: Values and Gates
description: Why both skills exist, the design principles they share, the few hard gates they never cross (privacy law, CARE, sensitivity tiers), the visibility decision, and the installed-base values spine with its affordance-and-duty coupling.
tags: [values, gates, privacy, care, sensitivity, visibility, installed-base, governance]
---

# Values and gates

Read this at the start of any project, in Outline section 1 (Scope & gate), and again whenever work touches identifiers, retention, access, audit or publication. It holds the *why* behind both skills, the few constraints that override every other default, and the values spine that keeps affordances from turning into surveillance or theater. Everything else in the skills is advisory; this file says what is not.

## Contents

- [Mission](#mission)
- [Design principles](#design-principles)
- [The hard gates](#the-hard-gates)
- [Sensitivity tiers](#sensitivity-tiers)
- [Visibility: private, embargoed or public](#visibility-private-embargoed-or-public)
- [The installed-base values spine](#the-installed-base-values-spine)
- [Minimum viable safeguards: the affordance-duty coupling](#minimum-viable-safeguards-the-affordance-duty-coupling)
- [How the spine interacts with right-sizing](#how-the-spine-interacts-with-right-sizing)
- [How the two skills divide the work](#how-the-two-skills-divide-the-work)
- [Default infrastructure profile](#default-infrastructure-profile)

## Mission

Both skills belong to CUPIDS, the CU (University of Colorado) Public Interest Data Science Lab and Clinic. They exist to help small, interdisciplinary, often short-lived teams turn locked or messy public information into datasets and projects that other people (collaborators, affected communities, future maintainers, downstream agents) can understand, trust, reuse and contest. The four goals are **accessible, documented, transparent and inclusive**, with **collaborative** and **reproducible** as the cross-cutting enablers that make the other four real.

The animating worry is *accountability theater*: a project that ships impressive affordances (stable identifiers, retention, dashboards, audit logs) without the duties and governance that make those affordances contestable. Affordances without duties are theater. The skills' job is to keep the two coupled, above all when the data touches people who can be harmed.

## Design principles

- **Right-size, always.** Build for the team and horizon that exist, not an imagined enterprise. Over-engineering a three-person, one-semester project is its own failure mode. Every Outline section is marked *now*, *later* or *skip* in `ROADMAP.md`; when in doubt, build less now and write the rest down as a deferred outcome. Say what you are not generating and why.
- **Originals are immutable, and *immutable* and *tracked* are separate choices.** Originals in `data/original/` are never edited in place, and every transformation is reproducible from them. Whether an original is committed is a storage decision made in section 2 (Acquire): bulk, external or re-downloadable inputs stay out of history (refetched by the pipeline, or held in Git LFS or external storage with hash and URL in provenance), while a small, curated source-of-record that *is* the project's asset is tracked through a `.gitignore` carve-out and documented as immutable in the data dictionary and decision-log. Don't git-ignore the project's only data, and don't let Git become an unplanned data store.
- **Documentation is half the work.** A dataset without a data dictionary, provenance and a decision trail is a private spreadsheet. Documentation lives next to what it documents and is written for someone who has none of the project's context.
- **Audit against originals.** Reconciliation against the source's own published totals is what makes a dataset defensible. Surprising results get double-checked before they get shipped. See `quality-and-bulletproofing.md`.
- **Center the partners doing the work**, named separately from the abstract beneficiaries. The project serves the people in the room and the communities they answer to, not a generic "the public."
- **Make tradeoffs legible** rather than burying them in defaults, above all the transparency-versus-privacy tension, which most public-interest data work manages rather than resolves.
- **Never assume publication.** Most projects these skills served did not want to publish, or not yet. Visibility is decided in section 1, and nothing downstream presumes a public release.
- **Lock-in is a form of enclosure.** Keep the project's core in plain-text, version-controllable formats; anything a hosted tool produces must be exportable, and no vendor-locked artifact is a required dependency.

## The hard gates

Almost everything the skills offer is advisory: a vocabulary for naming work and a menu for extending it. Two things are non-negotiable, and they can mean *do not collect, do not link, do not publish, or publish differently*:

1. **Privacy and data-protection law.** GDPR (including the Article 17 right to erasure), CCPA, FERPA and HIPAA where relevant, and any agency-specific correction or deletion procedure.
2. **The CARE Principles for Indigenous Data Governance** (<https://www.gida-global.org/careprinciples>): Collective benefit, Authority to control, Responsibility, Ethics.

Apply them in this order, during section 1 and before any parser is written:

1. **Privacy-law screen.** If the material contains personal data that a privacy regime protects, the question is whether to collect or publish it *at all*, and in what shape: redact, pseudonymize, aggregate or withhold. "It was extractable" is not authorization. Record the call and its legal basis in the decision-log.
2. **CARE-versus-FAIR check.** FAIR pushes toward maximal discoverability; CARE can pull the other way for data about Indigenous or other historically surveilled communities, toward restricted access under community authority. When they conflict, CARE governs the access decision and FAIR governs the *form* of whatever is released (see `standards-and-fair.md`). If the affected community would not endorse the work, that is a stop, not a footnote.
3. **Out-of-scope-use declaration.** Whatever ships, name the uses the project disavows (for example enrichment for enforcement, predictive policing, eviction targeting). It is not legally binding, but it is the documented community norm, and it belongs in the README and `AGENTS.md`.

Never invent a project's compliance posture. If IRB status, consent or sensitivity is unknown, mark it *must confirm* and default to the more protective option. No hosted service (OCR, a language or vision model, a publishing platform) receives documents that the sensitivity or visibility decision forbids it to see.

## Sensitivity tiers

Section 1 classifies the data into one tier, recorded in the decision-log and carried into templates as `SENSITIVITY_TIER`:

| Tier | Meaning | What it triggers |
| --- | --- | --- |
| `public` | Already-public records with no meaningful risk to individuals. | Light governance; the values spine collapses to a few sentences. |
| `de-identified` | Derived from data about people, with direct identifiers removed. | Re-identification check in the responsible-data checklist; access tiers if quasi-identifiers remain. |
| `sensitive-human` | Identifiable or re-identifiable information about people who can be harmed. | The coupling below fires; the responsible-data checklist is filled now; section 7's minimum safeguards are *now*. |
| `regulated` | Covered by a privacy or sector law (GDPR, CCPA, FERPA, HIPAA, an agency rule). | As `sensitive-human`, plus the legal basis recorded and the regime's own duties honored. |

Two modifiers sit beside the tier. **CARE** applies whenever Indigenous data is implicated, at any tier. **Conditional** sensitivity applies when the data is low-risk now but *becomes sensitive when* a named event happens (the corpus ingests article text with journalist PII, copyrighted material arrives, records get linked to individuals); record it as `public now; becomes sensitive when <event>`. Contributed or crowdsourced data also raises the tier by default, because it inherits duties to the people who supplied it (see `governance.md`).

## Visibility: private, embargoed or public

Section 1 also chooses the project's visibility, separately from its sensitivity, and records it in the decision-log:

- **Private.** The repository and outputs stay with named people. Section 8 (Publish) is *skip*. Section 9 may still apply as a restricted deposit or a partner share under the access tiers.
- **Embargoed.** Outputs are staged for release on a stated date or condition (a partner's sign-off, a court date, a publication). Section 8 stages the release, with its date and conditions, and does nothing public before then.
- **Public.** Section 8 applies, with the FAIR self-check and accessibility check for public outputs.

Evidence behind making this explicit: across the projects these skills were used on, one moved work in progress to a private repository with an embargo workflow, another rewrote its documents to remove "before public" framing, a third chose "private, no warnings," and none had a production public deposit. Do not write "before this goes public" language, publishing workflows or public-facing templates unless visibility is public or embargoed. Visibility can change later; record the change and its reason as a new decision-log entry.

## The installed-base values spine

Public-interest data infrastructure is installed infrastructure: other actors will depend on it. The spine is applied as a *guardrail* while scoping and building, not as a pile of extra files; it becomes artifacts (the access-tier table and values-spine section in `GOVERNANCE.md`) only when the project's collaboration type and sensitivity warrant them.

### Three pressures, three counter-values

Public-interest data infrastructure sits under three chronic pressures; each is answered by a counter-value the project operationalizes.

- **Enclosure → Openness.** Public evidence keeps getting locked into formats and platforms that are technically open but practically closed. Counter it with durable, legible openness: plain-text version-controllable formats, everything exportable, no vendor-locked required dependency. Openness here means legible and exportable, not necessarily published; a private project can still resist enclosure.
- **Exemption → Oversight.** Powerful actors carve out exemptions from scrutiny. Counter it with routinized, *testable* oversight: logging, reporting cadences, and a role with recognized authority to interpret and contest the evidence.
- **Erosion → Ownership.** These projects quietly erode when grants, pilots, semesters or administrations end. Counter it with stewardship obligations and collective governance: named custodians, retention schedules, and migration plans that survive turnover.

### Six installed-base elements, as repository requirements

Render each element as something the repository must *contain* when the relevant Outline section is in scope, not as an aspiration. The right-hand name is the same element as data-liberation's "liberation as infrastructure" checklist states it.

1. **Jurisdictional linkability** (linkability) — stable, persistent identifiers and crosswalks so records join across sources, decisions and time; name who owns the reference data. Lives in the data dictionary, the schema's composite keys and, when an OKF bundle is published, concept `resource` URIs. Sections 4 and 9.
2. **Provenance-in-practice** (interpretability, safe scrutiny) — documentation, change logs and version histories that are expected and reviewable, legible to affected parties and not only to builders. Lives in `provenance.csv`, the decision-log, `CHANGELOG.md`, the data dictionary's caveats and the immutable originals. Sections 2, 4 and 6.
3. **Stewardship continuity** (continuity) — retention schedules, redundancy or mirroring, migration plans, and *named custodians* who outlast budget cycles; a refresh workflow that survives the original developer leaving. Lives in the charter's "what survives the pilot," the governance retention schedule and the refresh workflow. Sections 7 and 10.
4. **Legitimate visibility / tiered access** (authority) — documented decision rules for what is public, what is restricted, and which accountable intermediaries may touch sensitive traces, plus the documented legal basis (FOIA, a sunshine law, a statutory disclosure) for holding the data at all. Lives in the governance access tiers, the visibility decision and `provenance.csv`'s legal-basis notes. Sections 1 and 7.
5. **Contestable oversight** (safe scrutiny) — logging and audit rights, a reporting cadence, a reconciliation report anyone can rerun, and a role authorized to interpret and contest the evidence. Lives in the roles, the governance oversight section and `data/audit/`. Sections 5 and 7.
6. **Remedy / escalation** (remedy) — accessible, protective, consequential pathways that convert a documented problem into review and correction, with transparency about outcomes and the audit trail preserved. Lives in the governance remedy section, the correction issue form and the changelog. Section 7.

A project that supplies tidy data but no documented remedy, or processed data but no provenance, has built infrastructure with missing struts.

## Minimum viable safeguards: the affordance-duty coupling

Identifiers and retention are not neutral goods. **Wherever vulnerable populations are implicated, pair every linkability and retention affordance with access tiers and contestable governance** over what is linkable, what is preserved, who can reach sensitive traces, and how those decisions are challenged. This coupling is automatic: when section 1 classifies data as `sensitive-human` or `regulated`, or implicates Indigenous data (CARE), do not build an identifier scheme, a crosswalk, a retention policy or an audit log without also building the corresponding access-tier and remedy/escalation language. If the project is too small to carry a full `GOVERNANCE.md`, write the coupling obligation into `ROADMAP.md` as a **blocking** row instead. Affordances without duties are theater; the skills refuse to ship the theater.

**Deferred but enforced (conditional sensitivity).** Some projects are public and low-risk *now* but become sensitive when a future step happens. Don't fire heavy governance now, and don't waive the duty either: record the coupling as **blocking** `ROADMAP.md` rows that *name the trigger event* and gate the sensitive build, so the affordance-duty pairing is enforced exactly when it becomes real. When there is a team, open the matching issue with a `blocking` label. The coupling is deferred in time, never dropped.

## How the spine interacts with right-sizing

The spine is not a license to over-build. For a public, non-sensitive teaching dataset, most of these elements collapse to a sentence in the README and a line or two in `ROADMAP.md`. The weight scales with sensitivity and collaboration type (data-project's `collaboration-architecture.md` has the typology), and the default for a low-sensitivity, small-team project is light. The coupling rule is the one place where sensitivity overrides leanness: there, the duty ships with the affordance no matter how small the project, and section 7's minimum safeguards are *now* whatever else is deferred.

## How the two skills divide the work

`data-liberation` gets the data out and tidy: it leads sections 2 (Acquire) through 5 (Pipeline & audit) and section 8 (Publish), turning PDFs, FOIA releases, scraped pages, APIs and panel spreadsheets into tidy, documented, reproducible datasets. `data-project` architects the collaboration, governance and knowledge layer around that data: it leads sections 1 (Scope & gate), 7 (Govern & collaborate) and 9 (Deposit, share & discover). Both share sections 6 and 10, the Outline, and these shared references. A liberated dataset is a natural input to a data-project collaboration, and a data-project repository is a natural home for one or more data-liberation-shaped pipelines (under `pipelines/<name>/` when they are independent datasets). The knowledge layer is the hand-off point: data-liberation's concept catalog and data-project's OKF bundle are the same idea at two scales.

## Default infrastructure profile

When the user signals CUPIDS or does not specify infrastructure, default, overridably, to a **Datasette** catalog, **Cloudflare R2** object storage for large originals and outputs, a **Quarto** front end, and **CU Research Computing** for heavier compute; orchestration beyond `python -m scripts.pipeline run` (Snakemake as a wrapper, or Prefect for scheduled multi-step flows) is optional. These defaults apply only where the matching section is in scope (Datasette and Quarto are section 8, so they don't apply to a private project). Keep the generated project's core stack-agnostic, and name the assumptions you are swapping when you localize.

---
type: Reference
title: ProPublica Collaborate (transferable contributed-data practices)
description: Operational practices for handling contributed/crowdsourced data — intake, deduplication, role-based access, automatic PII redaction, contributor contact logging, and verify-before-cite.
resource: https://propublica.gitbook.io/collaborate-user-manual
tags: [collaborative, inclusive, transparent, sensitive-data]
---

# ProPublica Collaborate (transferable practices)

The user manual for ProPublica's open-source "Collaborate" tool, mined here for the transferable practices of managing contributed/crowdsourced data responsibly (not the tool's installation details). Source: https://propublica.gitbook.io/collaborate-user-manual

## In one paragraph

When a project takes in data contributed by people — tips, survey responses, crowdsourced records — it inherits duties to those people. The transferable lessons are: ingest through defined channels, redact personal information at import, restrict who can see what, log contact with contributors, deduplicate, and never treat a contributed record as a fact until it is verified. These practices drive the contributed-data intake scaffold and reinforce the responsible-data posture.

## Key practices (sampleable units)

- **Defined intake channels** [collaborative, documented] — bring contributed data in through known methods (uploads, forms, live sheets) so provenance is clear and updates flow.
- **Redact PII at import** [inclusive, transparent] — strip names, contacts, and other identifiers on ingestion; remember that redaction downstream does not change the original source.
- **Role-based / project-level access** [inclusive, transparent] — restrict users to the projects and tiers they need; separate standard users from administrators.
- **Log contributor contact** [documented, inclusive] — track outreach for accountability and to honor commitments made to contributors.
- **Deduplicate and triage** [documented] — assign, tag, and status-track records; sort/filter/export rather than analyze in place.
- **Verify before you cite** [transparent] — distinguish collected from verified; a contributed record requires verification before it informs a published claim.

## Artifacts it implies

- → `templates/contributed-data-intake.md.tmpl`; reinforces `templates/responsible-data-checklist.md.tmpl` and `GOVERNANCE.md` access tiers.

## When most relevant

Only when the project accepts contributed/crowdsourced data. Strong signal on "tips," "submissions," "crowdsource," "survey responses," "contributed data." L3, and couples with sensitivity duties.

## Caveats / conflicts

The source is tool-specific; keep the practices and drop the tooling. Source/contributor protection here is a floor, not a ceiling — privacy law and CARE still govern.

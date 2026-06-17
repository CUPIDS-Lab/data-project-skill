---
type: Reference
title: Responsible Data Handbook
description: A practical guide to people's rights to consent, privacy, security, and ownership across the data lifecycle in social-change and public-interest work.
resource: https://responsibledata.io/resources/handbook/
tags: [transparent, inclusive, ethics, privacy, sensitive-data]
---

# Responsible Data Handbook

A practitioner handbook centering consent, privacy, security, and ownership through the whole data lifecycle. Source: https://responsibledata.io/resources/handbook/

## In one paragraph

Responsible Data frames data work around the rights and risks of the people the data is about, walking the lifecycle from project design through getting, understanding, and sharing data to closure, and asking at each stage what could go wrong and for whom. It supplies the L4 ethics scaffolds and drives the sensitivity-tier logic that triggers the installed-base affordance↔duty coupling.

## Key practices (sampleable units)

- **Lifecycle lens** [transparent, inclusive] — design → getting → understanding → sharing → closure; ask the responsible-data questions at *each* stage, not once.
- **Consent that is real** [inclusive, transparent] — freely given, specific, informed, revocable; record purpose, retention, sharing, and rights; track consent.
- **Data minimization & purpose limitation** [transparent] — collect and keep only what the stated purpose needs.
- **Risk and harms assessment** [transparent, inclusive] — enumerate harms (re-identification, profiling, discrimination, misuse) by lifecycle stage; rate likelihood/severity; plan mitigation and monitoring.
- **Security & access** [transparent] — encryption, least-privilege access, audit, breach response; protect sensitive traces.
- **Closure** [transparent] — retention schedules, secure disposal, final stakeholder communication.

## Artifacts it implies

- → `templates/responsible-data-checklist.md.tmpl` (roadmap), `templates/data-management-plan.md.tmpl` (roadmap), `templates/contributed-data-intake.md.tmpl` (roadmap); feeds `GOVERNANCE.md` access tiers and the `installed-base.md` coupling.

## When most relevant

Whenever data implicates people — strong signal on "sensitive," "PII," "consent," "vulnerable," "human subjects." Drives L4; overrides leanness via the sensitivity coupling even at low levels.

## Caveats / conflicts

Advisory, not a legal compliance substitute — the hard gates remain privacy law and CARE (see `context.md`). Scale the artifacts to sensitivity; a public dataset needs little of this.

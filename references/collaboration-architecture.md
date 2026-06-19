---
type: Reference
title: Collaboration Architecture
description: The collaboratory typology that sets governance weight, the five core roles plus mediator and gap-check, the eight team-data-science practices, the charter decisions a collaboration must settle, and the workflow anti-patterns to guard against.
tags: [collaboration, roles, governance, team-data-science, charter, anti-patterns]
---

# Collaboration Architecture

Read this when the project has more than one person, more than one institution, or contributed data — i.e. whenever you are at L3 or being asked about governance, roles, or partners. It supplies the typology that right-sizes governance, the roles a collaboration runs on, the data practices that make joint work possible, the decisions a charter must settle, and the workflow anti-patterns to design against.

## Collaboratory typology (sets governance weight)

Classify the project on two axes and let the type set defaults for access posture, governance weight, and which scaffolds matter. Do not enterprise-bloat a small synchronous team.

- **Resource shared:** tools/infrastructure · data · knowledge.
- **Activity:** aggregating across distance · co-creating.

Rough reads: *aggregating + data* ≈ a community data system or archive (governance and access tiers matter most); *co-creating + knowledge* ≈ a distributed research center (charter, shared definitions, and interpretation practices matter most); *tools/infrastructure* ≈ a community infrastructure project (stewardship continuity and maintenance matter most). The type is a defaulting hint, not a cage.

## Design partners vs. beneficiaries

Name the **design partners** (the people doing the work, who the scaffold should center) separately from the **intended beneficiaries** (the communities the work is for). They are not the same, and conflating them produces work that serves an abstract public while ignoring the room. Record both, and record whose risks are centered.

## Five core roles, the mediator, and the gap-check

A data collaboration runs on five core roles — **data engineer, software developer, subject-matter expert, mediator, project manager** — embedded in a wider community (publishers, consumers, connectors, communicators) and supported by auxiliary roles (infrastructure, statistics, legal).

- **Thinker/doer split:** subject-matter experts frame and interpret; technical members implement. These teams are small, interdisciplinary, and low-turnover, so design for tight, high-bandwidth, often synchronous feedback between the two — not for crowd scale.
- **The mediator function:** someone translates between technical and subject-matter views. Name it explicitly; it is where collaborations succeed or stall.
- **The gap-check:** if a core role is unfilled, say so in `ROLES.md` and make filling it the first priority rather than papering over it. `CODEOWNERS` maps roles to repository paths so review responsibility is legible.

## Eight team-data-science practices (FAIR- and tidy-aligned)

Encode these as the operational defaults behind the data dictionary and data-management scaffolds.

1. **Active collaboration** — engineers and analysts stay in regular contact with data collectors and domain experts.
2. **Consistent schema, field names, identifiers** — one variable per column, one observation per row, one unit of observation per table; identifiers shared across tables so joins are possible. This is the shared language between collectors, engineers, and analysts.
3. **Continuous quality control** — automated, ongoing consistency checks, not a one-time pass.
4. **Versioning, access control, auditing** — least privilege; changes tracked and replayable; handle the slowly-changing nature of evolving datasets.
5. **User-driven exploration** — non-programmers can query and chart without writing code.
6. **Import derived variables** — computed/normalized/summary variables are published centrally, not re-derived per analyst.
7. **Defined export formats and interfaces** — data available scriptably in open, version-stamped formats.
8. **Documentation co-located with the data** — the data dictionary and field descriptions live next to what they describe.

Add the replicability note: held-out / cross-validated checks guard against the overfitting that rapid, reusable, high-dimensional iteration invites.

## Charter decisions a collaboration must settle

Draw the charter (silently) from three interacting levels — organizational, political/policy, and data-technical — and require at minimum:

- **Shared definitions and joint indicators.** Different institutional logics define the same thing differently and register incompatible data. Force agreement up front.
- **Expectation management.** Expectations of data are high; quality is usually low. State what the data can plausibly support — description and comparison far more readily than prediction.
- **Beneficiary and standpoint.** Who the work is for, whose risks are centered, how categories distribute benefits and burdens.
- **Collaborative interpretation.** Make joint, contextualized interpretation of results a standing practice — data owners hold the context that prevents misreadings.
- **What survives the pilot.** State the maintenance commitment, the named custodians, and the retention duties explicitly, because the default trajectory of these projects is quiet erosion.

## Workflow anti-patterns (frame as what to do)

- **Pipeline-as-code is the shared artifact, not the cleaned snapshot.** When sources are re-released, share a text-based, re-runnable pipeline; sharing only the cleaned data guarantees redoing the work every vintage. Keep it legible to subject-matter experts, not only developers.
- **Notebooks stay in `exploratory/`.** They are playgrounds, not products; package code into importable modules under `src/<pkg>/` (the repo-wide package location) at the exploration boundary, and keep notebook outputs out of version control (`nbstripout`).
- **Reproducibility means pinned environments.** Capture dependencies so another person — or another agent — can re-run results; avoid binary blobs version control can't diff.
- **Secrets and sensitive data never land in the repo.** Keep credentials out of code and notebooks; desensitize before anything leaves the controlled tier.
- **Discoverability is a feature.** Data portals are poor at connecting people, so the README, roles, and charter carry the weight of making the project and its contributors findable.

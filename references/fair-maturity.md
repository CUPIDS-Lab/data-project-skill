---
type: Reference
title: FAIR Maturity — making FAIR explicit, measurable, and machine-actionable
description: The FAIR Guiding Principles (with sub-principles), the FAIR-DSM maturity model, the FAIR-as-continuum stance that grounds lean-by-default, the FAIR-not-Open reconciliation with CARE, and the crosswalk from FAIR facets to this skill's L0-L5 levels and the machine-readable metadata it emits.
resource: https://doi.org/10.1038/sdata.2016.18
tags: [fair, maturity, metadata, reproducible, accessible, machine-actionable]
---

# FAIR Maturity (explicit, measurable, machine-actionable)

Read this to turn the skill's informal "aims at FAIR" into an explicit, level-gated, checkable practice. Sources: the FAIR Guiding Principles (Wilkinson et al. 2016, `10.1038/sdata.2016.18`); the FAIR-DSM maturity model and FAIRification process ("FAIR in action", Welter et al. 2023, `10.1038/s41597-023-02167-2`; the FAIR Cookbook, Rocca-Serra et al. 2023, `10.1038/s41597-023-02166-3`); automated evaluation (Wilkinson et al. 2019, `10.1038/s41597-019-0184-5`); and the object-family extensions — software (FAIR4RS, Barker et al. 2022, `10.1038/s41597-022-01710-x`; the CODE roadmap, Di Cosmo et al. 2026, `10.1038/s41597-026-06705-6`), workflows (`10.1038/s41597-025-04451-9`), and AI models (`10.1038/s41597-023-02298-6`).

## In one paragraph

FAIR is not a badge you either have or lack; it is a **measurable continuum** you climb — which is exactly why it fits this skill's L0-L5 ladder. The move this reference makes is to stop "practicing FAIR informally" and instead (a) name each FAIR sub-principle, (b) map it to the level that satisfies it and to a *checkable* indicator, and (c) emit the small machine-readable metadata files (`FAIR-CHECKLIST`, `codemeta.json`, `CITATION.cff`) that make FAIRness legible to humans and agents. FAIR is **not** "open": authenticated, tiered access (A1.2) keeps restricted data FAIR while honoring CARE.

## The FAIR principles (verbatim)

**Findable** — F1 (meta)data are assigned a globally unique and persistent identifier; F2 data are described with rich metadata; F3 metadata clearly and explicitly include the identifier of the data they describe; F4 (meta)data are registered or indexed in a searchable resource. **Accessible** — A1 (meta)data are retrievable by their identifier using a standardized communications protocol; A1.1 the protocol is open, free, and universally implementable; A1.2 the protocol allows for an authentication and authorization procedure where necessary; A2 metadata are accessible even when the data are no longer available. **Interoperable** — I1 (meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation; I2 (meta)data use vocabularies that follow FAIR principles; I3 (meta)data include qualified references to other (meta)data. **Reusable** — R1 richly described with a plurality of accurate and relevant attributes; R1.1 a clear and accessible data-usage license; R1.2 detailed provenance; R1.3 meet domain-relevant community standards.

## FAIR is a continuum ("FAIR enough")

The FAIRification literature is emphatic that there is "neither one specific technology to implement, nor one magic solution," that FAIR is "a journey" scored by *maturity*, and that goals should be scoped and realistic — the FAIRplus process even advises avoiding the word "FAIR" in a project's own goals because it is "too general to impart clear meaning." This is the theoretical grounding for lean-by-default: you do not make a project "FAIR" in one shot, you raise its **FAIR-DSM** maturity rung by rung and defer the rest to `ROADMAP.md`.

## The FAIR-DSM maturity model → this skill's levels

FAIR-DSM scores three aspects — **Content**, **Representation/Format**, **Hosting** — on an ordinal scale (Level 0 "single-use" → higher "community level"). Crosswalk to the ladder (see `escalation-levels.md`):

| FAIR facet | Satisfied by (in this repo) | Level |
| --- | --- | --- |
| F2, R1 — rich metadata/attributes | `DATA-DICTIONARY`, `docs/data-card.md`, `codemeta.json` | L1 |
| R1.1 — license | `LICENSE` (+ `LICENSE-NOTE`) | L1 / L5 |
| R1.2 — provenance | pipeline-as-code + `decision-log` (Snakemake/targets) | L2 |
| R1.3, I1-I3 — standards, vocabularies, qualified links | OKF bundle, controlled vocabularies, JSON-LD | L5 |
| F1 — persistent identifier | Dataverse DOI / DataCite | L5 |
| F3 — identifier embedded in metadata | `dataset.json` / `ai-catalog.json` / OKF frontmatter | L5 |
| F4 — indexed / searchable | ARD `ai-catalog.json`, registry deposit | L5 |
| A1 / A1.1 — open protocol | HTTPS deposit + OpenSharing | L5 |
| A1.2 — authentication where needed | `GOVERNANCE.md` access tiers, OpenSharing scoped creds | L3+ |
| A2 — metadata outlive data | metadata deposited/indexed independently of the payload | L5 |
| the whole map, self-assessed | `docs/FAIR-CHECKLIST.md` | L4 |

## Machine-actionable, not questionnaire-driven

FAIR "mandates machine-actionable behavior," so its assessment "should be completely automated." Model each checklist item on a **Maturity Indicator** — *(an id, the FAIR principle it tests, a rationale, a precise machine test, and a success/failure criterion)* — so the FAIR checklist can graduate from a human checkbox to a CI test (a FAIR-compliance CI job is a documented `ROADMAP.md` extension, not an L0-L2 default). The metadata standards that make this possible are a concrete menu: **schema.org / JSON-LD**, **DCAT**, **DataCite** (DOIs), **ORCID** (people), **CodeMeta** (software), **CITATION.cff** (citation), **Croissant** (ML datasets), **RO-Crate** (workflows/packaging), **CRediT** (contributor roles).

## Beyond data: software, workflows, models

FAIR applies to the whole research-object family, and — unlike data — software FAIR "should start… when it is initially being developed," i.e. at *early* levels. This skill therefore emits `codemeta.json` + `CITATION.cff` from L1-L2 (the CODE roadmap's *Open* and *Document* rungs: a public forge, an explicit license, identified authors, a persistent id). Deeper object-specific FAIR — a Workflow-RO-Crate + run-provenance for the pipeline, a model card + uncertainty metrics for any published model — is a documented `ROADMAP.md` extension, added when the project actually ships a workflow or a model, not forced on a small L0-L2 build.

## Artifacts it implies

→ `templates/FAIR-CHECKLIST.md.tmpl` (per-principle self-assessment; lands in `docs/`), `templates/codemeta.json.tmpl` (software metadata; repo root), `templates/CITATION.cff.tmpl` (citation; repo root). Pairs with the OKF bundle, the ARD `ai-catalog.json`, the Dataverse deposit (F1/F3/F4), and the `GOVERNANCE.md` access tiers (A1.2).

## When most relevant

Whenever the user says "make it FAIR," "FAIR data," "reusable / findable," "get a DOI," "cite this," "machine-readable metadata," or "how FAIR is this repo," or is publishing/sharing at L4-L5. Below L1 a persistent-id and rich-metadata program is premature — name it in `ROADMAP.md`.

## Caveats / tensions

FAIR is aspirational and technology-agnostic — it "precedes implementation" and prescribes no single standard, so compliance is a continuum, never a 100%-or-bust score ("one should not chase a 100% score at any cost"). FAIR is not Open (A1.2). FAIR omits quality, ethics, preservation, and governance — those come from the responsible-data / bulletproofing checklists, `installed-base`, and the (deferred) TRUST / CoreTrustSeal stewardship layer. "Domain-relevant community standards" (R1.3, I2) are field-specific and often unsettled.

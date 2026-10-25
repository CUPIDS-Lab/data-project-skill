---
type: Reference
title: The Turing Way
description: A community handbook for reproducible, ethical, inclusive, and collaborative data science, spanning reproducible research, project design, communication, collaboration, and ethics.
resource: https://book.the-turing-way.org/
tags: [reproducible, documented, transparent, inclusive, collaborative, accessible, fair, ethics]
---

# The Turing Way

The backbone handbook for the four goals: reproducible research, project design, communication, collaboration, and ethical research. Source: https://book.the-turing-way.org/

## In one paragraph

The Turing Way is a broad, community-built guide whose five guides map almost one-to-one onto this skill's goals. It supplies the definitions and checklists behind reproducibility (version control, environments, testing, FAIR data, licensing, data-management plans), inclusive and open collaboration (codes of conduct, contributor recognition, distributed leadership), accessible communication (plain language, multiple formats), and research ethics. Where other sources give concrete recipes, the Turing Way gives the principled frame and the checklists.

## Key practices (sampleable units)

- **Reproducibility stack** [reproducible] — version control with reviewable history; captured environments (containers/lockfiles); automated testing; "don't touch raw data, back up read-only."
- **FAIR data + RDM** [accessible, documented, transparent] — Findable/Accessible/Interoperable/Reusable; maintain a Data Management Plan; persistent identifiers and metadata; standardized file naming and folder structure.
- **Licensing** [transparent, accessible] — always include a LICENSE; use SPDX names; license code, data, and docs appropriately.
- **Project design** [documented] — scope → strategic planning → operational planning; identify stakeholders, risks/biases, and minimum viable products; consider preregistration.
- **Open & inclusive collaboration** [inclusive, collaborative] — code of conduct; explicit contribution pathways and recognition; distributed, transparent, accountable decision-making; design around contributors' needs.
- **Accessible communication** [accessible] — tailor to diverse audiences; plain-language summaries; multiple formats; don't assume technical expertise.
- **Research ethics** [transparent, inclusive] — consent, privacy, institutional review, governance and oversight.

## Artifacts it implies

- DMP → `templates/data-management-plan.md.tmpl`; code of conduct → `templates/CODE_OF_CONDUCT.md.tmpl`; accessibility → `templates/accessibility-checklist.md.tmpl`; licensing → `templates/LICENSE-NOTE.md.tmpl`; FAIR/openness → the L5 OKF bundle.

## When most relevant

Almost always, as the principled frame; especially when the user names reproducibility, FAIR, openness, ethics, inclusion, or accessibility. Spans L1–L5.

## Caveats / conflicts

Broad and principle-level; pair it with the concrete sources (Cookiecutter, OUHSC, Snakemake, ProPublica/Quartz) for recipes. Favors flexibility over fixed structure — reconcile with CCDS's fixed tree by treating structure as an adaptable default.

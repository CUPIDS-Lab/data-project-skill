---
type: Reference
title: Data Cards Playbook
description: A people-centered approach to dataset transparency — structured Data Cards (15 documentation dimensions) produced through a four-stage participatory process, documenting a dataset's provenance, composition, sensitive attributes, uses, and maintenance for the stakeholders who need those facts.
resource: https://sites.research.google/datacardsplaybook/
tags: [documented, transparent, inclusive, datasets, fairness, sensitive-data]
---

# Data Cards Playbook

A toolkit from Google PAIR for producing **Data Cards** — structured, people-centered transparency documentation for datasets. Source: https://sites.research.google/datacardsplaybook/ (code & templates: https://github.com/pair-code/datacardsplaybook).

## In one paragraph

A Data Card is a "structured summary of essential facts about various aspects of [a] dataset needed by stakeholders across a project's lifecycle for responsible AI development" — where the data came from, what's in it, how it was collected and transformed, what's sensitive about it, what it should and shouldn't be used for, and who maintains it. The Playbook adds a participatory *process* for deciding, with stakeholders, what to document and how deeply, and for auditing whether the result is actually transparent. It is the dataset-level transparency artifact that complements this project's field-level data dictionary, and it pairs naturally with the L5 OKF knowledge bundle.

## Key practices (sampleable units)

- **People-centered transparency** [transparent, documented, accessible] — document for the stakeholders who need the facts (publishers, dataset owners, funding sources, Data Card authors, annotators, validators) and the decisions each must make, not for a generic audience.
- **Four-stage participatory process** [inclusive, collaborative, transparent] — **Ask** (co-create the card's template with stakeholders, capturing the human decisions and invisible explanations that shape the data), **Inspect** (test the schema on real datasets, find gaps, decide what can be automated), **Answer** (fill it in for diverse audiences), **Audit** (assess completeness and transparency impact through structured review).
- **Fifteen documentation dimensions** [documented, transparent] — Summary; Authorship; Dataset Overview; Example of Data Points; Motivations & Intentions; Access, Retention & Wipeout; Provenance; Human & Other Sensitive Attributes; Extended Use; Transformations; Annotations & Labeling; Validation Types; Sampling Methods; Known Applications & Benchmarks; Terms of Art. Each dimension carries fields with guidance; right-size which dimensions a given dataset needs.
- **Document intended *and* extended/out-of-scope uses** [transparent, inclusive] — naming foreseeable misuse is part of responsible release.
- **Surface sensitive attributes & fairness** [inclusive, transparent] — the "Human & Other Sensitive Attributes" and "Access, Retention & Wipeout" dimensions force PII, protected attributes, representation gaps, and disposal to the surface.
- **Answer for diverse audiences** [accessible] — make each fact legible to non-experts as well as experts.
- **Share openly** [transparent] — the Data Cards Playbook itself is licensed CC BY-SA 4.0; release completed cards under an open license too.

## Artifacts it implies

- A dataset-level transparency card → `templates/data-card.md.tmpl`. It **complements, and does not replace,** the field-level `DATA-DICTIONARY.md`. The Playbook also offers related artifacts — Healthsheets (health datasets) and Model Cards (models) — to adapt if relevant.

## When most relevant

When sharing or publishing a dataset, for significant or sensitive datasets, and for ML training/evaluation data. Strong signal on "data card," "dataset documentation," "transparency," "sensitive attributes," "intended use," or "model card." Lives at L4 (transparency), complementing the L1 data dictionary, and pairs with the L5 OKF bundle.

## Caveats / conflicts

The 15 dimensions are comprehensive and ML-oriented, so right-size them: a small public teaching dataset may need only Summary, Provenance, and a limitations note. It complements rather than replaces the data dictionary (field-level schema) and the responsible-data checklist (process and ethics). Treat the dimensions as a menu, not a mandate.

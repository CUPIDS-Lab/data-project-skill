---
type: Reference
title: ProPublica — Bulletproofing Your Data Analysis
description: A pre-publication QA checklist for data analysis — verify integrity, recompute independently, sample against the raw source, get a colleague to replicate, and document every step.
resource: https://github.com/propublica/guides/blob/master/data-bulletproofing.md
tags: [transparent, reproducible, documented]
---

# ProPublica — Bulletproofing Your Data Analysis

A practical checklist from investigative journalism for making a data analysis defensible before you publish it. Source: https://github.com/propublica/guides/blob/master/data-bulletproofing.md

## In one paragraph

Bulletproofing is the discipline of checking a dataset and an analysis hard enough that you would stake your reputation on the result: confirm the data is what it claims to be, recompute key numbers a different way, spot-check against the raw source and against published figures, have someone else replicate it, and write down everything you did. It is the operational core of the "transparent" goal at the point of release.

## Key practices (sampleable units)

- **Integrity checks** [transparent, reproducible] — verify record counts against expected totals (watch for software row limits); GROUP BY key fields to surface spelling variants and duplicates; validate value ranges and dates; decide whether blanks are real or import artifacts, and whether zeros are real or stand in for missing.
- **Recompute independently** [reproducible] — write a different query that should give the same answer and compare; pull a random sample of results and check them against the raw data.
- **Cross-reference** [transparent] — identify and verify the original source; reconcile your totals with any published reports.
- **Gut check & outliers** [transparent] — if a result seems off it probably is; double-check surprising findings and treat outliers as leads to investigate, not noise to drop; consult a subject-matter expert when the method exceeds your expertise.
- **Independent review** [collaborative, transparent] — have a knowledgeable colleague review findings before publication.
- **Keep a data notebook** [documented] — document every procedure, decision, and filter so the analysis is reproducible and auditable.

## Artifacts it implies

- → `templates/data-bulletproofing-checklist.md.tmpl`; reinforces the "known issues" section of `templates/data-dictionary.md.tmpl`.

## When most relevant

Before publishing or communicating any finding from data. Strong signal on "publish," "verify," "fact-check," "double-check," "is this right." L4.

## Caveats / conflicts

Complements automated code tests rather than replacing them — bulletproofing is the human, against-the-source layer on top of unit tests and schema validation.

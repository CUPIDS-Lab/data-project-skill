---
type: Reference
title: ProPublica Field Guides (collaboration · contributed data · bulletproofing)
description: Three field-tested ProPublica practice sets for public-interest data work — running a multi-partner collaboration, handling contributed/crowdsourced data responsibly, and bulletproofing a data analysis before publishing.
resource: https://propublica.gitbook.io/collaborative
tags: [collaborative, inclusive, transparent, reproducible, documented, sensitive-data]
---

# ProPublica Field Guides

Three operational guides from investigative journalism, each transferable to public-interest data collaborations. Sources: the [Collaborative Journalism Playbook](https://propublica.gitbook.io/collaborative), the [Collaborate user manual](https://propublica.gitbook.io/collaborate-user-manual), and [Bulletproofing Your Data Analysis](https://github.com/propublica/guides/blob/master/data-bulletproofing.md).

## In one paragraph

These cover three distinct phases of multi-partner, public-interest data work. **Collaboration** succeeds on trust, clear communication, and a coordinator whose job is to hold it together — not on heavy contracts. **Contributed data** (tips, survey responses, crowdsourced records) inherits duties to the people who supplied it: defined intake, PII redaction, role-based access, and verify-before-cite. **Bulletproofing** is the discipline of checking a dataset and analysis hard enough to stake your reputation on the result before publishing. Together they feed the collaboration-protocol, contributed-data-intake, and data-bulletproofing scaffolds.

## Key practices (sampleable units)

**Running a multi-partner collaboration** ([Collaborative Journalism Playbook](https://propublica.gitbook.io/collaborative))

- **Select partners deliberately** [collaborative] — weigh trust, geography, specialization, reach, and scale; start with a small committed core and grow.
- **Keep agreements minimal** [collaborative] — a one-page MOU or even email suffices; cover embargo, attribution, information-sharing, and data governance; keep a level playing field so smaller partners feel equally valued.
- **Invest in a coordinator** [collaborative, inclusive] — a dedicated project manager is the most undervalued and most load-bearing role; name it.
- **Over-communicate on a cadence** [collaborative] — regular calls/updates plus one-on-one check-ins, across whatever channels partners actually use; plan for turnover.
- **Document data caveats for partners** [transparent, documented] — write "reporting recipes" that explain how to use the shared data, what it does and doesn't support, and distinguish raw from verified; require verification before anyone publishes.
- **Share credit and celebrate** [inclusive] — attribute fairly and surface partners' wins.

**Handling contributed / crowdsourced data** ([Collaborate user manual](https://propublica.gitbook.io/collaborate-user-manual))

- **Defined intake channels** [collaborative, documented] — bring contributed data in through known methods (uploads, forms, live sheets) so provenance is clear and updates flow.
- **Redact PII at import** [inclusive, transparent] — strip names, contacts, and other identifiers on ingestion; remember that redaction downstream does not change the original source.
- **Role-based / project-level access** [inclusive, transparent] — restrict users to the projects and tiers they need; separate standard users from administrators.
- **Log contributor contact** [documented, inclusive] — track outreach for accountability and to honor commitments made to contributors.
- **Deduplicate and triage** [documented] — assign, tag, and status-track records; sort/filter/export rather than analyze in place.
- **Verify before you cite** [transparent] — distinguish collected from verified; a contributed record requires verification before it informs a published claim.

**Bulletproofing a data analysis before publishing** ([Bulletproofing Your Data Analysis](https://github.com/propublica/guides/blob/master/data-bulletproofing.md))

- **Integrity checks** [transparent, reproducible] — verify record counts against expected totals (watch for software row limits); GROUP BY key fields to surface spelling variants and duplicates; validate value ranges and dates; decide whether blanks are real or import artifacts, and whether zeros are real or stand in for missing.
- **Recompute independently** [reproducible] — write a different query that should give the same answer and compare; pull a random sample of results and check them against the raw data.
- **Cross-reference** [transparent] — identify and verify the original source; reconcile your totals with any published reports.
- **Gut check & outliers** [transparent] — if a result seems off it probably is; double-check surprising findings and treat outliers as leads to investigate, not noise to drop; consult a subject-matter expert when the method exceeds your expertise.
- **Independent review** [collaborative, transparent] — have a knowledgeable colleague review findings before publication.
- **Keep a data notebook** [documented] — document every procedure, decision, and filter so the analysis is reproducible and auditable.

## Artifacts it implies

- Collaboration → the collaboration-protocol section of `templates/CHARTER.md.tmpl`; complements `templates/GOVERNANCE.md.tmpl` and the `data-collaborative-canvas`.
- Contributed data → the contributed-data-intake section of `templates/data-management-plan.md.tmpl`; reinforces `templates/responsible-data-checklist.md.tmpl` and the governance access tiers.
- Bulletproofing → `templates/data-bulletproofing-checklist.md.tmpl`; reinforces the "known issues" section of `templates/data-dictionary.md.tmpl`.

## When most relevant

Multi-organization or cross-institution collaborations and onboarding partners — "partners," "collaboration," "consortium," "onboarding," "shared data" (L3). Whenever the project accepts contributed/crowdsourced data — "tips," "submissions," "crowdsource," "survey responses," "contributed data" (L3, couples with sensitivity duties). Before publishing or communicating any finding from data — "publish," "verify," "fact-check," "double-check," "is this right" (L4).

## Caveats / conflicts

Journalism-born; generalize "newsroom" to "collaborating organization." The collaboration playbook is operational where the Data Collaboratives Canvas is strategic — use them together. Contributed-data source/contributor protection is a floor, not a ceiling — privacy law and CARE still govern. Bulletproofing complements automated code tests rather than replacing them — it is the human, against-the-source layer on top of unit tests and schema validation; pair it with the `quartz-bad-data-guide` failure-mode taxonomy.

---
type: Reference
title: Responsible Data
description: The Responsible Data Handbook's lifecycle approach to consent, privacy, security and ownership, and how the responsible-data checklist is used — filled during scoping, before sensitive features are built.
resource: https://responsibledata.io/resources/handbook/
tags: [responsible-data, ethics, privacy, consent, sensitive-data, checklist]
---

# Responsible data

Read this in Outline section 1 (Scope & gate) whenever data implicates people, and again before any sensitive feature (an identifier scheme, a linkage, a retention rule, a release) is built. It digests the Responsible Data Handbook (<https://responsibledata.io/resources/handbook/>) and says how its checklist is used. The hard gates (privacy law and CARE) and the sensitivity tiers are in `values-and-gates.md`; the access tiers and remedy path are in `governance.md`.

## In one paragraph

Responsible Data frames data work around the rights and risks of the people the data is about. It walks the lifecycle from project design through getting, understanding and sharing data to closure, and asks at each stage what could go wrong and for whom. It drives the sensitivity-tier logic that fires the affordance-duty coupling, and it supplies the questions behind the responsible-data checklist. It is advisory, not a substitute for legal compliance: privacy law and CARE remain the gates.

## Key practices

- **Lifecycle lens** [transparent, inclusive] — design → getting → understanding → sharing → closure. Ask the responsible-data questions at *each* stage, not once, because a harm introduced at intake is cheapest to prevent there and most expensive to undo at release.
- **Consent that is real** [inclusive, transparent] — freely given, specific, informed and revocable. Record the purpose, retention, sharing and people's rights in terms they can understand, and track consent over time.
- **Data minimization and purpose limitation** [transparent] — collect and keep only what the stated purpose needs; nothing gathered "just in case."
- **Risk and harms assessment** [transparent, inclusive] — enumerate harms (re-identification, profiling, discrimination, misuse) by lifecycle stage, rate likelihood and severity, and plan mitigation and monitoring for the ones that matter.
- **Security and access** [transparent] — encryption at rest and in transit as warranted, least-privilege access, audit, and a breach-response path; protect sensitive traces.
- **Closure** [transparent] — retention schedules, secure disposal, and a final communication to the people the data is about and to partners.

## How the checklist is used

The responsible-data checklist (data-project's `responsible-data-checklist.md.tmpl`, generated into the project when section 1 classifies the data as anything above `public`, or when it is contributed data) works only when it gates a decision at the moment the decision is made.

- **Fill it during scoping, from the scoping conversation, before sensitive features exist.** The questions it asks (purpose, consent, minimization, legal regime, whose risks are centered) are cheap to answer before an identifier scheme or a linkage is built and expensive to retrofit afterward.
- **Don't generate it unfilled.** Evidence: in the one project where the checklist was filled from the scoping interview before the sensitive features were built, every item was completed and kept. In another project, checklists generated as a bundle sat at 0 of 65 boxes checked months later. A checklist that arrives as boilerplate rots.
- **When there is a team, offer it as an issue task list first**, linked from the section 1 issue, and as a file only when it must ship with a release or deposit.
- **Revisit it at each later gate.** Before section 8 (Publish) or section 9 (Deposit, share & discover), reread the Sharing and Closure stages and confirm nothing new (a linkage, a new source, a partner) changed the answers. Conditional sensitivity reopens it when the named trigger event happens.
- **Record decisions, not just ticks.** Each non-obvious answer (why a field is retained, why a release is aggregated, why consent was judged sufficient) gets a decision-log entry, tagged *Private* when its details cannot be shared.

### What the checklist covers, by stage

- **Design.** The purpose and the specific questions, stated narrowly enough to test collection against them; design partners named separately from beneficiaries, with whose risks are centered; the applicable legal and ethical regimes (privacy law, IRB or ethics approval, CARE) identified and confirmed satisfiable; the transparency-versus-privacy tradeoff made legible rather than left to defaults.
- **Getting.** Consent is real (as above) and tracked; minimization and purpose limitation applied; the authority and license to use, transform and share each source confirmed before ingesting it; provenance and chain of custody recorded on ingestion; raw sensitive data and credentials kept out of the repository.
- **Understanding.** Harms assessed by stage (re-identification, profiling, discrimination, misuse), each rated for likelihood and severity with a mitigation and monitoring plan; re-identification risk checked specifically (can individuals be singled out by combining quasi-identifiers or by linking to outside data?); subject-matter knowledge brought in so categories and patterns are not misread in ways that harm the people behind them; known limitations and biases documented in the data dictionary.
- **Sharing.** Security and least-privilege access in place, with access and changes audited and a breach-response path defined; the governance access tier applied (what is public, what is restricted, who may touch sensitive traces); data desensitized or aggregated before release, with out-of-scope uses and foreseeable misuses named; anything touching sensitive traces routed through the governance escalation rules before release; no hosted service (OCR, model API, publishing platform) sent documents the sensitivity decision forbids.
- **Closure.** A retention schedule tied to the stated purpose, with secure disposal by a named custodian; the wind-down communicated to the people the data is about and to partners, as the consent and relationship require; what survives the pilot (named custodians, ongoing duties) stated, so the project ends deliberately rather than eroding.

## Whether versus how: PII mechanics

The checklist decides *whether* something may be collected, linked, retained or released. data-liberation's PII redaction step (its `pipeline.md`, "PII redaction") is the *how*: drop identifiers never needed downstream, hash with a project-secret salt when needed for joins, generalize when needed for display but not precision (ZIP to ZIP3, date of birth to year), and keep only identifiers that are load-bearing for accountability, with the legal basis recorded in the data dictionary. Redaction is a publish-time transform: never redact inside `data/original/`, whose hashes assume the files are byte-identical to what the publisher released. Apply the gate first; redaction carries out its verdict, it doesn't substitute for it.

## When most relevant

Whenever data implicates people: strong signals are "sensitive," "PII," "consent," "vulnerable," "human subjects," "survey responses," "tips" or "contributed data." The sensitivity coupling overrides leanness even for a small project.

## Caveats

Advisory, not a legal compliance substitute; the hard gates remain privacy law and CARE. Scale the artifacts to sensitivity: a public dataset of already-public records needs little of this beyond a sentence in the README and the out-of-scope-use declaration.

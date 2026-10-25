---
type: Reference
title: Governance
description: Governance for both skills — roles, access tiers, license inheritance, PII policy, data-subject considerations, correction and remedy paths, contributed-data intake, project-internal rules, and honest governance for solo and small teams.
tags: [governance, roles, access-tiers, license, pii, remedy, contributed-data, branch-protection]
---

# Governance

Read this in Outline section 7 (Govern & collaborate), and in section 1 when the data is sensitive (the gates and tiers are in `values-and-gates.md`). It says who may touch what, under what license, how people represented in the data can get a correction, and how to write governance that is true. data-project's `GOVERNANCE.md.tmpl` is the project-side artifact; the collaboratory typology, the five core roles and the charter decisions are in data-project's `collaboration-architecture.md`.

## Contents

- [Honest governance first](#honest-governance-first)
- [Roles](#roles)
- [Access tiers](#access-tiers)
- [License inheritance](#license-inheritance)
- [PII policy](#pii-policy)
- [Data-subject considerations](#data-subject-considerations)
- [Correction and remedy paths](#correction-and-remedy-paths)
- [Contributed-data intake](#contributed-data-intake)
- [Project-internal governance](#project-internal-governance)
- [Retention, oversight and transparency versus privacy](#retention-oversight-and-transparency-versus-privacy)
- [Where these decisions land](#where-these-decisions-land)

## Honest governance first

Governance documents are only worth what they truthfully describe. The evidence from the projects these skills served: eight of nine had no second human reviewer; in two, governance that said owners confirm "by approving this PR" was itself merged with zero reviews; in five of six solo-run projects there were no issues at all, and the real record was PR bodies plus a decision-log; and in a two-person sprint every decision happened in issue comments and none reached the CHARTER, GOVERNANCE or checklists that claimed to be the source of truth.

So:

- **Claim a review gate only when it is enforced.** Any rule of the form "owners approve by PR," "changes to the schema need two reviews," or "CODEOWNERS must sign off" ships together with the branch-protection step that enforces it (on GitHub: a ruleset or branch protection on the default branch requiring pull requests, the stated number of approvals, and code-owner review where CODEOWNERS is claimed). If branch protection is not available or not wanted, don't write the rule.
- **Solo projects get a single-steward statement.** Say plainly: "This project has one steward, `<name>`, who makes and records all decisions. There is no second reviewer; review happens through the PR body checklist and the audit outputs." Don't scaffold pretend review gates, approval tables or quorum rules for a team of one. Add them when a second person joins.
- **The working record is PRs, issues and the decision-log.** Decision-log entries link the issue or PR where the decision happened. Solo PR bodies use four headings: *What changed / Why / What I checked / Left alone on purpose*.
- **Generate governance documents only when collaborators or sensitive data exist,** and for onboarding several people, prefer a short tested tutorial series over more governance documents.

## Roles

Name the roles the project actually has, and say which are unfilled.

- **Core roles** for a collaboration: data engineer, software developer, subject-matter expert, mediator (translates between technical and subject-matter views), and project manager or coordinator (the most undervalued, most load-bearing role). Auxiliary roles: infrastructure, statistics, legal.
- **The steward** (or stewards) holds the decision-log, the remedy path and the access list. In a solo project, the steward is every role; say so.
- **The gap check.** If a core role is unfilled, write it down (in the charter for a team, in the README's governance note for a solo project) and make filling it a priority rather than papering over it. A role nobody holds is a duty nobody performs.
- **Custodians.** Name who carries retention, disposal and migration duties, and who takes over if they leave. This is the stewardship-continuity element of the values spine.
- **Map roles to paths** with `CODEOWNERS` only when review by those roles is enforced (see above); otherwise list the mapping in the README so responsibility is legible without pretending it is gated.

## Access tiers

Access is documented and tiered so that visibility is legitimate rather than ambient: what is open is deliberately open, and what is restricted is reachable only by accountable people. Least privilege is the default.

| Tier | What it covers | Who may access | How access is granted |
| --- | --- | --- | --- |
| Public | Processed, non-sensitive outputs and documentation in open formats (only if visibility is public, or after an embargo lifts). | Anyone. | No request needed. |
| Restricted | Interim data, partner-shared data, anything not cleared for public release, and everything in a private project. | Named project members and approved collaborators. | Request to the steward or project manager; logged. |
| Sensitive | Identifiable, regulated or otherwise sensitive traces. | A named, minimal set of accountable intermediaries. | Documented approval; access logged and time-bound. |

Partner access in section 9 (OpenSharing shares, restricted Dataverse files) is declared under these tiers, never outside them. Secrets and sensitive data never land in the repository; desensitize before anything leaves the controlled tier.

## License inheritance

The source's license is not the project's license. Publishers attach terms (open-records conditions, "non-commercial use," "no redistribution without attribution") that the project must propagate or honor.

- **Identify each source's license** in the publisher's terms of use, the records-request response letter or the dataset metadata. If unclear, ask the records officer. Record it in `provenance.csv` (a `source_license` column or the extraction notes).
- **Pick the project's license deliberately.** Defaults: CC-BY-4.0 for data, MIT for code, CC-BY-4.0 for documentation. Ship a `LICENSE` file and explain the per-layer choice in the README's License section. If a source's terms preclude CC-BY, name the more restrictive license and say why.
- **No laundering by tidying.** Repackaging restricted data into a tidy CSV doesn't strip its terms. If a source carries "non-commercial" forward, the processed output does too.
- **Private projects still license.** A private repository needs a stated license or terms for collaborators, so that what partners may do with shared data is not ambiguous.

## PII policy

Decide in section 1 which personal information the project holds and why; the responsible-data checklist (`responsible-data.md`) decides whether, and the pipeline's redaction step carries out the decision.

- Identifiers never needed downstream are dropped; identifiers needed for joins but not display are hashed with a project-secret salt (document the function, never commit the salt); identifiers needed for display but not precision are generalized; identifiers load-bearing for accountability (elected officials acting in office, public-record case parties) are kept with the legal basis recorded in the data dictionary.
- Redaction happens at publish time, never in `data/original/`.
- PII never goes to a hosted OCR, model or publishing service unless the sensitivity decision explicitly allows it.
- Record the policy where it is enforced (the publish or redaction code) and where it is read (the data dictionary's per-column caveats).

## Data-subject considerations

Some sources contain information about people who did not consent to be in the dataset. Redaction handles obvious identifiers; the harder questions are these.

- **Identify the data subjects.** Records about employees (personnel records), residents (incident reports, service requests), defendants (court filings, arrest records), patients, beneficiaries, contributors. Each carries different ethical and legal weight.
- **Apply the right-to-erasure analog where it exists.** GDPR Article 17, CCPA and some agencies' correction-and-deletion procedures. Document the project's response path, typically a PR that adds an `erasure_log.csv` entry and propagates the removal downstream on the next refresh (and to any deposit as a new version).
- **Honor parallel sovereignty frames.** For data about Indigenous communities, CARE sits alongside FAIR (see `values-and-gates.md` for the decision order). For other historically surveilled populations, ask whether the affected community would endorse the work, and record the answer in `AGENTS.md` and the decision-log.
- **Declare out-of-scope uses** in the README and `AGENTS.md`.

## Correction and remedy paths

A documented problem must have a path to becoming a correction, or oversight is theater. Every project with outputs other people use needs one, scaled to its size.

- **An error-reporting path.** The README names how a downstream user or a person represented in the data flags a problem: a data-correction issue form, an email address, or both (an email for anyone who should not have to post publicly). State how a concern is acknowledged and in what timeframe, who reviews it, how it escalates if unresolved, and how the outcome is communicated back. Make it accessible, protective of the person raising it, and consequential.
- **Correction propagation.** A confirmed fix lands in the next refresh PR or an explicit hotfix PR; `provenance.csv` keeps the original and corrected hashes visible; `CHANGELOG.md` names the affected vintages. No silent rewrites.
- **Citation guidance.** `CITATION.cff` and a vintage or release tag, so a corrected dataset doesn't silently displace what someone cited.
- **Retraction-equivalent path.** If a vintage is unsalvageable (the source was withdrawn; a parser bug affected most rows), document the retraction in the changelog and keep the bad data in Git history or the prior deposit version. Don't quietly delete: someone may have cited it.
- **Transparency about outcomes.** Record what was raised and what happened (without identifying the person raising it), so the process is trusted enough to be used.

## Contributed-data intake

Contributed data (tips, survey responses, crowdsourced records, partner uploads) inherits duties to the people who supplied it. When a project accepts it, section 1 raises its sensitivity by default and section 7 writes an intake section into the data-management plan.

- **Defined intake channels** (uploads, forms, live sheets) so provenance is clear and updates flow.
- **Redact PII at import**, remembering that downstream redaction does not change the original submission.
- **Role-based, project-level access**, separating standard users from administrators.
- **Log contributor contact** for accountability and to honor commitments made to contributors.
- **Deduplicate and triage**: assign, tag and status-track records rather than analyzing in place.
- **Verify before citing**: a contributed record is "collected" until verified, and only verified records inform a published claim.

This is a floor, not a ceiling: privacy law and CARE still govern.

## Project-internal governance

Once a project is live it has its own governance surface: who may change the schema, who reviews refresh PRs, how disagreements are resolved.

- **Schema revisions are contract changes.** Changes to the canonical column list or the schema class require a `CHANGELOG.md` entry and a paragraph naming what breaks for downstream users.
- **Concept-catalog amendments** (a new cross-source equivalence) require a non-empty caveats list naming what is and isn't comparable.
- **Refresh-PR review norms.** Name who reviews refresh PRs and what they check: the row-count delta in the audit summary, new extraction errors, newly empty sources, new reconcile mismatches. For a solo project, the steward checks the same list in the PR body.
- **Conflict resolution.** Contributors from different functions will disagree about schema choices and caveats; that is the substrate, not a failure. Name the escalation path in `AGENTS.md`, and prefer a "minority report" field in the dictionary or a `disputes/` log to litigating in PR comments.
- **Decision-making.** Routine matters are decided by the role owning the affected path; larger decisions by consensus of the core roles with a named tie-breaker (or by the steward in a solo project). Non-obvious decisions go in the decision-log, tagged *Assumed* or *Private* where they apply.

## Retention, oversight and transparency versus privacy

- **Retention schedule.** State how long raw, interim and sensitive data are kept, the disposal or wipeout method, and who carries it out; review the schedule on a stated cadence so it doesn't drift into indefinite retention.
- **Contestable oversight.** Record what is logged (access to restricted and sensitive tiers, data and schema changes, releases), who holds audit rights, and how often logs are reviewed. At least one named role is authorized to interpret and contest the evidence, not merely receive it.
- **Transparency versus privacy.** Default to openness for non-sensitive aggregate findings (when visibility allows), default to protection for anything identifiable, and resolve specific tradeoffs deliberately with the reasoning in the decision-log. When they genuinely conflict, the duty to the people in the data comes first.
- **Values spine.** For a sensitive or multi-party project, `GOVERNANCE.md` closes with the three pressures, six installed-base elements and the affordance-duty coupling from `values-and-gates.md`, each pointed at the section of the file that answers it.

## Where these decisions land

| Decision | Lives in |
| --- | --- |
| Sensitivity tier, visibility, privacy-law screen, CARE check | decision-log (section 1); `ROADMAP.md` blocking rows if conditional |
| Roles, steward, gap check | README governance note (solo) or `CHARTER.md` (team) |
| Review gates | `CONTRIBUTING.md` plus the branch-protection step that enforces them; never one without the other |
| Access tiers, retention, oversight, remedy | `GOVERNANCE.md` (only with collaborators or sensitive data); otherwise a README paragraph |
| Source and project licenses | `LICENSE`, README License section, `provenance.csv` |
| PII policy | the redaction or publish code, and data-dictionary per-column caveats |
| Out-of-scope uses | README and `AGENTS.md` |
| Error reporting and corrections | README, the data-correction issue form, `CHANGELOG.md` |
| Contributed-data intake | the data-management plan's intake section |
| Schema and concept revisions, refresh review | `AGENTS.md`, `CHANGELOG.md`, the refresh PR body |

Fill these before the project ships a first vintage, release or deposit, not after the first complaint.

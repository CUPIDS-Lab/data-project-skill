---
type: Reference
title: Escalation Levels (L0–L5) and the Entry Protocol
description: The graded ladder that keeps every run right-sized, the Infer→State→Execute→Offer entry protocol, and the now/later/skip mechanism that defers work into ROADMAP.md.
tags: [levels, right-sizing, workflow, roadmap]
---

# Escalation Levels (L0–L5) & Entry Protocol

Read this to decide *how much to build now*. The ladder is the core right-sizing device: a project enters at the lowest level that meets its need and climbs only as far as the task actually requires. Most projects live at L0–L2. Higher rungs are opt-in, and anything not built now is documented in `ROADMAP.md` rather than silently generated.

## The ladder

Each level *adds* to the levels below it. A run instantiates only the "now" set for its chosen level (minus anything the user defers).

| Level | Theme | Adds now (typical) | Primary goals |
| --- | --- | --- | --- |
| **L0** | Structure | repo skeleton, `README`, `AGENTS.md`, `.gitignore`/`.gitattributes`, `data/{raw,interim,processed}` (`.gitkeep`, raw immutable), `ROADMAP.md` | Reproducible |
| **L1** | Document | `DATA-DICTIONARY` (tidy/FAIR; identifiers, derived variables, units, missingness, known-issues/caveats), `decision-log`, `CHANGELOG`, expanded `README` | Documented |
| **L2** | Reproduce | pinned environment, pipeline-as-code (`Snakefile` / `_targets.R`), `config`, `exploratory/` (notebooks live here only), CI dry-run | Reproducible |
| **L3** | Collaborate | `CONTRIBUTING` (anti-pattern guardrails), `CODE_OF_CONDUCT`, `ROLES`+`CODEOWNERS`, `GOVERNANCE`, `CHARTER`, `collaboration-protocol`, `contributed-data-intake`, nested `.skills/` | Collaborative, Inclusive |
| **L4** | Responsible & accessible | `INSTALLED-BASE`, `data-management-plan`, `responsible-data-checklist`, `data-bulletproofing-checklist`, `data-quality-checklist`, `accessibility-checklist` | Transparent, Accessible, Inclusive |
| **L5** | Publish as open knowledge | `knowledge/` OKF bundle (from the data dictionary), FAIR/CARE, `LICENSE-NOTE`, `data-collaborative-canvas`, `ai-catalog.json` + `DISCOVERY.md` (ARD agent-discovery; host `.well-known/` + registry deferred to `ROADMAP`), `dataverse/` deposit kit (Harvard Dataverse → citable DOI; draft until confirmed; periodically-updated data re-deposits as new versions on a schedule), optional publish surfaces | Accessible, Transparent |

Levels describe *depth*. They are orthogonal to *which* concerns matter, which is set by the collaboratory type and the data-sensitivity tier (see `collaboration-architecture.md` and `installed-base.md`). A sensitive L1 project, for example, still triggers the affordance↔duty coupling even though it is shallow. Note that automated checks (CI) first appear at **L2**: at L0/L1 there is no pipeline or CI, so there is nothing to "verify/watch after merge" at those rungs — verification there is the scaffold check itself (no unfilled tokens, links resolve).

## Entry protocol: Infer → State → Execute → Offer

1. **Infer** the lowest level that meets the need from the user's phrasing. "Get me a clean repo for this CSV" reads as L0/L1; "make it reproducible" as L2; "we're onboarding partners" or "this is sensitive" as L3+. When the user names a level explicitly, jump to it.
2. **State** the assumption and offer a one-sentence redirect, e.g. *"This reads like L1 — a documented repo. I'll start there unless you want the reproducible-pipeline path (L2)."* Do not silently pick a heavy level.
3. **Execute** that level fully. Keep L0/L1 genuinely lightweight — no pipeline, governance, or knowledge-bundle bloat at those rungs.
4. **Offer** the next rung on completion, e.g. *"Done. Want to go to L2 and add a pinned environment + pipeline so this re-runs on new data?"* Climbing is always the user's choice.

When signals span levels, start at the lowest prerequisite and climb, confirming at each rung rather than jumping to the ceiling.

## The now / later / skip mechanism

For every concern that sits *above* the chosen level, the interview offers three dispositions: **implement now** (pull it down into this run), **document for future** (record it in `ROADMAP.md` with what it is, why it's deferred, and which template/level adds it later), or **skip** (out of scope; not recorded). This is what keeps any single run small while still making the full menu discoverable. Defaulting a concern to "later" is usually the right call — a named, deferred concern beats an unmaintained file. The synthesizer is expected to prefer `ROADMAP.md` entries over generated files whenever it is unsure. A fourth shade applies to sensitivity specifically: **conditional** — a concern that is irrelevant now but *becomes blocking when* a named event occurs (e.g. "becomes sensitive once the corpus ingests PII"). Record it as a **blocking** `ROADMAP.md` row that names the trigger, so it gates the future build without firing governance today (see the deferred-but-enforced coupling in `installed-base.md`).

## Audit (the second entry point)

Auditing an existing repository reuses the same ladder in reverse: score what the repo already has against each level and goal, report the gaps in priority order with citations, check OKF conformance if a `knowledge/`-style bundle exists, and then offer to scaffold the missing rungs. Audit is read-only until the user approves remediation.

---
type: Reference
title: Background and Context
description: Why this skill exists, the design principles it encodes, the hard gates it respects, and how it relates to the sibling data-liberation skill.
tags: [context, values, cupids, fair, care]
---

# Background & Context

Read this when you want the *why* behind the scaffolds: the mission this skill serves, the principles it encodes, the few hard constraints it never crosses, and how it fits alongside the lab's other tooling. Everything here is operational stance, not literature notes.

## Mission

This skill belongs to CUPIDS — the CU (University of Colorado) Public Interest Data Science Lab/Clinic. It exists to help small, interdisciplinary, often short-lived teams stand up data projects that other people — collaborators, affected communities, future maintainers, downstream agents — can actually understand, trust, reuse, and contest. The four goals it optimizes are **accessible, documented, transparent, and inclusive**, with **collaborative** and **reproducible** as the cross-cutting enablers that make the other four real.

The animating worry is *accountability theater*: a project that ships impressive affordances — stable identifiers, retention, dashboards, audit logs — without the duties and governance that make those affordances contestable. Affordances without duties are theater. The skill's job is to keep the two coupled, especially when data touches people who can be harmed.

## Design principles (mirrored from the sibling, adapted for project architecture)

- **Right-size, always.** Scaffold for the team and horizon that exist, not an imagined enterprise. Over-engineering a three-person, one-semester project is its own failure mode. When in doubt, build less now and write the rest into `ROADMAP.md`.
- **Raw data is immutable — but *immutable* and *tracked* are separate choices.** Original sources are never edited in place and every transformation is reproducible from the original; this is why the canonical tree separates `data/raw` from `data/interim` and `data/processed`. Distinguish two kinds of raw: **bulk / external / re-downloadable** inputs stay git-ignored (out of history, refetched by the pipeline), while a **curated source-of-record** — a small, hand-made catalog or seed file that *is* the project's asset — is tracked via a `.gitignore` carve-out and documented as immutable in the data dictionary and decision log. Don't git-ignore the project's only data.
- **Documentation is half the work.** A dataset without a data dictionary, provenance, and a decision trail is a private spreadsheet. Documentation lives next to what it documents, and it is written for someone who has none of the project's context.
- **Audit against originals.** Reconciliation against the source's own published totals — "bulletproofing" — is what makes a dataset defensible. Surprising results get double-checked before they get shipped.
- **Center the partners doing the work**, named separately from the abstract beneficiaries. The scaffold serves the people in the room and the communities they answer to, not a generic "the public."
- **Make tradeoffs legible** rather than burying them in defaults — above all the transparency-versus-privacy tension, which most public-interest data work has to manage rather than resolve.

## The only hard gates

Almost everything this skill offers is advisory — a vocabulary for naming work and a menu for extending it. Hold exactly two things as non-negotiable: **privacy and data-protection law** (e.g. GDPR, CCPA, FERPA/HIPAA where relevant) and the **CARE Principles for Indigenous Data Governance** (Collective benefit, Authority to control, Responsibility, Ethics). These can constrain or redirect what may be collected, linked, retained, or published. When the interview marks data as sensitive or implicating vulnerable or Indigenous populations, these gates dominate the defaults and the affordance↔duty coupling fires automatically (see `installed-base.md`).

## Standards, practiced informally

The skill informally practices standards it does not mandate: provenance records resemble W3C PROV; dataset metadata mirrors DCAT; data-quality notes parallel the Data Quality Vocabulary; openness aims at FAIR (Findable, Accessible, Interoperable, Reusable). The point is honest citation, not conformance as a precondition for shipping — a tidy CSV with a data dictionary and a provenance trail is already doing most of the work these standards exist to encourage. At L5 the skill goes one step further and can emit a knowledge bundle in the **Open Knowledge Format (OKF)**; see `okf-open-knowledge-format.md`.

## Relationship to the sibling `data-liberation` skill

`data-liberation` and `data-project` are complementary halves of the same lab toolkit. **`data-liberation` gets the data out and tidy** — it turns government PDFs, FOIA releases, scraped HTML, and panel spreadsheets into tidy, documented, reproducible datasets (its workflow is Survey → Scaffold → Extract → Tidy → Audit → Publish, deliberately stopping before modeling). **`data-project` architects the collaboration, governance, and knowledge layer *around* that data.** A liberated dataset is a natural input to this skill; a project scaffolded here is a natural home for data-liberation's outputs. The shared hand-off point is the knowledge layer: data-liberation's L3 "concept catalog / crosswalk" and the OKF bundle this skill emits at L5 are the same idea, so the two compose without friction. Both are portable Agent Skills (Claude Code, Copilot, Cursor, and other AgentSkills clients), both MIT-licensed, both organized as a single `SKILL.md` with on-demand `references/`.

**The working shape is a monorepo of pipelines.** In practice a `data-project` repo hosts *N* `data-liberation` pipelines — one per liberated source — each under `pipelines/<name>/` (its own `Snakefile`, `config`, and tidy output) and each mapped 1:1 to a tracked issue or sub-issue under the umbrella `ROADMAP.md`/board, so the project board shows liberation progress source by source (e.g. a "water-data" epic decomposed into reservoir / streamflow / snowpack sub-issues, one per `pipelines/<name>/`). On the `src/` vs `scripts/` question the two skills could diverge on: standardize repo-wide, importable, tested code in **`src/<pkg>/`** (this skill's convention, for testability and clean imports); a nested `data-liberation` pipeline's own extractor `scripts/` may stay local to its `pipelines/<name>/` directory, but shared code belongs in `src/<pkg>/`. Stating that rule is not the same as enforcing it: once a repo crosses ~3 pipelines, factor the domain-agnostic plumbing into a shared core rather than copy-pasting it into each sibling — see `references/stamping-and-shared-core.md` for what to share, where it lives, and how to stamp a new pipeline from the pattern. (The sibling `data-liberation` skill lives in its own repo; aligning *its* template's default `scripts/` location is a follow-up there, out of scope for this skill.)

## CUPIDS default infrastructure profile (overridable)

When the user signals CUPIDS or does not specify infrastructure, default — overridably — to a **Datasette** catalog, **Cloudflare R2** object storage, a **Quarto** front-end, **Prefect** orchestration, and **CU Research Computing** for heavier compute. Treat these as defaults the user can swap, and keep the *generated repo's core stack-agnostic* (plain-text, version-controllable formats; no vendor-locked artifact as a required dependency; anything a hosted tool produces must be exportable). Lock-in is itself a form of enclosure, so name the assumptions you are swapping when you localize.

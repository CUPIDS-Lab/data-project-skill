---
type: Reference
title: Practice Sources
description: Digests of the external practice guides both skills draw on — Cookiecutter Data Science, OUHSC BBMC, The Turing Way, the USDS Digital Services Playbook, the Data Collaboratives Canvas, the Data Cards Playbook, the Quartz Bad Data Guide, ProPublica's field guides and Snakemake — each tagged with the Outline sections it informs.
tags: [practices, structure, reproducible, collaboration, documentation, data-quality, pipeline, sources]
---

<!-- Vendored from shared/references/practice-sources.md by tools/vendor.py. Edit shared/references/practice-sources.md, not this copy. -->

# Practice sources

Read the section for a source when its Outline section is in scope and you want the external practice behind a convention, or a citation for it. Each section keeps its source's substance: what it says, its key practices (tagged with the goals they serve: accessible, documented, transparent, inclusive, collaborative, reproducible), the artifacts it implies, when it is most relevant, and its caveats. Where a source's advice differs from the skills' canonical project shape (uv + `pyproject.toml`, code in `scripts/`, originals in `data/original/`), the caveat says how the two are reconciled.

## Contents

| Source | Informs Outline sections | Gives you |
| --- | --- | --- |
| [Cookiecutter Data Science](#cookiecutter-data-science) | 4 Model & tidy, 5 Pipeline & audit | A predictable layout and a few firm rules for reproducibility |
| [OUHSC BBMC Data Science Practices](#ouhsc-bbmc-data-science-practices) | 4, 5, also 1 and 7 for sensitive data | Concrete naming, script structure, defensive validation, the public/unshared split, team norms |
| [The Turing Way](#the-turing-way) | 6 Document & cite, 7 Govern & collaborate, also 1 | The principled frame and checklists for reproducible, open, inclusive, ethical work |
| [USDS Digital Services Playbook](#usds-digital-services-playbook) | 1 Scope & gate, also 8 | User-centered framing, iterative delivery, accessibility, default-to-open where visibility allows |
| [Data Collaboratives Canvas](#data-collaboratives-canvas) | 1, also 7 | Strategic planning for multi-partner, cross-sector collaborations |
| [Data Cards Playbook](#data-cards-playbook) | 6, also 1 for sensitive attributes | Dataset-level transparency documentation and a participatory process for it |
| [Quartz Bad Data Guide](#quartz-bad-data-guide) | 5, also 2 and 3 | A "who should fix it" taxonomy of data problems |
| [ProPublica field guides](#propublica-field-guides) | 7 (collaboration), 2 and 7 (contributed data), 5 (bulletproofing) | Running a collaboration, handling contributed data, bulletproofing before release |
| [Snakemake](#snakemake) | 5 | An optional workflow wrapper over the pipeline command |

## Cookiecutter Data Science

Source: <https://cookiecutter-data-science.drivendata.org/>. Informs sections 4 and 5.

**In one paragraph.** Cookiecutter Data Science (CCDS) is a conventional directory layout plus a short set of opinions about how analysis projects should be organized so that anyone can clone the repository and find their way around. Its core claim is that consistency and a few firm rules (raw data is immutable; data is not in version control; notebooks explore while source code reproduces) buy reproducibility and shareability cheaply.

**Key practices**

- **Standard directory tree** [reproducible, documented] — `data/{raw,interim,processed,external}`, `notebooks/`, a source package, `reports/figures/`, `references/`, `models/`, `docs/`. A predictable layout means low onboarding cost.
- **Treat the analysis as a DAG** [reproducible] — outputs trace back to inputs through versioned steps, so any product can be recreated from raw.
- **Raw data is immutable** [reproducible, transparent] — never edit raw in place; read it and write to interim or processed. Originals can always regenerate derived data.
- **Data is excluded from version control** [reproducible] — `.gitignore` blocks `data/`; large data lives in object storage or Git LFS.
- **Notebooks explore, source code reproduces** [reproducible, documented] — refactor reusable logic out of notebooks into tested, importable code; notebooks are numbered and exploratory.
- **Environment reproducibility** [reproducible] — pin dependencies; consider containers for complex needs.
- **Secrets in `.env`, never in code** [transparent] — load with `python-dotenv`; `.env` is git-ignored.

**Artifacts it implies.** The canonical project tree (data-liberation's `project-template.md`), the data-aware `.gitignore`, the pinned environment (`pyproject.toml` plus `uv.lock`), and an `exploratory/` folder for numbered notebooks with output stripping (`nbstripout`).

**When most relevant.** Any Python-leaning project; strong signal on "set up a repo," "project structure" or "make this shareable."

**Caveats.** CCDS prescribes a fairly fixed tree; The Turing Way favors flexibility. Treat the tree as a sensible default to prune or extend. The skills' canonical shape maps CCDS's `data/raw` to `data/original/`, adds `data/audit/` and `data/lookups/`, and keeps code in `scripts/` run as `python -m scripts.pipeline run`. It departs from "data is excluded from version control" deliberately: whether the processed CSV and audit summaries are tracked is a stated storage decision in section 2, because a refresh PR that can't carry the data or audit diff can't be reviewed. CCDS is Python and notebook-centric; for R projects, prefer the OUHSC layout.

## OUHSC BBMC Data Science Practices

Source: <https://ouhscbbmc.github.io/data-science-practices-1/>. Informs sections 4 and 5, and sections 1 and 7 when data is sensitive.

**In one paragraph.** A detailed, opinionated practices guide from the OUHSC Biomedical and Behavioral Methodology Core, strong on naming, coding discipline, sensitive-data handling and team norms (R and SQL-leaning but language-agnostic in spirit). It encodes how a careful research-data team actually works day to day: a public/unshared data split that prevents leakage, exact naming conventions that make joins and reviews legible, a linear file structure that keeps scripts predictable, defensive validation as you go, and review norms that catch problems early. It is the best source for the concrete conventions the other frameworks gesture at.

**Key practices**

- **Public versus unshared data separation** [transparent, inclusive, reproducible] — `data-public/` for non-sensitive data and `data-unshared/` for sensitive or local-only data, with a committed `contents.md` manifest (commit the manifest, never the sensitive data). Prevents accidental leakage.
- **Stable naming conventions** [documented, collaborative] — snake_case variables; kebab-case files; dataset prefixes (`ds_` file scope, `d_` function-local) that express the grain (`ds_pt_visit`); ISO 8601 dates; repository names as `[pi]-[topic]-[index]`.
- **Linear, predictable script structure** [reproducible, documented] — clear memory → load sources → load packages → declare globals → load data → tweak → analyze → verify → select outputs → save; a single orchestration file (`flow.R`) runs the stages.
- **Defensive validation as you go** [transparent, reproducible] — assertions on types, ranges and keys (for example `checkmate`); document constraints for future readers; error and warning thresholds prevent silent failures.
- **Data dictionaries with grain, sources and constraints** [documented] — per table: grain and provenance; per variable: type, description, constraints, units.
- **Collaboration norms** [collaborative, inclusive] — daily PR review; read the diff before committing; announce breaking changes in issues; run downstream dependencies before committing shared files; document workstation setup for fast onboarding.

**Artifacts it implies.** The data dictionary's grain, provenance and units fields; the sensitive-data split in the `.gitignore` and project tree; the single orchestration entry point (`scripts/pipeline.py` in Python, `_targets.R` in the R variant); review and onboarding norms in `CONTRIBUTING.md`.

**When most relevant.** Sensitive or human-subjects data; R-leaning teams; any project that needs concrete naming and coding conventions. Strong signal on "sensitive," "PII," "naming," "data dictionary" or "team norms."

**Caveats.** R and SQL idioms need translation for Python projects (the principles transfer; the syntax does not). The full convention set is heavy for a one-off extraction; pull only what the project needs. "Daily PR review" assumes a second reviewer; for a solo project, see the honest-governance rules in `governance.md`.

## The Turing Way

Source: <https://book.the-turing-way.org/>. Informs sections 6 and 7, and section 1 for project design and ethics.

**In one paragraph.** The Turing Way is a broad, community-built handbook whose five guides (reproducible research, project design, communication, collaboration, ethical research) map almost one-to-one onto the skills' goals. It supplies the definitions and checklists behind reproducibility (version control, environments, testing, FAIR data, licensing, data-management plans), inclusive and open collaboration (codes of conduct, contributor recognition, distributed leadership), accessible communication (plain language, multiple formats) and research ethics. Where other sources give concrete recipes, The Turing Way gives the principled frame.

**Key practices**

- **Reproducibility stack** [reproducible] — version control with reviewable history; captured environments (lockfiles, containers); automated testing; "don't touch raw data, back up read-only."
- **FAIR data and research data management** [accessible, documented, transparent] — Findable, Accessible, Interoperable, Reusable; maintain a data-management plan; persistent identifiers and metadata; standardized file naming and folder structure.
- **Licensing** [transparent, accessible] — always include a LICENSE; use SPDX names; license code, data and documentation appropriately.
- **Project design** [documented] — scope → strategic planning → operational planning; identify stakeholders, risks and biases, and minimum viable products; consider preregistration.
- **Open and inclusive collaboration** [inclusive, collaborative] — a code of conduct; explicit contribution pathways and recognition; distributed, transparent, accountable decision-making; design around contributors' needs.
- **Accessible communication** [accessible] — tailor to diverse audiences; plain-language summaries; multiple formats; don't assume technical expertise.
- **Research ethics** [transparent, inclusive] — consent, privacy, institutional review, governance and oversight.

**Artifacts it implies.** The data-management plan and code of conduct (section 7, with collaborators); the accessibility checklist (section 8); `LICENSE` and the README License section and `CITATION.cff` (section 6); the FAIR checklist and the OKF bundle (sections 8 and 9; see `standards-and-fair.md`).

**When most relevant.** Almost always, as the principled frame; especially when the user names reproducibility, FAIR, openness, ethics, inclusion or accessibility.

**Caveats.** Broad and principle-level; pair it with the concrete sources (Cookiecutter, OUHSC, ProPublica, Quartz) for recipes. It favors flexibility over fixed structure; reconcile with CCDS by treating structure as an adaptable default. "Open" practices apply as far as the project's visibility decision allows.

## USDS Digital Services Playbook

Source: <https://playbook.usds.gov/> (formerly `playbook.cio.gov`, which now redirects there). Informs section 1, and section 8 for accessibility and openness.

**In one paragraph.** The U.S. Digital Service's thirteen "plays" are a short, opinionated set of practices for public-interest delivery: start from real user needs, design the whole experience simply and accessibly, build iteratively with small teams shipping a minimum viable product fast, decide with data, and default to open. For a data project it mainly shapes the scoping frame, the accessibility bar and the openness defaults.

**Key practices**

- **Understand what people need** [accessible, inclusive] — research real users early and throughout; write prioritized user stories; test with real people.
- **Address the whole experience** [accessible] — map the online and offline touchpoints, not just the screen.
- **Make it simple and intuitive** [accessible] — plain language, consistent design and accessibility best practices (the root of the accessibility checklist).
- **Build with agile, iterative practices** [reproducible, collaborative] — ship a minimum viable product quickly, release often, keep a backlog, use source control and code review.
- **Use data to drive decisions** [transparent] — monitor the service, track metrics, and publish them internally and externally.
- **Default to open** [transparent, accessible] — publish source code and data, offer bulk downloads and versioned APIs, use the public domain or open licenses, and give users a way to report problems.

**Artifacts it implies.** The user-centered questions in the Scope canvas (section 1); the accessibility checklist (section 8); the openness defaults behind the README License section and, for public projects, the OKF bundle (section 9); the error-reporting path (section 7).

**When most relevant.** User-facing or civic-facing work, iterative delivery and openness goals. Strong signal on "users," "service," "iterate," "MVP," "default to open" or "publish."

**Caveats.** Written for government service delivery; adapt the cadence to research timelines (the principles transfer, "multiple releases per month" may not). "Default to open" is a government obligation; for a research or civic project it applies only where the section 1 visibility decision is public, and never overrides privacy law, CARE or the sensitivity tier. It complements rather than replaces the reproducibility and data-handling sources.

## Data Collaboratives Canvas

Source: <https://datacollaboratives.org/canvas.html>. Informs section 1, and section 7 for governance terms.

**In one paragraph.** A structured canvas for designing multi-partner, cross-sector data collaborations deliberately rather than discovering the hard parts painfully. It walks a collaboration through phases: demand (problem, value), supply (capacity, data inventory and gaps), collaboration (partner selection and incentives), design (collaborative type, risks, mitigation, terms, governance), implementation (roles, resources), communication, and learning (baseline, metrics, impact). It is the strategic complement to the operational collaboration practices.

**Key practices**

- **Define the problem and value first** [collaborative, transparent] — a one-page problem statement (who benefits, why now) and a concrete value proposition before any data moves.
- **Inventory data supply and gaps** [documented] — what data exists internally and externally, and what is missing.
- **Match partners to incentives** [collaborative, inclusive] — map partners and their motivations; keep a level playing field for smaller partners.
- **Assess risks across the lifecycle** [transparent, inclusive] — collection, analysis, sharing and use risks; prioritize by likelihood × severity; plan mitigation and monitoring.
- **Establish governance** [collaborative, transparent] — decision-making process, feedback loops, conflict resolution, and clear terms (liability, intellectual property, ownership, public-release expectations).
- **Define baseline and impact metrics** [transparent] — measure progress against agreed indicators; iterate.

**Artifacts it implies.** The Scope canvas (section 1, merging the former data-collaborative and project-design canvases); it feeds `GOVERNANCE.md` and `CHARTER.md` (section 7) and the partner-access declarations in section 9.

**When most relevant.** Multi-organization or cross-sector collaborations, data-sharing agreements and partner recruitment. Strong signal on "partners," "data sharing," "collaborative" or "cross-sector."

**Caveats.** Strategic and fairly heavy; for a single-team project most blocks collapse to a few lines. Pair it with ProPublica's collaboration guide for operational partner management. "Public-release expectations" is one of the terms to settle, not an assumption: many collaborations stay private or embargoed.

## Data Cards Playbook

Source: <https://sites.research.google/datacardsplaybook/> (code and templates: <https://github.com/pair-code/datacardsplaybook>, archived 2025). Informs section 6, and section 1 for sensitive attributes.

**In one paragraph.** A Data Card is a "structured summary of essential facts about various aspects of [a] dataset needed by stakeholders across a project's lifecycle for responsible AI development": where the data came from, what is in it, how it was collected and transformed, what is sensitive about it, what it should and shouldn't be used for, and who maintains it. Google PAIR's Playbook adds a participatory *process* for deciding, with stakeholders, what to document and how deeply, and for auditing whether the result is actually transparent. It is the dataset-level transparency artifact that complements the field-level data dictionary, and it pairs naturally with an OKF knowledge bundle.

**Key practices**

- **People-centered transparency** [transparent, documented, accessible] — document for the stakeholders who need the facts (publishers, dataset owners, funders, card authors, annotators, validators) and the decisions each must make, not for a generic audience.
- **Four-stage participatory process** [inclusive, collaborative, transparent] — **Ask** (co-create the card's template with stakeholders, capturing the human decisions and invisible explanations that shape the data), **Inspect** (test the schema on real datasets, find gaps, decide what can be automated), **Answer** (fill it in for diverse audiences), **Audit** (assess completeness and transparency impact through structured review).
- **Fifteen documentation dimensions** [documented, transparent] — Summary; Authorship; Dataset Overview; Example of Data Points; Motivations & Intentions; Access, Retention & Wipeout; Provenance; Human & Other Sensitive Attributes; Extended Use; Transformations; Annotations & Labeling; Validation Types; Sampling Methods; Known Applications & Benchmarks; Terms of Art. Each carries fields with guidance; right-size which a dataset needs.
- **Document intended and out-of-scope uses** [transparent, inclusive] — naming foreseeable misuse is part of responsible release.
- **Surface sensitive attributes and fairness** [inclusive, transparent] — the "Human & Other Sensitive Attributes" and "Access, Retention & Wipeout" dimensions force PII, protected attributes, representation gaps and disposal to the surface.
- **Answer for diverse audiences** [accessible] — make each fact legible to non-experts as well as experts.
- **Share openly** [transparent] — the Playbook is licensed CC BY-SA 4.0; release completed cards under an open license too, where visibility allows.

**Artifacts it implies.** `docs/data-card.md` (section 6, generated when publishing or depositing). It complements, and does not replace, the data dictionary. The Playbook's related artifacts, Healthsheets (health datasets) and Model Cards (models), can be adapted when relevant.

**When most relevant.** Sharing, publishing or depositing a dataset; significant or sensitive datasets; ML training or evaluation data. Strong signal on "data card," "dataset documentation," "transparency," "sensitive attributes," "intended use" or "model card."

**Caveats.** The fifteen dimensions are comprehensive and ML-oriented; a small public teaching dataset may need only Summary, Provenance and a limitations note. Treat the dimensions as a menu. It complements the data dictionary (field-level schema) and the responsible-data checklist (process and ethics). The repository is archived, so the site and templates are a stable reference rather than an evolving one.

## Quartz Bad Data Guide

Source: <https://github.com/Quartz/bad-data-guide>. Informs section 5, and sections 2 and 3 when a new source arrives.

**In one paragraph.** A field guide to the ways data goes wrong, organized by who is best placed to fix each problem. Most data problems are recognizable and many are fixable, but some mean you should not use the data at all, and others mean you can proceed only with stated caveats. It sorts roughly four dozen failure modes into four responsibility tiers (your source, you, an expert, a programmer) so you know whom to ask and what to do. It is the checklist behind the known issues recorded in the data dictionary and the scan run before trusting a dataset.

**Key practices**

- **Issues your source should fix** [transparent, documented] — missing values; zeros or sentinels (65535, -1, 1970-01-01) standing in for missing; expected records absent; inconsistent spelling, name order or date formats; unspecified units; ambiguous field names; undocumented provenance; truncation at 65,536 rows or 255 columns; numbers stored as text (lost leading zeros); totals that don't match published figures.
- **Issues you should fix** [reproducible, documented] — garbled text, encoding and line endings; data trapped in PDFs or scans; wrong aggregation level or geography; human-entry inconsistency; inflation or seasonality skew; a manipulated timeframe or frame of reference; non-random or biased samples; margins of error too large or unknown.
- **Issues an expert should weigh in on** [transparent] — an untrustworthy author; an opaque collection process; implausible precision; inexplicable outliers; p-hacking; an index masking underlying variation; "too good to be true" figures.
- **Issues a programmer should help with** [reproducible] — re-aggregating to different categories or geographies (quantifying the error introduced); tuning OCR for specific documents.

**Artifacts it implies.** The data-quality half of the pre-release checklist (section 5) and the known-issues section of the data dictionary (section 4). `quality-and-bulletproofing.md` carries the full taxonomy.

**When most relevant.** Whenever a messy dataset arrives, and before releasing anything. Strong signal on "messy data," "clean this," "is this data any good," "missing values" or "outliers."

**Caveats.** A menu of failure modes, not a process: pair it with ProPublica bulletproofing (the verification process) and record what you found and how you handled it. Some problems are unfixable; the honest move is to stop using the data.

## ProPublica field guides

Sources: the [Collaborative Journalism Playbook](https://propublica.gitbook.io/collaborative), the [Collaborate user manual](https://propublica.gitbook.io/collaborate-user-manual), and [Bulletproofing Your Data Analysis](https://github.com/propublica/guides/blob/master/data-bulletproofing.md). Informs section 7 (collaboration), sections 2 and 7 (contributed data) and section 5 (bulletproofing).

**In one paragraph.** Three operational guides from investigative journalism, each transferable to public-interest data collaborations. **Collaboration** succeeds on trust, clear communication and a coordinator whose job is to hold it together, not on heavy contracts. **Contributed data** (tips, survey responses, crowdsourced records) inherits duties to the people who supplied it: defined intake, PII redaction, role-based access and verify-before-cite. **Bulletproofing** is the discipline of checking a dataset and analysis hard enough to stake your reputation on the result before releasing it.

**Running a multi-partner collaboration** (section 7)

- **Select partners deliberately** [collaborative] — weigh trust, geography, specialization, reach and scale; start with a small committed core and grow.
- **Keep agreements minimal** [collaborative] — a one-page MOU or even an email suffices; cover embargo, attribution, information sharing and data governance; keep a level playing field so smaller partners feel equally valued.
- **Invest in a coordinator** [collaborative, inclusive] — a dedicated project manager is the most undervalued and most load-bearing role; name it.
- **Over-communicate on a cadence** [collaborative] — regular calls and updates plus one-on-one check-ins, on the channels partners actually use; plan for turnover.
- **Document data caveats for partners** [transparent, documented] — write "reporting recipes" that explain how to use the shared data, what it does and doesn't support, and what is raw versus verified; require verification before anyone publishes.
- **Share credit and celebrate** [inclusive] — attribute fairly and surface partners' wins.

**Handling contributed or crowdsourced data** (sections 2 and 7)

- **Defined intake channels** [collaborative, documented] — bring contributed data in through known methods (uploads, forms, live sheets) so provenance is clear and updates flow.
- **Redact PII at import** [inclusive, transparent] — strip names, contacts and other identifiers on ingestion; redaction downstream does not change the original source.
- **Role-based, project-level access** [inclusive, transparent] — restrict users to the projects and tiers they need; separate standard users from administrators.
- **Log contributor contact** [documented, inclusive] — track outreach for accountability and to honor commitments made to contributors.
- **Deduplicate and triage** [documented] — assign, tag and status-track records; sort, filter and export rather than analyze in place.
- **Verify before you cite** [transparent] — distinguish collected from verified; a contributed record requires verification before it informs a published claim.

**Bulletproofing a data analysis before release** (section 5)

- **Integrity checks** [transparent, reproducible] — verify record counts against expected totals (watch for software row limits); `GROUP BY` key fields to surface spelling variants and duplicates; validate value ranges and dates; decide whether blanks are real or import artifacts, and whether zeros are real or stand in for missing.
- **Recompute independently** [reproducible] — write a different query that should give the same answer and compare; pull a random sample of results and check them against the raw data.
- **Cross-reference** [transparent] — identify and verify the original source; reconcile totals with any published reports.
- **Gut check and outliers** [transparent] — if a result seems off it probably is; double-check surprising findings and treat outliers as leads, not noise; consult a subject-matter expert when the method exceeds your expertise.
- **Independent review** [collaborative, transparent] — have a knowledgeable colleague review findings before release.
- **Keep a data notebook** [documented] — document every procedure, decision and filter so the analysis is reproducible and auditable.

**Artifacts it implies.** Collaboration: the collaboration-protocol section of `CHARTER.md`, alongside `GOVERNANCE.md` and the Scope canvas. Contributed data: the contributed-data-intake section of the data-management plan, the responsible-data checklist and the governance access tiers (see `governance.md`). Bulletproofing: the bulletproofing half of the pre-release checklist and the data dictionary's known issues (see `quality-and-bulletproofing.md`).

**When most relevant.** Multi-organization collaborations and onboarding partners ("partners," "collaboration," "consortium," "shared data"); any project accepting contributed data ("tips," "submissions," "crowdsource," "survey responses"), which also raises its sensitivity; and before releasing or communicating any finding ("publish," "verify," "fact-check," "is this right").

**Caveats.** Journalism-born: read "newsroom" as "collaborating organization" and "publish" as "release, share or deposit." The collaboration playbook is operational where the Data Collaboratives Canvas is strategic; use them together. Contributor protection is a floor, not a ceiling: privacy law and CARE still govern. Bulletproofing complements automated tests rather than replacing them; it is the human, against-the-source layer on top of unit tests, schema validation and reconciliation. "Independent review" assumes a colleague; a solo project states honestly what stood in for one.

## Snakemake

Source: <https://snakemake.readthedocs.io/>. Informs section 5.

**In one paragraph.** Snakemake defines a pipeline as rules, each declaring inputs, outputs and a shell or script step; it infers the dependency DAG from filenames and runs only what is needed, scaling from a laptop to HPC or cloud unchanged. Config files parameterize runs and per-rule environments make steps reproducible. In the skills it is an **optional wrapper** over the canonical pipeline command, `python -m scripts.pipeline run` (or its per-stage subcommands), never required and never what CI discovers.

**Key practices**

- **Rules and wildcards** [reproducible] — each rule maps `input` → `output` with a command; wildcards generalize a rule across many sources or vintages; a `rule all` declares final targets.
- **DAG and dry run** [reproducible, transparent] — `snakemake -n` previews what would run without executing, a cheap correctness check.
- **Config-driven** [reproducible, documented] — parameters and paths live in `config.yaml`, overridable on the command line; no hard-coded constants.
- **Per-rule environments** [reproducible] — `conda:` directives pin a step's dependencies so runs are isolated and recreatable.
- **Pipeline-as-code is the shared artifact** [collaborative, reproducible] — share the re-runnable workflow, not just the cleaned output, so new vintages re-process automatically.

**Artifacts it implies.** An optional `Snakefile` and `config.yaml` whose rules call the pipeline's stages. The R variant uses `targets` (`_targets.R`) instead.

**When most relevant.** When a project already uses Snakemake, needs HPC or cluster execution, or has many independent per-source jobs that benefit from the DAG's incremental reruns.

**Caveats.** Overkill for a one-shot extraction, and unnecessary for most single-dataset pipelines, where `python -m scripts.pipeline run` already is the pipeline-as-code artifact. Multi-pipeline CI discovers `pipelines/*/pyproject.toml`, not a `Snakefile`, so a pipeline must run without Snakemake. Use `snakemake-minimal` for a light install, and note that executors became plugins in Snakemake 8, so cluster profiles written for 7.x need updating.

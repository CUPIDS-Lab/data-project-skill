# The Outline: from a source to a maintained dataset

This is the one map both skills, every project they scaffold, and the sprint-feedback form share. It has ten sections. Each states an **outcome**, a **done when** test anyone can check, which skill **leads**, what to **read**, and what gets **generated only if** that section is in scope. Work on a request by finding the sections it touches, doing only those, and checking their "done when" test before saying the work is finished.

Nothing here is a level to climb. A one-off CSV touches sections 3 and 4 and generates nothing else. A team collaboration starts at section 1 and decides, for every other section, whether it is **now**, **later** or **skip**. That decision is recorded in the project's `ROADMAP.md`, one row per section.

## Common routes

| Request | Sections | Leads | Generated |
| --- | --- | --- | --- |
| "Get the table out of this PDF" | 3 → 4 | data-liberation | the CSV, plus a dictionary and provenance row if asked to make it citable |
| "Make this re-runnable" / "add a source or vintage" | 2 → 3 → 4 → 5 | data-liberation | the project scaffold, then one parser per source |
| "Start a data collaboration" / "set up a repo for our team" | 1, then each section marked *now* | data-project | the five working files, then each section's artifacts when work reaches it |
| "Deposit this" / "get a DOI" / "share it with a partner" | 1 (gate check) → 9 | data-project | the deposit or share kit |
| "We finished a sprint" / "here's what went wrong" | 10 | data-project | a filled sprint-feedback issue on `CUPIDS-Lab/data-skills` |

## The five working files

Every scaffolded project starts with these and nothing else, because they are the files people keep current: `README.md` (what and why, how to use it), `AGENTS.md` (how to work here; `CLAUDE.md` is one line, `@AGENTS.md`), `ROADMAP.md` (the ten sections as now/later/skip, each with its "done when" test), `decision-log.md` (dated decisions, tagged *Assumed* or *Private* where they apply, linking the issue or PR where the decision happened), and `CHANGELOG.md`. When more than one person works on the project, also open one issue per *now* section with that section's test as a task list. Solo projects keep the record in PR bodies (*What changed / Why / What I checked / Left alone on purpose*) and the decision-log.

## Two gates that override leanness

- **Sensitivity.** If section 1 classifies the data as sensitive-human, regulated, or implicating Indigenous data (CARE), section 7's minimum safeguards are *now*, whatever else is deferred: every identifier, retention or audit affordance ships with access tiers and a contestable remedy. Affordances without duties are theater. See `values-and-gates.md`.
- **Visibility.** Section 1 chooses *private*, *embargoed* or *public*. Section 8 applies only to public or embargoed outputs, and no hosted service (OCR, LLM, publishing) receives documents the visibility or sensitivity decision forbids.

---

## 1. Scope & gate

- **Outcome:** everyone knows what question the data answers, what one row means, and what the project will not do.
- **Done when:**
  - the question, the unit of observation, the sources, and the partners versus beneficiaries are written in the README's "What & why";
  - the sensitivity tier, privacy-law screen and CARE check are decided and recorded in the decision-log;
  - visibility (private, embargoed, public) is chosen;
  - "what we won't liberate or publish" is stated;
  - every other section is marked now, later or skip in `ROADMAP.md`.
- **Leads:** data-project (data-liberation does a one-paragraph version for one-off extractions).
- **Read:** `values-and-gates.md`, `responsible-data.md`; data-project's `procedures/scope.md`.
- **Generate only if:** sensitive → the responsible-data checklist (filled now, from the scoping conversation, before sensitive features exist) and a GOVERNANCE stub.

## 2. Acquire

- **Outcome:** every original is in hand, reproducibly, and its origin is on record.
- **Done when:**
  - the live source was probed (real files opened, not just the landing page) before any parser was written;
  - every original is fetched by code, hashed, licensed, and has a provenance row;
  - the access path is recorded (download, API, dashboard, FOIA request, archive), and ephemeral sources have a snapshot cadence and a gap check;
  - a storage budget says which originals are committed, which live in Git LFS or external storage (with hash and URL in provenance), and CI fails on files near GitHub's 100 MB limit;
  - a forced refetch (`--fresh`) exists for when a cached original is stale.
- **Leads:** data-liberation.
- **Read:** `extract-web.md`, `extract-api.md`; `pipeline.md` (discovery, FOIA).
- **Generate only if:** a project exists → `scripts/{sources,config,fetch,discover}.py` and `data/original/`.

## 3. Extract

- **Outcome:** rows come out of the source faithfully, and every value can be traced back to where it was read.
- **Done when:**
  - every page or file was triaged (born-digital text, scanned, mixed; tables, forms, multi-page tables);
  - extracted rows reconcile with the source on a spot-check and against its own printed totals;
  - every value traces to source hash + page + region (or URL + selector);
  - model-based extraction (OCR, layout or vision models, hosted APIs) has a parser manifest, a cost cap, and an audit sample;
  - failures land in a fresh per-run error log, never in silence.
- **Leads:** data-liberation.
- **Read:** only the `extract-*.md` file for the input in hand.
- **Generate only if:** one-off → the CSV; project → one parser module per source.

## 4. Model & tidy

- **Outcome:** the data has one documented, validated shape that someone else can use correctly.
- **Done when:**
  - the table is tidy long (one row per observation) and validates against the schema contract;
  - duplicates are removed before validation, not reported by it;
  - the data dictionary covers every column (type, units, missingness, caveats), and controlled vocabularies in lookup files are enforced by a test;
  - cross-source concepts carry caveats saying what is and is not comparable (only when there is more than one source).
- **Leads:** data-liberation.
- **Read:** `data-modeling.md`.
- **Generate only if:** project → `scripts/schema.py`, `docs/data-dictionary.md`, filter-pivot recipes; a second source arrives → the source registry and `concepts.yaml`.

## 5. Pipeline & audit

- **Outcome:** anyone can regenerate the data from the originals with one command, and the build refuses to produce wrong data quietly.
- **Done when:**
  - a clean clone regenerates `data/processed/` with one command;
  - CI runs the tests, the audit, and a conservation check (no rows lost between stages);
  - empty or degenerate output fails loudly, and nothing substitutes synthetic or cached data for a failed download;
  - reconciliation against the source's totals passes, or each mismatch is documented;
  - audit samples are drawn on a stable key, so they survive renumbering;
  - the pre-release bulletproofing pass is done.
- **Leads:** data-liberation (data-project for multi-pipeline repos).
- **Read:** `pipeline.md`, `project-template.md`, `quality-and-bulletproofing.md`; data-project's `multi-pipeline.md`.
- **Generate only if:** project → the pipeline, tests, CI, `reconcile.py`; release planned → the pre-release checklist.

## 6. Document & cite

- **Outcome:** a newcomer can load the data and interpret it correctly without asking anyone.
- **Done when:**
  - the README alone is enough to load and correctly interpret the data;
  - every number quoted in prose (row counts, totals, match rates) is generated from the pipeline, and CI fails when a copy goes stale;
  - how to cite it and under what license are clear (`CITATION.cff`, `LICENSE`);
  - decisions are in the decision-log.
- **Leads:** both.
- **Read:** `practice-sources.md` (Data Cards, Turing Way); `standards-and-fair.md`.
- **Generate only if:** publishing or depositing → methodology page and data card; releasing a package → `codemeta.json`.

## 7. Govern & collaborate

- **Outcome:** who may touch what is decided, written down honestly, and enforced where it is claimed.
- **Done when:**
  - roles and the gap check are named, and a solo project says so plainly (a single steward, no pretend review gates);
  - any review gate the docs claim (for example "owners approve by PR") is enforced by branch protection;
  - a correction and remedy path exists for people represented in the data;
  - the sensitivity coupling from section 1 is satisfied.
- **Leads:** data-project.
- **Read:** `governance.md`, `values-and-gates.md`; data-project's `collaboration-architecture.md`.
- **Generate only if:** collaborators or sensitive data → GOVERNANCE, CHARTER, CODEOWNERS, CONTRIBUTING, CODE_OF_CONDUCT, data-management plan; onboarding several people → a short tested tutorial series, not more governance docs.

## 8. Publish (only if visibility is public or embargoed)

- **Outcome:** a stranger can find, query or read the data on the surface the project chose, or an embargoed release is staged.
- **Done when:**
  - the chosen surface works (Datasette, Quarto site, Git LFS release, DocumentCloud), or the embargo is staged with its release date and conditions;
  - the FAIR self-check and the accessibility check are done for public outputs.
- **Leads:** data-liberation.
- **Read:** `publishing.md`, `standards-and-fair.md`.
- **Generate only if:** in scope → that surface's files and workflows only, plus the FAIR and accessibility checklists.

## 9. Deposit, share & discover

- **Outcome:** the data has a citable, durable home, partners get the access they are entitled to, and agents can find it if that is intended.
- **Done when:**
  - a DOI is minted, or a reviewed draft deposit exists, with refreshes versioned (first refresh major, later refreshes minor);
  - partner access is declared under the governance access tiers;
  - agent discovery (ARD) and the OKF catalog are published if intended.
- **Leads:** data-project.
- **Read:** `procedures/deposit.md`, `dataverse-deposit.md`, `open-sharing-protocol.md`, `agentic-resource-discovery.md`, `okf-open-knowledge-format.md`.
- **Generate only if:** in scope → the Dataverse kit, OpenSharing kit, ARD catalog or OKF bundle.

## 10. Maintain & feedback

- **Outcome:** the data stays current, the work stays visible, and what each sprint learned improves these skills.
- **Done when:**
  - refreshes run on their cadence and arrive as reviewable PRs carrying the audit diff;
  - open work is tracked (ROADMAP rows, and issues when there is a team);
  - each sprint ends with an after-action review filed through the sprint-feedback form on `CUPIDS-Lab/data-skills`, against these section numbers.
- **Leads:** both.
- **Read:** `feedback.md`; data-project's `procedures/tracking.md` and `github.md`; `pipeline.md` (recurring refresh).
- **Generate only if:** recurring source → the refresh workflow; team → issue forms, labels, and the seed script.

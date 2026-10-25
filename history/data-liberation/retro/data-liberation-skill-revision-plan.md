# Claude Code revision plan — `data-liberation` skill

**Responds to:** the after-action report from the first real deployment of `data-liberation`
(Colorado Environmental Data Hub → `pipelines/reservoir-storage/`, 2026-06-19).
**Skill baseline:** `v0.4.0` (six-level restructure; template pin
`72b202020c12056f19c828bff0b619cda5aadf64`).
**Parallel to:** `retro/data-project-skill-revision-plan.md` in the sibling `data-project` skill.
**Status:** proposed; not yet executed. Each workstream below is sized to one PR.

This plan turns the AAR's eleven findings and six recommendations into phased, file-level edits
with acceptance criteria. It is deliberately a *plan*, not the edits themselves — execute it
phase by phase, shipping each phase as its own release.

---

## 0. Orienting notes (read first)

### 0.1 The AAR's file names are aspirational — here's the mapping to the real repo

The AAR was written from the *mental model* of the skill, so it names files that don't exist
under those names. Translate before acting:

| AAR says | Actually lives in | Notes |
|---|---|---|
| `references/toolchain-apis.md` (to add) | **new** `references/extract-api.md` | Name it for the `extract-*` family, not `toolchain-*` — that's the established convention (`extract-pdf`, `extract-tabular`, `extract-documents`, `extract-web`, `extract-images`). |
| `toolchain-scraping.md` | `references/extract-web.md` | Already exists; already has an *API discovery* subsection (CKAN / Socrata / `data.json` / `/api/v1`). |
| `discovery-and-audit.md` | `references/pipeline.md` (Part 2) | Discovery / audit / reconcile / bulletproofing all live here. |
| `data-modeling.md` | `references/data-modeling.md` | Correct as-is. |
| `discover.py`, `fetch.py`, `clean.py`, `reconcile.py`, `pipeline.py`, `stations.py` | the **template repo** (`brianckeegan/data-liberation-template`), described by `references/project-template.md` | These are *generated scaffold* files, not skill files. Editing them is template-repo work. |
| `retro/data-project-skill-revision-plan.md` | sibling `data-project` skill repo | This document is its `data-liberation` counterpart. |

### 0.2 Two repos, locked in step — the single most important execution constraint

The skill ships as **two repos that version together** (see `RELEASING.md`):

- **`data-liberation-skill`** (this repo) — `SKILL.md`, `references/*.md`, `scripts/scaffold.py`.
- **`data-liberation-template`** — the Python project skeleton `scaffold.py` renders, pinned by
  **commit SHA** in `scaffold.py`.

Consequences that shape the phasing:

1. **Skill-only changes** (new/edited `references/*.md`, `SKILL.md` prose) ship as a skill release
   that *re-pins the same template SHA*. No template bytes change. → **Phases 1 and 2.**
2. **Any change to the generated scaffold** (progress bars in `fetch.py`, run-scoped error log in
   `audit.py`, reject-port granularity in `clean.py`, a notebook variant, `nbstripout`) is a
   **template-repo change** and therefore a **joint skill+template version bump**: tag the template,
   capture its SHA, update both `DEFAULT_TEMPLATE_VERSION` and `DEFAULT_TEMPLATE_TAG` in
   `scaffold.py`, and confirm green `scaffold-e2e.yml` on **both** repos. → **Phases 3 and 4.**
3. **Editing `references/project-template.md` or `references/data-modeling.md` fires
   `dispatch-to-template.yml`**, which triggers the template repo's `scaffold-e2e.yml`. Expect (and
   want) that re-validation even for "skill-only" doc edits to those two files.
4. `RELEASING.md` already has a **"Planned follow-ups (template repo)"** section proposing
   `scaffold.py --level <0-5>`. The notebook variant in Phase 4 should be designed *with* that
   work, not against it (one render-walk subsetting mechanism, two axes: level and variant).

### 0.3 What already exists (so we extend, not re-invent)

The AAR's gaps are real, but several are *"present but scattered / unframed / not enforced,"* not
*"absent."* Calling this out keeps the edits surgical:

- **Pagination** — offset + cursor patterns already in `extract-documents.md#pagination-from-apis`.
  Work is to *centralize and extend* (link-header / `links.next`, row-cap guards), not author from zero.
- **API discovery** — CKAN / Socrata / `data.json` / `/api/v1` already in `extract-web.md#api-discovery`.
- **`fetch --force`** — already documented in `project-template.md` (`fetch.py` "exposes `--force`
  to redownload … where the upstream URL is stable but the content changed"). The gap is *framing*
  + *contract-change trigger* + a driver-level `FRESH` option, not the flag itself.
- **Dedup before validate** — deduplication is already cleaning-pipeline **step 3**, validation is
  **step 7**. The gap is a *failure-mode warning* (whole-frame uniqueness validation dropping a
  whole entity) and *reject granularity*, not the ordering.
- **Loud error surfacing** — already named as a fix in `pipeline.md`'s failure-modes table
  ("Add an early-section '⚠️ N extraction errors' line"). The gap is *implementing* it in the audit
  skeleton and making the log *run-scoped*.
- **`structlog`** — already a core dependency, so progress reporting needs no new dep.

---

## 1. Traceability matrix — every AAR finding maps to a workstream

| # | AAR finding (short) | Workstream | Primary files | Repo | Release |
|---|---|---|---|---|---|
| 3 | APIs badly under-served (REST/JSON:API/ArcGIS; probe-then-extract) | **WS-A** API toolchain + probe discipline | `references/extract-api.md` (new), `SKILL.md`, `README.md`, `extract-documents.md`, `extract-web.md` | skill | Ph 1 |
| 8 | Entity-universe enumeration not modeled | **WS-B** entity enumeration | `extract-api.md`, `pipeline.md`, `project-template.md` | skill (+template stub in Ph 3) | Ph 1/3 |
| 7 | Temporal grain (sub-daily, revisions, flooring) not modeled | **WS-C** temporal grain | `data-modeling.md` | skill | Ph 2 |
| 5 | Reject port silently dropped whole entities | **WS-D** validation granularity + dedup-before-validate | `pipeline.md`, `data-modeling.md` (prose); template `clean.py`/`schema.py` (behavior) | skill + template | Ph 2 (doc) → Ph 3 (code) |
| 4 | Immutable-originals has no cache-invalidation story | **WS-E** cache invalidation | `SKILL.md`, `pipeline.md` (prose); template `fetch.py`/`pipeline.py` (`FRESH`) | skill + template | Ph 2 (doc) → Ph 3 (code) |
| 6 | Error log accumulated stale failures | **WS-F** run-scoped, loud error log | `pipeline.md`, `project-template.md` (prose); template `audit.py` (behavior) | skill + template | Ph 3 |
| 9 | No progress/liveness for large fetches | **WS-G** fetch progress | `extract-web.md`, `extract-api.md`, `project-template.md` (prose); template `fetch.py` | skill + template | Ph 3 |
| 10 | Scaffolded operator copy assumes expertise | **WS-H** novice-legibility pass | `pipeline.md` (prose); template `reconcile.py` + stubs | skill + template | Ph 3 |
| 1 | Template is script-CLI; ask was notebooks | **WS-I** notebook-first variant | `scaffold.py`, `SKILL.md`, `project-template.md`; template (notebooks + package) | skill + template | Ph 4 |
| 2 | `scripts/` vs `src/` rigidity | **WS-J** layout reconciliation | `project-template.md`, `SKILL.md`, `scaffold.py` | skill + template | Ph 4 |
| 11 | Notebook output hygiene (`nbstripout`) | **WS-K** `nbstripout` scaffold | template (`.pre-commit-config`, `.gitattributes`); `project-template.md` | template | Ph 4 |

Findings the AAR marks as **working well** (immutable originals, tidy-long, concepts-carry-caveats,
pandera-as-boundary, durable-errors, AGENTS.md-first, reconcile-against-published-total) are
**load-bearing — do not regress them.** Each workstream below names what it must preserve.

---

## 2. Phase 1 — API toolchain + the "probe-then-extract" discipline *(skill-only)*

**Why first:** the AAR calls APIs "the single biggest gap" and the probe-then-extract loop "the
thing that actually worked every time." It is almost entirely prose in *this* repo, ships without a
template bump, and unblocks nothing downstream — highest impact, lowest coordination cost.

### WS-A — `references/extract-api.md` (new) + wiring

**Create `references/extract-api.md`** in the house style of the other `extract-*` files (intro →
decision tree → per-tool sections → "Common failure modes" table → "What to write in the AGENTS.md").
It must cover the exact traps the deployment hit:

- **The probe-then-extract loop** (the headline discipline): pull a handful of records, decode the
  contract (field names, envelope shape, null/empty conventions, required params), *then* write the
  parser. Frame it as the API analog of "profile before you parse."
- **Empty-vs-error conventions** — `404 = zero records` (CDSS), `200` with an empty body, `200` with
  an unrelated default page. How to tell "no data" from "you asked wrong."
- **Required-parameter quirks** — endpoints that need *both* `startDate` **and** `endDate` for full
  history (neither alone works); silently-defaulted filters (`locationId[]` / `search` returning an
  unrelated page).
- **Field-name surprises** — the value field is `measValue`, not `value`; decode by probing, don't
  assume.
- **Pagination, centralized** — `links.next` / RFC 5988 `Link` headers, cursor, offset; **document
  hard caps** (e.g. a 10k-row ceiling) and the guard pattern; the "cached session returns empty body
  for big pages" interaction. Make this the *canonical* pagination home; have
  `extract-documents.md#pagination-from-apis` cross-link here instead of duplicating.
- **API families** — REST/JSON, **JSON:API** (relationship traversal:
  `location → catalogRecords → catalogItems` is the reliable discovery path when filters lie),
  **GraphQL**, **ArcGIS FeatureServer** (the `query` endpoint; `where=1=1`, `outFields`,
  `resultOffset`/`resultRecordCount`; and the AAR's warning that a FeatureServer may be
  *boundaries-only* — a dead end for tabular data).
- **Rate limits + etiquette** — reuse `extract-web.md`'s polite-request budget, `requests-cache`,
  `tenacity`; cross-link rather than restate the ethics.
- **API discovery** — absorb or cross-link `extract-web.md#api-discovery` so "is there an API?" has
  one answer.

**Wire it in (four touch-points):**

1. `SKILL.md` Extract-phase routing table (§3) — add a row:
   `REST / JSON:API / GraphQL / ArcGIS / paginated endpoints → probe-then-extract loop, httpx + cache → extract-api.md`.
2. `SKILL.md` Reference index (§"Reference index") — add `extract-api.md` to the L0 toolchain list;
   update "Ten references" / "five `extract-*` files" counts to **eleven / six**.
3. `README.md` — add `extract-api.md` to the repo-contents tree and the toolchain bullet (the bullet
   currently folds JSON into `extract-documents`; split out API retrieval).
4. `extract-documents.md` and `extract-web.md` — replace their pagination/discovery detail with a
   one-line cross-link to `extract-api.md` (keep a pointer, move the depth).

**Also seed the discipline outside the toolchain file** (it's a *method*, not just a tool):

5. `SKILL.md` §1 Survey "Ask before assuming" — one clause: for API sources, probe a few records to
   decode the contract before writing parser code.
6. `pipeline.md` pre-extraction bulletproofing — add an **API-source row** to the source-level checks
   (probe the contract; confirm empty-vs-404; identify required params; confirm the value field name).

**Preserves:** the per-input split (an agent extracting a PDF never loads API material); the
"profile before you parse" spine (this is its API sibling).

**Acceptance criteria:**
- [ ] `references/extract-api.md` exists and covers, by name: probe-then-extract, empty-vs-404,
      required-param quirks, silent-default filters, `links.next`/cursor/offset **with a row-cap
      guard**, JSON:API relationship traversal, GraphQL, ArcGIS FeatureServer `query`, rate limits,
      entity enumeration (stub → WS-B), and the AGENTS.md checklist.
- [ ] `SKILL.md` routing table has the API row; reference index lists `extract-api.md`; the
      "ten references / five extract files" counts read **eleven / six**.
- [ ] `README.md` tree + toolchain bullet list `extract-api.md`.
- [ ] Pagination depth lives in `extract-api.md`; `extract-documents.md` cross-links, does not
      duplicate (no two copies of the offset/cursor code to drift apart).
- [ ] `SKILL.md` Survey and `pipeline.md` bulletproofing each name the probe-then-extract check.
- [ ] No `scaffold.py` / template change → ships **skill-only** (template SHA re-pinned unchanged).

### WS-B (part 1) — entity-universe enumeration *(pattern, in `extract-api.md`)*

Document **enumerating the entity universe behind an API** as a first-class, *separate* operation
from vintage discovery. Vintage discovery answers "is there a new file?"; entity enumeration answers
"what stations / reservoirs / institutions *exist* behind this endpoint?" (the CDSS station list; the
RISE catalog traversal; the hand-built `stations.py`).

In `extract-api.md`: a short "Enumerate the entity universe" section — the relationship-traversal
pattern, persisting the result to `data/lookups/<source>_entities.csv` as a reviewable artifact, and
treating a change in that set as a refresh signal (a new station = new rows, like a new vintage).
Add a `pipeline.md` Discovery-section note distinguishing the two. (The template-side `entities.py`
stub is Phase 3, WS-B part 2.)

**Acceptance criteria:**
- [ ] `extract-api.md` has an entity-enumeration section with the traversal pattern and the
      `data/lookups/<source>_entities.csv` artifact.
- [ ] `pipeline.md` Discovery explicitly contrasts *vintage discovery* vs *entity enumeration*.

---

## 3. Phase 2 — modeling guidance: temporal grain, validation granularity, cache framing *(skill-only)*

**Why second:** these are doc edits in `data-modeling.md` / `pipeline.md` / `SKILL.md`, but they
*specify the contracts* the template code in Phase 3 must honor. Writing the prose first means
Phase 3 implements an already-agreed spec. (Edits to `data-modeling.md` and `project-template.md`
will fire `dispatch-to-template.yml` — expected.)

### WS-C — temporal grain as a first-class modeling case (`data-modeling.md`)

Add a **"Temporal grain"** section near "When schema decisions are hard to reverse." Cover:

- **One row per period** — declaring the period (day, month, water-year) as part of the unit of
  observation, alongside the existing vintage-convention guidance.
- **Multiple readings per period** — sub-daily readings collapsed by day-flooring: state the policy
  *explicitly* (which timestamp the floor uses, which TZ) because it determines uniqueness.
- **Which observation wins** — same-period revisions: last-write-wins vs. max-quality-flag vs.
  provider-revision-number; tie it to the dedup keep-policy in `pipeline.md` step 3 (`keep='last'`
  for corrected-over-time data).
- **Revisions as data** — when a provider re-issues a value, keep the prior value's trail (provenance
  / a `revision` marker) rather than silently overwriting.

Cross-link from `pipeline.md` step 3 (deduplication) and from the composite-key discussion below.

**Preserves:** tidy-long as the storage shape; the "hard-to-reverse decisions" framing.

**Acceptance criteria:**
- [ ] `data-modeling.md` has a "Temporal grain" section covering period-as-unit, flooring (timestamp
      + TZ stated), which-reading-wins, and revisions.
- [ ] `pipeline.md` step 3 cross-links the temporal-grain section for the keep-policy choice.

### WS-D (part 1) — validation granularity + dedup-before-validate *(prose; `pipeline.md`, `data-modeling.md`)*

The deployment's worst bug: a handful of duplicate-date rows failed a **frame-uniqueness** check
*inside a parser*, the SchemaError was caught at the artifact level, and the **entire reservoir**
(ruedi, turquoise, twin-lakes…) was dropped and logged — a few bad rows became missing sources,
visible only by reading a JSON file.

Add guidance (do **not** weaken durable-errors — sharpen its granularity):

- `pipeline.md` step 7 (validation + reject port) and the reject-port section — a **warning box**:
  *whole-frame `pandera` validation inside `ingest`/a parser turns a few bad rows into a dropped
  source.* Prescribe: **deduplicate on the natural key (step 3) and resolve temporal revisions
  (WS-C) *before* the uniqueness check**; route the *offending rows* to the reject port, don't fail
  the frame.
- `pipeline.md` — name the **artifact-level vs row-level** failure distinction: a parse that can't
  produce a frame is an artifact failure (→ `extraction_errors.json`); a frame with some invalid
  rows is a row-level reject (→ `rejected.csv`). A uniqueness violation is almost always the latter.
- `data-modeling.md#validation` and the composite-key bullet in "When schema decisions are hard to
  reverse" — note that the multi-column uniqueness check belongs at the **clean.py boundary after
  concatenation + dedup**, not inside each parser, so one source's dupes can't drop another.

**Preserves:** pandera-as-boundary-contract; errors-durable-not-fatal; the reject port as a
first-class audit artifact.

**Acceptance criteria:**
- [ ] `pipeline.md` step 7 + reject-port section warn that in-parser frame-uniqueness validation can
      drop a whole entity, and prescribe dedup/revision-resolution before the check + row-level reject.
- [ ] `pipeline.md` names the artifact-level vs row-level failure distinction and which port each uses.
- [ ] `data-modeling.md` places the uniqueness check at the post-concat boundary, not per-parser.

### WS-E (part 1) — cache-invalidation framing *(prose; `SKILL.md`, `pipeline.md`)*

`data/original/` is currently framed as an immutable *archive*; the deployment learned the hard way
it's really a **rebuildable cache** — when the *extraction contract* changed (the full-history fix),
cached files went stale and never refreshed, so the CSV was silently partial.

- `SKILL.md` "Conventions worth defending" → "Immutable originals" — keep immutability, but add the
  nuance: *originals are a rebuildable cache, not a sacred archive; refetch when the extraction
  contract changes (URL stable, request parameters changed).* Point at `fetch --force`.
- `pipeline.md` — a short **"When to invalidate `data/original/`"** note: list the contract-change
  triggers (request params, date-range strategy, pagination params, entity set) and the rule that a
  contract change means refetch, not just re-clean. Suggest recording the *extraction parameters* in
  `provenance.csv` so a contract change is detectable (a provenance diff), not silent.

**Preserves:** immutable-originals + per-extract provenance (the AAR's #1 "worked well").

**Acceptance criteria:**
- [ ] `SKILL.md` "Immutable originals" carries the rebuildable-cache nuance + the refetch-on-
      contract-change rule + a pointer to `fetch --force`.
- [ ] `pipeline.md` has a "When to invalidate `data/original/`" note listing contract-change triggers
      and recommending extraction parameters in provenance.

---

## 4. Phase 3 — harden the generated scaffold *(joint skill + template bump)*

**Why third:** these change template bytes, so they're a coordinated release. They implement the
specs written in Phase 2 plus three self-contained scaffold improvements. Do them together as one
template tag + one skill pin bump to minimize release churn.

> **Release mechanics (per `RELEASING.md`):** tag the template `vX.Y.0`, capture its SHA, set both
> `DEFAULT_TEMPLATE_VERSION` (SHA) and `DEFAULT_TEMPLATE_TAG` (`vX.Y.0`) in `scaffold.py`, run the
> local scaffold rehearsal (render → `grep` for stray `{{ }}` → `uv sync` → `ruff` → `pytest`), and
> confirm green `scaffold-e2e.yml` on **both** repos via the `repository_dispatch` pairing.

### WS-D (part 2) — reject-port granularity in `clean.py` / `schema.py` *(template)*
Implement the WS-D spec: dedup + temporal-revision resolution before the uniqueness check; the
multi-column uniqueness check at the post-concat `clean.py` boundary; row-level rejects to
`rejected.csv` instead of artifact-level drops for uniqueness violations.
- [ ] A fixture with a few duplicate-date rows for one entity yields those rows in `rejected.csv`
      **and the rest of that entity's rows survive** (regression test for the exact AAR bug).
- [ ] `project-template.md`'s `clean.py` / `schema.py` descriptions match the new behavior.

### WS-E (part 2) — `FRESH` / contract-change refetch in the driver *(template)*
Surface cache invalidation operationally: a `FRESH`/`--force`-through path in `pipeline.py` (and the
notebook driver once it exists) that re-fetches when set; record extraction parameters in
`provenance.csv` so a contract change is visible.
- [ ] `uv run python -m scripts.pipeline fetch --force` (and a driver `FRESH` toggle) re-fetches even
      when files exist; `provenance.csv` carries the extraction parameters.

### WS-F — run-scoped, loud extraction-error log in `audit.py` *(template)*
Make `record_extraction_error()` **run-scoped** (truncate at run start, or write
`extraction_errors-<ts>.json` to match `summary-<ts>.md` / `cleaning-log-<ts>.json`, or stamp a
`run_id`) so a prior interrupted run's `JSONDecodeError`s can't mislead the next debug. Implement the
already-promised **loud surfacing**: a top-of-summary `⚠️ N extraction errors` line.
- [ ] An interrupted run's errors do not appear in the next run's report.
- [ ] `data/audit/summary-<ts>.md` shows the `⚠️ N extraction errors` line at the top when N > 0.
- [ ] `pipeline.md` audit section + failure-modes row updated to describe run-scoped + loud behavior.

### WS-G — progress/liveness in `fetch.py` *(template)*
Add `structlog` per-artifact progress (and a counter for paginated fan-out) so a hundreds-of-request
historical pull isn't silent. No new dependency (`structlog` is already core).
- [ ] A multi-artifact / paginated fetch emits per-unit progress; documented in `extract-web.md`
      (idempotent fetch pattern) and `extract-api.md` (pagination fan-out) + `project-template.md`.

### WS-H — novice-legibility pass on scaffolded operator copy *(template)*
Rewrite the `reconcile()` stub copy (and the bulletproofing-checklist operator copy) from
expert-shorthand to **what / where / how / success-vs-failure**. The AAR's example: the shipped
*"fill `expected` with current storage off each agency's page; any mismatch beyond tolerance is a
regression"* is unactionable for a novice.
- [ ] The `reconcile.py` stub docstring/comments tell a novice *what* to fill, *where* to find it,
      *how* to enter it, and *how to read* pass vs fail.
- [ ] `pipeline.md` reconcile section models the novice-legible copy standard (same bar the skill
      sets for data dictionaries).

### WS-B (part 2) — optional `entities.py` / lookups stub *(template)*
Ship an optional, documented entity-enumeration stub (or a `data/lookups/<source>_entities.csv`
convention) implementing the WS-B pattern, off by default (most file-based sources don't need it).
- [ ] Template carries an optional entity-enumeration stub matching the `extract-api.md` pattern;
      `project-template.md` documents it as optional.

---

## 5. Phase 4 — notebook-first variant, layout reconciliation, `nbstripout` *(joint bump; largest)*

**Why last:** biggest lift, depends on the Phase-4 decision points (§6), and is the natural place to
co-design with `RELEASING.md`'s already-planned `scaffold.py --level` work. Treat the render walk as
subsettable along **two axes**: *level* (0–5, already planned) and *variant* (`cli` default vs
`notebook`).

### WS-I — notebook-driven pipeline variant *(skill + template)*
A legitimate, natively-supported deliverable shape: **thin notebooks orchestrating a tested
package**, not logic-in-notebooks. The driver notebook runs the four stages
(retrieve → audit → cleanup → publish); the package stays the unit-tested core.
- `scaffold.py` — a `--variant notebook` flag (composes with `--level`); render-walk subsetting.
- Template — a `*-pipeline.ipynb` thin driver + the package; the notebook calls the same
  `discover/fetch/clean/audit` entry points the CLI does.
- `SKILL.md` Scaffold phase (§2) + `project-template.md` — document the variant; note it's common in
  data journalism and teaching.
- [ ] `scaffold.py --variant notebook` renders a thin-notebook-over-package project; `scaffold-e2e`
      green on both repos; `SKILL.md` + `project-template.md` document when to choose it.

### WS-J — reconcile `scripts/` ↔ `src/` with `data-project` *(skill + template)*
Resolve the rigidity the AAR flagged (skill mandates `scripts/`; the build needed `src/reservoir/`
for testability/importability and parent-repo consistency). **Decision required — see §6.1.** Whatever
is chosen, document the rationale and (if a flag) wire it through `scaffold.py`.
- [ ] `project-template.md` "Conventions worth defending" no longer reads as an absolute bar on
      `src/`; the chosen approach (flag or blessed-exception) is documented and consistent with
      `data-project`.

### WS-K — `nbstripout` scaffold *(template; shared with `data-project`)*
For the notebook variant, scaffold output hygiene: a `.pre-commit-config.yaml` `nbstripout` hook (+
`.gitattributes` filter) so notebooks aren't committed with executed outputs.
- [ ] Notebook-variant scaffold ships `nbstripout` wired via pre-commit; `project-template.md`
      documents it; matches the `data-project` finding's resolution.

---

## 6. Decision points for the maintainer (resolve before Phase 4)

These are genuine judgment calls the plan should not silently pre-empt:

### 6.1 `scripts/` vs `src/`
`project-template.md` defends `scripts/` because *"every mature civic liberation project — PUDL,
BoulderPublicData, IPEDS-pipeline — uses `scripts/`; predictability across projects is the point."*
The AAR wants reconciliation with `data-project`'s `src/`. Three options:
- **(a) Keep `scripts/` default, bless `src/` as a documented exception** for notebook+package and
  parent-repo-consistency cases. *Lowest churn; preserves the convention; mild inconsistency.*
- **(b) `scaffold.py --layout {scripts,src}`**, default `scripts/`. *Most flexible; adds a slot-fill
  + a render axis; both must stay green in `scaffold-e2e`.* **(recommended)**
- **(c) Switch the default to `src/`** to match `data-project`. *Cleanest cross-skill story; breaks
  the stated convention and every "looks like every other civic project" claim — highest blast radius.*

### 6.2 Notebook variant mechanism
Fold the notebook variant into the planned `--level` work as a second axis (`--variant`), or ship it
as a standalone flag first and integrate later? Recommend **co-design with `--level`** (one render-
walk subsetting mechanism) to avoid two overlapping subsetters.

### 6.3 New reference file name
`extract-api.md` (recommended; matches the `extract-*` family) vs the AAR's literal `toolchain-apis.md`.
Recommend `extract-api.md`.

### 6.4 Release grouping
Phases 1 and 2 are both skill-only — ship separately (faster feedback on the API reference) or as one
`v0.5.0`? Phases 3 and 4 are both joint bumps — bundle or split? Recommend: **Ph 1 → `v0.5.0`
(skill-only), Ph 2 → `v0.6.0` (skill-only), Ph 3 → `v0.7.0` (joint), Ph 4 → `v0.8.0` (joint)**, but
the skill-only/joint split matters more than the exact numbers.

---

## 7. Sequencing summary

```
Phase 1  WS-A, WS-B(1)            skill-only   ── ships the biggest gap (APIs) first, no template risk
Phase 2  WS-C, WS-D(1), WS-E(1)   skill-only   ── writes the specs Phase 3 implements
Phase 3  WS-D(2),E(2),F,G,H,B(2)  joint bump   ── hardens the generated scaffold to those specs
Phase 4  WS-I, WS-J, WS-K         joint bump   ── notebook variant + layout + nbstripout (needs §6)
```

Dependency edges: WS-C → WS-D (revision resolution precedes uniqueness); WS-D(1) → WS-D(2),
WS-E(1) → WS-E(2) (doc spec precedes code); WS-B(1) → WS-B(2); §6.1/§6.2 → all of Phase 4.

## 8. Non-goals / guardrails

- **Don't regress the spine.** Immutable originals, per-extract provenance, tidy-long,
  concepts-carry-caveats, pandera-at-the-boundary, durable-errors, AGENTS.md-first,
  reconcile-against-published-total — all rated "worked well." Every edit preserves them.
- **Don't turn durable-errors into silent-success.** WS-D sharpens *granularity* (row vs frame vs
  artifact); it must not let a genuinely empty source pass unflagged. The `--fail-on-empty` guard and
  the "Empty sources" audit flag stay.
- **Don't make the API reference an everything-reference.** Keep the per-input split: an agent
  extracting a PDF must not be made to load API material.
- **Don't break reproducibility.** SHA-pinning stays; every template change is a joint, tagged,
  `scaffold-e2e`-green release — never an unpinned float.
```

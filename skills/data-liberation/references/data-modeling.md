# Data Modeling: Schema, Dictionary, Concepts, Provenance, Validation

This reference covers what happens *after* extraction: how to reshape the rows, how to document them so someone else can use them, how to harmonize across sources, how to validate the result, and how to keep the audit trail intact. The decisions made here are what separate a liberated dataset from a private spreadsheet.

The conventions in this reference are distilled from PUDL, the [IPEDS pipeline](https://github.com/BrianMKeegan/ipeds-pipeline), and BoulderPublicData's Election-Results — three projects that converged on the same answers from different problem domains.

## Wickham-tidy as the storage shape

The canonical storage shape is **one row per observation, one column per variable, one cell per value**, per [Wickham 2014](https://www.jstatsoft.org/article/view/v059i10). Every column is a variable; every row is an observation; data of distinct kinds live in separate tables.

In a liberation project, this means:

- **One CSV** in `data/processed/` is the dataset. Each row is one observation, identified by a composite key (`source`, `vintage`, plus whatever domain key — `precinct`/`contest`/`candidate`, `unitid`/`year`/`variable`, etc.).
- A **second CSV** in `data/processed/provenance.csv` is the per-extract sidecar, keyed on `(source, vintage)`. See [Provenance](#provenance) below.
- A **third CSV** or YAML in `data/lookups/concepts.{csv,yaml}` (or a Python module `scripts/concepts.py`) carries the harmonization metadata when the project is multi-source. See [Concept catalogs](#concept-catalogs).

Why long form, given that nobody wants to *read* a long-form CSV?

- **Unions are trivial.** A new vintage is more rows, not more columns. A new source is more rows. The schema stays put.
- **Auditing is uniform.** Null rates, distinct counts, dtype conformance — the audit code runs the same against every column regardless of source or vintage.
- **Cross-source comparison is a `groupby`.** Once two sources have entries on the same concept, comparing them is one pandas call.
- **The wide views readers want are recipes, not schemas.** `docs/filter-pivot-recipes.md` (see [below](#filter-pivot-recipes)) is how analysts get the year × variable matrix.

### When wide is the natural primary

A few domains genuinely have a wide-as-primary unit of observation. Cast-Vote-Records are the canonical example: one row per ballot, one column per contest, the ballot is the observation. Forcing CVR into long form (one row per ballot × contest) bloats the dataset by 30–50× with no analytical benefit because nobody analyzes ballots one contest at a time.

The rule: if the row-as-observation cardinality is naturally small (≤ ~50 columns) and contests/variables are analytically inseparable, keep wide. Still emit a tidy long-form derivative for cross-source analysis if the project participates in a multi-source comparison. BoulderPublicData/Cast-Vote-Records does both.

## The canonical schema

`scripts/schema.py` declares the columns once and provides a normalization helper. Sketch:

```python
# scripts/schema.py
from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
from pandera.typing.pandas import DataFrame, Series

# The canonical column list. Every parser emits these (plus domain columns).
LONG_COLUMNS = [
    "source",          # registry slug; joins to provenance
    "vintage",         # year or version
    # ── identifying columns (domain-specific) ──
    "precinct",
    "contest",
    "candidate",
    # ── measurement column(s) ──
    "votes",
    # ── optional harmonization ──
    "concept",         # cross-source concept key, nullable
]


class CanonicalLong(pa.DataFrameModel):
    source: Series[str]
    vintage: Series[str]                       # string — vintages aren't always years
    precinct: Series[str] = pa.Field(nullable=True)
    contest: Series[str]
    candidate: Series[str] = pa.Field(nullable=True)
    votes: Series[pd.Int64Dtype] = pa.Field(ge=0, nullable=True)
    concept: Series[str] = pa.Field(nullable=True)

    class Config:
        strict = True
        coerce = True


def normalize_long(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce a parser's raw output to the canonical schema.

    Parsers may produce extra columns during cleaning; this helper drops
    them, reorders to LONG_COLUMNS, coerces dtypes, and validates.
    """
    missing = [c for c in LONG_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"normalize_long: missing required columns: {missing}")
    df = df[LONG_COLUMNS].copy()
    return CanonicalLong.validate(df)
```

Two design choices worth defending:

- **`vintage` is a string.** Years aren't always integers (`"2024-Q1"`, `"2024-special-recall"`), and even when they are, treating them as strings prevents accidental arithmetic and preserves the natural ordering for sort.
- **`Int64` (nullable) over `int64` (numpy-backed).** Vote counts, enrollment counts, dollar amounts — all are non-negative integers, but they're frequently missing for legitimate reasons (suppressed cells, year-not-reported). Nullable integers keep zero and NA distinct.

The schema goes *inside* the parser pipeline, not at the consumer boundary. Validation at write time is the gate; consumers read a validated artifact.

**The schema is a contract.** Think of `LONG_COLUMNS` + the pandera class together as a *contract* the processed CSV obeys, separate from how any particular parser produces it: declared column names + types + nullability + value ranges, with everything else (the source's quirks, the parser's intermediate columns) silently absorbed into the parser's internal work. The data dictionary is the human-readable side of the same contract; the pandera class is the machine-enforced side. A parser's job is to translate the *publisher's* contract (whatever the source happens to publish) into this contract; `_normalize.py` helpers are reusable contract-preserving operations. Naming this lets `AGENTS.md` distinguish two failure modes that look similar but require different fixes: a *contract violation* means the parser produced something the schema rejected (fix the parser); a *contract change* means the project decided to evolve `LONG_COLUMNS` or a dtype (a schema migration, document in the changelog).

## Data dictionary

Hand-maintained, one entry per column. Lives at `docs/data-dictionary.md`. The IPEDS pipeline's `DATA_DICTIONARY.md` is the model.

The dictionary plus the published `metadata.yaml` are an informal **DCAT** / **DCAT-US** catalog record (Catalog → Dataset → Distribution); emitting a formal DCAT record is an optional interoperability step covered in [`context.md`](context.md#crosswalk-standards--what-the-skill-already-builds), not a precondition for a good dictionary.

Template per column:

```markdown
## `<column_name>`

- **Type:** `<dtype>` (one of: `string`, `Int64`, `Float64`, `boolean`, `date`, `datetime`)
- **Description:** One or two sentences in plain English. Avoid jargon the data dictionary itself doesn't define.
- **Source(s):** Which `source` slugs contribute this column, and where in their original schema it comes from.
- **Vocabulary / units:** If categorical, the controlled vocabulary. If numeric, the units. If a code, the code system (FIPS, NCES, ISO 3166-2, agency-internal).
- **Known caveats:** Vintage breakpoints, definitional shifts, ID-format changes, sentinel values.
- **Crosswalks:** Joining lookup tables in `data/lookups/`, if any.
```

Caveats are what make the dictionary worth maintaining. *"2022's roster ID format changed from `R######` to `R21-######`, so roster IDs are not safely comparable across that boundary"* is the kind of note that prevents a downstream user from joining incorrectly across the breakpoint. Inventing the convention is cheap; maintaining it discipline.

The dictionary's mechanical complement is `docs/variables.{md,csv}`, **auto-generated** by `scripts/audit.py` from the data itself (dtype, distinct count, null rate, min/max for numeric, five sample values for categorical). Treat the auto-generated file as the dictionary's sanity check: if `variables.csv` says a column is `object` but the dictionary says `Int64`, one is wrong, and it's usually the parser.

## Concept catalogs

When two or more sources measure the same underlying thing under different names — IPEDS reports total fall enrollment as `EFTOTLT`, the Colorado Department of Higher Education reports it as `TOTAL_HEADCOUNT`, the institution's own factbook calls it `fall_census_total` — the harmonization happens through a **concept catalog**.

A concept catalog is *not* a rename map. A rename map is a foot-gun: it asserts equivalence without documenting the disagreements. A concept catalog is a structured record that for each concept declares:

1. The canonical concept name.
2. Which source variables map to it, per source × vintage.
3. **The caveats** — what is and is not comparable across those mappings.

Each concept entry functions as a *contract* — a reusable cross-source equivalence assertion with declared inputs (source × vintage × variable), a declared output (the canonical concept), and declared invariants (the caveats that bound the equivalence). Naming this matches the schema-as-contract framing above: the schema is the contract at the *column* level; the concept catalog is the contract at the *cross-source-equivalence* level. A concept whose caveats list is empty is suspicious — like a function with no preconditions, it's usually under-specified rather than universal.

The [IPEDS pipeline's `concepts.py`](https://github.com/BrianMKeegan/ipeds-pipeline) is the canonical model. Sketch in YAML form for projects that prefer a data-only catalog at `data/lookups/concepts.yaml`:

```yaml
- concept: enrollment.headcount_fall_total
  description: Total fall headcount enrollment, all students, all levels.
  sources:
    ipeds:
      vintages: [2010-, ]
      variable: EFTOTLT
      survey: EF
      notes: Census-date snapshot, fall term.
    cdhe:
      vintages: [2018-, ]
      variable: TOTAL_HEADCOUNT
      notes: Reported per-institution to the state Department of Higher Education.
  caveats:
    - "IPEDS' Non-Resident Alien category is wider than CDHE's Non-Resident
       category (CDHE excludes students on humanitarian visas); breakdowns
       by residency are NOT cross-source comparable, but the total is."
    - "CDHE data is not available before 2018; do not infer the IPEDS-only
       years as comparable in any sense to the later joint period."
```

Three patterns worth holding to:

- **Concepts carry caveats, always.** A concept with `caveats: []` is suspicious; either the comparison genuinely is clean (rare for multi-source civic data) or someone hasn't done the comparison carefully.
- **Vintage-bounded source mappings.** A source's variable name and definition can change mid-period. The concept entry records *which vintages of a source map to this concept*, not just the source as a whole.
- **The catalog is queried, not just read.** `scripts/concepts.py` should expose `concept_for(source, vintage, variable) -> str` and `caveats_for(concept) -> list[str]` so the pipeline can attach the harmonized `concept` column at clean time and the audit can flag missing caveats.

For single-source projects, no concept catalog is needed — the column names of the source *are* the concepts. The catalog earns its keep when the project crosses two sources or merges multiple agencies' data.

## Provenance

The audit trail. Three rules:

1. **Per-extract, not per-row.** Source URL, retrieval timestamp, sha256, extraction quality, extraction notes — these are properties of an *extract* (a source × vintage pull), not of every cell. Carrying them on every row inflates the deliverable for no analytical benefit. Sidecar instead.

2. **Sidecar at `data/processed/provenance.csv`.** One row per `(source, vintage)`. Joined on demand. Columns:

   | Column | Type | Description |
   |---|---|---|
   | `source` | string | Source slug; joins to processed CSV |
   | `vintage` | string | Vintage; joins to processed CSV |
   | `source_url` | string | Where the original was fetched |
   | `retrieved_at` | datetime UTC | When it was fetched |
   | `sha256` | string | Content hash of the original artifact |
   | `extraction_quality` | string | One of `clean`, `caveats`, `degraded`, `ocr_tesseract` |
   | `extraction_notes` | string | Free text — vintage drift, OCR fallback used, etc. |
   | `parser_module` | string | Which parser file was used (`scripts.parsers.boulder_sov_2009`) |

3. **Per-row hashes only when the parser legitimately needs them.** If a parser is OCR-fragile and you want each row to declare which source PDF it came from at the page level, add `source_file_sha256` and `page` as columns. [`extract-pdf.md`](extract-pdf.md) shows this pattern in its parser skeleton. Most pipelines don't need it.

Provenance is what makes the dataset *defensible*. When a downstream user finds an anomaly, the chain is: `(source, vintage)` in the processed CSV → matching row in `provenance.csv` → `source_url` and `sha256` → the original file in `data/original/`. Anyone with a clone can reproduce the extraction and verify.

The sidecar is, in effect, a hand-rolled **W3C PROV** record — its columns map onto PROV's *Entity* (the source artifact), *Activity* (the parser run), and *Agent* (the project). You don't need to serialize PROV-O to benefit from naming the alignment; see [`context.md`](context.md#crosswalk-standards--what-the-skill-already-builds) for the optional deepening. Background, not a requirement.

## Data quality

"Quality" is the deliverable, but it isn't one thing. The skill commits to a working definition: **data is high-quality when it is *fit for use*** (Juran 1974; Wang & Strong 1996). What "fit" means depends on what the user is doing with it, so the skill uses a multi-dimensional decomposition for naming what changed when a parser, schema, or audit changes.

### Five dimensions, mapped to pipeline operations

This skill adopts the five-dimension naming from Cai & Zhu (2015) because it's organized from the *user's* perspective — the right framing for civic data where the publisher and the consumer are different organizations. Every pipeline operation maps to one of these dimensions, so when a reviewer asks "what improved?" or "what broke?" the answer is a dimension, not a vibe. (For the standards-minded: this decomposition parallels the W3C **Data Quality Vocabulary**; the optional alignment is sketched in [`context.md`](context.md#crosswalk-standards--what-the-skill-already-builds). It's background, not a measurement requirement.)

| Dimension | What it covers | Where this skill produces it |
|---|---|---|
| **Availability** | Can the user obtain the data? Is it current? Is the use authorized? | `fetch.py` + the source registry + `provenance.csv`'s `source_url`, `retrieved_at`, license/legal-basis notes |
| **Usability** | Is the data documented, credible, and accompanied by enough metadata to be used safely? | `docs/data-dictionary.md` (hand-authored), `docs/methodology.qmd`, Datasette `metadata.yaml`, the bibliography of prior work in the README's *movement context* |
| **Reliability** | Is the data accurate, consistent, complete, structurally intact, and auditable? | `pandera` schema (consistency + integrity); `audit.py` null rates and distinct values (completeness); `reconcile.py` against authoritative totals (accuracy); the diff-able `data/audit/summary-*.md` (auditability) |
| **Relevance** | Does the data answer the question the user is bringing? | Survey-phase decisions (unit of observation, vintage convention); the concept catalog (cross-source harmonization with caveats) |
| **Presentation Quality** | Can the user read and reason about the data without translating? | Tidy long-form, ID-like columns kept as strings, documented sentinel values, Datasette's faceted views, the filter-pivot recipes |

The first four are load-bearing; presentation quality is the polish on top. When a parser is failing, identify which of these is in trouble — that tells you which file to open.

### The four operational dimensions

For dimensions you actually *compute* in code, four are durable enough across the literature to take seriously:

| Dimension | Working definition | How the skill measures it |
|---|---|---|
| **Accuracy** | Closeness to a known reference value | `reconcile.py` against the source's own published totals |
| **Completeness** | Non-null share, with the three-way distinction *missing-and-known-to-exist* / *does-not-exist* / *unknown-whether-exists* recorded in the dictionary | `audit.py` null rates; sentinel-value handling in parsers (see [`pipeline.md`](pipeline.md#4-missing-value-treatment)) |
| **Consistency** | Conformance to declared schema and to cross-source agreement | `pandera` schema violations; cross-source `reconcile.py` |
| **Timeliness** | `max(0, 1 − (fetched_at − published_at) / publisher_cadence)` | `provenance.csv`'s timestamps + the source's declared cadence |

### Three layers of quality work — profile, measure, monitor

A useful decomposition for what `audit.py` actually does (Ehrlinger & Wöß 2022):

- **Profiling** — *describe what's there.* Dtypes, distinct counts, null rates, min/max, value patterns, distributions. The skill produces `docs/variables.{md,csv}` automatically on every audit.
- **Measurement** — *compute metrics against declared dimensions.* Pandera catches schema violations at write time; `reconcile.py` catches accuracy violations against authoritative totals.
- **Monitoring** — *catch drift over time.* The recurring-refresh PR + diff-able `data/audit/summary-*.md` is the skill's monitoring loop. Commercial DQ tools generally paywall monitoring; this comes for free from cron + version control.

Don't conflate them. A project that profiles without measuring has descriptive stats but no thresholds; a project that measures without monitoring catches today's bug but not tomorrow's drift.

## Free-text quality — the narrative-column pattern

Most civic-data sources combine a few structured fields (date, location, status, cost) with one or more free-text fields (incident narrative, FOIA response, case disposition note, 311 description). The free text is almost always the lowest-quality part of the record and the highest-stakes part for analysis — it determines what category the row belongs to, and it's written by many different staff over many years with no controlled vocabulary.

The pattern that works (after Woods et al. 2024's maintenance-work-order study):

1. **Treat the free-text field as the primary site of DQ failure**, not as the authoritative description. Benchmark it *against* the structured fields, not the other way around.
2. **Build the controlled vocabulary empirically.** Frequency-analyze the corpus, find the top tokens covering ~99% of records, lexically normalize (misspellings, tense, prefixes), then group synonyms into 5–10 canonical action/disposition terms. Top-down vocabularies miss the verbs that actually appear; bottom-up vocabularies catch the long-tail synonyms.
3. **Store the vocabulary in `data/lookups/`** as a yaml file with one entry per canonical term and its synonym set. Same structure as the concept catalog (see [Concept catalogs](#concept-catalogs)), with two differences: the canonical terms are verbs/dispositions instead of variables, and each entry can carry an *expected-structured-field-pattern* the term should co-occur with.
4. **Write parser-level cross-checks** that compare the narrative verb against the structured fields and flag mismatches as DQ issues: cost-vs-action ("service" with $0 labour = work logged but not done); preventative-vs-corrective; verb-conflated-with-discovery ("investigate X" with $0 follow-up).
5. **For records with no verb in the narrative**, *infer* the likely category from the structured fields but mark the row with an `inferred` or `uncertain` classifier so downstream users can choose whether to include it. Never silently fill.

The audit's job, then, is not to clean these records but to report: *N records had the verb match the structured fields, M had mismatches (catalogued by pattern), K had no verb (inferred), L could not be classified.*

## Pipeline shape

Two complementary lenses; the same artifacts read by each.

**Conceptual / logical / physical** — every data workflow traverses three layers regardless of tooling. *Conceptual* is what the workflow is supposed to do; *logical* is how it's sequenced, typed, and validated; *physical* is how the code runs. Naming the layer you're working in shortcuts the wrong-altitude argument ("we're at conceptual; defer the dtype question").

| Layer | Question it answers | Where this skill produces it |
|---|---|---|
| Conceptual | *What* is this workflow doing, and what does its output mean? | Survey notes; the data dictionary; `LONG_COLUMNS`; the concept catalog |
| Logical | *How* are the pieces sequenced and validated? What are the contracts at each boundary? | The pandera schema; the 9-step cleaning pipeline; `validators.py`; the reject-port pattern |
| Physical | *How does this actually execute?* | The per-vintage parsers; `clean.py`; the published CSV / Datasette / Quarto deploys |

A bug in a parser is a *physical* problem; a bug in the schema is *logical*; a bug in "we picked the wrong unit of observation" is *conceptual* and orders-of-magnitude more expensive to fix late. The workflow's six phases (Survey → Scaffold → Extract → Tidy → Audit → Publish) progress through these layers more or less in order — the layering is the diagnostic vocabulary, not a separate workflow.

**Three phases of DQ work** (Batini et al. 2009) — orthogonal to the layers above, this names the *kinds* of activity any DQ effort performs:

- **State reconstruction** — the contextual work *before* you measure: find the codebook, identify the records officer, surface prior journalism, get the FOIA history. This is the Survey phase; see [SKILL.md's Survey section](../SKILL.md).
- **Assessment** — measurement plus comparison against reference values. `audit.py` is measurement; `reconcile.py` is assessment.
- **Improvement** — parser-by-parser, vintage-by-vintage iteration. The recurring-refresh PR is the closure.

Two strategic choices structure improvement:

- **Data-driven** — fix the data after it's published. Civic projects are almost always here, because the publisher is out of reach. Cost-efficient short-term, expensive long-term.
- **Process-driven** — fix the publisher's process so the data arrives clean. Cheap long-term, but the lead time is years. For civic data, the closest realistic move is *advocating for better source agreements* (the FOIA-modernization angle).

The honest framing for AGENTS.md: a civic liberation pipeline is the data-driven *short-term* answer to a problem whose process-driven long-term answer (the agency publishes better data in the first place) is decades away. That tradeoff is structural, not accidental.

## Validation

A liberation pipeline benefits from validation in three places, each catching a different class of problem.

| Layer | Tool | What it catches |
|---|---|---|
| Record-level | `pydantic` | Malformed individual records during parsing (e.g., a vote count that parsed as `"---"`). Per-row validation is slow; use sparingly, usually only inside a parser's coercion pass. |
| DataFrame-level | `pandera` | Schema drift at the boundary of the pipeline (new column appeared, dtype changed, required column missing, value out of declared range). This is the gate. |
| Behavior | `pytest` | The parser does what the project says it does — a known-fixture-in, expected-frame-out test per source × vintage. |

The pandera schema in `scripts/schema.py` is the most consequential of the three. It runs at clean time, before write, and rejects frames that don't match. `strict=True` rejects unknown columns; `coerce=True` lets parsers be loose with intermediate dtypes and the schema does the final cast.

Pandera schemas also double as documentation. The schema declaration is more enforceable than prose in `docs/data-dictionary.md`; treat the two as complementary — the schema declares the contract, the dictionary explains it.

Per-parser pytest tests live at `tests/test_<source>_<vintage>.py`. The minimum useful test:

```python
# tests/test_boulder_sov_2009.py
from pathlib import Path
import pandas as pd
from scripts.parsers.boulder_sov_2009 import parse

FIXTURE = Path(__file__).parent / "fixtures" / "boulder_sov_2009_small.pdf"

def test_parses_canonical_schema():
    df = parse(FIXTURE)
    # Validated by normalize_long inside parse()
    assert len(df) > 0
    assert df["source"].unique().tolist() == ["boulder_county_sov"]
    assert set(df["contest"].unique()) >= {"PRESIDENT", "GOVERNOR"}

def test_known_totals():
    """Top-line totals from a small subset of the SoV."""
    df = parse(FIXTURE)
    pres_total = df.query("contest == 'PRESIDENT'")["votes"].sum()
    assert pres_total == 12_345  # known from the source PDF's own total row
```

The second test is doing the reconciliation work that `scripts/reconcile.py` would do at full scale — a small enough version that it can run on a fixture in CI in milliseconds. Both tests are cheap; both fail loudly when a vintage's parser drifts.

## Filter-pivot recipes

`docs/filter-pivot-recipes.md` is the document that bridges tidy storage to wide-form analysis. Ship it in three stacks, all reading the canonical CSV at `data/processed/<project>.csv`:

- **Python / pandas** — for Python-using analysts and downstream pipelines. `pd.read_csv(path, dtype=str)` is the safe default; coerce specific columns explicitly.
- **R / tidyverse** — for academic and policy researchers. `readr::read_csv(path, col_types = cols(.default = col_character()))` mirrors the pandas default.
- **SQL / DuckDB** — for analysts who prefer SQL, and as a copy-paste-into-Datasette path. `duckdb` reads the CSV directly via `read_csv('data/processed/<project>.csv')`; no load step, no `pyarrow` dependency, and the same SQL runs against the published Datasette instance and most warehouse engines.

(If non-technical readers are a primary audience, an Excel / Google Sheets pivot-table recipe earns a fourth slot. The three above are the durable defaults.)

Four recipes carry most of the weight:

1. **Single-vintage wide pivot.** "Show me 2024 only, with one row per observation_id and the measurements as columns."
2. **Year × source matrix.** "How many rows from each source, in each vintage?" — the audit table, on demand for readers.
3. **Roll up to coarser geography.** "Aggregate from precinct to district." Requires a crosswalk; the recipe documents the join.
4. **Cross-source concept comparison.** "For every observation where source A and source B both report the same concept, show both values side by side." This is the payoff of the concept catalog.

Each recipe in each stack runs against a fixture so the documentation doesn't drift from the data. The IPEDS pipeline's filter-pivot recipes are the model.

## When schema decisions are hard to reverse

A few choices are expensive to change once the project has data and downstream users:

- **The unit of observation.** Changing from "row per precinct × contest × candidate" to "row per precinct × contest" later means every downstream join breaks. Get this right before the second source goes in.
- **The vintage convention.** Whether `vintage` is `"2024"`, `"2024-general"`, `"2024-Q1"`, or `"2024-11-05"` determines what kinds of within-year comparisons are sayable in the schema. Pick the finest granularity any source publishes and use that uniformly.
- **The composite primary key.** Whatever combination of columns must be unique — declare it in the pandera schema as a multi-column uniqueness check and enforce it. If you discover later that the key isn't actually unique, the cleanup is painful.

Spend the survey phase on these specifically. The cost of revisiting them after a project has a year of data and citations is high; the cost of getting them right upfront is one careful afternoon.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Schema validation fails on a previously-passing source | New vintage added new columns | Update `LONG_COLUMNS` and the schema; add the new columns to the data dictionary in the same commit |
| Pivot recipe in `filter-pivot-recipes.md` returns mostly NaN | New source introduced sparse coverage on the pivoted variable | Document in the concept catalog's `caveats`; consider whether the pivot is honest given the sparsity |
| Two sources have the "same" concept but different totals | Definitional difference not yet caveated | Add the caveat to the concept entry; do not silently average or pick a winner |
| Per-row hashes on every row | Provenance design drifted into per-row | Move to sidecar; carry only `source` and `vintage` on the row |
| `provenance.csv` has rows with no matching data | Source was registered but parser failed silently | `audit.py` should flag this; check for empty parser output upstream |
| Dictionary says `Int64`, `variables.csv` says `object` | Parser is returning a string column; schema is silently coercing to NaN | Fix the parser; the dictionary and the auto-generated variables report agreeing is a precondition |

## What to write in the AGENTS.md

- **Unit of observation** and why this one was chosen over the alternatives.
- **Vintage convention** — string format and granularity (year, year-quarter, election-date).
- **Concept catalog status** — none / single-source, or which concepts harmonize across which sources with which caveats.
- **Provenance scope** — per-extract sidecar by default; note any per-row provenance columns for OCR-fragile parsers.
- **Validation surface** — which parsers have pytest fixtures.

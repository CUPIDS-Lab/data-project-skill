# Pipeline: acquisition, cleaning, audit, reconciliation, and refresh

This reference covers the processing and verification layer of a liberation project, Outline sections 2 (Acquire) and 5 (Pipeline & audit), with the parser-time cleaning that sits inside section 3. It explains how originals arrive (probing, discovery, storage, records requests), what a parser does to make rows conform to the schema without losing the trail of what changed, and the watchful steps that catch what went wrong: audit, conservation, reconciliation, and the recurring refresh. What to *produce* (tidy shape, the schema contract, the dictionary, provenance, concepts) is in [`data-modeling.md`](data-modeling.md); the skeleton and every file in it are in [`project-template.md`](project-template.md); the checks every build runs and the human bulletproofing pass are in [`_shared/quality-and-bulletproofing.md`](_shared/quality-and-bulletproofing.md). The patterns here come from BoulderPublicData/Election-Results (where `reconcile.py` originated), the IPEDS pipeline (`discover.py` self-refresh), ProPublica's [data-bulletproofing guide](https://github.com/propublica/guides/blob/master/data-bulletproofing.md), and the projects these skills have served.

## Contents

- [Principles](#principles)
- [Part 1: Acquire](#part-1-acquire)
  - [Probe the live source before writing a parser](#probe-the-live-source-before-writing-a-parser)
  - [Vintage keys come from the file, not the publish path](#vintage-keys-come-from-the-file-not-the-publish-path)
  - [Discovery](#discovery)
  - [Fetching: idempotent, verified, refreshable](#fetching-idempotent-verified-refreshable)
  - [Storage budget](#storage-budget)
  - [Ephemeral sources](#ephemeral-sources)
  - [When the source path is a records request (FOIA, sunshine laws)](#when-the-source-path-is-a-records-request-foia-sunshine-laws)
- [Part 2: Cleaning and standardization](#part-2-cleaning-and-standardization)
  - [The cleaning steps](#the-cleaning-steps)
  - [1. Initial assessment: profile before you parse](#1-initial-assessment-profile-before-you-parse)
  - [2. Structural fixes](#2-structural-fixes)
  - [3. Deduplication](#3-deduplication)
  - [4. Missing-value treatment](#4-missing-value-treatment)
  - [5. Outlier detection](#5-outlier-detection)
  - [6. Standardization and normalization](#6-standardization-and-normalization)
  - [7. Validation and the reject file](#7-validation-and-the-reject-file)
  - [8. PII redaction](#8-pii-redaction)
  - [9. The row ledger and the conservation check](#9-the-row-ledger-and-the-conservation-check)
  - [Where this lives in the project](#where-this-lives-in-the-project)
- [Part 3: Audit, reconciliation, and refresh](#part-3-audit-reconciliation-and-refresh)
  - [Audit: what came in](#audit-what-came-in)
  - [The error log](#the-error-log)
  - [Reconciliation](#reconciliation)
  - [The recurring-refresh pattern](#the-recurring-refresh-pattern)
  - [Common failure modes](#common-failure-modes)
  - [What to write in AGENTS.md](#what-to-write-in-agentsmd)

## Principles

- **Originals are immutable.** Nothing writes back to `data/original/`. Every cleaning step reads from there and writes to `data/processed/` or `data/audit/`.
- **Probe before you parse.** Open real files from every era of the live source, and profile their columns, before writing coercion code.
- **Errors are durable, not fatal, and never silent.** An artifact that fails is recorded in a per-run error log that starts empty; a row that fails validation goes to the reject file with a reason; the rest of the run continues, and the audit summary reports both counts.
- **Fail loudly on empty or degenerate output.** An empty extraction, or one whose key columns are all null, is an error. If nothing survives, nothing is written over the last good output. No step substitutes sample, synthetic or cached data for a failed download or parse.
- **Count every row.** Each stage boundary keeps a ledger, and rows that disappear without being counted fail the build.
- **Coerce explicitly.** pandas's silent dtype inference causes most leading-zero bugs; declare types at the boundary.
- **Deterministic outputs.** The same originals produce byte-identical CSVs, provenance and audit reports: stable sort orders, no wall-clock time in content. Run times live in a separate, ignored `data/audit/run.json`.
- **Imputation is opt-in.** Preserve missingness and document it; fill only after an explicit decision in the decision-log.
- **Redact PII at the boundary of `data/processed/`.** Originals keep what the publisher published; the processed data obeys the project's policy.

---

# Part 1: Acquire

## Probe the live source before writing a parser

Before writing any parser, fetch one real file from *each* era you believe the source has, open several pages or sheets of each, and write down what you found as numbered findings in the decision-log. Every later cleaning rule should be able to cite a finding.

- **The live source, not a description of it.** Papers, notebooks, earlier pipelines and landing pages describe the source as it was. Publishers silently re-export: a series once served in several heterogeneous formats may now be served in one uniform format, or the reverse. One project built a parser for each of several historical schemas and then discarded all five when the live files turned out to be uniform; one download per claimed era would have cost minutes.
- **Every structural cohort, not one specimen.** A parser validated on one convenient file can fail silently on a file whose internal structure differs (another project's PDF adapter produced empty output on volumes with a different cross-reference layout). Validate on at least one file from every era and format variant, and run the reconcile gate across the whole corpus, not only the file it was developed on.
- **Embedded OCR is a claim, not a fact.** Compare an embedded text layer in a scanned PDF against the page image before trusting it; such layers were unusable several times in the projects reviewed.
- **Find the documentation and the contact.** The publisher's codebook, methodology or mandating statute, and a records officer or other person to ask when something is strange. Not finding them is itself a finding for the README's caveats.
- **Check the source against itself:** record counts against the publisher's claim (watch for truncation at 65,536 or 1,048,576 rows and other round limits), printed totals against the sum of rows, the date and geography range against what is claimed, and every categorical column grouped to surface spelling drift. Format-native error markers (`#REF!`, `#DIV/0!`, `#N/A` in spreadsheets, `null` in required JSON fields) originated with the publisher: count them and record them as caveats rather than silently coercing them to missing.

The full pre-release bulletproofing pass and its checklist are in [`_shared/quality-and-bulletproofing.md`](_shared/quality-and-bulletproofing.md).

## Vintage keys come from the file, not the publish path

Derive each artifact's vintage (the period it covers) from its file name or its content, never from the directory, URL path or date it was published under. Publishers routinely post a period's file later (fourth-quarter data the following February, an annual report in the next year's folder), and a discovery scan keyed on the publish path silently mislabels vintages. `scripts/source.py` has `vintage_from_filename()` and the template's `tests/test_source.py` pins a publish-directory case; add one for your source's naming pattern. When a document covers several periods, record both the printed period and the page it came from.

## Discovery

Discovery answers "is there a vintage we don't have yet?" without downloading anything. In the template, `artifacts()` in `scripts/source.py` lists everything upstream; `discover.py` (refresh group) reports which artifacts are new and writes `data/audit/discovery.md`. Two patterns:

**Static list.** For publishers with predictable URLs (`https://example.gov/annual-report/2024.pdf`, `…/2025.pdf`), list them, or generate them from a year range:

```python
# scripts/source.py
ARTIFACTS = [(str(year), f"https://example.gov/annual-report/{year}.pdf") for year in range(2010, 2026)]
```

A year that hasn't been published yet fails at fetch with a 404 in the error log; extend the range deliberately rather than guessing ahead.

**Index page.** For publishers with a landing page that lists what is available, scrape it and read each vintage from the link's file name:

```python
# scripts/source.py
import httpx
from selectolax.parser import HTMLParser

INDEX_URL = "https://example.gov/elections/historical-results/"


def artifacts() -> list[Artifact]:
    html = httpx.get(INDEX_URL, headers={"User-Agent": USER_AGENT}, timeout=60).text
    out = []
    for link in HTMLParser(html).css("a[href$='.pdf']"):
        url = link.attributes["href"]
        vintage = vintage_from_filename(url.rsplit("/", 1)[-1])
        if vintage is None:
            continue  # not a results file: log it if unsure
        out.append(Artifact(SOURCE_SLUG, vintage, url, DATA_ORIGINAL / SOURCE_SLUG / vintage / "sov.pdf"))
    return sorted(out, key=lambda a: (a.vintage, a.rel))
```

Save a copy of the index page as a test fixture, so a redesign that breaks the selector fails a test rather than producing an empty list. Discovery that suddenly finds zero artifacts is a regression, not a quiet month.

## Fetching: idempotent, verified, refreshable

`fetch.py` downloads what is missing into `data/original/<source>/<vintage>/` and records each file in `data/original/manifest.json` (URL, sha256, size, fetch time). It is idempotent: a re-run downloads nothing and changes nothing. It retries with exponential backoff on connection errors and 429 or 5xx responses only, never caches an error response, and rejects an empty body or an HTML error page served where a PDF was expected. It identifies itself with a user agent that carries a contact, and prints throttled progress (`[i/n] fetch …`) so a long run shows it is alive.

**Forced refetch.** A cached original can go stale when a publisher revises a file at the same URL. `fetch --fresh` (or `run --fresh`) bypasses the HTTP cache and re-downloads everything. Identical bytes change nothing; changed bytes replace the file, keep the old hash in `previous_sha256`, and are reported, so the revision shows in the refresh PR's manifest diff and the change can be explained in `CHANGELOG.md`. Without `--fresh`, a re-download that doesn't match the recorded hash is an error. Cleaning also re-hashes each original and reports any file that no longer matches its manifest entry.

**Scraper hygiene.** Back off on 429 and 503; expect a CI runner's IP to be blocked where a laptop isn't, and plan a local capture; use the Wayback Machine's timemap when its CDX endpoint is overloaded; never disable TLS verification (complete the certificate chain instead); and keep an error page's status and title as evidence, not its text as data. `extract-web.md` and `extract-api.md` cover the details.

## Storage budget

Decide per source where the originals live, and record it in the decision-log: committed to git (small text and tabular files), Git LFS (large binaries such as PDF volumes and scans), or outside git with the URL and sha256 kept in the committed manifest (files too large or too many for LFS, or restricted from redistribution). CI fails on any committed file over 95 MiB, short of GitHub's 100 MB limit, because a file over the limit can't be pushed and removing it from history is painful. When processed data is too large to commit, the committed audit reports and `headline.json` are the shared record that every regeneration must reproduce. The mechanics are in [`project-template.md`](project-template.md#storage-budget).

## Ephemeral sources

Some sources show only the current state (today's list of open cases, this week's inspections), so a missed capture is lost for good and cannot be backfilled. For them:

- **Write once per capture:** one dated file per run under `data/original/<source>/<YYYY-MM-DD>/`, never overwritten.
- **Don't trust a single scheduled run.** GitHub's scheduled workflows start late or are skipped under load. Schedule a second, redundant run a few hours later (the second finds the day's file already present and does nothing), and keep a run log.
- **Detect gaps:** the discovery report lists capture dates, and a missing date is reported as a gap, with the cause recorded when known.
- **Say what can't be recovered.** The dictionary's caveats and the README name the first capture date and every known gap.

## When the source path is a records request (FOIA, sunshine laws)

If the data has to be requested rather than downloaded, the request is part of acquisition, and a few process choices change what comes back:

- **Ask for data, not narrative.** Request the underlying records in their native machine-readable format ("the database export, or the spreadsheet behind this report"), not "a report about X". Agencies often default to printing to PDF; naming the format avoids a second request.
- **Know the clock and the fees.** Federal FOIA runs about 20 business days, often longer; fee categories differ for commercial, news-media or educational, and other requesters, and public-interest waivers exist. State open-records laws vary; the records officer is the contact, and `FOIA.gov` routes federal requests.
- **Treat redactions as findings.** A heavily redacted or truncated release can still carry usable tables; record what was withheld and the claimed exemption in the dictionary's caveats and the decision-log. An excessive redaction is itself a transparency story.
- **Decide what the project will not liberate.** "Available to extract" is not "responsible to publish." Where a release contains personal data that privacy law protects, or where a likely downstream use is one the project disavows, that judgment belongs in Outline section 1, before parsing: see [`_shared/values-and-gates.md`](_shared/values-and-gates.md). The wider transparency-law landscape is in [`lineage-and-landscape.md`](lineage-and-landscape.md).

---

# Part 2: Cleaning and standardization

## The cleaning steps

Every parser does three things: extract from a source, transform what is there, and publish to a sink. Naming the role a step plays sharpens diagnosis: a *source-extraction* failure (wrong encoding, a missed sentinel, a mis-inferred dtype) is fixed in the parser's read calls; a *transformation* failure (consistency, dedup logic, missingness) in the middle of the parser; a *sink-publication* failure (leaked PII, inconsistent formats, output that breaks the schema contract) at the end, or in `clean.py` and the publish code.

| Step | Role | Goal | Where it happens |
| --- | --- | --- | --- |
| 1. Initial assessment | Source-extraction | Know what you have | while probing; `docs/variables.*` on every audit |
| 2. Structural fixes | Source-extraction | Make the shape canonical | the parser |
| 3. Deduplication | Transformation | Remove repeated keys before validation | `clean.py` (`schema.dedupe`); fuzzy matching in the parser |
| 4. Missing-value treatment | Transformation | Decide per mechanism, document | the parser and the dictionary |
| 5. Outlier detection | Transformation | Catch the impossible and the suspicious | the parser, or schema checks |
| 6. Standardization | Transformation | Make values uniform | the parser; vocabularies in `data/lookups/` |
| 7. Validation and the reject file | Transformation | Gate output against the [schema contract](data-modeling.md#the-canonical-schema) | `clean.py` (`schema.split_valid`) → `data/audit/rejected.csv` |
| 8. PII redaction | Sink-publication | Apply policy at the processed boundary | the parser or publish code |
| 9. Row ledger and conservation | Sink-publication | Account for every row | `clean.py` → `run.json`, `summary.md` |

Run them in order: earlier steps surface issues that change how later ones behave.

## 1. Initial assessment: profile before you parse

Three things, every time, before writing any coercion code:

- **`Describe`** — `df.describe(include='all')` for numeric + categorical summaries; `df.info()` for dtypes and non-null counts; `df.shape` for dimensions.
- **`Column profile`** — per column: dtype, distinct count, null count and percentage, min/max for numeric, top-5 frequent values for categorical, length distribution for strings.
- **`Histogram`** — for any numeric column, plot a histogram or compute quartiles. For categorical columns, plot a value-counts bar. Outliers and modal sentinel values (`-9`, `9999`, `1900-01-01`) show up immediately.

Tools, in order of escalation:

| Tool | When |
|---|---|
| `pandas.DataFrame.describe()`, `.info()`, `.value_counts()` | Default; for a quick parser-side profile |
| [`ydata-profiling`](https://github.com/ydataai/ydata-profiling) | One-shot HTML report; useful for sharing with non-Python collaborators |
| `DuckDB`'s `SUMMARIZE table` | When the data is large enough that pandas is slow |
| `sqlite-utils analyze-tables` | When the data is already in the Datasette SQLite file |

The profile produced *at this step* gets persisted: `audit.py`'s auto-generated `docs/variables.{md,csv}` is the durable artifact, and the diff between vintages is what surfaces drift over time. See the *profiling* sub-step of profiling / measurement / monitoring in [`data-modeling.md#data-quality`](data-modeling.md#data-quality).

## 2. Structural fixes

- **Column names → `snake_case`** with no spaces, no special characters, no leading digits. A small helper:
  ```python
  import re
  def snake(s: str) -> str:
      s = re.sub(r'[^0-9a-zA-Z]+', '_', s).strip('_').lower()
      if s and s[0].isdigit():
          s = '_' + s
      return s
  df.columns = [snake(c) for c in df.columns]
  ```
- **Dtype casting** with `pandas.to_numeric(..., errors='coerce')`, `pandas.to_datetime(..., errors='coerce')`, and explicit `dtype="string"` for ID-like columns. The `errors='coerce'` flag turns un-parseable values into `NaT`/`NaN` instead of raising — combined with schema validation (step 7), this is how values that won't parse reach the reject file instead of crashing the parser.
- **Split or merge columns** as the schema requires — e.g. an "Address" column → `street`, `city`, `state`, `zip`; or a `first_name` + `last_name` → `full_name`. Document either direction in the data dictionary.
- **Drop fully empty rows and columns:** `df.dropna(how='all')` for rows; `df.dropna(axis=1, how='all')` for columns. Fully empty *and not previously documented* is a structural artifact (Excel padding, export bug), not data.

## 3. Deduplication

Deduplicate *before* validating, so validation reports real violations rather than duplicates it cannot drop. `clean.py` removes rows that repeat the natural key (`KEY_COLUMNS`) with `schema.dedupe`, keeping the last reading (the latest correction wins), and counts them in the ledger. Inside a parser, two kinds of duplicates call for two different operations:

### Exact duplicates

```python
exact_dupes = df[df.duplicated(subset=KEY_COLS, keep=False)]
df = df.drop_duplicates(subset=KEY_COLS, keep='first')
```

The `subset=` argument matters. Across the whole row often catches too few (one whitespace character means two rows aren't equal); restricted to the natural key catches the right ones. Decide the keep policy and log it:

- **`keep='first'`** — earliest record wins; safe default when there's no quality difference.
- **`keep='last'`** — latest record wins; appropriate when records get corrected over time.
- **Merge** — fold the duplicates into one row, preferring non-null values per column. Pandas's `groupby(key).agg(...)` with a per-column priority dict is the standard pattern.

### Near-duplicates (fuzzy matching)

Two records that refer to the same entity but differ in spelling, case, whitespace, or transcription. Two algorithms cover most cases:

| Algorithm | What it measures | When to use |
|---|---|---|
| **Levenshtein** | Edit distance (insertions + deletions + substitutions) | OCR'd text, typos, transcription errors |
| **Jaro-Winkler** | String similarity favoring prefix matches | Names, addresses (where prefix consistency matters more than the tail) |

Tools:

- [`rapidfuzz`](https://github.com/maxbachmann/RapidFuzz) — the fast modern fuzzy-matching library; `fuzz.ratio`, `fuzz.token_sort_ratio`, `process.extract`.
- [`jellyfish`](https://github.com/jamesturk/jellyfish) — `jaro_winkler_similarity`, `damerau_levenshtein_distance`, plus phonetic encoders (Soundex, Metaphone, NYSIIS) when phonetic matches matter.
- [`recordlinkage`](https://github.com/J535D165/recordlinkage) — full record-matching framework with blocking, comparison, and classification stages; appropriate when matching across two large sources.

Pattern for **record matching** between two sources:

```python
import recordlinkage
indexer = recordlinkage.Index()
indexer.block('zip')                     # block by an exact-match field to limit pairs
candidate_pairs = indexer.index(df_a, df_b)
compare = recordlinkage.Compare()
compare.string('name', 'name', method='jarowinkler', threshold=0.85, label='name_sim')
compare.exact('dob', 'dob', label='dob_match')
features = compare.compute(candidate_pairs, df_a, df_b)
# features is a DataFrame of similarity scores per pair; threshold + score to classify
matches = features[features.sum(axis=1) > 1.5]
```

Output a *similarity score* with every match, and persist the pair-with-score table to `data/audit/`. Never silently merge near-duplicates without a reviewable record of which records were merged and at what similarity.

## 4. Missing-value treatment

The default is **preserve NA** and document the mechanism. Imputation is opt-in and requires an explicit, dated decision in the decision-log.

Classify the missingness mechanism (Rubin's framework):

| Mechanism | Definition | How to test | Reasonable response |
|---|---|---|---|
| **MCAR** — Missing Completely At Random | Missingness is unrelated to any variable, observed or not. *Example: lab samples randomly lost in transit.* | [Little's MCAR test](https://en.wikipedia.org/wiki/Missing_data#Little's_MCAR_Test); compare the distributions of observed columns conditional on missingness in the target column. | Listwise delete if <5% of records affected; document the deletion count. Mean/median imputation acceptable if needed downstream. |
| **MAR** — Missing At Random | Missingness depends on *observed* variables, not the missing value itself. *Example: younger participants skip income questions more.* | Compare missingness patterns across groups defined by observed variables (`df.groupby('age_bracket')['income'].isna().mean()`). | Multiple imputation (`sklearn.experimental.IterativeImputer`, `miceforest`) or regression imputation — both should be opt-in flags, not pipeline defaults. |
| **MNAR** — Missing Not At Random | Missingness depends on the *unobserved* value itself. *Example: high-income respondents refuse to report income.* | Cannot be tested from the data alone; requires domain knowledge or external corroboration. | Sensitivity analysis, selection models. Often the right answer is **don't impute** and document the bias in the data dictionary's caveat section. |

The data dictionary should record, per column, the three-way distinction Batini surfaces — *missing-and-known-to-exist* vs *does-not-exist* vs *unknown-whether-exists* — because they require different downstream treatment.

Concrete sentinel-to-NA conversion belongs in the parser, not the consumer:

```python
df['income'] = df['income'].replace([-9, -99, 999999, '.', 'N/A', 'NULL'], pd.NA)
df['birth_date'] = df['birth_date'].replace({'1900-01-01': pd.NaT, '9999-12-31': pd.NaT})
```

Document the sentinel set per column in `docs/data-dictionary.md` under *Known caveats*.

## 5. Outlier detection

Two complementary approaches; use both.

### Statistical outliers

| Method | Definition | When |
|---|---|---|
| **IQR rule** | Below `Q1 − 1.5·IQR` or above `Q3 + 1.5·IQR` | Default for skewed distributions; robust to non-normality |
| **z-score** | `|x − μ| / σ > 3` | When the column is approximately normal |
| **Mahalanobis distance** | Multi-variate distance from the centroid in covariance-weighted space | When outliers are only visible in two+ dimensions jointly |
| **Isolation Forest** | Tree-based density anomaly score | Large mixed-type data where rules are hard to set |

```python
q1, q3 = df['amount'].quantile([0.25, 0.75])
iqr = q3 - q1
df['amount_outlier'] = (df['amount'] < q1 - 1.5*iqr) | (df['amount'] > q3 + 1.5*iqr)
```

### Domain validation — the impossible-value table

A row whose value violates physical or definitional limits isn't outlier-suspicious; it's *wrong*. Catch these with explicit range checks:

| Field | Plausible range | Notes |
|---|---|---|
| Age (years) | 0 – 120 | Flag >100 for review |
| Height (cm) | 50 – 250 | |
| Weight (kg) | 1 – 300 | |
| Systolic BP (mmHg) | 60 – 250 | |
| Diastolic BP (mmHg) | 30 – 150 | Must be < systolic |
| Body temperature (°C) | 30 – 45 | |
| Likert scale | integers 1 – 5 | reject non-integers |
| Percentage | 0 – 100 | unless explicitly proportion (0 – 1) |
| Latitude | −90 – 90 | |
| Longitude | −180 – 180 | |
| Year of birth | 1900 – current year | Or earlier for historical datasets, with floor documented |
| Email | regex `^[^@\s]+@[^@\s]+\.[^@\s]+$` | Stricter validators (RFC 5322) are usually overkill |
| US ZIP | regex `^\d{5}(-\d{4})?$` | preserve as string |
| US phone | digits-only length 10, or E.164 `+1\d{10}` | |

Decision policy per outlier: **correct** (if you can verify), **cap** (winsorize to the plausible bound), **remove** (route to the reject file), or **keep with flag** (an `outlier_method` column). Pick one per column, document it.

## 6. Standardization and normalization

Different sources will have spelled the same value many ways. Unify at parser time so downstream joins work.

- **Casing.** `str.lower()` / `str.upper()` / `str.title()` consistently. The pattern that breaks: `"BOB"` vs `"Bob"` vs `"bob"` are three rows after a naive `groupby`.
- **Whitespace.** `str.strip()` removes leading/trailing whitespace; `str.replace(r'\s+', ' ', regex=True)` collapses runs.
- **Unicode normalization.** `unicodedata.normalize('NFKC', s)` — converts ligatures, full-width characters, decomposed accents to a canonical form. Critical for any source that mixes ASCII and accented characters.
- **Encoding.** Detect with `chardet` if uncertain; convert to UTF-8 at read time. Document the source's actual encoding in `provenance.csv`.
- **Date formats.** Convert everything to ISO-8601 (`YYYY-MM-DD`). `pd.to_datetime(..., format='...', errors='coerce')` with the source's format declared explicitly. Never let pandas auto-detect on mixed-locale data — it will guess wrong on `01/02/2024`.
- **Phone numbers.** Normalize to E.164 (`+1\d{10}` for US). The [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers) library handles parsing across countries.
- **Addresses.** USPS-standardized form for US addresses ([`usaddress`](https://github.com/datamade/usaddress) for parsing; [`scourgify`](https://github.com/EdgewiseSolutions/scourgify) for normalization). For non-US, `libpostal` is the more general option.
- **Categorical canonicalization.** A `data/lookups/normalize_<column>.yaml` mapping raw values to canonical ones — `{"Mr.": "Mr", "Mister": "Mr", "MR": "Mr"}` — applied at parse time. This is a one-way crosswalk; see the *concept catalog* in [`data-modeling.md#concept-catalogs`](data-modeling.md#concept-catalogs) for the multi-way cross-source case.
- **Regex / string transforms.** Name common patterns as functions (strip trailing `.` from initials; collapse `St.` and `Street`; extract a leading numeric ID from `"R21-007: Description..."`) and share them between parsers once a second parser needs them.

## 7. Validation and the reject file

`clean.py` validates the deduplicated frame against the pandera contract in `scripts/schema.py` with `split_valid`: rows that fail a row-level check (a null key, a value outside its declared range, a type that won't coerce) go to `data/audit/rejected.csv` with their original values, the artifact they came from and a `reject_reason`; valid rows go on. A failure not tied to specific rows (a missing or unexpected column) fails the whole artifact, which is recorded in the error log. The reject file is rewritten every run, is gitignored (it can hold personal data), and its count by reason appears in the audit summary, which is committed.

```python
# scripts/schema.py — the contract carries the row-level rules
class CanonicalLong(pa.DataFrameModel):
    precinct: Series[str]
    votes: Series[pd.Int64Dtype] = pa.Field(ge=0, nullable=True)
    ...

    class Config:
        strict = True
        coerce = True
        unique = KEY_COLUMNS
```

Beyond per-row checks:

- **Cross-field rules** (`start_date < end_date`, `total = sum of parts`) are pandera dataframe-level checks (`@pa.dataframe_check`) in `schema.py`, so they report the failing rows and route them to the reject file like any other check.
- **Referential integrity:** values in a column must appear in a lookup table (every `precinct` in `data/lookups/precincts.csv`). Mismatches are usually new entities or typos and deserve review.
- **Controlled vocabularies:** a `data/lookups/vocab_<column>.csv` per categorical column, which `tests/test_lookups.py` checks against the dictionary and the data.
- **Business rules** a stakeholder names live in the same schema module, so the full rule set is inspectable in one place.

A jump in rejected rows between runs (from 22 to 4,200) means the parser broke or the source changed; the refresh PR's summary diff shows it.

## 8. PII redaction

A liberation project is publishing data; whatever PII was in the original *and is not load-bearing for the public-interest analysis* should be redacted from `data/processed/` outputs. The original retains the source's content; the processed outputs obey the project's policy.

Redaction is the *mechanical* step; the *decision* it implements lives one level up. Whether a dataset should be published at all under privacy law (GDPR Art. 17, CCPA) or the CARE principles is a governance gate — one of the few places in this skill that can mean *do not publish, or publish differently* — covered in [`_shared/values-and-gates.md`](_shared/values-and-gates.md) and [`_shared/governance.md`](_shared/governance.md). Apply the gate first; redaction carries out its verdict, it doesn't substitute for it.

Common PII patterns and a regex starter set (use as a baseline; combine with a real library for production):

| PII type | Regex (Python) | Replacement strategy |
|---|---|---|
| Email | `r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'` | `<EMAIL>` or a faker-generated token |
| US phone | `r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'` | `<PHONE>` |
| SSN | `r'\b\d{3}-\d{2}-\d{4}\b'` | `<SSN>` — and confirm the source legally should have shared this in the first place |
| Credit card | `r'\b(?:\d[ -]*?){13,19}\b'` | `<CC>`, then verify with a Luhn check before redacting (avoid false positives on long ID numbers) |
| IPv4 | `r'\b(?:\d{1,3}\.){3}\d{1,3}\b'` | `<IP>` |
| Date of birth | varies; flag any column the dictionary marks as DOB | hash, generalize to year-only, or drop |

Tools that are sturdier than rolling regex from scratch:

- [`presidio`](https://github.com/microsoft/presidio) — Microsoft's PII detection and anonymization library; ships analyzers for ~50 entity types and supports redaction, hashing, replacement, encryption.
- [`scrubadub`](https://github.com/LeapBeyond/scrubadub) — focused on email/URL/phone/SSN with a clean API.
- [`faker`](https://github.com/joke2k/faker) — produces realistic replacement values when full nulling would break downstream use.

The decision matrix:

| Use case | Redaction |
|---|---|
| Identifier never needed downstream | Drop the column entirely |
| Identifier needed for joins but not display | Hash with a project-secret salt; document the hash function in the dictionary |
| Identifier needed for display but not full precision | Generalize (ZIP → ZIP3; DOB → birth year; address → census tract) |
| Identifier load-bearing for accountability (elected officials' official acts, public-record case parties) | Keep, with the legal basis documented in the dictionary |

**Never** redact PII in `data/original/`. The hash manifest assumes those files are byte-identical to what the publisher published. Redaction is a publish-time transform.

## 9. The row ledger and the conservation check

`clean.py` keeps a ledger for every run: rows parsed, duplicates dropped, rows rejected, rows written. It must balance (`parsed = duplicates_dropped + rejected + written`) or the build fails with exit code 3; `audit.py` then checks that the processed CSV holds exactly the rows `clean` reported writing. The ledger goes to `data/audit/run.json` (with the run's start and end times, ignored by git) and into the committed summary and `headline.json`. Per-artifact counts (`rows_parsed`, `rows_out`, `rows_rejected`) are in `provenance.csv`, so an artifact that suddenly yields a fraction of its usual rows stands out.

Where a transformation inside a parser drops or merges rows on purpose (dropping footnote rows, merging continuation lines), count what it removed and say so in the parser's `NOTES` or the dictionary's caveats, so the gap between the source's row count and `rows_parsed` is explained. Where meaningful, conserve a key amount as well as the row count: a total that changes between stages is as loud a signal as a missing row.

## Where this lives in the project

| Operation | Lives in |
| --- | --- |
| Per-era parser logic (steps 1–6, 8) | `scripts/parsers/<source>_<era>.py` |
| Routing artifacts to parsers | `scripts/source.py` (`parser_for`) |
| Dedup, validation, reject file, ledger, writing | `scripts/clean.py` with `scripts/schema.py` |
| The schema contract and row-level rules | `scripts/schema.py` (see [`data-modeling.md`](data-modeling.md#validation)) |
| Lookup tables (vocabularies, crosswalks, entity seeds) | `data/lookups/` |
| Reject file | `data/audit/rejected.csv` (per run, ignored) |
| Error logs | `data/audit/extraction_errors.json`, `data/audit/fetch_errors.json` (per run, ignored) |
| Ledger and run times | `data/audit/run.json` (per run, ignored); counts in `summary.md` (committed) |

When two parsers need the same helper (strip trailing periods from initials, collapse `St.` and `Street`), lift it into a shared module under `scripts/parsers/` then, not before.

---

# Part 3: Audit, reconciliation, and refresh

## Audit: what came in

Audit answers "does what we just produced look right?" and runs after every `clean`. It writes `data/audit/summary.md`, a stable file name with no timestamp inside, so it can be committed and each refresh PR shows exactly what changed. A maintainer should be able to scan it in thirty seconds.

| Section | What it tells you |
| --- | --- |
| **Headline** | Rows, columns, sources, vintages and their range, duplicates and rejects: the same block that is generated into the README and AGENTS. |
| **Row ledger** | Parsed, duplicates dropped, rejected, written. |
| **Rows per source and vintage** | Every expected source and vintage should be non-zero. |
| **Artifacts that produced no rows** | An artifact with zero rows out is almost always a regression. |
| **Extraction methods** | Counts of `extraction_method` × `extraction_quality`, so degraded extractions are visible. |
| **Null rate per column** | A column that is suddenly all null usually means a layout change broke a parser. |
| **Small vocabularies** | Distinct values of columns with at most 30 of them: did a controlled vocabulary gain or lose a value? |
| **Errors this run** | Every fetch and extraction error from this run's fresh logs, with the count in the heading. |
| **Rejected rows** | Count by reason. |
| **Spot-check sample** | Ten rows chosen by hashing the natural key, to check by eye against their originals. |

The spot-check sample is drawn on a **stable key**: rows are ranked by a hash of their natural-key values, not by row number or a seeded shuffle of row order, so the sample survives the publisher re-sorting or renumbering its records (one project's seeded sample changed when an agency renumbered its record IDs) and new rows rarely displace old ones. Never key a sample, or a dedup, on an upstream row number or object ID.

`audit` also writes `docs/variables.{md,csv}`, the mechanical column profile (dtype, distinct count, null rate, sample values) beside the hand-kept dictionary; if the profile says `object` and the dictionary says `Int64`, one of them is wrong, usually the parser. And it writes `data/audit/headline.json` and refreshes the generated blocks in README and AGENTS; a test fails when those blocks are stale (see [`project-template.md`](project-template.md#generated-numbers-in-docs)).

## The error log

Each run's errors start from an empty log: `fetch` and `clean` delete the previous `fetch_errors.json` and `extraction_errors.json` before writing new ones. A log that appends across runs lets old failures mask new ones and grows until nobody reads it. Each record names the stage, source, vintage, artifact, URL, error type and message (plus a traceback); the summary lists them all, and `clean --strict` (for CI) exits non-zero when there are any. A parser failure on one artifact never blocks the others: that is "durable, not fatal". An empty or degenerate extraction is a failure like any other, not a silent gap.

## Reconciliation

When the source prints totals (statements of vote, financial statements, statistical tables), recompute them from the processed rows and compare. A mismatch is a regression: the run completes, so data isn't lost, but `reconcile` exits 2 and the refresh PR shows the mismatch in `data/audit/reconcile.md`.

[BoulderPublicData/Election-Results' `reconcile.py`](https://github.com/BoulderPublicData/Election-Results) is the model: 149 of 150 cross-checks match exactly, and the one mismatch is documented with its upstream cause (the source PDF had an arithmetic error in one precinct subtotal). Every mismatch accounted for, not zero mismatches, is what safe scrutiny looks like.

**Reconcile at the finest grain both sides share.** Compare per office, per precinct, per page or per line item, not only the grand total. Grand totals often cover different scopes (a different date window, a different list of entities, inclusion rules), so a large top-line gap can be correct and a top-line match can hide offsetting errors. One project spent days chasing a large grand-total gap that turned out to be a documented scope difference, while the per-entity totals matched to the cent. Compare the keys both sides have; report keys present on only one side as a documented scope difference, not a mismatch. `compare_totals` in `scripts/reconcile.py` does exactly this:

```python
# scripts/reconcile.py
def reconcile_example() -> ReconcileResult:
    df = pd.read_csv(PROCESSED_CSV, dtype={"votes": "Int64"})
    checks = []
    for pdf in sorted((DATA_ORIGINAL / "example_source").rglob("*.pdf")):
        vintage = pdf.parent.name
        printed = read_printed_contest_totals(pdf)  # independent of the parser's path
        recomputed = df.query("vintage == @vintage").groupby("contest")["votes"].sum().to_dict()
        checks += compare_totals(printed, recomputed, prefix=f"{vintage}:", tolerance=0)
    return ReconcileResult("example_source", checks)


RECONCILERS = {"example_source": reconcile_example}
```

Turn reconciliation on whenever the source prints totals and the data will be cited or is contested. Skip it only when there is no independent total to compare against, and say so in the dictionary. Document what the reconcile checks (which totals, at which grain, against which originals) and every known mismatch with its explanation in the dictionary's caveats, so a future maintainer knows which numbers are authoritative.

## The recurring-refresh pattern

For sources that publish on a cadence, the refresh group's `.github/workflows/refresh.yml.disabled` (renamed to enable) runs `pipeline run` on a schedule and opens a pull request when anything changed. Four decisions matter:

**Cadence: slightly trail the publisher.** Running more often than the publisher updates wastes compute and fills the history with noise; `workflow_dispatch` covers the impatient case. Pick a minute other than `:00`, when GitHub's scheduler is busiest.

| Publisher cadence | Cron |
| --- | --- |
| Annual (after certification) | `"17 13 1 11 *"`: November 1, 13:17 UTC |
| Monthly | `"17 13 1 * *"`: the first of each month |
| Weekly | `"17 13 * * 1"`: Mondays |
| On demand | omit `schedule:`; keep `workflow_dispatch:` |

**Pull request, not a commit to main.** An automatic commit silently changes published data. A PR forces a human pass over the signals in its diff: the row change in `summary.md`, new errors and rejected rows, a changed sha256 in `manifest.json`, a new reconcile mismatch, the spot-check sample. Some mature pipelines with strong reconcile coverage relax this to commit-to-main with audit-driven rollback; the PR is the safer default.

**Commit what reviewers need, and only that.** The PR stages `data/original/**` (under the storage budget), `data/processed/*.csv`, `data/audit/*.md`, `data/audit/headline.json`, `docs/variables.*`, and the regenerated README and AGENTS blocks; `.gitignore` agrees, so nothing staged is ignored and nothing reviewed is missing. Anything outside that list means the workflow misbehaved.

**Fail instead of shipping bad data.** If a stage fails (no rows survive, rows are lost between stages, a fetch fails), the job fails and no PR opens; the failed-run notification is the signal. For ephemeral sources, see [Ephemeral sources](#ephemeral-sources).

## Common failure modes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Discovery finds zero artifacts | The index page was redesigned and the selector no longer matches | Update the selector; keep the saved index page as a test fixture so the next redesign fails a test |
| A vintage is labeled a year late | The vintage was read from the publish path | Read it from the file name or content; add a test for that case |
| An artifact suddenly yields far fewer rows, or none | The parser broke on a layout change, or the file is truncated | Compare the newest original's layout with the previous era's; check `rows_out` in `provenance.csv` and the error log |
| A column's null rate jumps to 1.0 | A layout change broke one field | As above; add a fixture from the new layout |
| Old errors keep appearing | The error log appends across runs | Start each run's log empty, as the template does |
| A stale original survives a refresh | The file existed, so fetch skipped it | `fetch --fresh`; the manifest records the old and new hashes |
| Reconcile passed for years and now fails on one check | A regression in a new parser, or an arithmetic error in the source | Recompute that total by hand from the original. If the source is wrong, document it in the dictionary's caveats and adjust the expected value with a note |
| The grand total is far off but every per-entity total matches | The two files cover different scopes | Reconcile at the shared grain; document the scope difference |
| The cron runs daily for an annual publisher | Cadence mismatch | Move the cron; use `workflow_dispatch` for impatient refreshes |
| A refresh PR sits unreviewed for months | Nobody is accountable for it | Name the reviewer in AGENTS.md and set up notifications (and `CODEOWNERS` with branch protection when there is a team) |

## What to write in AGENTS.md

- **Refresh cadence:** the cron expression, if refresh is enabled, and which part of the publication cycle it trails.
- **Discovery surface:** what `artifacts()` checks (URL pattern, index page, year range); the first place to look after a publisher redesign.
- **Storage budget:** where each source's originals live.
- **Reconcile scope:** which totals are checked at which grain against which originals, with a pointer to the known mismatches in the dictionary.
- **Audit invariants** the summary can't express on its own, such as "source X is non-empty for every vintage from 2010" or "the null rate of `precinct` stays at or below 0.01".

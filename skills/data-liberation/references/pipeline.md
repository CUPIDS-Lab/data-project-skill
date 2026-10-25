# Pipeline: cleaning, discovery, audit, and reconciliation

This reference covers the processing-and-verification layer of a liberation pipeline: the parser-time cleaning pipeline (the Level 2 "how to process" — what to do during a parser to make a row conform to the canonical schema without losing the trail of what changed) plus discovery, audit, and reconciliation (how to verify that what came in matches the truth). Cleaning work happens between fetching the immutable original and writing the validated CSV — i.e. inside `scripts/parsers/<source>_<vintage>.py` and `scripts/clean.py`; the three "watchful" steps then find what's available upstream (`discover.py`), report on what came in (`audit.py`), and verify the output against authoritative top-line totals (`reconcile.py`). What to *produce* — tidy shape, the canonical schema, the data dictionary, concepts, and the quality dimensions — lives in [`data-modeling.md`](data-modeling.md). The discovery/audit patterns here are distilled from BoulderPublicData/Election-Results (where `reconcile.py` originated), the IPEDS pipeline (which formalized the `discover.py` self-refresh), and ProPublica's [data-bulletproofing guide](https://github.com/propublica/guides/blob/master/data-bulletproofing.md).

The skill commits to seven principles:

- **Originals are immutable.** Never write back to `data/original/`. Every cleaning operation reads from there and writes to `data/processed/` (or `data/audit/`).
- **Profile before you parse.** Inspect dtypes, distinct counts, null patterns, distributions *before* writing any coercion code.
- **Errors are durable, not fatal.** Malformed rows go to a *reject port* (`data/audit/rejected.csv`) with a reason; the rest of the pipeline keeps running.
- **Coerce explicitly.** Pandas's silent dtype inference is the source of most leading-zero bugs. Declare types at the boundary.
- **Document every transform.** A cleaning log (`data/audit/cleaning-log-<ts>.json`) records before/after counts per operation. Reproducibility is the property that distinguishes liberation from cleaning-by-spreadsheet.
- **Imputation is opt-in.** The default civic-data stance is to preserve missingness (NA) and document it, not to fill it. Imputation lives behind an explicit decision logged in `AGENTS.md`.
- **Redact PII at the boundary of `data/processed/`.** The originals retain whatever the publisher published; the processed CSV obeys the project's redaction policy.

# Part 1 — Cleaning and standardization

## The cleaning pipeline

Every parser does three things — *extract from a source*, *transform what's there*, *publish to a sink* — and the 9 steps below group cleanly into those three roles. Naming the role a step plays sharpens diagnosis: a *source-extraction* failure (encoding wrong, sentinel missed, dtype mis-inferred) calls for fixes in the parser's `read_*` calls; a *transformation* failure (consistency, dedup logic, missingness handling) belongs in the middle of the parser; a *sink-publication* failure (PII leaked, format unified inconsistently, output didn't match the schema contract) belongs at the end or in `publish.py`.

| Step | Role | Goal | Output |
|---|---|---|---|
| 1. Initial assessment | Source-extraction | Know what you have | Profile report; structural-issues note |
| 2. Structural fixes | Source-extraction | Make the shape canonical | Standardized column names, dtypes, no fully-empty rows/cols |
| 3. Deduplication | Transformation | Remove redundant rows | Deduplicated frame + dropped-rows log |
| 4. Missing-value treatment | Transformation | Decide per-mechanism, document | Frame with NA preserved or imputed with rationale |
| 5. Outlier detection | Transformation | Catch the impossible and the suspicious | Outlier flag column (`outlier_method`, `outlier_reason`) |
| 6. Standardization / normalization | Transformation | Make values uniform | Casing, encoding, formats unified |
| 7. Validation + reject port | Transformation | Gate the canonical output against the [schema contract](data-modeling.md#the-canonical-schema) | Valid rows → `data/processed/`; invalid → `data/audit/rejected.csv` |
| 8. PII redaction | Sink-publication | Apply policy at the publish boundary | Redacted columns in `data/processed/` only |
| 9. Documentation | Sink-publication | Log what changed | `data/audit/cleaning-log-<ts>.json` |

Run them in order — earlier steps surface issues that change how later steps behave. Skipping forward means redoing later. The rest of this part unpacks each step with concrete tools and the integration point in this skill's project layout.

## 1. Initial assessment — profile before you parse

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
- **Dtype casting** with `pandas.to_numeric(..., errors='coerce')`, `pandas.to_datetime(..., errors='coerce')`, and explicit `dtype="string"` for ID-like columns. The `errors='coerce'` flag turns un-parseable values into `NaT`/`NaN` instead of raising — combined with the reject port (step 7), this is how the pipeline routes parser failures without crashing.
- **Split or merge columns** as the schema requires — e.g. an "Address" column → `street`, `city`, `state`, `zip`; or a `first_name` + `last_name` → `full_name`. Document either direction in the data dictionary.
- **Drop fully empty rows and columns:** `df.dropna(how='all')` for rows; `df.dropna(axis=1, how='all')` for columns. Fully empty *and not previously documented* is a structural artifact (Excel padding, export bug), not data.

## 3. Deduplication

Two kinds of duplicates, two different operations:

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

The default is **preserve NA** and document the mechanism. Imputation is opt-in and requires an explicit AGENTS.md decision.

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

Decision policy per outlier: **correct** (if you can verify), **cap** (winsorize to the plausible bound), **remove** (route to reject port), or **keep with flag** (an `outlier_method` column). Pick one per column, document it.

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
- **Regex / string transforms.** Lift common patterns into named functions in `scripts/parsers/_normalize.py` and import them per-parser. Examples: strip trailing `.` from name initials; collapse `St.` and `Street`; extract a leading numeric ID from `"R21-007: Description..."`.

## 7. Validation and the reject port

The **reject port** pattern: any row that fails a parser's validation rules goes to `data/audit/rejected.csv` with a `reject_reason` column and the original row content preserved. The pipeline keeps running. The reject port is a first-class audit artifact, not a debug file.

```python
def parse(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str)
    raw['_row_num'] = raw.index

    # apply structural fixes, normalization...

    valid_mask = (
        raw['age'].astype(float).between(0, 120) &
        raw['email'].str.match(EMAIL_RE) &
        raw['zip'].str.match(ZIP_RE)
    )
    rejected = raw.loc[~valid_mask].assign(
        reject_reason=lambda d: _reason_for_each(d),
        source_file=path.name,
    )
    rejected.to_csv(REJECT_PORT, mode='a', header=not REJECT_PORT.exists(), index=False)

    return raw.loc[valid_mask].drop(columns=['_row_num'])
```

Beyond per-record validation:

- **Schema validation** via `pandera` at the boundary of `clean.py` (covered in [`data-modeling.md#validation`](data-modeling.md#validation)).
- **Cross-field validation** — `start_date < end_date`; `diastolic_bp < systolic_bp`; `child_age < parent_age`; `total = sum_of_parts`. These are pandera `Check` callables, or explicit assertions in `clean.py` that route violations to the reject port.
- **Referential integrity** — values in a column must appear in a lookup table. E.g. every `precinct` in the data must appear in `data/lookups/precincts.csv`. Mismatches are usually new precincts (or typos) and warrant a review.
- **Business rules** — domain-specific assertions a stakeholder names. Capture them in a `scripts/validators.py` registry so the rule set is inspectable in one place.

## 8. PII redaction

A liberation project is publishing data; whatever PII was in the original *and is not load-bearing for the public-interest analysis* should be redacted from `data/processed/` outputs. The original retains the source's content; the processed outputs obey the project's policy.

Redaction is the *mechanical* step; the *decision* it implements lives one level up. Whether a dataset should be published at all under privacy law (GDPR Art. 17, CCPA) or the CARE principles is a governance gate — one of the few places in this skill that can mean *do not publish, or publish differently* — covered in [`project-template.md`](project-template.md#governance) and framed in [`context.md`](context.md). Apply the gate first; redaction carries out its verdict, it doesn't substitute for it.

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
| Identifier load-bearing for accountability (elected officials' salaries, public-record case parties) | Keep, with the legal basis documented in the dictionary |

**Never** redact PII in `data/original/`. The hash manifest assumes those files are byte-identical to what the publisher published. Redaction is a publish-time transform.

## 9. Documentation

Every cleaning run writes one structured log: `data/audit/cleaning-log-<ts>.json`. Minimum content:

```json
{
  "run_ts": "2026-05-25T18:00:00Z",
  "source": "boulder_county_sov",
  "vintage": "2024-general",
  "parser": "boulder_sov_2024.py@a1b2c3d",
  "rows_in": 14823,
  "rows_out": 14801,
  "rows_rejected": 22,
  "transforms": [
    {"step": "snake_case_columns", "columns_renamed": 17},
    {"step": "sentinel_to_na", "column": "votes", "values_replaced": 142},
    {"step": "drop_exact_duplicates", "keys": ["precinct", "contest", "candidate"], "dropped": 8},
    {"step": "outlier_flag", "column": "votes", "method": "IQR", "flagged": 3},
    {"step": "pii_redact", "column": "voter_email", "strategy": "drop_column"}
  ],
  "reject_port": "data/audit/rejected.csv"
}
```

This log is what reviewers read on the refresh PR. The per-vintage diff between two runs surfaces silent drift — e.g., a sudden jump from 22 rejected rows to 4,200 means the parser broke or the source changed.

## Where this lives in the project

| Operation | Lives in |
|---|---|
| Per-source parser logic (steps 1–7) | `scripts/parsers/<source>_<vintage>.py` |
| Shared normalization helpers | `scripts/parsers/_normalize.py` |
| Cross-source orchestration | `scripts/clean.py` |
| Validators (cross-field rules, business rules) | `scripts/validators.py` |
| PII redaction policy (per column) | `scripts/publish.py` (applied to the published artifact only) |
| Lookup tables (categorical canonicalizations, FK targets) | `data/lookups/` |
| Reject-port output | `data/audit/rejected.csv` |
| Per-run cleaning log | `data/audit/cleaning-log-<ts>.json` |
| Schema enforcement (pandera) at the boundary | `scripts/schema.py` (see [`data-modeling.md#validation`](data-modeling.md#validation)) |

The cleaning pipeline runs once per vintage at parser time. The reject port and cleaning log are first-class audit artifacts, reviewed on every refresh PR. Drift in any of the per-transform counts is usually the earliest signal that the upstream source changed.

# Part 2 — Discovery, audit, and reconciliation

The "watchful" steps. Where Part 1 describes *what to do* during a parser, Part 2 describes *what's wrong* and how to catch it — together, they make a pipeline *trustworthy* rather than just *runnable*.

## Pre-extraction bulletproofing

Before writing a single parser, vet the source itself. ProPublica's data-bulletproofing guide distills this practice; the checklist below adapts it for the liberation workflow. Most of these are five-minute checks; skipping them buys hours of debugging later.

Each check below corresponds to a specific [data-quality dimension](data-modeling.md#data-quality) — naming the dimension makes the check defensible to engineers, and using the engineer's framework keeps the journalist honest about what's being measured. The five quality dimensions themselves are defined canonically in [`data-modeling.md#data-quality`](data-modeling.md#data-quality); the table below maps each check to one of them rather than re-defining them here:

| Check | Dimension it serves |
|---|---|
| Record count verification (watch for the 65,536-row Excel ceiling, powers of two) | Completeness |
| Top-line totals match the publisher's claim | Accuracy |
| Date and geography range checks | Timeliness; Relevance |
| `GROUP BY` every categorical field to surface spelling drift | Consistency |
| Find the publisher's codebook / methodology / statute | Usability (Documentation, Metadata) |
| Identify the records officer / contact | Usability (Credibility) |
| Discriminate blanks from sentinel values (`-9`, `9999`, `1900-01-01`) | Completeness (with the three-way *exists-but-unknown* / *does-not-exist* / *unknown-whether-exists* distinction in the data dictionary) |
| Demand questionnaires for survey-derived data | Usability (Credibility) |
| Cross-source corroboration | Consistency |
| Random-sample physical spot-check | Auditability |

The documentation-and-contact checks are *state reconstruction* — the under-rotated, highest-leverage phase that happens before any measurement code is written. See [`data-modeling.md#pipeline-shape`](data-modeling.md#pipeline-shape).

This checklist parallels the quality, provenance, and metadata best practices in the W3C **Data on the Web Best Practices** — DWBP is a useful published yardstick to skim once if you want an external "did we miss anything?" list, but the journalistic checklist here is the operational form. See [`context.md`](context.md#a-meta-synthesis-four-lenses-on-open-data) for the framing; it's background, not an added gate.

### Source-level checks

- **Record count.** Confirm the total matches what the publisher claims (or what an independent count says it should be). Watch for *suspicious round limits* — 65,536 rows in an Excel export, 1,048,576 rows, exactly 10,000 rows, powers of two — they often mean the export was truncated upstream.
- **Top-line totals.** If the source publishes a "Total" line, sum the rows and compare. A mismatch here is either an arithmetic error in the source (document it explicitly in `docs/data-dictionary.md` under "Known mismatches" — see [reconciliation](#reconciliation)) or evidence the export is incomplete.
- **Date and geography ranges.** Does the data actually cover the years and jurisdictions the publisher claims? A "1980–present" dataset that has zero records before 1995 needs explaining.
- **Categorical field consistency.** `GROUP BY` every important categorical column and read the result. Spelling variations (`"Main St"` vs `"Main Street"` vs `"MAIN ST."`), trailing whitespace, and case differences are how dirty data hides.
- **Blank values.** Determine whether blanks are *real values* (the publisher genuinely didn't measure this) or *import errors* (the column dropped during export). The two cases require different treatment in the parser.
- **Suspicious sentinel values.** `-9`, `9999`, `99999999`, `-1`, `1900-01-01`, the empty string — government datasets use ALL of these for "missing." Document the ones this source uses and convert them to NA in the parser, not silently in the pipeline. See [4. Missing-value treatment](#4-missing-value-treatment) above for the Rubin MCAR/MAR/MNAR framework and treatment choices.
- **Format-native error markers are quality signals, not noise.** When the source format encodes its own failure states — `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?` in spreadsheets; `null` in JSON columns the schema says are required; `<missing>` placeholders in HTML tables — those errors *originated with the publisher*, not the parser, and they're worth surfacing as audit findings rather than silently coerced to NA. The principle generalizes past spreadsheets: any format-native "this value is broken" marker is a publisher-side data-quality issue worth a row in `data/audit/source_errors.csv` so the count can be trended over time. Silently converting them to NA loses the signal that the *source* has a problem.

### Methodology and provenance checks

- **Find the original documentation.** The publisher's codebook, methodology PDF, statute or regulation mandating the publication. Read it before parsing. If you can't find one, that's a finding worth recording in `AGENTS.md` "Known limitations."
- **Identify the contact.** Records officer, FOIA liaison, the journalist who last covered this beat, the academic who maintains a derivative dataset. Make the introduction early; you'll need them when something is weird.
- **Demand questionnaires/methodologies for survey-derived data.** Refusal to share methodology is a red flag worth naming. Identify non-scientific methods (web-based panels, self-selection) and bake that caveat into the dictionary.
- **Cross-source corroboration.** Find an independent source for the same underlying phenomenon — a federal mirror of state data, an aggregator (Census, BLS), a watchdog dataset that audits the original. Two sources that match build confidence; two that diverge surface a story.

### When the source path is a records request (FOIA / sunshine laws)

If the data has to be *requested* rather than downloaded, the request itself is part of the Survey. A few process notes that change what you get back:

- **Ask for data, not narrative.** Request the underlying records in their native machine-readable format ("the database export / the spreadsheet behind this report," not "a report about X"). Agencies often default to printing-to-PDF; naming the format you want up front avoids a re-request.
- **Know the clock and the fee tiers.** Federal FOIA runs ~20 business days (often longer); fee categories differ for commercial vs. news-media/educational vs. other requesters, and waivers exist for public-interest requests. State **sunshine / open-records laws** vary — the records officer is the contact, and `FOIA.gov` routes federal requests.
- **Treat redactions as findings, not just obstacles.** A heavily-redacted or truncated release can still carry usable tables; record what was withheld and the claimed exemption in `AGENTS.md` "Known limitations." An *excessive* redaction is itself a transparency story worth naming, not silently absorbing.
- **Decide what the project will not liberate.** "Available to extract" is not the same as "responsible to publish." Where a release contains personal data that privacy law protects, or where the downstream use is one the project considers out of scope, that judgment belongs in the Survey, not after publication — see the governance section of [`project-template.md`](project-template.md#governance). The wider transparency-law and records-request landscape is catalogued in [`context.md`](context.md).

### Cognitive checks worth naming

- *"If something doesn't seem right, it probably isn't."* The 50% year-over-year jump that doesn't appear in the press? Almost always an extraction bug, not a real spike.
- *"Avoid false precision."* Reporting "52.18%" when the underlying counts have ±30 of margin invents accuracy. The data dictionary should declare which columns have meaningful precision and which round to integers.
- *"Set a cutoff date."* Organic datasets that grow during your reporting will rewrite history under you. Pick a freeze date, document it, and don't reach past it except for explicit corrections.
- *"Spot-check physically."* For a small sample (say, 10 records), open the original source artifact and verify each cell of the processed CSV by eye. This catches column-shift bugs that no automated check finds.

### A practitioner's prep list

The colleagues quoted in ProPublica's guide each contributed one durable practice; the union is the working baseline:

- **Maintain a work log.** A `docs/notebook.md` recording each cleaning decision, why, and when. The IPEDS pipeline's `AGENTS.md` is the maximalist version; a chronological log is the minimum.
- **Document SQL.** Every non-trivial query in the audit or reconcile modules gets a comment explaining why this aggregation/filter, not just what it does.
- **Write the alternate query.** For top-line numbers that will be published, derive the same value via a different code path. Two queries that agree raise confidence by more than two queries that look similar.
- **Random-sample validation.** Pull 50 rows at random from the processed CSV; verify each against the original. Repeat after every significant parser change.
- **Pre-publication review.** Show findings to the subject before publishing them. Errors caught at this stage are corrections; errors caught after are retractions.

### How this fits the workflow

| Workflow phase | Bulletproofing checks that belong here |
|---|---|
| **Survey** | Source-level checks against publisher's own summary; methodology/provenance fact-finding; identifying the contact |
| **Extract** | Sentinel-value handling in parsers; categorical consistency; physical spot-checks of the first parser's output |
| **Tidy** | Date and geography range verification post-normalization; cross-source corroboration setup |
| **Audit** | `audit.py` automates the easy checks (null rates, distinct values, suspicious counts); see [Audit](#audit-what-came-in) below |
| **Reconcile** | Top-line totals against the source's own published total; see [Reconciliation](#reconciliation) below |

The Survey-phase checks are the cheapest and the most under-done. Lean into them.

## Discovery

**Discovery's job:** answer the question "is there a vintage we don't have yet?" without downloading anything. A correctly-implemented `discover()` is cheap, idempotent, and a precondition for any recurring-refresh workflow.

Two patterns, depending on how the upstream publishes.

### Static-list discovery

For sources where new vintages appear at predictable URLs — say, an agency that publishes `https://example.gov/annual-report/2024.pdf`, `…/2025.pdf` annually — the `discover()` implementation is a static URL pattern plus a year range:

```python
# scripts/sources.py (excerpt)
from datetime import datetime
from scripts.sources import Source, Artifact


class AgencyAnnualReport(Source):
    name = "agency_annual"
    label = "Example Agency Annual Report"
    URL_PATTERN = "https://example.gov/annual-report/{year}.pdf"

    def discover(self):
        current = datetime.now().year
        for year in range(2010, current + 1):
            yield Artifact(
                source=self.name,
                vintage=str(year),
                url=self.URL_PATTERN.format(year=year),
                local_path=Path(f"data/original/{self.name}/{year}/report.pdf"),
                metadata={"year": year},
            )
```

The corresponding `fetch.py` is responsible for HEAD-checking each artifact (so a year that hasn't been published yet doesn't get downloaded). Discovery is the catalog; fetch is the gate.

### Index-page discovery

For publishers with an index page that lists what's available — most agencies' "Reports" landing pages, most secretary of state election archives — `discover()` scrapes the index and yields one artifact per linked PDF/XLSX/CSV:

```python
import httpx
from selectolax.parser import HTMLParser


class BoulderCountySoV(Source):
    name = "boulder_county_sov"
    label = "Boulder County Statement of Vote"
    INDEX_URL = "https://bouldercounty.gov/elections/historical-results/"

    def discover(self):
        with httpx.Client() as client:
            html = client.get(self.INDEX_URL).text
        tree = HTMLParser(html)
        for link in tree.css("a[href$='.pdf']"):
            href = link.attributes.get("href", "")
            text = link.text(strip=True)
            vintage = self._parse_vintage(text)
            if vintage is None:
                continue
            yield Artifact(
                source=self.name,
                vintage=vintage,
                url=href,
                local_path=Path(f"data/original/{self.name}/{vintage}/sov.pdf"),
                metadata={"link_text": text},
            )

    @staticmethod
    def _parse_vintage(link_text: str) -> str | None:
        """Extract `2009` from `'2009 General Election - Statement of Vote (PDF)'`."""
        import re
        m = re.search(r"\b(20\d{2})\b", link_text)
        return m.group(1) if m else None
```

This is what makes the pipeline self-updating: a cron run of `discover → fetch → clean → audit` automatically picks up a new vintage when the publisher posts it. The recurring-refresh pattern below depends on this.

### Standalone discovery script

`scripts/discover.py` runs every source's `discover()` and prints what's available, optionally filtering to "what's not yet in `data/original/`":

```bash
$ uv run python -m scripts.pipeline discover
boulder_county_sov: 12 artifacts available, 11 already fetched, 1 NEW
  NEW  2024: https://bouldercounty.gov/.../2024-sov.pdf
co_secretary_of_state: 8 artifacts available, 8 already fetched
```

Output also written to `data/audit/discovery-<ts>.txt`. The diff between consecutive runs is a useful change signal: a new vintage appearing is the trigger to fetch.

## Audit: what came in

**Audit's job:** answer "does what we just produced look right?" Run after every `clean.py` pass. The artifact is `data/audit/summary-<ts>.md`, scannable in 30 seconds by a maintainer reviewing a refresh PR.

What goes in the audit (this is what `audit.py` writes to `data/audit/summary-<ts>.md`):

| Section | What it tells you |
|---|---|
| **Row count** | Total rows in the processed CSV. Headline number for refresh diffs. |
| **Source coverage** | Rows per `(source, vintage)`. Should match expectations: every registered source × vintage should be non-zero. |
| **Null rates per column** | Catches schema drift (a column suddenly all-null usually means a layout change broke a parser). |
| **Distinct values for low-cardinality columns** | Sanity check for categorical columns: did the controlled vocabulary just gain or lose a value? |
| **Empty sources / vintages** | Explicit flagged section. A registered source returning zero rows is almost always a regression. |
| **Extraction errors** | Summary of `data/audit/extraction_errors.json` — which artifacts failed to parse, with the exception type and the first line of the error. |

The Markdown format is deliberate. Auto-generated reports that nobody reads are wasted effort; Markdown renders inline in a GitHub PR diff and is what a human reviewer actually sees.

### A minimal audit implementation

```python
# scripts/audit.py
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import structlog

from scripts.config import DATA_AUDIT, PROCESSED_CSV

log = structlog.get_logger()


def audit_all() -> int:
    if not PROCESSED_CSV.exists():
        log.error("audit_no_processed_csv", path=str(PROCESSED_CSV))
        return 1

    df = pd.read_csv(PROCESSED_CSV, dtype=str)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = DATA_AUDIT / f"summary-{ts}.md"

    lines = [f"# Audit Summary — {ts}", "", f"Rows: **{len(df):,}**", ""]
    lines.extend(_section_source_coverage(df))
    lines.extend(_section_null_rates(df))
    lines.extend(_section_low_cardinality(df))
    lines.extend(_section_empty_sources(df))
    lines.extend(_section_extraction_errors())

    out.write_text("\n".join(lines))
    variables_report(PROCESSED_CSV)
    return 0


def _section_source_coverage(df):
    coverage = (
        df.groupby(["source", "vintage"], dropna=False)
        .size().rename("rows").reset_index()
        .sort_values(["source", "vintage"])
    )
    return ["## Source coverage", "", coverage.to_markdown(index=False), ""]
```

### `docs/variables.{md,csv}` — the long-form column report

The same `audit.py` (or a sibling function) emits the long-form per-column summary that complements the hand-maintained `docs/data-dictionary.md`:

```python
def variables_report(processed_csv: Path) -> None:
    df = pd.read_csv(processed_csv)
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append({
            "column": col,
            "dtype": str(s.dtype),
            "distinct": int(s.nunique(dropna=True)),
            "null_rate": float(s.isna().mean()),
            "min": s.min() if pd.api.types.is_numeric_dtype(s) else "",
            "max": s.max() if pd.api.types.is_numeric_dtype(s) else "",
            "sample_values": ", ".join(str(v) for v in s.dropna().unique()[:5]),
        })
    rep = pd.DataFrame(rows)
    rep.to_csv("docs/variables.csv", index=False)
    Path("docs/variables.md").write_text(
        "# Variables (auto-generated)\n\n" + rep.to_markdown(index=False)
    )
```

If `variables.csv` says a column is `object` and `docs/data-dictionary.md` says it's `Int64`, the dictionary is wrong or the parser is. Treat their agreement as a precondition — see `references/data-modeling.md` for the rationale.

### Recording extraction errors

`audit.py` also defines `record_extraction_error()`, called from `clean.py` when an individual artifact's parse fails. The pipeline doesn't stop — the failure appends to `data/audit/extraction_errors.json` and the next vintage proceeds:

```python
def record_extraction_error(*, source: str, artifact, error: Exception) -> None:
    EXTRACTION_ERRORS_JSON.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(EXTRACTION_ERRORS_JSON.read_text()) if EXTRACTION_ERRORS_JSON.exists() else []
    existing.append({
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "artifact_url": artifact.url,
        "artifact_vintage": artifact.vintage,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
    })
    EXTRACTION_ERRORS_JSON.write_text(json.dumps(existing, indent=2, default=str))
```

This is the "durable, not fatal" pattern: a parser failure on one vintage doesn't block the eleven other vintages from refreshing. The audit summary flags it next run; a human investigates on their own schedule.

## Reconciliation

For high-stakes pipelines (anything that will be cited publicly — election results, financial reports, agency budgets), re-open each original file independently and compute a small set of authoritative top-line totals, then compare to the processed output. Mismatches are regressions: the pipeline run completes (don't lose the data), but CI fails on the reconcile job and the audit flags it.

[BoulderPublicData/Election-Results' `reconcile.py`](https://github.com/BoulderPublicData/Election-Results) is the canonical example. It currently has 149 of 150 cross-checks matching exactly. The one mismatch is documented in `docs/data-dictionary.md` with the upstream-error explanation (a Statement of Vote PDF that itself contained an arithmetic error in one precinct subtotal). That kind of *known and documented* mismatch is what "safe scrutiny" looks like at a pipeline level — not zero mismatches, but every mismatch accounted for.

### The skeleton

```python
# scripts/reconcile.py
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd


@dataclass
class Check:
    label: str
    expected: int | float
    actual: int | float
    match: bool
    delta: int | float = 0
    notes: str = ""


@dataclass
class ReconcileResult:
    source: str
    checks: list[Check] = field(default_factory=list)


def reconcile_boulder_sov() -> ReconcileResult:
    """Sum votes per contest from each original PDF; compare to processed CSV."""
    df = pd.read_csv("data/processed/boulder_election_results.csv")
    checks: list[Check] = []
    for original_pdf in sorted(Path("data/original/boulder_county_sov").rglob("*.pdf")):
        vintage = original_pdf.parent.name
        pdf_totals = _extract_totals_from_pdf(original_pdf)  # parser-specific
        csv_totals = (
            df.query("source == 'boulder_county_sov' and vintage == @vintage")
              .groupby("contest")["votes"].sum().to_dict()
        )
        for contest, expected in pdf_totals.items():
            actual = csv_totals.get(contest, 0)
            checks.append(Check(
                label=f"{vintage}:{contest}",
                expected=expected, actual=actual,
                match=(expected == actual),
                delta=actual - expected,
            ))
    return ReconcileResult(source="boulder_county_sov", checks=checks)


RECONCILE_REGISTRY: dict[str, Callable[[], ReconcileResult]] = {
    "boulder_county_sov": reconcile_boulder_sov,
}
```

### When to turn reconciliation on

Default: off. Reconciliation costs developer time to write per-source logic and CI time on every run.

Turn it on when:

- The data will be cited publicly.
- The data is contested (election results, salary databases, anything where someone has motivation to dispute the numbers).
- The publisher publishes top-line totals separately from the per-row data, *and* those totals are authoritative (the published total is the ground truth, not just a side-effect).

Don't turn it on for:

- Exploratory pipelines.
- Sources where you don't have an independent total to compare against.
- One-shot extractions that won't be re-run.

When you do turn it on, document the reconciliation logic in `AGENTS.md` so a future maintainer knows which totals are the authoritative ones to check against. Boulder Election-Results does this clearly: the AGENTS.md section "What reconcile.py checks" enumerates the four authoritative totals per Statement of Vote and explains why each is independent of the per-precinct rows.

### Reconcile output

`scripts/reconcile.py` writes `data/audit/reconcile.json` with the full per-check results and prints a summary:

```
$ uv run python -m scripts.pipeline reconcile
[boulder_county_sov] 149/150 checks matched
    ✗ 2009:BOULDER COUNTY COMMISSIONER DISTRICT 1: expected=23456 actual=23457 delta=1
       (known: precinct 042 subtotal in source PDF has +1 arithmetic error;
        see docs/data-dictionary.md "Known mismatches")
```

Non-matching checks return a non-zero exit code, which fails the CI reconcile job. The pipeline `run` workflow continues; the reconcile failure is a separate signal.

## The recurring-refresh pattern (cron + PR)

For recurring sources (annual statements of vote, monthly FOIA logs, weekly compensation pulls), wire a GitHub Actions cron that runs `discover → fetch → clean → audit` and opens a PR with the new data and audit report. The template ships a ready-to-rename `refresh.yml.disabled`; the canonical pattern is captured there. Three decisions matter:

**Cadence — slightly trail the publisher.** Faster than the publisher updates wastes compute and pollutes the audit history; lagging is fine because `workflow_dispatch` covers the impatient case.

| Publisher cadence | Cron |
|---|---|
| Annual (post-certification) | `"0 13 1 11 *"` — Nov 1, 13:00 UTC |
| Monthly | `"0 13 1 * *"` — 1st of each month |
| Weekly | `"0 13 * * 1"` — Mondays |
| On-demand | Omit `schedule:`; keep `workflow_dispatch:` |

**PR, not commit-to-main.** Auto-commits make a silent change to published data. A PR forces a human pass on four signals: does the row-count delta in `data/audit/summary-*.md` match expectations? Any new entries in `extraction_errors.json`? Any new "Empty sources" flags? Did `reconcile.py` (if enabled) newly mismatch? Mature pipelines with strong reconcile coverage sometimes relax this to commit-to-main with audit-driven rollback; PR is the safer default and what BoulderPublicData, PUDL, and IPEDS-pipeline actually use.

**Path-scoped commits.** Stage `data/original/**`, `data/processed/**`, `data/audit/**`, and the auto-generated `docs/variables.*` files. Anything outside that scope means the workflow misbehaved.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `discover.py` reports zero artifacts | Index page redesigned; CSS selector no longer matches | Update the selector; commit a recorded HTTP cassette in `tests/fixtures/` so the test catches the next breakage |
| Audit shows null rates of 1.0 for a previously-working column | Parser broke silently on a layout change | Look at the most recent vintage in `data/original/`; compare to the prior vintage's layout |
| `extraction_errors.json` accumulates across runs without anyone noticing | Audit summary doesn't surface error count prominently enough | Add an early-section "⚠️ N extraction errors" line to the audit Markdown |
| Reconcile passed for years and now fails on one check | (a) Genuine regression in a new parser, OR (b) upstream arithmetic error in the source PDF | Re-open the source PDF; compute the totals by hand on one precinct. If the source PDF itself is wrong, document in `docs/data-dictionary.md` "Known mismatches" and adjust the expected total. |
| Cron runs daily and the publisher updates annually | Cadence mismatch; audit history is mostly noise | Move cron to annual; use `workflow_dispatch` for impatient refreshes |
| PR from cron sits unreviewed for months | No notification or human accountability | Add a `CODEOWNERS` entry; configure GitHub notifications; or move to commit-to-main with strong audit-driven rollback |

## What to write in the AGENTS.md

- **Refresh cadence** — the cron expression (if `refresh.yml` is enabled) and which day of the publication cycle it trails.
- **Discovery surface** — what `discover.py` checks per source (URL pattern, index page, year range). First place to look when a publisher redesigns.
- **Reconcile scope** (if enabled) — which authoritative totals are checked against which originals, plus a "Known mismatches" subsection with each entry's explanation.
- **Audit invariants** the summary alone can't express, e.g., "source X should always be non-empty for vintages ≥ 2010" or "null rate on `precinct` must stay ≤ 0.01."

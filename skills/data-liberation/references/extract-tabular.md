# Extract: tabular inputs (XLSX, CSV, Parquet, databases)

A large fraction of public datasets are already tabular when published — XLSX from government portals, CSV from open-data sites, Parquet from data brokers, dumps from SQL databases. They are *technically* structured but often as hostile to reuse as PDFs: panel-format spreadsheets with merged headers, CSVs with inconsistent delimiters across years, schema drift, undocumented sentinel values, encoding bombs. This part covers reading these inputs reliably and surfacing structural problems early.

## Reading XLSX

[`pandas.read_excel`](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html) (with the `openpyxl` engine for modern `.xlsx` and `xlrd` for legacy `.xls`) is the default. For 80% of well-formed spreadsheets it just works:

```python
import pandas as pd

df = pd.read_excel("data/original/agency/2024.xlsx", sheet_name="Data", header=0)
```

The 20% that doesn't is where civic data liberation lives. The diagnostic order when a spreadsheet doesn't yield cleanly:

### Inspect first, parse second

Before calling `read_excel`, open the file with `openpyxl` and look at the structure:

```python
import openpyxl

wb = openpyxl.load_workbook("data/original/agency/2024.xlsx", data_only=True)
for ws in wb.worksheets:
    print(ws.title, ws.dimensions, ws.max_row, ws.max_column)
    print("merged ranges:", [str(r) for r in ws.merged_cells.ranges][:5])
    # first 5 rows, raw
    for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
        print(row)
```

Note `data_only=True` — without it, cells containing formulas return the formula string, not the cached value. For pipelines that need the displayed values, `data_only=True` is essential.

What you are looking for:

- **Multiple sheets** — is the data split across years/categories by sheet?
- **Merged cells** — these break naive `read_excel`. The merged value lives in the top-left cell only; the others come back as `NaN`.
- **Header position** — is row 1 the header, or are there 3 rows of title and metadata above it?
- **Multi-row headers** — column meaning is determined by 2+ stacked rows, often combined with merging.
- **Panel format** — the same logical schema is repeated in rectangular blocks down the page (one block per region/year/category).
- **Sentinel values** — empty cells, `"-"`, `"N/A"`, `"."`, `999`, `9999` — what stands in for missing?
- **Trailing junk** — a totals row, footnotes, source citations below the data.

The Boulder County 2008 and 2010 Statement of Vote XLS files are real examples of panel format with merged headers: `precinct-ID ↔ candidate-column` alignment is irregular and required a vintage-specific parser even though the file is "structured."

### Patterns for awkward XLSX

**Multi-row header:**

```python
df = pd.read_excel(path, sheet_name="Data", header=[0, 1])
# columns is now a MultiIndex; flatten:
df.columns = [" / ".join(str(c) for c in tup if pd.notna(c)).strip()
              for tup in df.columns]
```

**Merged header cells forward-fill correctly:**

```python
# After read_excel, the merged value is only in the first column position.
# For a two-row header where row 0 has merged group names:
import pandas as pd

raw = pd.read_excel(path, header=None, nrows=5)
group = raw.iloc[0].ffill()       # forward-fill group across merged span
field = raw.iloc[1]
header = [f"{g} / {f}" for g, f in zip(group, field)]

df = pd.read_excel(path, header=None, skiprows=2)
df.columns = header
```

**Panel format (same schema repeated in blocks):**

The reliable approach is to read the sheet with `header=None` and find the block boundaries programmatically — usually by detecting the rows where a known marker (region name, year header, "Total" row) appears.

```python
raw = pd.read_excel(path, header=None, sheet_name="Data")
block_starts = raw[raw[0].astype(str).str.match(r"^20\d\d$")].index.tolist()
block_starts.append(len(raw))

frames = []
for start, end in zip(block_starts[:-1], block_starts[1:]):
    year = int(raw.iat[start, 0])
    block = raw.iloc[start + 1 : end].copy()
    block.columns = raw.iloc[start + 1].tolist()  # next row is the per-block header
    block = block.iloc[1:]
    block.insert(0, "year", year)
    frames.append(block)

df = pd.concat(frames, ignore_index=True)
```

**Sheet-per-year:**

```python
xls = pd.ExcelFile(path)
frames = []
for sheet in xls.sheet_names:
    if not sheet.isdigit():
        continue
    df = pd.read_excel(xls, sheet_name=sheet)
    df["year"] = int(sheet)
    frames.append(df)
df = pd.concat(frames, ignore_index=True)
```

### Legacy `.xls`

Use `engine="xlrd"`. Note that recent xlrd versions dropped `.xlsx` support; the engine choice in pandas tracks this. For old `.xls` files where the extension lies about the format (Boulder's 2013 SoV is actually XLSX with an `.xls` extension), let pandas auto-detect and pass `engine=None`, or pre-rename the file in `data/original/` with a note.

### Recompute before you trust formulas

When a publisher distributes an XLSX with cells whose values come from formulas, the file stores both the *formula* and the *last-computed value cached when the file was saved*. `pandas.read_excel(..., data_only=True)` reads the cached value — fast, but **stale if the source-of-truth formula and its cached value disagree**. Two ways to find out:

- *The source was edited but not recalculated before save.* Excel and LibreOffice both default to recalc-on-save, but agency exporters built on `openpyxl` (or hand-edited files) often skip this; the cached values silently lag the formula intent.
- *The formula references external workbooks or named ranges that don't resolve in your parser context.* The cached value is the last value seen on the publisher's machine; your environment can't reproduce it.

The general principle: **for any format that separates source-of-truth-expression from cached-value, recompute before parsing.** For XLSX specifically, headless LibreOffice in a `--calc --headless --convert-to xlsx` pass forces a full recalc and writes a normalized file the parser can trust. Document the recompute step in `provenance.csv`'s `extraction_notes` so downstream consumers know which values are publisher-as-saved vs project-recomputed; the two can diverge meaningfully when formulas pull from `INDIRECT()`, `OFFSET()`, or external links.

The same principle applies past XLSX — materialized database views with stale incremental updates, cached query results in BI tools, derived columns in CMS-backed datasets. Any time the file format distinguishes formula from result, the recompute step is part of the parser, not the consumer.

When the formulas themselves are *broken* in the source — visible as `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?` cells — the source has a data-quality problem worth surfacing rather than papering over. See [`pipeline.md#pre-extraction-bulletproofing`](pipeline.md#pre-extraction-bulletproofing) for the "format-native errors are quality signals" check that belongs in the bulletproofing pass.

## Reading CSV

`pandas.read_csv` is well known. Three patterns deserve naming because they trip up almost every project.

### Always declare dtypes for ID-like columns

```python
# WRONG — pandas will parse "07003" as int 7003, losing the leading zero
df = pd.read_csv(path)

# RIGHT — leading zeros preserved
df = pd.read_csv(path, dtype={"precinct_id": str, "zip": str, "fips": str})
```

This is the single most common silent bug in civic data work. Census FIPS codes, ZIP codes, precinct IDs, bill numbers — anything where the leading zero matters — needs explicit string typing.

### Explicit NA tokens

```python
df = pd.read_csv(path, na_values=["", "N/A", "n/a", ".", "--", "NULL", "999", "9999"])
```

Domain sentinels (`-9`, `9999`, `99999`) for missing values are common in government datasets. Document them in `docs/data-dictionary.md` and pass them via `na_values`.

### Encoding

Government CSVs are commonly Latin-1, Windows-1252, or UTF-8 with a BOM. If `pd.read_csv` raises a `UnicodeDecodeError`:

```python
# Try in order
for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
    try:
        df = pd.read_csv(path, encoding=enc)
        break
    except UnicodeDecodeError:
        continue
```

Capture the encoding that worked into provenance — it's a property of the source file that downstream users may need to know.

### Malformed rows

For CSVs with inconsistent column counts per row (e.g., agency exports with unescaped commas in free-text fields):

```python
df = pd.read_csv(path, on_bad_lines="warn")  # log and skip; not silent
# Or, for severe corruption, drop down to the csv module:
import csv
with open(path, newline="") as f:
    reader = csv.reader(f)
    rows = [row for row in reader if len(row) == EXPECTED_NCOLS]
```

If you have to drop rows, **count them and emit the count to the audit log**. Silent loss is the worst kind.

## Reading Parquet

Parquet is the friendly format. `pandas.read_parquet` (with `pyarrow` as the engine) just works:

```python
df = pd.read_parquet("data/original/dataset.parquet")
```

For very large files, read columns or row groups selectively rather than the whole file:

```python
import pyarrow.parquet as pq

# Schema inspection without reading data
schema = pq.read_schema(path)
print(schema)

# Read a subset of columns
df = pd.read_parquet(path, columns=["year", "unitid", "value"])

# Read row groups one at a time
pf = pq.ParquetFile(path)
for batch in pf.iter_batches(batch_size=100_000):
    chunk = batch.to_pandas()
    # process chunk
```

Parquet preserves dtypes — including nullable integers, datetimes, and categoricals — natively. When you write processed data to Parquet, dtype information survives round trips, which is one reason Parquet is the better long-term storage format than CSV for the `data/processed/` directory. Many liberation projects ship both: CSV for accessibility, Parquet for analyst use.

## Reading databases

When the source is a database dump (PostgreSQL, MySQL, SQL Server, SQLite), or a connection string for a live database:

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql+psycopg://user:pw@host/db")
df = pd.read_sql("SELECT * FROM elections WHERE year >= 2010", engine)
```

For SQLite files (a common FOIA release format), no server needed:

```python
import sqlite3
import pandas as pd

with sqlite3.connect("data/original/foia/release.sqlite") as conn:
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
    df = pd.read_sql("SELECT * FROM voters", conn)
```

For ad-hoc exploration of large database dumps, [`duckdb`](https://duckdb.org/) is excellent: it can query CSV, Parquet, and SQLite files directly without a load step, and uses standard SQL.

```python
import duckdb

# Query a Parquet file directly
df = duckdb.sql(
    "SELECT year, COUNT(*) FROM 'data/original/big.parquet' GROUP BY year"
).df()

# Cross-format join in one query
df = duckdb.sql("""
    SELECT a.*, b.region
    FROM 'data/original/elections.csv' a
    LEFT JOIN 'data/original/precincts.parquet' b USING (precinct_id)
""").df()
```

DuckDB is particularly useful in `scripts/audit.py` for reconciliation queries that would be slow in pandas.

## Choosing the output format for `data/processed/`

A liberation project usually ships processed data in multiple formats. Defaults that work:

| Format | When | Why |
|---|---|---|
| **CSV** | Always | Universal accessibility; opens in any tool; the format readers expect when they download a dataset |
| **Parquet** | Always (alongside CSV) | Preserves dtypes; compact; fast to read for analyst-grade use |
| **JSON / JSONL** | When the data is genuinely nested | Better than flattening for irregularly-structured records |
| **SQLite** | When the dataset has multiple related tables | Single-file relational database; downloadable; queryable with any SQL tool |
| **DuckDB file** | For very large multi-table releases | Columnar storage in a single file; future-friendly |

A common emission pattern:

```python
# scripts/pipeline.py end
df.to_csv("data/processed/elections_tidy.csv", index=False)
df.to_parquet("data/processed/elections_tidy.parquet", index=False)
```

Both files have the same content but different downstream affordances. Document this in the README; many readers don't know what Parquet is and default to CSV.

## Dtype hygiene at the boundary

Whatever the input format, **coerce to canonical dtypes at the boundary of the parser** before returning the DataFrame. Use pandas's nullable dtypes (`Int64`, `Float64`, `string`, `boolean`) rather than the legacy numpy-backed types, because nullable dtypes preserve NA distinctly from 0 / empty-string / NaN:

```python
import pandas as pd

def _coerce(df: pd.DataFrame) -> pd.DataFrame:
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["count"] = pd.to_numeric(df["count"], errors="coerce").astype("Int64")
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce").astype("Float64")
    for col in ("source", "precinct_id", "contest", "candidate"):
        df[col] = df[col].astype("string")
    return df
```

This pays off downstream: pandera schemas validate cleanly, parquet write preserves the types, and analysts joining your data to theirs don't get surprised by `int64` columns silently turning into `float64` because of NAs.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Leading zeros stripped from IDs | pandas inferred numeric dtype | Pass `dtype={"id_column": str}` to `read_csv`/`read_excel` |
| `NaN` everywhere in a column after `read_excel` | Cells contain formulas, not values | Pass `data_only=True` to `openpyxl.load_workbook`, or pre-resolve formulas in Excel |
| `UnicodeDecodeError` | Encoding is not UTF-8 | Try `cp1252`, `latin-1`, `utf-8-sig` (BOM) |
| One row has wrong column count | Unescaped delimiter in a text field | `quoting=csv.QUOTE_ALL` if author's choice, or `on_bad_lines="warn"` to log + skip |
| Date column comes back as strings | pandas didn't infer datetime | `parse_dates=["date_col"]` or `pd.to_datetime` after read |
| Numeric column has trailing whitespace | Source has " 123" with leading space | `pd.to_numeric(s.str.strip(), errors="coerce")` |
| Same data, different schemas across years | Mid-period schema change | Vintage-specific parser, harmonize via concept catalog |
| Sentinel value `999` treated as a real number | Domain-specific NA token | Pass `na_values=[999, "999"]` to `read_csv` |

---

## What to write in the AGENTS.md

- File format(s), including any cases where the extension lies about the actual format.
- Encoding — often a hidden property of the source.
- Sentinel values used for missing data.
- Panel format / multi-row headers / merged cells, with the per-vintage strategy.
- Dtype expectations for ID-like columns (FIPS, ZIP, precinct ID, agency code).

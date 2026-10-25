# Extract: PDF (pdfplumber, camelot)

The tools — `pdfplumber` and `camelot` — each excel at a different class of born-digital PDF, and most projects use both in combination. Scanned or image-only PDFs go down the OCR path in [`extract-images.md`](extract-images.md) instead.

## First: identify the PDF type

Classify the input before opening any extractor. Run this triage and write the result in the project's Survey notes.

```python
import pdfplumber

with pdfplumber.open(path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text() or ""
    has_text_layer = len(text.strip()) > 20
    n_chars = len(page.chars)
    n_lines = len(page.lines) + len(page.rects)
    n_images = len(page.images)
```

| `has_text_layer` | `n_lines` | `n_images` | Diagnosis | Default tool |
|---|---|---|---|---|
| True | Many | Few | **Born-digital ruled table** | `camelot` (lattice) |
| True | Few/none | Few | **Born-digital text-positioned table** | `pdfplumber` |
| True | Some | Few | **Born-digital mixed** | `pdfplumber` first, `camelot` for grid pages |
| False | — | Many or full-page | **Scanned PDF (image-only)** | `tesseract` via `pytesseract` |
| True | — | Many | **Hybrid (scanned + text overlay)** | Inspect; usually `pdfplumber` works |

Sanity check: open the PDF in a viewer and try to **select and copy text** from a table cell. If you get the cell content, the text layer is good — use `pdfplumber` or `camelot`. If you get nothing or garbled glyphs, it's scanned and you need OCR.

Scanned or image-only PDF? The rasterize → preprocess → OCR path lives in [`extract-images.md`](extract-images.md).

## pdfplumber — the default for born-digital PDFs

[`pdfplumber`](https://github.com/jsvine/pdfplumber) is the workhorse. It exposes characters with positions, lines, rectangles, and curves, and offers a configurable table-detection pass that infers rows and columns from spatial layout. It is the right default whenever the PDF has a text layer. (Pdfplumber is built on [`pdfminer.six`](https://github.com/pdfminer/pdfminer.six), the community-maintained text-extraction engine — drop to pdfminer.six directly when pdfplumber's higher-level abstractions get in the way, but the rest of this section assumes the pdfplumber API.)

### Minimal idiomatic use

```python
import pdfplumber

with pdfplumber.open("data/original/agency/report.pdf") as pdf:
    rows = []
    for page in pdf.pages:
        for table in page.extract_tables() or []:
            rows.extend(table)
```

`page.extract_tables()` returns a list of lists (outer = tables on the page; inner = rows of cell strings). `page.extract_table()` returns just the first table.

The PDF also carries metadata via `pdf.metadata` — title, author, creator (authoring application), producer (library that wrote the bytes), creation/modification timestamps. None is load-bearing for extraction, but the *producer* field is useful provenance: when a multi-vintage series shifts from `"Microsoft Word"` to `"Adobe PDF Library"` mid-period, the parser usually needs a vintage branch shortly after. Worth copying into `provenance.csv`'s `extraction_notes` for the vintages where the source switched.

### When the default detection misfires

The default detector uses both lines and text positioning. When it's wrong it's usually wrong in one of these ways:

- **Splits one table into many** — usually because there are blank rows mid-table or section headers that look like table breaks. Pass `table_settings={"vertical_strategy": "lines", "horizontal_strategy": "text"}` to lean harder on rulings.
- **Merges two adjacent tables** — opposite cause; pass `{"vertical_strategy": "text", "horizontal_strategy": "text"}` or extract by cropping to a bounding box first.
- **Misses rows that wrap** — increase `snap_tolerance` and `text_tolerance` so wrapped lines aren't treated as new rows.
- **Hallucinates columns from spaced-out text** — pass explicit `explicit_vertical_lines` from inspecting `page.lines` and `page.rects`.

The configuration vocabulary is in [the pdfplumber README](https://github.com/jsvine/pdfplumber#extracting-tables) and [Unstract's pdfplumber guide](https://unstract.com/blog/guide-to-pdfplumber-text-and-table-extraction-capabilities/). Two patterns worth memorizing:

```python
# Bounding-box crop before extraction — when the page has a table plus headers/footers
bbox = (40, 100, page.width - 40, page.height - 80)
table = page.crop(bbox).extract_table()

# Use the lines you can see, ignore the inferred ones
table = page.extract_table({
    "vertical_strategy": "explicit",
    "horizontal_strategy": "lines",
    "explicit_vertical_lines": [v["x0"] for v in page.lines if v["height"] > 100],
})
```

### What pdfplumber struggles with

- **Tables that span multiple pages** — pdfplumber doesn't join them. Handle in your parser: detect a continuation header on each page, drop it, concatenate the row lists.
- **Multi-row column headers / merged header cells** — extracted as separate rows; flatten in the parser.
- **Panel-format tables** where the same logical row repeats blocks across pages — write a vintage-specific parser that knows the panel structure.
- **Cells with embedded line breaks** — pdfplumber returns the raw text including the newline; clean in the parser.

Boulder Public Data's older Statements of Vote (2005, 2007, 2009) are pdfplumber-extractable but with vintage-specific parsers per year. The 2009 SoV is bundled here as a test fixture.

## camelot — for cleanly ruled tables

[`camelot`](https://github.com/camelot-dev/camelot) is purpose-built for table extraction from born-digital PDFs and provides two modes:

- **Lattice mode** (`flavor="lattice"`) — detects ruled tables by finding line intersections. Outstanding when the table has visible grid lines; useless when it doesn't.
- **Stream mode** (`flavor="stream"`) — uses text positioning, similar to pdfplumber's default. Often worse than pdfplumber for stream-style tables; reach for camelot specifically for lattice.

### When to choose camelot over pdfplumber

- The table has clear horizontal AND vertical rulings forming a complete grid.
- pdfplumber's default detection is breaking on multi-row header cells (camelot handles these better via the grid).
- You need a quick accuracy report — camelot returns an `accuracy` and `whitespace` percentage per table that's useful for triaging which pages need manual review.

```python
import camelot

tables = camelot.read_pdf(
    "data/original/agency/report.pdf",
    pages="1-end",
    flavor="lattice",
)
for t in tables:
    print(t.page, t.parsing_report)  # accuracy, whitespace, order, page
    df = t.df  # pandas DataFrame
```

The [camelot test corpus](https://github.com/camelot-dev/camelot/tree/master/tests/files) contains documented examples of both lattice and stream cases — use them as fixtures when validating a new parser.

### camelot's quirks

- Requires `ghostscript` (lattice mode) — install via the system package manager. On macOS: `brew install ghostscript`. On Debian/Ubuntu: `apt install ghostscript`.
- Slow on long PDFs. If you only need a few pages, pass `pages="3,7,12"`.
- The `accuracy` metric is a useful triage signal but not a substitute for reconciliation against an authoritative total.

## Putting it together — a working extraction skeleton

```python
"""scripts/parsers/agency_2009_sov.py — example parser for a born-digital SoV PDF.

Pattern: a parser module exposes `parse(path: Path) -> pd.DataFrame` returning
a tidy long-form frame conforming to scripts.schema.LONG_COLUMNS, and is
called from scripts/clean.py for the relevant (source, vintage) tuple.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
import pandas as pd

from scripts.schema import normalize_long


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse(path: Path) -> pd.DataFrame:
    """Parse a 2009-vintage Boulder County Statement of Vote PDF."""
    extracted_at = datetime.now(timezone.utc).isoformat()
    file_hash = _sha256(path)
    rows: list[dict] = []

    with pdfplumber.open(path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "text",
                "snap_tolerance": 4,
            })
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header, *body = table
                # ... vintage-specific cleaning here ...
                for body_row in body:
                    rows.append({
                        "source": "boulder_county_sov",
                        "vintage": 2009,
                        "page": page_idx + 1,
                        "source_file_sha256": file_hash,
                        "extracted_at": extracted_at,
                        # ... domain fields per scripts/schema.py ...
                    })

    return normalize_long(pd.DataFrame(rows))
```

A few patterns this skeleton illustrates that you should keep:

- **Hash the source file** on every parse run and emit it on every row (or, more economically, into the per-extract provenance sidecar). This makes downstream errors traceable to the exact input file.
- **`extracted_at` timestamp** — UTC ISO-8601. Required for provenance.
- **`vintage`** as a column — the data was published in a particular year, possibly with that year's quirks.
- **Vintage-specific parsing logic** is fine and expected. Resist the urge to write one parser that handles all years; you'll fight every special case forever. One parser per vintage, with shared helpers in `scripts/parsers/_normalize.py` (regex / string transforms; see [`pipeline.md`](pipeline.md#6-standardization-and-normalization)).
- **Return normalized long-form** at the boundary. The parser's job ends when it has produced a tidy DataFrame; the schema module's job is to validate it.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `page.extract_table()` returns `None` | No table detected on page | Crop to the table region; try lattice mode in camelot; if scanned, switch to OCR |
| Rows look right but one column is consistently empty | Column header text overlaps with a ruling; default detection split the column | Pass `explicit_vertical_lines` from inspecting `page.lines` |
| Numbers come out with a digit missing | Cell is very narrow and pdfplumber's text grouping is dropping characters | Reduce `text_tolerance` and `snap_tolerance`; or extract via `page.chars` directly and reconstruct |
| Multi-page table has duplicate header rows in the output | No detection of repeated continuation headers | Detect by exact-match on the first row; drop on continuation pages |
| Two adjacent tables get merged | Default detection treated whitespace between as a row | Crop before extraction, one table at a time |
| `camelot` accuracy reports >95% but the data is wrong anyway | Table structure is irregular; camelot recovered the grid but the cells are mislabeled | Reconcile against authoritative totals (the `reconcile.py` pattern) — accuracy != correctness |

OCR-specific failure modes (`"rn"`/`"m"` artifacts, dropped digits, fragmented rows) live in [`extract-images.md`](extract-images.md#common-failure-modes).

---

## What to write in the AGENTS.md

- Which tool (pdfplumber / camelot) for which source × vintage, and the classifier fact that drove the choice. (For OCR engine choices on scanned PDFs, see [`extract-images.md`](extract-images.md#what-to-write-in-the-agentsmd).)
- Any non-default configuration — table_settings, snap/text tolerances, explicit lines.
- Per-vintage quirks (merged cells, footnoted rows, multi-page table headers).

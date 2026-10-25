# Extract: born-digital PDF (PDFium, pdfplumber, camelot)

A born-digital PDF was written by software (Word, Excel, a report writer), so its text layer holds the publisher's own characters at exact positions. That text layer is ground truth: read it, don't re-read pixels. Most civic tables (statements of vote, financial reports, agency annual reports) are born-digital. This file covers Outline section 3 (Extract) for them; scanned pages go to [`extract-images.md`](extract-images.md), and layouts that defeat rule-based tools go to [`extract-documents.md`](extract-documents.md).

## Contents

- [Install](#install)
- [1. Triage every page](#1-triage-every-page)
- [2. Read the text layer with PDFium](#2-read-the-text-layer-with-pdfium)
- [3. Positioned words and tables with pdfplumber](#3-positioned-words-and-tables-with-pdfplumber)
- [4. Ruled tables with camelot](#4-ruled-tables-with-camelot)
- [5. Multi-page tables, footnotes and redactions](#5-multi-page-tables-footnotes-and-redactions)
- [6. Coordinates and region provenance](#6-coordinates-and-region-provenance)
- [7. Reconcile against printed totals](#7-reconcile-against-printed-totals)
- [8. A working parser skeleton](#8-a-working-parser-skeleton)
- [9. The provenance row](#9-the-provenance-row)
- [When to leave this file](#when-to-leave-this-file)
- [Common failure modes](#common-failure-modes)
- [What to write in the AGENTS.md](#what-to-write-in-the-agentsmd)

## Install

For a one-off, run without a project: `uv run --with pypdfium2 --with pdfplumber --with camelot-py python extract.py`. In a project, add the same three to the `pdf` extra in `pyproject.toml` and pin them through `uv.lock`, because text-extraction output can change between library versions.

Versions checked on 2026-10-25 by installing from PyPI: [`pypdfium2`](https://pypi.org/project/pypdfium2/) 5.14.0 (Apache-2.0/BSD, a single wheel with PDFium inside, no system packages); [`pdfplumber`](https://github.com/jsvine/pdfplumber/releases) 0.11.10 on pdfminer.six 20260107 (MIT); [`camelot-py`](https://pypi.org/project/camelot-py/) 2.0.0 (MIT). Camelot no longer needs Ghostscript: since 1.0 its image backend is PDFium ([install docs](https://camelot-py.readthedocs.io/en/latest/_sources/user/install.rst)), Ghostscript is an optional extra, and the old `camelot-py[cv]` extra no longer exists. Camelot depends on `opencv-python-headless`, which conflicts with any other OpenCV wheel (`opencv-python`, `opencv-contrib-python`) in the same environment, so keep only one.

Avoid two older choices unless a project already depends on them. PyMuPDF and pymupdf4llm are fast and good, but AGPL-3.0, which matters if the pipeline is ever offered as a service ([Artifex, 2026-03-16](https://artifex.com/blog/introducing-the-new-pymupdf4llm-now-including-layout)). Tabula needs Java and has had little activity since tabula-py 2.10.0 (2024-10-17); keep it only in legacy pipelines.

## 1. Triage every page

Classify each page, not the document and not page one: agency PDFs mix typed pages, scanned inserts, image-only appendices and pages with an OCR layer pasted over a scan. Test the *quality* of the text, not only whether text exists. Write the per-page result into the project's Survey note (or the one-off's README note).

```python
"""Per-page triage: run on every page and keep the table it prints."""
import re
from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

WORDISH = re.compile(r"[A-Za-z]{2,}")
NUMBERISH = re.compile(r"[\d.,$()%-]+")


def text_quality(text: str) -> float:
    """Share of tokens that look like words or numbers; garbled glyph maps score low."""
    tokens = text.split()
    if not tokens:
        return 0.0
    return sum(bool(WORDISH.search(t) or NUMBERISH.fullmatch(t)) for t in tokens) / len(tokens)


def triage(path: Path) -> list[dict]:
    rows = []
    pdf = pdfium.PdfDocument(path)
    with pdfplumber.open(path) as plumb:
        for i in range(len(pdf)):
            page = pdf[i]
            width, height = page.get_size()
            text = page.get_textpage().get_text_bounded()
            image_area = 0.0
            for obj in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]):
                left, bottom, right, top = obj.get_bounds()
                image_area += max(0, right - left) * max(0, top - bottom)
            pp = plumb.pages[i]
            rows.append({
                "page": i + 1,
                "pdfium_chars": len("".join(text.split())),
                "plumber_chars": len(pp.chars),   # 0 while PDFium reads text: pdfminer can't read this file
                "text_quality": round(text_quality(text), 3),
                "garbled": text.count("�") + text.count("(cid:"),
                "rules": len(pp.lines) + len(pp.rects),
                "image_cover": round(min(image_area / (width * height), 1.0), 2),
                "rotation": page.get_rotation(),
            })
    pdf.close()
    return rows


def classify(r: dict) -> str:
    if r["pdfium_chars"] < 20:
        return "scanned" if r["image_cover"] > 0.5 else "blank"
    if r["image_cover"] > 0.8:
        return "ocr_layer"         # text over a page image: test it before trusting it
    if r["text_quality"] < 0.8 or r["garbled"]:
        return "bad_text_layer"
    return "ruled" if r["rules"] > 20 else "text"
```

| Class | What it means | Go to |
|---|---|---|
| `text` | Born-digital, whitespace-aligned table or prose | PDFium lines (section 2) or pdfplumber words (section 3) |
| `ruled` | Born-digital table with drawn grid lines | camelot lattice or pdfplumber `lines` strategy (sections 3–4) |
| `ocr_layer` | A page image with text on top, usually from a scanner or an agency's OCR | [`extract-images.md`](extract-images.md): test the embedded layer before using it |
| `bad_text_layer` | Text exists but is garbled (broken font mapping) | Try the other reader first; if both are garbled, OCR the page via [`extract-images.md`](extract-images.md) |
| `scanned` | Image only | [`extract-images.md`](extract-images.md) |

Also try the manual check on a few pages of each class: select and copy a table cell in a viewer. A clean paste confirms the class; garbage, or a paste that differs from what you see, means the text layer can't be trusted for that page. Thresholds in `classify` are starting points; adjust them per corpus and record what you used.

## 2. Read the text layer with PDFium

[PDFium](https://pdfium.googlesource.com/pdfium/), through `pypdfium2`, is the default reader. It is fast, ships as one wheel, and reads files that pdfminer.six (and therefore pdfplumber) has been seen to return as silently empty, for example some PDFs with hybrid cross-reference tables. Use it for text, character boxes and page renders.

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("data/original/agency/2009/report.pdf")
page = pdf[0]
width, height = page.get_size()             # PDF points
textpage = page.get_textpage()
full_text = textpage.get_text_bounded()     # whole page, in PDFium's reading order
for r in range(textpage.count_rects()):     # text runs, each roughly one cell or line segment
    left, bottom, right, top = textpage.get_rect(r)          # bottom-left origin
    run = textpage.get_text_bounded(left, bottom, right, top)
box = textpage.get_charbox(0)               # (left, bottom, right, top) for one character
image = page.render(scale=300 / 72).to_pil()  # a 300-DPI render, for OCR or audit crops
pdf.close()
```

Text runs grouped by their vertical position give you visual lines with boxes; section 8 does exactly that. Keep the reading layer engine-agnostic: one function turns the PDF into `(page, text, bbox)` lines, and the parsing rules work on those lines with no PDF imports. Then the rules are testable without a PDF, and a reader can be swapped or cross-checked without touching them.

A cheap completeness check: compare page counts and per-page character counts from two readers (PDFium and pdfplumber, as in the triage). A page where one reader finds text and the other finds none is a reader problem, not an empty page.

## 3. Positioned words and tables with pdfplumber

[`pdfplumber`](https://github.com/jsvine/pdfplumber) exposes every character, word, line and rectangle with coordinates in PDF points with a top-left origin, and a configurable table finder that returns each cell's box. Use it when you need words by position (whitespace-aligned columns) or cell-level boxes.

```python
import pdfplumber

with pdfplumber.open("data/original/agency/2009/report.pdf") as pdf:
    page = pdf.pages[13]
    words = page.extract_words()              # dicts with text, x0, top, x1, bottom
    for table in page.find_tables({"vertical_strategy": "lines", "horizontal_strategy": "lines"}):
        data = table.extract()                 # list of rows of cell strings
        for row, cells in zip(table.rows, data):
            for text, cell_bbox in zip(cells, row.cells):   # cell_bbox: (x0, top, x1, bottom) or None
                ...
```

When the default table detection misfires:

- **Splits one table into many** (blank rows or section headers look like breaks): `{"vertical_strategy": "lines", "horizontal_strategy": "text"}`.
- **Merges two adjacent tables:** crop to one table first with `page.crop((x0, top, x1, bottom))`, then extract.
- **Misses rows that wrap:** raise `snap_tolerance` and `text_tolerance`.
- **Invents columns from spaced-out text:** pass `"vertical_strategy": "explicit"` with `explicit_vertical_lines` taken from `page.lines` and `page.rects`, or from x positions measured once per vintage.
- **Dashed rules are ignored or produce noise:** pdfplumber 0.11.8 added `edge_min_length_prefilter` for this ([releases](https://github.com/jsvine/pdfplumber/releases)).

Record every non-default `table_settings` value in the parser and in `AGENTS.md`; pdfplumber's table defaults have changed across 0.11.x releases. `pdf.metadata["Producer"]` is worth copying into the provenance notes: when a series switches producer mid-period, a vintage branch usually follows.

## 4. Ruled tables with camelot

[`camelot`](https://github.com/camelot-dev/camelot) is the tool for tables with a complete drawn grid. `flavor="lattice"` (the default) finds line intersections on a PDFium render and fills cells from the text layer. It is excellent on ruled tables and of little use without rules.

```python
import camelot

tables = camelot.read_pdf(
    "data/original/agency/2009/report.pdf",
    pages="all",        # the default is page 1 only
    flavor="lattice",
)
for t in tables:
    print(t.page, t.parsing_report)    # accuracy, whitespace, order, page
    df = t.df                          # cells as strings
    cell = t.cells[0][0]               # cell.x1, cell.y1, cell.x2, cell.y2: points, bottom-left origin
```

Camelot 2.0.0 (installed 2026-10-25) also lists `stream`, `network` and `hybrid` flavors for borderless tables, `auto` (chooses a flavor per page), and an optional `ml` flavor (`camelot-py[ml]`) that finds structure with a table-transformer model and fills cells from the PDF's own text layer. For borderless tables pdfplumber is usually easier to control; try the newer flavors when it plateaus and compare results on golden pages before switching. `parsing_report["accuracy"]` is a triage signal for which pages to inspect, never a substitute for reconciliation: a table can score 100 and still put values in the wrong columns.

## 5. Multi-page tables, footnotes and redactions

**Multi-page tables.** No tool reliably joins a table across pages, so stitching is an explicit, tested parser step. On each continuation page, detect and drop the repeated header (exact match on its text), carry forward any group label the header implies ("Precinct 12, continued"), keep page-break rows such as "Page total" or "Carried forward" out of the data but use them as checks, and keep the source page on every row. A test fixture should include at least one page break.

**Footnotes.** Footnote markers change what a number means ("revised", "estimate", "excludes X"). Never drop them silently. Split the marker into a `note` column and keep the footnote text in the data dictionary or a lookup. Watch for superscript digits glued to numbers: `1,2341` is often `1,234` with note `1`. pdfplumber's `char["size"]` (or the PDFium character-box height) tells a superscript from a digit.

**Redactions.** Some redactions are only black rectangles drawn over live text, so the "redacted" text is still in the text layer. Detect filled rectangles that overlap characters (`page.rects` with a dark `non_stroking_color`, intersected with `page.chars`). Record those regions as withheld (null value, a `withheld` flag and the box) and do not extract, store or publish the text underneath. Tell the user: it is a governance question, not a parsing one (see `_shared/responsible-data.md`).

**Page numbers.** The PDF page index and the printed folio often differ. Record the PDF page (1-based) on every row and keep the printed folio too when people will cite the document by it. Take period keys (year, quarter) from the content of the page, not from the filename or folder.

## 6. Coordinates and region provenance

Every value should trace to source hash, page and region. Each tool reports boxes differently, so convert once, at the reader boundary, to one canonical form: **PDF points, top-left origin, 1-based page, `(x0, y0, x1, y1)`**.

| Tool | Native boxes | To canonical |
|---|---|---|
| pdfplumber | points, top-left (`x0, top, x1, bottom`) | as is |
| PDFium / pypdfium2 | points, bottom-left (`left, bottom, right, top`) | `y0 = height - top`, `y1 = height - bottom` |
| pdfminer.six | points, bottom-left | as PDFium |
| camelot cells | points, bottom-left (`x1, y1, x2, y2`) | as PDFium |
| a page render at D DPI | pixels, top-left | multiply by `72 / D` |

Check `page.get_rotation()` (or pdfplumber's `page.rotation`) and a non-zero media box origin (`page.bbox` in pdfplumber) during triage; both shift coordinates. Write the region as `page` and `bbox_pt` columns on each row (or a `region_id` that joins to a regions sidecar), and say in the data dictionary which granularity applies (character, cell, line or block). A human-followable citation looks like `sha256:ab12…#page=14&bbox=72.0,301.5,540.3,318.0`; `#page=` is a standard PDF open parameter, and the `bbox` part is this project's convention.

## 7. Reconcile against printed totals

When the document prints totals or subtotals, the extracted rows must sum to them, and the result is reported either way. Reconcile at the finest grain the document prints (per office, per precinct, per fund), not only a grand total, which can hide offsetting errors or differ for legitimate scope reasons. A mismatch is an error to explain, not a rounding to absorb. When a document prints no totals, compare row counts against any count it states, and spot-check a sample of cells against the page.

## 8. A working parser skeleton

This parser is for one vintage of a born-digital table. It reads lines with PDFium, parses them with plain rules, keeps page and box on every row, drops repeated headers, reconciles with the printed total, and fails loudly on empty or unreconciled output. It was run on 2026-10-25 against a three-page ruled table with pypdfium2 5.14.0 and pandas 3.1.

```python
"""scripts/parsers/county_sov_2009.py: parser for one born-digital vintage.

`read_lines` is the only code that touches a PDF library; `parse_lines` works on
plain (page, text, bbox) lines, so it is testable without a PDF.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pypdfium2 as pdfium

SOURCE, VINTAGE = "county_sov", "2009"
HEADER = re.compile(r"^Precinct\s+Candidate A\s+Candidate B$")
ROW = re.compile(r"^(?P<precinct>\d{4})\s+(?P<a>[\d,]+)\s+(?P<b>[\d,]+)$")
TOTAL = re.compile(r"^TOTAL\s+(?P<a>[\d,]+)\s+(?P<b>[\d,]+)$")


@dataclass(frozen=True)
class Line:
    page: int                                  # 1-based PDF page
    text: str
    bbox: tuple[float, float, float, float]    # PDF points, top-left origin: x0, y0, x1, y1


def read_lines(path: Path, y_tol: float = 2.0) -> list[Line]:
    """Group PDFium text runs into visual lines, top to bottom, left to right."""
    lines: list[Line] = []
    pdf = pdfium.PdfDocument(path)
    try:
        for i in range(len(pdf)):
            page = pdf[i]
            _, height = page.get_size()
            textpage = page.get_textpage()
            runs = []
            for r in range(textpage.count_rects()):
                left, bottom, right, top = textpage.get_rect(r)
                text = textpage.get_text_bounded(left, bottom, right, top).strip()
                if text:  # flip PDFium's bottom-left origin to top-left, once, here
                    runs.append((height - top, left, height - bottom, right, text))
            runs.sort(key=lambda s: (round(s[0] / y_tol), s[1]))
            current: list[tuple] = []
            for run in runs + [None]:
                if current and (run is None or abs(run[0] - current[0][0]) > y_tol):
                    lines.append(Line(
                        page=i + 1,
                        text=" ".join(s[4] for s in current),
                        bbox=(min(s[1] for s in current), min(s[0] for s in current),
                              max(s[3] for s in current), max(s[2] for s in current)),
                    ))
                    current = []
                if run is not None:
                    current.append(run)
    finally:
        pdf.close()
    return lines


def _num(s: str) -> int:
    return int(s.replace(",", ""))


def parse_lines(lines: list[Line]) -> tuple[pd.DataFrame, dict[str, int], list[Line]]:
    """Return (tidy rows, printed totals, lines no rule recognized)."""
    rows, printed, unparsed = [], {}, []
    for ln in lines:
        if HEADER.match(ln.text):              # repeated on every continuation page
            continue
        if m := TOTAL.match(ln.text):
            printed = {"Candidate A": _num(m["a"]), "Candidate B": _num(m["b"])}
            continue
        if m := ROW.match(ln.text):
            for candidate, key in (("Candidate A", "a"), ("Candidate B", "b")):
                rows.append({
                    "source": SOURCE,
                    "vintage": VINTAGE,
                    "precinct": m["precinct"],     # a string: leading zeros matter
                    "candidate": candidate,
                    "votes": _num(m[key]),
                    "page": ln.page,
                    "bbox_pt": ",".join(f"{v:.1f}" for v in ln.bbox),
                })
            continue
        unparsed.append(ln)
    return pd.DataFrame(rows), printed, unparsed


def reconcile(df: pd.DataFrame, printed: dict[str, int]) -> list[str]:
    if not printed:
        return ["no printed total found"]
    sums = df.groupby("candidate")["votes"].sum().to_dict()
    return [f"{k}: extracted {sums.get(k, 0)} != printed {v}"
            for k, v in printed.items() if sums.get(k, 0) != v]


def parse(path: Path) -> pd.DataFrame:
    df, printed, unparsed = parse_lines(read_lines(path))
    if df.empty:
        raise ValueError(f"{path.name}: no rows extracted")      # empty is an error
    if problems := reconcile(df, printed):
        raise ValueError(f"{path.name}: does not reconcile: {problems}")
    df.attrs["unparsed"] = [(ln.page, ln.text) for ln in unparsed]  # caller logs and counts these
    return df
```

Patterns to keep:

- **No per-row timestamps.** Retrieval time, hash and tool versions belong to the extract, in `provenance.csv` (section 9). A per-row `extracted_at` makes the processed output differ on every run.
- **One parser per vintage**, with shared helpers in `scripts/parsers/_normalize.py`. A format change mid-series gets a new vintage branch, not another `if` in an old one.
- **Unrecognized lines are counted, not ignored.** The pipeline writes them to the run's error log and reports the count; a jump in that count is the first sign of a format change.
- **Return tidy long rows** and let `scripts/schema.py` validate them.
- **Test `parse_lines` with hand-written `Line` objects** for the edge cases (page break, footnote marker, missing value), and test `parse` end to end on one committed fixture PDF per structural cohort, not one specimen for the whole series.

## 9. The provenance row

One row in `provenance.csv` per source artifact and parser run, never repeated on data rows:

| Column | Example |
|---|---|
| `source`, `vintage` | `county_sov`, `2009` |
| `source_url` | where the PDF was fetched |
| `retrieved_at` | UTC time of the fetch (from the fetch log, not file mtime) |
| `sha256` | hash of the original PDF |
| `extraction_method` | `text_layer` (PDFium lines or pdfplumber words), `table_lattice` (camelot lattice or pdfplumber `lines` strategy), or `table_stream` (camelot stream/network or pdfplumber `text` strategy) |
| `extraction_quality` | `clean` (reconciled, nothing to flag), `caveats` (reconciled with documented exceptions), or `degraded` (did not reconcile, or known errors remain) |
| `extraction_notes` | tool versions, non-default settings, producer, pages excluded, reconcile result |
| `parser_module` | `scripts.parsers.county_sov_2009` |

If some pages of the same file went through OCR, they are a separate extract with their own row and `extraction_method` (see [`extract-images.md`](extract-images.md)).

## When to leave this file

- **Pages triaged `scanned`, `ocr_layer` or `bad_text_layer`:** go to [`extract-images.md`](extract-images.md). Keep this file's reader for the born-digital pages of the same document.
- **Layout defeats rules** (multi-column reports, nested headers, sidebars, tables inside narrative): use the Docling standard pipeline from [`extract-documents.md`](extract-documents.md), which reads the text layer, then check every extracted number against the PDFium or pdfplumber characters inside its box. Where they disagree, the text layer wins.
- **Don't send a born-digital PDF to a vision model or a hosted parser as a first step.** Most of them rasterize the page and re-read pixels, which turns an exact problem into a probabilistic one.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| pdfplumber returns no text, but the PDF shows text | pdfminer can't parse this file's structure | Read it with PDFium; keep pdfplumber only for pages where both agree |
| Text comes out as garbage glyphs | Broken font-to-Unicode mapping | Try the other reader; if both fail, OCR the page and mark it `degraded` or `caveats` |
| `find_tables` / `extract_table` finds nothing | No table detected | Crop to the table region; try a different strategy or camelot lattice; re-check triage |
| One column always empty | A header overlaps a rule and the column was split | `explicit_vertical_lines` from `page.lines` |
| A digit missing from narrow cells | Text grouping drops characters | Lower `text_tolerance`; rebuild from `page.chars` |
| Duplicate header rows mid-table | Continuation pages repeat the header | Drop by exact match on the header text |
| `1,2341` where the page shows `1,234¹` | Superscript footnote glued to the number | Split by character size; move the marker to `note` |
| Coordinates off on some pages | Rotation or a non-zero media box | Normalize at the reader boundary; record rotation in triage |
| camelot reports 100% accuracy but values are wrong | Grid found, cells misassigned | Reconcile against printed totals; accuracy is not correctness |
| A whole vintage parses to zero or one row | Layout changed; rules no longer match | Fail on empty output; read the unparsed-line count |

## What to write in the AGENTS.md

- The per-page triage result for each source and vintage, the thresholds used, and the reader chosen for each class.
- Tool versions (pypdfium2, pdfplumber, pdfminer.six, camelot) and every non-default setting: `table_settings`, tolerances, explicit lines, camelot flavor.
- Per-vintage quirks: merged cells, footnote markers, multi-page stitching rules, printed folio versus PDF page, redacted regions found.
- What reconciles against which printed totals, and any documented scope differences.

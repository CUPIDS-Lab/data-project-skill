# Extract: layout pipelines and structured documents (HTML, XML, JSON, DOCX)

This file covers two jobs in Outline section 3 (Extract). The first is **unified layout pipelines** (Docling, Marker, MinerU, Unstructured and others) for documents whose layout defeats per-format tools, or for mixed corpora where one converter beats ten. The second is **structured documents already on disk**: HTML, XML, JSON and DOCX/RTF, each with its own calmer toolchain. Fetching pages is in [`extract-web.md`](extract-web.md); pulling from APIs, dashboards and map layers is in [`extract-api.md`](extract-api.md).

A born-digital PDF should not start here. Its text layer is ground truth, and [`extract-pdf.md`](extract-pdf.md) reads it exactly. Most vision-model parsers rasterize every page and re-read pixels, ignoring the text layer, which turns an exact problem into a probabilistic one. Come here from `extract-pdf.md` only when its rule-based readers can't recover the layout, and then check every number against the text layer.

## Contents

- [1. Unified layout pipelines](#1-unified-layout-pipelines)
- [2. Reading the benchmarks](#2-reading-the-benchmarks)
- [3. Pipeline or per-format tool?](#3-pipeline-or-per-format-tool)
- [4. HTML](#4-html)
- [5. XML](#5-xml)
- [6. JSON](#6-json)
- [7. DOCX, RTF and other narrative formats](#7-docx-rtf-and-other-narrative-formats)
- [8. Output and provenance](#8-output-and-provenance)
- [Common failure modes](#common-failure-modes)
- [What to write in the AGENTS.md](#what-to-write-in-the-agentsmd)

## 1. Unified layout pipelines

These tools take a PDF (and often DOCX, PPTX, HTML or images) and return a document model with reading order, headings, tables and figures. They differ most in what they keep for provenance: whether each block keeps a page and a box, and whether they read the text layer or re-read pixels. Sources below were checked on 2026-10-25.

| Tool | License | Runs on | Reads the text layer? | Finest box | Notes |
|---|---|---|---|---|---|
| [Docling](https://github.com/docling-project/docling) | MIT (code); models licensed separately (GraniteDocling Apache-2.0) | CPU; GPU faster | **Yes**, in the standard pipeline; OCR is pluggable and can be turned off | block: `prov` with `page_no`, `bbox` and `coord_origin`, plus `charspan`, in its lossless JSON ([data model](https://docling-project.github.io/docling/concepts/docling_document/)) | Markdown and HTML exports drop the boxes; keep the JSON. Needs Python 3.10 or later since 2.70. The VLM pipeline (GraniteDocling) rasterizes and inherits VLM nondeterminism |
| [Marker](https://github.com/datalab-to/marker) | Code Apache-2.0; weights modified OpenRAIL-M, free below USD 5M funding or revenue | GPU recommended; CPU "fast" mode | Partly: OCR via Surya where needed (not re-verified) | block polygons in its JSON tree | `--use_llm` merges tables across pages and fills forms by calling a hosted LLM, which adds a nondeterministic dependency and an upload |
| [MinerU](https://github.com/opendatalab/MinerU) | MinerU Open Source License (Apache-2.0 plus extra conditions; read them before adopting) | CPU tiers via ONNX and llama.cpp; NVIDIA for the full install | Not in its VLM backend (MinerU2.5 reads page images); check the backend you run | block | Strong on tables in its own reports; Markdown, HTML, LaTeX, DOCX and content-list JSON |
| [PP-StructureV3](https://github.com/PaddlePaddle/PaddleOCR) | Apache-2.0 | CPU or GPU | No: OCR-based | **table cell**, line, character | The only open option with cell-level boxes; see [`extract-images.md`](extract-images.md) |
| [Unstructured](https://github.com/Unstructured-IO/unstructured) (open-source library) | Apache-2.0 | CPU | Yes for text PDFs; `hi_res` adds layout detection and Tesseract | element coordinates in `hi_res` (per its docs; not re-verified) | Typed elements (Title, NarrativeText, Table). The vendor rates the open library well below its hosted API. **Telemetry is on by default**; set `DO_NOT_TRACK=true` |
| [Kreuzberg](https://github.com/kreuzberg-dev/kreuzberg) | MIT (not re-verified for 2026) | CPU; Rust core with bindings for many languages | Yes (PDFium) | limited | Breadth across many formats for bulk text, not layout depth |

Docling with OCR off, keeping the boxes:

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

opts = PdfPipelineOptions(do_ocr=False)          # born-digital: use the text layer only
converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
doc = converter.convert("data/original/agency/2024/plan.pdf").document
doc.save_as_json("data/original/agency/2024/_parsed/docling/plan.json")   # lossless; keeps prov

for table in doc.tables:
    df = table.export_to_dataframe(doc=doc)
    prov = table.prov[0]                                     # page_no, bbox, charspan
    height = doc.pages[prov.page_no].size.height
    box = prov.bbox.to_top_left_origin(page_height=height)   # canonical: points, top-left
    print(prov.page_no, (box.l, box.t, box.r, box.b), df.shape)
```

After any pipeline run on a born-digital file, collect the PDFium or pdfplumber characters inside each numeric cell's box and compare them with the pipeline's value. If they agree, record that the text layer confirmed it; if not, the text layer wins and the disagreement is logged. This check is cheap, deterministic and catches digit errors. Cache the pipeline's raw JSON as a derived original (see the audit discipline in [`extract-images.md`](extract-images.md)) and pin its version, because block segmentation changes between releases.

For research background on how document understanding got here (layout-aware pretraining, OCR-free models, specialist parser VLMs), [harrytea/Awesome-Document-Understanding](https://github.com/harrytea/Awesome-Document-Understanding) (updated 2026-10-24) is a maintained paper list. It is a reading list, not a tool guide: it has no licenses, benchmarks or library comparisons.

## 2. Reading the benchmarks

Vendors cite three benchmarks. None settles which tool is right for civic tables:

- **olmOCR-Bench** ([dataset card](https://huggingface.co/datasets/allenai/olmOCR-bench)): about 1,400 PDFs and 7,000 unit tests, nearly half on math. Its public leaderboard is labeled experimental and is mostly self-reported. The "Old Scans" category, closest to scanned FOIA material, is the weakest for every system: in OXR's own comparison the best open model reaches about 59%, against 85–99% on clean pages.
- **OmniDocBench** (v1.6): heavily Chinese and English academic, textbook and financial pages. Each major version changed both the pages and the matching, so scores across versions can't be compared.
- **DocParsingBench** ([repo](https://github.com/SoMarkAI/DocParsingBench)): 1,400 pages from five industries, scored on Markdown only, with tables 20% of the score. It is built and published by SoMark, whose own model (OXR) ranks first on it.

Common to all three: the results are self-reported and selective (peer numbers are often copied from model cards rather than rerun, and vendors publicly dispute rankings); and **no benchmark scores page-region provenance**, numeric accuracy on government tables, run-to-run stability or behavior on redactions. Use benchmarks to shortlist two or three tools, then decide on 20–50 hand-keyed pages from your own corpus.

## 3. Pipeline or per-format tool?

| Need | Use |
|---|---|
| One specific table, reproducibly, from a born-digital PDF | `extract-pdf.md` (PDFium, pdfplumber, camelot) |
| Layout-rich born-digital PDF (multi-column reports, sidebars, nested headers) | Docling standard pipeline with OCR off, then the text-layer cross-check |
| Scanned or degraded pages | [`extract-images.md`](extract-images.md) (OCR, PP-StructureV3, vision-model parsers with a manifest) |
| Narrative text from a large mixed corpus (PDF, DOCX, PPTX, HTML), no figures to cite | Docling or Kreuzberg for bulk conversion; record the tool and version |
| A precise selector on HTML, or an XPath on namespaced XML | per-format tools (sections 4–5) |
| Key-value fields from forms | a forms-capable parser or hosted forms API, subject to the gates in `extract-images.md` |
| Questions answered over a corpus | out of scope: build the dataset here, then let a separate retrieval layer read the liberated data, not the originals |

## 4. HTML

Agency reports rendered as pages, FOIA logs in `<table>` form, legislative records with one item per `<div>`. This section assumes the HTML is already saved under `data/original/` (fetching is in `extract-web.md`).

**`pandas.read_html` for real `<table>` elements.** The first thing to try when the page has a `<table>` tag. It needs `lxml` (and `html5lib` for messy markup).

```python
from io import StringIO
from pathlib import Path

import pandas as pd

html = Path("data/original/agency/2024/report.html").read_text(encoding="utf-8")
tables = pd.read_html(StringIO(html), match="Statement of Vote")   # list of DataFrames
df = tables[0]
```

Pass literal HTML wrapped in `StringIO` (recent pandas deprecates raw strings). Refinements: `header=[0, 1]` for stacked headers (then flatten the MultiIndex), `skiprows=` for title rows, `match=` to pick a table by its text, and `converters=` or `dtype` handling afterward for ID columns (`read_html` infers numbers and strips leading zeros). It does not understand `<div>` layouts, nested tables, or anything rendered by JavaScript.

**`selectolax` for layout-as-tables.** When rows live in `<div>` or `<li>` blocks, use a real parser. [`selectolax`](https://github.com/rushter/selectolax) is fast, uses CSS selectors, and tolerates malformed HTML.

```python
from selectolax.parser import HTMLParser

tree = HTMLParser(html)
rows = []
for card in tree.css("div.report-card"):
    title = card.css_first("h3.title")
    link = card.css_first("a.download")
    rows.append({
        "title": title.text(strip=True) if title else None,
        "url": link.attributes.get("href") if link else None,
    })
```

Check for `None` before calling `.text()`: a selector that matches on most pages but not all is a common crash. XPath via `lxml` is the fallback for ancestor, sibling or attribute queries that CSS can't express; BeautifulSoup is fine in projects that already use it. Commit a saved copy of each layout variant as a test fixture so a redesign becomes a test failure, and record the load-bearing selectors in `AGENTS.md`. For provenance, a value's region is its URL plus selector (and the saved file's hash).

## 5. XML

XML is structured by design, but files are either tiny (feeds, sitemaps) or very large (agency dumps, regulatory filings). The tool follows the size.

**Small documents:** `pd.read_xml("data/original/feed.xml", xpath="//entry")` returns one row per matched element. Pass `namespaces={"ns": "http://..."}` and use `//ns:entry` when the root declares a default namespace; forgetting namespaces is the most common cause of a query that returns nothing.

**Large documents:** stream with `lxml.etree.iterparse` and free memory as you go.

```python
from lxml import etree

rows = []
for _, elem in etree.iterparse("data/original/big.xml", events=("end",), tag="record"):
    rows.append({"id": elem.findtext("id"), "value": elem.findtext("value"), "agency": elem.get("agency")})
    elem.clear()                                   # free the parsed subtree
    while elem.getprevious() is not None:          # and the siblings already processed
        del elem.getparent()[0]
```

Both memory calls matter: without them `iterparse` still builds the whole tree. For very large files, write rows in batches to Parquet with `pyarrow.parquet.ParquetWriter` instead of accumulating a list. Useful XPath patterns: `//report[@status='final']`, `//*[contains(text(), 'Total')]`, `/root/level1/level2`.

## 6. JSON

JSON files on disk (portal exports, document-store dumps) are the friendliest input. For JSON that comes from an API (paging, rate limits, caching raw responses), see [`extract-api.md`](extract-api.md).

```python
import json
from pathlib import Path

import pandas as pd

data = json.loads(Path("data/original/records.json").read_text(encoding="utf-8-sig"))  # tolerates a BOM

# Nested records: one row per inner item, carrying parent fields along.
filings = pd.json_normalize(
    data,
    record_path="filings",
    meta=["id", ["agency", "name"], ["agency", "code"]],
    sep=".",
)

# JSON Lines: one record per line.
df = pd.read_json("data/original/records.jsonl", lines=True, dtype={"id": str})
```

`record_path` points at the nested list that becomes rows; `meta` lists parent fields to copy onto each row. Inspect `pd.json_normalize(data)` without a path first to find which column holds lists. `max_level` caps how deep dotted expansion goes. Keys missing from some records become NaN columns, which is correct but easy to miss. For very large JSONL, read line by line and write Parquet in batches, as for XML.

## 7. DOCX, RTF and other narrative formats

Convert proprietary narrative formats to Markdown first, then parse the Markdown with the same rules you would use for HTML. [Pandoc](https://pandoc.org/) is the standard converter; Docling also reads DOCX and PPTX directly.

```python
import subprocess
from pathlib import Path

src = Path("data/original/agency/2024/report.docx")
out = Path("data/original/agency/2024/_converted/report.md")    # a derived file; the .docx stays as fetched
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["pandoc", "-f", "docx", "-t", "gfm", "-o", str(out), str(src)], check=True)
```

Two failure modes recur. DOCX tables can lose their structure in conversion; then read the OOXML directly (the file is a ZIP of XML; tables are `<w:tbl>` elements) or use `python-docx`. Older RTF files often use legacy encodings (CP1252, Mac Roman); record the encoding in the provenance notes.

**Revision history is provenance.** DOCX tracked changes and comments (`<w:ins>`, `<w:del>`, `<w:comment>`), PDF incremental updates and RTF revision marks carry who changed what and when. Usually the final text is the data and the history is noise, but sometimes the history is the story (a leaked draft, a contested clause, a dissenting reviewer's comment). When a source carries an audit trail, extract it to `data/audit/revision_history/<source>/<vintage>.json` rather than flattening it into the processed data, or at least note in the data dictionary that it exists and where the raw file is. Editor names in revision history are personal data; apply the same sensitivity gate as any other personal field.

## 8. Output and provenance

Each source lowers to the project's canonical tidy table through `scripts/parsers/<source>_<vintage>.py`, validated by `scripts/schema.py`. Keep large originals in their native format; if they are too big to commit, keep them outside git with the hash in `data/original/manifest.json` and the URL in `provenance.csv`.

One row in `provenance.csv` per source artifact and parser run, with `extraction_method` set to `layout:<tool>` (`layout:docling`, `layout:marker`, `layout:mineru`) for pipeline output, `text_layer` for HTML, XML, JSON and DOCX parsed directly, or `vlm:<model>@<revision>` when a pipeline's vision model produced the values; and `extraction_quality` set to `clean`, `caveats` or `degraded`. Put the tool version, pipeline options (OCR on or off) and the text-layer cross-check result in `extraction_notes`.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Pipeline output has a wrong digit the PDF doesn't | The pipeline re-read pixels (OCR or VLM stage on) | Turn OCR off for born-digital files; cross-check against the text layer |
| Boxes missing from the output | Exported Markdown or HTML | Save and parse the lossless JSON |
| Boxes don't line up with the page | Mixed coordinate origins or render pixels | Convert to points, top-left origin, at the parser boundary |
| Results change after a dependency update | Block segmentation changed between releases | Pin the version; rerun golden pages on any bump |
| `pd.read_html` returns `[]` | No `<table>` element | `selectolax` on the real structure |
| Leading zeros vanish from IDs after `read_html` | Type inference | Re-read IDs as strings; fix with `converters=` |
| XPath returns nothing that should match | Undeclared namespaces | Pass `namespaces=` |
| `iterparse` uses gigabytes | Missing `elem.clear()` and sibling deletion | Add both |
| `json_normalize` gives one row | `record_path` points at a key, not the list | Inspect without a path first |
| `UnicodeDecodeError` on JSON | BOM | `encoding="utf-8-sig"` |
| `css_first(...)` crashes the parser | Selector missing on some pages | Check for `None`; commit that page as a fixture |

## What to write in the AGENTS.md

- Which pipeline (if any) is used for which source and vintage, its version, its options (OCR on or off, VLM pipeline or not), and why the per-format tools weren't enough.
- Where the pipeline's raw JSON is cached, and the text-layer cross-check result.
- For HTML: the load-bearing selectors and the fixture that pins each layout variant. For XML: the record element and namespace declarations. For JSON: the `record_path` and `meta` used.
- Encodings, and any document whose revision history was preserved or deliberately ignored.

# Extract: HTML, XML, JSON, and proprietary documents

This part covers structured-document formats that aren't tabular but are usually trying to be: HTML pages with tables (or layout-as-tables), XML feeds and document formats (RSS, agency-specific schemas, GIS metadata), and JSON from APIs or document stores. The job is the same — recover a tidy long-form DataFrame — but the failure modes differ and the tooling is calmer. For *scraping* HTML pages (dynamic content, polite request rates, cached fetches), see [`extract-web.md`](extract-web.md); this part assumes you already have the document on disk or in a string.

## The document-understanding design space

A liberation project chooses among per-format parsers (the rest of this part) and *unified document extractors* (modern libraries that handle many formats end-to-end). **What civic data actually faces**, framed against the [awesome-document-understanding](https://github.com/tstanislawek/awesome-document-understanding) catalog of document-AI research:

| Document type the source is | Civic examples | Default approach |
|---|---|---|
| **Born-digital structured** — XML, JSON, RSS, EDGAR / USPTO XBRL filings | Agency XML dumps, open-data portals, regulatory filings | `lxml`, `pd.read_xml`, `pd.json_normalize` — sections below |
| **Born-digital narrative HTML** — clean DOM with `<table>` or `<div>` rows | Agency dashboards, FOIA case logs, legislative records | `pandas.read_html` for tables; `selectolax` for layout-as-tables — sections below |
| **Born-digital PDF with text layer** — selectable text, possibly with tables | Statements of vote, annual reports, budget books | `pdfplumber` / `camelot` — see [`extract-pdf.md`](extract-pdf.md) |
| **Scanned image PDF** — no text layer | Older Statements of Vote, scanned FOIA responses, faxed records | OCR via `tesseract` + `pdf2image`, or a VLM-based pipeline via `docling` |
| **Visually-rich documents** — layout *bears meaning* (a field's position on the page is part of its identity) | Invoices, applications, structured forms, agency cover sheets | `docling` (layout-aware) or a key-information-extraction model |
| **Mixed-media documents** — PDFs with embedded narrative + tables + footnotes + figures | Comprehensive plans, environmental impact statements, court opinions | `docling` for unified extraction with reading-order preserved; per-component decomposition if you need to attribute each row to a page region |

The awesome-document-understanding repo names additional research problems — *Key Information Extraction*, *Document Layout Analysis*, *Document Question Answering* — that civic-data work occasionally needs. The pragmatic rule: for QA-over-documents (asking natural-language questions of a corpus), step out of this skill's scope and into a RAG / agent layer that reads the *liberated* dataset, not the originals. The skill's job is to produce the clean structured input that QA layers consume.

## Modern unified extractors — when one tool is enough

Two libraries have emerged as the post-2024 defaults for "I want this document parsed end-to-end without writing per-format code":

- **[docling](https://github.com/docling-project/docling)** (LF AI & Data, IBM origin) — best-in-class for *PDF understanding*. Parses page layout, reading order, table structure, code blocks, formulas, image classification. Outputs the unified `DoclingDocument` representation with exports to Markdown, HTML, lossless JSON, and `DocTags` (an LLM-friendly intermediate). Native VLM support via [GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M) and other vision-language models. Supports PDF, DOCX, PPTX, XLSX, HTML, images, LaTeX, and several application-specific XML schemas (USPTO patents, JATS articles, XBRL financial reports). Ships an MCP server and integrations with LangChain / LlamaIndex / Haystack / Crew AI. Reach for `docling` when the source has complex layout, embedded code or formulas, multi-column reading order that matters, or when you want a markdown-or-JSON dump suitable for downstream RAG without writing per-format code.

- **[kreuzberg](https://github.com/kreuzberg-dev/kreuzberg)** — polyglot (Python / Rust / Node / WASM / Java / Go / C# / PHP / Ruby / Elixir / R / Dart / Kotlin / Swift) high-throughput extractor across 90+ formats. Rust core with PDFium + Tesseract / PaddleOCR. Includes a *code intelligence* mode with semantic chunking across 300+ programming languages. Faster than docling for bulk extraction at scale, less PDF-understanding depth. Reach for `kreuzberg` when the project is *bulk-extracting* a large heterogeneous corpus, when extraction needs to run from a non-Python service (the polyglot bindings are real), or when the source mix includes a lot of formats that don't fit one specialist tool.

**When to skip both and use per-format tools:** when you need fine control over what comes out — e.g., a specific table on page 7 with the exact column boundaries pinned by reproducible `explicit_vertical_lines`, or a precise XPath against a namespaced XML schema. Per-format tools (pdfplumber, lxml, selectolax) give you that control; docling and kreuzberg trade some of it for breadth. The decision tree:

```
Need one specific table or selector, reproducibly       → per-format tool
Need a markdown dump of a complex layout-rich PDF       → docling
Need bulk extraction across many heterogeneous formats  → kreuzberg
Need a layout-aware embedding for downstream RAG        → docling (export DocTags)
Need scanned-PDF text with no per-source tuning         → docling (VLM pipeline) or kreuzberg
Need structured key/value extraction from forms         → docling + a KIE prompt, or a dedicated KIE model
Need fine control over OCR config per source/vintage    → tesseract directly — see extract-images.md
```

The rest of this part covers the per-format tools that the right side of that tree calls into.

## HTML

The web's lingua franca, and a surprisingly common civic-data format: agency reports rendered as HTML pages, FOIA logs in `<table>` form, dashboards backed by data tables, legislative records with one bill per `<div>`. Two paths into HTML, in increasing order of complexity:

### `pandas.read_html` for clean `<table>` elements

The friendliest path. `pd.read_html` walks the document, finds every `<table>` element, and returns a list of DataFrames. It works astonishingly well for well-formed HTML tables and is the right first try whenever the source contains an actual `<table>` tag:

```python
import pandas as pd

tables = pd.read_html("https://example.gov/quarterly-report.html")
# tables is a list of DataFrames — one per <table> on the page
df = tables[0]
```

For local files, pass a path; for HTML strings, pass the string. `pd.read_html` requires `lxml` and `html5lib` for robust parsing; install both.

Common refinements:

- **Multi-row headers:** `pd.read_html(..., header=[0, 1])` for stacked headers; flatten the `MultiIndex` afterward as in the tabular part.
- **Skip rows:** `pd.read_html(..., skiprows=2)` for tables preceded by title rows.
- **Encoding:** `pd.read_html(..., encoding="utf-8")` if the page lies about its encoding via the HTTP header.
- **Specific table:** Use `match=` with a regex to pick the table by a string in its caption or contents: `pd.read_html(url, match="Statement of Vote")`.

What `pd.read_html` does *not* do:

- Recover meaning from CSS-styled layouts (`<div>`-as-tables; tables drawn with `<span>` and `display: grid`). For those, drop to a parser.
- Resolve nested tables sensibly. If a table contains another table in a cell, the result is ugly; reach for `selectolax` or `lxml`.
- Handle JavaScript-rendered content. The HTML must already be in the document; if it's injected by JS, use `playwright` per [`extract-web.md`](extract-web.md).

### `selectolax` for layout-as-tables and structured non-table content

When the data lives in `<div>` or `<li>` blocks — most modern agency dashboards, most "card grid" layouts — drop to a real HTML parser. [`selectolax`](https://github.com/rushter/selectolax) is the right default: it's an order of magnitude faster than BeautifulSoup, has a CSS-selector API that matches `querySelectorAll`, and handles malformed HTML gracefully.

```python
from selectolax.parser import HTMLParser

tree = HTMLParser(html_string)

rows = []
for card in tree.css("div.report-card"):
    rows.append({
        "title": card.css_first("h3.title").text(strip=True),
        "agency": card.css_first("span.agency").text(strip=True),
        "published": card.css_first("time").attributes.get("datetime"),
        "url": card.css_first("a.download").attributes.get("href"),
    })

df = pd.DataFrame(rows)
```

CSS selectors are usually the right vocabulary for civic-data scraping (developers writing public sites tend to use class names that mirror the data they're displaying — `.report-row`, `.agency-name`, `.fiscal-year`). XPath via `lxml` is the fallback when CSS isn't expressive enough; reach for it for ancestor/sibling queries or attribute predicates beyond CSS's reach.

`BeautifulSoup` is the older, more widely-known alternative. It's fine, just slower; if a project already uses it, no urgency to migrate.

### When the HTML page is really a table-with-CSS-styling

A common government-site pattern: a `<table>` element exists, but each row is split across multiple `<tr>` (one for the visible row, one for an expanded-detail row that JS toggles open), or the visible "rows" are actually `<div>` blocks styled to look like a table. Don't fight the HTML; treat the visible structure as the source of truth and assemble rows from the divs:

```python
rows = []
for row_div in tree.css("div.results-row"):
    cells = [c.text(strip=True) for c in row_div.css("div.cell")]
    if len(cells) == EXPECTED_NCOLS:
        rows.append(cells)
```

The fragility budget here is the page redesign. Commit a saved copy of the page HTML as a `tests/fixtures/` artifact, write a small parser test against it, and the redesign becomes a clear test failure rather than a silent regression.

## XML

XML is calmer than HTML — it's actually structured by design — but the documents tend to be either trivially small (RSS feeds, sitemaps) or alarmingly large (full agency document corpora, GIS metadata catalogs, regulatory filing repositories like SEC EDGAR). The tool choice tracks the size.

### Small documents: `pd.read_xml`

For shallow, well-formed XML with a clear repeated-record structure:

```python
import pandas as pd

df = pd.read_xml("data/original/feed.xml", xpath="//entry")
```

`pd.read_xml` (which uses `lxml` under the hood) returns one row per matched element and one column per child element or attribute. It works well for RSS, Atom, and most agency-flat-XML formats. Pass a custom `xpath` to pick out a specific record-level element.

### Large documents: streaming with `lxml.etree.iterparse`

Loading a multi-gigabyte XML into memory is not an option for many civic sources (SEC filings, full agency dumps). Stream:

```python
from lxml import etree

rows = []
context = etree.iterparse(
    "data/original/big.xml",
    events=("end",),
    tag="record",       # only fire events for <record> elements
)
for _, elem in context:
    rows.append({
        "id": elem.findtext("id"),
        "value": elem.findtext("value"),
        "agency": elem.get("agency"),  # an attribute
    })
    elem.clear()         # free the parsed subtree — critical for memory
    # Also clear preceding siblings to release their memory
    while elem.getprevious() is not None:
        del elem.getparent()[0]
```

The two memory-management calls (`elem.clear()` and the sibling-deletion) are not optional for large files. Without them, `iterparse` is still building the full tree as it goes; you just get a callback per element. With them, memory stays flat.

For very large documents, write rows to disk (CSV, Parquet) in chunks rather than accumulating them in memory:

```python
import pyarrow as pa
import pyarrow.parquet as pq

writer = None
buffer = []
BATCH = 100_000

for _, elem in context:
    buffer.append({"id": elem.findtext("id"), ...})
    elem.clear()
    if len(buffer) >= BATCH:
        table = pa.Table.from_pylist(buffer)
        if writer is None:
            writer = pq.ParquetWriter("data/processed/big.parquet", table.schema)
        writer.write_table(table)
        buffer.clear()

if buffer:
    table = pa.Table.from_pylist(buffer)
    writer.write_table(table)
if writer:
    writer.close()
```

### XPath patterns worth knowing

`lxml` and `pd.read_xml` accept XPath 1.0. A few patterns recur in civic data:

- **All elements anywhere:** `//element-name`
- **Direct children:** `/root/level1/level2`
- **By attribute:** `//report[@status='final']`
- **Text contains:** `//*[contains(text(), 'Total')]`
- **Namespaces:** `//ns:element` with a `namespaces={"ns": "http://example.org"}` argument. Namespace-heavy XML (SEC, NIEM-derived schemas) requires registering namespaces explicitly — there is no shortcut.

If the XML defines namespaces (declared via `xmlns` attributes on the root), every XPath query must address them. The most common failure mode in agency XML is forgetting this and getting empty results from a query that "should work."

## JSON

JSON is the friendliest input format and the most common output from APIs. Three patterns, in increasing order of structural awkwardness.

### Flat JSON arrays

When the source is a list of records with no nesting:

```python
import json
import pandas as pd

with open("data/original/records.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)
```

This is the happy path. Encoding gotchas don't really apply (JSON is UTF-8 by spec; if a file claims otherwise, the publisher made a mistake worth flagging).

### Nested JSON: `pd.json_normalize`

When each record contains nested objects or lists, [`pd.json_normalize`](https://pandas.pydata.org/docs/reference/api/pandas.json_normalize.html) is the workhorse:

```python
data = [
    {
        "id": "001",
        "agency": {"name": "DOE", "code": "DE"},
        "filings": [{"year": 2023, "amount": 1000}, {"year": 2024, "amount": 1200}],
    },
    # ...
]

# Flatten top-level objects with dot notation:
df = pd.json_normalize(data, sep=".")
# Columns: id, agency.name, agency.code, filings (still a list)

# Or, normalize an inner list to its own DataFrame, propagating parent fields:
filings = pd.json_normalize(
    data,
    record_path="filings",
    meta=["id", ["agency", "name"], ["agency", "code"]],
    sep=".",
)
# Columns: year, amount, id, agency.name, agency.code
```

`record_path` is the path into the nested list that becomes one row per inner record; `meta` is the parent fields to propagate. Both accept dot-style strings for shallow nesting and lists-of-strings for deeper nesting (`["agency", "name"]` means the parent's `agency.name`).

Two `json_normalize` gotchas:

- **`max_level`** caps the depth of dotted expansion. Default is None (expand everything); set to `1` if a deeply nested object would explode the column count.
- **Missing inner keys** in some records become NaN columns, which is correct but can surprise you when one row in 10,000 happens to have a key the others don't.

### JSON Lines: stream from disk

For large JSON exports — common in document-store dumps and log archives — the publisher usually emits JSON Lines (one record per line, no top-level array). Pandas reads this directly:

```python
df = pd.read_json("data/original/records.jsonl", lines=True)
```

For very large JSONL, stream:

```python
import json

with open("data/original/records.jsonl") as f:
    for line in f:
        record = json.loads(line)
        # process record incrementally
```

Combined with the Parquet writer pattern from the XML streaming section, JSONL → Parquet conversion is the standard way to handle big civic-data document dumps without ever loading them into memory.

### Pagination from APIs

Most public APIs paginate. Two patterns:

```python
import httpx

# Offset-based pagination
def paginate_offset(base_url, page_size=100):
    offset = 0
    with httpx.Client() as client:
        while True:
            r = client.get(base_url, params={"limit": page_size, "offset": offset})
            r.raise_for_status()
            batch = r.json()["results"]
            if not batch:
                break
            yield from batch
            offset += page_size

# Cursor-based pagination
def paginate_cursor(base_url):
    cursor = None
    with httpx.Client() as client:
        while True:
            params = {"cursor": cursor} if cursor else {}
            r = client.get(base_url, params=params)
            r.raise_for_status()
            data = r.json()
            yield from data["results"]
            cursor = data.get("next_cursor")
            if not cursor:
                break
```

Both should be paired with `requests-cache` (idempotent reruns) and a `tenacity` retry decorator (transient API failures). See [`extract-web.md`](extract-web.md) for the polite-request budget — the same etiquette applies to API consumption.

## Narrative documents in proprietary formats — DOCX, RTF, and the markdown-as-intermediate pattern

Agency reports, FOIA-released drafts, and legislative responses sometimes arrive as `.docx` or `.rtf` rather than PDF or HTML. The pattern that scales across all of them is to **pass through markdown as an intermediate representation** before the parser does anything domain-specific: the markdown form is plain text with predictable structural conventions (headings, lists, tables), the OOXML / RTF byte format is not. Pandoc is the canonical converter; the *principle* (proprietary narrative → markdown → tidy long via the same parser conventions used for HTML extraction) is format-agnostic and survives format-of-the-month churn.

```python
# Conceptual sketch. The point is the two-stage flow, not the specific tool.
import subprocess
from pathlib import Path

src = Path("data/original/agency/2024-report.docx")
md  = src.with_suffix(".md")
subprocess.run(["pandoc", "-f", "docx", "-t", "gfm", "-o", str(md), str(src)], check=True)
# md is now parseable by the same selectolax/regex/headings-and-tables pipeline
# you use for born-digital HTML.
```

Two recurring failure modes worth naming: (1) DOCX-embedded tables that lose row-column structure on conversion — fall back to direct OOXML inspection (the document is a ZIP of XML files; tables are `<w:tbl>` elements with predictable structure) when the markdown shape isn't faithful. (2) RTF documents from older agencies sometimes have legacy encodings (CP1252, Mac Roman) — pandoc's `--from rtf` flag handles the parse but document the encoding in `provenance.csv`.

### Forensic revision history as a first-class signal

DOCX, RTF, and PDF revision streams all carry metadata most consumers ignore — *tracked changes*, *comments*, *revision marks*, *editor identities*, *timestamps of each edit*. For most civic liberation work, the final visible text is the data and the audit trail is noise. But sometimes **the audit trail is the story**: an FOIA release where the redactions tell you what was sensitive; a leaked draft where the tracked changes reveal which clause an agency lawyer fought; an annotated policy document where the comments name the dissenting reviewer.

The generalizable principle: **when a source carries an audit trail in its native format, preserving that trail is part of provenance, not optional metadata.** Two concrete moves:

- **Extract the audit trail alongside the surface text.** For DOCX, that's `<w:ins>`, `<w:del>`, `<w:comment>` elements in the OOXML. For PDF, it's the revision objects in the trailer dictionary. For source repositories (some publishers FOIA-release git history), it's the commit log. The audit trail becomes a sibling artifact under `data/audit/revision_history/<source>/<vintage>.json` — never silently flattened into the processed CSV.
- **Document the existence even when not extracted.** A column in `docs/data-dictionary.md` *Known caveats* noting *"the source DOCX contains 47 tracked-change insertions by 'A. Smith (DOJ)' between 2019-03-14 and 2019-03-21; raw OOXML preserved in `data/audit/revision_history/`"* is enough to let a future researcher follow the lead. The forensic value of revision history compounds over time; the cost of preserving it is small.

The principle generalizes past DOCX: any format that distinguishes *displayed text* from *edit history* (PDF incremental updates, RTF revision marks, OOXML tracked changes, git commit logs, Wikipedia article histories) gets the same treatment.

## Choosing the output format

These document formats lower into the same canonical CSV/Parquet via `scripts/parsers/<source>_<vintage>.py`. The parser's job is to call the right library, recover the rows, return a DataFrame validated against `CanonicalLong` (see `references/data-modeling.md`).

For very large source documents (multi-GB XML, JSON dumps), keep the original on disk in its native format and write only the *processed* output to `data/processed/`. Don't try to commit the original to Git LFS unless the project genuinely needs versioned access to it — for most civic projects, the original is reproducible by re-fetching, and the sha256 in `data/original/manifest.json` plus the URL in `provenance.csv` is sufficient.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `pd.read_html` returns `[]` | Page has no `<table>` element (often `<div>`-as-table) | Drop to `selectolax` and target the actual structural classes |
| `pd.read_html` returns the table but cells are merged or missing | Multi-row headers or merged cells | Pass `header=[0, 1]` and flatten the MultiIndex; if that fails, drop to `selectolax` |
| XML query returns empty results that should match | Document uses XML namespaces; XPath doesn't address them | Register namespaces explicitly via `namespaces=` argument |
| `iterparse` is using gigabytes of memory | Forgot `elem.clear()` and the sibling-deletion | Add both; verify memory stays flat during the stream |
| `pd.json_normalize` returns one row when you expected many | `record_path` is wrong — pointing at a key rather than the nested list | Inspect with `pd.json_normalize(data)` (no path) first; identify the column that's a list, then re-normalize with that as `record_path` |
| JSON file claims `utf-8` but `json.load` raises `UnicodeDecodeError` | File has a BOM or is actually `utf-8-sig` | `json.loads(Path(p).read_text(encoding="utf-8-sig"))` |
| Selectolax's `css_first` returns `None` and the parser crashes | Selector matches nothing on some pages; assumed every page had the element | Check for `None` before `.text()`; commit a page where the element is missing as a fixture |
| API pagination loops forever | `next_cursor` returned but it's the same as the previous one | Detect repeat cursor and break; also bound by a max-pages safety limit |

---

## What to write in the AGENTS.md

- **Format and the load-bearing selector** (HTML) or root element / repeated record (XML, JSON).
- **Encoding** (HTML/JSON) and **namespace declarations** (XML) — the kind of detail that's invisible until it breaks.
- **API pagination style** — offset vs cursor, page size, rate limit, link to publisher's API docs if any.
- **Structural fragility** — which selectors / paths are load-bearing, where the pinning fixture lives.
- **Streaming requirements** — note when a parser uses `iterparse` or chunked JSONL because the document is too large to load.

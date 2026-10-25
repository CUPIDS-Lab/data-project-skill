# Extract: scans, photos, maps and computer vision

When the input is an image (a scanned PDF, a photographed page, a PNG or TIFF, a map, an exhibit), there are no characters to read; they have to be recovered by OCR or a vision model, and every recovered value is an estimate until something checks it. This file covers Outline section 3 (Extract) for image-based inputs: testing an embedded OCR layer, OCR engines, layout and vision-model parsers, hosted APIs, the audit discipline model-based extraction needs, and computer vision when the image itself is the dataset. Born-digital PDFs belong in [`extract-pdf.md`](extract-pdf.md); unified layout pipelines for mixed corpora are in [`extract-documents.md`](extract-documents.md).

## Contents

- [Install](#install)
- [1. Test any embedded OCR layer before trusting it](#1-test-any-embedded-ocr-layer-before-trusting-it)
- [2. Render and preprocess](#2-render-and-preprocess)
- [3. OCR engines](#3-ocr-engines)
- [4. Layout and vision-model parsers](#4-layout-and-vision-model-parsers)
- [5. Hosted OCR and document APIs](#5-hosted-ocr-and-document-apis)
- [6. Gates before any hosted upload](#6-gates-before-any-hosted-upload)
- [7. Guardrails for paid or hosted OCR](#7-guardrails-for-paid-or-hosted-ocr)
- [8. Audit discipline for model-based extraction](#8-audit-discipline-for-model-based-extraction)
- [9. The provenance row](#9-the-provenance-row)
- [10. Embedded images as evidence](#10-embedded-images-as-evidence)
- [11. Computer vision when the image is the dataset](#11-computer-vision-when-the-image-is-the-dataset)
- [Common failure modes](#common-failure-modes)
- [What to write in the AGENTS.md](#what-to-write-in-the-agentsmd)

## Install

For a one-off: `uv run --with pypdfium2 --with pytesseract --with pillow python ocr.py`, with the Tesseract binary from the system package manager (`apt install tesseract-ocr`, `brew install tesseract`). Render pages with `pypdfium2` (one wheel, no Poppler) rather than `pdf2image`. [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) is a separate install (`apt install ocrmypdf` or `uv tool install ocrmypdf`) and also needs Tesseract and Ghostscript. Vision-model parsers bring their own heavy dependencies and usually a GPU; install them in a separate environment from the pipeline and record the versions (section 8).

## 1. Test any embedded OCR layer before trusting it

Many scans arrive with text already on them: from the scanner, from the agency, from an archive (the Internet Archive adds its own), or from Acrobat. That layer was produced by an unknown engine at an unknown setting, and real projects have found layers that kept the words and lost the numbers, layers from mis-rotated pages, and Acrobat **ClearScan** copies, which replace the page image with synthesized fonts so that re-OCRing them only re-reads Acrobat's guess. Treat an embedded layer as one unverified reading, never as the text layer of a born-digital file.

Test it on a sample of pages from every batch, numbers first:

```python
"""Compare an embedded OCR layer's numbers with a fresh OCR of the same page image."""
import re
from collections import Counter
from pathlib import Path

import pypdfium2 as pdfium
import pytesseract

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers(text: str) -> Counter:
    return Counter(n.replace(",", "") for n in NUM.findall(text))


def layer_agreement(path: Path, pages: list[int], dpi: int = 300) -> list[dict]:
    out = []
    pdf = pdfium.PdfDocument(path)
    for p in pages:                                    # 1-based page numbers
        page = pdf[p - 1]
        embedded = numbers(page.get_textpage().get_text_bounded())
        fresh = numbers(pytesseract.image_to_string(page.render(scale=dpi / 72).to_pil()))
        shared = sum((embedded & fresh).values())
        out.append({
            "page": p,
            "embedded_numbers": sum(embedded.values()),
            "fresh_numbers": sum(fresh.values()),
            "agreement": round(shared / max(sum(embedded.values()), sum(fresh.values()), 1), 3),
        })
    pdf.close()
    return out
```

Then check the printed totals on those pages against the embedded layer's numbers. Use the layer only if its numbers agree with an independent reading and sum to the printed totals; otherwise ignore it and OCR the page images yourself. Record the test and its result in the Survey note. If the only copy you have is a ClearScan or otherwise re-rendered file, ask for the original scan.

## 2. Render and preprocess

Image quality matters more than the engine. Render PDF pages from the original at 300 DPI (400 for small type) with `page.render(scale=dpi / 72).to_pil()`, and keep the renders as derived files, never in place of the original.

- **Rotation and skew.** Detect whole-page rotation first (`tesseract --psm 0` reports orientation), then deskew; even 1° costs accuracy. [`deskew`](https://pypi.org/project/deskew/) or `cv2.minAreaRect` on the content contour.
- **Binarize** with Otsu (`cv2.threshold`) or `cv2.adaptiveThreshold` for uneven lighting; **despeckle** with `cv2.medianBlur` before thresholding.
- **Crop to content** so margins and punch holes don't become text.
- **Record every step and its parameters**; they are part of the parser manifest (section 8).

Enhancement models (super-resolution, deblurring) invent detail. Use them only on a working copy, flag the output as enhanced, and never treat invented detail as a reading.

## 3. OCR engines

Classic OCR engines return words or lines with boxes and confidences, and run deterministically on CPU once versions are pinned. Start here for typed tables on decent scans.

| Engine | When | Boxes | Notes |
|---|---|---|---|
| [Tesseract](https://github.com/tesseract-ocr/tesseract) via `pytesseract` | The default for typed pages | word, with confidence | Tune `--psm` (6 for a uniform block, 11 for sparse text) and use a digit whitelist for numeric tables |
| [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) | Make a scanned PDF searchable, then extract it like a born-digital one | word (in the added layer) | Writes a new PDF with a text layer; the original stays untouched. The added layer is still OCR: provenance says `ocr:tesseract`, not `text_layer` |
| [PaddleOCR 3.x](https://github.com/PaddlePaddle/PaddleOCR) (PP-OCR, PP-StructureV3) | Degraded, rotated or multilingual scans; tables needing cell boxes | line, character, and table-cell (PP-StructureV3) | Apache-2.0; 3.7.0 released 2026-06-11. PP-StructureV3 is the only open option with cell-level boxes, which suits page-and-region provenance |
| [RapidOCR](https://github.com/RapidAI/RapidOCR) | PaddleOCR's models on ONNX Runtime, light install | line | Used by camelot's optional `ocr` extra |
| [docTR](https://github.com/mindee/doctr) | A clean Python API for a sustained OCR service | word | Detection and recognition models; Apache-2.0 |
| [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Quick multilingual text from many images | line | Least tunable |
| [Surya](https://github.com/datalab-to/surya) | Reading order and line detection | line | Now mostly used inside Marker and Chandra (section 4) |

Tesseract with positions, for tables:

```python
import pytesseract
from pytesseract import Output

data = pytesseract.image_to_data(image, lang="eng", config="--psm 6", output_type=Output.DATAFRAME)
data = data.dropna(subset=["text"])            # columns: left, top, width, height, conf, text, ...
# Cluster on `top` (within a tolerance) to rebuild rows and on `left` to rebuild columns.
# Box units are pixels of this render: points = pixels * 72 / dpi.
```

Keep low-confidence words rather than filtering them out silently: send them to the review queue (section 8).

## 4. Layout and vision-model parsers

Between 2025 and 2026 document parsing moved from "layout model + OCR + table model" pipelines to small vision-language models (VLMs) trained to turn a page image into Markdown or JSON. They read complex and degraded layouts better than classic OCR, but they hallucinate plausible values, they rasterize pages and ignore any text layer, and their output can change from run to run. For provenance, the deciding axis is not accuracy but whether the tool keeps region boxes: decoupled or JSON-emitting designs keep block boxes; pure page-to-Markdown designs lose them.

As of October 2026 (sources checked 2026-10-25; benchmark scores are self-reported by each vendor unless noted):

| Tool | License | Local / hardware | Outputs | Finest box | Determinism | Cost |
|---|---|---|---|---|---|---|
| [PP-StructureV3](https://github.com/PaddlePaddle/PaddleOCR) (pipeline) | Apache-2.0 | CPU or GPU | Markdown, JSON | table cell, line, character | Deterministic (classic models) | Local compute |
| [PaddleOCR-VL-1.6](https://github.com/PaddlePaddle/PaddleOCR) (0.9B) | Apache-2.0 | GPU | Markdown, JSON | block | VLM: only with controls below | Local compute |
| [MinerU](https://github.com/opendatalab/MinerU) (MinerU2.5, 4.0 line) | MinerU Open Source License (Apache-2.0 plus extra conditions; read them) | CPU tiers via ONNX/llama.cpp; NVIDIA for full | Markdown, HTML, JSON content list | block | VLM stage needs pinning | Local compute |
| [OXR-1.0](https://github.com/SoMarkAI/OXR) (1.3B) | Apache-2.0 plus OXR terms: commercial use only below USD 2M funding and revenue, no competing hosted API | NVIDIA, 24 GB minimum, Linux | Markdown + JSON blocks | block, pixels of a 150-DPI render | `temperature=0` by default; still test | Local compute; its free hosted API is "not recommended in production" |
| [dots.mocr](https://github.com/rednote-hilab/dots.ocr) (about 3B; formerly dots.ocr) | MIT plus a separate dots.ocr license agreement; read both | One GPU with vLLM | One JSON with boxes, 11 categories, HTML tables | block | VLM | Local compute |
| [MonkeyOCR](https://github.com/Yuliang-Liu/MonkeyOCR) (v1.5, pro, v2) | Code Apache-2.0; v1 weights non-commercial; v2 (0.7B) announced Apache-2.0 | 8 GB GPU when quantized | Markdown, `middle.json` with blocks and relations | block | VLM | Local compute |
| [Chandra OCR 2](https://github.com/datalab-to/chandra) (about 4–5B) | Code Apache-2.0; weights modified OpenRAIL-M, free below USD 2M funding or revenue, no competing API | H100-class with vLLM | Markdown, HTML, JSON with layout | block (boxes confirmed for the hosted API only) | VLM | Local compute or Datalab's hosted API |
| [Marker](https://github.com/datalab-to/marker) | Code Apache-2.0; weights modified OpenRAIL-M, free below USD 5M | GPU recommended; CPU "fast" mode | Markdown, HTML, JSON block tree with polygons | block | `--use_llm` adds a hosted, nondeterministic LLM | Local compute or Datalab's hosted API |
| [olmOCR 2](https://github.com/allenai/olmocr) (7B) | Apache-2.0 | NVIDIA, 12 GB or more | Markdown, JSONL | none | VLM | Local compute |
| [LightOnOCR-2-1B](https://huggingface.co/lightonai/LightOnOCR-2-1B) / 3-4B | Apache-2.0 (2-1B) | GPU | ordered text, Markdown | none | VLM | Local compute |
| [GOT-OCR 2.0](https://huggingface.co/stepfun-ai/GOT-OCR-2.0-hf) | Apache-2.0 | GPU | text | none (accepts a box as input) | VLM | Useful to re-read one known crop |
| [Qwen3-VL](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) (general VLM) | Apache-2.0 (8B card) | GPU; 2B–235B | free text; HTML with `data-bbox` when prompted | block or line, normalized 0–1000 (verify the scale) | prompt-sensitive | Local compute |
| [Nougat](https://huggingface.co/facebook/nougat-base) | weights CC-BY-NC-4.0 | GPU | Markdown/LaTeX | none | prone to repetition and hallucination | Don't use for civic data |

What the benchmarks do and don't tell you. On olmOCR-Bench ([dataset card](https://huggingface.co/datasets/allenai/olmOCR-bench)), whose public leaderboard is mostly self-reported, the "Old Scans" category, closest to scanned FOIA material, is the weakest for every system: OXR's own table puts the best open models at about 33–59% there, against 85–99% on clean pages. No public benchmark scores numeric accuracy on government tables, whether a value is cited to the right region, or run-to-run stability. Use benchmarks to shortlist; decide with your own golden pages (section 8).

Which path, for image-based pages:

| Situation | Start with | Then |
|---|---|---|
| Typed tables, decent scan | Tesseract or OCRmyPDF, then the `extract-pdf.md` readers on the OCR'd file; or PP-StructureV3 for cell boxes | Printed-total checks; audit sample |
| Complex layout, degraded or mixed pages | A local VLM parser with block boxes (MinerU, PaddleOCR-VL, dots.mocr, OXR if its license fits), pinned and cached | A second reader (Tesseract or PP-OCR on each numeric cell's crop); disagreements to review |
| Narrative text only, nothing to cite by region | OCRmyPDF or olmOCR | Spot checks |
| Forms, checkboxes, handwriting | A hosted forms API if the gates allow (section 6); otherwise Chandra or PP-StructureV3 locally | Review every checkbox and handwritten field |
| Sensitive documents | Local tools only | Hosted use needs documented approval |

## 5. Hosted OCR and document APIs

Every option here uploads the document to a third party, and the model behind it can change without notice. List prices around October 2026, per 1,000 pages; confirm the live price before budgeting.

| Service | Boxes and confidence | Strengths | Price | Reproducibility |
|---|---|---|---|---|
| AWS Textract | word, line and cell geometry (normalized 0–1), per-block confidence | Tables, forms (key-value), checkboxes, handwriting | about $1.50 text; $15 tables; $50 forms; $65 both (secondary: [wring.co](https://wring.co/blog/aws-textract-pricing-guide)) | Versioned API; model changes without notice |
| Azure AI Document Intelligence | word, line and cell polygons (inches for PDF, pixels for images), confidence | Layout, prebuilt and custom models, handwriting | about $1.50 read; $10 layout; $30 custom (secondary sources) | Pin `api-version=` |
| [Google Document AI](https://cloud.google.com/products/document-ai/pricing) | normalized 0–1 polygons, confidence | Layout Parser, Form Parser | $10 layout; $30 forms ($20 above 1M a month) | Processor versions can be pinned |
| [Mistral OCR 4](https://mistral.ai/news/ocr-4) (2026-06-23) | per-block box and type, per-page and per-word confidence | Tables, signatures, 170 languages, JSON-schema extraction | $4 ($2 batch); Document AI $5 | Model named and dated; its benchmark rank is publicly disputed ([report](https://mind-verse.de/news/debatte-leistung-mistral-ocr-4-olmocrbench)) |
| [LlamaParse v2](https://developers.llamaindex.ai/llamaparse/general/pricing/) | optional layout extraction | Agentic tiers backed by LLMs | about $1.25 / $3.75 / $12.50 / $56 by tier | LLM tiers nondeterministic |
| Datalab (hosted Marker and Chandra) | blocks with polygons | Layout conversion; schema-constrained extraction | Check the vendor; schema-constrained extraction can cost far more per page, and unpredictably | Cache everything |
| [SoMark](https://docs.somark.ai/api-reference) (hosted OXR) | blocks with coordinates | Cross-page merge flags (off by default) | Not published | Response carries no model version; its client defaults to a mainland-China endpoint |
| Frontier LLM vision (Claude, Gemini, GPT) | Gemini returns 0–1000 boxes when prompted; Claude's PDF citations give pages, not regions (verify for current models) | Good narrative reading; weaker table structure than specialists | token-based | Models are deprecated on a schedule; output varies |

Use a frontier LLM as a second reader or adjudicator, not as the system of record for numbers. Real projects found that free local OCR (a PDFium render, rotation fix, Tesseract via OCRmyPDF) matched a paid layout conversion on accuracy; the paid service earns its cost only where a local reader demonstrably fails on your golden pages.

## 6. Gates before any hosted upload

Before any page leaves the machine, state the destination (vendor, region or endpoint, retention if known) and check the project's sensitivity and visibility decision from Outline section 1 (see `_shared/values-and-gates.md`). FOIA releases with personal data, sealed or juvenile records, partner data and anything private or embargoed default to local-only; a hosted run then needs a documented approval in the decision-log. Don't upload a sample "just to test" either: a test page is still an upload.

Record license limits in the Survey note: AGPL (PyMuPDF) matters if the pipeline is served; funding or revenue thresholds (OXR USD 2M, Chandra weights USD 2M, Marker weights USD 5M); non-commercial weights (MonkeyOCR v1, Nougat); no-competing-API clauses (OXR, Chandra). Most civic nonprofits sit under the thresholds, but grants and university hosting can change that. Hosted APIs add terms of service on data use and retention; link them.

## 7. Guardrails for paid or hosted OCR

Paid OCR fails expensively: a retry loop pays twice, a schema-constrained mode costs many times the base price, and a crash halfway through loses the pages already paid for. The guardrails real projects converged on:

- **Estimate, then confirm.** Nothing is sent until a dry run prints pages, mode and estimated cost, and a second explicit flag (`--yes`) confirms. Set a per-run cap and refuse to start a run that would exceed it.
- **Cache every paid page** keyed on the source hash, page number and configuration hash, and never call the service again for a cached key.
- **Keep a crash ledger.** Write a pending entry before each request and clear it after the response is cached, so a crash never causes a second payment for the same page.
- **Stop on spend limits.** An HTTP 402 or a quota error ends the run; it is not retried.
- **Log every request** (time, page, mode, request ID, cost) to an append-only JSONL file under `data/audit/`.
- **Line-buffer progress output** (`print(..., flush=True)` or `python -u`) so a long background run is visibly alive.

```python
"""Skeleton of a guarded hosted-OCR run. `client.submit` stands in for the vendor SDK."""
import hashlib
import json
from pathlib import Path

PRICE_PER_PAGE = 0.004        # from the vendor's live price page; record the date you checked
CAP_USD = 5.00


def run(pages: list[tuple[str, int, bytes]], config: dict, cache: Path, confirm: bool, client) -> None:
    cfg = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]
    todo = [(sha, n, img) for sha, n, img in pages
            if not (cache / f"{sha}-p{n:04d}-{cfg}.json").exists()]
    cost = len(todo) * PRICE_PER_PAGE
    print(f"{len(todo)} uncached pages, estimated ${cost:.2f} (cap ${CAP_USD:.2f})", flush=True)
    if cost > CAP_USD or not confirm:
        return                                            # dry run, or over the cap: send nothing
    ledger = cache / "_pending.json"
    for sha, n, img in todo:
        key = f"{sha}-p{n:04d}-{cfg}"
        ledger.write_text(json.dumps({"pending": key}))
        resp = client.submit(img, **config)
        if resp.status_code == 402:
            raise SystemExit("spend limit reached; stopping")
        resp.raise_for_status()
        (cache / f"{key}.json").write_text(resp.text)    # the cached response is an immutable derived original
        ledger.unlink()
        with (cache.parent / "ocr-requests.jsonl").open("a") as log:
            log.write(json.dumps({"key": key, "request_id": resp.headers.get("x-request-id")}) + "\n")
```

**Accept a value only when two independent readings agree.** A figure enters the dataset when a second reading confirms it: a second OCR engine, the text layer where one exists and passed section 1's test, the same figure printed in another document, or the page's own arithmetic (row and column totals pin it down). Everything else stays in a review queue and is never loaded silently. "Independent" means a different engine or source, not the same engine run twice and not a ClearScan copy.

**Printed totals are checksums.** Verify every OCR'd row against its printed row total and every column against its column total. A table that doesn't sum is wrong somewhere even if every cell looks right. Watch for known model fabrications: dollar values derived from printed percentages, chart bar heights returned as numbers, and blank or redacted cells "filled" with a plausible value.

## 8. Audit discipline for model-based extraction

A VLM or hosted parser is not a re-runnable pure function. Treat its output as a cached, hashed, derived original, and make the chain from original to tidy row reproducible by keeping that cache.

**Immutable cache of parser output.** Store the raw output (JSON, Markdown, and the manifest below) under `data/original/<source>/<vintage>/_parsed/<engine>/<config_hash>/`, keyed on the source file hash plus a configuration hash, and hash each file into the originals manifest. Never re-call a nondeterministic or paid parser on retry; reuse the cached artifact, and never pick up an adjacent or older cached result by name. The tidy CSV is then a deterministic function of the original, the cached parse and your parser code.

**Parser manifest**, one per extract, as a `manifest.json` beside the cached output:

- tool and version; `model_id` and `model_revision` (Hugging Face commit hash, or the vendor's model name and date), and the weights hash where available;
- inference engine and version (for example vLLM), container image digest, GPU type, and whether serving was batch-invariant;
- sampling settings (`temperature`, `top_p`, `max_tokens`) and a hash of the prompt or config; the layout-model version where the layout stage is pluggable;
- render DPI, preprocessing steps, and the native coordinate convention;
- hosted only: endpoint and region, API version, request IDs, and, if the vendor exposes no model version, a note saying so;
- status: `parsed`, then `verified` only after the reconcile and audit checks pass, or `partial` / `failed`, with a list of degradations (truncated output, repetition loops, pages skipped).

**Determinism controls.** For local VLMs use `temperature=0`, a fixed `max_tokens`, single-request or batch-invariant serving (vLLM's `VLLM_BATCH_INVARIANT=1`, which needs recent NVIDIA GPUs per the [vLLM docs](https://docs.vllm.ai/en/latest/features/batch_invariance/)) and a pinned GPU type; temperature 0 alone is not enough ([Thinking Machines, September 2025](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)). Then run the golden pages twice and diff. Detect truncated output and repetition loops and log them as degradations rather than accepting a short table. For hosted APIs assume drift; the cache is the only reproducibility guarantee.

**Normalize coordinates** at the parser boundary to PDF points, top-left origin, 1-based page (`x0, y0, x1, y1`): a render at D DPI converts with `points = pixels × 72 / D` (OXR: 150 DPI); Textract and Google use 0–1 of the page; Qwen-VL and Gemini 0–1000; Azure inches for PDFs. Say in the data dictionary which granularity applies (cell, line or block).

**Cross-check against a second reader.** For numeric cells, re-read each cell's crop with a different engine (Tesseract or PP-OCR, or GOT-OCR with a box input). Agreement allows a lower audit rate; disagreement goes to the review queue. Never resolve a disagreement by quietly majority-voting a third model; if you add one, record it.

**Human audit sample.** Stratify by source, vintage, page class and engine. For acceptance use the rule of three: with zero errors in *n* randomly sampled cells, the 95% upper bound on the error rate is about 3/*n*, so 60 clean cells bound it near 5% and 300 near 1%. Values that feed published totals or headlines get 100% review or are covered by reconciliation. Build the audit sheet automatically from the box citations (crop each sampled region from the original page and put it beside the value) and record each verdict in `data/audit/review-<date>.csv`. Report the measured error rate per engine in the provenance notes.

**Golden pages as a regression set.** Hand-key 20–50 pages from the actual corpus (expected cells and boxes) and commit them as fixtures. Rerun extraction against them on any change to tool version, model revision, prompt or configuration, score cell-exact match, and fail CI on regression. A bump is a new parser vintage: re-extract, diff against the previous output, and note the diff in `CHANGELOG.md`.

## 9. The provenance row

One row in `provenance.csv` per source artifact and parser run:

| Column | Values |
|---|---|
| `extraction_method` | `ocr:<engine>` (`ocr:tesseract`, `ocr:paddleocr`), `layout:<tool>` (`layout:pp-structurev3`, `layout:mineru`), `vlm:<model>@<revision>` (`vlm:olmocr-2@<revision>`), `cv:<model>`, or `manual` for hand transcription |
| `extraction_quality` | `clean` (two readings agree and totals reconcile), `caveats` (reconciled with a documented review queue or exceptions), `degraded` (unreconciled values remain, or the engine's measured error rate is material) |
| `extraction_notes` | path to the parser manifest, the embedded-layer test result, the audit sample size and errors found, the reconcile result |

plus the usual `source`, `vintage`, `source_url`, `retrieved_at`, `sha256` and `parser_module`. Hand-transcribed values carry a `source_id` (document, page, region) per value and `extraction_method = manual`.

## 10. Embedded images as evidence

Court filings, incident reports and FOIA archives often carry images that are the evidence: exhibits, photographs, signatures, maps. If the text refers to an image, the image is part of the dataset. Extract it (pdfplumber's `page.images` gives boxes; `pypdfium2` page objects of type image can be extracted with `obj.extract()`), hash it, store it under `data/original/<source>/<vintage>/_images/<page>-<index>.<ext>`, and add a sidecar `images.csv` keyed on `(source, vintage, page)` so a processed row can join back to the exhibit it cites. Record an images-extracted count per extract so the audit notices when a refresh suddenly stops producing images.

## 11. Computer vision when the image is the dataset

Sometimes the photograph, satellite tile or video is the source and the deliverable is a measurement derived from pixels: a count, a position, a time, an authenticity flag. The New York Times R&D group's [computer vision for journalism agenda](https://rd.nytimes.com/projects/computer-vision-vision/) maps the tasks that show up in reporting. Every CV-derived value is a model's estimate, not a reading: it carries a confidence, `extraction_method = cv:<model>` with the model version in the manifest, and validation against a hand-labeled sample, reported as precision and recall.

| CV task | What you liberate | Methods and tools | Civic caveat |
|---|---|---|---|
| Satellite and aerial imagery | Counts, footprints and change per tile and date | Tile the raster, then a detector (YOLO, Detectron2) or segmenter ([Segment Anything](https://github.com/facebookresearch/segment-anything)); [TorchGeo](https://github.com/microsoft/torchgeo), [Raster Vision](https://github.com/azavea/raster-vision) | Georeference every detection (latitude and longitude plus the tile's CRS), never pixel x/y; validate against hand-counted tiles |
| Crowd counting | An attendance estimate with a range | Density-estimation models for dense crowds, detection for sparse ones | Report a range with the method; estimates are politically contested |
| Archive transcription at scale | Text and fields from newspaper or document archives | Sections 3–4, with article and column segmentation first | Audit transcription accuracy per vintage |
| Syncing found video | A timeline and camera positions from several clips | Audio and visual alignment; structure-from-motion ([COLMAP](https://colmap.github.io/)) | Forensic reconstruction; record every assumption |
| 3D reconstruction | A 3D model from photos or video | Photogrammetry, NeRF, Gaussian splatting | Interpretive; keep the source frames as the originals |
| Pose and motion from uncalibrated video | Positions, speeds, angles per frame | Pose estimation ([MediaPipe](https://github.com/google-ai-edge/mediapipe), MMPose) plus homography | Relative, not absolute, unless calibrated against a known in-frame reference |
| Synthetic-media checks | An authenticity signal before you build on a source | Read content-provenance metadata ([C2PA](https://c2pa.org/)); detectors are weak and decay fast | A verification gate upstream of extraction, not proof |
| Enhancement | A more legible working copy | Super-resolution, colorization, frame interpolation | Invents detail: flag it, never cite it as evidence, never overwrite the original |

Face recognition and other biometric identification, and any handling of possibly synthetic media about real people, are hard privacy and CARE gates, not defaults: decide whether to run the model before deciding how, and record the decision (see `_shared/values-and-gates.md` and `_shared/responsible-data.md`).

**Verifying and locating source media.** Before building on a photo or video, establish where and when it was captured and whether it is recycled. Bellingcat's [Online Investigation Toolkit, image and video category](https://bellingcat.gitbook.io/toolkit/categories/image-video) indexes the tools by job: reverse image search (Google Lens, Yandex, TinEye, Bing), EXIF and metadata viewers (easily stripped or forged, so a GPS tag is a lead, not proof), geolocation and chronolocation (landmarks, shadows, satellite overlays), and video keyframe and forensics tools such as [InVID-WeVerify](https://www.invid-project.eu/). Record what each check established in `extraction_notes`.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Embedded text reads fine but the numbers are wrong | The scan's OCR layer kept words and lost digits | Run the section 1 test; re-OCR from the page images |
| Re-OCR "confirms" the embedded layer exactly | The file is a ClearScan or re-rendered copy, not an independent image | Get the original scan; don't count it as a second reading |
| "rn" read as "m", 0/O and 1/l confusion | Small type, low resolution | Render at 400 DPI; digit whitelist; try PaddleOCR |
| Rows fragmented or out of order | Wrong page segmentation mode, skew, multi-column | `--psm 6` or `11`; deskew; a layout parser |
| VLM table looks perfect but doesn't sum | Hallucinated or shifted values | Printed-total checks; second reader on numeric cells |
| A cell shows a number where the page shows a percentage or a bar | Model derived or invented the value | Two-reading rule; review chart and percentage regions by hand |
| Output differs between two identical runs | Batching or sampling nondeterminism | Batch-invariant serving, temperature 0, pinned GPU; cache the first run |
| A long table is silently short | Output token cap or repetition loop | Detect truncation; split the page; log a degradation |
| The OCR bill doubled | Retries re-sent cached pages | Cache by key; crash ledger; estimate-then-confirm |
| CV counts look plausible but are wrong | No ground truth | Hand-label a sample; report precision and recall |

## What to write in the AGENTS.md

- The embedded-layer test result per batch, and whether the layer is used or ignored.
- The engine or model per source and vintage, its version or revision, render DPI, preprocessing, and the settings that matter (PSM, whitelist, prompt hash, sampling).
- Where the parser cache and manifests live, and the rule that paid or nondeterministic parsers are never re-called for a cached key.
- For hosted services: the approval in the decision-log, the endpoint and region, the cost cap, and the license or terms limits.
- The two-reading rule as applied (which second reader), the printed totals used as checksums, the review queue location, the audit sample size and measured error rate, and the golden-page set.
- For computer vision: the model and version per task, the hand-labeled validation sample and its precision and recall, the georeferencing or calibration scheme, and any biometric or synthetic-media decision.

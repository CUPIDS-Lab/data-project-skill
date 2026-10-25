# Extract: images, OCR, and computer vision

When the input is image-based rather than a text layer — scanned PDFs, photographed documents, image files (PNG/TIFF/JPG), maps, exhibits, signatures — extraction can't read characters off the page; it has to recover them. The path is **rasterize → preprocess → OCR (or a vision model) → handle the output as text**. Quality varies dramatically by document and is dominated by input image quality, so preprocessing matters more than the engine choice. This is the **Level 0** reference for the image/OCR/CV branch; the born-digital PDF path is in [`extract-pdf.md`](extract-pdf.md), and multi-format unified extractors (docling/kreuzberg) are in [`extract-documents.md`](extract-documents.md#modern-unified-extractors--when-one-tool-is-enough).

This file covers two related jobs. The first is **OCR** — recovering text from a document that happens to be an image (most of the sections below). The second is **computer vision when the image itself is the dataset** — counting objects in a satellite tile, estimating a crowd, reading measurements off a video, or flagging that a source image was synthetically generated. There the deliverable isn't transcribed text but *structured measurements derived from pixels*. See [Computer vision when the image is the dataset](#computer-vision-when-the-image-is-the-dataset).

## When the input is image-based

Run the same triage you'd run on any PDF: is there a usable text layer? Open the file in a viewer and try to **select and copy text** from it. If you get the content back, you have a born-digital document — use the path in [`extract-pdf.md`](extract-pdf.md). If you get nothing or garbled glyphs, or the input is a raster image file (PNG/TIFF/JPG) to begin with, the text doesn't exist as characters yet and you're here: rasterize each page (if it's a PDF), preprocess, and OCR.

## OCR engines — tesseract and its alternatives

When the PDF has no text layer (or a corrupt one): rasterize each page, OCR it with [Tesseract](https://github.com/tesseract-ocr/tesseract), then handle the output as text. Quality varies dramatically by document and is sensitive to preprocessing.

### Minimal idiomatic use — tesseract

```python
import pdf2image  # requires poppler
import pytesseract
from PIL import Image

images = pdf2image.convert_from_path("data/original/scan.pdf", dpi=300)
text_by_page = [pytesseract.image_to_string(img, lang="eng") for img in images]
```

For tabular layout recovery, use `image_to_data` and reconstruct rows by clustering on the `top` coordinate:

```python
import pytesseract
from pytesseract import Output

data = pytesseract.image_to_data(image, output_type=Output.DATAFRAME, lang="eng")
# data has columns: level, page_num, block_num, par_num, line_num, word_num,
# left, top, width, height, conf, text
data = data.dropna(subset=["text"]).query("conf > 30")
```

Cluster on `top` (within tolerance) to recover rows; cluster on `left` to recover columns.

OCR'd output should always be **flagged as such in provenance** (e.g., `extraction_quality = "ocr_tesseract"` in the provenance sidecar) so downstream users can apply extra skepticism.

### When tesseract isn't enough

Tesseract remains the default — bundled in every Linux distro, 100+ language packs, tunes well via PSM and character-whitelist flags. But several modern OCR engines outperform it on specific failure modes, in this order:

| If tesseract is failing on… | Try |
|---|---|
| **Degraded or low-resolution scans** where preprocessing isn't enough | [**PaddleOCR**](https://github.com/PaddlePaddle/PaddleOCR) — production-grade engine with 80+ languages; reliably better than tesseract on noisy or rotated scans. Heavier install (PaddlePaddle wheel) but the accuracy bump is usually worth it. Also the backend kreuzberg uses by default. |
| **Mixed printed + handwritten** or **complex layouts where reading order matters** | [**Surya**](https://github.com/VikParuchuri/surya) — newer (VikParuchuri); does OCR + line / paragraph / reading-order detection in one pass. Pure-Python install, fast on CPU. Strong on multi-column documents. |
| **High-throughput batch processing** where install simplicity beats peak accuracy | [**EasyOCR**](https://github.com/JaidedAI/EasyOCR) — `pip install easyocr` and you have a working multi-language OCR. Less tunable than tesseract, but the lowest-friction option when you just need text out of a thousand scans. |
| **Production deployment with a clean Python API** for documents (not just images) | [**docTR**](https://github.com/mindee/doctr) — explicit "alternative for Tesseract" from Mindee; ships text-detection + text-recognition models with a higher-level document API than tesseract exposes. Worth it for projects building a sustained OCR service. |

Two-tool combinations also help: **[`OCRmyPDF`](https://github.com/jbarlow83/OCRmyPDF) + pdfplumber** is the canonical pattern for a scanned-PDF corpus that needs to be searched *and* extracted. OCRmyPDF wraps tesseract (or any tool above) to add a text layer *to the PDF in place* — the scanned PDF becomes a born-digital PDF that [`pdfplumber`](extract-pdf.md) can then parse normally. This collapses the otherwise-awkward "OCR the page, save text separately, re-attribute text to coordinates" three-step into one. The original is preserved (OCRmyPDF writes a sidecar `.ocr.pdf`), so the immutable-originals discipline holds.

Update `extraction_quality` in `provenance.csv` to name the engine used (`ocr_paddleocr`, `ocr_surya`, `ocrmypdf`, etc.) — downstream users apply different skepticism levels depending on which engine produced the text.

## Image preprocessing for OCR

Image quality at the input is the single biggest factor in OCR output quality. Standard fixes:

- **Resolution.** 300 dpi minimum, 400 dpi for small fonts. Below 200 dpi you will fight Tesseract for every digit.
- **Deskew.** Even a 1° rotation degrades accuracy noticeably. Use `cv2.minAreaRect` on the document's bounding contour or [`deskew`](https://pypi.org/project/deskew/).
- **Binarize.** `cv2.threshold` with Otsu's method or `cv2.adaptiveThreshold` for uneven lighting.
- **Despeckle.** A median filter (`cv2.medianBlur`) before thresholding helps with scanner noise.
- **Crop to content.** Margins waste OCR effort and confuse the layout analyzer.

## OCR gotchas

- **Numbers vs letters confusion.** "0" vs "O", "1" vs "I" vs "l". For numeric tables, restrict the character set with `--psm 6 -c tessedit_char_whitelist=0123456789.,-`.
- **PSM (Page Segmentation Mode) matters.** The default (`--psm 3`, "auto") is often wrong for tables. Try `--psm 6` (assume a single uniform block of text) or `--psm 11` (sparse text) when default OCR is fragmenting rows.
- **Language packs.** English is bundled; other languages require `tesseract-ocr-<lang>` system packages. If the document is multilingual, pass `lang="eng+spa"`.
- **Training a custom model** is rarely worth it for civic data; the [tesseract training guide](https://github.com/neiths/tesseract_training_guide) documents the path if you do need it.

## Extracting embedded images as evidence

PDFs aren't always text-with-tables. Court filings, incident reports, environmental impact assessments, and FOIA-released archives often carry images that *are* the evidence — exhibits, photographs, scanned signatures, maps. The principle: **if the image is referenced by the surface text, the image is part of the dataset**, not optional ephemera. Extract it, hash it, store it alongside the text under `data/original/<source>/<vintage>/_images/<page>-<index>.<ext>`, and add a `has_image` column or a sidecar `images.csv` keyed on `(source, vintage, page)` so a downstream reader can join from a processed-CSV row back to the exhibit it cites.

```python
# pdfplumber exposes pdf.pages[N].images — bounding boxes + the raw bytes
# behind each embedded image. The same image objects are also reachable
# from the PDF's resource dictionary via pdfminer.six or pypdf for projects
# that need image-format-preserving extraction.
```

Update `provenance.csv` with an `images_extracted` count per (source, vintage) so the audit can flag the drift case where a refresh suddenly stops emitting images (usually a parser regression or a publisher format change).

## Document layout analysis

For documents where the structure is not just tables but mixed layout (figures, multi-column text, sidebars), reach for:

- [**`docling`**](https://github.com/docling-project/docling) — the modern default for PDF understanding with mixed layout. Parses reading order, table structure, code blocks, formulas, and image classification into a unified `DoclingDocument` representation with Markdown / HTML / lossless JSON / DocTags exports. Native VLM support via [GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M) handles scanned PDFs without a separate OCR pass. See [the documents part](extract-documents.md#modern-unified-extractors--when-one-tool-is-enough) for the decision tree on docling vs per-format tools.
- [**`unstructured`**](https://github.com/Unstructured-IO/unstructured) for general document partitioning into typed blocks (Title, NarrativeText, Table, ListItem, …) — older incumbent, still fine but generally less capable than docling for PDFs.
- [**`layoutparser`**](https://github.com/Layout-Parser/layout-parser) for ML-based region detection if classical methods fail and you need lower-level control than docling exposes.

These are heavier dependencies. Reach for them only when the layout itself is the problem; for table-centric extraction, pdfplumber/camelot remain the default.

## Computer vision when the image is the dataset

Sometimes the photograph, satellite tile, or video clip *is* the source — there's no text to OCR, and the deliverable is a **structured measurement derived from pixels**: a count, a position, a timestamp, an authenticity flag. The New York Times R&D group's [computer-vision-for-journalism agenda](https://rd.nytimes.com/projects/computer-vision-vision/) is a useful map of the tasks that show up in reporting; each one is, in liberation terms, a way of turning an image corpus into a tidy table. The discipline is the same as everywhere else in this skill: **every CV-derived value is a model's estimate, not a reading** — so it carries a confidence, a model + version in `provenance.csv`, and an `extraction_quality` of `cv_detection` / `cv_estimate`, and it gets validated against a hand-labeled sample the way [`reconcile.py`](pipeline.md#reconciliation) validates totals.

| CV task | What you liberate | Methods / OSS tools | Civic caveat |
|---|---|---|---|
| **Satellite & aerial imagery** | Object counts, footprints/areas, and change/event detection per tile × date (buildings, vehicles, ships, flooding, deforestation, construction) | Tile the raster, run a detector (`YOLO`, `Detectron2`) or segmenter ([Segment Anything](https://github.com/facebookresearch/segment-anything)); geospatial frameworks [TorchGeo](https://github.com/microsoft/torchgeo), [Raster Vision](https://github.com/azavea/raster-vision); diff across vintages for change detection | Georeference every detection (lat/lon, not pixel x/y); counts are estimates — validate against a hand-counted sample of tiles |
| **Crowd counting** | An attendance estimate (with a range) from a photo or video frame | Density-estimation models (CSRNet and successors) for dense crowds; object detection for sparse ones | Report a *range with method*, never a single authoritative number; crowd estimates are politically contested — document the model and the assumptions |
| **Archive / document transcription at scale** | Web-native, human-parity text + structured fields from scanned newspaper or document archives | The OCR engines above, plus VLM transcription ([GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M), Qwen-VL-class models); article/column segmentation for newspaper layouts before OCR | This is the high-volume version of the rest of this file; flag OCR/VLM provenance and spot-check transcription accuracy per vintage |
| **Spacetime-syncing video** | A synchronized event timeline + camera positions, from multiple found clips (bystander, security, dashcam) of one event | Audio/visual alignment for time-sync; structure-from-motion ([COLMAP](https://colmap.github.io/)) for camera geometry | This is forensic/verification work; record every assumption — the output is an evidentiary reconstruction, not a raw reading |
| **3D scene reconstruction** | An interactive 3D model of a scene from photos/video | Photogrammetry (COLMAP), NeRF, 3D Gaussian Splatting | A reconstruction is interpretive; label it as a model and keep the source frames as the immutable originals |
| **Pose / performance from uncalibrated video** | Per-frame measurements (positions, speeds, angles) from cameras of unknown location/distance | Pose estimation ([MediaPipe](https://github.com/google-ai-edge/mediapipe), MMPose, OpenPose) + homography/camera calibration | Uncalibrated cameras yield *relative*, not absolute, measurements unless you calibrate against a known reference in-frame |
| **Synthetic-media detection & provenance** | An authenticity signal on a source image/video *before* you build a dataset on it | Detection models exist but are unreliable and decay fast; the durable path is reading content-provenance metadata ([C2PA / Content Credentials](https://c2pa.org/)) and recording it | Treat any detector score as a weak signal, not proof; prefer provenance metadata. This is a *verification gate* on the source, upstream of liberation |
| **Image / video enhancement** | A more legible working copy: upscaled, deblurred, colorized, or frame-interpolated | Super-resolution ([Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)), colorization, frame interpolation (RIFE) | **Two-edged.** Enhancing a *working copy* to make a degraded scan OCR-able is fine; but enhancement *invents* detail that was never in the source. Never overwrite the immutable original, always flag enhanced media in provenance, and never treat invented detail (a colorized photo, an upscaled "plate number") as evidence |

Two governance hooks tie this back to the rest of the skill:

- **CV-derived fields are inferred, not observed.** Mark them (`extraction_quality = cv_detection | cv_estimate`), store the model name + version + per-detection confidence in `provenance.csv`, and — for counts and measurements — validate against a hand-labeled sample, exactly as reconciliation checks an authoritative total. A CV pipeline with no ground-truth check is a guess with good production values.
- **Some of these are real gates, not advisory.** Face recognition / biometric identification, and any handling of possibly-synthetic media, sit squarely in the privacy-and-CARE territory that the skill treats as a hard gate — see [`context.md`](context.md) and the governance section of [`project-template.md`](project-template.md#governance). Decide *whether* to run the model before deciding how.

### Verifying and locating source media — the OSINT toolkits

Before you build a dataset on a photo or video, you often have to answer provenance questions about the *medium* itself: where and when was it captured, is it authentic, and is this "exclusive" image actually recycled from an older event? Those questions belong in the Survey note and `provenance.csv`, upstream of any extraction. The standing practitioner catalog is **Bellingcat's [Online Investigation Toolkit, image/video category](https://bellingcat.gitbook.io/toolkit/categories/image-video)** — a curated, regularly-updated index that organizes the tools by job:

- **Reverse image search** (Google Lens, Yandex, TinEye, Bing Visual Search) — the cheap first check: has this image appeared earlier or elsewhere? Catches recycled and miscaptioned media before it contaminates a dataset. Complements the near-duplicate detection in the table above.
- **Metadata / EXIF** viewers — camera model, capture timestamp, and sometimes GPS coordinates embedded in the file. Powerful when present, but trivially stripped or forged, so corroborate (a GPS tag is a lead, not proof) and record what you relied on.
- **Geolocation & chronolocation** — fixing *where* (landmark matching, shadow/sun-angle analysis, overlaying satellite imagery) and *when* (shadow length, weather, signage). This is the manual counterpart to the satellite and spacetime-syncing rows above; the output is a coordinate + time you can put on a row.
- **Video tools** — keyframe extraction and frame-level forensics ([InVID-WeVerify](https://www.invid-project.eu/), the YouTube/video metadata viewers) for pulling stills to OCR or geolocate and for checking whether a clip has been edited.
- **Facial recognition** — listed in the toolkit, but for civic-liberation work this is a **hard privacy/CARE gate**, almost always out of scope; see the governance pointer above.

The liberation framing: these tools establish the *provenance and authenticity* of image/video sources the same way the [pre-extraction bulletproofing checklist](pipeline.md#pre-extraction-bulletproofing) establishes it for documents. Use them to fill the `source_url`, `retrieved_at`, and `extraction_notes` of `provenance.csv` — and to decide whether a source is trustworthy enough to liberate at all.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| OCR text has "rn" where you expect "m" | Tesseract artifact on small fonts | Increase image resolution to 400 dpi; consider character whitelist if domain is numeric |
| OCR drops or mangles digits in numeric tables | Low resolution, or "0"/"O" and "1"/"I"/"l" confusion | Raise dpi to 400; restrict with `tessedit_char_whitelist`; try PaddleOCR/Surya |
| OCR rows are fragmented or out of order | Wrong PSM, or skew/multi-column layout | Try `--psm 6`/`--psm 11`; deskew first; use Surya for reading order |
| CV counts look plausible but are wrong | No ground-truth check on the detector | Hand-label a sample of images/tiles and validate against it, like `reconcile.py` checks a total; report precision/recall |
| Satellite detections can't be joined to places | Stored in pixel coordinates, not georeferenced | Carry lat/lon (and the tile's CRS) on every detection, not pixel x/y |
| An enhanced/upscaled image is cited as evidence | Super-resolution / colorization invented detail | Never treat enhanced media as source; keep the original immutable and flag the enhanced copy in provenance |

---

## What to write in the AGENTS.md

- Which OCR engine (tesseract / PaddleOCR / Surya / EasyOCR / docTR) for which source × vintage, and the failure mode that drove the choice.
- Any preprocessing applied — resolution/dpi, deskew, binarize, despeckle, crop.
- Non-default OCR configuration — PSM mode and character whitelist.
- The `extraction_quality` values used (`ocr_tesseract`, `ocr_paddleocr`, `ocr_surya`, `ocrmypdf`, …) so downstream users know which engine produced each batch.
- Whether OCRmyPDF was used to add a text layer in place (and that the original scanned PDF is preserved as the immutable source).
- For any **computer-vision** task: the model + version per task, the hand-labeled sample used to validate it (and the measured precision/recall), the georeferencing/calibration scheme for counts and measurements, and the `extraction_quality` values used for inferred fields (`cv_detection`, `cv_estimate`).
- Whether any **biometric, geolocation, or synthetic-media** model was run, and the privacy/CARE decision behind it (these are governance gates, not defaults).
- For media-verification work, the tools used and what they established — see the verification-toolkit note below.

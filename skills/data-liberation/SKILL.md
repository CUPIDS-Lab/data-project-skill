---
name: data-liberation
description: >-
  Turn documents and messy sources into tidy, provenance-tracked datasets. Extracts tables from
  government PDFs, scanned reports, FOIA releases, spreadsheets, web pages, APIs and dashboards;
  models them as tidy long data with a data dictionary; and, when asked, builds a re-runnable,
  audited Python pipeline and publishes it. Use when the user wants a CSV out of a document, to
  scrape or pull tabular data from a government or institutional source, to add a source or
  vintage to an extraction pipeline, to harmonize records across sources, to write a data
  dictionary or crosswalk for an extracted dataset, or to reconcile or audit data against its
  originals. Trigger on "data liberation," "PDF extraction," "get the data out," "tidy data,"
  "data dictionary," "crosswalk," "provenance," "reconcile," "scrape this site," even when the
  skill is not named. Do not use for setting up a team data collaboration, governance, a
  Dataverse deposit or data sharing (use data-project), for ML model training, or for generic
  Python help.
license: MIT
metadata:
  version: "0.5.0"
  repository: https://github.com/CUPIDS-Lab/data-skills
---

# Data Liberation

Turn documents (PDFs, scans, spreadsheets, web pages, APIs, dashboards) into tidy, documented datasets that someone else can trust and re-create, in the civic-data tradition. Do only what the request needs: a table out of a PDF is a few minutes of work and generates nothing else.

## Non-negotiables

These hold on every request, at every size.

1. **Originals are immutable.** Never edit a source file in place; keep it as fetched, hashed, with where it came from. Cleaning produces new files.
2. **Every value is traceable.** Each extract records source hash, page and region (or URL and selector), tool and version. Provenance is per extract in a sidecar `provenance.csv`, not repeated on every row.
3. **Probe before parsing.** Open the real files (several pages, several vintages) before writing a parser. Don't trust a landing page, a first page, or an OCR text layer that came embedded in a scan.
4. **Fail loudly, never silently.** Empty or degenerate output is an error. Never substitute synthetic, sample or stale cached data for a failed download. Rows that can't be parsed go to a fresh per-run error log, and the count is reported.
5. **Reconcile against the source.** When the document prints totals, check the extracted rows sum to them, and report the result, including mismatches.
6. **Tidy long is the storage shape.** One row per observation, one column per variable; documented in a data dictionary; concepts that cross sources carry caveats about what is and isn't comparable.
7. **Respect the gates.** Ask about sensitivity before handling personal data, and never send documents to a hosted service (OCR, LLM, upload) when the project's sensitivity or visibility forbids it. See `references/_shared/values-and-gates.md`.
8. **Write only into the user's working directory**, never into this skill's folder.

## Find the sections the request touches

This skill follows the shared ten-section Outline (`references/_shared/OUTLINE.md`). It leads sections 2–5 and 8; it contributes to 6 and 10; `data-project` leads 1, 7 and 9. Identify the sections the request touches, read only their references, and check each section's "done when" test before saying the work is finished. Don't announce sections or ask the user to choose one; just do the work and say what you did and didn't do.

| Request sounds like | Sections | Do this |
| --- | --- | --- |
| "get the table out," "give me a CSV," "what's in this spreadsheet," "scrape this page into a table" | 3, 4 | **One-off.** No scaffold, no project. Extract, emit the CSV, report reconciliation. |
| "so I can cite it," "data dictionary," "what do the columns mean," "where did this come from" | 3, 4, 6 | One-off plus `data-dictionary.md`, `provenance.csv` and a short README note. Still no scaffold. |
| "reproducible," "pipeline," "someone can re-run this," "audit," "reconcile," "add tests" | 2–5 | **Project.** Scaffold from the bundled template (below). |
| "add a source," "add this year," "the format changed" | 2–5 | Extend an existing project (below). |
| "harmonize," "crosswalk," "combine these sources," "compare across years or agencies" | 4 | Concept catalog with caveats, only now that a second source exists. |
| "publish," "Datasette," "put it online," "documentation site," "DocumentCloud" | 8 | Only if visibility is public or embargoed; generate only the chosen surface. |
| "start a data collaboration," "governance," "deposit," "DOI," "share with a partner," "we finished a sprint" | 1, 7, 9, 10 | Hand off to the `data-project` skill. If it isn't installed, follow `references/_shared/OUTLINE.md` for that section. |

When the request is ambiguous, start with the smallest route that satisfies it, say so in one sentence, and offer the next step when you finish ("Here's `data.csv`, reconciled to the printed totals. Want a data dictionary and provenance so it's citable?").

## One-off extraction (sections 3–4)

1. **Triage** every page or file: born-digital text, scanned, or mixed; tables, forms, multi-page tables, footnotes that change meaning.
2. **Pick the tool** from the table below and open only that input's reference.
3. **Extract**, keeping page and region for each value.
4. **Check** row counts and printed totals; list anything that didn't reconcile and any rows that failed.
5. **Emit** a tidy CSV to the user's working directory, plus `provenance.csv` and `data-dictionary.md` if they asked for something citable.

| Input | Start with | Reference |
| --- | --- | --- |
| Born-digital PDF (has a real text layer) | PDFium text (`pypdfium2`), `pdfplumber` for positioned words, `camelot` for ruled tables | `references/extract-pdf.md` |
| Scanned PDF, photos, image files, maps | test any embedded OCR first, then OCR, layout or vision-model parsers with a parser manifest | `references/extract-images.md` |
| Complex layouts or mixed corpora (DOCX, HTML, many documents) | unified layout pipelines (born-digital PDFs still start in `extract-pdf.md`) | `references/extract-documents.md` |
| XLSX (incl. panel format), CSV, Parquet, databases | explicit dtypes, never inferred | `references/extract-tabular.md` |
| HTML pages, scraping, archives | cached requests, browser automation only when needed, Wayback fallback; scheduled snapshots for sources that show only the current state | `references/extract-web.md` |
| APIs, BI dashboards, ArcGIS layers | the endpoint behind the dashboard, paged and cached | `references/extract-api.md` |

## Project (sections 2–5)

**Start single-source.** Scaffold for the one source in hand. Add the source registry, `concepts.yaml` and cross-source harmonization only when a second source actually arrives; building them on day one produced premature abstraction in real projects.

**Scaffold from the bundled template** at `templates/project/`. Read `references/project-template.md` first; it explains every file, the slot-fills and the file groups. For each file in the groups that are in scope: strip a trailing `.tmpl`, substitute the `{{UPPER_SNAKE}}` slot-fills (`PROJECT_NAME`; `PROJECT_SLUG`, kebab-case for the repository; `PKG_NAME`, snake_case for imports; `DESCRIPTION`; `AUTHOR`; `OWNER`; `CONSUMER_STACK`), drop `<!-- IF:FLAG -->…<!-- /IF -->` blocks whose flag is off, and write into the user's directory. Leftover `{{ }}` is a bug. Don't invent a parallel structure, and don't read `templates/` unless you are scaffolding.

The project starts with the five working files from the Outline (`README.md`, `AGENTS.md` plus a one-line `CLAUDE.md`, `ROADMAP.md`, `decision-log.md`, `CHANGELOG.md`) and the pipeline core. Publishing files are generated only when section 8 is in scope.

**Verify** before saying it's done: `uv sync && uv run pytest`, then `uv run python -m scripts.pipeline run` on a sample file. Confirm the audit report, the reconcile result and the error log say what you claim.

**Adding a source or a vintage to an existing project:**

1. Read the project's `AGENTS.md` first; it answers the architecture questions.
2. Probe the new files. Decide whether this is a new vintage of a known format, a format change mid-series (add a vintage-specific branch), or a genuinely new source.
3. Add the parser under `scripts/parsers/`, a fixture and a test under `tests/`, and the artifact list and `parser_for` routing in `scripts/source.py`. A second source is when the source registry and concept catalog arrive (`references/project-template.md`, "Adding a second source").
4. Run the pipeline, then audit and reconcile. A new mismatch blocks the merge until it is explained.
5. Update the data dictionary's caveats and the decision-log, and open a PR whose body carries the audit and reconcile diffs.

## Publishing (section 8)

Only when the project's visibility is public or embargoed. Generate only the surface asked for, from `references/publishing.md`: Datasette (queryable interface), a Quarto site (methodology and tutorials), Git LFS (large files), DocumentCloud (the source documents, page by page). An embargoed project stages the release with its date and conditions and publishes nothing early.

## When you finish

Report what you produced, what reconciled and what didn't, what you deliberately did not build, and the next sensible step. At the end of a sprint on a project, remind the user to file sprint feedback (`references/_shared/feedback.md`).

## References (load only what the current section needs)

- `references/_shared/OUTLINE.md`: the ten sections, their "done when" tests, and the five working files.
- **Acquire and extract (2–3):** `extract-pdf.md`, `extract-images.md`, `extract-documents.md`, `extract-tabular.md`, `extract-web.md`, `extract-api.md`.
- **Model and tidy (4):** `data-modeling.md` (tidy shape, schema contract, dictionary, provenance, concept catalogs, validation).
- **Pipeline and audit (5):** `pipeline.md` (cleaning order, discovery, audit, reconcile, recurring refresh, FOIA), `project-template.md` (the skeleton and every file in it), `_shared/quality-and-bulletproofing.md`.
- **Publish (8):** `publishing.md`, `_shared/standards-and-fair.md`.
- **Background and gates:** `lineage-and-landscape.md` (where this practice comes from), `_shared/values-and-gates.md`, `_shared/responsible-data.md`, `_shared/governance.md`, `_shared/practice-sources.md`.
- **Feedback (10):** `_shared/feedback.md`.

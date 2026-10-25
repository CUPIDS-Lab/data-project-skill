---
type: Reference
title: Quality and Bulletproofing
description: The quality and pre-release bulletproofing pass for both skills — the Quartz "who fixes it" taxonomy, ProPublica bulletproofing, conservation and fail-loudly checks, generated-number staleness checks, and second-reader checks for model-based extraction.
tags: [quality, bulletproofing, audit, reconcile, conservation, verification, data-quality]
---

# Quality and bulletproofing

Read this in Outline section 5 (Pipeline & audit), and before any number leaves the project: a release, a deposit, a partner share, a chart, a quoted figure. It merges the Quartz Bad Data Guide (what goes wrong, and who should fix it), ProPublica's *Bulletproofing Your Data Analysis* (how to check hard enough to stake a reputation on the result), and the lessons projects learned the hard way (conservation checks, failing loudly, generated numbers, second readings for model-based extraction). data-liberation's `pipeline.md` carries the extraction-specific version of the pre-extraction checks, mapped to its quality dimensions; this file is the cross-skill pass.

## Contents

- [What quality means here](#what-quality-means-here)
- [Is the data usable at all: the Quartz taxonomy](#is-the-data-usable-at-all-the-quartz-taxonomy)
- [Checks the build runs every time](#checks-the-build-runs-every-time)
- [Generated numbers and staleness checks](#generated-numbers-and-staleness-checks)
- [Second-reader checks for model-based extraction](#second-reader-checks-for-model-based-extraction)
- [The human bulletproofing pass](#the-human-bulletproofing-pass)
- [Cognitive checks worth naming](#cognitive-checks-worth-naming)
- [The pre-release checklist](#the-pre-release-checklist)
- [Where findings are recorded](#where-findings-are-recorded)

## What quality means here

Data is high quality when it is *fit for use*, and fitness has dimensions: availability (can it be obtained, is use authorized), usability (documented, credible), reliability (accurate, consistent, complete, auditable), relevance (does it answer the question), and presentation (can people read it without translating). The four computed ones are accuracy (reconciliation against published totals), completeness (null rates, with the three-way distinction *exists but unknown* / *does not exist* / *unknown whether it exists* recorded in the dictionary), consistency (schema and cross-source agreement) and timeliness (fetched versus published, against the source's cadence). Quality work has three layers that should not be conflated: **profile** what is there, **measure** it against declared thresholds, **monitor** it for drift over time. data-liberation's `data-modeling.md` defines these canonically.

Three passes use this file, at different moments:

1. **Before trusting a source** (sections 2 and 3): the Quartz scan below, the source-level checks (record counts, printed totals, ranges, sentinels), the methodology hunt, and identifying a contact.
2. **Every build** (section 5): automated checks that make the pipeline refuse to produce wrong data quietly.
3. **Before release** (sections 5, 8 and 9): the human bulletproofing pass and the pre-release checklist.

## Is the data usable at all: the Quartz taxonomy

Most data problems are recognizable and many are fixable, but some mean you should not use the data at all and others mean you may proceed only with stated caveats. The Quartz Bad Data Guide sorts roughly four dozen failure modes by who is best placed to fix each, because knowing whose problem it is determines what to do next. Run this scan on a new source or a new vintage before building on it.

**Issues your source should fix** (ask the publisher; document what they say):

- Values missing where data was expected, with unexplained gaps; expected records absent.
- Zeros standing in for missing values, or the reverse, so absence is counted as a measurement.
- Sentinel values that mean "unknown" (`65535`, `-1`, `-9`, `9999`, `99999999`, `1900-01-01`, `1970-01-01`, the empty string).
- Inconsistent spelling, capitalization or name order fragmenting one category.
- Inconsistent date and number formats (`MM/DD` mixed with `DD/MM`; thousands separators in some rows).
- Units or essential metadata missing; ambiguous field names; undocumented provenance.
- Truncation at a tool's limit (65,536 or 1,048,576 rows, 255 columns, exactly 10,000 rows, powers of two).
- Numbers stored as text, losing leading zeros.
- Totals that don't match published figures.
- Format-native error markers (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `null` in required JSON fields): these originated with the publisher, so surface them as audit findings rather than coercing them silently to missing.

**Issues you should fix** (in the parser, with the change recorded):

- Garbled text from encoding or line-ending mismatches.
- Data trapped in PDFs or scans that must be extracted first.
- Wrong aggregation level or geography for the question.
- Inconsistent human data entry (free text where codes were expected, ad hoc abbreviations).
- Figures not adjusted for inflation, or seasonal series compared without accounting for seasonality.
- A manipulated timeframe or frame of reference.
- Non-random or biased samples that don't support the claim.
- Margins of error that are too large or unknown.

**Issues an expert should weigh in on** (a subject-matter expert, before anything is claimed):

- An author or collecting body of uncertain trustworthiness, or with an interest in the result.
- An opaque collection process, so you can't tell what the numbers measure.
- Implausible or false precision.
- Inexplicable outliers.
- Signs of p-hacking: results that survive only one of many specifications.
- An index or composite masking the variation that matters.
- Figures that are too good to be true.

**Issues a programmer should help with**:

- Re-aggregating to different categories or geographies (and quantifying the error that introduces).
- Tuning OCR or extraction for specific documents.

Some problems are unfixable; the honest move is to stop using the data, or to publish only with the caveat stated where every reader will see it.

## Checks the build runs every time

Section 5's "done when" test says the build refuses to produce wrong data quietly. These checks are code, not checklist items, and they run in CI.

- **Schema validation.** The tidy table validates against the schema contract on every run; drift fails.
- **Deduplicate before validating.** Remove exact duplicates (and resolve near-duplicates by a documented rule) before validation, so validation reports real violations rather than duplicates it cannot drop.
- **Conservation checks.** Count rows (and, where meaningful, sum key amounts) at each stage boundary: fetched, parsed, cleaned, deduplicated, rejected, written. Every row that enters a stage either leaves it or lands in a named reject or dedup output, and CI fails if the counts don't balance. A stage that loses rows silently is the most common way a pipeline produces plausible wrong data.
- **Fail loudly on empty or degenerate output.** An empty table, a column that is entirely null, a vintage with a fraction of the previous vintage's rows, a single distinct value where there should be many: each fails the build (or, for a known exception, requires an explicit allow-list entry with a reason). Never silently write an empty CSV.
- **Never substitute.** Nothing replaces a failed download or parse with synthetic, sample, cached or previous-vintage data without failing. Two inherited notebooks in the projects these skills served silently generated synthetic data when a download failed; the outputs looked fine.
- **A fresh error log per run.** Extraction errors go to a per-run log that starts empty, so old failures can't mask new ones, and the audit summary shows the error count prominently.
- **Reconciliation.** When the source publishes totals, recompute them from the processed rows, at the finest grain the source and the output share, and compare. Mismatches fail the reconcile job (the run still completes, so data isn't lost), and each known mismatch is documented with its upstream cause, for example an arithmetic error in the source's own subtotal. The goal is not zero mismatches but every mismatch accounted for.
- **Audit samples on a stable key.** Random samples for human checking are drawn by hashing a stable natural key, not by row number or a seed over row order, so the sample survives an agency renumbering its records or a re-sort.
- **Controlled vocabularies enforced.** A test checks that values in lookup files and categorical columns match the data dictionary's allowed values.
- **File-size guard.** CI fails on any tracked file near GitHub's 100 MB limit, so large originals go to Git LFS or external storage with a hash and URL in provenance.

## Generated numbers and staleness checks

Every number quoted in prose (row counts, totals, match rates, date ranges, the number of sources) is generated by the pipeline into machine-readable audit outputs, and the README, methodology, data card, manuscript or deposit description quotes a copy. Projects that generated counts and tables into their docs and failed CI when they went stale stayed accurate; hand-typed numbers drifted in four of nine.

- Write headline figures to a JSON or Markdown file under `data/audit/` on every run.
- Render the quoted copies from it, between `<!-- BEGIN generated -->` and `<!-- END generated -->` markers, with a small script.
- Add a CI step that re-renders and fails if the committed docs differ (`git diff --exit-code` on the rendered files).
- When a number can't be generated (a figure from a partner's report), cite its source and date beside it.

## Second-reader checks for model-based extraction

OCR engines, layout tools, vision-language models and hosted extraction APIs produce plausible output when they are wrong. Before their output is used:

- **Parser manifest.** Record the tool, model and revision, settings, prompt or schema, and date for each run, and use the canonical `extraction_method` value (`ocr:<engine>`, `vlm:<model>@<revision>`, `layout:<tool>`, `cv:<model>`) with an `extraction_quality` of `clean`, `caveats` or `degraded` in `provenance.csv`.
- **Test an embedded text layer before trusting it.** Embedded OCR layers in scanned files proved unusable three times in the projects reviewed; compare a sample against the page image before using one.
- **Two readings must agree.** Accept a figure only when two independent readings agree: two engines, two models, a model and a deterministic parser, or a model run twice with different prompts. Disagreements go to a human queue.
- **Printed totals as checksums.** Where the page prints a total, recompute it from the extracted rows; a page that doesn't reconcile is quarantined, not shipped.
- **A human audit sample.** Check a stratified sample by eye against the page image (including the hardest page types), record the error rate, and repeat after any model or prompt change.
- **Watch for shifts the sum can't see.** A name-to-amount row shift preserves a column total; check row alignment directly on sampled pages, especially in itemized personnel or line-item tables.
- **Cost cap and sensitivity.** Hosted services get a spending cap and a page budget, and they receive only documents the sensitivity and visibility decisions allow.

## The human bulletproofing pass

Automated tests catch what you thought to test. Bulletproofing is the human, against-the-source layer on top of them, run before any release, deposit, partner share or published claim.

**Integrity**

- Verify record counts against expected totals and watch for silent software row limits.
- `GROUP BY` every key categorical field to catch inconsistent spelling, stray whitespace and duplicates hiding behind near-identical values.
- Validate that numeric ranges and dates are plausible and cover the period and jurisdictions the source claims.
- Decide whether blanks are real values or import artifacts, and whether zeros are real or stand in for missing.

**Recomputation**

- Recompute each published figure by a different code path (a different query, a different tool) and confirm the two agree. Two queries that agree raise confidence more than two that look alike.
- Pull a random sample (about 50 rows, drawn on a stable key) and check each against the original source; repeat after every significant parser change.
- Spot-check physically: for about ten records, open the original artifact and verify every cell by eye, which catches column shifts no automated check finds.

**Cross-reference**

- Identify and verify the original source; reconcile totals with any published reports.
- Corroborate with an independent source for the same phenomenon (a federal mirror, an aggregator, a watchdog dataset). Two that match build confidence; two that diverge surface a finding.

**Gut check and outliers**

- If a result seems off, it probably is: a 50% year-over-year jump that nobody else reported is almost always an extraction bug.
- A number that is exactly what you hoped for gets more scrutiny, not less.
- Treat outliers as leads to investigate, not noise to drop, and bring in a subject-matter expert when the method exceeds your expertise.

**Independent review**

- Have a knowledgeable colleague replicate the key results from the originals without copying your queries.
- In a solo project, say so honestly: the second reader is the alternate code path, the stable-key sample and a self-review after a delay, recorded in the PR body ("What I checked"). Don't claim a review that didn't happen.
- Where the work names people or institutions, show findings to them before release when the relationship and safety allow; errors caught then are corrections, errors caught after are retractions.

**Keep a data notebook.** Record every procedure, filter and decision (sources, transformations, queries, why) in the decision-log or a dated work log, and comment every non-trivial audit or reconcile query with why it aggregates or filters as it does.

## Cognitive checks worth naming

- **Avoid false precision.** "52.18%" from counts with a margin of ±30 invents accuracy; the dictionary says which columns carry meaningful precision.
- **Set a cutoff date.** Datasets that grow while you work rewrite history under you; freeze a date, document it, and reach past it only for explicit corrections.
- **Ask for the methodology.** A publisher's refusal to share a questionnaire or method is a red flag worth recording; non-scientific methods (self-selected web panels) become dictionary caveats.

## The pre-release checklist

One checklist, merging the data-quality scan and the bulletproofing pass, is generated when a release, deposit or partner share is planned (section 5's "generate only if"). It works when it gates that decision at the moment it is made: offer it first as a task list on the release or deposit issue (or in the PR body for a solo project), and as a file only when it must ship with the release or deposit. A checklist generated early and left unfilled rots; in another project, bundled checklists sat at 0 of 65 boxes while the release they were meant to gate never happened.

For sensitive data, run every check inside the controlled tier, share only desensitized samples with reviewers, treat any field that could re-identify someone as both a quality and a privacy concern, and complete the responsible-data checklist (`responsible-data.md`) before release.

## Where findings are recorded

- Known issues, sentinel values, caveats and known mismatches: the data dictionary.
- Per-run counts, errors, conservation balances and reconcile results: `data/audit/`, committed in summary form so a refresh PR carries the diff.
- Decisions about what to drop, fix or caveat: the decision-log.
- Publisher-side failures (format-native errors, missing methodology, totals that don't add up, redactions): recorded as findings in the audit outputs and `AGENTS.md`'s known limitations; they are part of the project's contribution, not just an inconvenience.

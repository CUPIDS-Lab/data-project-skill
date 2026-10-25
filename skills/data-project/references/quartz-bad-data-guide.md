---
type: Reference
title: Quartz Bad Data Guide
description: A taxonomy of ~46 common data problems organized by who should fix them — the source, you, a subject-matter expert, or a programmer — with the recommended response to each.
resource: https://github.com/Quartz/bad-data-guide
tags: [transparent, documented, reproducible, data-quality]
---

# Quartz Bad Data Guide

A comprehensive field guide to the ways data goes wrong, organized by who is best placed to fix each problem. Source: https://github.com/Quartz/bad-data-guide

## In one paragraph

Most data problems are recognizable and many are fixable — but some mean you should not use the data at all, and others mean you can proceed only with stated caveats. The guide sorts roughly four dozen failure modes into four responsibility tiers (your source, you, an expert, a programmer) so you know who to ask and what to do. It is the checklist behind the "known issues" you record in the data dictionary and the data-quality scan you run before trusting a dataset.

## Key practices (sampleable units)

- **Issues your source should fix** [transparent, documented] — missing values; zeros or sentinels (65535, -1, 1970-01-01) standing in for missing; expected records absent; inconsistent spelling, name order, or date formats; unspecified units; ambiguous field names; undocumented provenance; truncation at 65,536 rows / 255 columns; numbers stored as text (lost leading zeros); totals that don't match published figures.
- **Issues you should fix** [reproducible, documented] — garbled text/encoding and line endings; data trapped in PDFs or scans; wrong aggregation level or geography; human-entry inconsistency; inflation or seasonality skew; manipulated timeframe or frame of reference; non-random or biased samples; margins of error that are too large or unknown.
- **Issues an expert should weigh in on** [transparent] — untrustworthy author; opaque collection process; implausible precision; inexplicable outliers; p-hacking; an index masking underlying variation; "too good to be true" figures.
- **Issues a programmer should help with** [reproducible] — re-aggregating to different categories/geographies (quantifying the error introduced); tuning OCR for specific documents.

## Artifacts it implies

- → `templates/data-quality-checklist.md.tmpl`; feeds the "known issues / caveats" section of `templates/data-dictionary.md.tmpl`.

## When most relevant

Whenever you receive a messy dataset, and before publishing. Strong signal on "messy data," "clean this," "is this data any good," "missing values," "outliers." L4, alongside bulletproofing.

## Caveats / conflicts

It is a menu of failure modes, not a process — pair it with ProPublica bulletproofing (the verification process) and record what you found and how you handled it. Some problems are unfixable; the honest move is to stop using the data.

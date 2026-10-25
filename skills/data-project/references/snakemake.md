---
type: Reference
title: Snakemake
description: A Python-based workflow manager for reproducible, scalable data analyses defined as a DAG of rules with per-rule environments.
resource: https://snakemake.readthedocs.io/
tags: [reproducible, pipeline, transparent]
---

# Snakemake

A tool to create reproducible and scalable data analyses, expressed as rules that form a directed acyclic graph. Source: https://snakemake.readthedocs.io/

## In one paragraph

Snakemake defines a pipeline as a set of rules, each declaring inputs, outputs, and a shell/script step; Snakemake infers the dependency DAG from filenames and runs only what's needed, scaling from a laptop to HPC/cloud unchanged. Config files parameterize runs and per-rule conda environments make steps reproducible. It is the default "pipeline-as-code" artifact at L2 for Python-leaning projects.

## Key practices (sampleable units)

- **Rules + wildcards** [reproducible] — each rule maps `input` → `output` with a command; wildcards generalize a rule across many samples; a `rule all` declares final targets.
- **DAG + dry-run** [reproducible, transparent] — Snakemake builds the dependency graph and `snakemake -n` previews what would run without executing — a cheap correctness check.
- **Config-driven** [reproducible, documented] — parameters and paths live in `config.yaml` (`configfile:`), overridable on the CLI; no hard-coded constants.
- **Per-rule environments** [reproducible] — `conda:` directives pin a step's dependencies; runs are isolated and recreatable.
- **Pipeline-as-code is the shared artifact** [collaborative, reproducible] — share the re-runnable workflow, not just the cleaned output, so new data vintages re-process automatically.

## Artifacts it implies

- Pipeline skeleton → `templates/python/Snakefile.tmpl`; parameters → `templates/python/config.yaml.tmpl`; environment → `templates/python/environment.yml.tmpl`. R analogue is `_targets.R`.

## When most relevant

L2 and above; whenever the user wants reproducibility, a pipeline, "re-run on new data," or multi-sample processing. Python default; R projects use `targets` instead.

## Caveats / conflicts

Overkill for a one-shot analysis (stay at L1) — introduce it only when re-runnability or scale justifies it. For R-centric teams prefer `targets`/`_targets.R` over Snakemake.

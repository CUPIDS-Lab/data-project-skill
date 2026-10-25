---
type: Procedure
title: Deposit to Dataverse (section 9)
description: The deposit procedure for archiving a project's processed data, code and documentation in a Dataverse repository for a citable DOI. Sensitivity gate first, then manifest, preflight, idempotent create-or-update, lock- and ingest-aware upload, versioned refreshes, and publication only on explicit confirmation.
tags: [deposit, dataverse, doi, section-9, versioning]
---

# Deposit to Dataverse (section 9)

Use this when the user asks to deposit, archive, "get a DOI," or refresh an existing deposit. It runs the kit in `templates/dataverse/` (rendered into the project's `dataverse/`; `scaffold.md`). The API details, metadata fields and the mechanics behind each rule are in `../dataverse-deposit.md`; read it once before the first deposit.

## Contents

- [Inputs](#inputs)
- [Steps](#steps)
- [What goes where](#what-goes-where)
- [Versioning](#versioning)
- [Agent permission prompts](#agent-permission-prompts)
- [Report](#report)

## Inputs

The project (default: the working directory) with `data/processed/`, its code, and its documentation; the citation facts (`PROJECT_NAME`, `PI_NAME`, `LAB_NAME`, `CONTACT_EMAIL`, `DESCRIPTION`, a controlled-vocabulary subject, `LICENSE`); the target `DATAVERSE_URL` (default `https://dataverse.harvard.edu`) and `DATAVERSE_COLLECTION` alias; the project's sensitivity tier, visibility, and the access tiers in `docs/governance/GOVERNANCE.md`.

## Steps

1. **Gate on sensitivity and visibility first.** A private project does not deposit openly; an embargoed one deposits only after its release condition is met (or as a restricted draft the user explicitly approves). If the data is sensitive-human, regulated or CARE-implicated, never deposit identifiable traces openly: apply the access tiers (desensitize, upload the affected files as restricted with `RESTRICT_DATA=1`, or withhold them and deposit only code and documentation) and confirm the pre-release checklist and responsible-data checklist are done. When in doubt, withhold and ask.
2. **Build the manifest.** Write or refresh `dataverse/dataset.json` from the project's own front matter (`README.md`, `CITATION.cff`: title, authors with ORCIDs, contact, description, keywords, license) so the paper, the citation and the deposit cannot drift. Keep `subject` to a value Dataverse offers. Keep it valid JSON.
3. **Preflight, then pick a tier.** Is `DATAVERSE_API_TOKEN` set in the environment? Is the collection reachable (`GET {url}/api/dataverses/{alias}`)? Is `pyDataverse` importable? On any gap, print "missing X → set or grant it via Y" and drop a tier rather than stopping:
   - **A, pyDataverse:** `python dataverse/deposit_dataverse.py` (validates the metadata, then creates or updates and uploads).
   - **B, curl:** `bash dataverse/deposit-dataverse.sh` (no Python needed; same result).
   - **C, emit and hand off:** with no token or collection, write the kit and tell the user the one command and the token and collection to set. Never fail the scaffold for missing credentials.
4. **Rehearse on the demo sandbox.** The scripts target `https://demo.dataverse.org` unless `--prod` is passed. Recommend `DRY_RUN=1` first, then a full demo run, before touching production.
5. **Create or update, idempotently.** `--collection` creates a new dataset. A recorded `dataverse/.dataverse-deposit.json` (or an explicit `--pid`) updates the existing dataset: files whose names already exist are replaced in place (`forceReplace`), only new files are added, so a re-run never duplicates. The file listing uses the `:latest` version, which is the draft when one exists and the last published version otherwise.
6. **Upload lock-aware and ingest-aware.** Poll the dataset's locks between uploads, because a CSV ingest locks the dataset and the next call fails until it clears. Plain CSV and TSV files are tabular-ingested (typed, with a UNF); ship one large combined dump as `.gz` so it is stored opaque, never as a `.zip`, which Dataverse unpacks into separately ingested members. Preparing `data/processed` for the ingester (UTF-8, ISO dates, uniformly typed numeric columns, deterministic bytes) is the pipeline's job, not the deposit script's.
7. **Deposit the self-documenting bundle.** Alongside the data, upload the data dictionary, the data card, the provenance file and the audit and validation reports, so the archived snapshot carries its own evidence.
8. **Stop at a draft.** Show the draft URL, confirm the license and that the pre-release checks passed, and ask explicitly whether to publish. Publishing mints the DOI and is effectively permanent. Publish only on an explicit yes; otherwise leave the draft and give the one-line publish command.
9. **After publishing,** record the DOI in `README.md`, `CITATION.cff` (`identifiers:`), the data card and the data-management plan, add a CHANGELOG entry, and mark section 9 in `ROADMAP.md` with the DOI as evidence. Verify the record read-only (`GET {url}/api/datasets/:persistentId?persistentId=<doi>`, or the `mcp-dataverse` server's `search_datasets`).

## What goes where

| Project files | Dataverse category | Folder in the dataset |
| --- | --- | --- |
| `data/processed/*` (including `provenance.csv`) | Data | `data/processed` |
| `scripts/`, `pyproject.toml`, `uv.lock`; R: `R/`, `_targets.R`, `DESCRIPTION`, `renv.lock`; optional `Snakefile`, `config.yaml`; multi-pipeline: each `pipelines/<name>/` with the same files and `pipelines/_core/` | Code | `code` |
| `README.md`, `CHANGELOG.md`, `decision-log.md`, `docs/data-dictionary.md`, `docs/data-card.md`, `knowledge/` | Documentation | `documentation` |
| `data/audit/*` reports, `docs/checklists/*` | Documentation | `documentation/validation` |

`data/original/` is not deposited by default; deposit originals only when their license allows redistribution and the sensitivity decision permits it.

## Versioning

One dataset, one DOI, successive versions; cite a version by its number and UNF. The **first publication is a major version** (v1.0; Dataverse requires it). **Later refreshes publish as minor versions** (v1.1, v1.2, …), which is what projects actually needed: the DOI stays stable and each refresh is citable. Reserve a new major version for a breaking change (a schema change, a redefined variable), and say why in the CHANGELOG. The scripts choose major for the first publication and minor afterward; `--major` forces a major version.

For a dataset refreshed on a cadence (`UPDATING`), the scheduled `.github/workflows/dataverse-deposit.yml` regenerates the data, uploads a new **draft** version with `--no-publish`, and opens a review issue. It never publishes; a maintainer reviews the draft and runs `--publish`. Record each refresh in `CHANGELOG.md`, which is deposited with the data.

## Agent permission prompts

An agent's permission mode may block an approved upload because it looks like data exfiltration (a command sending project files to an outside host). Don't route around the block. Ask the user to approve that exact command explicitly (for example a single allow rule for `bash dataverse/deposit-dataverse.sh --prod --pid <doi>`), record the approval and its scope as a dated rule in `AGENTS.md`, and keep the scope enforced in code: the script's file list, not the agent, decides what leaves the machine. Never widen the permission beyond that command.

## Report

Return the tier reached, the draft or published URL and DOI, the version number, what was created versus updated, which files were restricted or withheld and why, and, if you degraded, the exact command and the missing token or permission needed to finish. Never commit the token.

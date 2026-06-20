---
type: Reference
title: Harvard Dataverse Deposit (Native API, pyDataverse)
description: How a data project deposits its processed data, code, and documentation to a Dataverse repository (e.g. Harvard Dataverse) for a citable DOI — the dataset/file/publish workflow, required citation metadata, the data/code/docs→file-category mapping, and the capability-degradation chain (pyDataverse → curl → emitted artifacts).
resource: https://guides.dataverse.org/en/latest/api/native-api.html
tags: [accessible, transparent, fair, findable, deposit, dataverse]
---

# Harvard Dataverse Deposit (Native API)

How a finished project archives its outputs in a Dataverse repository so they are findable, citable (a DOI), and reusable — the L5 deposit surface, sibling to the OKF knowledge bundle and the ARD catalog. Source: the Dataverse [Native API guide](https://guides.dataverse.org/en/latest/api/native-api.html); clients: [pyDataverse](https://github.com/gdcc/pyDataverse) (official GDCC Python client) and [mcp-dataverse](https://github.com/gdcc/mcp-dataverse) (read-only discovery).

## In one paragraph

A Dataverse *installation* (e.g. `dataverse.harvard.edu`) holds *collections* (each has an `alias`); a collection holds *datasets*; a dataset holds *files* and gets a **DOI at publication**. Depositing is three Native-API calls — create a draft dataset from a citation-metadata JSON, add files (each tagged with a category and folder), then publish — authenticated with an `X-Dataverse-key` token. This skill generates that metadata manifest and runnable deposit scripts from the project it already scaffolded, maps `data/processed`/code/docs onto Dataverse file categories, and leaves the dataset reviewable as a **draft** until a human confirms publication (which mints the DOI and is effectively irreversible).

## Key practices (sampleable units)

- **Three-step deposit** [accessible, transparent] — (1) `POST /api/dataverses/{alias}/datasets` with a `dataset.json` (creates a **draft**, returns the persistent id); (2) `POST /api/datasets/:persistentId/add?persistentId={pid}` once per file (multipart: `file`, `description`, `directoryLabel`, `categories`, `restrict`, `tabularTagIngest`); (3) `POST /api/datasets/:persistentId/actions/publish?persistentId={pid}&type=major` to publish. Header `X-Dataverse-key: {token}` on every write.
- **Required citation metadata** [documented] — the `citation` block requires **title**, **author** (compound, `authorName` required), **datasetContact** (compound, `datasetContactEmail` required), **dsDescription** (compound, `dsDescriptionValue` required), and **subject** (controlled vocabulary, ≥1). The dataset.json nests these as `datasetVersion.metadataBlocks.citation.fields[]`, each field carrying `typeName` + `value` (primitive = string; compound = array of `{child: {value}}`; controlled-vocab = array of strings).
- **Subject controlled vocabulary** [documented] — exactly one or more of: Agricultural Sciences; Arts and Humanities; Astronomy and Astrophysics; Business and Management; Chemistry; Computer and Information Science; Earth and Environmental Sciences; Engineering; Law; Mathematical Sciences; Medicine, Health and Life Sciences; Physics; Social Sciences; Other. (Fills `{{DATASET_SUBJECT}}`.)
- **Files carry category + folder** [documented, accessible] — `categories` tags a file (use **Data** / **Code** / **Documentation**) and `directoryLabel` places it in a virtual folder preserved on download (allowed chars: alphanumerics, `_ - .` and space). `tabularTagIngest=true` triggers tabular ingest for CSV/Stata/SPSS so columns become searchable.
- **DOI at publish, versioned** [transparent] — a draft has no DOI until published; `type=major` → v1.0, `type=minor` → v1.1 (after first release). Re-deposit updates the draft of the next version rather than creating a new dataset.

## Capability & degradation chain (what the depositor does)

API token present? → pyDataverse importable? → target collection reachable? Land at the richest tier; never fail the scaffold, and **never publish without explicit confirmation**.
- **A — pyDataverse (preferred):** `NativeApi(base_url, token)` → `create_dataset(alias, ds.json())` → `upload_datafile(pid, path, df.json())` → (confirmed) `publish_dataset(pid, "major")`, with `ds.validate_json()` catching metadata errors before the network call.
- **B — curl Native API (zero-dep):** the generated `deposit-dataverse.sh` runs the three calls with only `curl` + a token; identical result, no Python.
- **C — emit artifacts, run later:** write `dataset.json` + `deposit-dataverse.sh` + `deposit_dataverse.py` + `DEPOSIT.md`, and hand back the **one command** plus the token/collection the user must set.
- **D — always:** the `dataset.json` manifest + `DEPOSIT.md` guide are written regardless, so the deposit is reproducible off-skill.
- **Verification (read-only side-channel):** after publish, `mcp-dataverse` (`search_datasets`, `get_croissant_record`) or a `GET /api/datasets/:persistentId` confirms the record. mcp-dataverse cannot create/upload/publish.

Idempotency: a `.dataverse-deposit.json` manifest maps `pid` + each file path → file id + content hash; re-running **replaces changed files and adds new ones** rather than duplicating.

## Versioned / periodically-updated ("streaming") deposits

When the project's data is refreshed on a cadence (monthly/quarterly/annually), follow the Dataverse [data-citation best practices](https://dataverse.org/best-practices/data-citation): keep **one dataset DOI** and publish each refresh as a **new version** (`type=major` → v2.0, v3.0…), never a new dataset. A published version is cited by **author, year, title, repository, version, the DOI, and the UNF** — the Universal Numerical Fingerprint Dataverse computes for tabular files, which pins the exact data snapshot independent of format. Re-running the deposit against the recorded `pid` makes a **draft of the next version** automatically.

- **Scheduled re-deposit** [findable, transparent] — at L5 with the `UPDATING` flag, emit `templates/ci/dataverse-deposit.yml`: a workflow that runs on `{{DEPOSIT_CRON}}` (derived from the cadence), regenerates `data/processed`, re-deposits a **draft** new version (`--no-publish`), and opens a review issue. It never publishes — minting a version stays a human decision.
- **Metadata** — record the cadence (`UPDATE_FREQUENCY` → citation `notesText`), the `timePeriodCovered`, and per-release changes in `CHANGELOG.md` (deposited as Documentation), so each version carries its own changelog.
- **Integrity** — keep `tabularTagIngest=true` for CSVs so Dataverse computes the UNF; always cite the **version + UNF** of the snapshot used.

## Access & tokens — make sure the agent can actually do this

- **Get a token (Harvard):** log in to `https://dataverse.harvard.edu` → account menu → **API Token** → Create. It is a user-level credential (treat like a password); read it from `DATAVERSE_API_TOKEN` in the environment, never commit it.
- **Permissions:** the token's user needs *create dataset* in the target collection (`{{DATAVERSE_COLLECTION}}`), which **must already exist and be published**; publishing may require a curator/admin role or trigger a review workflow on some installations.
- **Test safely:** dry-run against the demo instance `https://demo.dataverse.org` (free, throwaway DOIs) before touching production `https://dataverse.harvard.edu`. Preflight: token set? collection reachable (`GET /api/dataverses/{alias}`)? on a gap, print "missing X → set/grant via Y" and degrade a tier rather than aborting.

## Project artifact → Dataverse mapping

| Project artifact | `categories` | `directoryLabel` | Notes |
| --- | --- | --- | --- |
| `data/processed/*` | `Data` | `data/processed` | `tabularTagIngest=true` for `.csv`/`.tab`; never deposit `data/raw` if sensitive |
| `src/<pkg>/`, `Snakefile`/`_targets.R`, `config.yaml` | `Code` | `code` | the re-runnable pipeline; link `{{REPO_URL}}` in metadata too |
| `README.md`, `DATA-DICTIONARY.md`, `data-card.md`, `knowledge/` (OKF) | `Documentation` | `documentation` | so a reader can interpret the data |
| name / PI / contact / description / subject / license | citation `metadataBlocks` | — | `{{PROJECT_NAME}}`, `{{PI_NAME}}`, `{{CONTACT_EMAIL}}`, `{{DESCRIPTION}}`, `{{DATASET_SUBJECT}}`, `{{LICENSE}}` |

## Artifacts it implies

→ `templates/dataverse/dataset.json.tmpl` (citation manifest), `templates/dataverse/deposit-dataverse.sh.tmpl` (curl) + `templates/dataverse/deposit_dataverse.py.tmpl` (pyDataverse), `templates/dataverse/DEPOSIT.md.tmpl` (guide), `templates/ci/dataverse-deposit.yml.tmpl` (scheduled versioned re-deposit, emitted when `UPDATING`), and the `data-project-depositor` agent. Emitted at L5 when `{{DATAVERSE}}`; the `data-management-plan` (L4) names the deposit target and records the DOI, and `release-and-share` (L3) triggers the deposit at release.

## When most relevant

L5, when the project is publishing finished outputs and wants a citable archive: strong signal on "deposit," "Dataverse," "Harvard Dataverse," "get a DOI," "archive the data," "FAIR / findable," "publish the dataset to a repository." Pairs with the OKF bundle (open-knowledge description), the Data Card, and `LICENSE-NOTE` (the deposited license).

## Caveats / conflicts

Publication mints a DOI and is effectively permanent — default to a reviewable **draft** and gate publish behind explicit confirmation. The sensitivity coupling is load-bearing here: never deposit sensitive-human/regulated/Indigenous traces openly — apply the `GOVERNANCE.md` access tiers (`restrict=true`, or desensitize, or withhold) and finish the `data-bulletproofing-checklist` + `responsible-data-checklist` first. The target collection must exist and be published before deposit; `subject` must come from the controlled list above; and the deposited data should be the regenerable `data/processed` output plus the pipeline, not a frozen one-off.

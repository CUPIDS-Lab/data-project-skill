---
type: Reference
title: OpenSharing Protocol (zero-copy data & AI asset sharing)
description: How a data project shares its data and AI assets across organizations in place — zero-copy, via temporary scoped credentials — using the OpenSharing protocol (Linux Foundation, Delta-Sharing-compatible). Covers the Share→Schema→Asset model, the Table/Volume/AgentSkill/Model asset types, the recipient profile + credential-vending flow, the project-artifact→asset mapping, and how access tiers govern what enters a share.
resource: https://github.com/OpenSharing-IO/OpenSharing
tags: [accessible, transparent, fair, collaborative, sharing, opensharing]
---

# OpenSharing Protocol

How a finished project shares its outputs as *live, governed, zero-copy* access rather than a copy — the L5 sharing surface, sibling to the OKF knowledge bundle (which shares the *understanding*), the ARD catalog (which *advertises* resources), and the Dataverse deposit (which archives a *frozen, citable copy*). Source: [OpenSharing](https://github.com/OpenSharing-IO/OpenSharing) — "the open sharing protocol for the agentic era," a Linux Foundation AI & Data project (Apache 2.0), backward-compatible with [Delta Sharing](https://delta.io/sharing/) clients.

## In one paragraph

OpenSharing lets a provider share assets that **stay in their own object storage**: a recipient discovers what's shared over a REST API and, per asset, is vended **short-lived, scoped credentials** (AWS STS, Azure SAS, GCP OAuth, or Cloudflare R2) to read it directly — no data is moved or duplicated. Assets are organized **Share → Schema → Asset**, where an asset is a **Table** (Delta/Iceberg/Parquet), a **Volume** (a directory of files), an **AgentSkill** (an AgentSkills-spec capability), a **Model**, or — as community proposals — an **Agent** or **Page**. This skill maps the project it scaffolded onto that model (processed tables, file/doc volumes, and the project's `.skills/`) and emits a share declaration plus a recipient profile and a `SHARING.md` guide, so the project can be shared in place under the same access tiers that govern it.

## Key practices (sampleable units)

- **Zero-copy, credential-vended access** [accessible, transparent] — the provider never ships data; the recipient calls a per-asset endpoint (`POST {prefix}/shares/{share}/schemas/{schema}/tables/{table}/temporary-table-credentials`, and the `…/volumes/{volume}/…` / `…/skills/{skill}/…` analogues) and receives `awsTempCredentials` | `azureUserDelegationSas` | `gcpOauthToken` | `r2Credentials` with an `expirationTime`. Least privilege and revocation are built in: the credential is scoped to one asset's storage location and expires.
- **Share → Schema → Asset hierarchy** [documented] — a **Share** (`{name, id?, displayName?, comment?, properties?}`) groups **Schemas** (`{name, share}`), each grouping assets. Discovery is REST: `GET {prefix}/shares`, `GET {prefix}/shares/{share}/schemas`, then `…/schemas/{schema}/tables` (or `/volumes`, `/skills`) and the `…/all-tables` cross-schema variants — each returning `{ "items": [...], "nextPageToken": ... }`.
- **Typed assets carry storage + format** [documented, accessible] — a **Table** is `{name, schema, share, format ("delta"|"iceberg"), location, accessModes (["url"]|["dir"]|["url","dir"])}`; a **Volume** is `{name, schema, share, storageLocation}`; an **AgentSkill** is `{name (lowercase/digits/hyphens, ≤64, matches the skill dir), schema, share, description, storageLocation, license, compatibility, allowedTools, metadata?}` following the [AgentSkills](https://agentskills.io/specification) directory structure.
- **Recipient profile is a small JSON** [accessible] — a consumer holds a Delta-Sharing-style profile: `{"shareCredentialsVersion": 1, "endpoint": "https://…/open-sharing/", "icebergEndpoint": "…/iceberg/" (optional), "bearerToken": "<token>", "expirationTime": "<ISO 8601>" (optional)}`. Auth is a bearer token — **a secret**: the filled profile is gitignored, never committed.
- **AgentSkills bridge to discovery** [transparent] — the AgentSkill asset is the *same* `.skills/` the ARD `ai-catalog.json` advertises: ARD says a skill **exists**, OpenSharing grants **scoped access** to fetch it. Sharing data and sharing capability use one protocol.

## Project artifact → OpenSharing asset mapping

| Project artifact | OpenSharing asset | Object fields it fills |
| --- | --- | --- |
| `data/processed/*` as Delta/Iceberg/Parquet | **Table** | `format`, `location` (object-store path), `accessModes` |
| `data/` file directories, `documentation/`, `knowledge/` (OKF) | **Volume** | `storageLocation` |
| `.skills/<name>` (AgentSkills) | **AgentSkill** | `description`, `storageLocation`, `license`, `compatibility`, `allowedTools` |
| trained models, if any | **Model** | version + provenance metadata |
| project name / description / license / contact | Share `displayName` / `comment` / `properties` | — |

## Capability & degradation chain (what the skill does)

The skill emits the **declaration**; it does **not** run a sharing server or vend credentials — that is the provider's infrastructure (an OpenSharing/Delta-Sharing-compatible server in front of S3/GCS/Azure/R2). Never fail the scaffold on missing infra; degrade and record the gap.
- **A — full declaration:** write `opensharing/share.json` mapping the project's tables/volumes/skills onto Share/Schema/asset objects, plus `share-profile.example.json` (recipient profile) and `SHARING.md` (serve + consume).
- **B — placeholders + roadmap:** when the storage base or server endpoint is unknown, fill `{{SHARE_STORAGE_BASE}}`/`{{OPENSHARING_ENDPOINT}}` with clearly-marked placeholders and record "stand up the sharing server + point it at storage" as `ROADMAP.md` items.
- **D — always:** `SHARING.md` is written regardless, so serving and consuming are reproducible off-skill (provider config + the Delta-Sharing client snippet for recipients).
- **Verification (recipient side):** a Delta-Sharing client (`delta-sharing` Python, Spark, DuckDB, …) loads the profile and lists/reads the share — proof the declaration matches what the server exposes.

## Artifacts it implies

→ `templates/opensharing/share.json.tmpl` (Share/Schema/asset declaration), `templates/opensharing/share-profile.example.json.tmpl` (recipient profile, token gitignored), `templates/opensharing/SHARING.md.tmpl` (serve + consume + governance). Emitted at L5 when `{{OPENSHARING}}`; `release-and-share` (L3) offers it at release and the `data-management-plan` (L4) names it as the live-access sharing channel.

## When most relevant

L5, when a project wants to give partners or other organizations **access without handing over a copy**: strong signal on "share the data," "zero-copy," "data sharing," "OpenSharing," "Delta Sharing," "share with another org / a partner," "give access without copying," "share an agent skill or model." Pairs with the `GOVERNANCE.md` access tiers (which decide what enters a share), the ARD catalog (the skills), and the Dataverse deposit (the frozen, citable copy).

## Caveats / conflicts

It is a *protocol*, not a file: serving a share needs a running OpenSharing/Delta-Sharing server plus object storage — `share.json` is a declaration you map onto that server's config, not a spec-defined artifact the server reads directly. Sharing **in place** makes governance *continuous*, not one-time: access is controlled by what you put in the share and by rotating/revoking the bearer token and scoped credentials — so the sensitivity coupling is load-bearing. Never place identifiable, regulated, or Indigenous-data (CARE) assets in an open share; apply the `GOVERNANCE.md` access tiers first (scope the recipient, desensitize, or withhold) and finish the `responsible-data-checklist`. Scoped, expiring credentials are a control, not a license to share what shouldn't be shared. Bearer tokens are secrets — the filled profile never enters the repo.

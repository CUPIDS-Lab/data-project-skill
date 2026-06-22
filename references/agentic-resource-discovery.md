---
type: Reference
title: Agentic Resource Discovery (ARD)
description: An open, federated spec for publishing a machine-readable catalog (`ai-catalog.json`) of a project's agentic resources — skills, MCP servers, A2A agents, datasets, APIs — so agents can discover them. The project's L5 agent-discovery layer, paired with the OKF bundle.
resource: https://agenticresourcediscovery.org/spec/
tags: [accessible, transparent, discovery, agents, fair]
---

# Agentic Resource Discovery (ARD)

An open, vendor-neutral discovery spec (announced 2026 by Google, Hugging Face, Microsoft, GitHub, Snowflake and others; Apache-2.0, draft ~v0.9) for cataloging a project's **agentic resources** so agents can find them without preloading every tool into a context window. Source: https://agenticresourcediscovery.org/spec/ · publishing guide: https://agenticresourcediscovery.org/how_to_publish/ · schemas: https://github.com/ards-project/ard-spec.

## In one paragraph

ARD is a small JSON manifest, `ai-catalog.json`, that advertises what a publisher exposes — A2A agents, MCP servers, **Markdown skills**, datasets, APIs, or nested catalogs — as a list of typed entries an agent can browse or index. It is to *agent discovery* what the OKF bundle is to *open knowledge*: a durable, plain-format publishing layer this skill emits at **L5**, so a published data project's nested `.skills/`, its datasets, and any service it runs become discoverable. Discovery is deliberately separated from execution — the catalog only points at resources; agents invoke them through each resource's own protocol.

## Key practices (sampleable units)

- **One manifest, `ai-catalog.json`** [transparent, accessible] — a JSON object with a required `specVersion` (currently the string `"1.0"`), a recommended `host` object (`displayName`, optional `identifier` such as `did:web:<domain>`, `documentationUrl`, `logoUrl`), and a required `entries` array.
- **Each entry is a typed pointer** [documented] — required `identifier` (a domain-anchored URN `urn:ai:<domain>:<namespace>:<name>`, matching `^urn:ai:[a-zA-Z0-9.-]+(:[a-zA-Z0-9._-]+)+$`), `displayName`, and `type` (an IANA media type), plus **either** `url` **or** `data` (mutually exclusive — never both). Optional: `description`, `tags`, `capabilities` (named skills/tools for filtering without fetching the artifact), `representativeQueries` (2–5 natural-language examples for semantic indexing), `version`, `updatedAt` (ISO 8601), `metadata`, and a `trustManifest` (verifiable identity).
- **Media types name the resource** [documented] — de-facto values include `application/a2a-agent-card+json`, `application/mcp-server+json`, `application/ai-catalog+json` (a nested catalog), `application/ai-registry+json` (a live search endpoint), `application/ai-skill` / `application/ai-skill+md` (a Markdown skill — what this toolkit's nested `.skills/` are), and ordinary data types like `application/parquet`. The spec treats these as community standards and tells consumers to omit strict verification, so new resource kinds need no spec change.
- **Deploys across a hierarchy of levels** [accessible] — the same manifest is published at escalating scopes: **repo** (checked into version control), **host/domain** (served at `https://<domain>/.well-known/ai-catalog.json` with `Content-Type: application/json`, `Access-Control-Allow-Origin: *`, over HTTPS), and **org/ecosystem registry** (a curated, searchable endpoint with `POST /search` and federation, e.g. Hugging Face Discover or a Google Agent Registry). Higher scopes are an ops/deployment step, not a code change.
- **Multiple discovery routes** [accessible] — agents find the manifest via the well-known URI, a `robots.txt` `Agentmap:` directive, an HTML `<link rel="ai-catalog">`, or DNS records; registries can federate by referral with a depth limit. (Confirm the exact directive spellings against the spec's discovery section.)

## Artifacts it implies

- → `templates/ard/ai-catalog.json.tmpl`, generated into the project root at **L5** when the project exposes ≥1 agentic resource (its nested `.skills/`, a dataset, an MCP/A2A service). The entry shapes above are the cheat-sheet for adding dataset/MCP/A2A entries beyond the default skills entry.
- → `templates/ard/DISCOVERY.md.tmpl`, a short companion that documents what the catalog advertises and the checklist to **promote** it to the host (`/.well-known/`) and registry levels — the deferred higher deployment scopes.

## When most relevant

Publishing a data project so agents can discover and use it: it has nested `.skills/`, ships a dataset others should find, or exposes an MCP server / A2A agent / data API. Strong signal on "make it discoverable by agents," "ARD," "ai-catalog," "agent registry," "well-known catalog." **L5**; pairs with the OKF bundle (knowledge for humans/tools), the Data Card, and the OpenSharing share kit (which grants scoped access to the resources ARD advertises).

## Caveats / conflicts

Discovery is not execution — ARD advertises resources; it does not run them, transform data, or replace MCP/A2A. It is the *agent-facing* discovery layer, complementary to the OKF bundle's *human/tool-facing* knowledge layer (advertise the dataset in ARD; describe it in OKF). Only advertise resources that actually exist and that you intend to be discoverable; domain-anchored URNs mean the `host` domain is the trust anchor, so publish from a domain you control. Host- and registry-level publishing are deployment steps deferred to `ROADMAP.md` unless explicitly in scope.

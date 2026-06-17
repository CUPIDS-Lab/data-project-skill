---
type: Reference
title: Open Knowledge Format (OKF)
description: A vendor-neutral format for representing knowledge as plain Markdown files with YAML frontmatter, organized into "bundles" of linked concepts — the project's L5 knowledge/publish layer.
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
tags: [accessible, transparent, documented, fair, knowledge]
---

# Open Knowledge Format (OKF)

A universal, vendor-neutral format (from Google Cloud's knowledge-catalog project) for representing knowledge as plain Markdown with YAML frontmatter, so humans, agents, and tools can produce and consume metadata without lock-in. Source: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf

## In one paragraph

OKF turns a project's knowledge into a "bundle": a directory tree of Markdown "concept" files, each with light YAML frontmatter and a prose body, linked into a graph. It is deliberately minimal and permissive, which makes it a good open, durable knowledge layer for a published dataset — the L5 artifact this skill emits from the data dictionary, and the shared hand-off point with the `data-liberation` skill's concept catalogs.

## Key practices (sampleable units)

- **Concepts are Markdown + frontmatter** [documented, accessible] — every non-reserved `.md` file is a concept with a YAML frontmatter block; the **only required field is `type`** (a non-empty string like `Dataset` or `Table`), with optional `title`, `description`, `resource` (a canonical URI), `tags`, and `timestamp`.
- **Bundles group concepts by type** [documented] — concepts live in subdirectories such as `datasets/` and `tables/` as `<type>/<name>.md`; reserved filenames `index.md` and `log.md` are not concepts.
- **Bundle-relative links form a graph** [transparent, accessible] — cross-link with paths beginning `/` (e.g. `/tables/customers.md`); links are treated as untyped directed edges, so the bundle renders as a knowledge graph.
- **Conventional body sections** [documented] — use `# Schema`, `# Examples`, and `# Citations` where applicable.
- **Permissive conformance** [accessible] — consumers must not reject a bundle over missing optional fields, unknown keys, or broken links; the bundle root `index.md` may declare `okf_version: "0.1"`.

## Artifacts it implies

- → `templates/okf/{index,log,concept,dataset,table}.md.tmpl`, generated into the project's `knowledge/` directory from `DATA-DICTIONARY.md`. The toolkit's own `references/` are themselves OKF-conformant (every file has a `type`), so they double as a worked example.

## When most relevant

Publishing a dataset as open knowledge, building a concept catalog/crosswalk, or pursuing FAIR. Strong signal on "open knowledge," "OKF," "concept catalog," "knowledge graph," "publish the dataset." L5; pairs with the Data Card.

## Caveats / conflicts

It is a knowledge-layer format, not a pipeline or a schema validator — it documents and links, it does not transform. The table-lookup crosswalk in `INDEX.md` scales to dozens of frameworks; OKF bundles scale similarly, but very large catalogs may want tooling to generate indices and the graph view.

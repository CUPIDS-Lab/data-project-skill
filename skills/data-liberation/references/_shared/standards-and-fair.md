---
type: Reference
title: Standards and FAIR
description: FAIR made explicit and measurable (sub-principles, FAIR-DSM maturity, FAIR is not open, CARE reconciliation, CITATION/codemeta/FAIR-CHECKLIST artifacts) mapped to Outline sections, plus the DCAT, PROV, DQV and DWBP standards and the FAIRsharing and re3data registries — optional, never a gate.
resource: https://doi.org/10.1038/sdata.2016.18
tags: [fair, care, standards, dcat, prov, dqv, dwbp, metadata, registries]
---

<!-- Vendored from shared/references/standards-and-fair.md by tools/vendor.py. Edit shared/references/standards-and-fair.md, not this copy. -->

# Standards and FAIR

Read this in Outline section 6 (Document & cite) and section 8 (Publish), and in section 9 (Deposit, share & discover) when a DOI or catalog is in play. It names the standards the skills' artifacts already practice, maps FAIR to the sections that satisfy it, and sketches the optional path to deeper conformance. **Conformance is never a precondition for shipping.** A tidy CSV with a data dictionary and a provenance trail is already doing most of what these standards exist to encourage; they are a vocabulary for naming that work and a menu for extending it, reached for only when a real consumer benefits. The one thing in this area that does gate is CARE, which belongs to `values-and-gates.md`.

## Contents

- [Why this reference exists](#why-this-reference-exists)
- [FAIR, explicit and measurable](#fair-explicit-and-measurable)
- [FAIR is not open: the CARE reconciliation](#fair-is-not-open-the-care-reconciliation)
- [FAIR facets mapped to Outline sections](#fair-facets-mapped-to-outline-sections)
- [Machine-actionable, not questionnaire-driven](#machine-actionable-not-questionnaire-driven)
- [Beyond data: software, workflows, models](#beyond-data-software-workflows-models)
- [FAIR artifacts](#fair-artifacts)
- [Open-data standards profiled](#open-data-standards-profiled)
- [Four lenses on open data](#four-lenses-on-open-data)
- [Crosswalk: standards to what the skills already build](#crosswalk-standards-to-what-the-skills-already-build)
- [Using standards responsibly](#using-standards-responsibly)
- [Source map](#source-map)

## Why this reference exists

Three things are true at once:

1. **The skills already embody these standards.** `provenance.csv` is a hand-rolled W3C PROV record; `metadata.yaml` and the data dictionary are a DCAT-shaped catalog entry; the quality dimensions and audit outputs parallel the W3C Data Quality Vocabulary; immutable originals, open formats and permanent links track the Sunlight policy principles. Naming them earns interoperability cheaply and tells downstream users which conventions the project adopted.
2. **None of them is a requirement the skills impose.** Civic data work is constrained by the source, records-request timelines and a one-to-three-person team. A standard that would block shipping is worse than no standard.
3. **Knowing the landscape prevents reinvention.** When a domain already has a standard (a repository's required metadata, an agency's exchange schema, a journal's deposit policy), reusing it beats inventing a parallel scheme. The registries exist so you can look first.

## FAIR, explicit and measurable

FAIR (Wilkinson et al. 2016, `10.1038/sdata.2016.18`) is the exception the skills practice explicitly: each sub-principle maps to an Outline section and a checkable indicator, and small machine-readable files make FAIRness legible to people and agents.

**The principles (verbatim).** **Findable** — F1 (meta)data are assigned a globally unique and persistent identifier; F2 data are described with rich metadata; F3 metadata clearly and explicitly include the identifier of the data they describe; F4 (meta)data are registered or indexed in a searchable resource. **Accessible** — A1 (meta)data are retrievable by their identifier using a standardized communications protocol; A1.1 the protocol is open, free, and universally implementable; A1.2 the protocol allows for an authentication and authorization procedure where necessary; A2 metadata are accessible even when the data are no longer available. **Interoperable** — I1 (meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation; I2 (meta)data use vocabularies that follow FAIR principles; I3 (meta)data include qualified references to other (meta)data. **Reusable** — R1 richly described with a plurality of accurate and relevant attributes; R1.1 a clear and accessible data-usage license; R1.2 detailed provenance; R1.3 meet domain-relevant community standards.

**FAIR is a continuum ("FAIR enough").** The FAIRification literature is emphatic that there is "neither one specific technology to implement, nor one magic solution," that FAIR is "a journey" scored by maturity, and that goals should be scoped and realistic; the FAIRplus process even advises against putting the word "FAIR" in a project's own goals because it is "too general to impart clear meaning." This is the grounding for right-sizing: you don't make a project FAIR in one shot, you raise its maturity facet by facet as sections come into scope, and record the rest as deferred outcomes in `ROADMAP.md`.

**The FAIR-DSM maturity model** ("FAIR in action," Welter et al. 2023, `10.1038/s41597-023-02167-2`; the FAIR Cookbook, Rocca-Serra et al. 2023, `10.1038/s41597-023-02166-3`) scores three aspects, **Content**, **Representation/Format** and **Hosting**, on an ordinal scale from Level 0 ("single-use") up to "community level." Use it to describe where a project stands on each aspect in the FAIR checklist, not as a target to max out ("one should not chase a 100% score at any cost").

## FAIR is not open: the CARE reconciliation

FAIR is not the same as open. A1.2 (authentication and authorization where necessary) keeps restricted data FAIR: a private or embargoed dataset with rich metadata, a persistent identifier, and access under governance tiers is FAIR. The CARE Principles (Collective benefit, Authority to control, Responsibility, Ethics) can pull against FAIR's push toward discoverability for data about Indigenous and other historically surveilled communities. When they conflict, CARE governs the access decision and FAIR governs the form of whatever is released; the metadata can be findable while the data stays under community authority. FAIR also omits quality, ethics, preservation and governance; those come from `quality-and-bulletproofing.md`, `responsible-data.md`, `governance.md` and the values spine.

## FAIR facets mapped to Outline sections

| FAIR facet | Satisfied by | Outline section |
| --- | --- | --- |
| F2, R1 — rich metadata and attributes | data dictionary (every column: type, units, missingness, caveats); data card; `codemeta.json` when a package is released | 4 (Model & tidy), 6 (Document & cite) |
| R1.1 — license | `LICENSE` plus the README License section (per-layer: data, code, docs) | 6 |
| R1.2 — provenance | `provenance.csv` per extract, immutable hashed originals, pipeline-as-code, decision-log | 2 (Acquire), 3 (Extract), 5 (Pipeline & audit) |
| R1.3, I1–I3 — community standards, vocabularies, qualified links | controlled vocabularies in lookup files enforced by a test; concept catalog with caveats; OKF bundle; JSON-LD | 4, 9 (Deposit, share & discover) |
| F1 — persistent identifier | Dataverse DOI (DataCite) | 9 |
| F3 — identifier embedded in metadata | `dataset.json`, `ai-catalog.json`, OKF frontmatter, `CITATION.cff` | 6, 9 |
| F4 — indexed and searchable | repository deposit, ARD `ai-catalog.json`, a DCAT record harvested into a portal | 9 |
| A1, A1.1 — open, standard protocol | HTTPS access to the published surface or deposit; OpenSharing | 8 (Publish), 9 |
| A1.2 — authentication where needed | governance access tiers; restricted deposit files; OpenSharing scoped credentials | 7 (Govern & collaborate), 9 |
| A2 — metadata outlive data | metadata deposited and indexed independently of the payload | 9 |
| The whole map, self-assessed | `docs/FAIR-CHECKLIST.md` | 8 for public outputs; 9 for a deposit |

A private project that never publishes can still meet R1, R1.1 and R1.2 fully; F1, F4 and A2 wait for section 9.

## Machine-actionable, not questionnaire-driven

FAIR "mandates machine-actionable behavior," so its assessment "should be completely automated" (Wilkinson et al. 2019, `10.1038/s41597-019-0184-5`). Model each FAIR checklist item on a **Maturity Indicator**: an id, the principle it tests, a rationale, a precise machine test, and a success or failure criterion. That lets an item graduate from a human checkbox to a CI test; a FAIR-compliance CI job is a deferred outcome in `ROADMAP.md`, not a default. The metadata standards that make this possible form a concrete menu: **schema.org / JSON-LD**, **DCAT**, **DataCite** (DOIs), **ORCID** (people), **CodeMeta** (software), **CITATION.cff** (citation), **Croissant** (ML datasets), **RO-Crate** (workflows and packaging), **CRediT** (contributor roles).

## Beyond data: software, workflows, models

FAIR applies to the whole research-object family: software (FAIR4RS, Barker et al. 2022, `10.1038/s41597-022-01710-x`; the CODE roadmap, Di Cosmo et al. 2026, `10.1038/s41597-026-06705-6`), workflows (`10.1038/s41597-025-04451-9`) and AI models (`10.1038/s41597-023-02298-6`). Unlike data, software FAIR "should start… when it is initially being developed": a forge, an explicit license, identified authors and a citation file are cheap from the first commit (the CODE roadmap's *Open* and *Document* steps), so `LICENSE` and `CITATION.cff` belong to section 6 from the start. Deeper object-specific FAIR (a Workflow RO-Crate with run provenance for the pipeline, a model card with uncertainty metrics for a published model, `codemeta.json` for a released package) is added when the project actually ships that object.

## FAIR artifacts

- **`CITATION.cff`** (repository root; section 6) — how to cite the data and code; GitHub renders BibTeX and APA from it. Use real release dates, never placeholder dates.
- **`codemeta.json`** (repository root; section 6) — software metadata, generated only when the project releases a package.
- **`docs/FAIR-CHECKLIST.md`** (section 8 or 9) — per-principle self-assessment with the FAIR-DSM aspect levels, generated when a public release or deposit is in scope.
- They pair with the OKF bundle, the ARD `ai-catalog.json` and the Dataverse deposit (F1, F3, F4), and with the governance access tiers (A1.2).

## Open-data standards profiled

| Framework | History | Precedents | Standards body | Adopters | Infrastructure |
| --- | --- | --- | --- | --- | --- |
| **Sunlight Open Data Policy Guidelines** | Drafted 2007–2014; static archive after Sunlight wound down its open-government work (~2020) | The 8 Principles of Open Government Data (2007); FOIA tradition | Sunlight Foundation (archived); mirrored by US Ignite | Municipal and state open-data programs; civic-tech advocates | 10 principles + 32 model provisions in 3 categories |
| **DCAT-US** | Began as the Project Open Data metadata schema under OMB M-13-13 (2013); v3 modernizes it on the Evidence Act | W3C DCAT, Dublin Core, Project Open Data | US federal CDO Council and FCSM, profiling W3C DCAT | Federal agencies; many state and local governments | `data.gov` catalog and validator; JSON-LD / RDF |
| **W3C DCAT and the Data Activity vocabularies** | DCAT a Recommendation 2014 (v2 2020, v3 2024); PROV-O 2013; DQV 2016 | Semantic Web / Linked Data; RDF | W3C | National data portals; CKAN and Socrata ecosystems | DCAT, PROV-O, DQV, Org, RDF Data Cube |
| **W3C Data on the Web Best Practices (DWBP)** | Working group chartered 2013; Recommendation 2017 | DCAT, PROV, the FAIR conversation | W3C | Data publishers broadly | 35 best practices plus a use-cases document |
| **FAIR principles** | 2016 (Wilkinson et al.) | Earlier data-stewardship and e-science norms | FORCE11; stewarded via RDA and others | Funders, journals, repositories | 15 guiding principles |
| **FAIRsharing** | Grew from BioSharing (~2011) | FAIR; community standards curation | RDA-affiliated; community-curated | Journals, funders, repositories, researchers | Registry interlinking standards, databases and policies, with an API |
| **re3data** | Launched 2012 (DFG-funded) | Library and repository cataloging | KIT and Purdue University Libraries | Research libraries, funders, publishers | Registry of 3,000+ research-data repositories, schema and API |
| **NIEM** | Began 2005 from DOJ/DHS GJXDM; now NIEMOpen | GJXDM; W3C XML Schema | OASIS Open Project (NIEMOpen) | Justice, emergency response, health, child welfare | Reference and extension XML schemas; Naming and Design Rules; IEPDs |

Notes on the cells that need them:

- **Sunlight** is the publisher-side counterpart to data liberation: its ten principles (completeness, primacy, timeliness, ease of physical and electronic access, machine readability, non-discrimination, commonly owned standards, licensing, permanence, low or no usage cost) and 32 model provisions are the obligations whose absence is why liberation work exists. Immutable originals honor permanence, tidy CSVs machine readability, CC-BY defaults licensing.
- **DCAT-US** is a three-tier hierarchy, **Catalog → Dataset → Distribution**, with v3 adding **DataService** (APIs) and **DatasetSeries** (recurring releases). A project is a catalog, the processed table is a dataset, and the CSV, SQLite file or Datasette API are its distributions.
- **W3C vocabularies** beyond DCAT: **PROV-O** (Entity / Activity / Agent), **DQV** (data quality), the Organization ontology and the **RDF Data Cube** (multidimensional statistics, rarely worth the RDF overhead in civic work).
- **DWBP**'s 35 practices span metadata, licenses, provenance, quality, versioning, identifiers, formats, vocabularies, access and APIs, and republication. It is the best single "did we miss anything?" review lens, and it aligns with FAIR.
- **NIEM** is the heaviest standard here and the one to reach for least often: only when an agency partner mandates a NIEM exchange package.
- **US federal mandates** make some of this a legal duty for publishers: OMB M-13-13 and Project Open Data (2013), the OPEN Government Data Act (Title II of the Foundations for Evidence-Based Policymaking Act, 2019: open by default, machine-readable inventories, Chief Data Officers) and the DATA Act (2014, federal spending data). When a source is PDF-locked despite a mandate, cite the mandate in the README: that is the difference between nice-to-have and owed.

## Four lenses on open data

1. **Policy and governance: should this be open, and on what terms?** Sunlight's guidelines and the federal mandates. The questions (completeness, timeliness, non-discrimination, licensing, permanence, cost) are the ones section 1 and `governance.md` make a project answer. Normative, not about file formats.
2. **Cataloging and metadata interoperability: can a machine find and understand it?** DCAT-US, W3C DCAT and W3C *Publishing Open Government Data*. The data dictionary and `metadata.yaml` are this lens in miniature; a DCAT record is the optional step into federated catalogs.
3. **Domain standards and registries: has someone already solved this?** FAIRsharing, re3data and NIEM, consulted in section 1 and section 2 before inventing a schema or choosing a repository. Most civic projects find nothing binding and proceed, but the five-minute check is worth it.
4. **Web best practice and FAIR: is it good open data by a published yardstick?** DWBP and FAIR, used as a review pass in section 8 or 9 to catch a missing license, an unstable identifier or undocumented provenance.

## Crosswalk: standards to what the skills already build

| Standard | Already in the skills (cite it today) | Optional deepening (only if a consumer needs it) |
| --- | --- | --- |
| **DCAT-US v3 / W3C DCAT** | data dictionary, `metadata.yaml`, Datasette per-table and per-column metadata | Emit a `dcat-us.jsonld` record so the dataset federates into `data.gov`-style, CKAN or Socrata catalogs (section 8, portal publishing) |
| **W3C PROV-O** | `provenance.csv`, one row per source artifact and parser run, with `extraction_method` and `extraction_quality` | Map columns to PROV terms (source URL → Entity, parser run → Activity, project → Agent); serialize to PROV-JSON only if a graph consumes it |
| **W3C DQV + DWBP quality practices** | the quality dimensions, the audit outputs and the reconciliation report | Tag audit metrics with DQV dimension URIs and expose them in `metadata.yaml` |
| **FAIR** | tidy long tables, stable composite keys, the data dictionary, provenance, `CITATION.cff` | The FAIR checklist (section 8 or 9); Maturity-Indicator CI tests as a deferred outcome |
| **DWBP** | metadata, licensing, provenance, versioning, identifiers and access all have a home | A one-time DWBP review before a public release |
| **Sunlight 10 principles** | immutable originals, tidy CSVs, CC-BY defaults, open repositories | Self-assess a public release against the principles; record any the source violates as a finding |
| **FAIRsharing / re3data** | section 1 and 2 survey of prior work and existing standards | Consult them to find a domain standard to reuse or a repository to deposit in (section 9) |
| **NIEM** | per-source parsers plus the concept catalog | Map the canonical schema to an IEPD only when an agency partner mandates it |

## Using standards responsibly

- **Cite, don't conform for its own sake.** When an artifact already matches a standard, say so in the README or `AGENTS.md` ("provenance follows W3C PROV; metadata is DCAT-shaped"). Don't restructure a working pipeline to chase a badge.
- **Look before you invent.** Spend five minutes in FAIRsharing, re3data and the publisher's own metadata during scoping.
- **Never let conformance block shipping.** If a standard would delay a release, record it as a deferred outcome.
- **Record what you didn't adopt, and why** ("no DCAT-US JSON-LD: no federated-catalog consumer yet"). A one-line note is more honest than silent omission.
- **Let the standard catch the source's failures.** A source that fails permanence (dead links) or machine readability (scanned PDFs) is generating a finding worth recording.
- **Don't over-trust any single aggregator.** Follow the primary links below and verify figures before citing them.

## Source map

- **FAIR principles** — Wilkinson et al. 2016, <https://doi.org/10.1038/sdata.2016.18>; GO FAIR's summary at <https://www.gofair.foundation/fair-principles>.
- **CARE Principles** — <https://www.gida-global.org/careprinciples>.
- **Sunlight Open Data Policy Guidelines** — <https://opendatapolicyhub.sunlightfoundation.com/guidelines/> (archived); US Ignite mirror at <https://www.us-ignite.org/tools/data-standards-and-policies/open-data-policy-guidelines-sunlight/>.
- **DCAT-US** — <https://resources.data.gov/standards/catalog/dcat-us/>.
- **W3C DCAT 3** — <https://www.w3.org/TR/vocab-dcat-3/>; **PROV-O** — <https://www.w3.org/TR/prov-o/>; **DQV** — <https://www.w3.org/TR/vocab-dqv/>; the W3C Data Activity hub — <https://www.w3.org/2013/data/>.
- **W3C Data on the Web Best Practices** — <https://www.w3.org/TR/dwbp/>; use cases at <https://w3c.github.io/dwbp/usecasesv1.html>.
- **W3C *Publishing Open Government Data*** — <https://www.w3.org/TR/gov-data/>.
- **FAIRsharing** — <https://fairsharing.org/>.
- **re3data** — <https://www.re3data.org/>.
- **NIEMOpen** — <https://niemopen.org/> (the former `niem.gov` site).
- **CodeMeta** — <https://codemeta.github.io/>; **Citation File Format** — <https://citation-file-format.github.io/>.

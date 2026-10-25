# Lineage and landscape: where data liberation comes from, and the world it lands in

This reference is **background, not a gate**. It covers the civic-data liberation tradition the skill descends from, the critical perspectives that shape how its artifacts get built, and the open-government landscape around the data: transparency law, federal mandates, civic tech, data portals and international initiatives. Read it once at the start of a project, then return to the part a concrete need calls for. The only real gates in this territory are privacy law and the CARE Principles, which can mean *do not publish, or publish differently*; they are set out in [`_shared/values-and-gates.md`](_shared/values-and-gates.md). The open-data standards (DCAT, PROV, DQV, FAIR, DWBP, Sunlight's guidelines) and the crosswalk to what the skill already builds are in [`_shared/standards-and-fair.md`](_shared/standards-and-fair.md).

## Contents

- [Part 1: The movement and its critics](#part-1-the-movement-and-its-critics)
  - [Why "liberation"?](#why-liberation)
  - [Lineage of civic liberation projects](#lineage-of-civic-liberation-projects)
  - [What the lineage teaches](#what-the-lineage-teaches)
  - [The lineage is US-centric: the international frame](#the-lineage-is-us-centric-the-international-frame)
  - [Critical perspectives worth absorbing](#critical-perspectives-worth-absorbing)
  - [Academic framing](#academic-framing)
  - [Liberation as infrastructure](#liberation-as-infrastructure)
  - [How to use this in a project](#how-to-use-this-in-a-project)
- [Part 2: The open-government landscape](#part-2-the-open-government-landscape)
  - [The five themes](#the-five-themes)
  - [Gaps and tensions, and how the skill responds](#gaps-and-tensions-and-how-the-skill-responds)
  - [Institutional publishing: the portal layer](#institutional-publishing-the-portal-layer)
  - [Referenced-resources catalog](#referenced-resources-catalog)
  - [Using the landscape responsibly](#using-the-landscape-responsibly)
- [Further reading](#further-reading)

---

# Part 1: The movement and its critics

Two intertwined traditions ground the skill: the **civic data liberation movement** (an activist response to the inaccessibility of public data) and the **academic table-and-document understanding literature** (the methodological response to the same problem). They are the same struggle viewed from different sides. This part shapes how a project frames its README, what it cites in `AGENTS.md`, and which design decisions are worth defending.

## Why "liberation"?

Tables and figures in PDF documents are arguably the dominant medium of public-record data: financial reports, statements of vote, FOIA responses, regulatory filings, scientific articles, statistical abstracts. The format suits publishers and human readers and is hostile to machines. A PDF table is a set of rendering instructions: text strokes positioned on a page, sometimes with line strokes that suggest, but do not declare, a grid. Reconstructing the relational structure is a research problem (see [Academic framing](#academic-framing)); doing it across many documents at scale is a civic infrastructure problem.

The term enters from the activist side. Tom Lee at the Sunlight Foundation, [writing in early 2014](https://sunlightfoundation.com/2014/01/24/pdf-liberation-why-it-matters-and-how-you-can-help/), argued that government PDFs lock public data inside a format that is technically open but practically closed. The fix is not to scold publishers into better formats, a slow battle civil society has been losing for decades, but to build durable tooling and shared corpora that move data out of PDFs into analyzable form. Sunlight organized a PDF Liberation Hackathon in 2014, and the [PDF Liberation Working Group](https://github.com/pdfliberation) on GitHub became a clearinghouse for tools and conventions. The phrase stuck because it names the politics: the data was already public, but extraction labor was the gate.

## Lineage of civic liberation projects

A short, opinionated genealogy. Each project taught the community something this skill encodes.

### Sunlight Foundation and the PDF Liberation Hackathon (2013–2014)

Sunlight's post coined the framing and the hackathon scaffolded the first wave of shared tooling. The lessons that survived: PDF extraction is per-document craft (no universal parser), open-source toolchains accumulate value across projects, and *most of the value is in documentation*: without provenance and a data dictionary, an extracted CSV is barely more useful than the PDF. Sunlight also produced the policy counterpart, the [Open Data Policy Guidelines](https://opendatapolicyhub.sunlightfoundation.com/guidelines/) (10 principles, 32 model provisions), which describe what publishers *should* do; that standards view is in [`_shared/standards-and-fair.md`](_shared/standards-and-fair.md).

### NPP / Tax Break: Recovery Act spending (2010s)

The [NPP tax-break project](https://github.com/npp/tax-break/tree/master) showed that patient, source-by-source extraction could produce a longitudinal dataset from federal disclosure PDFs that researchers and journalists could query. It pioneered the convention, now ubiquitous, of treating each agency-and-year PDF as its own parser, with a thin schema-conformance layer above.

### MuckRock and FOIA-driven liberation (2010s to now)

[MuckRock](https://www.muckrock.com/) industrialized FOIA requests and accumulated a corpus of agency releases, mostly PDFs of wildly variable quality. The [BU Spark × MuckRock liberation project](https://github.com/BU-Spark/ds-muckrock-liberation/tree/main) is one of several student-team efforts to turn that corpus into reusable structured data. The lesson: the corpus is heterogeneous, the long tail is huge, and pragmatic per-document parsers with good provenance beat any universal extractor.

### PUDL: Public Utility Data Liberation (Catalyst Cooperative, 2017 to now)

[PUDL](https://github.com/catalyst-cooperative/pudl) is the mature reference for infrastructural liberation: a multi-source ETL pipeline that harmonizes FERC, EIA and EPA energy data into a unified relational database with rigorous documentation, versioning and CI. Its conventions (raw and processed data kept apart, source-by-source ingest modules, comprehensive data dictionaries, vintage tracking, CI-built artifacts) directly inform this skill's project template. PUDL also shows that academic-quality data infrastructure can be sustained as an open-source project with public funding.

### BoulderPublicData: Election-Results and Cast-Vote-Records (2020s)

[Boulder Public Data](https://github.com/BoulderPublicData) shows the small-scale modern shape of liberation work: one to three contributors, a single domain (elections), heavy automation. [Election-Results](https://github.com/BoulderPublicData/Election-Results) harmonizes 2004–2024 precinct-level statements of vote from Boulder County and the Colorado Secretary of State into a tidy long dataset, with a `reconcile.py` that re-opens the originals to verify the processed totals match, an audit pattern worth copying wherever a source carries an authoritative total. [Cast-Vote-Records](https://github.com/BoulderPublicData/Cast-Vote-Records) liberates anonymized ballot-level data using Colorado's risk-limiting audit framework as the legal mechanism. Both use `uv`, an agent instructions file and `data/original/` → `data/processed/` → `data/audit/` → `data/lookups/`, the layout adopted here.

## What the lineage teaches

- **Per-source, per-vintage parsers.** No universal PDF extractor. Each new layout era is a parser file. Resist generalizing early.
- **Immutable originals.** The source files are part of the dataset: hash them, keep them (in git, Git LFS or durable storage), and never edit them in place.
- **Tidy long as canonical storage; wide as analysis output.** Storage rewards uniformity; analysis rewards locality.
- **Documentation is half the work.** A liberation without a data dictionary, a crosswalk and a provenance trail is a private spreadsheet. The point is reuse.
- **Audit against originals.** A pipeline that doesn't reconcile against its source is faith-based; reconciliation is what makes the dataset defensible.

## The lineage is US-centric: the international frame

The genealogy above is entirely US and Anglophone, and so are the skill's default tools (GitHub, CC-BY, Datasette). That is a deliberate scope boundary, not a claim that liberation is a US phenomenon, and an agent working elsewhere should know which parts transfer. The **principles** are universal: immutable originals, tidy long form, per-extract provenance, reconciliation against the source's own totals. The **implementation assumptions** are not: the license regime (CC-BY may not be the local norm; some states prefer national public-domain or open licenses), portal software (much of the world publishes through **CKAN**, stewarded by the **Open Knowledge Foundation**, rather than a self-hosted Datasette), hosting, and document language. The international scaffolding (the **Open Government Partnership**, the **International Open Data Charter**, OKFN, the **World Bank Open Government Data Toolkit**, and fiscal-transparency bodies such as the **International Budget Partnership**) is catalogued in [Part 2](#part-2-the-open-government-landscape). When localizing, keep the principles and name the assumptions you swap.

## Critical perspectives worth absorbing

The lineage above is told from inside the movement. Four arguments from outside change how the artifacts get built.

**The skill's working self-description: *empowering intermediary*** (Baack 2015, *Big Data & Society*). Open-data activists carry three open-source practices into the data domain:

1. *Raw data as source code.* Sharing the underlying records, not just summaries, breaks the publisher's interpretive monopoly. Implication: the **data dictionary and per-extract provenance** are the load-bearing artifacts; every documented sentinel value and every `extraction_quality` flag is a small act of that breaking. "Raw" means *as collected*, not mythically neutral: the dictionary's job is transparency about the choices, not their denial.
2. *The bazaar model applied to participation.* Self-selected contribution to the *governance* of data, not just its consumption. Implication: reviewable refresh pull requests and opt-in workflows are how a project performs this; someone who notices an error can fix it without going through official channels.
3. *Empowering intermediaries.* Raw data alone doesn't empower citizens; someone must build the intermediary layer. Baack's three criteria: *data-driven* (handles real datasets), *open* (publishes sources alongside conclusions) and *engaging* (cooperative, not broadcast). The README should name the downstream intermediaries the project serves (journalists, researchers, NGOs, advocates), not only the end readers.

**A vocabulary for what a project is doing** (Schrock 2016, *New Media & Society*). Civic-data work has five modes, and a healthy project does several:

| Mode | What it is | Project example |
| --- | --- | --- |
| **Request** | Extract data from where it's locked | Scrape a portal; file a FOIA or open-records request |
| **Digest** | Interpret and make legible | Concept catalog, dictionary, crosswalks |
| **Contribute** | Add to the shared corpus | Publish a tidy CSV with provenance |
| **Model** | Build a prototype that demonstrates use | A Quarto explainer, a Datasette canned query |
| **Contest** | Name what's missing or wrong | An audit that calls out the publisher's gaps; reconcile failures published |

The pipeline naturally covers *Request* (Outline sections 2–3) and *Contribute* (sections 4–5 and 8). *Digest*, *Model* and *Contest* need explicit space in the README and documentation, or the project ships a dataset without the politics that justify the work. Schrock's argument: machine-readable release without interpretation reproduces "naked transparency" (Lessig), which is not accountability.

**Three problems open data alone doesn't solve** (Johnson 2014, *Ethics and Information Technology*, building on Saitta's "data sovereignty must trump open data"). The skill encodes these as caveat-writing requirements, not warnings to skip:

1. **Embedded privilege.** Datasets carry social privilege from the moment they are constructed (census undercounts; *Bhoomi* land records excluding Dalit claims documented only orally; net-price calculators that mislead first-generation students). The data dictionary's caveats should answer, per variable: *who is over- or under-represented in this source, and why?*
2. **Differential capabilities.** Open data is "dominated by state and business users… 'citizen-open' pales in comparison to 'enterprise-open'." Tutorials and filter-pivot recipes exist to flatten this asymmetry; without them, a project just supplies new feedstock for police and ad tech. `AGENTS.md` and the README should name uses that are out of scope (enrichment for enforcement, predictive policing, eviction targeting).
3. **Disciplinary normalization.** Data systems impose norms through their function: IPEDS reifies the four-year, residential, full-time student; *Gainful Employment* metrics discipline institutions toward one outcome shape. When a project's schema mirrors the publisher's, it inherits the publisher's disciplinary structure; naming that in `AGENTS.md` or the decision-log is the floor.

**Data culture inside an institution is plural and contested** (Casemajor 2025, *Big Data & Society*). The "build a data culture" framing is mistaken not because there is too little data work but because there is too much: archivists, librarians, marketers, lawyers, executives and open-data advocates all say "data" with different action logics and incompatible standards (MARC versus ISAD(G), heritage versus AI training, KPI dashboards versus professional craft). A liberation project inside such an institution shouldn't try to resolve those tensions. It should name the surplus explicitly in `AGENTS.md`, let the data dictionary give contested terms more than one definition (one per stakeholder reading), and expect contributors from different functions to disagree, not as a failure of governance but as its substrate.

## Academic framing

Three durable ideas from the methodology literature trace the skill's scoping decisions; each is operational, named so the skill's commitments are auditable.

**CRISP-DM and what this skill targets.** The Cross-Industry Standard Process for Data Mining (Wirth and Hipp 2000) divides a data project into business understanding, data understanding, data preparation, modeling, evaluation and deployment. This skill targets **data understanding, preparation and deployment** and stops short of modeling, which belongs to the analyst once liberation is done. CRISP-DM also names the under-specified phase, *data understanding*. Holstein et al.'s (2024) five-dimension expansion of it (Foundations, Collection and Selection, Contextualization and Integration, Exploration and Discovery, Insights) maps roughly onto the skill's artifacts: probe findings ≈ Insights; the data dictionary ≈ Foundations; the concept catalog ≈ Contextualization; the audit summary ≈ Exploration. The point isn't the taxonomy; it's that the artifacts answer the questions the phase poses.

**Table Understanding.** A useful vocabulary when probing a new source. The document-analysis community splits the table problem into two subproblems and seven tasks (Shigarov 2023):

```
Table Understanding (TU)
├── Table Extraction (TE)
│   ├── Table Detection (TD)              <- find table regions
│   ├── Table Structure Recognition (TSR) <- recover rows, columns, cells
│   ├── Table Functional Analysis (TFA)   <- header vs data; cell roles
│   └── Table Structural Analysis (TSA)   <- relationships between cells
└── Table Interpretation (TI)
    ├── Table Canonicalization (TC)       <- to relational form
    ├── Table Normalization (TN)          <- to 3NF; entity resolution
    └── Semantic Table Interpretation (STI) <- match to a knowledge graph
```

A liberation project touches all of TE plus the canonicalization and normalization halves of TI. Semantic interpretation (matching to Wikidata or DBpedia) is a research frontier rarely worth the cost in civic work; the concept catalog with caveats handles cross-source entity resolution well enough. The audit that matters is reconciliation against the source's own printed totals, not benchmark scores; benchmark corpora (PubTabNet, FinTabNet, SciTSR, ICDAR) are useful as parser-test fixtures, not as targets to optimize against. Which extraction tools to reach for, and when model-based parsers earn their cost, is in the `extract-*.md` references.

**Tidy data.** Wickham's "Tidy Data" (2014) anchors the storage shape: one row per observation, one column per variable, one cell per value. Mature civic projects converge on it because unions, audits and dictionaries become uniform operations. The cost, that long form is awkward to read by eye, is bridged by shipping filter-pivot recipes with the dataset. `data-modeling.md` has the operational form.

## Liberation as infrastructure

A liberation project is *installed infrastructure* that other people will depend on. A complete one covers six components:

| Component | What the project provides |
| --- | --- |
| **Linkability** | A stable schema and unique identifiers that downstream uses can join against |
| **Interpretability** | A data dictionary and a concept catalog with caveats |
| **Continuity** | A refresh workflow that survives the original developer leaving |
| **Safe scrutiny** | A reconciliation report, an audit log, immutable originals, visible provenance |
| **Authority** | A documented legal basis: FOIA, an open-records law, a statutory disclosure |
| **Remedy** | A path for users and data subjects to flag errors, and for the project to correct them with the audit trail kept |

A project that supplies tidy data with no documented remedy, or processed data with no provenance, has built infrastructure with missing struts. The same six elements, as repository requirements tied to safeguards, form the values spine in [`_shared/values-and-gates.md`](_shared/values-and-gates.md).

## How to use this in a project

- **In the README,** cite the relevant lineage. Liberating government PDFs: name Sunlight's framing. Energy or utility data: point to PUDL. Elections: point to Boulder Public Data. The citations orient users (and agents) to the conventions adopted.
- **In `AGENTS.md`,** name the conventions followed: "Data is stored tidy (Wickham 2014); concepts follow the PUDL and IPEDS-pipeline pattern; reconciliation follows the BoulderPublicData/Election-Results model." This earns interoperability cheaply.
- **In the data dictionary,** when a concept spans sources, include the caveats; renaming variables across sources without them is malpractice.
- **In the audit,** say what the reconciliation does and does not catch, and document known unreconcilable vintages rather than papering over them.

---

# Part 2: The open-government landscape

Background, not a constraint on the workflow. Where [`_shared/standards-and-fair.md`](_shared/standards-and-fair.md) covers the technical standards the skill's artifacts implement, this part maps the civic and institutional landscape around them: how governments are *obliged* to publish (transparency law and open-data policy), who *consumes* liberated data (the civic-tech ecosystem), and how the work connects to *international* open-government efforts. Nothing here gates shipping a tidy CSV; it is a map of the territory the dataset lands in.

> **Source-quality note.** This material began as a synthesis of the *Open Government Platform* knowledge base (`opengovtplatform.org`), whose pages could not be fetched directly and were reconstructed through web search, so its site-specific particulars are approximate. Everything below is anchored on independently verifiable primary resources (data.gov, FOIA.gov, OGP, OKFN and CKAN, the World Bank toolkit, the Open Data Charter). Treat figures as indicative and verify them against the linked primaries before citing.

## The five themes

Each theme maps onto something the skill does, or marks a boundary it deliberately doesn't cross.

### 1. Open data: the publishing layer

Open data is public-sector information released in standardized, machine-readable, openly licensed form. The durable touchstones: the **8 Principles of Open Government Data** (Sebastopol, 2007, the ancestor of Sunlight's 10), the **3-star minimum** (CSV, JSON or XML before a dataset has earned a star for openness), and the federal lineage from `data.gov` (2009) through the metadata standard now called **DCAT-US**. Government **APIs** (`api.data.gov`, the Census and USAspending APIs) are the machine-to-machine face of the same idea; `extract-api.md` covers reading them.

*How the skill relates:* this is home turf. The gap is **institutional publishing**: the skill builds its own Datasette, Quarto and LFS surfaces but says little about federating back into a `data.gov`, CKAN or Socrata portal. See [Institutional publishing](#institutional-publishing-the-portal-layer) and the DCAT-export note in `publishing.md`.

### 2. Government transparency: the obligation layer

Transparency is the *why* beneath much liberation work: the federal **Freedom of Information Act** (1966, 5 U.S.C. § 552), state **sunshine and open-records laws**, spending disclosure (**USAspending.gov** and Treasury Fiscal Data, mandated by the **DATA Act** of 2014), and **whistleblower** protections. FOIA is a *process*, not just a source of PDFs: drafting a request, the roughly 20-business-day clock, fee categories (commercial, news media or educational, other), appeals, and redaction disputes.

*How the skill relates:* `pipeline.md` has the records-request process notes (ask for data rather than narrative, know the clock and fees, treat redactions as findings, decide what the project will not liberate). Transparency *politics* (when a redaction is excessive, what the project will refuse to publish) is a section 1 decision recorded in the decision-log.

### 3. Civic technology: the consumer and intermediary layer

Civic tech is the ecosystem that puts government data in front of people: reporting tools (**SeeClickFix**, 311), legislative trackers (**GovTrack**, **Councilmatic**, **OpenStates** and Open Civic Data), accountability databases (**OpenSecrets**, **Follow the Money**), and investigative journalism (**ProPublica**). Civic **hackathons** (from "Apps for Democracy," Washington DC, 2008) are how open data turns into demonstrations of use.

*How the skill relates:* the skill frames its output as feedstock for empowering intermediaries and names Schrock's five modes (see [Critical perspectives](#critical-perspectives-worth-absorbing)). What it underplays is the operational hookup: which export shape (bulk CSV, API, DCAT-cataloged) suits which downstream tool, and how to find and reach the journalists and NGOs a dataset is for rather than hoping they discover it. That stays a documentation concern for the README.

### 4. Policy and legislation: the mandate layer

The legal scaffolding that makes open data *owed*, not merely nice:

- **FOIA** (1966) and state **sunshine laws**: the request-driven floor.
- **OMB M-13-13** ("Open Data Policy: Managing Information as an Asset," 2013) and **Project Open Data**: the origin of the federal metadata schema that became **DCAT-US**.
- The **OPEN Government Data Act** (Title II of the **Foundations for Evidence-Based Policymaking Act**, 2019): makes "open by default" and machine-readable inventories a statutory duty for federal agencies, and creates agency **Chief Data Officers**.
- The **DATA Act** (2014): standardized federal spending data.
- Privacy counterweights: **GDPR** (Article 17 erasure), **CCPA**, and the **CARE Principles** for Indigenous Data Governance, which sit alongside FAIR and can pull the other way (collective authority and restricted access versus maximal openness).

*How the skill relates:* naming a mandate lets an agent prioritize (federally required but PDF-locked beats nice to have) and gives the README a citation for *why* the data should have been public. The privacy and CARE counterweights are the hard gates in [`_shared/values-and-gates.md`](_shared/values-and-gates.md); the FAIR-versus-CARE reconciliation is in [`_shared/standards-and-fair.md`](_shared/standards-and-fair.md).

### 5. Global initiatives: the international layer

Open government is not only a US story. The anchors: the **Open Government Partnership** (OGP, founded 2011; 75 or more member countries plus local jurisdictions, working through National Action Plans and an Independent Reporting Mechanism co-created with civil society); the **International Open Data Charter** (principles adopted by many national and subnational governments); the **Open Knowledge Foundation** (OKFN, steward of **CKAN**, the portal software behind data.gov, `open.canada.ca` and many national portals, and of the **Open Data Handbook**); fiscal-transparency bodies (**GIFT**, sunsetted in July 2025 with its materials hosted by the **International Budget Partnership**, and the **Open Budget Index**); and **Transparency International** and the **World Bank Open Government Data Toolkit**.

*How the skill relates:* this is the skill's biggest blind spot. Its lineage and tooling are US and Anglophone, a deliberate scope boundary that it names rather than closes; see [The lineage is US-centric](#the-lineage-is-us-centric-the-international-frame) for which principles transfer and which assumptions to localize.

## Gaps and tensions, and how the skill responds

| # | Gap or tension | Disposition |
| --- | --- | --- |
| 1 | **Institutional data portals:** the skill publishes its own surfaces and ignores federating into data.gov, CKAN or Socrata | A DCAT-export and CKAN note in `publishing.md`; [framing below](#institutional-publishing-the-portal-layer) |
| 2 | **Federal policy not encoded:** M-13-13, the Evidence Act, the DATA Act | Named in [theme 4](#4-policy-and-legislation-the-mandate-layer); cite the mandate in the README |
| 3 | **Civic-tech intermediaries named but not connected** | [Theme 3](#3-civic-technology-the-consumer-and-intermediary-layer) and the README's lineage and audience notes; a documentation concern |
| 4 | **CARE, GDPR and CCPA named but not operationalized** | Operationalized as hard gates in [`_shared/values-and-gates.md`](_shared/values-and-gates.md), decided in Outline section 1 |
| 5 | **International landscape absent:** OGP, OKFN, the Open Data Charter, SDMX, CKAN | [Theme 5](#5-global-initiatives-the-international-layer) and the international note in Part 1; a scope boundary, now named |
| 6 | **Transparency politics underexplored:** redaction disputes, what to refuse | [Theme 2](#2-government-transparency-the-obligation-layer) and the records-request notes in `pipeline.md` |

## Institutional publishing: the portal layer

The skill's default deployment is *activist*: extract locked data, build its own Datasette, Quarto and LFS surfaces, host it yourself. That is the right starting point for a small liberation project. But when the audience is a city or agency open-data program, the expected endpoint is *their* portal, a **CKAN** or **Socrata** instance that harvests a **DCAT** catalog record. These are two different workflows:

- For **self-hosted** publishing, nothing changes: Datasette, Quarto and LFS (`publishing.md`).
- For **portal federation**, emit a DCAT-US catalog record alongside `metadata.yaml` (the note in `publishing.md` and the crosswalk in [`_shared/standards-and-fair.md`](_shared/standards-and-fair.md)) so the dataset can be harvested into data.gov-style discovery. Only when a portal consumer exists.
- For **citable archiving**, a DOI-minting repository such as Harvard Dataverse or Zenodo; that is Outline section 9, led by the data-project skill.

This is the load-bearing tension between the institutional, federated, global landscape and the small-team, self-hosted, US skill. Naming it is the fix; turning the skill into a portal CMS is not.

## Referenced-resources catalog

A load-on-demand catalog of primary, verifiable sources, grouped by purpose. Status notes flag resources that have sunsetted; verify before relying on any of them.

### Federal data and API portals

- **data.gov** — <https://data.gov/> — the US federal open-data catalog.
- **api.data.gov** — <https://api.data.gov/> — a unified API-key gateway across federal APIs.
- **Census Bureau APIs** — <https://developer.census.gov/> — demographic, economic and housing data.
- **USAspending.gov** and its API — <https://www.usaspending.gov/> and <https://api.usaspending.gov/> — federal contracts, grants and loans (DATA Act).
- **Treasury Fiscal Data** — <https://fiscaldata.treasury.gov/> — official budget and financial datasets and APIs.

### Portal software, standards and toolkits

- **CKAN** — <https://ckan.org/> — the open-source portal platform behind data.gov and many national portals; speaks DCAT.
- **DCAT** and **FAIR** — see [`_shared/standards-and-fair.md`](_shared/standards-and-fair.md).
- **Open Civic Data** — <https://open-civic-data.readthedocs.io/> — schemas for governments, officials, legislation and events (OpenStates lineage).
- **8 Principles of Open Government Data** — <https://opengovdata.org/> — the 2007 foundational principles.
- **World Bank Open Government Data Toolkit** — <https://opendatatoolkit.worldbank.org/> — implementation guidance for open-data programs.
- **Open Data Handbook** (OKFN) — <https://opendatahandbook.org/> — a practical how-to for opening data.

### Transparency and access to information

- **FOIA.gov** — <https://www.foia.gov/> — official federal FOIA guidance and request routing.
- **Reporters Committee for Freedom of the Press** — <https://www.rcfp.org/> — legal resources for journalists seeking records.
- **State sunshine and open-records laws** — these vary by state; the publisher's records officer is the entry point (see `pipeline.md`).

### Money in politics and accountability

- **OpenSecrets** — <https://www.opensecrets.org/> — federal campaign finance and lobbying.
- **Follow the Money** — <https://www.followthemoney.org/> — state-level campaign finance.
- **GAO** — <https://www.gao.gov/> — the congressional audit and watchdog agency.
- **Office of Special Counsel** — <https://osc.gov/> — federal whistleblower protection.
- **POGO** — <https://www.pogo.org/> — nonpartisan government-oversight investigations.

### Civic-tech and civil-society organizations

- **Code for America** — <https://codeforamerica.org/> — civic-tech tools and the Brigade network.
- **Open Knowledge Foundation** — <https://okfn.org/> — the global open-data nonprofit; stewards CKAN and the Open Data Handbook.
- **OpenTheGovernment** — <https://www.openthegovernment.org/> — an open-government advocacy coalition.

### International initiatives and frameworks

- **Open Government Partnership** — <https://www.opengovpartnership.org/> — the multilateral open-government initiative (National Action Plans, the Independent Reporting Mechanism).
- **International Open Data Charter** — <https://opendatacharter.org/> — shared open-data principles across governments.
- **Transparency International** — <https://www.transparency.org/> — global anti-corruption work; the Corruption Perceptions Index.
- **International Budget Partnership** — <https://internationalbudget.org/> — fiscal transparency, the Open Budget Survey and Index; hosts legacy **GIFT** materials (GIFT sunsetted July 2025).
- **World Bank, Open Government** — <https://www.worldbank.org/en/topic/governance> — global open-government programs.

### Privacy and compliance

- **GDPR** — the EU data-protection regime (Article 17, the right to erasure); the global reference standard.
- **Data Privacy Framework** — <https://www.dataprivacyframework.gov/> — transatlantic data-transfer compliance.
- **CARE Principles for Indigenous Data Governance** — <https://www.gida-global.org/careprinciples> — Collective benefit, Authority to control, Responsibility, Ethics.

## Using the landscape responsibly

- **Cite the mandate, don't just extract.** When a source is legally owed (the Evidence Act, M-13-13, a state sunshine law), say so in the README: it is the strongest justification for the work and orients users.
- **Match the surface to the audience.** A self-hosted Datasette for an activist release; a DCAT record for portal federation; a DOI deposit for researchers who need to cite. Don't build machinery the project doesn't need.
- **Localize before you globalize.** Outside the US the principles transfer, but the license regime, portal software, language and hosting need local judgment. Name the assumptions you carry.
- **Let privacy law and CARE actually constrain.** Unlike most of this territory, they can mean *do not publish, or publish differently*; treat them as gates ([`_shared/values-and-gates.md`](_shared/values-and-gates.md)).
- **Don't over-trust any one aggregator.** Follow the primary links and verify figures before citing them.

---

## Further reading

Activist and movement tradition:

- Tom Lee (Sunlight Foundation), [*PDF Liberation: Why It Matters And How You Can Help*](https://sunlightfoundation.com/2014/01/24/pdf-liberation-why-it-matters-and-how-you-can-help/), 2014
- [PDF Liberation Working Group](https://github.com/pdfliberation) on GitHub
- [catalyst-cooperative/pudl](https://github.com/catalyst-cooperative/pudl), the multi-source ETL reference
- [BoulderPublicData/Election-Results](https://github.com/BoulderPublicData/Election-Results), the small-team liberation pattern
- [ProPublica's data-bulletproofing guide](https://github.com/propublica/guides/blob/master/data-bulletproofing.md), the journalistic standard for vetting a dataset before publishing it (applied in [`_shared/quality-and-bulletproofing.md`](_shared/quality-and-bulletproofing.md))

Consumer-side practice, adjacent to this skill rather than within it:

- [NYT data-training](https://github.com/nytimes/data-training), the *New York Times* newsroom training materials for data journalists: brainstorming story angles from a dataset, verification habits that prevent common misreadings, and editorial review of data stories. Spreadsheet-first by audience, but the methodological content is what a liberation hands off to. Point users there from the README rather than reinventing consumer-side methodology in the pipeline's docs.

Critical and scholarly tradition:

- Schrock, *Civic hacking as data activism and advocacy: A history from publicity to open government data*, *New Media & Society*, 2016
- Baack, *Datafication and empowerment: How the open data movement re-articulates notions of democracy, participation, and journalism*, *Big Data & Society*, 2015
- Johnson, *From open data to information justice*, *Ethics and Information Technology*, 2014
- Casemajor, *Data cultures: Contested meanings in a public cultural institution*, *Big Data & Society*, 2025

Methodological and academic tradition:

- Wirth and Hipp, *CRISP-DM: Towards a standard process model for data mining*, 2000
- Holstein, Spitzer, Hoell, Vössing and Kühl, *Understanding Data Understanding: A Framework to Navigate the Intricacies of Data Analytics*, ECIS 2024
- Shigarov, *Table understanding: Problem overview*, *WIREs Data Mining and Knowledge Discovery*, 2023
- Kasem et al., *Deep Learning for Table Detection and Structure Recognition: A Survey*, *ACM Computing Surveys*, 2024
- Göbel, Hassan, Oro and Orsi, *A Methodology for Evaluating Algorithms for Table Understanding in PDF Documents*, DocEng 2012
- Long, Wang, Xue, Gao, Yang, Wang and Xia, *Parsing Table Structures in the Wild*, ICCV 2021
- Wickham, *Tidy Data*, *Journal of Statistical Software*, 2014
- Tamir Hassan's [Table Understanding Competition pages](https://tamirhassan.com/html/competition.html), historical competition datasets and evaluation
- [tanfiona/LLM-on-Tabular-Data-Prediction-Table-Understanding-Data-Generation](https://github.com/tanfiona/LLM-on-Tabular-Data-Prediction-Table-Understanding-Data-Generation), a maintained survey of LLM and table work with a curated benchmark catalog

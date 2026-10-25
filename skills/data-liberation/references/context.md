# Context: the movement, the standards, and the open-government landscape

This reference is **background, not a gate**. It collects three complementary framings the skill descends from and operates within: the **civic-data liberation tradition** (the activist and academic lineage that shapes why the conventions look the way they do), the **open-data standards** the skill's artifacts already informally implement (named here to deepen and to cite, never to block shipping), and the **open-government landscape** — transparency law, civic tech, federal mandates, and international initiatives — around the data. Hold one thing throughout: the *only* real gates in this document are **privacy law (GDPR/CCPA) and the CARE Principles**, which can mean *do not publish, or publish differently*. Everything else here is advisory — a vocabulary for talking about the work and a menu for extending it, not a precondition for a tidy CSV with a data dictionary and a provenance trail. Read it once at the start of a new project, then reach for the relevant part when a concrete need arises.

The three parts are the same struggle viewed from different sides: Part 1 tells it from the **activist and academic** side (getting public data *out*), Part 2 from the **standards / policy** side (how institutions agree to publish it *well*), and Part 3 from the **civic and institutional** side (the laws, consumers, and global efforts the data lands in). A skilled data liberator draws on all three.

---

# Part 1 — Movement history: data liberation as activism and method

This part grounds the skill in two intertwined traditions: the **civic data liberation movement** (an activist response to the inaccessibility of public data) and the **academic table-and-document understanding literature** (the methodological response to the same problem). They are the same struggle viewed from different sides, and a skilled data liberator draws on both. It shapes how you frame the README, what citations belong in the AGENTS.md, and which design decisions are worth defending.

## Why "liberation"?

Tables and figures in PDF documents are arguably the dominant medium of public-record data communication: budget reports, statements of vote, FOIA responses, regulatory filings, scientific articles, statistical abstracts. The format is convenient for publishers and human readers, and deeply hostile to machine readability. A PDF table is, in computational terms, a set of rendering instructions: text strokes positioned on a page, sometimes accompanied by line strokes that suggest (but do not declare) a grid. Reconstructing the relational structure is a research problem (see [academic framing](#academic-framing) below); reconstructing it across many documents at scale is a civic infrastructure problem.

The term "liberation" enters from the activist side. Tom Lee at the Sunlight Foundation, [writing in early 2014](https://sunlightfoundation.com/2014/01/24/pdf-liberation-why-it-matters-and-how-you-can-help/), framed the problem this way: government PDFs lock up public data inside a format that is technically open but practically closed. The fix is not to scold publishers into using better formats (a slow battle that civil society has been losing for decades), but to build durable tooling and shared corpora that move data out of PDFs and into analyzable form. The Sunlight Foundation organized a PDF Liberation Hackathon in 2014; the [PDF Liberation Working Group](https://github.com/pdfliberation) on GitHub became a clearinghouse for tools and conventions. The phrase stuck because it names the underlying politics: the data was already public, but extraction labor was the gate.

## Lineage of civic liberation projects

A short, opinionated genealogy. Each project taught the community something that this skill encodes.

### Sunlight Foundation and the PDF Liberation Hackathon (2013–2014)

Sunlight's blog post coined the framing and the hackathon scaffolded the first wave of shared tooling. The lessons that survived: PDF extraction is per-document craft (no universal parser), open-source toolchains accumulate value across projects, and *most of the value is in documentation* (without provenance and a data dictionary, an extracted CSV is barely more useful than the original PDF).

Sunlight also produced the *policy* counterpart to this activist history: the [Open Data Policy Guidelines](https://opendatapolicyhub.sunlightfoundation.com/guidelines/) (10 principles, 32 model provisions) that describe what publishers *should* do — the obligations whose absence makes liberation necessary. That standards-and-policy view, alongside DCAT-US, the W3C vocabularies, FAIR, and the research-data registries, lives in [Part 2](#part-2--open-data-standards-as-background) as background context for naming and optionally deepening what a project already does.

### NPP / Tax Break — Recovery Act spending (2010s)

The [NPP tax-break project](https://github.com/npp/tax-break/tree/master) was an early demonstration that *patient, source-by-source extraction* could produce a longitudinal dataset from federal disclosure PDFs that researchers and journalists could query. It pioneered the convention — now ubiquitous — of treating each agency × year PDF as its own parser, with a thin schema-conformance layer above.

### MuckRock and the FOIA-driven liberation (2010s–ongoing)

[MuckRock](https://www.muckrock.com/) industrialized FOIA requests and accumulated a corpus of agency releases, mostly PDFs of wildly variable quality. The [BU Spark × MuckRock liberation project](https://github.com/BU-Spark/ds-muckrock-liberation/tree/main) is one of several student-team efforts to turn that corpus into reusable structured data. The lesson: the corpus is heterogeneous, the long tail is huge, and pragmatic per-document parsers + good provenance beats any universal extractor.

### PUDL — Public Utility Data Liberation (catalyst-cooperative, 2017–ongoing)

[PUDL](https://github.com/catalyst-cooperative/pudl) is the mature reference for infrastructural liberation: a multi-source ETL pipeline that harmonizes FERC, EIA, EPA energy data into a unified relational database with rigorous documentation, versioning, and CI. PUDL's conventions — `data/raw/` ↔ `data/processed/`, source-by-source ingest modules, comprehensive data dictionaries, vintage tracking, CI-built artifacts — directly inform the project template in this skill. PUDL also demonstrates that an academic-quality data infrastructure can be sustained as an open-source project with public funding.

### BoulderPublicData — Election-Results and Cast-Vote-Records (2020s)

[Boulder Public Data](https://github.com/BoulderPublicData) shows the small-scale modern shape of liberation work: 1–3 contributors, single-domain (elections), heavy automation. [Election-Results](https://github.com/BoulderPublicData/Election-Results) harmonizes 2004–2024 precinct-level statements of vote from Boulder County and the Colorado Secretary of State into a tidy long-form dataset, with a `reconcile.py` that re-opens originals to verify the processed totals match — an audit pattern worth stealing for any pipeline where the source carries an authoritative top-line. [Cast-Vote-Records](https://github.com/BoulderPublicData/Cast-Vote-Records) liberates anonymized ballot-level data using Colorado's Risk-Limiting Audit framework as the legal mechanism. Both repos use `uv` + AGENT.md + `data/original/` ↔ `data/processed/` ↔ `data/audit/` ↔ `data/lookups/` — the convention adopted here.

### What the lineage teaches

Across these projects a few hard-won patterns recur:

- **Per-source, per-vintage parsers.** No universal PDF extractor. Each new vintage is a parser file. Resist the urge to generalize prematurely.
- **Immutable originals.** The source files are part of the dataset. Hash them, commit them (or LFS them), and never edit them in place.
- **Tidy long-form as canonical storage; wide as analysis output.** Storage rewards uniformity; analysis rewards locality. Don't fight the trade.
- **Documentation is half the work.** A liberation without a data dictionary, a crosswalk, and a provenance trail is a private spreadsheet. The point is reuse.
- **Audit against originals.** A pipeline that doesn't reconcile against its source is faith-based. Reconciliation is what makes the dataset defensible.

### The lineage is US-centric — the international frame

The genealogy above (Sunlight, MuckRock, PUDL, BoulderPublicData, NPP) is entirely US and Anglophone, and so are the skill's default tools (GitHub, CC-BY, Datasette). That is a *deliberate scope boundary*, not a claim that liberation is a US phenomenon — and an agent working elsewhere should know which parts transfer. The **principles** are universal: immutable originals, tidy long-form, per-extract provenance, reconciliation against the source's own totals. The **implementation assumptions** are not: license regime (CC-BY may not be the local norm; some states prefer national public-domain or open licenses), portal software (much of the world publishes through **CKAN**, stewarded by the **Open Knowledge Foundation**, rather than a self-hosted Datasette), hosting, and document language. The international scaffolding — the **Open Government Partnership** (National Action Plans co-created with civil society), the **International Open Data Charter**, OKFN, the **World Bank Open Government Data Toolkit**, and fiscal-transparency bodies (the **International Budget Partnership** / Open Budget Index) — is catalogued in [Part 3](#part-3--open-government-landscape). When localizing, keep the principles and name the assumptions you're swapping.

### Critical perspectives worth absorbing

The lineage above is told from inside the movement. Four claims from outside change how the artifacts get built:

**The skill's working self-description: *empowering intermediary*** (Baack 2015, *Big Data & Society*). Open-data activists modulate three open-source practices into the data domain:

1. *Raw data as source code* — sharing the underlying records, not just summaries, breaks the publisher's interpretive monopoly. Implication: the **data dictionary and per-extract provenance** are the load-bearing artifacts; every documented sentinel value, every `extraction_quality` flag is a small act of that breaking. "Raw" means *as collected*, not mythically neutral — the dictionary's job is transparency about the choices, not their denial.
2. *Bazaar model applied to political participation* — self-selective contribution to *governance* of data, not just *consumption* of it. Implication: the **PR-reviewable refresh diffs** and opt-in workflows are how the project performs this — contributors who notice an issue can fix it without going through official channels.
3. *Empowering intermediaries* — raw data alone doesn't empower citizens; the project must build the intermediary layer. Baack's three criteria for an empowering intermediary are *data-driven* (handles real datasets), *open* (publishes sources alongside conclusions), and *engaging* (cooperative, not broadcast). **Empowering intermediary** is the right working self-description for a civic-data project; the README's *movement context* section should name the downstream intermediaries (journalists, researchers, NGOs, advocates) the project is for, not the end-readers.

**A vocabulary for what any specific project is doing** (Schrock 2016, *New Media & Society*). Civic-data work has five distinct modes; a healthy project does several:

| Mode | What it is | Project example |
|---|---|---|
| **Request** | Extract data from where it's locked | Scrape a portal; file FOIA/CORA |
| **Digest** | Interpret and make legible | Concept catalog, dictionary, crosswalks |
| **Contribute** | Add to the shared corpus | Publish a tidy CSV with provenance |
| **Model** | Build a prototype that demonstrates use | A Quarto explainer, a Datasette canned query |
| **Contest** | Name what's missing or wrong | An audit that calls out the publisher's gaps; reconcile failures published |

The skill's six-phase workflow naturally covers *Request* (discover/fetch) and *Contribute* (clean/publish). It's harder to make sure a project also *Digests*, *Models*, and *Contests* — those need explicit space in the README and the Quarto site, or the project ships a dataset without the politics that justify the work. Schrock's argument: machine-readable release without interpretation reproduces "naked transparency" (Lessig), which is not accountability.

**Three problems open data alone doesn't solve** (Johnson 2014, *Ethics and Information Technology*; building on Saitta's "data sovereignty must trump open data"). The skill encodes these as caveat-writing requirements, not as warnings to skip:

1. **Embedded privilege.** Datasets carry social privilege from the moment they're constructed (Census undercount; *Bhoomi* land records excluding Dalit claims documented only orally; net-price calculators that mislead first-generation students). The data dictionary's caveat section should answer per variable: *who is over- or under-represented in this source, and why?*
2. **Differential capabilities.** Open data is "dominated by state and business users… 'citizen-open' pales in comparison to 'enterprise-open'." The Quarto tutorials and filter-pivot recipes exist to flatten this asymmetry; without them, the project just supplies new feedstock for police and ad-tech. AGENTS.md should name uses that are *out of scope* (e.g., enrichment for enforcement, predictive policing, eviction targeting).
3. **Disciplinary normalization.** Data systems impose norms via their function — IPEDS reifies the four-year residential full-time student; *Gainful Employment* metrics discipline institutions toward a particular outcome shape. When the project's schema mirrors the publisher's, it inherits the publisher's disciplinary structure. Naming that explicitly in `AGENTS.md` design-decisions is the floor.

**Data culture inside any institution is plural and contested, not coherent** (Casemajor 2025, *Big Data & Society*). The "build a data culture" framing is mistaken not because there is *too little* data work but because there's *too much* — archivists, librarians, marketers, legal, executives, and open-data advocates all use the word "data" with different action logics and incompatible standards (MARC vs ISAD(G), heritage vs AI-training, KPI dashboards vs professional craft). A liberation project deployed inside such an institution shouldn't try to resolve those tensions; **`AGENTS.md` should name the surplus problem explicitly**, the **data dictionary should let contested terms have multiple definitions** (one row per stakeholder reading), and the project should expect contributors from different functional areas to disagree — not as a failure of governance but as the substrate.

## Academic framing

The skill's scoping decisions trace to three durable ideas from the methodology literature. Each one is operational, not theoretical — they're named here so the skill's commitments are auditable.

**CRISP-DM and what this skill targets.** The Cross-Industry Standard Process for Data Mining (Wirth & Hipp 2000) divides a data project into six phases: business understanding, data understanding, data preparation, modeling, evaluation, deployment. This skill targets **data understanding, preparation, and deployment** and deliberately stops short of modeling — the rest belongs to the analyst after liberation is done. The CRISP-DM framing also names the under-specified phase: *data understanding*. Holstein et al.'s (2024) five-dimension expansion of it (Foundations / Collection & Selection / Contextualization & Integration / Exploration & Discovery / Insights) maps roughly onto the skill's artifacts — Survey notes ≈ Insights; data dictionary ≈ Foundations; concept catalog ≈ Contextualization; `audit.py` output ≈ Exploration. The point isn't the taxonomy; it's that the artifacts answer the questions the phase poses.

### Table Understanding (TU)

A useful vocabulary when surveying a new source. The document-analysis community decomposes the table problem into two subproblems and seven tasks (Shigarov 2023):

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

A liberation project touches all of TE plus the canonicalization and normalization halves of TI. Semantic interpretation (matching to Wikidata/DBpedia) is a research frontier rarely worth the cost in civic work — the concept catalog with caveats handles cross-source entity resolution at a sufficient level.

**Use rule-based / heuristic tools first** (pdfplumber, camelot). Deep-learning table extractors (TableFormer, CascadeTabNet, GTE) are impressive on average but rarely worth the operational cost for civic data — per-document craft remains more reliable, and the output is auditable. Reach for ML extractors only when classical methods genuinely fail, and prefer open-source extractors with reproducible behavior over closed LLM-based parsers. The audit that matters is *top-line reconciliation against the source's own published total*, not benchmark scores. Benchmark corpora (PubTabNet, FinTabNet, SciTSR, ICDAR) are useful as *fixtures* for parser tests but not as targets to optimize against.

**Tidy data.** Wickham's "Tidy Data" (2014) anchors the canonical storage shape: one row per observation, one column per variable, one cell per value. Every mature civic project converges on this because unions, audits, and dictionaries all become uniform operations. The trade — tidy long-form is awkward to read by eye — is bridged by shipping `docs/filter-pivot-recipes.md` with the dataset. See [`data-modeling.md#wickham-tidy-as-the-storage-shape`](data-modeling.md#wickham-tidy-as-the-storage-shape) for the operational form.

## Liberation as infrastructure

A useful checklist framing: a liberation project is *installed infrastructure* that other actors will depend on. Six components a complete project covers:

| Component | What the project provides |
|---|---|
| **Linkability** | Stable schema + unique identifiers downstream uses can join against |
| **Interpretability** | Data dictionary + concept catalog (with caveats) |
| **Continuity** | CI refresh workflow that survives the original developer leaving |
| **Safe scrutiny** | Reconciliation report; audit log; immutable originals; visible provenance |
| **Authority** | Documented legal framework — CORA / FOIA / statutory disclosure |
| **Remedy** | A path for downstream users to flag errors and for the project to correct them with the audit trail preserved |

A project that supplies tidy data but no documented remedy, or processed data but no provenance, has built infrastructure with missing struts.

## How to use this in a project

When you start a new liberation project:

- **In the README**, cite the relevant lineage. If you're liberating government PDFs, name Sunlight's framing. If it's energy or utility data, point to PUDL. If it's elections, point to Boulder Public Data. The citations are not throat-clearing — they orient downstream users (and AI assistants) to the conventions you've adopted.
- **In AGENTS.md**, name the academic conventions you've followed. "We store data tidy per Wickham 2014; harmonization concepts follow the IPEDS-pipeline / PUDL pattern; reconciliation follows the BoulderPublicData/Election-Results model." This earns interoperability cheaply.
- **In data-dictionary.md**, when documenting a concept that spans sources, *include the caveats*. The IPEDS pipeline's `concepts.py` is the model: every concept entry that crosses sources notes what is and isn't comparable. Renaming variables across sources without caveats is malpractice.
- **In the audit log**, note explicitly what the reconciliation report does and does not catch. If there are known unreconcilable years (legacy formats, mid-period schema changes), document them rather than papering over them.

The skill exists to make this kind of work cheaper to start and harder to do badly. The traditions above — activist and academic — are why the conventions look the way they do.

---

# Part 2 — Open data standards as background

This part is **background context**, not a checklist that gates the workflow. The skill's six-phase pipeline (Survey → Scaffold → Extract → Tidy → Audit → Publish) already *practices* most of what the official open-data standards prescribe — it just doesn't usually *name* them. The purpose is twofold: to let an agent **recognize and name** the standard a given artifact already informally implements (so it can cite it in the README or `AGENTS.md`), and to sketch the **optional** path to deeper conformance when a downstream consumer actually needs it.

Read it the way you'd read [Part 1](#part-1--movement-history-data-liberation-as-activism-and-method): once, to share the framing. Then forget it until a project gives you a concrete reason to reach for a specific standard. **Conformance is never a precondition for shipping a liberated dataset.** A tidy CSV with a data dictionary and a provenance trail is already doing the work these standards exist to encourage; the standards are a vocabulary for *talking about* that work and a menu for extending it, not a gate in front of it. Where Part 1 tells the open-data story from the **activist** side (PDF Liberation, MuckRock, PUDL — getting public data *out*), this part tells the complementary **standards / policy** side (how institutions agree to publish it *well*). They are the same struggle from two directions.

## Why this reference exists

Three things are true at once, and holding all three is the point:

1. **The skill already embodies these standards.** `provenance.csv` is a hand-rolled W3C **PROV** record; `metadata.yaml` is a **DCAT**-shaped catalog entry; the five-dimension quality framework parallels the W3C **Data Quality Vocabulary**; the immutable-originals / non-discrimination / permanence conventions track the **Sunlight** policy principles. Naming them earns interoperability cheaply and tells downstream users which conventions the project adopted.
2. **None of them is a requirement the skill imposes.** Civic liberation work is constrained by the source, the FOIA timeline, and a 1–3 person team. A standard that would block shipping is worse than no standard. Every item below is *optional deepening*, reached for only when a real consumer benefits.
3. **Knowing the landscape prevents reinvention.** When a domain already has a standard (a research repository's required metadata, an agency's NIEM exchange schema, a journal's deposit policy), reusing it beats inventing a parallel scheme. The registries below (FAIRsharing, re3data) exist precisely so you can *look first*.

## Standards profiled by theme

The nine sources organize cleanly along five recurring themes — **history** (when/why it emerged), **precedents** (what it built on), **standards organization** (who governs it), **institutions** (who adopts/runs it), and **infrastructure** (the concrete tooling/registries it ships). The matrix is the at-a-glance comparison; the per-source notes below add nuance where a cell needs it.

| Framework | History | Precedents | Standards org | Institutions | Infrastructure |
|---|---|---|---|---|---|
| **Sunlight Open Data Policy Guidelines** | Drafted 2007–2014, maintained as a static archive after Sunlight wound down its open-gov work (~2020) | The 8 Principles of Open Government Data (2007 Sebastopol meeting); FOIA tradition | Sunlight Foundation (archived); mirrored by **US Ignite** for continuity | Municipal & state open-data programs; civic-tech advocates | A policy framework: 10 principles + 32 model provisions in 3 categories |
| **DCAT-US** | Began as Project Open Data Metadata Schema under OMB **M-13-13** (2013); v3 modernizes it on the Evidence Act | W3C **DCAT** ← Dublin Core; Project Open Data | US Federal **CDO Council** + **FCSM**, profiling W3C DCAT | Federal agencies; many state/local govs | `data.gov` catalog + validator; JSON-LD / RDF serializations |
| **W3C DCAT & the Data Activity vocabularies** | DCAT a W3C Recommendation 2014 (v2 2020, v3 2024); PROV-O 2013; DQV 2016 | Semantic Web / Linked Data; RDF | **W3C** (Government Linked Data WG; Data Activity) | National data portals worldwide; CKAN/Socrata ecosystems | RDF vocabularies: DCAT, **PROV-O**, **DQV**, Org, RDF Data Cube |
| **W3C Data on the Web Best Practices (DWBP)** | WG chartered 2013; Recommendation 2017 | DCAT, PROV, the FAIR conversation | **W3C** Data on the Web Best Practices WG | Data publishers broadly (gov + research + commercial) | 35 best practices + a use-cases/requirements companion doc |
| **FAIR principles** | Articulated 2016 (Wilkinson et al., *Sci. Data*) | Earlier data-stewardship & e-science norms | **Force11** community; stewarded via RDA et al. | Funders, journals, repositories across the sciences | 15 guiding principles (Findable / Accessible / Interoperable / Reusable) |
| **FAIRsharing** | Grew from BioSharing (~2011) into cross-domain registry | The FAIR principles; community standards curation | **Research Data Alliance**–affiliated; community-curated | Journals, funders, repositories, researchers | A registry interlinking **standards ↔ databases ↔ policies**, with an API |
| **re3data** | Launched 2012 (DFG-funded) | Library/repository cataloging traditions | **KIT** + **Purdue University Libraries** (orig. w/ Helmholtz, HU Berlin) | Research libraries, funders, publishers | A registry of 3,000+ research-data repositories + metadata schema + API |
| **NIEM** | Began 2005 from DOJ/DHS **GJXDM** (justice-XML); now **NIEMOpen** | GJXDM; W3C XML Schema | **OASIS** Open Project (NIEMOpen); orig. DOJ/DHS/HHS | Justice, emergency-response, health, child-welfare agencies | Reference + extension XML schemas; Naming & Design Rules (NDR); IEPDs |

A few cells reward expansion:

- **Sunlight Open Data Policy Guidelines** — the *policy* counterpart to the skill's *activist* lineage. Its **ten principles** (completeness, primacy, timeliness, ease of physical and electronic access, machine readability, non-discrimination, use of commonly-owned standards, licensing, permanence, low/no usage costs) and **32 model provisions** ("what data should be public," "how to make data public," "how to implement policy") read as the publisher-side obligations whose absence is *why liberation work exists*. The skill already honors several (immutable originals → permanence; tidy machine-readable CSVs → machine readability; CC-BY defaults → licensing). US Ignite hosts a maintained mirror after Sunlight's wind-down.
- **DCAT-US** — the mandatory metadata standard behind `data.gov`. Its data model is a three-tier hierarchy — **Catalog → Dataset → Distribution** — with v3 adding **DataService** (APIs) and **DatasetSeries** (versioned/recurring releases). This is almost exactly the shape of the skill's published artifacts: a project is a *catalog*, the processed CSV is a *dataset*, and the CSV / SQLite / Datasette API are its *distributions*.
- **W3C Data Activity vocabularies** — beyond DCAT, the W3C stack includes **PROV-O** (provenance: Entity / Activity / Agent), **DQV** (data quality), the **Organization ontology**, and the **RDF Data Cube** (multidimensional statistics). The skill informally uses the first two; the Data Cube is occasionally relevant for statistical sources but rarely worth the RDF overhead in civic work.
- **DWBP** — 35 best practices spanning metadata, licenses, provenance, quality, versioning, identifiers, formats, vocabularies, access/APIs, and republication. It is the single best "did we miss anything?" checklist, and it aligns one-to-one with FAIR. Treat it as a *review lens*, not a gate.
- **NIEM** — the heaviest standard here and the one to reach for *least* often. It earns its keep only when the project exchanges data with an agency that mandates a NIEM **IEPD** (Information Exchange Package Documentation). Its reusable-component philosophy rhymes with the skill's concept catalog, but its XML-schema machinery is overkill for a tidy CSV.

## A meta-synthesis: four lenses on open data

Synthesized rather than listed, the nine sources resolve into four perspectives. A complete liberation project touches all four — and, reassuringly, the skill's existing artifacts already land in each.

**1. Policy / governance — *should* this be open, and on what terms?** Sunlight's guidelines (and the US Ignite mirror) are the canonical statement. The questions they pose — completeness, timeliness, non-discrimination, licensing, permanence, cost — are the same ones the skill's [governance section](project-template.md#governance) makes a project answer in its README and `AGENTS.md`. The lens is *normative*: it's about obligations, not file formats.

In the US, those obligations are also *statutory*, and naming the mandate strengthens a project's justification: **OMB M-13-13** ("Open Data Policy — Managing Information as an Asset," 2013) and **Project Open Data** are the origin of the federal metadata schema that became DCAT-US; the **OPEN Government Data Act** (Title II of the **Foundations for Evidence-Based Policymaking Act**, 2019) makes "open by default," machine-readable inventories, and agency Chief Data Officers a *legal duty*; and the **DATA Act** (2014) standardized federal spending data. When a source is PDF-locked despite one of these mandates, that's the difference between *nice-to-have* and *owed* — cite it in the README. The broader transparency-law, civic-tech, and international context around these mandates lives in [Part 3](#part-3--open-government-landscape).

**2. Cataloging / metadata interoperability — can a machine *find and understand* it?** DCAT-US, W3C DCAT, and the W3C *Publishing Open Government Data* note answer this with a shared vocabulary (Catalog / Dataset / Distribution / DataService). The skill's `metadata.yaml` and hand-maintained data dictionary are this lens in miniature; emitting a DCAT record is the optional step that makes the dataset show up in a federated catalog.

**3. Discipline / domain standards & registries — has someone *already solved* this?** FAIRsharing (standards ↔ databases ↔ policies), re3data (repositories), and NIEM (agency exchange) are where you look *before* inventing. This lens maps onto the skill's **Survey** phase: cataloguing prior work and existing standards is exactly the "ask before assuming" discipline the workflow already prescribes. Most civic projects consult these, find nothing binding, and proceed — but the five-minute check is worth it.

**4. Web best practice + FAIR — is it *good* open data, by a published yardstick?** DWBP's 35 practices and the four FAIR principles are the connective tissue across the other three lenses. They're the most useful as a *review* pass near Publish: a quick self-check against Findable / Accessible / Interoperable / Reusable (or the DWBP practice list) catches the gap — a missing license, an unstable identifier, undocumented provenance — without imposing a process.

## Crosswalk: standards ↔ what the skill already builds

The actionable core. Each row names a standard, the **existing** skill artifact that already embodies it (no new work), and an **optional** deepening step to reach for only when a consumer benefits. The "already in the skill" column is the load-bearing one — it's what lets you *cite* the standard honestly today.

| Standard / vocabulary | Already in the skill | Optional deepening (only if a consumer needs it) |
|---|---|---|
| **DCAT-US v3 / W3C DCAT** (Catalog → Dataset → Distribution) | `data/processed/metadata.yaml`, `docs/data-dictionary.md`, Datasette's per-table/column metadata ([`publishing.md`](publishing.md#metadata-the-documentation-surface-that-travels-with-the-data)) | Emit a `dcat-us.jsonld` catalog record alongside `metadata.yaml` so the dataset federates into `data.gov`-style catalogs |
| **W3C PROV-O** (Entity / Activity / Agent) | `data/processed/provenance.csv`, the per-extract sidecar ([`data-modeling.md`](data-modeling.md#provenance)) | Map the sidecar columns to PROV terms (`source_url`→Entity, `parser_module`→Activity, the project→Agent); serialize to PROV-JSON only if a downstream graph consumes it |
| **W3C DQV + DWBP quality BPs** | The five-dimension quality framework + `audit.py` + `reconcile.py` ([`data-modeling.md`](data-modeling.md#data-quality)) | Tag audit metrics with DQV dimension URIs; expose them in `metadata.yaml` |
| **FAIR principles** | Tidy long-form, stable composite keys, the data dictionary, the provenance trail | Run a four-line FAIR self-check (Findable/Accessible/Interoperable/Reusable) before Publish and record gaps in `AGENTS.md` |
| **DWBP** (35 best practices) | The whole workflow — metadata, licensing, provenance, versioning, identifiers, access all have a home | Use the DWBP list as a one-time "did we miss anything?" review near Publish |
| **Sunlight 10 principles / 32 provisions** | Immutable originals (permanence), tidy CSVs (machine readability), CC-BY defaults (licensing), open repos (non-discrimination, low cost) ([`project-template.md`](project-template.md#governance)) | Self-assess the published dataset against the 10 principles; note any the source itself violates as a *finding* |
| **FAIRsharing / re3data** | The Survey-phase "search and catalog" discipline + README lineage citations | Consult the registries during Survey to find a domain standard to reuse or a repository to deposit a copy in |
| **NIEM** (reusable components, IEPDs) | Per-source parsers + the concept catalog (reusable cross-source equivalences) ([`data-modeling.md`](data-modeling.md#concept-catalogs)) | Only when an agency partner mandates a NIEM exchange — map the canonical schema to the required IEPD |

## Using the standards responsibly

A short discipline, consistent with the skill's existing caveat-writing ethos:

- **Cite, don't conform for its own sake.** When an artifact already matches a standard, name the standard in the README or `AGENTS.md` ("provenance follows W3C PROV; metadata is DCAT-shaped"). That's the cheap, high-value move. Don't restructure a working pipeline to chase a badge.
- **Look before you invent.** In Survey, spend five minutes in FAIRsharing / re3data and on the publisher's own metadata. If a domain standard exists, reuse it; if not, proceed without guilt.
- **Never let conformance block shipping.** A liberated dataset that exists beats a perfectly DCAT-conformant one that doesn't. If a standard would delay publication, defer it to an issue.
- **Record what you *didn't* adopt, and why.** Consistent with the skill's "concepts carry caveats" principle: a one-line note in `AGENTS.md` ("we did not emit DCAT-US JSON-LD — no federated-catalog consumer yet") is more honest and more useful than silent omission.
- **Let the standard catch the source's failures.** The Sunlight principles and DWBP are also a lens on the *publisher*: a source that fails "permanence" (dead links) or "machine readability" (scanned PDFs) is generating a *finding* worth recording, not just an inconvenience.

## Source map

The nine authoritative sources, one line each, so an agent can fetch the primary document on demand rather than relying on this distillation:

- **Sunlight Open Data Policy Guidelines** — <https://opendatapolicyhub.sunlightfoundation.com/guidelines/> — the 10 principles + 32 model provisions for government open-data policy (archived).
- **US Ignite mirror of the Sunlight guidelines** — <https://www.us-ignite.org/tools/data-standards-and-policies/open-data-policy-guidelines-sunlight/> — maintained continuity copy of the same framework.
- **DCAT-US** — <https://resources.data.gov/standards/catalog/dcat-us/> — the US federal metadata profile (Catalog → Dataset → Distribution; DataService, DatasetSeries) behind `data.gov`.
- **FAIRsharing** — <https://www.fairsharing.org/> — curated registry interlinking standards, databases/repositories, and data policies across disciplines.
- **NIEM** — <https://www.niem.gov/> — the National Information Exchange Model: XML-schema framework + Naming & Design Rules for cross-agency data exchange.
- **re3data** — <https://www.re3data.org/> — the Registry of Research Data Repositories (3,000+ repositories, metadata schema, API).
- **W3C Data on the Web Best Practices — use cases** — <https://w3c.github.io/dwbp/usecasesv1.html> — the use cases and requirements grounding the 35 DWBP best practices.
- **W3C *Publishing Open Government Data*** — <https://www.w3.org/TR/gov-data/> — the W3C note on publishing government data as Linked Open Data (introduces DCAT in a gov context).
- **W3C Data Activity hub** — <https://www.w3.org/2013/data/> — the coordination point for DCAT, PROV-O, DQV, Org, and RDF Data Cube.

---

# Part 3 — Open government landscape

Background context, **not a constraint** on the workflow — the same register as [Part 2](#part-2--open-data-standards-as-background). Where that part covers the *technical* standards the skill's artifacts implement (DCAT, PROV, DQV, FAIR), this one zooms out to the *civic and institutional* landscape around them: how governments are *obliged* to publish (transparency law and open-data policy), who *consumes* liberated data (the civic-tech ecosystem), and how the work connects to *international* open-government efforts. It complements [Part 1](#part-1--movement-history-data-liberation-as-activism-and-method) — that part tells the activist lineage; this one maps the surrounding institutions, laws, and resources.

Read it once for orientation, then reach for the resource catalog at the end when a project needs a portal, a law, a request channel, or a downstream outlet. Nothing here gates shipping a tidy CSV; it's a map of the territory the dataset lands in.

> **Source-quality note.** This material was prompted by a synthesis of the *Open Government Platform* knowledge base (`opengovtplatform.org`), whose pages could not be fetched directly (HTTP 403) and were reconstructed via web search — so its site-specific particulars are approximate and some article URLs may not be stable. Everything below is therefore anchored on **independently verifiable primary resources** (data.gov, FOIA.gov, OGP, OKFN/CKAN, the World Bank toolkit, the Open Data Charter, etc.), not on that site's specific claims. Treat the figures as indicative and verify against the linked primaries before citing them.

## The five themes, synthesized

The knowledge base organizes open government into five themes. Each maps onto something the skill already does — or marks a boundary the skill deliberately doesn't cross.

### 1. Open data — the publishing layer

Open data is public-sector information released in standardized, machine-readable, openly-licensed form. The durable touchstones: the **8 Principles of Open Government Data** (Sebastopol, 2007 — the ancestor of Sunlight's 10), the **3-star minimum** (CSV/JSON/XML before you've earned a star for openness), and the federal lineage from `data.gov` (launched 2009) through the metadata standard now known as **DCAT-US**. Government **APIs** (`api.data.gov`, the Census and USAspending APIs) are the machine-to-machine face of the same idea.

*How the skill relates:* this is the skill's home turf — see [Part 2](#part-2--open-data-standards-as-background) for the standards and the artifact crosswalk. The gap the knowledge base surfaces is **institutional publishing**: the skill builds a Datasette + Quarto + LFS bundle, but says little about federating *back* into a `data.gov`/CKAN/Socrata portal. See [the portal-federation note](#institutional-publishing-the-portal-layer) below and the DCAT-export pointer added to [`publishing.md`](publishing.md).

### 2. Government transparency — the obligation layer

Transparency is the *why* beneath much liberation work: FOIA (the federal **Freedom of Information Act**, 1966, 5 U.S.C. § 552), state **sunshine / open-records laws**, spending disclosure (**USAspending.gov**, Treasury Fiscal Data, mandated by the **DATA Act** of 2014), and **whistleblower** protections. The knowledge base treats FOIA as a *process* — drafting a request, the ~20-business-day clock, fee categories (commercial vs. news-media/educational vs. other), appeals, and redaction disputes — not just as a source of PDFs.

*How the skill relates:* the skill names FOIA/MuckRock/CORA as *source paths* but is thin on FOIA *procedure* and on transparency *politics* (when a redaction is excessive; what the project will *refuse* to liberate). A short FOIA-as-process + scope note now lives in [`pipeline.md`](pipeline.md) under the Survey-phase checks.

### 3. Civic technology — the consumer/intermediary layer

Civic tech is the ecosystem of tools that put government data in front of people: reporting tools (**SeeClickFix**, 311), legislative trackers (**GovTrack**, **Councilmatic**, **OpenStates** / Open Civic Data), accountability databases (**OpenSecrets**, **Follow the Money**), and the investigative-journalism layer (**ProPublica**). Civic **hackathons** (the lineage from "Apps for Democracy," DC 2008) are how open data gets turned into demonstrations of use.

*How the skill relates:* the skill already frames its output as feedstock for "empowering intermediaries" (Baack) and names Schrock's five activities (Request / Digest / Contribute / Model / Contest) — see [the critical perspectives in Part 1](#critical-perspectives-worth-absorbing). What it underplays is the *operational hookup*: which export shapes (bulk CSV vs. API vs. DCAT-cataloged) suit which downstream tool, and how to *find and recruit* the journalists/NGOs a dataset is for rather than hoping they discover it. This stays largely a documentation concern (the README's *movement context* section), not a pipeline change.

### 4. Policy & legislation — the mandate layer

The legal scaffolding that makes open data *owed*, not merely nice:

- **FOIA** (1966) and state **sunshine laws** — the request-driven floor.
- **OMB M-13-13** ("Open Data Policy — Managing Information as an Asset," 2013) and **Project Open Data** — the origin of the federal metadata schema that became **DCAT-US**.
- The **OPEN Government Data Act** (Title II of the **Foundations for Evidence-Based Policymaking Act**, 2019) — makes "open by default" and machine-readable inventories a *statutory* duty for federal agencies, and stands up agency **Chief Data Officers**.
- The **DATA Act** (2014) — standardized federal spending data.
- Privacy counterweights: **GDPR** (Art. 17 erasure), **CCPA**, and the **CARE Principles** for Indigenous Data Governance, which sit *alongside* FAIR and can pull the other way (collective authority and restricted access vs. maximal openness).

*How the skill relates:* the skill is strong on Sunlight + licensing but didn't name the federal *mandates*. A focused policy note (M-13-13 → DCAT-US, the Evidence Act / OPEN Government Data Act, the DATA Act) now lives in [Part 2](#part-2--open-data-standards-as-background), and the CARE-vs-FAIR tension is sharpened in [`project-template.md`](project-template.md#governance). Naming a mandate lets an agent prioritize — *federally-required-but-PDF-locked* beats *nice-to-have* — and gives the README a citation for *why* the data should have been public.

### 5. Global initiatives — the international layer

Open government is not a US-only story. The anchors: the **Open Government Partnership** (OGP, est. 2011; ~75+ member countries plus local jurisdictions, working through National Action Plans and an Independent Reporting Mechanism co-created with civil society), the **International Open Data Charter** (principles adopted by a large number of national and subnational governments), the **Open Knowledge Foundation** (OKFN — steward of **CKAN**, the portal software behind data.gov, `open.canada.ca`, `data.europa.eu`-adjacent and many national portals, and the **Open Data Handbook**), fiscal-transparency bodies (**GIFT** — sunsetted July 2025, materials hosted by the **International Budget Partnership**; the **Open Budget Index**), and **Transparency International** / the **World Bank Open Government Data Toolkit**.

*How the skill relates:* this is the skill's biggest blind spot — its lineage and tooling (GitHub, CC-BY, Datasette) are US/Anglophone. That's a *deliberate scope boundary*, not a defect the skill can fully close, but it should be *named*. A short international-context note now lives in [Part 1](#the-lineage-is-us-centric--the-international-frame) so an agent working outside the US knows which universal principles transfer (immutable originals, tidy long-form, provenance, reconciliation) and which implementation assumptions to localize (license regime, portal software, hosting, language).

## Gaps and tensions, and how the skill responds

The audit against the knowledge base surfaced six gaps. Honest disposition: two are addressed by *fixes*, two by *this reference plus light cross-links*, and two are *deliberate scope boundaries* now made explicit rather than silently left open.

| # | Gap / tension | Disposition |
|---|---|---|
| 1 | **Institutional data portals** — skill publishes its own surfaces, ignores federating into data.gov / CKAN / Socrata | Fix: DCAT-export / CKAN note in [`publishing.md`](publishing.md); framing [below](#institutional-publishing-the-portal-layer) |
| 2 | **Federal policy not encoded** — no M-13-13, Evidence Act, DATA Act | Fix: policy note added to [Part 2](#part-2--open-data-standards-as-background) |
| 3 | **Civic-tech intermediaries named but not connected** | This reference (theme 3) + the existing README *movement context* convention; stays a documentation concern |
| 4 | **CARE / GDPR / CCPA named but not operationalized** | Fix: CARE-vs-FAIR + privacy decision note sharpened in [`project-template.md`](project-template.md#governance) |
| 5 | **International landscape absent** — OGP, OKFN, Open Data Charter, SDMX, CKAN | This reference (theme 5) + international-context note in [Part 1](#the-lineage-is-us-centric--the-international-frame); a deliberate scope boundary, now named |
| 6 | **Transparency politics underexplored** — redaction disputes, what to refuse | This reference (theme 2) + FOIA-process/scope note in [`pipeline.md`](pipeline.md) |

### Institutional publishing: the portal layer

The skill's default deployment is *activist*: extract locked data, build a Datasette + Quarto + LFS bundle, host it yourself. That is the right MVP for a 1–3-person liberation project. But when the audience is a city or agency open-data program, the expected endpoint is *their* portal — a **CKAN** or **Socrata** instance that ingests a **DCAT** catalog record. These are two different workflows, and the skill should not pretend the second away:

- For **self-hosted** publishing, nothing changes — Datasette/Quarto/LFS as today.
- For **portal federation**, emit a DCAT-US catalog record alongside `metadata.yaml` (see the note in [`publishing.md`](publishing.md) and the crosswalk in [Part 2](#crosswalk-standards--what-the-skill-already-builds)) so the dataset can be harvested into data.gov-style discovery. Optional, only when a portal consumer exists.

This is the load-bearing tension between the knowledge base (institutional, federated, global) and the skill (small-team, self-hosted, US). Naming it is the fix; collapsing the skill into a portal CMS is not.

## Referenced-resources catalog

The knowledge base's *Resources* directory, incorporated here as a load-on-demand catalog. Grouped by purpose; each entry is a primary, verifiable source an agent can fetch when a project needs it. (Status notes flag resources that have sunsetted — verify before relying on them.)

### Federal data & API portals
- **data.gov** — <https://data.gov/> — the US federal open-data catalog (hundreds of thousands of datasets).
- **api.data.gov** — <https://api.data.gov/> — unified API-key gateway across federal APIs.
- **Census Bureau APIs** — <https://developer.census.gov/> — demographic, economic, housing data.
- **USAspending.gov** + **API** — <https://www.usaspending.gov/> / <https://api.usaspending.gov/> — federal contracts, grants, loans (DATA Act).
- **Treasury Fiscal Data** — <https://fiscaldata.treasury.gov/> — official budget/financial datasets and APIs.

### Portal software, standards & toolkits
- **CKAN** — <https://ckan.org/> — open-source data-portal platform behind data.gov and many national portals; speaks DCAT.
- **DCAT** (W3C) — the data-catalog vocabulary; see [Part 2](#part-2--open-data-standards-as-background).
- **FAIR principles** — Findable / Accessible / Interoperable / Reusable; see [Part 2](#part-2--open-data-standards-as-background).
- **Open Civic Data** — <https://open-civic-data.readthedocs.io/> — schemas for governments, officials, legislation, events (OpenStates lineage).
- **8 Principles of Open Government Data** — <https://opengovdata.org/> — the 2007 foundational principles.
- **World Bank Open Government Data Toolkit** — <https://opendatatoolkit.worldbank.org/> — implementation guidance for OGD programs.
- **Open Data Handbook** (OKFN) — <https://opendatahandbook.org/> — practical how-to for opening data.

### Transparency & access to information
- **FOIA.gov** — <https://www.foia.gov/> — official federal FOIA guidance + request routing.
- **Reporters Committee for Freedom of the Press** — <https://www.rcfp.org/> — legal resources for journalists seeking records.
- **State sunshine / open-records laws** — vary by state; the publisher's records officer is the entry point (see [`pipeline.md`](pipeline.md)).

### Money in politics & accountability
- **OpenSecrets** — <https://www.opensecrets.org/> — federal campaign finance and lobbying.
- **Follow the Money** — <https://www.followthemoney.org/> — state-level campaign finance.
- **GAO** — <https://www.gao.gov/> — congressional audit/watchdog.
- **Office of Special Counsel** — <https://osc.gov/> — federal whistleblower protection.
- **POGO** — <https://www.pogo.org/> — nonpartisan government-oversight investigations.

### Civic-tech & civil-society organizations
- **Code for America** — <https://codeforamerica.org/> — civic-tech tools and the Brigade network.
- **Open Knowledge Foundation** — <https://okfn.org/> — global open-data nonprofit; stewards CKAN and the Open Data Handbook.
- **OpenTheGovernment** — <https://www.openthegovernment.org/> — open-government advocacy coalition.

### International initiatives & frameworks
- **Open Government Partnership** — <https://www.opengovpartnership.org/> — multilateral open-gov initiative (National Action Plans, IRM).
- **International Open Data Charter** — <https://opendatacharter.org/> — shared open-data principles across governments.
- **Transparency International** — <https://www.transparency.org/> — global anti-corruption; Corruption Perceptions Index.
- **International Budget Partnership** — <https://internationalbudget.org/> — fiscal transparency; Open Budget Survey/Index; hosts legacy **GIFT** materials (GIFT sunsetted July 2025).
- **World Bank — Open Government** — <https://www.worldbank.org/en/topic/governance> — global open-government solutions.

### Privacy & compliance
- **GDPR** — the EU data-protection regime (Art. 17 right to erasure); the global reference standard.
- **Data Privacy Framework** — <https://www.dataprivacyframework.gov/> — transatlantic data-transfer compliance.
- **CARE Principles for Indigenous Data Governance** — <https://www.gida-global.org/care> — collective benefit, authority to control, responsibility, ethics.

## Using the landscape responsibly

- **Cite the mandate, don't just extract.** When a source is legally *owed* (Evidence Act, M-13-13, a state sunshine law), name that in the README — it's the strongest justification for the work and orients downstream users.
- **Match the publishing surface to the audience.** Self-hosted Datasette for an activist release; a DCAT record for portal federation. Don't build portal machinery a project doesn't need.
- **Localize before you globalize.** Outside the US, the principles transfer but the implementation (license regime, CKAN vs. GitHub Pages, language, hosting) needs local judgment. Name the assumptions you're carrying.
- **Let privacy law and CARE actually constrain.** Unlike most of this skill's "optional" guidance, GDPR/CCPA and CARE can mean *do not publish, or publish differently*. Treat those as real gates, not caveats — see [`project-template.md`](project-template.md#governance).
- **Don't over-trust any single aggregator.** This very reference was prompted by a site that couldn't be fetched; follow the primary links above and verify figures before citing.

---

## Further reading within this skill

Activist / movement tradition (Part 1):
- Tom Lee (Sunlight Foundation), [*PDF Liberation: Why It Matters And How You Can Help*](https://sunlightfoundation.com/2014/01/24/pdf-liberation-why-it-matters-and-how-you-can-help/), 2014
- [PDF Liberation Working Group](https://github.com/pdfliberation) on GitHub
- [catalyst-cooperative/pudl](https://github.com/catalyst-cooperative/pudl) — multi-source ETL reference
- [BoulderPublicData/Election-Results](https://github.com/BoulderPublicData/Election-Results) — modern small-team liberation pattern
- [ProPublica's data-bulletproofing guide](https://github.com/propublica/guides/blob/master/data-bulletproofing.md) — the journalistic standard for vetting a dataset before publishing it

Consumer-side practice (what happens *after* a liberation ships — adjacent to this skill, not within it):
- [NYT data-training](https://github.com/nytimes/data-training) — the *New York Times*' newsroom training materials for data journalists. Covers brainstorming story angles from a dataset, the verification practices reporters apply to avoid misreading data, and editorial review of data stories. Spreadsheet-first by audience (Google Sheets, not pandas), but the *methodological* content is what a complete liberation hands off to: a project that ships a tidy CSV and a data dictionary has done half the work; these materials describe the other half. Point downstream consumers here from the project's README rather than reinventing the consumer-side methodology in the pipeline's docs.

Critical / scholarly tradition (the movement read from outside):
- Schrock, *Civic hacking as data activism and advocacy: A history from publicity to open government data*, *New Media & Society*, 2016 — civic hacking's pre-2010 history
- Baack, *Datafication and empowerment: How the open data movement re-articulates notions of democracy, participation, and journalism*, *Big Data & Society*, 2015 — open-source modulation framework
- Johnson, *From open data to information justice*, *Ethics and Information Technology*, 2014 — the case that open data alone reproduces injustice
- Casemajor, *Data cultures: Contested meanings in a public cultural institution*, *Big Data & Society*, 2025 — data culture as plural and contested inside an institution

Methodological / academic tradition:
- Wirth & Hipp, *CRISP-DM: Towards a standard process model for data mining*, 2000
- Holstein, Spitzer, Hoell, Vössing, Kühl, *Understanding Data Understanding: A Framework to Navigate the Intricacies of Data Analytics*, ECIS 2024
- Shigarov, *Table understanding: Problem overview*, *WIREs Data Mining and Knowledge Discovery*, 2023
- Kasem et al., *Deep Learning for Table Detection and Structure Recognition: A Survey*, *ACM Computing Surveys*, 2024
- Göbel, Hassan, Oro, Orsi, *A Methodology for Evaluating Algorithms for Table Understanding in PDF Documents*, DocEng 2012
- Long, Wang, Xue, Gao, Yang, Wang, Xia, *Parsing Table Structures in the Wild*, ICCV 2021
- Wickham, *Tidy Data*, *Journal of Statistical Software*, 2014
- Tamir Hassan's [Table Understanding Competition pages](https://tamirhassan.com/html/competition.html) — historical competition datasets and evaluation
- [tanfiona/LLM-on-Tabular-Data-Prediction-Table-Understanding-Data-Generation](https://github.com/tanfiona/LLM-on-Tabular-Data-Prediction-Table-Understanding-Data-Generation) — actively-maintained survey of LLM × table work, with curated benchmark and outlink catalog

Standards & governance (Part 2 / Part 3):
- [`data-modeling.md`](data-modeling.md) — where provenance (PROV), metadata (DCAT), concept catalogs (NIEM-adjacent), and the quality dimensions (DQV) actually live in code.
- [`project-template.md`](project-template.md#governance) — the governance checklist that operationalizes the Sunlight policy questions, licensing, CARE-vs-FAIR, privacy, and out-of-scope uses.
- [`pipeline.md`](pipeline.md) — FOIA-as-process and the bulletproofing checklist / audit-reconcile loop that parallel DWBP's quality and provenance practices.
- [`publishing.md`](publishing.md#metadata-the-documentation-surface-that-travels-with-the-data) — `metadata.yaml`, the DCAT-shaped catalog surface that travels with the data, and the optional DCAT/CKAN federation path.

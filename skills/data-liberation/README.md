# data-liberation

An [Agent Skill](https://agentskills.io) for orchestrating data liberation projects — turning government PDFs, FOIA releases, scanned reports, scraped HTML, and panel-format spreadsheets into tidy, documented, reproducible civic datasets.

## What the skill does

Loaded into a compatible agent (Claude Code, Claude.ai, VS Code Copilot, Cursor, OpenAI Codex, Gemini CLI, Goose, OpenCode, and the [other clients in the AgentSkills ecosystem](https://agentskills.io/home)), it gives the agent:

- **Six escalating levels of complexity.** The skill's organizing idea: start at the lowest level that satisfies the request and offer to climb, so getting a CSV out of a PDF never requires buying the whole apparatus.
  - **L0 Extract** — source to CSV, no scaffold. "Just the data."
  - **L1 + Documentation** — data dictionary, provenance, README note. Now citable.
  - **L2 + Pipeline & Audit** — scaffolded, reproducible, validated. "Someone can re-run this."
  - **L3 + Harmonization** — crosswalks across sources, with caveats. Multi-source.
  - **L4 + Standards & Governance** — DCAT/PROV/FAIR naming + governance/ethics. Publishable responsibly.
  - **L5 + Publishing** — Datasette, Quarto site, Git LFS, DocumentCloud.

  The agent infers the level from the request, states its assumption, executes, and offers the next rung — see SKILL.md's *The six levels* section.
- **A six-phase workflow** — Survey → Scaffold → Extract → Tidy → Audit → Publish — mapping to CRISP-DM's data understanding → preparation → deployment phases and deliberately stopping where modeling begins. The phases describe *how* the work gets done within a project; the levels above describe *how far* a given engagement goes. Searchable against industry vocabulary (Goal Planning, Data Extraction, Data Cleaning and Transformation, Data Loading, Data Validation, Data Lineage, Data Observability, Data Governance, Data Maintenance) — see SKILL.md's vocabulary-alignment table.
Underneath the levels and phases, the skill carries a set of methods and conventions, each wired to the reference file (loaded on demand) that holds the detail:

- **Toolchain decision trees** *(L0)* — match the input to the tool: pdfplumber vs. camelot for born-digital PDFs; tesseract / PaddleOCR / Surya for scans and images; `read_html` / `selectolax` / `lxml` for HTML/XML; `json_normalize` for JSON; `read_excel` / `openpyxl` for panel spreadsheets; `requests` + cache vs. headless browser vs. archived snapshots for the web. → the five [`extract-*.md`](references/extract-pdf.md) files (pdf · tabular · documents · web · images).
- **A project template** *(L2+)* — immutable originals → processed tidy data → audit reports → lookups (crosswalks). Bootstraps single-source but is structured for multi-source from day one; **bundled in this repo** at [`templates/project/`](templates/project/) and rendered into the user's working directory at scaffold time. → [`project-template.md`](references/project-template.md).
- **Documentation and the contract framing** *(L1–L3)* — data dictionaries and pandera schemas as a *contract* the processed CSV obeys; concept catalogs as contracts at the cross-source-equivalence level; per-extract provenance; the five-dimension data-quality framework (availability / usability / reliability / relevance / presentation). → [`data-modeling.md`](references/data-modeling.md).
- **A 9-step cleaning pipeline** *(L2)* — profile → structural fixes → exact + fuzzy deduplication (Jaro-Winkler / Levenshtein) → missing-value treatment (Rubin's MCAR/MAR/MNAR) → outlier detection (IQR + impossible-value ranges) → standardization → validation + reject port → PII redaction (presidio/scrubadub) → documentation, plus discovery, reconciliation against authoritative totals, the pre-extraction bulletproofing checklist, and the cron-driven recurring-refresh PR. → [`pipeline.md`](references/pipeline.md).
- **Publishing surfaces** *(L5)* — Datasette (queryable SQLite + JSON API), a Quarto documentation site on GitHub Pages, Git LFS for bulk distribution, and DocumentCloud for the underlying source documents. → [`publishing.md`](references/publishing.md).
- **A governance section** *(L4)* — license inheritance, data-subject considerations (CARE principles, out-of-scope use declarations), project-internal governance, and downstream accountability (error-reporting paths, citation guidance). → [`project-template.md`](references/project-template.md#governance).
- **Movement context, standards, and the open-government landscape** *(L4 background — not a gate)* — the civic-data tradition (Sunlight, PDF Liberation, MuckRock, PUDL, BoulderPublicData) and its scholarly critiques (Baack, Schrock, Johnson, Casemajor); the standards the artifacts already informally implement (DCAT-US / W3C DCAT, PROV-O, DQV, DWBP, FAIR, the FAIRsharing / re3data / NIEM registries), each crosswalked to the artifact it matches; and the institutional/legal landscape (FOIA, M-13-13, the OPEN Government Data Act / Evidence Act, the DATA Act, data.gov / CKAN / Socrata, OGP, the International Open Data Charter). Privacy law and the CARE principles are the only *real gates*; everything else is for naming and optionally deepening what the pipeline already does. → [`context.md`](references/context.md).

The skill triggers on phrases like "data liberation," "PDF extraction," "get the data out," "give me a CSV," "make this citable," "reproducible pipeline," "tidy data," "data dictionary," "crosswalk," "provenance," "reconcile," and "scrape this site" — and on any request that involves turning a document into a dataset someone else could reuse. See [SKILL.md](SKILL.md) for the full instructions.

## Repository contents

```
data-liberation-skill/
├── SKILL.md           # Skill entry point (loaded on activation) — the six levels + workflow
├── references/        # Toolchain + methodology docs (loaded on demand), grouped by level
│   ├── extract-pdf.md        # L0: born-digital PDFs — pdfplumber, camelot, parser skeleton
│   ├── extract-tabular.md    # L0: XLSX (incl. panel-format), CSV, Parquet, databases
│   ├── extract-documents.md  # L0: HTML, XML, JSON, DOCX; docling/kreuzberg unified extractors
│   ├── extract-web.md        # L0: web scraping — ethics, archives, protocols, dynamic pages
│   ├── extract-images.md     # L0: images, OCR (tesseract/PaddleOCR/Surya), preprocessing, computer vision
│   ├── data-modeling.md      # L1–L3: tidy, schema-as-contract, dictionary, concepts/crosswalks, provenance, validation, quality dimensions
│   ├── pipeline.md           # L2: 9-step cleaning pipeline + discovery/audit/reconcile + bulletproofing + recurring refresh
│   ├── project-template.md   # L2/L4: project skeleton spec + governance section
│   ├── publishing.md         # L5: Datasette, Quarto site, Git LFS, DocumentCloud
│   └── context.md            # L4 background (not a gate): movement history + critical perspectives, open-data standards, open-government landscape
├── scripts/validate.py  # Lints templates/ and renders + smoke-tests the scaffold (CI)
├── templates/project/   # The bundled project skeleton, rendered at scaffold time (L2+)
└── RELEASING.md         # Single-repo release procedure
```

The working project template is **bundled in this repo** at [`templates/project/`](templates/project/) — token-bearing files carry a `.tmpl` suffix and `{{UPPER_SNAKE}}` slot-fills, everything else renders verbatim. There is no separate repo and no version pin: the template ships in the same commit as the skill, so what gets scaffolded is exactly what's in the tree (reproducibility comes from the shared commit, not a cross-repo SHA). Agents read `templates/` only when scaffolding (L2+); `scripts/validate.py` renders it and smoke-tests the result in CI.

## Installation

The skill follows the [AgentSkills.io specification](https://agentskills.io/specification): a folder containing a `SKILL.md` with `name` and `description` frontmatter, plus optional `scripts/`, `references/`, and `assets/`. Every AgentSkills-compatible client discovers skills the same way — by scanning one or more known directories — so installation is just cloning this repo (or symlinking it) into the directory your client watches, **as a folder named `data-liberation`** (the folder name must match the `name:` field in the frontmatter).

### Claude Code, Claude.ai, Claude Agent SDK

User-level (available across all projects):

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/brianckeegan/data-liberation-skill.git ~/.claude/skills/data-liberation
```

Project-level (scoped to one repo):

```bash
mkdir -p .claude/skills
git clone https://github.com/brianckeegan/data-liberation-skill.git .claude/skills/data-liberation
```

### VS Code (Copilot agent mode), Cursor, and most other AgentSkills clients

Project-level — the default location is `.agents/skills/`:

```bash
mkdir -p .agents/skills
git clone https://github.com/brianckeegan/data-liberation-skill.git .agents/skills/data-liberation
```

### Other clients

For OpenAI Codex, Gemini CLI, Goose, OpenCode, OpenHands, Amp, Letta, Factory, and the rest of the [client showcase](https://agentskills.io/home), check that client's skills documentation for its install path, then clone this repo into it under the folder name `data-liberation`. The skill itself is unchanged across clients.

### Verify it loaded

In Claude Code, run `/skills` and confirm `data-liberation` appears. In VS Code Copilot agent mode, do the same in the chat panel. The skill should activate on prompts like *"get the data out of this PDF into a CSV"* (L0), *"liberate this PDF into a documented, citable dataset"* (L1), or *"scaffold a new civic data project"* (L2).

## Getting started: a walkthrough

The skill is designed to be entered at the **lowest level that satisfies your ask** and climbed only as far as you need. You never have to know the level names — the agent infers one, tells you its assumption, and offers the next rung when it's done. Here's the same source taken up the ladder.

Say you have `county-budget-2024.pdf` — a born-digital PDF with a few tables.

### L0 — just the data

> **You:** Get the data out of `county-budget-2024.pdf` into a CSV.

The agent recognizes an extraction request, infers **L0**, and says so:

> **Agent:** This reads like L0 — just the data. I'll start there. *(reads the PDF, picks `pdfplumber` from the [`extract-pdf.md`](references/extract-pdf.md) decision tree, writes the table out)* Done — `county-budget-2024.csv`, 412 rows × 7 columns. Want me to go to **L1** and add a data dictionary + provenance so this is citable?

You have a CSV. Nothing else was created — no project, no scaffold. (If the PDF were a **scan**, the agent would route to [`extract-images.md`](references/extract-images.md) for the OCR path instead; a spreadsheet routes to [`extract-tabular.md`](references/extract-tabular.md), a web page to [`extract-web.md`](references/extract-web.md).)

### L1 — make it citable

> **You:** Yes, do L1.

> **Agent:** *(writes, alongside the CSV)*
> - `data-dictionary.md` — one row per column: type, units, source vocabulary, caveats
> - `provenance.csv` — the source PDF's SHA256, page range, tool + version, timestamp, row count
> - `README.md` — a one-page Survey note: what the document is, the unit of observation, who publishes it, and a short ethics note
>
> Now anyone can cite the dataset and trace every value back to a page in the original. Want **L2** — a reproducible pipeline someone else can re-run?

### L2 — someone can re-run this

This is the first level that scaffolds a project. The agent renders the bundled [project template](templates/project/) into a working repo:

```
county-budget/
├── data/{original,processed,audit,lookups}/
├── scripts/{schema,sources,config,fetch,clean,audit,pipeline}.py + parsers/
├── tests/                # pandera schema contract + a parser fixture
├── docs/{data-dictionary.md, filter-pivot-recipes.md}
└── AGENTS.md  README.md  pyproject.toml
```

Your L0 extraction becomes a parser under `scripts/parsers/`; `audit.py` profiles the output; `reconcile.py` (if the budget carries an authoritative total) checks the processed numbers against it. Verify with:

```bash
uv sync && uv run pytest          # schema contract + parser fixtures pass
uv run python -m scripts.pipeline # regenerate data/processed/ from data/original/
```

### L3–L5 — when the project grows

- **L3 (harmonize)** — *"add last year's budget and make the categories comparable"* → a concept catalog with caveats so cross-year comparisons are honest. See [`data-modeling.md`](references/data-modeling.md#concept-catalogs).
- **L4 (standards & governance)** — *"is this OK to publish, and can it federate into a catalog?"* → a governance section + optional DCAT/PROV/FAIR naming. See [`context.md`](references/context.md) and [`project-template.md`](references/project-template.md#governance).
- **L5 (publish)** — *"put it online so people can query it"* → a Datasette instance, a Quarto docs site, Git LFS for the big files, DocumentCloud for the source PDFs. See [`publishing.md`](references/publishing.md).

### Tips

- **Jump straight to a level** by naming it: *"scaffold an L2 project for these election PDFs."*
- **Point at your sources up front** — a URL, a FOIA tracking ID, a prior repo, or a codebook. The Survey phase uses them, and good leads beat web search.
- **Skip the ladder** when you already know the destination: *"build a fully published, multi-source pipeline"* lands at L5 directly.

## License

MIT — see [LICENSE](LICENSE).

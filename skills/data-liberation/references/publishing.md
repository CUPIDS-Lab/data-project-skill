# Publishing: Datasette, Quarto, Git LFS, and DocumentCloud

A complete liberation project ships up to four deployment surfaces: the **queryable data interface** ([Datasette](#part-1-datasette--sqlite-utils)), the **documentation site** ([Quarto](#part-2-quarto--github-pages) on GitHub Pages), the **bulk-distribution layer** ([Git LFS](#part-3-git-lfs-for-large-datasets)), and the **source-document layer** ([DocumentCloud](#part-4-documentcloud)). This is the **Level 5** reference. Each surface plays to its strength — Datasette makes the data queryable, Quarto explains how to use it, LFS distributes raw artifacts as opaque downloads, and DocumentCloud renders source PDFs with OCR, embeds, and page-anchored permalinks. Pick the subset the project needs; a small dataset may use only one, a documents-heavy investigation may use all four.

---

# Part 1: Datasette + sqlite-utils

[Datasette](https://datasette.io/) turns a SQLite database into a queryable web app with SQL editor, facet browsing, JSON API, and one-command deploy. [`sqlite-utils`](https://sqlite-utils.datasette.io/) is the workhorse for getting tidy CSV/Parquet into SQLite. The patterns here come from the [PyCon 2023 SQLite tutorial](https://sqlite-tutorial-pycon-2023.readthedocs.io/) and Simon Willison's "Baked Data" architecture that powers Niche Museums, TILs, and PUDL's published instance.

## Why Datasette for liberated data

The CSV-only baseline asks every downstream user to repeat the same setup work — load it, declare dtypes, build the joins to provenance, write the filter expressions. Datasette delivers all of that as a deployed read-only web app:

- **SQL in the browser.** Any reader can write SQL against the published database, including joins across tables, full-text search, and JSON output. Civic-data consumers (reporters, advocates, students) who would never install pandas can query a Datasette site fine.
- **Faceted browsing.** Categorical columns get per-value facets automatically — readers click "Boulder County" to filter, then "2024" to filter further, and the URL captures the state. The query is shareable; the result is citable.
- **JSON API for free.** Every table view and SQL query has a `.json` (and `.csv`) sibling. Downstream pipelines, Observable notebooks, and journalism teams pin against the URL rather than re-fetching the source.
- **Metadata as documentation.** Per-database, per-table, and per-column descriptions render alongside the data — the data dictionary travels with the database file.
- **One-command publishing.** `datasette publish` deploys to Google Cloud Run, Heroku, Vercel, or Fly with a single command.

## From processed data to SQLite

`sqlite-utils` is the workhorse. (The older [`csvs-to-sqlite`](https://datasette.io/tools/csvs-to-sqlite) is unmaintained; use `sqlite-utils` instead.)

### Basic ingest

```bash
uvx sqlite-utils insert data/processed/elections.db elections \
    data/processed/boulder_election_results.csv --csv

uvx sqlite-utils insert data/processed/elections.db provenance \
    data/processed/provenance.csv --csv
```

This creates two tables (`elections` and `provenance`) inside the single SQLite file. The `insert` command infers a schema from the CSV; for civic data with leading-zero IDs or other string-typed numeric columns, declare types explicitly:

```bash
uvx sqlite-utils insert data/processed/elections.db elections \
    data/processed/boulder_election_results.csv --csv \
    --pk source --pk vintage --pk precinct --pk contest --pk candidate
uvx sqlite-utils transform data/processed/elections.db elections \
    --type votes INTEGER \
    --type precinct TEXT \
    --type vintage TEXT
```

Patterns worth memorizing:

- **`--pk` declares the composite primary key.** Datasette uses this for clean per-row URLs and pagination.
- **`--alter` lets a second insert append columns** — useful when a new vintage introduces new columns.
- **`--ignore` / `--replace` handle re-runs.** `--ignore` skips rows whose PK already exists; `--replace` overwrites.
- **Foreign keys connect tables.** `sqlite-utils add-foreign-key elections.db elections source provenance source` lets Datasette render the link as a clickable cross-table reference.

### Indexes

For tables of more than a few thousand rows, declare indexes on the columns readers will filter or facet by:

```bash
uvx sqlite-utils create-index data/processed/elections.db elections vintage
uvx sqlite-utils create-index data/processed/elections.db elections source
uvx sqlite-utils create-index data/processed/elections.db elections "contest, vintage"
```

Without indexes, Datasette's facet generation falls back to full-table scans, which gets slow above ~50k rows.

### Full-text search

For narrative columns (FOIA response text, candidate biographies, agency descriptions), enable SQLite FTS5:

```bash
uvx sqlite-utils enable-fts data/processed/elections.db elections candidate contest
```

The Datasette table view picks this up automatically and exposes a search box.

### A `scripts/publish.py` wrapper

The canonical pattern is a small Python module that reproduces the SQLite build from the canonical CSV in a single command:

```python
# scripts/publish.py
import subprocess
from pathlib import Path

DB = Path("data/processed/elections.db")
CSV = Path("data/processed/boulder_election_results.csv")
PROV = Path("data/processed/provenance.csv")


def build():
    if DB.exists():
        DB.unlink()  # rebuild from scratch — single canonical source

    subprocess.run([
        "sqlite-utils", "insert", str(DB), "elections", str(CSV), "--csv",
        "--pk", "source", "--pk", "vintage", "--pk", "precinct",
        "--pk", "contest", "--pk", "candidate",
    ], check=True)

    subprocess.run([
        "sqlite-utils", "insert", str(DB), "provenance", str(PROV), "--csv",
        "--pk", "source", "--pk", "vintage",
    ], check=True)

    subprocess.run([
        "sqlite-utils", "add-foreign-key", str(DB),
        "elections", "source", "provenance", "source",
    ], check=False)  # idempotent: ignore "already exists"

    for col in ("vintage", "source", "contest"):
        subprocess.run([
            "sqlite-utils", "create-index", "--if-not-exists",
            str(DB), "elections", col,
        ], check=True)


if __name__ == "__main__":
    build()
```

Wire this into the pipeline driver as `uv run python -m scripts.publish build`. The `elections.db` file is then a reproducible artifact: any commit + uv environment regenerates an identical database file.

## Running Datasette locally

Once `data/processed/elections.db` exists, serve it:

```bash
uvx datasette serve data/processed/elections.db --metadata data/processed/metadata.yaml -o
```

`-o` opens the browser at `http://localhost:8001`. `--reload` auto-restarts on file changes during development. For dev with plugins:

```bash
uvx --with datasette-cluster-map --with datasette-render-markdown \
    datasette serve data/processed/elections.db --metadata metadata.yaml --reload
```

The `uvx --with` pattern installs Datasette plus plugins into an ephemeral environment without polluting the project's `pyproject.toml`.

## Metadata: the documentation surface that travels with the data

Datasette reads a YAML or JSON file describing the dataset — title, license, source, per-table descriptions, per-column descriptions, canned queries. This is what readers see at the top of every page.

A starter `metadata.yaml`:

```yaml
title: Boulder Election Results
description_html: |
  Precinct-level statements of vote from Boulder County and the
  Colorado Secretary of State, 2004–present. Tidy long format,
  one row per (source, vintage, precinct, contest, candidate).
license: CC-BY-4.0
license_url: https://creativecommons.org/licenses/by/4.0/
source: Boulder County Clerk & Recorder + Colorado Secretary of State
source_url: https://bouldercounty.gov/elections/

databases:
  elections:
    description: |
      Tidy long-form precinct results, joined to per-extract provenance.
      See data-dictionary.md in the source repo for the full schema.
    tables:
      elections:
        title: Precinct results
        description: One row per (source, vintage, precinct, contest, candidate).
        sort: vintage
        facets: [vintage, source, contest]
        columns:
          source: Source registry slug; joins to `provenance` for fetch metadata.
          vintage: Election cycle; string ("2024-general").
          precinct: Boulder County precinct ID. Leading zeros preserved.
          votes: Vote count. Nullable when source suppressed the count.
        units:
          votes: count
      provenance:
        title: Per-extract provenance
        description: One row per (source, vintage); fetch URL, sha256, parser used.

    queries:
      total_votes_per_contest_per_vintage:
        title: Total votes per contest per vintage
        sql: |
          SELECT vintage, contest, SUM(votes) AS total_votes
          FROM elections
          WHERE votes IS NOT NULL
          GROUP BY vintage, contest
          ORDER BY vintage DESC, total_votes DESC
```

Three patterns to lean into:

- **Mirror `docs/data-dictionary.md` column descriptions into `metadata.yaml`.** The dictionary is the source of truth (see [`data-modeling.md`](data-modeling.md#data-dictionary) for the per-column template); the metadata file is the published projection. A small `scripts/publish.py` step can read the dictionary and emit the metadata to keep them in sync.
- **Use `facets` to pre-declare browsable categoricals.** Datasette will auto-detect facetable columns, but declaring them sets the default view readers see first.
- **Write canned queries for the questions readers will ask.** Per-contest totals, year-over-year change, top-N. Each canned query gets a clean URL anyone can cite.

This `metadata.yaml` is already a **DCAT** / **DCAT-US**-shaped catalog record (the project is a Catalog, the database a Dataset, the CSV/SQLite/JSON-API its Distributions). For a project that needs to federate into a `data.gov`-style catalog, `scripts/publish.py` can emit a `dcat-us.jsonld` record from the same dictionary — optional, covered in [`context.md`](context.md#crosswalk-standards--what-the-skill-already-builds). Background, never a publishing prerequisite.

This matters most when the real audience is an **institutional portal** rather than a standalone site. Much of the world's government data is published through **CKAN** (the open-source platform behind data.gov and many national catalogs) or **Socrata**, both of which harvest DCAT records. A self-hosted Datasette is the right activist MVP; a DCAT record is the bridge when a city or agency open-data program wants the dataset in *their* catalog. The two are different endpoints — pick the one the audience actually uses. The portal/federation landscape is mapped in [`context.md`](context.md#institutional-publishing-the-portal-layer).

### `metadata.yaml` vs `datasette.yaml` (Datasette 1.0a8+)

In the 1.0 alpha series, Datasette splits configuration into two files. **`metadata.yaml`** keeps dataset-identity content (title, description, license, source, per-table/column descriptions, canned queries). **`datasette.yaml`** carries server configuration (plugin settings, permissions, settings that used to live in `metadata.yaml`). 0.x deployments keep both in `metadata.yaml`. See the [annotated release notes for 1.0a8](https://docs.datasette.io/en/latest/changelog.html#a8-2024-02-07) to decide which file each setting belongs in. The pragmatic rule: civic projects on a stable footing should stay on 0.x and a single `metadata.yaml` until 1.0 ships stably.

## Plugins worth knowing for civic data

| Plugin | What it adds | When to use |
|---|---|---|
| [`datasette-cluster-map`](https://datasette.io/plugins/datasette-cluster-map) | Renders any table with `latitude` and `longitude` columns as a clustered map. | Geospatial liberated data — incident logs, facility lists, polling places. |
| [`datasette-render-markdown`](https://datasette.io/plugins/datasette-render-markdown) | Renders Markdown in designated columns. | FOIA case logs, narrative descriptions, agency response text. |
| [`datasette-vega`](https://datasette.io/plugins/datasette-vega) | Lets readers chart query results with Vega-Lite. | Any time-series, any per-category comparison. |
| [`datasette-graphql`](https://datasette.io/plugins/datasette-graphql) | Exposes a GraphQL API alongside the REST/JSON one. | Downstream consumers that prefer GraphQL. |
| [`datasette-search-all`](https://datasette.io/plugins/datasette-search-all) | One search box across every FTS-enabled table. | Multi-table corpora (FOIA collections, legislative records). |
| [`datasette-copyable`](https://datasette.io/plugins/datasette-copyable) | Adds copy-to-clipboard for rows in CSV / TSV / Markdown. | Reporter workflows: read row, paste into draft. |

Install plugins into the deployment by adding `--install <plugin>` to `datasette publish` or by listing them in `pyproject.toml`'s `publish` extras group.

## The "Baked Data" pattern

The right architecture for liberated civic data: the database is built fresh during the deploy step from the source CSVs, and the deployed instance is read-only. No application-layer writes; no separate database server. See Simon Willison's [Baked Data architecture](https://sqlite-tutorial-pycon-2023.readthedocs.io/en/latest/baked-data.html); Niche Museums and TILs are the canonical examples.

This is the right architecture for liberated civic data specifically because:

- **The dataset is the deliverable.** Every cycle of `clean → audit → publish` produces a new version of the SQLite file. There's no user-generated content layered on top.
- **Cache headers can be aggressive.** A static-like artifact behind a CDN serves at near-zero cost per request, even under journalism-driven traffic spikes.
- **Versioning is automatic.** Each deploy is a new build; the git commit hash and the SQLite file's sha256 together cite a specific dataset version.
- **Reverting is trivial.** A bad refresh produced a broken database? Roll back the deploy.

Implementation: the publishing workflow runs `scripts/publish.py build` (which produces `data/processed/elections.db`) and then `datasette publish <provider>` with the freshly-built database. The pipeline runs in CI; the result is a deploy.

## Publishing options

A spectrum from zero infrastructure to fully self-hosted:

### Datasette Lite (zero infrastructure)

[Datasette Lite](https://lite.datasette.io/) is Datasette compiled to WebAssembly. A static-hosted HTML page loads the SQLite file from a URL, runs Datasette entirely in the user's browser, and serves the interface. No server. No deploy.

```
https://lite.datasette.io/?url=https://github.com/{user}/{project}/raw/main/data/processed/elections.db
```

For datasets up to ~50 MB this works well and costs nothing. Above that, the browser's memory becomes the constraint. Best for small projects, demonstrations, and personal datasets.

### `datasette publish cloudrun` (built-in)

Google Cloud Run. The Datasette package ships this command natively:

```bash
uvx datasette publish cloudrun data/processed/elections.db \
    --metadata data/processed/metadata.yaml \
    --service boulder-election-results \
    --install datasette-cluster-map --install datasette-render-markdown
```

Builds a Docker image, deploys it, returns a URL. Cloud Run's free tier handles small-traffic civic sites for free.

### `datasette publish vercel` (plugin)

[Vercel](https://vercel.com/) via the [`datasette-publish-vercel`](https://github.com/simonw/datasette-publish-vercel) plugin. Serverless functions; free tier suitable for most civic-data sites:

```bash
uvx --with datasette-publish-vercel \
    datasette publish vercel data/processed/elections.db \
    --metadata data/processed/metadata.yaml \
    --project boulder-election-results \
    --install datasette-cluster-map
```

### `datasette publish fly` (plugin)

[Fly.io](https://fly.io/) via [`datasette-publish-fly`](https://github.com/simonw/datasette-publish-fly). Edge containers, supports SpatiaLite extension for geospatial data:

```bash
uvx --with datasette-publish-fly \
    datasette publish fly data/processed/elections.db \
    --metadata data/processed/metadata.yaml \
    --app boulder-election-results \
    --spatialite
```

### Choosing among them

For most civic projects, the choice is between Datasette Lite (one-off or small datasets) and Vercel or Fly (ongoing deployments under a custom domain). Cloud Run is right when the project is already in a GCP environment.

A pattern worth considering: ship to Datasette Lite for the "always available" demo URL, and to Vercel or Fly for the canonical production instance. The Lite URL works even when the production deploy is rebuilding.

## Datasette Agent (alpha, May 2026)

[Datasette Agent](https://datasette.io/blog/2026/datasette-agent/) is a plugin (released May 21, 2026, alpha) that adds a conversational LLM interface to a Datasette instance. The agent uses the [LLM library](https://llm.datasette.io/) to support hundreds of tool-calling models — OpenAI, Anthropic, Gemini, and open-weight models via local providers like LM Studio or Ollama. Readers ask natural-language questions; the agent writes SQL and returns the result.

Local run for development:

```bash
uvx --prerelease=allow --with datasette-agent \
    datasette -s plugins.datasette-llm.default_model gpt-5.5 \
    --internal internal.db --root data/processed/elections.db
```

When the agent helps:

- **Reporter or researcher discovery.** Someone unfamiliar with the schema asks "which contests had the closest margins in 2020?" and gets a useful SQL query and answer.
- **Reducing the SQL barrier.** Datasette's SQL UI is excellent for people who write SQL; the agent extends usefulness to those who don't.
- **Schema exploration.** "What columns describe the candidate?" reads from `metadata.yaml` and the database schema together.

When the agent doesn't help, or hurts:

- **As a substitute for canned queries.** A frequently-asked question is better served by a canned query with a stable URL than by a per-request LLM call.
- **For high-stakes citation.** LLM-generated SQL may be subtly wrong (off-by-one filters, wrong join condition). For data that will be cited publicly, the human-written canned query is the durable artifact.
- **Without rate limiting and identity.** A public Datasette Agent without sign-in costs real money under any traffic spike.

For a stable civic dataset, starting with a published Datasette without the agent and adding it later — once the metadata, canned queries, and faceting are solid — is the safer order.

## SQL patterns worth canning

Code these as canned queries in `metadata.yaml` and they become the stable read-paths for the dataset. (The PyCon SQLite tutorial's "Advanced SQL" chapter covers each in depth.)

### Aggregations by category and vintage

```sql
SELECT vintage, contest, SUM(votes) AS total_votes
FROM elections
WHERE votes IS NOT NULL
GROUP BY vintage, contest
ORDER BY vintage DESC, total_votes DESC
```

### CTEs for cross-vintage comparison

```sql
WITH by_year AS (
    SELECT vintage, contest, candidate, SUM(votes) AS votes
    FROM elections
    WHERE votes IS NOT NULL
    GROUP BY vintage, contest, candidate
)
SELECT a.contest, a.candidate,
       a.votes AS votes_2020, b.votes AS votes_2024,
       (b.votes - a.votes) AS delta
FROM by_year a
JOIN by_year b USING (contest, candidate)
WHERE a.vintage = '2020-general' AND b.vintage = '2024-general'
ORDER BY ABS(delta) DESC
```

### Window functions for year-over-year change

```sql
SELECT vintage, contest, candidate, SUM(votes) AS votes,
       SUM(votes) - LAG(SUM(votes)) OVER (
           PARTITION BY contest, candidate ORDER BY vintage
       ) AS change_from_prior
FROM elections
GROUP BY vintage, contest, candidate
ORDER BY contest, candidate, vintage
```

### Joining to provenance

```sql
SELECT e.vintage, e.contest, SUM(e.votes) AS total,
       p.source_url, p.retrieved_at, p.sha256
FROM elections e
JOIN provenance p USING (source, vintage)
WHERE e.contest = :contest
GROUP BY e.vintage, e.contest, p.source_url, p.retrieved_at, p.sha256
```

The `:contest` is a Datasette named parameter — when the canned query is published, the URL gets a form input letting readers fill it in.

## Common failure modes — Datasette

| Symptom | Likely cause | Fix |
|---|---|---|
| `sqlite-utils insert` reads numeric columns with leading zeros as `INTEGER` | Schema inference; column looked numeric | Pass `--text` for those columns, or `transform` after insert with `--type col TEXT` |
| Facets don't appear for a column with reasonable cardinality | Column not indexed; Datasette falls back to no-facet | Add an index via `sqlite-utils create-index`; declare in `metadata.yaml` `facets` list |
| Published Datasette shows raw HTML in a column | Plain-text rendering of HTML-containing column | Add `datasette-render-html` plugin and declare the column in metadata; or strip HTML during clean |
| Canned query times out under load | Inefficient SQL or missing index | `EXPLAIN QUERY PLAN <sql>` in the SQL view; add indexes or rewrite to avoid full scans |
| `datasette publish vercel` deploy succeeds but the page 500s | Plugin installed at deploy didn't pin a compatible version | Pin the plugin version in `--install datasette-cluster-map==0.18.2`; check the deploy logs |
| Full-text search returns no rows for an obviously-matching term | FTS index not refreshed after data update | Re-run `sqlite-utils enable-fts ... --replace` or use `sqlite-utils populate-fts` |
| Database file in deploy is stale | CI deployed before `scripts/publish.py build` ran | Make `build` a hard prerequisite of `datasette publish` in the workflow |
| Datasette Agent generates a query that joins to the wrong key | Provenance table not foreign-keyed; agent guesses | Add the foreign key with `sqlite-utils add-foreign-key`; refresh the schema-prompt the agent uses |

---

# Part 2: Quarto + GitHub Pages

[Quarto](https://quarto.org/) authors `.qmd` files (Markdown with executable code blocks in Python, R, Julia, or Observable JS), renders to HTML / PDF / Word, and publishes to GitHub Pages with one command. The result is a static site sitting alongside the GitHub repo, free to host, with clean URLs the project can cite.

## Why Quarto alongside Datasette

Datasette publishes the *data interface* — per-column metadata, faceted browsing, canned queries, SQL editor. Quarto publishes the *prose about how to use it* — methodology, long-form data dictionary, tutorials, change log, replication code. The split matches what readers want at different moments:

| Content | Lives in | Reason |
|---|---|---|
| Per-column description, units, controlled vocabulary | Datasette `metadata.yaml` | Renders inline with the column; readers see it where they need it |
| Long-form column rationale, vintage breakpoints, caveats | `docs/data-dictionary.qmd` | Too long for inline metadata; benefits from prose, links, examples |
| Canned queries with named parameters | Datasette `metadata.yaml` | Datasette renders these as forms; readers run them in the browser |
| Methodology essays, reconciliation logs, change log | `docs/*.qmd` | Static prose; readers consume sequentially, not query-by-query |
| The data itself | Datasette + CSV/Parquet downloads | The site is *about* the data, not a copy of it |

A small script in `scripts/publish.py` can read `docs/data-dictionary.md` (or `.qmd` front-matter + content) and emit `metadata.yaml`'s per-column descriptions, so the long form and the inline form stay in sync.

## Minimum viable Quarto setup

The `_quarto.yml` at the project root declares it a Quarto project and tells Quarto how to render:

```yaml
project:
  type: website
  output-dir: _site

website:
  title: "{{ project_name }}"
  description: "{{ description }}"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - href: data-dictionary.qmd
        text: Data dictionary
      - href: filter-pivot-recipes.qmd
        text: Recipes
      - href: methodology.qmd
        text: Methodology
    right:
      - icon: github
        href: https://github.com/{{ owner }}/{{ project_name }}
      - text: "Datasette"
        href: https://{{ project_name }}.vercel.app/

format:
  html:
    theme: cosmo
    toc: true
    code-copy: true
    code-overflow: wrap

execute:
  freeze: auto      # store computation results; re-run only when source changes
```

A small set of `.qmd` files in `docs/` becomes the site:

- `docs/index.qmd` — landing page: what the dataset is, where to get it, who to cite, the Datasette URL, the bulk-download URL.
- `docs/data-dictionary.qmd` — the long-form column-by-column reference.
- `docs/filter-pivot-recipes.qmd` — Python/pandas + R/tidyverse + SQL/DuckDB recipes, with executable code blocks that run against a small sample of the data committed to the repo.
- `docs/methodology.qmd` — how the data was extracted, what's known to be incomplete, the reconciliation log, the cross-source caveats from the concept catalog.
- `docs/changelog.qmd` — what changed in each vintage, what schema migrations happened, what's deprecated.

This is the documentation a journalist or researcher reads *before* opening the CSV.

## Publishing with `quarto publish gh-pages` (one-time setup)

Quarto needs a one-time local setup to create the `gh-pages` branch — this isn't optional, because the GitHub Action below relies on the branch already existing:

```bash
quarto publish gh-pages
```

That command renders the site, creates a `gh-pages` orphan branch with just the rendered output, pushes it, and (for project sites) GitHub auto-configures Pages to serve from it. The URL is `https://<owner>.github.io/<repo>/`. Custom domains work via a `CNAME` file at the project root — see [Quarto's GitHub Pages docs](https://quarto.org/docs/publishing/github-pages.html) for the details.

## Automated publishing via GitHub Actions

After the one-time local setup, automation is a small workflow:

```yaml
# .github/workflows/gh-pages.yml
name: Quarto site

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - '_quarto.yml'
      - 'data/processed/**'   # rebuild when the data changes
  workflow_dispatch:

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write          # required to push to gh-pages
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true            # pull LFS pointers (see Part 3: Git LFS)

      - uses: quarto-dev/quarto-actions/setup@v2

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true

      - name: Install Python and project dependencies
        run: uv sync --extra publish

      - name: Render and publish to gh-pages
        uses: quarto-dev/quarto-actions/publish@v2
        with:
          target: gh-pages
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The key elements:

- **`permissions: contents: write`** — required so the action can push to `gh-pages`. Without it the publish step fails with a 403.
- **`quarto-dev/quarto-actions/setup@v2`** then **`publish@v2 target: gh-pages`** — the two-step canonical pattern. `publish@v2` renders before pushing by default; set `render: false` if rendering happens elsewhere.
- **`paths:` filter** — rerender only when `docs/`, `_quarto.yml`, or the data itself changes. Avoids spurious rebuilds.
- **`with: lfs: true`** — pulls Git LFS-tracked files so the Quarto site can embed sample data.

The `_freeze/` directory (created by `quarto render` with `freeze: auto`) should be committed to version control. It stores executed-code outputs so the GH Action only re-runs the code that actually changed, not the entire site every time. The PyCon SQLite tutorial's published instance uses this pattern.

## The LFS-and-Pages constraint

**Git LFS files do not work in GitHub Pages sites** — so the Quarto site cannot serve LFS-tracked data files directly. It can embed small non-LFS samples committed under `docs/`, and it can link out to the bulk data hosted elsewhere (the Datasette URL, a GitHub Release, a Zenodo DOI). See [The critical caveat: LFS cannot be used with GitHub Pages](#the-critical-caveat-lfs-cannot-be-used-with-github-pages) in Part 3 for the full statement, the per-plan size limits, and the natural division of labor across surfaces.

## Common failure modes — Quarto

| Symptom | Likely cause | Fix |
|---|---|---|
| Quarto GH Action fails with 403 on push to gh-pages | Workflow lacks `contents: write` permission | Add `permissions: contents: write` at workflow or job level |
| Quarto re-runs all code on every CI build, taking 20+ minutes | `_freeze/` not committed; `freeze: auto` not configured | Set `execute: freeze: auto` in `_quarto.yml`; run `quarto render` locally; commit `_freeze/` |
| `quarto publish gh-pages` fails: "branch does not exist" | First-time setup never run; GH Action depends on the branch already existing | Run `quarto publish gh-pages` once locally before relying on the Action |
| Quarto site shows pointer text instead of an embedded data file | LFS-tracked file referenced from a `.qmd`; Pages can't serve LFS | Move a small sample (non-LFS) under `docs/`; link to the Datasette URL or a Release for the full file |
| `.md` files in `docs/` render with the site title instead of their own | Missing YAML frontmatter | Add `---\ntitle: "Page title"\n---` at the top |

---

# Part 3: Git LFS for large datasets

A liberation project accumulates two kinds of files that strain ordinary Git: large source artifacts (full-resolution scanned PDFs, multi-gigabyte XML dumps, archive ZIPs) and large processed outputs (multi-million-row Parquet files). GitHub politely rejects files over 100 MB and *recommends* keeping repos under 1 GB total. [Git Large File Storage (LFS)](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) is the escape hatch: Git tracks a small pointer file (sha256 + size, ~130 bytes), and the actual content lives on a separate LFS server that GitHub provides. LFS dumps raw artifacts as opaque downloadable files; [DocumentCloud](#part-4-documentcloud) renders them with a reader UI — pick the right one for the source by the *reader want* (tarball vs page-anchored permalink).

## When LFS earns its keep

- **`data/original/` artifacts over ~25 MB.** Election Statement of Vote PDFs from large counties; full-resolution scanned annual reports; agency document-dump ZIPs.
- **Processed Parquet files over ~100 MB.** Multi-million-row tidy long-form outputs; multi-decade longitudinal datasets.
- **Reproducible build artifacts.** A SQLite database that's expensive to rebuild (hours of OCR or scraping) and that downstream users want to clone-and-go.

When LFS doesn't earn its keep:

- **The processed CSV is under 10 MB.** Standard Git handles it fine, with the diff history downstream users actually want.
- **The source artifact can be re-fetched.** A small fetch script + a URL in `provenance.csv` is more durable than an LFS pointer that depends on GitHub's LFS billing remaining favorable.

The single most-cited disadvantage of LFS for civic projects: it imposes a billing dependency on GitHub. The free plan ships with 1 GB storage and 1 GB/month bandwidth bundled; data packs cost real money beyond that. For a project that may outlive a particular developer's GitHub account, this is a coupling worth understanding.

## Setting up LFS

```bash
# One-time per machine
git lfs install

# Per-repo: declare which file globs are LFS-tracked
git lfs track "data/original/*.pdf"
git lfs track "data/original/**/*.pdf"
git lfs track "data/processed/*.parquet"
git lfs track "data/processed/*.db"

# This created/modified .gitattributes — commit it
git add .gitattributes
```

The `.gitattributes` entries look like:

```
data/original/*.pdf filter=lfs diff=lfs merge=lfs -text
data/original/**/*.pdf filter=lfs diff=lfs merge=lfs -text
data/processed/*.parquet filter=lfs diff=lfs merge=lfs -text
data/processed/*.db filter=lfs diff=lfs merge=lfs -text
```

Now `git add` on a matching file pushes the content to LFS and commits the pointer. `git clone` of the repo downloads pointers only; `git lfs pull` (or `git clone --recurse-submodules` with LFS configured) downloads the actual files.

## Per-file size limits by plan

| Plan | Per-file limit |
|---|---|
| GitHub Free | 2 GB |
| GitHub Pro | 2 GB |
| GitHub Team | 4 GB |
| GitHub Enterprise Cloud | 5 GB |

Files exceeding the per-file limit are rejected with a clear error. For artifacts larger than 5 GB — full Common Crawl snapshots, multi-region warehouse dumps — LFS is not the right tool; use [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github) for one-off attached binaries (per-file limit 2 GB but no LFS billing), [Zenodo](https://zenodo.org/) for citable archival (the PUDL pattern), or a separate object-storage bucket linked from `provenance.csv`.

## The critical caveat: LFS cannot be used with GitHub Pages

**Git LFS files do not work in GitHub Pages sites.** Pages serves content from the `gh-pages` branch directly; LFS pointers in that branch resolve to text-pointer-file content, not the underlying data. This is a hard architectural constraint, [documented in GitHub's docs](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).

The implication for the layered publishing setup:

- The Quarto site (published to `gh-pages`) **cannot serve LFS-tracked data files directly.** A `docs/methodology.qmd` that tries to embed a 500 MB Parquet via a link will serve the LFS pointer text, not the data.
- The Quarto site **can embed small samples** of the data — the first 1000 rows committed as a regular file (not LFS-tracked) under `docs/` works fine.
- The Quarto site **can link out to the bulk data** hosted elsewhere — the Datasette deployment URL, a GitHub Release asset, a Zenodo DOI, an S3 bucket.

The natural division of labor:

- **`data/original/` LFS-tracked, in the main branch.** The pipeline reads from here. CI checks out with `lfs: true`. Not exposed to Pages.
- **`data/processed/<project>.db` built fresh during the Datasette publish step.** Deployed to Vercel/Fly/Cloud Run, *not* served from Pages. LFS plays no role here.
- **`data/processed/<project>.csv` and `.parquet`** — if small (<10 MB), regular Git; if large, LFS in main + small sample committed under `docs/` for the Quarto site to embed + a GitHub Release with the full file attached for direct download.
- **`docs/_freeze/` and rendered `_site/`** — never LFS; checked into Git normally so Pages serves them.

This works out to a clean three-deployment architecture: Pages serves the documentation, the Datasette platform serves the queryable data, and Releases (or Zenodo) serve the citable archival snapshots. Each surface plays to its strengths; nothing tries to serve LFS through Pages.

## LFS in CI

Workflows that need the actual data files must pull LFS in checkout:

```yaml
- uses: actions/checkout@v4
  with:
    lfs: true            # pull LFS-tracked files, not just pointers
```

This counts against the repo's LFS bandwidth quota. For projects with heavy CI activity (every PR triggers a full pipeline run with LFS data), this can exhaust the free 1 GB/month quickly. Mitigations:

- **Cache LFS objects** in CI: GitHub Actions caches `~/.cache/lfs` between runs.
- **Skip LFS in jobs that don't need it**: the test job that runs schema unit tests against `tests/fixtures/` doesn't need the full 5 GB of `data/original/`; the full pipeline job does.
- **Don't re-fetch on every commit**: the `refresh.yml` workflow that runs the pipeline against the upstream sources usually doesn't need LFS at all — it's *writing* new data to LFS, not reading existing data.

## Common failure modes — Git LFS

| Symptom | Likely cause | Fix |
|---|---|---|
| Quarto / Pages site shows pointer text instead of an embedded data file | LFS-tracked file referenced from a `.qmd`; Pages can't serve LFS | Move a small sample (non-LFS) under `docs/`; link to the Datasette URL or a Release for the full file |
| `git clone` of a fresh repo lacks data files | LFS not installed; only pointers were pulled | Contributor runs `git lfs install` once, then `git lfs pull` |
| LFS bandwidth quota exhausted mid-month | Heavy CI with `lfs: true` on every job | Cache LFS objects in CI; skip `lfs: true` on jobs that don't need raw data |
| File rejected at `git push`: "exceeds size limit" | File over 100 MB but not LFS-tracked | Add the pattern to `.gitattributes` *before* the first commit of the file; use `git lfs migrate` for retroactive conversion |

---

# Part 4: DocumentCloud

[DocumentCloud](https://www.documentcloud.org/) (a MuckRock project, descended from the *New York Times* and *ProPublica* journalism platform) is the publishing endpoint for the *source documents themselves* — the PDFs, scanned originals, FOIA responses, and agency reports that the processed CSV was extracted from. Hosting them on DocumentCloud rather than dumping them in LFS gives readers a real reading UI, automatic OCR, page-level permalinks, text-selection permalinks, annotations, embed iframes, and full-text search across the corpus. It's the difference between *the data is reproducible* and *the data is accountable*.

## When to reach for DocumentCloud

| If the source artifacts are… | And readers will… | Then |
|---|---|---|
| Born-digital PDFs in `data/original/` (statements of vote, budget books, annual reports) | Want to verify a number by looking at the original page it came from | **Yes** — DocumentCloud's page-permalink + text-selection-permalink is the affordance |
| Scanned PDFs that need OCR before they're searchable | Want to search the corpus by phrase, not just by filename | **Yes** — DocumentCloud OCRs every upload and exposes the text via search |
| FOIA responses (often hundreds of documents per request) | Want a single browsable, citable corpus | **Yes** — `Project` model groups documents; the project has its own URL |
| Multi-gigabyte raw archives, ZIPs, parquet files | Want a tarball download, not a reader | **No** — use [Part 3: Git LFS](#part-3-git-lfs-for-large-datasets) or GitHub Releases |
| Already-tidy CSV / Parquet (no originals worth showing) | Want to query the data | **No** — use [Part 1: Datasette](#part-1-datasette--sqlite-utils) |
| Source documents in a *sensitive* corpus (whistleblower drops, draft FOIAs, redaction-in-progress) | Need controlled access | DocumentCloud's `private` and `organization` access levels handle this; LFS doesn't have access control beyond the repo |

The rule: **if a reader of the published Datasette / Quarto pages might want to click through to the source PDF, the source PDF should be on DocumentCloud.** If not, LFS or Releases.

## Install and authenticate

```bash
uv add python-documentcloud
```

`python-documentcloud` (the [official MuckRock wrapper](https://github.com/MuckRock/python-documentcloud)) is the canonical client. The library reads anonymously without credentials (public documents only) and authenticated with a DocumentCloud account:

```python
from documentcloud import DocumentCloud

client_anon = DocumentCloud()                          # public read only
client = DocumentCloud(USERNAME, PASSWORD)             # upload + read private
```

For projects, register a *Squarelet* account (the MuckRock auth service) and store the credentials in `.env` alongside the project's other secrets. **Never commit credentials**; the `.env` template in the project template already excludes them.

## Upload patterns

The four upload modes cover every civic-data ingestion shape:

```python
# 1. Single document from local path
doc = client.documents.upload(
    "data/original/boulder_county_sov/2024/sov-2024-general.pdf",
    title="Boulder County Statement of Vote, 2024 General",
    source="Boulder County Clerk and Recorder",
    project=PROJECT_ID,
    access="public",
)

# 2. Multiple URLs (DocumentCloud fetches them — useful when the source
#    publisher hosts the artifact and you don't want to mirror)
docs = client.documents.upload_urls([
    "https://bouldercounty.gov/elections/results/2024-general.pdf",
    "https://bouldercounty.gov/elections/results/2024-primary.pdf",
], project=PROJECT_ID, access="public")

# 3. Directory of PDFs at once (recommended for bulk vintages)
docs = client.documents.upload_directory(
    "data/original/boulder_county_sov/2024/",
    project=PROJECT_ID,
)

# 4. Non-PDF source files (DOCX, TXT, XLSX) — pass extension explicitly
doc = client.documents.upload(
    "data/original/agency_response/foia_log.xlsx",
    original_extension="xlsx",
)
```

Uploads enter a server-side processing queue. Documents are not viewable, searchable, or embeddable until processing completes — poll the document's status field if your pipeline needs to wait synchronously:

```python
import time
while doc.status != "success":
    time.sleep(5)
    doc = client.documents.get(doc.id)
```

For bulk corpora (more than a few hundred documents), use the [`pneumatic`](https://github.com/anthonydb/pneumatic) or [`dcupload`](https://github.com/onyxfish/dcupload) bulk-upload CLIs rather than scripting around `upload()` directly — they handle retry, deduplication, and rate-limit backoff that the basic library leaves to the caller.

## Projects — organizing the corpus

Every uploaded document should belong to a **project**. A project has its own canonical URL (`documentcloud.org/projects/<id>`), and the project page is where readers land when following an "all source documents" link from the Quarto site or Datasette metadata.

```python
project = client.projects.create(
    title="Boulder County Election Results — Source Documents",
    description="Statements of vote and underlying ballots, 2004–present. "
                "Liberated by github.com/owner/boulder-elections.",
)
project.document_list = docs   # attach uploaded documents
project.put()
```

The project structure should mirror the source registry in `scripts/config.py::SOURCES` — one DocumentCloud project per source registry slug, or one project per (source × vintage) for long-running series. Document this convention in `AGENTS.md` under *Deployment surface*.

## Embedding in the Quarto site

DocumentCloud's main reader-facing payoff is the **embed iframe** — every document gets HTML that drops cleanly into a Quarto page:

```html
<iframe src="https://embed.documentcloud.org/documents/{ID}/?embed=1"
        width="100%" height="600" frameborder="0">
</iframe>
```

The library exposes this directly:

```python
doc.embed_code()       # full <iframe> HTML
doc.canonical_url      # plain link to the reader UI
```

The plain full-document embed is the right default, but the embed URL accepts query parameters that change what the reader lands on — and a methodology page is *much* more legible when the embed opens on the exact page being discussed rather than the document's title page. Three useful variants:

```html
<!-- Open on a specific page -->
<iframe src="https://embed.documentcloud.org/documents/{ID}/?embed=1&page=17"
        width="100%" height="600"></iframe>

<!-- Open on a specific note (annotation) by note ID -->
<iframe src="https://embed.documentcloud.org/documents/{ID}/annotations/{NOTE_ID}/?embed=1"
        width="100%" height="600"></iframe>

<!-- Page-image only (no reader UI) — useful for a static thumbnail next to body text -->
<img src="https://embed.documentcloud.org/documents/{ID}/pages/17-large.gif"
     alt="SoV 2024 page 17 — Boulder County precinct totals">
```

The page-anchored iframe is the workhorse. Combine with a permalinked text-selection URL — the DocumentCloud reader supports `?selection={start}-{end}` URL fragments that highlight a text range — and a methodology paragraph can deep-link into the exact paragraph of the original that the processed CSV's column was derived from.

Inside a `.qmd` file, the canonical pattern is to keep iframe HTML in per-document partial files under `docs/_includes/` and `{{< include >}}` them from the prose pages, so the same embed can appear in multiple places (methodology page, vintage changelog entry, data-dictionary caveat) without copy-pasting the iframe markup. The partial files are tiny — typically 3-line HTML stubs — but factoring them out keeps the `.qmd` source readable:

```markdown
## How the 2024 results were extracted

The published Statement of Vote ([source]({{< var sov_2024_url >}})) is
a 412-page PDF. Pages 17–143 carry the precinct-by-contest tables that
became `data/processed/elections.csv`.

{{< include _includes/sov_2024_pages_17_to_143_embed.html >}}

The vote-totals row at the bottom of every precinct block is the
authoritative figure `reconcile.py` verifies against.
```

For a *comparison* layout — two source vintages side by side on the same Quarto page — Quarto's column layout works directly with iframes:

```markdown
:::: {.columns}
::: {.column width="50%"}
**2020 General**
{{< include _includes/sov_2020_embed.html >}}
:::
::: {.column width="50%"}
**2024 General**
{{< include _includes/sov_2024_embed.html >}}
:::
::::
```

Two practical notes on rendering: (1) Iframes are *not* captured by Quarto's `freeze: auto` cache — every render fetches DocumentCloud live. That's the right default (the embed reflects the current state of the source document) but it means the rendered site will have broken embeds if the network is down at render time or if the document has been deleted from DocumentCloud. Pin the document IDs in `_quarto.yml`'s `var` block or in a per-source YAML so a typo doesn't silently break the build. (2) For PDF output of the Quarto site, iframes don't render — replace them at PDF-build time with the page-image variants (the `pages/N-large.gif` URLs) plus a permalink to the live reader.

The LFS-cannot-serve-from-Pages constraint (see [Part 3: Git LFS](#the-critical-caveat-lfs-cannot-be-used-with-github-pages)) is what makes DocumentCloud structurally important here: the Quarto site can embed DocumentCloud iframes without serving the PDFs from `gh-pages`. The methodology page describes the data; the iframe shows the data; the underlying file lives on a third host that handles the OCR and the reader UI for free.

## Splitting large documents before upload

DocumentCloud accepts large PDFs but its sweet spot is documents in the ~50-page range. Multi-hundred-page PDFs (the typical scale of a county Comprehensive Plan, a multi-year fiscal report, or a complete EIS) hit three real problems: (1) server-side OCR takes minutes-to-hours and occasionally fails silently; (2) the reader UI gets sluggish over ~500 pages, especially on mobile; (3) the embed's page-anchored URL is less useful when the relevant page is one of two thousand. Splitting upstream — before upload — solves all three.

Splitting is a *parser-side* concern, not a DocumentCloud concern. The immutable-originals discipline (`data/original/` is write-once) means splits live as derived files. Two conventions work:

- **Split-at-upload**, no on-disk derivative: the parser reads the whole original, slices into per-section page ranges in memory, and uploads each slice as a separate DocumentCloud document. The original PDF stays whole on disk; no `data/original/` mutation. Simplest; right default for most projects.
- **Split-and-persist**, derivative on disk: derived splits live under `data/original/<source>/<vintage>/_splits/` (or `data/processed/_splits/` if you prefer the derivative-bucket framing). Each split file gets its own entry in `manifest.json` with a `parent_sha256` field pointing back at the unsplit original. Heavier; useful when splits get cited or re-used independently of the parent.

For Python-native splitting, [`pypdf`](https://github.com/py-pdf/pypdf) is the canonical library (formerly PyPDF2):

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("data/original/boulder/sov-2024-general.pdf")
splits = [
    ("sov-2024-general_summary",          0, 16),    # cover + summary
    ("sov-2024-general_precincts",       16, 143),   # the precinct tables
    ("sov-2024-general_recount_appendix", 143, 412), # appendices
]
for name, start, end in splits:
    writer = PdfWriter()
    for i in range(start, end):
        writer.add_page(reader.pages[i])
    with open(f"/tmp/{name}.pdf", "wb") as f:
        writer.write(f)
```

For command-line splitting in shell pipelines, [`qpdf`](https://github.com/qpdf/qpdf) (`qpdf input.pdf --pages . 17-143 -- output.pdf`) and [`pdftk`](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/) (`pdftk input.pdf cat 17-143 output output.pdf`) are the durable choices — pick whichever is already in the project's container or system image. Both handle multi-gigabyte PDFs without loading them into memory.

The harder question is *where* to split. Three strategies, in order of robustness:

- **By structural marker** (most robust). Use `pdfplumber` to scan the PDF for a known section boundary — "PRECINCT REPORT" header, a fiscal-year-divider page, a contest-name change — and split at those page indices. The split logic lives in `scripts/parsers/_split.py` (or inline in the parser); the markers belong in the parser's docstring or `AGENTS.md` so a future contributor knows why the page boundaries are what they are. Vintage-specific: different years may have moved the marker.
- **By section in a table of contents** (when the source has a parseable ToC). `pypdf` exposes `reader.outline` — if the publisher included PDF bookmarks, those are the right split points and they survive across vintages if the publisher's template stayed put.
- **By fixed page count** (last resort). 100-page chunks with a 5-page overlap so context isn't lost at the boundary. Easy to script, terrible for citation — the chunks have no semantic meaning and a reader following a permalink lands on an arbitrary mid-document page.

Whichever strategy, the split chunks need to carry their lineage in provenance so the chain of custody back to the original survives. Conventions:

- **Naming.** `<original-stem>_<descriptor>.pdf` (`sov-2024-general_precincts.pdf`) when splitting by marker; `<original-stem>_pages-N-to-M.pdf` when splitting by page range. Names are stable across re-runs so the upload step's dedup-by-sha256 stays reliable.
- **`provenance.csv` extensions.** Add `parent_sha256` (the unsplit original's hash), `parent_documentcloud_url` (a link to the unsplit version if it's also on DocumentCloud), and `page_range` (`17-143`) columns. The processed-CSV-row-to-source-page chain becomes: row → `(source, vintage)` → provenance entry → split DocumentCloud URL → page within the split.
- **`AGENTS.md` *Deployment surface* note.** Document the split convention per source — "Boulder SoV PDFs split into summary / precincts / appendices; the precincts split is the citable one; the appendices split is uploaded as `organization` because the recount narratives reference jurors by name" — so the access-level and citation choices stay legible.

A split is not a transformation in the parser sense — it doesn't change pixels or text. It's a packaging decision at the *publish* boundary. The split's content is the original's content; the value is purely that readers can find what they need without scrolling through 412 pages. Treat splitting as part of the upload step, not the cleaning step.

## Access levels and provenance chain-of-custody

DocumentCloud has three access levels:

| Level | Who sees it | When to use |
|---|---|---|
| `public` | Anyone (search-indexed) | Default for liberated public-record corpora |
| `organization` | Members of your DocumentCloud organization | In-progress liberation; documents from a pending FOIA that aren't yet ready to publish |
| `private` | Only the uploader | Sensitive material in early review; one-off testing |

The access decision is a **governance decision** (see [`project-template.md#governance`](project-template.md#governance)) and should be documented per source in `provenance.csv`. Add a `documentcloud_url` and `documentcloud_access` column to the provenance schema once DocumentCloud is in use; this keeps the chain of custody traceable: `processed CSV row → (source, vintage) → provenance.csv entry → DocumentCloud project URL → individual document URL → original page`.

The `source_url` column in `provenance.csv` should remain the *publisher's* original URL (the agency website where the document came from); the DocumentCloud URL is a *mirror* with reader affordances, not a replacement for the canonical source.

## Search and discovery

DocumentCloud's search is exposed both via web UI and the API:

```python
# All documents tagged with this project
hits = client.documents.search(f"projectid:{PROJECT_ID}")

# Full-text search across the corpus
hits = client.documents.search("non-resident alien tuition")

# Combine
hits = client.documents.search(f'projectid:{PROJECT_ID} "right to know"')
```

Search results respect the document's access level — anonymous queries see only `public` documents. For civic projects, this means the published corpus is discoverable by anyone searching DocumentCloud directly, not just by people who land on the project's Quarto site. That's part of the value: liberated documents become *findable* in the broader DocumentCloud corpus, not just behind one project's URL.

## Add-ons — DocumentCloud as an ETL hook

[DocumentCloud Add-ons](https://www.documentcloud.org/help/add-ons/) (GitHub-hosted Python scripts that run server-side against documents in a user's account) extend the platform with custom processing: redaction, entity extraction, language detection, classification, OCR-cleanup. Civic-data projects rarely need to author add-ons, but two existing add-ons are useful as upload-time hooks:

- [`documentcloud-scraper-addon`](https://github.com/MuckRock/documentcloud-scraper-addon) — periodically scrapes a publisher's site and uploads new artifacts to a project. Pair with `discover.py` to keep the DocumentCloud project in sync with the source registry.
- [`documentcloud-scraper-cron-addon`](https://github.com/MuckRock/documentcloud-scraper-cron-addon) — cron-driven version of the above for daily/weekly auto-refresh.

For projects with a custom ETL hook (entity extraction, redaction-on-upload), authoring a project-specific add-on can move processing off the project's CI infrastructure and onto DocumentCloud's, which scales better for large corpora.

## Common failure modes — DocumentCloud

| Symptom | Likely cause | Fix |
|---|---|---|
| `upload()` returns immediately but the document never appears in search | Server-side processing failed (OCR error, corrupted PDF, oversized file) | Poll `doc.status`; if `error`, check `doc.error_message`; for huge PDFs, split first |
| `upload_directory()` is slow and re-uploads on each run | No built-in deduplication | Use `pneumatic` or `dcupload` for bulk; or compute sha256 against an existing `documentcloud_url` column in provenance.csv and skip already-uploaded files |
| Embedded iframe shows a permissions-denied page | Document is `private` or `organization`-only; reader isn't logged in | Set `access="public"` for liberated documents; or accept the permission boundary for sensitive ones |
| Search returns nothing despite a known phrase | OCR hasn't run or failed | Check `doc.status == "success"`; re-trigger OCR via `doc.process()`; for image-only PDFs from older scans, OCR may need preprocessing first |
| `Unauthorized` on every upload despite correct credentials | Squarelet credentials expired or 2FA enabled | Refresh credentials via DocumentCloud web UI; use an API token instead of password |
| Documents uploaded but not visible in the project | Forgot `project=PROJECT_ID` on upload | `project.document_list = [...]; project.put()` to attach retroactively |
| `upload_urls()` queues fail silently for some URLs | DocumentCloud's fetcher hit a 403 / paywall / Cloudflare | Mirror the file locally first via `fetch.py`, then `upload()` from disk |

## Where this lives in the project

| Operation | Lives in |
|---|---|
| Initial bulk upload of an existing corpus | A one-off script under `scripts/` (e.g., `scripts/upload_to_documentcloud.py`); not part of the recurring pipeline |
| Per-refresh upload of newly-fetched documents | A new step in `refresh.yml` running after `fetch`, OR a DocumentCloud scraper add-on configured against the source URL |
| Project URL + access level | `provenance.csv` (extended schema) + `AGENTS.md` *Deployment surface* table |
| Embed iframes for the Quarto site | `docs/_includes/<source>_<vintage>_embed.html` partials referenced from the relevant `.qmd` pages |
| Credentials | `.env` (gitignored) + GitHub Actions secrets (`DOCUMENTCLOUD_USERNAME`, `DOCUMENTCLOUD_PASSWORD`) |

DocumentCloud is the fourth publishing surface; it sits next to Datasette, Quarto, and LFS, not on top of them. The recurring-refresh PR pattern (see [`pipeline.md`](pipeline.md)) extends naturally: a cron-driven `discover → fetch → clean → audit → upload-to-documentcloud → audit-the-upload` chain, with each new vintage producing both a processed-CSV row *and* a citable source-document URL.

---

## What to write in the AGENTS.md

**Datasette (queryable data interface):**

- **Build command and target** — exact `scripts.publish build` invocation that produces the `.db`, and the deployment command (or workflow path) that ships it.
- **Metadata source of truth** — typically `docs/data-dictionary.md`, generated into `metadata.yaml` by `scripts/publish.py`; warn readers not to edit `metadata.yaml` by hand.
- **Deployment surface** — production URL, Datasette Lite URL if any, auth posture.
- **Plugin set** — which plugins are installed in production and why; explicitly note whether Datasette Agent is enabled.
- **Canned-query catalog** — short list of named queries in `metadata.yaml` with one sentence each on what they're for. New canned queries are the cheapest user-research signal.
- **Refresh workflow** — what triggers a redeploy (typically merging a refresh PR).

**Quarto (documentation site):**

- **Site URL and source of truth** — `https://<owner>.github.io/<project>/`, rendered from `docs/*.qmd` by `.github/workflows/gh-pages.yml`.
- **`docs/` ↔ `metadata.yaml` split** — which content lives where, and how they're kept in sync (typically `scripts/publish.py` generates `metadata.yaml` from `docs/data-dictionary.md`).
- **Freeze policy** — code in `.qmd` files executes locally with `_freeze/` committed, or re-runs in CI on every render (slower but always fresh).

**Git LFS (bulk distribution):**

- **What's tracked** — globs in `.gitattributes`; the one-line contributor note that `git lfs install` is required.
- **Bandwidth posture** — Free / Pro / Team plan and any purchased data packs; which CI jobs skip `lfs: true` to conserve quota.
- **Pages constraint** — note explicitly that the Quarto site doesn't serve LFS; what it links to instead (Datasette URL, Releases).
- **Fallback if LFS budget is exceeded** — typically a mirror to GitHub Releases per tagged version, or Zenodo for citable archival.

**DocumentCloud (source documents):**

- **The DocumentCloud project URL(s)** — one per source registry slug, with the convention named.
- **Access level per source** — what's `public`, what's `organization`, what's `private`, and why. The justification is a governance decision per [`project-template.md#governance`](project-template.md#governance); document it where the access-level choice lives.
- **Upload-trigger policy** — does new content reach DocumentCloud automatically (via an add-on, or a step in `refresh.yml`) or manually? If automatic, where the credentials live (`.env`, GitHub secret) and which workflow uses them.
- **Quarto embed convention** — how the methodology pages reference DocumentCloud documents (direct iframe; partial-include of an iframe HTML file; jump-to-page links). Pick one and stick to it so the site reads consistently.
- **Provenance schema extensions** — `documentcloud_url` + `documentcloud_access` columns in `provenance.csv`; how the chain-of-custody is documented when a downstream reader follows a CSV row back to the source page.

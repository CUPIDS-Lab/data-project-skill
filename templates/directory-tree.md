# Canonical project layout (structural source of truth)

This file is read by the skill, not copied into the project. It defines the directory layout the orchestrator creates, annotated with the level at which each part appears. Prune to the chosen level; create empty data directories with a `.gitkeep`; document `data/raw` as immutable.

```
<project-slug>/
├── README.md                 # L0  front door; links every other doc
├── AGENTS.md                 # L0  repo-level guidance any agent reads first
├── ROADMAP.md                # L0  deferred-work record (now vs. later)
├── LICENSE                   # L0  (user adds; see LICENSE-NOTE at L5)
├── .gitignore                # L0  data-aware ignore rules
├── .gitattributes            # L0  line-ending normalization (+ optional LFS)
├── data/
│   ├── raw/        .gitkeep   # L0  original, immutable — never edited in place
│   ├── interim/    .gitkeep   # L0  intermediate transforms
│   ├── processed/  .gitkeep   # L0  final, analysis-ready
│   └── external/   .gitkeep   # L0  third-party sources (optional)
├── DATA-DICTIONARY.md        # L1  schema, grain, provenance, units, missingness, caveats
├── decision-log.md           # L1  dated design/data decisions with rationale
├── CHANGELOG.md              # L1  human-readable change history
├── exploratory/    .gitkeep  # L2  notebooks live here only — never shipped to production
├── Snakefile                 # L2  pipeline-as-code at the repo root (Python default); run `snakemake -n` from here
├── config.yaml               # L2  pipeline parameters & paths, resolved relative to the repo root
├── _targets.R                # L2  pipeline-as-code for the R variant (run via `targets::tar_make()`)
├── src/<pkg>/                # L2  Python source: reusable, importable, tested code (pkg = PKG_NAME, the slug with underscores)
├── R/                        # L2  R source: stage functions sourced by _targets.R (R projects use this instead of src/<pkg>/)
├── pipelines/                # L2+ MULTI-pipeline monorepo (the data-liberation hand-off): one self-contained
│   └── <name>/               #     pipeline per liberated source; each maps 1:1 to a tracked issue/sub-issue
│       ├── Snakefile         #     this pipeline's own DAG + the CI discovery marker (single-pipeline projects keep the root Snakefile above)
│       ├── config.yaml       #     this pipeline's parameters & paths
│       ├── environment.yml   #     this pipeline's pinned env (or point CI at a shared root env)
│       └── README.md         #     what it liberates, its sources, and its tidy output
├── results/
│   ├── figures/    .gitkeep  # L2  generated charts
│   └── tables/     .gitkeep  # L2  generated tables
├── tests/          .gitkeep  # L2  data/code validation
├── docs/           .gitkeep  # L2  Quarto/Markdown documentation
├── CONTRIBUTING.md           # L3  workflow + anti-pattern guardrails
├── CODE_OF_CONDUCT.md        # L3  inclusive collaboration norms
├── ROLES.md                  # L3  five roles, mediator, gap-check
├── CODEOWNERS                # L3  roles mapped to paths
├── GOVERNANCE.md             # L3  access tiers, retention, escalation, transparency/privacy
├── CHARTER.md                # L3  purpose, partners, shared definitions, what survives the pilot
├── .skills/                  # L3  nested guidance skills for downstream agents/humans
│   ├── data-intake/SKILL.md
│   ├── documentation/SKILL.md
│   └── release-and-share/SKILL.md
├── INSTALLED-BASE.md         # L4  values spine rendered as repo requirements
├── data-management-plan.md   # L4  storage, retention, sharing, backup, compliance
├── responsible-data-checklist.md   # L4  consent, minimization, harms, security
├── data-bulletproofing-checklist.md # L4  pre-publication QA
├── data-quality-checklist.md # L4  known-issues checks (bad-data taxonomy)
├── accessibility-checklist.md# L4  alt text, plain language, colorblind-safe viz
├── ai-catalog.json           # L5  ARD manifest: agent-discoverable resources (repo scope; see DISCOVERY.md)
├── DISCOVERY.md              # L5  what the catalog advertises + how to deploy it to host/registry (deferred)
├── dataverse/                # L5  Dataverse deposit kit (archive data/code/docs → citable DOI)
│   ├── dataset.json          #     citation metadata manifest (Native API format)
│   ├── deposit-dataverse.sh  #     curl deposit (zero-dep); deposit_dataverse.py is the pyDataverse path
│   └── DEPOSIT.md            #     what's deposited + how to run it (draft → confirm → publish)
├── opensharing/              # L5  OpenSharing zero-copy share kit (share data/AI assets in place)
│   ├── share.json            #     Share→Schema→Asset declaration (tables, volumes, .skills)
│   ├── share-profile.example.json  # recipient profile; copy → share-profile.json (gitignored) + add token
│   └── SHARING.md            #     what's shared + how to serve/consume it (governed by access tiers)
└── knowledge/                # L5  OKF bundle (concept catalog) generated from the data dictionary
    ├── index.md              #     bundle root; declares okf_version: "0.1"
    ├── datasets/<name>.md
    └── tables/<name>.md
```

Notes: `data/raw` is immutable (never edited in place); keep **bulk/external** raw out of version control (see `.gitignore`), but **track a small curated source-of-record** via a `.gitignore` carve-out and document it as immutable. The package directory under `src/<pkg>/` is named for the project and is the **repo-wide** location for reusable, importable, tested code (`R/` for the R variant); a nested `data-liberation` pipeline's own `scripts/` may stay local to its `pipelines/<name>/`. A **single-pipeline** project keeps `Snakefile`/`config.yaml` at the repo root (above); a repo hosting **several** liberated pipelines gives each its own `pipelines/<name>/` and maps each to a tracked issue/sub-issue — promote a root pipeline into `pipelines/<name>/` when a second one arrives, then land every subsequent pipeline by the ordered procedure in `references/landing-a-pipeline.md` (the monorepo CI `templates/ci/pipelines-ci.yml.tmpl` auto-discovers `pipelines/*/Snakefile`, so no workflow edit is needed per pipeline). Once the repo crosses ~3 pipelines, factor shared plumbing into a shared core — `src/<pkg>/` or a `pipelines/_core/` package — instead of copy-pasting it into each sibling (`references/stamping-and-shared-core.md`). At L0–L1 most of this collapses to the top-level docs plus `data/`. Everything above the chosen level belongs in `ROADMAP.md`, not on disk.

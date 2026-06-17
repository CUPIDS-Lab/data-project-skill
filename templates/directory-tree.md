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
├── src/<pkg>/                # L2  reusable, importable, tested source code (pkg = PKG_NAME: the slug with underscores, a valid Python module name)
├── pipelines/                # L2  pipeline-as-code (Snakefile / _targets.R) + config
│   ├── Snakefile             #     (Python default)
│   └── config.yaml
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
└── knowledge/                # L5  OKF bundle (concept catalog) generated from the data dictionary
    ├── index.md              #     bundle root; declares okf_version: "0.1"
    ├── datasets/<name>.md
    └── tables/<name>.md
```

Notes: keep `data/raw` read-only and out of version control (see `.gitignore`); the package directory under `src/` is named for the project. At L0–L1 most of this collapses to the top-level docs plus `data/`. Everything above the chosen level belongs in `ROADMAP.md`, not on disk.

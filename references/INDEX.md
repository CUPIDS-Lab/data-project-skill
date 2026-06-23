---
type: Crosswalk
title: Reference Corpus Crosswalk and Sampling Map
description: The map the indexer uses to sample practices for a project — goal→practice, profile-signal→emphasis, level→artifact, and artifact→template (with build status).
tags: [index, crosswalk, sampling]
---

# Reference Corpus Crosswalk (sampling map)

This is the indexer's primary working file. Use it to turn a Project Context Profile into a small, cited set of relevant practices and the templates they imply — a table lookup refined by judgment, not a vector search. Cite source files by name. With ~15 framework digests plus the skill's spine references this lookup is the right tool; if the corpus ever grows past a few dozen documents, revisit with a retrieval index.

Build status legend: **⭐ built** — the template/digest exists now and can be generated; **○ roadmap** — not yet built, so route the concern into `ROADMAP.md` instead of generating a file. As of this build, every template and digest below is **⭐ built**; the now/later mechanism (see `escalation-levels.md`) still defers concerns into `ROADMAP.md` by the user's choice, not because a template is missing.

## §A — Goal → Practice matrix

| Goal | Practices (source file) |
| --- | --- |
| **Accessible** | plain-language summary, multiple formats (`turing-way`); FAIR/open access (`turing-way`); colorblind-safe viz & alt text (`turing-way`, accessibility-checklist ⭐); OKF concept catalog at L5 (`okf-open-knowledge-format` ⭐); user-centered design & default-to-open (`usds-playbook`); agent-discovery catalog at L5 (`agentic-resource-discovery` ⭐); repository deposit for a DOI at L5 (`dataverse-deposit` ⭐); zero-copy data/AI-asset sharing at L5 (`open-sharing-protocol` ⭐) |
| **Documented** | data dictionary w/ grain, provenance, units, missingness, known-issues (`ouhsc-bbmc-practices`, `data-collaboratives-canvas`); decision log & changelog (`ouhsc-bbmc-practices`); README front door (`cookiecutter-data-science`); comments explain *why* (`github`); dataset transparency Data Card (`datacards-playbook`); engagement memo & assignable to-do checklist (`github`) |
| **Transparent** | immutable raw data & DAG provenance (`cookiecutter-data-science`); decision/change logs (`ouhsc-bbmc-practices`); data bulletproofing/QA (`propublica` ⭐, `quartz-bad-data-guide` ⭐); Data Card — provenance, uses, sensitive attributes (`datacards-playbook`); licensing (`turing-way`); access tiers & oversight (`installed-base`); published capability catalog (`agentic-resource-discovery` ⭐) |
| **Inclusive** | code of conduct & contributor recognition (`turing-way`); design partners vs. beneficiaries, mediator, gap-check (`collaboration-architecture`); responsible data & consent (`responsible-data-handbook`); sensitive-attributes & fairness documentation (`datacards-playbook`); accessible comms (`turing-way`) |
| **Collaborative** | feature-branch + PR workflow, CI (`github`); roles + CODEOWNERS (`collaboration-architecture`); collaboration canvas & governance (`data-collaboratives-canvas`); partner lifecycle & contributed-data intake (`propublica` ⭐); issue/project/milestone tracking (`github`) |
| **Reproducible** | standard tree & immutable raw (`cookiecutter-data-science`, `ouhsc-bbmc-practices`); pinned env + pipeline-as-code + dry-run (`snakemake`); seeds, linear scripts, validation (`ouhsc-bbmc-practices`); version control & testing (`turing-way`) |

## §B — Profile-signal → emphasis rules

| Signal in the Profile | Boost these sources | Require / route these artifacts |
| --- | --- | --- |
| sensitivity = sensitive-human / regulated / Indigenous (CARE) | `responsible-data-handbook`, `installed-base`, `ouhsc-bbmc-practices` | **fire the affordance↔duty coupling**; `responsible-data-checklist` ⭐, `data-management-plan` ⭐, `GOVERNANCE` ⭐; if too shallow for GOVERNANCE, write the coupling as a blocking `ROADMAP.md` item |
| multi-organization / cross-sector | `data-collaboratives-canvas`, `propublica` ⭐, `collaboration-architecture` | `GOVERNANCE` ⭐, `CHARTER` ⭐ (charter now carries the roles table + collaboration protocol) |
| contributed / crowdsourced data | `propublica` ⭐, `responsible-data-handbook` | contributed-data intake — folded into `data-management-plan` ⭐ |
| publishing / communicating findings | `propublica` ⭐, `quartz-bad-data-guide` | `data-bulletproofing-checklist` ⭐, `data-quality-checklist` ⭐ |
| publishing or sharing a dataset; sensitive attributes / fairness | `datacards-playbook` | `data-card` ⭐ |
| publish as open knowledge / FAIR | `okf-open-knowledge-format` ⭐, `turing-way` | `knowledge/` OKF bundle ⭐, `LICENSE-NOTE` ⭐ |
| make the project discoverable by agents; exposes skills, a dataset, MCP, or an API | `agentic-resource-discovery` ⭐ | `ai-catalog.json` (ARD) + `DISCOVERY.md` at **L5** ⭐; host `.well-known/` + registry deployment → `ROADMAP.md` |
| deposit / archive outputs in a data repository; get a DOI; Harvard Dataverse; FAIR findable; **data updated on a schedule / versioned / "streaming"** | `dataverse-deposit` ⭐ | `dataverse/` deposit kit (`dataset.json` + `deposit-dataverse.sh` + `deposit_dataverse.py` + `DEPOSIT.md`) at **L5** ⭐; deposit via Deposit mode (`data-project-depositor`); **periodically-updated** → `UPDATING` flag → scheduled `ci/dataverse-deposit.yml` versioned re-deposit ⭐ |
| share data/AI assets across orgs without copying; zero-copy; OpenSharing; Delta Sharing; scoped credentials | `open-sharing-protocol` ⭐ | `opensharing/` share kit (`share.json` + `share-profile.example.json` + `SHARING.md`) at **L5** ⭐; access gated by `GOVERNANCE.md` tiers |
| tooling = R | `ouhsc-bbmc-practices` | `r/` variant ⭐ (default Python ⭐) |
| accessibility flagged | `turing-way` | `accessibility-checklist` ⭐ |
| user-facing / civic service; openness or iterative delivery | `usds-playbook` | `project-design-canvas` ⭐, `accessibility-checklist` ⭐, `LICENSE-NOTE` ⭐ |
| collaborators / "how do we track work" / wants issues, a board, or a wiki | `github` | issue forms + `seed-github.sh` + Project at **L3** ⭐ (wiki seeds at L4 ⭐); below L3 keep to `NEXT-STEPS` + the `ROADMAP` checklist |
| multi-pipeline monorepo / liberating several sources / "add another pipeline" | `landing-a-pipeline` ⭐, `stamping-and-shared-core` ⭐ | `PIPELINES` flag → auto-discovered `ci/pipelines-ci.yml` ⭐ + one `pipelines/<name>/` per source; land each via the ordered flow in `landing-a-pipeline`; factor a shared core at ~3 pipelines (`stamping-and-shared-core`) |
| small synchronous team, low sensitivity | `cookiecutter-data-science`, `collaboration-architecture` (typology) | keep light — prefer L0–L1 ⭐ and `ROADMAP.md` over governance bloat |

## §C — Level → artifact → template (with build status)

| Level | Artifact | Template | Status |
| --- | --- | --- | --- |
| L0 | structure | `templates/directory-tree.md` | ⭐ |
| L0 | front door | `templates/README.md.tmpl` | ⭐ |
| L0 | agent guidance | `templates/AGENTS.md.tmpl` | ⭐ |
| L0 | assignable checklist + deferred work | `templates/ROADMAP.md.tmpl` | ⭐ |
| L0 | ignore / attributes | `templates/gitignore.tmpl`, `templates/gitattributes.tmpl` | ⭐ |
| L1 | data dictionary | `templates/data-dictionary.md.tmpl` | ⭐ |
| L1 | decision log / changelog | `templates/decision-log.md.tmpl`, `templates/CHANGELOG.md.tmpl` | ⭐ |
| L1 | handoff memo | `templates/NEXT-STEPS.md.tmpl` | ⭐ |
| L2 | env / pipeline / config (Python) | `templates/python/{environment.yml,Snakefile,config.yaml,pyproject.toml,pre-commit-config.yaml}.tmpl` | ⭐ |
| L2 | env / pipeline (R) | `templates/r/{DESCRIPTION,_targets.R,renv-note.md,Makefile}.tmpl` | ⭐ |
| L2 | CI (single project) | `templates/ci/github-actions-ci.yml.tmpl` | ⭐ |
| L2 | CI (multi-pipeline monorepo) | `templates/ci/pipelines-ci.yml.tmpl` | ⭐ |
| L3 | contributing / conduct | `templates/CONTRIBUTING.md.tmpl`, `templates/CODE_OF_CONDUCT.md.tmpl` | ⭐ |
| L3 | ownership | `templates/CODEOWNERS.tmpl` (paths → roles; roles live in `CHARTER.md.tmpl`) | ⭐ |
| L3 | governance / charter (+ roles, collaboration protocol, values spine) → `docs/governance/` | `templates/GOVERNANCE.md.tmpl`, `templates/CHARTER.md.tmpl` | ⭐ |
| L3 | nested guidance skills | `templates/nested-skills/{data-intake,documentation,release-and-share}.SKILL.md.tmpl` | ⭐ |
| L3 | how-we-track-work | folded into `templates/CONTRIBUTING.md.tmpl` | ⭐ |
| L3 | issue forms / PR / labels | `templates/github/ISSUE_TEMPLATE/{task,data-issue,config}.yml.tmpl`, `templates/github/PULL_REQUEST_TEMPLATE.md.tmpl`, `templates/github/labels.yml.tmpl` | ⭐ |
| L3 | issue seeding + access + project template | `templates/github/{seed-github.sh,engagement-issues.md,ACCESS.md,project-template.md}.tmpl` | ⭐ |
| L4 | DMP (+ contributed-data intake) → `docs/governance/` | `templates/data-management-plan.md.tmpl`, `templates/responsible-data-checklist.md.tmpl` | ⭐ |
| L4 | QA checklists → `docs/checklists/` | `templates/data-bulletproofing-checklist.md.tmpl`, `templates/data-quality-checklist.md.tmpl` | ⭐ |
| L4 | accessibility → `docs/checklists/` | `templates/accessibility-checklist.md.tmpl` | ⭐ |
| L4 | dataset transparency card → `docs/` | `templates/data-card.md.tmpl` | ⭐ |
| L4 | wiki seeds | `templates/github/wiki-seeds/{Home,_Sidebar}.md.tmpl` | ⭐ |
| L5 | knowledge bundle | `templates/okf/{index,log,concept,dataset,table}.md.tmpl` | ⭐ |
| L5 | licensing / canvases | `templates/LICENSE-NOTE.md.tmpl`, `templates/data-collaborative-canvas.md.tmpl`, `templates/project-design-canvas.md.tmpl` | ⭐ |
| L5 | agent-discovery catalog | `templates/ard/ai-catalog.json.tmpl`, `templates/ard/DISCOVERY.md.tmpl` | ⭐ |
| L5 | repository deposit (DOI) | `templates/dataverse/dataset.json.tmpl`, `templates/dataverse/deposit-dataverse.sh.tmpl`, `templates/dataverse/deposit_dataverse.py.tmpl`, `templates/dataverse/DEPOSIT.md.tmpl` | ⭐ |
| L5 | scheduled versioned re-deposit (periodically-updated data) | `templates/ci/dataverse-deposit.yml.tmpl` | ⭐ |
| L5 | zero-copy sharing | `templates/opensharing/share.json.tmpl`, `templates/opensharing/share-profile.example.json.tmpl`, `templates/opensharing/SHARING.md.tmpl` | ⭐ |

## Sampling guidance

Select the smallest set of practices that serves the chosen level and the profile signals; for everything relevant but above the chosen level (or that the user defers), hand the synthesizer a `ROADMAP.md` entry rather than a file. Always state what you are *not* recommending and why (e.g. "skipping governance scaffolds: single-person, public dataset"). The only place to override leanness is the sensitivity coupling in §B.

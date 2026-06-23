# data-project-skill

An **Agent Skill** that scaffolds accessible, documented, transparent, and inclusive collaborative data projects — right-sized to the team and horizon that actually exist. It interviews you about the project, samples best practices from a curated corpus of frameworks, proposes a plan you approve, and generates only the files the chosen complexity needs — documenting the rest in a `ROADMAP.md` so nothing important is lost and nothing is over-built.

Built by CUPIDS — the CU (University of Colorado) Public Interest Data Science Lab/Clinic. MIT-licensed. Portable across agent harnesses (Claude Code, and other [Agent Skills](https://agentskills.io)–compatible clients).

## What it optimizes

The four goals are **accessible, documented, transparent, and inclusive**, with **collaborative** and **reproducible** as the cross-cutting enablers that make the other four real. The animating worry is *accountability theater* — shipping affordances (identifiers, retention, dashboards, audit logs) without the duties and governance that make them contestable — so the skill keeps affordances and duties coupled, automatically, whenever data is sensitive.

## Lean by default, graded, right-sized

The corpus and templates are a menu, not a default output. Two dials, set in a short interview, keep every run small: the **level** (L0–L5 — how much to build now) and a **now / later / skip** choice for each concern above that level (deferred concerns are written into the project's `ROADMAP.md`, never silently generated). Start low and climb only as far as the task needs.

| Level | Adds | Goals |
| --- | --- | --- |
| **L0 Structure** | repo skeleton, README, AGENTS.md, ignore rules, `data/` tree, ROADMAP | Reproducible |
| **L1 Document** | data dictionary, decision log, changelog | Documented |
| **L2 Reproduce** | pinned environment, pipeline-as-code, config, CI dry-run | Reproducible |
| **L3 Collaborate** | contributing (+ how-we-track-work), code of conduct, CODEOWNERS, and under `docs/governance/`: governance, charter (roles + collaboration protocol); nested skills | Collaborative, Inclusive |
| **L4 Responsible & accessible** | data-management plan, responsible-data/bulletproofing/data-quality/accessibility checklists, data card — grouped under `docs/` | Transparent, Accessible, Inclusive |
| **L5 Publish as open knowledge** | OKF knowledge bundle, ARD agent-discovery catalog, Dataverse deposit (DOI), OpenSharing zero-copy sharing, FAIR/CARE, licensing, publication | Accessible, Transparent |

## How it works

The skill runs a short workflow: **Interview → Sample → Synthesize → Approve → Scaffold (now) + Roadmap (later) → Verify → Offer next rung.** Three bundled agents do the first three phases — `data-project-interviewer` (asks what's needed), `data-project-indexer` (samples the reference corpus), and `data-project-synthesizer` (proposes a right-sized blueprint). In a harness with sub-agents they run as agents; otherwise the skill performs each role inline.

## Getting started

New here? Install the skill for your agent, then point it at a repo — brand-new or existing — and describe the project. The skill interviews you briefly, proposes a right-sized plan, and scaffolds the files once you approve. The sections below cover installation, a first run on a **new** repo, using it on an **existing** repo (scaffold-in, climb, audit, track), and a quick-reference of example prompts for common scenarios.

### 1. Install it

This is plain Markdown that follows the open [Agent Skills](https://agentskills.io) standard (a root `SKILL.md`) and ships an [`AGENTS.md`](https://agents.md) (the cross-tool agent-instructions convention). Any agent that can read files and write to your working directory can use it: point the agent at `SKILL.md` and ask it to start — or audit — a data project. The three agents in `agents/` run as real sub-agents where the harness supports them, and inline everywhere else. Per-harness directions follow; everywhere, first clone it somewhere stable with `git clone https://github.com/cupids-lab/data-project-skill`.

**Claude Code** — install it as a skill and invoke it directly:

```bash
git clone https://github.com/cupids-lab/data-project-skill ~/.claude/skills/data-project
```

Then run `/data-project`, or just describe starting a data project — the description is written to trigger on that. To register the three agents as Claude Code subagents, copy `agents/*.md` into `~/.claude/agents/`; otherwise the skill drives them inline.

**ChatGPT Codex (OpenAI Codex CLI)** — Codex reads `AGENTS.md` for instructions. Either clone this repo into your project root so Codex discovers its `AGENTS.md`, or add a line to your project's `AGENTS.md` (or `~/.codex/AGENTS.md`) pointing Codex at the clone, e.g. *"To start or audit a data project, read and follow `path/to/data-project-skill/SKILL.md`."* The agents run inline.

**Google Gemini CLI** — Gemini loads hierarchical `GEMINI.md` context files. Add a pointer in your `GEMINI.md` (or `~/.gemini/GEMINI.md`): *"For data-project scaffolding, follow `path/to/data-project-skill/SKILL.md`."* You can also wire it to a custom command under `.gemini/commands/`. The agents run inline.

**Mistral (Le Chat / coding agents)** — there is no skills-directory convention, so include `SKILL.md` in the agent's system/context instructions (reference or paste it) and ask it to follow the data-project workflow. The agents run inline.

**Cursor, GitHub Copilot, Windsurf, Cline, and other file-aware agents** — most read an `AGENTS.md` (or a rules file such as `.cursor/rules`). Drop this repo into your workspace so its `AGENTS.md` is discovered, or reference `SKILL.md` from your tool's rules/context mechanism. Because the whole skill is plain Markdown, any agent that can read and write files can follow it.

### 2. Start a project in a brand-new repo

Once it's installed, here is a first run starting from an empty repository.

1. **Create or clone an empty repo and enter it.**

```bash
mkdir my-data-project && cd my-data-project   # or clone an empty repo and cd into it
```

2. **Invoke the skill.** In Claude Code, run `/data-project` — or just describe the work, e.g. *"set up a data project for a CSV of city eviction filings."* The description is written to trigger the skill even when you don't name it. In another harness, tell the agent: *"Follow the data-project SKILL.md and start a project here."*

3. **Answer the short interview.** The skill infers the lowest level that fits and states its assumption (*"this reads like L1 — a documented repo"*). It asks only what changes the output — maturity level, data sensitivity, tooling, openness — with sensible defaults you can accept as-is. For anything beyond the chosen level it asks *build now / document for later / skip*, so the run stays small.

4. **Review and approve the plan.** You get a concise plan: the directory tree, the exact files it will create now, and the roadmap of deferred items. Nothing is written until you approve, so edit freely.

5. **Let it scaffold.** The skill writes files into your working directory (never its own), creates the data directories with `.gitkeep`, marks `data/raw` immutable, and writes a `ROADMAP.md` listing what was deferred and how to add it later. Then review what was created and commit it — stage **explicit paths** rather than `git add -A`, so that in a shared checkout you never sweep another agent's in-progress files into your commit:

```bash
git status                                   # see exactly what was scaffolded
git add README.md AGENTS.md ROADMAP.md .gitignore .gitattributes data/ \
        DATA-DICTIONARY.md decision-log.md CHANGELOG.md
git commit -m "Scaffold data project"
```

6. **Climb when you're ready.** Re-run the skill in the same repo and ask to *"climb to L2"* (add a reproducible pipeline) or *"take this to L3"* (collaboration and governance); it adds only the new level's artifacts and refreshes `ROADMAP.md`. Running it on a repo you *didn't* scaffold — scaffolding in, auditing, or syncing to GitHub — is covered next.

A first run at L0–L1 gives you a small, documented repo — not a pile of governance boilerplate. That leanness is intentional; complexity is opt-in.

### 3. Use it on an existing repo

The skill is just as useful on a repo that already has data and code. It defaults to creating a new `./<project-slug>/`, so when you want it to work **in place**, say so — and it never overwrites an existing file without asking. Run it from inside the repo:

**Scaffold into an existing repo.** Add the missing structure and docs without disturbing your code:

> *"Set up data-project structure in this existing repo — I already have `analysis.py` and a `data/` folder. Work in place and don't move my code."*

It first globs what's already there, plans **only the missing pieces** (e.g. `README`, `DATA-DICTIONARY.md`, `.gitignore`/`.gitattributes`, `ROADMAP.md`), shows you that plan, and writes only after approval — leaving files you already have untouched unless you ask it to change them.

**Climb a level.** Re-run it in any project — one it scaffolded or not — and ask for the next rung:

> *"Take this project to L2: add a pinned environment and a pipeline that re-runs on new data."*
>
> *"We're onboarding two partner orgs and the data is sensitive — add L3 governance."*

It adds only that level's artifacts and refreshes `ROADMAP.md`. Sensitive data automatically couples every identifier/retention/audit affordance with access tiers and contestable governance, regardless of level.

**Audit an existing repo (read-only).** Get a prioritized gap report before changing anything:

```bash
/data-project audit .
```

> *"Audit this repo against open, reproducible, and inclusive data standards and tell me what's missing."*

It scores the repo across L0–L5 and the six goals, prints a gap table (*Goal/Level → Found? → Recommended template → Source*), checks OKF-bundle conformance if a `knowledge/` bundle exists, and **makes no changes** until you approve remediation.

**Track the roadmap on GitHub.** Turn the assignable checklist into issues and a project board — idempotently, so re-running after edits updates items instead of duplicating them:

```bash
/data-project track
```

> *"Turn my ROADMAP into GitHub issues and put them on a board."*

### 4. More example prompts

Each of these triggers the skill (you don't have to name it), and each still lands at a right-sized level you approve before anything is written.

| Say something like… | The skill… |
| --- | --- |
| *"Get me a clean repo for this eviction-filings CSV."* | L0/L1 — structure + data dictionary; no pipeline or governance |
| *"Make this reproducible in **R** with `targets`."* | L2 on the R stack (`DESCRIPTION`, `_targets.R`, `renv`, `Makefile`) instead of the Python default |
| *"Set up a reproducible **Python** project with a Snakemake pipeline."* | L2 on the Python stack (`environment.yml`, `Snakefile`, `config.yaml`, CI dry-run) |
| *"Multi-partner project with sensitive tenant records across three nonprofits."* | L3+ with the affordance↔duty coupling — `GOVERNANCE` (access tiers, retention, remedy), `CHARTER`, roles, contributed-data intake |
| *"We're publishing this dataset as open knowledge / FAIR."* | L5 — OKF `knowledge/` bundle from the data dictionary, layered licensing, Data Card |
| *"Publish it so other agents can discover and use it."* / *"set up agent discovery."* | L5 — an ARD `ai-catalog.json` + `DISCOVERY.md` advertising the project's skills/dataset (host `.well-known/` + registry deployment deferred to `ROADMAP.md`) |
| *"Audit `<path>` and tell me what's missing."* | Audit mode — read-only gap report across L0–L5 |
| *"Turn my roadmap into issues / update the board."* | Track mode — idempotent sync to GitHub Issues / Project / Wiki |
| *"Deposit the data, code, and docs to Harvard Dataverse and get a DOI."* | Deposit mode — citation metadata + upload as Data/Code/Documentation; draft → confirm → publish (DOI) |
| *"Share the data and our agent skills with a partner org without copying."* | L5 — an OpenSharing `share.json` + `SHARING.md`: zero-copy Share→Schema→Asset with scoped credentials, gated by `GOVERNANCE.md` |

## What it draws on

The corpus distills the following frameworks into concise, citable digests under `references/`, sampled by the indexer via `references/INDEX.md`:

[The Turing Way](https://book.the-turing-way.org/) · [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) · [Snakemake](https://snakemake.readthedocs.io/) · [OUHSC BBMC Data-Science Practices](https://ouhscbbmc.github.io/data-science-practices-1/) · [Git & GitHub for data science](https://arounddatascience.com/blog/coding/how-to-use-github-and-git-for-collaborative-data-science-projects-a-complete-guide-for-algerian-data-scientists/) & [GitHub Projects best practices](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects) · [Data Collaboratives Canvas](https://datacollaboratives.org/canvas.html) · [USDS Playbook](https://playbook.usds.gov/) · [Responsible Data Handbook](https://responsibledata.io/resources/handbook/) · ProPublica [Collaborative](https://propublica.gitbook.io/collaborative), [Collaborate](https://propublica.gitbook.io/collaborate-user-manual) & [Bulletproofing](https://github.com/propublica/guides/blob/master/data-bulletproofing.md) · [Quartz Bad Data Guide](https://github.com/Quartz/bad-data-guide) · [Google Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) · [Data Cards Playbook (Google PAIR)](https://sites.research.google/datacardsplaybook/) · [Agentic Resource Discovery (ARD)](https://agenticresourcediscovery.org/spec/) · [Dataverse Native API](https://guides.dataverse.org/en/latest/api/) · [pyDataverse](https://github.com/gdcc/pyDataverse) · [OpenSharing](https://github.com/OpenSharing-IO/OpenSharing) · [AgentSkills](https://agentskills.io/specification).

## Relationship to `data-liberation`

This is the companion to the lab's [`data-liberation`](https://github.com/cupids-lab/data-liberation-skill) skill. `data-liberation` gets data *out and tidy* (government PDFs, FOIA, scraped HTML → tidy, documented datasets); `data-project` architects the *collaboration, governance, and knowledge layer around* that data. They share a knowledge layer — `data-liberation`'s concept catalogs and the OKF bundle this skill emits at L5 are the same idea — so the two compose.

## Build status

All six levels (L0–L5) are built: structure and documentation; the Python and R reproducible stacks plus CI (single-project, and an auto-discovered multi-pipeline monorepo matrix); collaboration and governance (contributing — also carrying how-we-track-work — code of conduct, CODEOWNERS, and a grouped `docs/governance/` tree holding governance with its values spine and the charter with roles + the collaboration protocol, plus nested `.skills/`); the responsible-data, data-management (with contributed-data intake), bulletproofing, data-quality, and accessibility artifacts and a Data Card — the governance set and checklists organized under `docs/`; and the L5 licensing, canvases, OKF knowledge bundle, the ARD agent-discovery catalog, the Harvard Dataverse deposit kit, and the OpenSharing zero-copy share kit. `references/INDEX.md` tracks each template's status. Having the full menu doesn't change the lean-by-default behavior: the interview still right-sizes every run and defers anything above the chosen level into the project's `ROADMAP.md`.

## License

MIT — see `LICENSE`.

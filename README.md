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
| **L3 Collaborate** | contributing, code of conduct, roles, governance, charter, nested skills | Collaborative, Inclusive |
| **L4 Responsible & accessible** | data-management plan, responsible-data & data-quality checklists, accessibility | Transparent, Accessible, Inclusive |
| **L5 Publish as open knowledge** | OKF knowledge bundle, FAIR/CARE, licensing, publication | Accessible, Transparent |

## How it works

The skill runs a short workflow: **Interview → Sample → Synthesize → Approve → Scaffold (now) + Roadmap (later) → Verify → Offer next rung.** Three bundled agents do the first three phases — `data-project-interviewer` (asks what's needed), `data-project-indexer` (samples the reference corpus), and `data-project-synthesizer` (proposes a right-sized blueprint). In a harness with sub-agents they run as agents; otherwise the skill performs each role inline.

## Install

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

## What it draws on

The corpus distills the following frameworks into concise, citable digests under `references/`, sampled by the indexer via `references/INDEX.md`:

[The Turing Way](https://book.the-turing-way.org/) · [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) · [Snakemake](https://snakemake.readthedocs.io/) · [OUHSC BBMC Data-Science Practices](https://ouhscbbmc.github.io/data-science-practices-1/) · [Git/GitHub for collaborative data science](https://arounddatascience.com/blog/coding/how-to-use-github-and-git-for-collaborative-data-science-projects-a-complete-guide-for-algerian-data-scientists/) · [Data Collaboratives Canvas](https://datacollaboratives.org/canvas.html) · [USDS Playbook](https://playbook.usds.gov/) · [Responsible Data Handbook](https://responsibledata.io/resources/handbook/) · [ProPublica — Bulletproofing your data analysis](https://github.com/propublica/guides/blob/master/data-bulletproofing.md) · [ProPublica Collaborative](https://propublica.gitbook.io/collaborative) · [ProPublica Collaborate](https://propublica.gitbook.io/collaborate-user-manual) · [Quartz Bad Data Guide](https://github.com/Quartz/bad-data-guide) · [Google Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf).

## Relationship to `data-liberation`

This is the companion to the lab's [`data-liberation`](https://github.com/cupids-lab/data-liberation-skill) skill. `data-liberation` gets data *out and tidy* (government PDFs, FOIA, scraped HTML → tidy, documented datasets); `data-project` architects the *collaboration, governance, and knowledge layer around* that data. They share a knowledge layer — `data-liberation`'s concept catalogs and the OKF bundle this skill emits at L5 are the same idea — so the two compose.

## Build status

This is an MVP. **L0–L2** (structure, documentation, the Python reproducible stack) plus the full interview/sample/synthesize/audit workflow are built. **L3–L5** templates (governance, roles, charter, nested skills, responsible-data and data-quality checklists, accessibility, the R variant, CI, and the OKF bundle) are on the roadmap: `references/INDEX.md` marks each template ⭐ built or ○ roadmap, and the skill routes ○ concerns into each project's `ROADMAP.md` until they land.

## License

MIT — see `LICENSE`.

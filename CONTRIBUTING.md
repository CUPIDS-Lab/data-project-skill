# Contributing to the data-project skill

Thanks for improving this skill. It is a portable Agent Skill — plain Markdown plus a few templates — so contributing is mostly writing clear prose and keeping the corpus and templates consistent. Read `SKILL.md` for the workflow and `references/context.md` for the values before making substantive changes.

## Conventions

Prose follows **one paragraph per line** (no hard-wrapping; lists, tables, and code keep their normal structure). Write in the imperative and explain *why* rather than stacking "MUST"s. Keep the lean-by-default ethos: the skill should build only what a project's level needs and defer the rest into `ROADMAP.md`, so prefer adding a roadmap-able artifact over making any single run heavier.

## Adding a reference digest

Add `references/<name>.md` with YAML frontmatter carrying a non-empty `type:` (so the corpus stays an OKF-conformant bundle) and follow the existing digest schema: a one-paragraph intro, goal-tagged **Key practices**, the **Artifacts it implies** (mapped to a template), **When most relevant**, and **Caveats / conflicts**. Then wire it into `references/INDEX.md` — at least one §A goal row and, where it applies, a §B profile-signal row — otherwise the indexer can never sample it.

## Adding a template

Add `templates/<name>.md.tmpl`, using only the placeholder tokens and `<!-- IF:FLAG -->` conditionals documented in `SKILL.md` ("Placeholders & conditionals"). Add a row to `references/INDEX.md` §C mapping it to a level, and list it in `templates/directory-tree.md` if it changes the project layout. Keep intra-project links pointed at files the scaffold actually creates at that level, or hedge them toward `ROADMAP.md`.

## Before you open a PR

Run `python scripts/validate.py` — it checks reference frontmatter, template conditional/token consistency, and that every template cited in the INDEX exists. The `validate` GitHub Actions workflow runs the same check on every pull request. For behavioral changes, walk one or two prompts from `evals/evals.json` through the skill and confirm the scaffold is right-sized and placeholder-free.

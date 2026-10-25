# Plan — fold `data-liberation-template` into `data-liberation-skill` (one repo)

**Goal:** eliminate the separate `data-liberation-template` repo and the two-repo
version-lock dance; ship the project template *inside this repo*, the way
[`CUPIDS-Lab/data-project-skill`](https://github.com/CUPIDS-Lab/data-project-skill) ships its
`templates/` directory.
**Secondary ask:** decide *whether and how* to mirror data-project-skill's templating
design — adopt what fits, adapt what half-fits, and consciously skip what doesn't.
**Baseline:** skill `v0.4.0`; template currently at `brianckeegan/data-liberation-template`,
fetched by `scripts/scaffold.py` (SHA-pinned tarball), version-locked via `RELEASING.md` +
`dispatch-to-template.yml` + `scaffold-e2e.yml` on both repos.
**Status:** **executed** on PR #27. Per maintainer decision the build went **agent-driven**
(overriding §6.1's recommendation to keep `scaffold.py`) and adopted **cross-skill symmetry**
with data-project (§6.3): `{{UPPER_SNAKE}}` tokens, `.tmpl` files, `scripts/validate.py`, and a
single `validate.yml`. The "scaffold actually runs" guarantee is preserved by `validate.py --smoke`
rendering `templates/project/` and running `uv sync` + ruff + pytest on the result. See
`CHANGELOG.md`. The phases below are the plan as proposed; the executed shape differs only at §6.1/§6.3.

> **Relationship to PR #27** (`retro/data-liberation-skill-revision-plan.md`): that plan's
> Phases 3–4 are framed as *joint skill+template version bumps*. Folding the template in
> **deletes that whole class of release** — after this, every change is a single-repo skill
> release. This plan should land **before or alongside** PR #27's Phase 3, because it removes
> the coordination tax those phases were budgeted for.

---

## 1. How `data-project-skill` does it (the reference architecture)

Read from the live repo, so the comparison is concrete, not assumed:

| Aspect | `data-project-skill` |
|---|---|
| **Where templates live** | `templates/` at repo root, a **sibling of `SKILL.md`** and `references/`. No separate repo, no fetch, no SHA pin. |
| **Template organization** | by concern: `templates/python/`, `r/`, `ci/`, `github/`, `okf/`, `ard/`, `nested-skills/`, plus top-level document templates (`README.md.tmpl`, `AGENTS.md.tmpl`, `CHARTER.md.tmpl`, `GOVERNANCE.md.tmpl`, …) and a `directory-tree.md` skeleton. |
| **Template format** | `*.tmpl` files; `{{UPPER_SNAKE}}` tokens; `<!-- IF:FLAG -->…<!-- /IF -->` conditional blocks. |
| **Who renders** | the **agent**, following a 7-step `SKILL.md` workflow (Resolve → Interview → Sample → Synthesize → Approve → Scaffold → Verify). There is **no scaffold program.** |
| **Selection logic** | three-phase: **level** (L0–L5) sets baseline scope; a **Profile** from an interview + `references/INDEX.md` crosswalk (goal/level/signal → practice → template) picks practices; **flags** (`SENSITIVE`, `PIPELINE`, `COLLAB`, `OKF`, `ARD`, `GH`) strip/keep conditional blocks. Anything above the level → deferred to `ROADMAP.md`. |
| **`scripts/`** | just **`validate.py`** — a *static* self-consistency lint: balanced conditionals, every flag/token in `DOCUMENTED_FLAGS`/`DOCUMENTED_TOKENS`, every `INDEX.md` template path resolves, JSON templates parse under all-flags-on **and** all-flags-off, references carry OKF `type:` frontmatter. |
| **CI** | one workflow, `validate.yml` (runs `validate.py`). No cross-repo dispatch. |
| **Verification of output** | "no unfilled `{{ }}` remain (`grep -Rn "{{" <project>/`)." **It never executes a rendered project.** |

## 2. The decisive difference — and what it implies

data-project's templates are **mostly inert documents** (governance, checklists, canvases) plus
a handful of config files (`pyproject.toml.tmpl`, `Snakefile.tmpl`, `environment.yml.tmpl`,
`pre-commit-config.yaml.tmpl`). They template cleanly as fragments, and a *static* lint ("does it
render without leftover tokens / is the JSON still valid") is sufficient.

**data-liberation's template is a runnable Python application** — `schema.py`, `sources.py`,
`fetch.py`, `clean.py`, `audit.py`, `reconcile.py`, `publish.py`, `pipeline.py`, `parsers/`, and a
real `tests/` suite with fixtures. Its current, load-bearing guarantee is *"the scaffolded project
actually runs: `uv sync && ruff && pytest` passes and the CLI works"* — enforced today by
`scaffold-e2e.yml` rendering the template and executing it. data-project's static lint provides
nothing equivalent because data-project never needs it.

**Implication:** mirror data-project's **repo architecture** (in-repo `templates/`, single repo,
single CI, no fetch/SHA/dispatch), but **do not** mirror the parts that assume inert templates —
keep the executable template as *real, runnable files* and keep a deterministic renderer + a CI job
that *runs the rendered project's tests*. A literal mirror would trade away the one guarantee that
matters most for an executable scaffold.

### Mirror / adapt / skip

| data-project choice | Verdict | data-liberation approach |
|---|---|---|
| Templates in-repo, sibling of `SKILL.md` | **Mirror** | move template to `templates/project/` in this repo |
| Separate template repo + fetch + SHA pin + two-repo `RELEASING` dance | **Drop** | the entire point — delete |
| Single CI workflow | **Mirror (adapt)** | one workflow, but it *renders + runs the scaffolded tests* (stronger than a static lint) |
| `scripts/validate.py` static lint | **Adopt (additive)** | add a small `validate.py` for token/skeleton/slot-fill lint, **on top of** the render-and-test job |
| Agent-driven scaffolding, **no** scaffold program | **Don't mirror** | keep `scaffold.py`, but read the template **locally** — executable code needs deterministic `str.replace` rendering + reproducibility, not per-file agent substitution across ~30 modules |
| `*.tmpl` suffix + inert fragments | **Partial** | keep Python/tests/configs as **real runnable files** (so they lint/test in place); suffix only is unnecessary given `scaffold.py` already substitutes by content |
| `{{UPPER_SNAKE}}` tokens | **Optional** | keep `{{ lower_snake }}` + the documented slot-fill table unless cross-skill token alignment is itself a goal (see §6.3) |
| `<!-- IF:FLAG -->` conditionals + `INDEX.md` + Profile interview | **Optional / later** | heavier; synergizes with the already-planned `scaffold.py --level` work — defer to an optional rung (§5 Phase E) |
| Level-keyed selection (L0–L5) | **Converge** | both skills *already* have L0–L5; wire `--level` to template subsetting (this repo's `RELEASING.md` already plans it) |

## 3. Target architecture (single repo)

```
data-liberation-skill/
├── SKILL.md
├── references/                      <- unchanged (ten + the planned extract-api.md)
├── scripts/
│   ├── scaffold.py                  <- SIMPLIFIED: renders from ../templates/project (no network)
│   └── validate.py                  <- NEW: static lint (slot-fills documented, skeleton present)
├── templates/
│   └── project/                     <- the FORMER data-liberation-template repo, verbatim-ish
│       ├── data/{original,processed,audit,lookups}/.gitkeep
│       ├── scripts/{schema,sources,config,concepts,fetch,discover,clean,audit,reconcile,publish,pipeline}.py + parsers/
│       ├── tests/{conftest,test_schema,…}.py + fixtures/
│       ├── docs/*.qmd
│       ├── github-workflows/        <- RENAMED from .github/workflows (see §4 Phase A note)
│       ├── AGENTS.md  README.md  pyproject.toml  _quarto.yml  gitignore  gitattributes
│       └── (TEMPLATE.md content folded into references/project-template.md, not shipped)
├── README.md  LICENSE  CHANGELOG.md (new)  RELEASING.md (gutted → single-repo)
└── .github/workflows/scaffold-e2e.yml   <- SIMPLIFIED single-repo render-and-test; dispatch-to-template.yml DELETED
```

Key choices, each justified in §6:
- Templates at `templates/project/` (mirrors data-project's `templates/`; `project/` namespaces the
  single runnable template and leaves room for a future `templates/notebook/` per PR #27 WS-I).
- `scaffold.py` stays but reads `Path(__file__).resolve().parent.parent / "templates" / "project"`.
- The shipped template's CI lives under `templates/project/github-workflows/` and is **rendered to
  `.github/workflows/`** at scaffold time, so it never executes inside the skill repo.

## 4. File-level workplan

### Phase A — bring the template in-repo *(mechanical move)*
1. Copy the `brianckeegan/data-liberation-template` tree (at the pinned SHA
   `72b202020c12056f19c828bff0b619cda5aadf64`) into `templates/project/`.
2. **Rename `.github/` → `github-workflows/`** inside the template (or `templates/project/_github/`).
   *Reason:* a nested `.github/workflows/*.yml` won't run as the skill repo's own CI (GitHub only
   activates root `.github/workflows/`), but renaming removes all ambiguity and matches data-project's
   `templates/ci/` + `templates/github/` precedent. `scaffold.py` maps it back to `.github/workflows/`
   on render.
3. Drop the template's self-describing `TEMPLATE.md` from the shipped tree; migrate its content into
   `references/project-template.md` (which already documents every file).
4. Keep the template's own `tests.yml` / `refresh.yml.disabled` / `publish.yml.disabled` /
   `gh-pages.yml.disabled` — they become part of the rendered output exactly as before.
- **Acceptance:** `templates/project/` contains the full runnable skeleton; no `.yml` under a path
  GitHub would auto-run; `references/project-template.md` absorbs `TEMPLATE.md`.

### Phase B — rewire `scaffold.py` to read locally *(net deletion)*
Remove the network/versioning machinery; keep the renderer:
- **Delete:** `DEFAULT_TEMPLATE_REPO`, `DEFAULT_TEMPLATE_VERSION`, `DEFAULT_TEMPLATE_TAG`,
  `fetch_template`, `_git_clone`, `_parse_github_repo`, `_GITHUB_URL_RE`, the tarball/`urllib`/`tarfile`
  imports, and the `--template-repo` / `--template-version` CLI flags.
- **Replace** `fetch_template(...)` with a one-liner resolving the bundled dir
  (`TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates" / "project"`), validated to exist.
- **Add** the `github-workflows/ → .github/workflows/` path remap in `walk_and_write` (or a rename pass).
- **Keep** `walk_and_write`, `substitute`, `build_placeholders`, `derive_slug`, `is_text_file`, and the
  `--dest/--name/--description/--author/--owner/--consumers/--dry-run` CLI unchanged.
- **Net effect:** `scaffold.py` gets ~40% shorter and gains zero network dependencies.
- **Acceptance:** `python scripts/scaffold.py --dest /tmp/t --name t --description d --owner o` renders
  offline; `grep -rE '\{\{ *[a-z_]+ *\}\}' /tmp/t` is empty; `cd /tmp/t && uv sync && uv run pytest`
  passes; `--dry-run` works; no import of `urllib`/`tarfile`/`subprocess`-for-clone remains.

### Phase C — collapse CI + release process *(delete the two-repo machinery)*
- **Delete** `.github/workflows/dispatch-to-template.yml` (no second repo to notify).
- **Simplify** `.github/workflows/scaffold-e2e.yml`: drop the `repository_dispatch: template-updated`
  trigger, the `template_ref` input, and the `--template-version` plumbing. It now: render the bundled
  template → assert no stray `{{ }}` → `uv sync --extra publish` → `ruff check/format --check` →
  `pytest -q` → `pipeline --help` / `publish --help`. This is data-liberation's analog of
  data-project's `validate.yml`, **but stronger** (it executes the scaffold). Optionally rename to
  `validate.yml` for cross-skill symmetry.
- **Gut `RELEASING.md`:** remove the template-repo tag dance, SHA-pinning section, cross-repo
  `repository_dispatch` token setup, and the "CI workflows across two repos" table. Replace with a
  short single-repo release note (bump skill version; update `CHANGELOG.md`; tag). **Keep** the
  "Planned follow-ups: `scaffold.py --level`" item but reframed single-repo.
- **Add `CHANGELOG.md`** (data-project has one; single-repo releases want a human changelog now that
  the SHA pin no longer encodes "what gets scaffolded").
- **Acceptance:** one scaffold/validate workflow, green; `dispatch-to-template.yml` gone; `RELEASING.md`
  describes a single-repo release with no SHA pin; `CHANGELOG.md` exists.

### Phase D — docs & progressive-disclosure *(the context-budget answer)*
Folding the template in **re-introduces the concern the two-repo split originally solved** — README
line 51 and SKILL.md line 234 keep the template out so *"an agent doesn't burn context on files it
shouldn't read directly."* Answer it the way data-project does: scope template reads to scaffold time.
- **`SKILL.md`:** rewrite "The template repo" section (≈ lines 232–234) → "The bundled template
  (`templates/project/`)"; update the Scaffold-phase instructions (≈ lines 122–138, 193) to render the
  local template; **add a guardrail:** *"Do not read `templates/` unless you are scaffolding (L2+);
  it is rendered, not reference material."* (mirrors data-project's "read templates from here; write
  only to the user's working dir").
- **`references/project-template.md`:** change the opening ("The working version lives in a separate
  repo … fetched by `scripts/scaffold.py`") → bundled at `templates/project/`; absorb `TEMPLATE.md`.
- **`README.md`:** update the repo-contents tree (add `templates/`), the "separate repo, pinned to a
  commit SHA" paragraph, and the toolchain bullet that says the template is "fetched on demand."
- **Acceptance:** no doc claims a separate template repo or SHA pin; SKILL.md carries the "don't read
  `templates/` unless scaffolding" guardrail; README tree shows `templates/project/`.

### Phase E — *optional* deeper mirror of data-project *(only if desired; see §6)*
Each item is independently shippable and **not required** to achieve the single-repo goal:
- **`scripts/validate.py`** (static lint, additive to scaffold-e2e): every `{{ slot }}` used in
  `templates/` appears in the `project-template.md` slot-fill table and in `build_placeholders`; the
  skeleton in `project-template.md` matches the files on disk; `pyproject.toml.tmpl`-style configs parse.
- **`--level` selection** wired to template subsetting (already planned in `RELEASING.md`), now a pure
  single-repo render-walk allowlist — no template bump.
- **`<!-- IF:FLAG -->` conditionals + a `references/INDEX.md` crosswalk** for optional surfaces
  (publish / gh-pages / reconcile / concepts) instead of today's ship-disabled-then-rename. Heavier;
  adopt only if the flag UX is wanted.
- **Token-syntax alignment** (`{{ lower_snake }}` → `{{UPPER_SNAKE}}`) for cross-skill symmetry — churn
  with no functional gain unless symmetry is a stated goal.

## 5. Sequencing

```
Phase A  move template into templates/project/        mechanical, low-risk
Phase B  scaffold.py reads locally (delete fetch)     depends on A
Phase C  delete dispatch, simplify CI, gut RELEASING  depends on B (CI renders locally)
Phase D  docs + progressive-disclosure guardrail      depends on A–C landing
Phase E  optional deeper mirror (validate/IF/INDEX)   independent, later
```
A–D are one cohesive PR (or A–B then C–D); E is opt-in follow-ups.

## 6. Decision points (recommendations)

### 6.1 Keep `scaffold.py`, or go fully agent-driven like data-project?
**Recommend keep `scaffold.py` (local-reading).** data-project can be agent-driven because its
templates are documents; data-liberation's template is ~30 executable modules + a test suite, where a
deterministic `str.replace` render is safer and reproducible, and where CI must actually run the
output. Going agent-driven would forfeit reproducibility and the render-and-test guarantee. *(Pure-mirror
alternative: delete `scaffold.py`, describe rendering in SKILL.md, rely on `validate.py` + the agent —
viable but a real downgrade for executable scaffolds.)*

### 6.2 `.tmpl` suffixes + inert fragments, or real runnable files?
**Recommend real runnable files.** `scaffold.py` substitutes by *content*, so suffixes buy nothing,
and keeping the template a real project is what lets `scaffold-e2e` lint+test it in place. (data-project
needs `.tmpl` because its agent-render has no other way to mark "this is a template.")

### 6.3 Token syntax — keep `{{ lower_snake }}` or adopt `{{UPPER_SNAKE}}`?
**Recommend keep `{{ lower_snake }}`** (already documented in the slot-fill table; `scaffold-e2e`
already greps for it) unless cross-skill alignment with data-project is an explicit goal — then do it
in Phase E as a mechanical rename + table update.

### 6.4 Where do templates live — `templates/` or `assets/`?
**Recommend `templates/project/`** to mirror data-project. (`assets/` is the AgentSkills spec's named
optional dir and is equally valid; `templates/` wins on sibling-skill symmetry.)

### 6.5 How much data-project machinery (Profile interview / IF-flags / INDEX crosswalk) to adopt?
**Recommend defer to Phase E / fold into the planned `--level` work.** The single-repo goal needs none
of it. Adopt the level-keyed selection (cheap, both skills already have levels); treat the
interview/flag/INDEX system as an optional later convergence.

## 7. Cutover, migration, and risks

- **The old `brianckeegan/data-liberation-template` repo:** archive it (read-only) with a README note
  pointing here; do **not** delete (existing clones / citations). Add a tombstone commit. The
  CUPIDS-Lab fork, if any, same treatment.
- **Existing pinned consumers:** the SHA pin disappears; "skill `vX` scaffolds template `vX`" becomes
  "skill `vX` *contains* its template," which is strictly simpler. Note it in `CHANGELOG.md`.
- **Context budget (the real risk):** the template's ~40 files now live in the skill repo. Mitigation
  is behavioral, not structural — the SKILL.md guardrail (§Phase D) scopes template reads to scaffold
  time, exactly as data-project does. Net context cost is paid only at L2+ scaffolding, which is when
  those files are needed anyway.
- **Provenance of reproducibility:** today the SHA pin makes scaffold output byte-reproducible. After
  folding in, reproducibility comes from the template being *in the same commit* as the skill — equal
  or better (no cross-repo drift window). Call this out so the change reads as a *strengthening*.
- **Don't regress the runnable guarantee:** the single CI job must still `uv sync && ruff && pytest`
  the rendered project. If Phase E later introduces IF-flags, render-and-test must cover both
  flags-on and flags-off (data-project's `validate.py` already models the all-on/all-off discipline —
  borrow it).

## 8. Acceptance criteria (rollup)
- [ ] `templates/project/` holds the full runnable template; no auto-running nested `.github/workflows`.
- [ ] `scaffold.py` renders offline from the bundled dir; no network/SHA/tag/`--template-*` code remains.
- [ ] Rendered project passes `uv sync && ruff && uv run pytest` in CI via one workflow.
- [ ] `dispatch-to-template.yml` deleted; `RELEASING.md` describes a single-repo release; `CHANGELOG.md` added.
- [ ] `SKILL.md`, `references/project-template.md`, `README.md` no longer reference a separate template
      repo or SHA pin, and SKILL.md carries the "don't read `templates/` unless scaffolding" guardrail.
- [ ] Old template repo archived with a pointer here.
- [ ] (If Phase E) `validate.py` + `validate.yml` lint the template system; `--level` subsets the render.
```

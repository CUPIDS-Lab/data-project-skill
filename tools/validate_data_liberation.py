#!/usr/bin/env python3
"""Validate the bundled project template — and prove it renders to a working project.

`data-liberation` scaffolds **agent-driven**: the agent reads the templates under
`templates/project/`, keeps the files of the file groups in scope, substitutes
`{{UPPER_SNAKE}}` tokens, strips `<!-- IF:FLAG -->…<!-- /IF -->` blocks whose flag
is off, and writes the result into the user's working directory (see SKILL.md and
`references/project-template.md`). There is no scaffold CLI.

The file groups (`core`, `publish`, `multi-source`, `refresh`) and their flags are
defined once, in the "File groups" table of `references/project-template.md`
(between `<!-- BEGIN file-groups -->` and `<!-- END file-groups -->`). This
validator reads that table, so the documentation and the check cannot drift. The
slot-fill table in the same reference must list exactly `DOCUMENTED_TOKENS`.

Because the template is a *runnable Python application* (not inert documents), this
validator renders it twice and checks both:

  1. **Static lint** — no stray lower-case `{{ token }}`, every `{{UPPER}}` token
     and `IF` flag is documented, `IF` blocks balance, `.tmpl` suffixes agree with
     tokens, every template file belongs to exactly one group, and no template
     points at a retired reference or uses the retired level ladder.
  2. **Render** — a *minimal* project (`core` only, no flags) and a *full* one
     (every group, every flag) into a temp dir with test values; no residual
     tokens or `IF` markers; every rendered `.py` compiles.
  3. **Smoke test** (`--smoke`, run in CI) — on the full render: `uv sync`, `ruff
     check`, `ruff format --check`, `pytest`, `python -m scripts.pipeline --help`
     and `run --help`; on the minimal render: `uv sync`, `pytest` and `--help`
     (which must not offer the optional `discover`/`publish` commands). Needs
     network (uv fetches dependencies); skipped by default.

Usage
-----
    python tools/validate_data_liberation.py            # lint + both renders + compile
    python tools/validate_data_liberation.py --smoke    # also uv sync + ruff + pytest (CI)
    python tools/validate_data_liberation.py --keep     # don't delete the rendered temp dir
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills" / "data-liberation"
TEMPLATE_ROOT = SKILL_ROOT / "templates" / "project"
REFERENCES = SKILL_ROOT / "references"
PROJECT_TEMPLATE_MD = REFERENCES / "project-template.md"

# The slot-fills the agent must provide. Kept in lockstep with the "Slot-fills"
# table in references/project-template.md (checked below).
DOCUMENTED_TOKENS = {
    "PROJECT_NAME",
    "PROJECT_SLUG",
    "PKG_NAME",
    "DESCRIPTION",
    "AUTHOR",
    "OWNER",
    "CONSUMER_STACK",
}

# Test values for the render pass. PKG_NAME must be a valid Python identifier;
# PROJECT_NAME has several words so a BibTeX `{{…}}` can't look like a token.
RENDER_VALUES = {
    "PROJECT_NAME": "Validation Render Project",
    "PROJECT_SLUG": "validation-render-project",
    "PKG_NAME": "validation_render_project",
    "DESCRIPTION": "End-to-end validation render",
    "AUTHOR": "CI <ci@example.org>",
    "OWNER": "ci-bot",
    "CONSUMER_STACK": "pandas",
}

# Files every project starts with (the Outline's five working files and the pipeline
# core); the `core` group must contain them.
REQUIRED_CORE = {
    "README.md.tmpl",
    "AGENTS.md.tmpl",
    "CLAUDE.md",
    "ROADMAP.md.tmpl",
    "decision-log.md.tmpl",
    "CHANGELOG.md.tmpl",
    "pyproject.toml.tmpl",
    "scripts/pipeline.py.tmpl",
    "scripts/source.py",
    "scripts/clean.py",
    "scripts/schema.py.tmpl",
    "tests/test_schema.py",
    ".github/workflows/tests.yml",
}

# Pointers that must never come back: reference files retired in 0.4.0, the
# superseded context.md, and the L0–L5 ladder the Outline replaced.
RETIRED_RE = re.compile(
    r"toolchain-[a-z]+\.md|discovery-and-audit|movement-history|cleaning-and-standardization"
    r"|references/context\.md|\bL[0-5]\b|\b[Ll]evel [0-5]\b"
)
SKILL_URL_RE = re.compile(
    r"github\.com/CUPIDS-Lab/data-skills/(?:tree|blob)/main/skills/data-liberation/references/([\w./-]+\.md)"
)

# `(?<!\$)` excludes GitHub Actions `${{ … }}` expressions, which are not our tokens.
ANY_TOKEN_RE = re.compile(r"(?<!\$)\{\{ *([A-Za-z_]+) *\}\}")
IF_BLOCK_RE = re.compile(r"<!-- IF:(\w+) -->\n?(.*?)<!-- /IF -->\n?", re.DOTALL)
IF_OPEN_RE = re.compile(r"<!-- IF:(\w+) -->")
IF_CLOSE_RE = re.compile(r"<!-- /IF -->")


def _iter_files():
    for p in sorted(TEMPLATE_ROOT.rglob("*")):
        if p.is_file():
            yield p


def _rel(p: Path) -> str:
    return p.relative_to(TEMPLATE_ROOT).as_posix()


def _read(p: Path) -> str | None:
    try:
        return p.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return None


# ── 0. The groups and tokens, as documented ──────────────────────────────────


def documented_groups() -> tuple[dict[str, dict], list[str]]:
    """Parse the File groups table: {group: {"flag": str|None, "files": [patterns]}}."""
    errors: list[str] = []
    text = PROJECT_TEMPLATE_MD.read_text(encoding="utf-8")
    m = re.search(r"<!-- BEGIN file-groups -->\n(.*?)<!-- END file-groups -->", text, re.S)
    if not m:
        return {}, [f"{PROJECT_TEMPLATE_MD.name}: no <!-- BEGIN file-groups --> table"]
    groups: dict[str, dict] = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0].startswith("`"):
            continue
        name = cells[0].strip("`")
        flag = cells[1].strip("`") if cells[1] not in ("", "—", "-") else None
        files = re.findall(r"`([^`]+)`", cells[3])
        groups[name] = {"flag": flag, "files": files}
    if "core" not in groups:
        errors.append("file-groups table has no `core` row")
    return groups, errors


def documented_tokens() -> set[str]:
    text = PROJECT_TEMPLATE_MD.read_text(encoding="utf-8")
    m = re.search(r"\| Token \|.*?\n\n", text, re.S)
    return set(re.findall(r"\{\{([A-Z_]+)\}\}", m.group(0))) if m else set()


def assign_groups(groups: dict[str, dict]) -> tuple[dict[str, str], list[str]]:
    """Map every template file to its group; core is everything not listed elsewhere."""
    errors: list[str] = []
    owner: dict[str, str] = {}
    files = [_rel(p) for p in _iter_files()]
    for name, g in groups.items():
        if name == "core":
            continue
        for pat in g["files"]:
            hits = [f for f in files if fnmatch.fnmatch(f, pat)]
            if not hits:
                errors.append(f"file group `{name}` lists `{pat}`, which matches no template file")
            for f in hits:
                if f in owner and owner[f] != name:
                    errors.append(f"{f}: in two file groups ({owner[f]}, {name})")
                owner[f] = name
    for f in files:
        owner.setdefault(f, "core")
    for f in sorted(REQUIRED_CORE):
        if owner.get(f) != "core":
            errors.append(f"{f}: must be in the `core` group (found {owner.get(f, 'missing')})")
    return owner, errors


# ── 1. Static lint ────────────────────────────────────────────────────────────


def lint(flags: set[str]) -> list[str]:
    errors: list[str] = []
    for p in _iter_files():
        text = _read(p)
        if text is None:
            continue
        rel = _rel(p)

        for m in ANY_TOKEN_RE.finditer(text):
            tok = m.group(1)
            if tok.islower():
                errors.append(f"{rel}: stray un-migrated token {{{{ {tok} }}}} (use UPPER_SNAKE)")
            elif tok.isupper() and tok not in DOCUMENTED_TOKENS:
                errors.append(f"{rel}: undocumented token {{{{{tok}}}}} (add to DOCUMENTED_TOKENS)")

        opens = IF_OPEN_RE.findall(text)
        closes = IF_CLOSE_RE.findall(text)
        if len(opens) != len(closes):
            errors.append(f"{rel}: unbalanced IF blocks ({len(opens)} open, {len(closes)} close)")
        for flag in opens:
            if flag not in flags:
                errors.append(f"{rel}: undocumented IF flag '{flag}' (add it to the file-groups table)")

        # A token-bearing file should carry the .tmpl marker; a plain file should not
        # contain our tokens. (Actions ${{ }} already excluded by the regex.)
        has_token = any(
            t.group(1).isupper() and t.group(1) in DOCUMENTED_TOKENS
            for t in ANY_TOKEN_RE.finditer(text)
        )
        if has_token and not rel.endswith(".tmpl"):
            errors.append(f"{rel}: contains tokens but lacks the .tmpl suffix")
        if rel.endswith(".tmpl") and not has_token and not IF_OPEN_RE.search(text):
            errors.append(f"{rel}: has .tmpl suffix but no tokens or IF blocks")

        if rel not in ("ROADMAP.md.tmpl", "decision-log.md.tmpl"):  # vendored copies
            for m in RETIRED_RE.finditer(text):
                errors.append(f"{rel}: retired pointer or level language `{m.group(0)}`")
        for m in SKILL_URL_RE.finditer(text):
            if not (REFERENCES / m.group(1)).exists():
                errors.append(f"{rel}: links to a skill reference that doesn't exist: {m.group(1)}")
    return errors


# ── 2. Render ─────────────────────────────────────────────────────────────────


def _strip_ifs(text: str, active: set[str]) -> str:
    return IF_BLOCK_RE.sub(lambda m: m.group(2) if m.group(1) in active else "", text)


def _sub_tokens(text: str, values: dict[str, str]) -> str:
    for tok, val in values.items():
        text = re.sub(r"\{\{ *" + tok + r" *\}\}", val, text)
    return text


def render(dest: Path, values: dict[str, str], include: set[str], owner: dict[str, str],
           active_flags: set[str]) -> None:
    for p in _iter_files():
        rel = _rel(p)
        if owner.get(rel, "core") not in include:
            continue
        out = dest / (rel[:-5] if rel.endswith(".tmpl") else rel)
        out.parent.mkdir(parents=True, exist_ok=True)
        text = _read(p)
        if text is None:
            shutil.copy2(p, out)
            continue
        out.write_text(_sub_tokens(_strip_ifs(text, active_flags), values), encoding="utf-8")


def check_rendered(dest: Path) -> list[str]:
    errors: list[str] = []
    for p in sorted(dest.rglob("*")):
        if not p.is_file():
            continue
        text = _read(p)
        if not text:
            continue
        rel = p.relative_to(dest).as_posix()
        if ANY_TOKEN_RE.search(text):
            leftover = sorted({m.group(0) for m in ANY_TOKEN_RE.finditer(text)})
            errors.append(f"{dest.name}/{rel}: residual tokens {leftover}")
        if IF_OPEN_RE.search(text) or IF_CLOSE_RE.search(text):
            errors.append(f"{dest.name}/{rel}: residual IF markers")
    # py_compile every rendered .py — catches a template edit that breaks syntax,
    # with no network needed.
    pys = [str(p) for p in dest.rglob("*.py")]
    if pys:
        r = subprocess.run([sys.executable, "-m", "py_compile", *pys],
                           capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"py_compile failed on {dest.name} render:\n{r.stderr}")
    return errors


# ── 3. Smoke test (CI) ────────────────────────────────────────────────────────


def smoke(dest: Path, *, full: bool) -> list[str]:
    errors: list[str] = []

    def run(cmd: list[str]) -> str:
        r = subprocess.run(cmd, cwd=dest, capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"[{dest.name}] `{' '.join(cmd)}` failed:\n"
                          f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
        return r.stdout

    run(["uv", "sync", "--extra", "publish"] if full else ["uv", "sync"])
    if errors:
        return errors  # nothing else will work without deps
    if full:
        run(["uv", "run", "ruff", "check", "scripts", "tests"])
        run(["uv", "run", "ruff", "format", "--check", "scripts", "tests"])
    run(["uv", "run", "pytest", "-q"])
    help_text = run(["uv", "run", "python", "-m", "scripts.pipeline", "--help"])
    run(["uv", "run", "python", "-m", "scripts.pipeline", "run", "--help"])
    optional = {"discover", "publish"}
    m = re.search(r"\{([a-z,]+)\}", help_text)  # argparse lists subcommands as {run,fetch,…}
    shown = optional & set(m.group(1).split(",")) if m else set()
    if full and shown != optional:
        errors.append(f"[{dest.name}] pipeline --help lacks {sorted(optional - shown)}")
    if not full and shown:
        errors.append(f"[{dest.name}] pipeline --help offers {sorted(shown)} without their files")
    if full:
        run(["uv", "run", "python", "-m", "scripts.publish", "--help"])
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true",
                    help="Also uv sync + ruff + pytest the rendered projects (needs network).")
    ap.add_argument("--keep", action="store_true", help="Keep the rendered temp dir.")
    args = ap.parse_args(argv)

    if not TEMPLATE_ROOT.is_dir():
        print(f"error: template not found at {TEMPLATE_ROOT}", file=sys.stderr)
        return 2

    all_errors: list[str] = []

    print("Reading file groups and slot-fills from references/project-template.md …")
    groups, group_errors = documented_groups()
    owner, assign_errors = assign_groups(groups)
    flags = {g["flag"] for g in groups.values() if g["flag"]}
    meta_errors = group_errors + assign_errors
    doc_tokens = documented_tokens()
    if doc_tokens != DOCUMENTED_TOKENS:
        meta_errors.append(
            f"slot-fill table lists {sorted(doc_tokens)}; validator expects {sorted(DOCUMENTED_TOKENS)}"
        )
    all_errors += meta_errors
    counts = {name: sum(1 for g in owner.values() if g == name) for name in groups}
    print(f"  {'FAIL' if meta_errors else 'ok'} — groups {counts}, flags {sorted(flags)}")

    print(f"Linting templates under {TEMPLATE_ROOT.relative_to(SKILL_ROOT)} …")
    lint_errors = lint(flags)
    all_errors += lint_errors
    print(f"  {'FAIL' if lint_errors else 'ok'} — {len(lint_errors)} issue(s)")

    tmp = Path(tempfile.mkdtemp(prefix="dl-validate-"))
    renders = {
        "minimal": ({"core"}, set()),
        "full": (set(groups), flags),
    }
    try:
        for name, (include, active) in renders.items():
            dest = tmp / name
            print(f"Rendering the {name} project ({', '.join(sorted(include))}) to {dest} …")
            render(dest, RENDER_VALUES, include, owner, active)
            render_errors = check_rendered(dest)
            all_errors += render_errors
            print(f"  {'FAIL' if render_errors else 'ok'} — no residual tokens, syntax compiles")

        if args.smoke:
            for name in renders:
                print(f"Smoke-testing the {name} project …")
                smoke_errors = smoke(tmp / name, full=(name == "full"))
                all_errors += smoke_errors
                print(f"  {'FAIL' if smoke_errors else 'ok'}")
    finally:
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"  (kept renders under {tmp})")

    print()
    if all_errors:
        print(f"VALIDATION FAILED — {len(all_errors)} issue(s):")
        for e in all_errors:
            print(f"  ✗ {e}")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

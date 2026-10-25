#!/usr/bin/env python3
"""Validate the bundled project template — and prove it renders to a working project.

`data-liberation` scaffolds **agent-driven**: the agent reads the templates under
`templates/project/`, substitutes `{{UPPER_SNAKE}}` tokens, strips
`<!-- IF:FLAG -->…<!-- /IF -->` blocks whose flag is off, and writes the result into
the user's working directory (see SKILL.md, *Scaffold*). There is no scaffold CLI.

Because the template is a *runnable Python application* (not inert documents), this
validator does double duty — mirroring how `data-project-skill/scripts/validate.py`
renders templates to check them, extended to actually execute the rendered project:

  1. **Static lint** — no stray lower-case `{{ token }}` (un-migrated), every
     `{{UPPER}}` token is documented, `IF:FLAG` blocks are balanced and use
     documented flags.
  2. **Render** — deterministically render `templates/project/` to a temp dir using
     test values (the same transform the agent performs), and assert no residual
     `{{ }}` tokens escaped.
  3. **Smoke test** (`--smoke`, run in CI) — `uv sync`, `ruff`, `pytest`, and the CLI
     `--help` in the rendered project, so a template edit that breaks the scaffold
     fails loudly. Needs network (uv fetches deps); skipped by default.

Usage
-----
    python scripts/validate.py            # static lint + render + syntax-compile
    python scripts/validate.py --smoke    # the above + uv sync + ruff + pytest (CI)
    python scripts/validate.py --keep      # don't delete the rendered temp dir
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "templates" / "project"

# The slot-fills the agent must provide. Kept in lockstep with the
# "Slot-fills" table in references/project-template.md.
DOCUMENTED_TOKENS = {
    "PROJECT_NAME",
    "PROJECT_SLUG",
    "DESCRIPTION",
    "AUTHOR",
    "OWNER",
    "CONSUMER_STACK",
}

# Conditional flags the template may gate optional surfaces on. None are used yet
# (optional surfaces ship as `*.yml.disabled`), but the syntax + checks are here so
# the convention matches data-project-skill and is ready when wanted.
DOCUMENTED_FLAGS: set[str] = set()

# Test values for the render pass. PROJECT_SLUG must be a valid Python identifier
# and package name (the rendered pyproject.toml uses it).
RENDER_VALUES = {
    "PROJECT_NAME": "e2e-test-project",
    "PROJECT_SLUG": "e2e_test_project",
    "DESCRIPTION": "End-to-end validation render",
    "AUTHOR": "CI <ci@example.org>",
    "OWNER": "ci-bot",
    "CONSUMER_STACK": "pandas",
}

# `(?<!\$)` excludes GitHub Actions `${{ … }}` expressions, which are not our tokens.
ANY_TOKEN_RE = re.compile(r"(?<!\$)\{\{ *([A-Za-z_]+) *\}\}")
IF_BLOCK_RE = re.compile(r"<!-- IF:(\w+) -->\n?(.*?)<!-- /IF -->\n?", re.DOTALL)
IF_OPEN_RE = re.compile(r"<!-- IF:(\w+) -->")
IF_CLOSE_RE = re.compile(r"<!-- /IF -->")


def _iter_files():
    for p in sorted(TEMPLATE_ROOT.rglob("*")):
        if p.is_file():
            yield p


def _read(p: Path) -> str | None:
    try:
        return p.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return None


# ── 1. Static lint ────────────────────────────────────────────────────────────

def lint() -> list[str]:
    errors: list[str] = []
    for p in _iter_files():
        text = _read(p)
        if text is None:
            continue
        rel = p.relative_to(TEMPLATE_ROOT).as_posix()

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
            if flag not in DOCUMENTED_FLAGS:
                errors.append(f"{rel}: undocumented IF flag '{flag}' (add to DOCUMENTED_FLAGS)")

        # A token-bearing file should carry the .tmpl marker; a plain file should not
        # contain our tokens. (Actions ${{ }} already excluded by the regex.)
        has_token = any(t.group(1).isupper() and t.group(1) in DOCUMENTED_TOKENS
                        for t in ANY_TOKEN_RE.finditer(text))
        if has_token and not rel.endswith(".tmpl"):
            errors.append(f"{rel}: contains tokens but lacks the .tmpl suffix")
        if rel.endswith(".tmpl") and not has_token and not IF_OPEN_RE.search(text):
            errors.append(f"{rel}: has .tmpl suffix but no tokens or IF blocks")
    return errors


# ── 2. Render ─────────────────────────────────────────────────────────────────

def _strip_ifs(text: str, active: set[str]) -> str:
    return IF_BLOCK_RE.sub(lambda m: m.group(2) if m.group(1) in active else "", text)


def _sub_tokens(text: str, values: dict[str, str]) -> str:
    for tok, val in values.items():
        text = re.sub(r"\{\{ *" + tok + r" *\}\}", val, text)
    return text


def render(dest: Path, values: dict[str, str], active_flags: set[str]) -> None:
    for p in _iter_files():
        rel = p.relative_to(TEMPLATE_ROOT).as_posix()
        out_rel = rel[:-5] if rel.endswith(".tmpl") else rel
        out = dest / out_rel
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
        if text and ANY_TOKEN_RE.search(text):
            leftover = sorted({m.group(0) for m in ANY_TOKEN_RE.finditer(text)})
            errors.append(f"{p.relative_to(dest).as_posix()}: residual tokens {leftover}")
    # py_compile every rendered .py — catches a template edit that breaks syntax,
    # with no network needed.
    pys = [str(p) for p in dest.rglob("*.py")]
    if pys:
        r = subprocess.run([sys.executable, "-m", "py_compile", *pys],
                           capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"py_compile failed on rendered project:\n{r.stderr}")
    return errors


# ── 3. Smoke test (CI) ────────────────────────────────────────────────────────

def smoke(dest: Path) -> list[str]:
    errors: list[str] = []

    def run(cmd: list[str]) -> None:
        r = subprocess.run(cmd, cwd=dest, capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"`{' '.join(cmd)}` failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")

    run(["uv", "sync", "--extra", "publish"])
    if errors:
        return errors  # nothing else will work without deps
    run(["uv", "run", "ruff", "check", "scripts", "tests"])
    run(["uv", "run", "ruff", "format", "--check", "scripts", "tests"])
    run(["uv", "run", "pytest", "-q"])
    run(["uv", "run", "python", "-m", "scripts.pipeline", "--help"])
    run(["uv", "run", "python", "-m", "scripts.publish", "--help"])
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true",
                    help="Also uv sync + ruff + pytest the rendered project (needs network).")
    ap.add_argument("--keep", action="store_true", help="Keep the rendered temp dir.")
    args = ap.parse_args(argv)

    if not TEMPLATE_ROOT.is_dir():
        print(f"error: template not found at {TEMPLATE_ROOT}", file=sys.stderr)
        return 2

    all_errors: list[str] = []

    print(f"Linting templates under {TEMPLATE_ROOT.relative_to(SKILL_ROOT)} …")
    lint_errors = lint()
    all_errors += lint_errors
    print(f"  {'FAIL' if lint_errors else 'ok'} — {len(lint_errors)} issue(s)")

    tmp = Path(tempfile.mkdtemp(prefix="dl-validate-"))
    dest = tmp / "render"
    try:
        print(f"Rendering to {dest} …")
        render(dest, RENDER_VALUES, set(DOCUMENTED_FLAGS))
        render_errors = check_rendered(dest)
        all_errors += render_errors
        print(f"  {'FAIL' if render_errors else 'ok'} — no residual tokens, syntax compiles")

        if args.smoke:
            print("Smoke-testing rendered project (uv sync + ruff + pytest) …")
            smoke_errors = smoke(dest)
            all_errors += smoke_errors
            print(f"  {'FAIL' if smoke_errors else 'ok'}")
    finally:
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"  (kept render at {dest})")

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

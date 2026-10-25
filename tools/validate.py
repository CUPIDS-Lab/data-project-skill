#!/usr/bin/env python3
"""Validate the whole data-skills repository: layout, spec, links, vendoring, and each skill.

This is the one entry point CI runs. It checks what both skills share, then runs each
skill's own template validator (`tools/validate_<skill>.py`), which knows that skill's
tokens, flags and render rules.

Checks
------
1. **Layout** — no `SKILL.md` at the repository root or outside `skills/<name>/SKILL.md`
   (a shallower `SKILL.md` hides the skills below it from `npx skills`, and a literal
   `SKILL.md` inside `templates/` would be discovered as a skill), and no
   repository-maintenance files inside a skill folder (installs copy the whole folder).
2. **Agent Skills spec** — frontmatter keys limited to the set claude.ai uploads and the
   Skills API accept, `name` equal to its directory, description ≤ 1,024 characters,
   `metadata.version` in semver. Bodies over ~5,000 tokens are reported, because Claude
   Code keeps only a skill's first 5,000 tokens after compaction.
3. **Links** — every relative Markdown link in the skills' own docs (not the project
   templates, whose links resolve inside a generated project) points at a file that exists.
4. **Vendoring** — every copy of `shared/` content matches its source (`tools/vendor.py --check`).
5. **Per-skill validators** — `tools/validate_data_project.py` and
   `tools/validate_data_liberation.py` (`--smoke` is passed through).
6. **Version bump** (`--base REF`) — any change under `skills/<name>/` since REF must bump
   that skill's `metadata.version`.

Usage
-----
    python tools/validate.py                    # checks 1–5
    python tools/validate.py --smoke            # also smoke-test the rendered data-liberation project
    python tools/validate.py --spec-tool        # also run the official `agentskills validate`
    python tools/validate.py --base origin/main # also enforce version bumps (CI on PRs)

Needs PyYAML (`uv run --no-project --with pyyaml python tools/validate.py`).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
TOOLS = REPO / "tools"

# Keys accepted by claude.ai uploads and the Skills API. Claude Code-only keys
# (argument-hint, when_to_use, context, hooks, paths, …) make an upload fail.
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")
TOKEN_BUDGET = 5000
# Files that belong at the repository root, never inside an installed skill.
MAINTENANCE_NAMES = {"README.md", "CHANGELOG.md", "CONTRIBUTING.md", "RELEASING.md",
                     "CITATION.cff", ".github", "evals", "retro", "history", "tools"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def skill_dirs() -> list[Path]:
    return sorted(p.parent for p in SKILLS.glob("*/SKILL.md"))


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("no YAML frontmatter")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


# ── 1. Layout ─────────────────────────────────────────────────────────────────

def check_layout() -> list[str]:
    errors: list[str] = []
    if (REPO / "SKILL.md").exists():
        errors.append("SKILL.md at the repository root hides skills/*/ from `npx skills`")
    expected = {d / "SKILL.md" for d in skill_dirs()}
    for p in REPO.rglob("SKILL.md"):
        if ".git" in p.parts:
            continue
        if p not in expected:
            errors.append(f"{p.relative_to(REPO)}: stray SKILL.md (name templates *.SKILL.md.tmpl)")
    for d in skill_dirs():
        for name in MAINTENANCE_NAMES:
            if (d / name).exists():
                errors.append(f"{(d / name).relative_to(REPO)}: repository file inside a skill "
                              "folder is copied into every install; move it to the root")
    return errors


# ── 2. Spec ───────────────────────────────────────────────────────────────────

def check_spec() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []
    for d in skill_dirs():
        rel = (d / "SKILL.md").relative_to(REPO)
        try:
            fm, body = frontmatter(d / "SKILL.md")
        except (ValueError, yaml.YAMLError) as e:
            errors.append(f"{rel}: {e}")
            continue
        extra = set(fm) - ALLOWED_KEYS
        if extra:
            errors.append(f"{rel}: frontmatter keys {sorted(extra)} are rejected by claude.ai "
                          f"uploads; allowed: {sorted(ALLOWED_KEYS)}")
        name = fm.get("name", "")
        if name != d.name:
            errors.append(f"{rel}: name '{name}' must equal the directory name '{d.name}'")
        if not NAME_RE.match(str(name)) or len(str(name)) > 64:
            errors.append(f"{rel}: name must be lowercase letters, digits and hyphens, ≤ 64 chars")
        desc = str(fm.get("description", "")).strip()
        if not desc:
            errors.append(f"{rel}: description is empty")
        elif len(desc) > 1024:
            errors.append(f"{rel}: description is {len(desc)} chars (limit 1,024)")
        if len(str(fm.get("compatibility", ""))) > 500:
            errors.append(f"{rel}: compatibility exceeds 500 chars")
        version = (fm.get("metadata") or {}).get("version")
        if not version or not SEMVER_RE.match(str(version)):
            errors.append(f"{rel}: metadata.version must be semver (found {version!r})")
        tokens = len(body) // 4
        if tokens > TOKEN_BUDGET:
            notes.append(f"{rel}: body is ~{tokens:,} tokens (target ≤ {TOKEN_BUDGET:,}; "
                         "put the rules that must survive compaction first)")
    return errors, notes


def check_spec_tool() -> list[str]:
    """Run the official validator. Its exit code is 0 even on failure, so read its output."""
    errors: list[str] = []
    for d in skill_dirs():
        r = subprocess.run(["uvx", "--from", "skills-ref", "agentskills", "validate", str(d)],
                           capture_output=True, text=True)
        out = (r.stdout + r.stderr)
        if r.returncode != 0 or "Validation failed" in out:
            lines = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("-")]
            errors.append(f"agentskills validate {d.relative_to(REPO)}: " + ("; ".join(lines) or out[-500:]))
    return errors


# ── 3. Links ──────────────────────────────────────────────────────────────────

def doc_files() -> list[Path]:
    files: list[Path] = []
    for d in skill_dirs():
        files += [p for p in d.rglob("*.md") if "templates" not in p.relative_to(d).parts]
    files += [p for p in REPO.glob("*.md")]
    return files


def check_links() -> list[str]:
    errors: list[str] = []
    for f in doc_files():
        text = f.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)  # links in code samples are examples
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if not path or "{{" in path or "<" in path:
                continue
            if not (f.parent / path).exists():
                errors.append(f"{f.relative_to(REPO)}: broken link → {target}")
    return errors


# ── 4–6. Vendoring, per-skill validators, version bumps ──────────────────────

def run_tool(args: list[str]) -> list[str]:
    r = subprocess.run([sys.executable, *args], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        return [f"`python {' '.join(args)}` failed:\n{(r.stdout + r.stderr)[-4000:]}"]
    return []


def check_version_bumps(base: str) -> list[str]:
    errors: list[str] = []
    changed = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD", "--", "skills/"],
                             cwd=REPO, capture_output=True, text=True, check=True).stdout.split()
    touched = {Path(p).parts[1] for p in changed if len(Path(p).parts) > 2}
    for name in sorted(touched):
        skill_md = f"skills/{name}/SKILL.md"
        old = subprocess.run(["git", "show", f"{base}:{skill_md}"], cwd=REPO,
                             capture_output=True, text=True)
        if old.returncode != 0:
            continue  # a new skill, or new to this path: nothing to compare against
        m = re.match(r"^---\n(.*?)\n---\n", old.stdout, re.S)
        old_version = ((yaml.safe_load(m.group(1)) or {}).get("metadata") or {}).get("version") if m else None
        new_version = (frontmatter(SKILLS / name / "SKILL.md")[0].get("metadata") or {}).get("version")
        if old_version is not None and old_version == new_version:
            errors.append(f"skills/{name}/ changed since {base} but metadata.version is still {new_version}")
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true", help="Smoke-test the rendered data-liberation project.")
    ap.add_argument("--spec-tool", action="store_true", help="Also run `agentskills validate` via uvx.")
    ap.add_argument("--base", help="Git ref to compare against for the version-bump check.")
    args = ap.parse_args(argv)

    sections: list[tuple[str, list[str]]] = []
    sections.append(("layout", check_layout()))
    spec_errors, spec_notes = check_spec()
    sections.append(("spec", spec_errors))
    if args.spec_tool:
        sections.append(("agentskills validate", check_spec_tool()))
    sections.append(("links", check_links()))
    sections.append(("vendoring", run_tool(["tools/vendor.py", "--check"])))
    sections.append(("data-project templates", run_tool(["tools/validate_data_project.py"])))
    dl_args = ["tools/validate_data_liberation.py"] + (["--smoke"] if args.smoke else [])
    sections.append(("data-liberation templates", run_tool(dl_args)))
    if args.base:
        sections.append(("version bumps", check_version_bumps(args.base)))

    failed = 0
    for label, errs in sections:
        print(f"{'FAIL' if errs else 'ok  '}  {label}")
        for e in errs:
            print(f"        - {e}")
        failed += len(errs)
    for n in spec_notes:
        print(f"note  {n}")
    print()
    print(f"VALIDATION FAILED — {failed} issue(s)" if failed else "VALIDATION PASSED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

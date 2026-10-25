#!/usr/bin/env python3
"""Validate the data-project skill's references and templates for internal consistency.

Run from anywhere: `python3 tools/validate_data_project.py`. Exits non-zero on any failure.
It guards the drift a manual audit found: references without OKF `type` frontmatter,
unbalanced, nested or undocumented template conditionals, undocumented tokens, templates
that render to invalid JSON or YAML or leave tokens behind, leftover level language, and
review gates claimed without the branch protection that enforces them. Keep the two
documented sets below in sync with the token and flag tables in
`references/procedures/scaffold.md` (check 2 enforces that). `references/_shared/` is
vendored from `shared/` and validated by `tools/validate.py`, so it is skipped here except
that links into it must resolve.
"""
import json
import re
import shutil
import subprocess
import sys
import pathlib
import tempfile

try:
    import yaml  # optional: YAML templates are parsed only when PyYAML is installed
except ImportError:  # pragma: no cover
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent.parent / "skills" / "data-project"
REFS = ROOT / "references"
TEMPLATES = ROOT / "templates"
SCAFFOLD = REFS / "procedures" / "scaffold.md"
errors: list[str] = []

DOCUMENTED_TOKENS = {
    # Core project facts (from the scoping brief)
    "PROJECT_NAME", "PROJECT_SLUG", "PKG_NAME", "DESCRIPTION", "PI_NAME", "LAB_NAME",
    "CONTACT_EMAIL", "YEAR", "DATE", "SKILL_VERSION", "LICENSE", "SENSITIVITY_TIER",
    "VISIBILITY", "TOOLING", "REPO_URL", "RAW_FILE",
    # GitHub layer (governance, tracking)
    "REPO_SLUG", "DEFAULT_BRANCH", "PROJECT_TITLE", "OWNER_DEFAULT", "ISSUE_SEED_ROWS",
    # Agentic Resource Discovery (section 9)
    "ARD_SPEC_VERSION", "ARD_HOST_DOMAIN", "ARD_HOST_IDENTIFIER",
    # Dataverse deposit, including scheduled versioned re-deposit (section 9)
    "DATAVERSE_URL", "DATAVERSE_COLLECTION", "DATASET_SUBJECT", "UPDATE_FREQUENCY", "DEPOSIT_CRON",
    # OpenSharing zero-copy sharing (section 9)
    "OPENSHARING_ENDPOINT", "SHARE_STORAGE_BASE",
}
DOCUMENTED_FLAGS = {"PIPELINE", "PIPELINES", "SENSITIVE", "OPEN", "COLLAB", "SOLO", "GH", "PROJECT",
                    "NOTEBOOKS", "OKF", "ARD", "DATAVERSE", "UPDATING", "OPENSHARING"}

# Sample values used when rendering templates for checks 5 and 7.
SAMPLE = {tok: "sample" for tok in DOCUMENTED_TOKENS}
SAMPLE.update({"DATE": "2026-01-31", "YEAR": "2026", "DEFAULT_BRANCH": "main", "LICENSE": "MIT",
               "REPO_SLUG": "owner/repo", "DEPOSIT_CRON": "0 6 1 * *", "ARD_SPEC_VERSION": "1.0",
               "ISSUE_SEED_ROWS": 'seed_issue "section-1" "Section 1: Scope & gate" "section:1" "high" "M" "- [ ] done"'})

IF_OPEN = re.compile(r"<!-- IF:([A-Z_]+) -->")
IF_CLOSE = "<!-- /IF -->"
TOKEN = re.compile(r"(?<!\$)\{\{([^}]*)\}\}")


def rel(p: pathlib.Path) -> str:
    return str(p.relative_to(ROOT))


def render(text: str, flags_on: bool) -> str:
    """Resolve IF blocks (all flags on, or all off) and fill tokens with sample values."""
    if flags_on:
        out = re.sub(r"<!-- IF:[A-Z_]+ -->|<!-- /IF -->", "", text)
    else:
        out = re.sub(r"<!-- IF:[A-Z_]+ -->.*?<!-- /IF -->", "", text, flags=re.S)
    return TOKEN.sub(lambda m: SAMPLE.get(m.group(1), m.group(0)), out)


skill_refs = sorted(REFS.glob("*.md")) + sorted((REFS / "procedures").glob("*.md"))

# 1. Every reference and procedure is an OKF-conformant concept: non-empty `type` in frontmatter.
for f in skill_refs:
    head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:8])
    if not head.startswith("---") or not re.search(r"^type:\s*\S", head, re.M):
        errors.append(f"{rel(f)}: missing non-empty `type:` frontmatter (OKF conformance)")

# 2. Template conditionals balanced, not nested and documented; tokens well-formed and documented;
#    every documented token and flag appears in the scaffold procedure's tables.
templates = sorted(TEMPLATES.rglob("*.tmpl"))
for f in templates:
    text = f.read_text(encoding="utf-8")
    opens = IF_OPEN.findall(text)
    closes = text.count(IF_CLOSE)
    if len(opens) != closes:
        errors.append(f"{rel(f)}: unbalanced IF blocks (open={len(opens)} close={closes})")
    depth = 0
    for m in re.finditer(r"<!-- IF:[A-Z_]+ -->|<!-- /IF -->", text):
        depth += 1 if m.group(0) != IF_CLOSE else -1
        if depth > 1:
            errors.append(f"{rel(f)}: nested IF blocks (keep conditionals one level deep)")
            break
    for fl in opens:
        if fl not in DOCUMENTED_FLAGS:
            errors.append(f"{rel(f)}: undocumented IF flag '{fl}'")
    # GitHub Actions ${{ ... }} expressions (the $-prefixed form) are not skill tokens.
    for tok in TOKEN.findall(text):
        if not re.fullmatch(r"[A-Z0-9_]+", tok):
            errors.append(f"{rel(f)}: malformed token '{{{{{tok}}}}}'")
        elif tok not in DOCUMENTED_TOKENS:
            errors.append(f"{rel(f)}: undocumented token '{{{{{tok}}}}}'")
scaffold_text = SCAFFOLD.read_text(encoding="utf-8") if SCAFFOLD.exists() else ""
for name in sorted(DOCUMENTED_TOKENS | DOCUMENTED_FLAGS):
    if f"| `{name}` |" not in scaffold_text:
        errors.append(f"{rel(SCAFFOLD)}: token/flag `{name}` is not in its token or flag table")

# 3. SKILL.md declares name + description.
skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
if not re.search(r"^name:\s*\S", skill_text, re.M):
    errors.append("SKILL.md: missing `name:` frontmatter")
if not re.search(r"^description:", skill_text, re.M):
    errors.append("SKILL.md: missing `description:` frontmatter")

# 4. Removed machinery stays removed: no agents/ folder, no level language in templates, no
#    nested `.skills/` paths or plugin-only `${CLAUDE_PLUGIN_ROOT}` anywhere in the skill.
if (ROOT / "agents").exists():
    errors.append("agents/: removed in 0.11.0 (its procedures live in references/procedures/)")
LEVEL = re.compile(r"\{\{LEVEL\}\}|\blevel:|\bL[0-5]\b|\bescalation level", re.I)
for f in sorted(TEMPLATES.rglob("*")):
    if f.is_file() and LEVEL.search(f.read_text(encoding="utf-8")):
        errors.append(f"{rel(f)}: level language ({LEVEL.search(f.read_text(encoding='utf-8')).group(0)!r}); "
                      "refer to Outline sections instead")
for f in [ROOT / "SKILL.md", *skill_refs, *sorted(TEMPLATES.rglob("*"))]:
    if not f.is_file():
        continue
    text = f.read_text(encoding="utf-8")
    if re.search(r"(?<![\w-])\.skills/", text):
        errors.append(f"{rel(f)}: `.skills/` path (no agent discovers it; nested skills were removed)")
    if "CLAUDE_PLUGIN_ROOT" in text:
        errors.append(f"{rel(f)}: `${{CLAUDE_PLUGIN_ROOT}}` is plugin-only; use paths relative to the skill folder")

# 5. Links from references into `_shared/` resolve (they are vendored by tools/vendor.py).
for f in skill_refs:
    for m in re.finditer(r"`((?:\.\./)?_shared/[\w.-]+\.md)`", f.read_text(encoding="utf-8")):
        if not (f.parent / m.group(1)).resolve().exists():
            errors.append(f"{rel(f)}: link `{m.group(1)}` does not resolve (run tools/vendor.py?)")

# 6. Honest review gates: a template that claims an approval gate on PRs or reviews must also
#    carry the branch-protection step that enforces it, and the governance templates ship both
#    the collaborator (COLLAB) and single-steward (SOLO) variants.
GATE = re.compile(r"approv\w*[^.\n]{0,60}\b(review|PR|pull request)\b|approving review", re.I)
for f in templates:
    text = f.read_text(encoding="utf-8")
    if GATE.search(text) and not re.search(r"branch[ -]protection", text, re.I):
        errors.append(f"{rel(f)}: claims an approval/review gate without the branch-protection step")
for name in ("GOVERNANCE.md.tmpl", "CONTRIBUTING.md.tmpl"):
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    for fl in ("COLLAB", "SOLO"):
        if f"<!-- IF:{fl} -->" not in text:
            errors.append(f"templates/{name}: missing the {fl} variant")

# 7. Render every template with all flags on and all off: no residual tokens or IF markers, and
#    JSON/YAML/shell/Python templates stay parseable in both renderings.
bash = shutil.which("bash")
for f in templates:
    text = f.read_text(encoding="utf-8")
    target = f.name[: -len(".tmpl")]
    for label, flags_on in (("all flags on", True), ("all flags off", False)):
        out = render(text, flags_on)
        if TOKEN.search(out):
            errors.append(f"{rel(f)}: residual token {TOKEN.search(out).group(0)} when rendered with {label}")
        if "<!-- IF:" in out or IF_CLOSE in out:
            errors.append(f"{rel(f)}: residual IF marker when rendered with {label}")
        try:
            if target.endswith(".json"):
                json.loads(out)
            elif target.endswith((".yml", ".yaml")) and yaml is not None:
                yaml.safe_load(out)
            elif target.endswith(".py"):
                compile(out, target, "exec")
        except (json.JSONDecodeError, SyntaxError) as e:
            errors.append(f"{rel(f)}: invalid {target.rsplit('.', 1)[-1]} when rendered with {label}: {e}")
        except Exception as e:  # yaml.YAMLError
            errors.append(f"{rel(f)}: invalid YAML when rendered with {label}: {e}")
        if target.endswith(".sh") and bash:
            with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as tmp:
                tmp.write(out)
            r = subprocess.run([bash, "-n", tmp.name], capture_output=True, text=True)
            pathlib.Path(tmp.name).unlink()
            if r.returncode:
                errors.append(f"{rel(f)}: bash syntax error when rendered with {label}: {r.stderr.strip()}")

# 8. The multi-pipeline CI discovers what every data-liberation pipeline has (pyproject.toml),
#    never an optional marker such as a Snakefile, and fails on a pipeline directory without one.
ci = (TEMPLATES / "ci" / "pipelines-ci.yml.tmpl").read_text(encoding="utf-8")
if "-name pyproject.toml" not in ci or "Snakefile" in ci:
    errors.append("templates/ci/pipelines-ci.yml.tmpl: must discover pipelines/*/pyproject.toml, not a Snakefile")
if "has no pyproject.toml" not in ci:
    errors.append("templates/ci/pipelines-ci.yml.tmpl: missing the check that fails on a pipeline without pyproject.toml")

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"All checks passed ({len(skill_refs)} references and procedures, {len(templates)} templates).")

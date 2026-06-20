#!/usr/bin/env python3
"""Validate the data-project skill repo for internal consistency.

Run from anywhere: `python scripts/validate.py`. Exits non-zero on any failure.
This guards exactly the classes of drift a manual audit found: missing OKF
`type` frontmatter on references, unbalanced or undocumented template
conditionals, and malformed or undocumented placeholder tokens. Keep the two
documented sets below in sync with SKILL.md's "Placeholders & conditionals".
"""
import json
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []

DOCUMENTED_TOKENS = {
    "PROJECT_NAME", "PROJECT_SLUG", "PKG_NAME", "DESCRIPTION", "PI_NAME",
    "LAB_NAME", "YEAR", "LICENSE", "LEVEL", "SENSITIVITY_TIER", "OPENNESS",
    "CONTACT_EMAIL", "TOOLING", "REPO_URL", "RAW_FILE", "ROADMAP_ROWS",
    # GitHub project-management layer (Step 6.5 Handoff / Track mode)
    "REPO_SLUG", "DEFAULT_BRANCH", "MILESTONE_TITLE", "PROJECT_TITLE",
    "TRACKING_ROWS", "ISSUE_SEED_ROWS", "OWNER_DEFAULT",
    # Agentic Resource Discovery layer (L5 ai-catalog.json)
    "ARD_SPEC_VERSION", "ARD_HOST_DOMAIN", "ARD_HOST_IDENTIFIER",
    # Harvard Dataverse deposit layer (L5)
    "DATAVERSE_URL", "DATAVERSE_COLLECTION", "DATASET_SUBJECT",
    # Versioned / periodically-updated Dataverse deposit (scheduled re-deposit)
    "UPDATE_FREQUENCY", "DEPOSIT_CRON",
}
DOCUMENTED_FLAGS = {"WHY", "PIPELINE", "SENSITIVE", "OPEN", "COLLAB", "NESTED_SKILLS", "OKF",
                    "GH", "PROJECT", "WIKI", "ARD", "DATAVERSE", "NOTEBOOKS", "UPDATING"}


def rel(p: pathlib.Path) -> str:
    return str(p.relative_to(ROOT))


# 1. Every reference is an OKF-conformant concept: non-empty `type` in frontmatter.
for f in sorted((ROOT / "references").glob("*.md")):
    head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:8])
    if not re.search(r"^type:\s*\S", head, re.M):
        errors.append(f"{rel(f)}: missing non-empty `type:` frontmatter (OKF conformance)")

# 2. Template conditionals balanced + documented; tokens well-formed + documented.
for f in sorted((ROOT / "templates").rglob("*.tmpl")):
    text = f.read_text(encoding="utf-8")
    opens = re.findall(r"<!-- IF:([A-Z_]+) -->", text)
    closes = re.findall(r"<!-- /IF -->", text)
    if len(opens) != len(closes):
        errors.append(f"{rel(f)}: unbalanced IF blocks (open={len(opens)} close={len(closes)})")
    for fl in opens:
        if fl not in DOCUMENTED_FLAGS:
            errors.append(f"{rel(f)}: undocumented IF flag '{fl}'")
    # Skip GitHub Actions ${{ ... }} expressions (the $-prefixed form) so workflow templates can
    # reference secrets/inputs; only bare {{ ... }} are treated as skill tokens.
    for tok in re.findall(r"(?<!\$)\{\{([^}]*)\}\}", text):
        if not re.fullmatch(r"[A-Z0-9_]+", tok):
            errors.append(f"{rel(f)}: malformed token '{{{{{tok}}}}}'")
        elif tok not in DOCUMENTED_TOKENS:
            errors.append(f"{rel(f)}: undocumented token '{{{{{tok}}}}}'")

# 3. SKILL.md and every agent declare name + description.
for f in [ROOT / "SKILL.md", *sorted((ROOT / "agents").glob("*.md"))]:
    text = f.read_text(encoding="utf-8")
    if not re.search(r"^name:\s*\S", text, re.M):
        errors.append(f"{rel(f)}: missing `name:` frontmatter")
    if not re.search(r"^description:", text, re.M):
        errors.append(f"{rel(f)}: missing `description:` frontmatter")

# 4. Every template path cited in INDEX.md §C exists (expanding {a,b,c} groups).
index = (ROOT / "references" / "INDEX.md").read_text(encoding="utf-8")
for path in set(re.findall(r"`(templates/[^`]+)`", index)):
    m = re.search(r"\{([^}]*)\}", path)
    variants = (
        [path[: m.start()] + opt + path[m.end():] for opt in m.group(1).split(",")]
        if m else [path]
    )
    for v in variants:
        if not (ROOT / v.strip()).exists():
            errors.append(f"INDEX.md cites missing template: {v.strip()}")

# 5. JSON templates (ARD ai-catalog, Dataverse dataset.json, …) stay valid JSON once
#    conditionals resolve and tokens are filled. Check both extremes — all flags on (strip
#    only the IF markers) and all off (drop the whole IF blocks) — so neither rendering can
#    ship malformed JSON.
for f in sorted((ROOT / "templates").rglob("*.json.tmpl")):
    text = f.read_text(encoding="utf-8")
    all_on = re.sub(r"<!-- /?IF(?::[A-Z_]+)? -->", "", text)
    all_off = re.sub(r"<!-- IF:[A-Z_]+ -->.*?<!-- /IF -->", "", text, flags=re.S)
    for label, rendered in (("all flags on", all_on), ("all flags off", all_off)):
        filled = re.sub(r"\{\{[A-Z0-9_]+\}\}", "x", rendered)
        try:
            json.loads(filled)
        except json.JSONDecodeError as e:
            errors.append(f"{rel(f)}: invalid JSON when rendered with {label}: {e}")

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"All checks passed ({len(list((ROOT/'references').glob('*.md')))} references, "
      f"{len(list((ROOT/'templates').rglob('*.tmpl')))} templates).")

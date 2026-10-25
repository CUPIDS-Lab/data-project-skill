#!/usr/bin/env python3
"""Copy shared/ content into each skill, or check that the copies have not drifted.

Installed skills must be self-contained: a claude.ai upload, an `npx skills` install
or a manual copy brings only the skill's own folder, so a skill can never reference
`../shared/`. Content both skills need therefore lives once in `shared/` and is
vendored into each skill at the paths listed in `shared/vendor.toml`. Edit the file in
`shared/`, run this script, and commit both.

Usage
-----
    python tools/vendor.py           # write every vendored copy
    python tools/vendor.py --check   # exit 1 if any copy is missing or differs (CI)
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHARED = REPO / "shared"
MANIFEST = SHARED / "vendor.toml"

# Markdown copies carry a provenance header so nobody edits the copy by mistake. Other
# file types are copied byte-for-byte (a header could break JSON, YAML or templates).
HEADER = "<!-- Vendored from shared/{src} by tools/vendor.py. Edit shared/{src}, not this copy. -->\n\n"


def load_manifest() -> list[tuple[str, list[str]]]:
    """Return (shared-relative source, [repo-relative destinations]) pairs."""
    data = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    pairs: list[tuple[str, list[str]]] = []
    for entry in data.get("file", []):
        pairs.append((entry["src"], list(entry["dest"])))
    return pairs


def expected_bytes(src: str) -> bytes:
    raw = (SHARED / src).read_bytes()
    if not src.endswith(".md"):
        return raw
    text = raw.decode("utf-8")
    header = HEADER.format(src=src)
    # Frontmatter must stay on line 1 to remain frontmatter, so the header follows it.
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4) + len("\n---\n")
        return (text[:end] + "\n" + header + text[end:].lstrip("\n")).encode("utf-8")
    return (header + text).encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="Report drift instead of writing.")
    args = ap.parse_args(argv)

    problems: list[str] = []
    written = 0
    for src, dests in load_manifest():
        if not (SHARED / src).is_file():
            problems.append(f"shared/{src}: listed in vendor.toml but missing")
            continue
        want = expected_bytes(src)
        for dest in dests:
            out = REPO / dest
            have = out.read_bytes() if out.is_file() else None
            if have == want:
                continue
            if args.check:
                state = "missing" if have is None else "differs from shared/" + src
                problems.append(f"{dest}: {state}")
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(want)
                written += 1

    if problems:
        print("VENDOR DRIFT:" if args.check else "VENDOR ERRORS:")
        for p in problems:
            print(f"  - {p}")
        if args.check:
            print("Fix: edit the file under shared/, then run `python tools/vendor.py` and commit.")
        return 1
    print("vendored copies up to date" if args.check else f"wrote {written} vendored file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

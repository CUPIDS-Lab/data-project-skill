#!/usr/bin/env python3
"""Build one upload-ready zip per skill (for claude.ai organization skills).

Each zip's top level is the skill's own folder (`data-project/SKILL.md`), which is the
shape claude.ai expects; a bare SKILL.md at the zip root is not recognized. Vendored
copies are checked first, so a zip never ships stale shared content.

Usage
-----
    python tools/build_zips.py                  # every skill → dist/<skill>.zip
    python tools/build_zips.py data-liberation  # one skill
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIST = REPO / "dist"
SKIP = {"__pycache__", ".DS_Store"}


def build(name: str) -> Path:
    src = REPO / "skills" / name
    if not (src / "SKILL.md").is_file():
        raise SystemExit(f"no skill at skills/{name}/")
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(src.rglob("*")):
            if p.is_file() and not SKIP & set(p.parts):
                zf.write(p, Path(name) / p.relative_to(src))
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    if f"{name}/SKILL.md" not in names:
        raise SystemExit(f"{out}: {name}/SKILL.md missing from the archive")
    print(f"{out.relative_to(REPO)}: {len(names)} files")
    return out


def main(argv: list[str]) -> int:
    check = subprocess.run([sys.executable, str(REPO / "tools" / "vendor.py"), "--check"])
    if check.returncode != 0:
        return 1
    names = argv or sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md"))
    for name in names:
        build(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

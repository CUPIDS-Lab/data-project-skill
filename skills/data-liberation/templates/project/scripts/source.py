"""The project's one source: what to fetch, and which parser reads each file.

Two functions are the whole contract:

* `artifacts()` lists every file upstream as an `Artifact` (vintage, URL, local
  path). It is cheap and downloads nothing; `fetch` downloads, `clean` parses.
* `parser_for(artifact)` returns the parser module that reads that file. Each
  module under `scripts/parsers/` exposes `parse(path) -> DataFrame` and two
  constants, `METHOD` and `TOOLS`, that land in `provenance.csv`.

Before writing either, probe the live source: download one real file from every
era you believe exists and open several pages of each. Descriptions, landing pages
and older pipelines describe the source as it was, not as it is served now.

Vintage keys come from the file's own name or content, never from the directory
or date it was published under: a period's file is often posted months later.

This module is deliberately concrete. When a second source arrives, move it to
`scripts/sources/<slug>.py` and add a registry then, not before (see "Adding a
second source" in the data-liberation skill's `project-template.md`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from scripts.config import DATA_ORIGINAL, SOURCE_SLUG


@dataclass(frozen=True)
class Artifact:
    """One downloadable file from upstream."""

    source: str
    vintage: str
    url: str
    local_path: Path

    @property
    def rel(self) -> str:
        """Path relative to `data/original/`: the key in the manifest and provenance."""
        try:
            return self.local_path.relative_to(DATA_ORIGINAL).as_posix()
        except ValueError:
            return self.local_path.as_posix()


# (vintage, url) pairs for publishers with a stable list of files. Replace with a
# scrape of the index page in `artifacts()` when the list changes over time.
ARTIFACTS: list[tuple[str, str]] = [
    # ("2024", "https://example.gov/reports/2024-annual-report.pdf"),
]


def artifacts() -> list[Artifact]:
    """Every artifact upstream, in a stable order. Cheap; no downloads."""
    out = []
    for vintage, url in ARTIFACTS:
        name = url.rstrip("/").rsplit("/", 1)[-1] or "download"
        path = DATA_ORIGINAL / SOURCE_SLUG / vintage / name
        out.append(Artifact(SOURCE_SLUG, vintage, url, path))
    return sorted(out, key=lambda a: (a.vintage, a.rel))


# A year, optionally followed by a quarter or month: 2024, 2024Q1, 2024-Q3, 2024-07.
VINTAGE_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?:[-_ ]?(Q[1-4]|0[1-9]|1[0-2]))?(?!\d)", re.I)


def vintage_from_filename(name: str) -> str | None:
    """Read the period a file covers from its own file name.

    Pass the file name, not the URL: `/2026-02/permits-2025Q4.csv` covers
    2025Q4, though it was published in 2026. When a name carries several years,
    the last one wins, because names usually end with the period they cover.
    """
    matches = list(VINTAGE_RE.finditer(Path(name).name))
    if not matches:
        return None
    year, part = matches[-1].groups()
    if not part:
        return year
    if part.upper().startswith("Q"):
        return f"{year}{part.upper()}"
    return f"{year}-{part}"


def parser_for(artifact: Artifact) -> ModuleType:
    """Return the parser module for one artifact.

    One module per layout era, chosen by an explicit condition, for example:

        if artifact.vintage < "2015":
            from scripts.parsers import example_2009_2014 as module
        else:
            from scripts.parsers import example_2015_present as module
        return module
    """
    raise NotImplementedError(
        f"No parser for {artifact.rel} (vintage {artifact.vintage}). Add a module under "
        "scripts/parsers/ and route to it in scripts/source.py:parser_for."
    )

"""The `Source` abstract base class and `Artifact` dataclass.

Every upstream provider in this project subclasses `Source` and obeys
the two-method contract: `discover` enumerates what's available
upstream (cheap, no downloads); `ingest` reads a previously-fetched
local file and returns a canonical-schema DataFrame.

This `discover` / `ingest` split is the convention from
BoulderPublicData/Election-Results. It separates the *online* question
("what's available?") from the *offline* question ("how do I parse
this file?"), which lets `fetch.py` be reused across sources and makes
parsers unit-testable against fixtures.

See `references/project-template.md` for the per-source layout and
`references/data-modeling.md` for what the returned DataFrame must
look like.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd


@dataclass
class Artifact:
    """One downloadable unit from upstream.

    A `Source.discover()` yields these; `fetch.py` downloads to `local_path`;
    `Source.ingest()` reads them.
    """

    source: str
    vintage: str
    url: str
    local_path: Path
    metadata: dict[str, Any] = field(default_factory=dict)


class Source(ABC):
    """The contract every source obeys.

    Subclasses set `name` (matches `data/original/<name>/`) and `label`
    (human-readable), and implement `discover` and `ingest`.
    """

    name: ClassVar[str]
    label: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Allow ABCs / partial implementations to skip this check via _abstract = True.
        if getattr(cls, "_abstract", False):
            return
        for attr in ("name", "label"):
            if not getattr(cls, attr, None):
                raise TypeError(f"{cls.__name__} must define class attribute `{attr}`")

    @abstractmethod
    def discover(self) -> Iterator[Artifact]:
        """Enumerate available artifacts upstream. Cheap; no downloads.

        Implementations either build a static list of URLs (publishers
        with predictable annual filenames) or scrape an index page (most
        agencies' "Reports" landing pages). See
        `references/discovery-and-audit.md` for both patterns.
        """

    @abstractmethod
    def ingest(self, artifact: Artifact) -> pd.DataFrame:
        """Load `artifact.local_path` and return a canonical-schema DataFrame.

        Implementations dispatch to `scripts.parsers.<source>_<vintage>`
        modules based on `artifact.vintage` for long-running series where
        upstream layouts change. Each parser exposes `parse(path) -> pd.DataFrame`
        returning a frame that validates via `scripts.schema.normalize_long`.

        Errors raised here are caught by `clean.py` and recorded in
        `data/audit/extraction_errors.json`; the pipeline continues with
        the remaining artifacts.
        """

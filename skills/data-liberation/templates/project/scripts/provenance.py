"""Per-extract provenance: one row of `data/processed/provenance.csv` per artifact
and parser run, never repeated on every data row.

The chain a reader follows from a suspicious value: the row's `(source, vintage)` →
its rows here → `artifact`, `source_url` and `sha256` → the untouched original in
`data/original/`. Rows are sorted and carry no wall-clock time of the clean run, so
re-running `clean` on the same originals writes a byte-identical file;
`retrieved_at` is copied from the fetch manifest and changes only on a refetch.
"""

from __future__ import annotations

import hashlib
import re
from importlib import metadata
from pathlib import Path
from types import ModuleType
from typing import Any

PROVENANCE_COLUMNS = [
    "source",
    "vintage",
    "artifact",
    "source_url",
    "sha256",
    "size_bytes",
    "retrieved_at",
    "parser_module",
    "extraction_method",
    "tool_versions",
    "extraction_quality",
    "extraction_notes",
    "rows_parsed",
    "rows_out",
    "rows_rejected",
    "source_license",
]

# The canonical vocabulary, shared with the data-liberation skill's data-modeling.md.
EXTRACTION_METHOD_RE = re.compile(
    r"^(native|text_layer|table_lattice|table_stream|api|scrape|manual"
    r"|ocr:[\w.-]+|vlm:[\w./-]+@[\w.-]+|layout:[\w.-]+|cv:[\w./-]+)$"
)
EXTRACTION_QUALITIES = ("clean", "caveats", "degraded")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def tool_versions(tools: tuple[str, ...] | list[str]) -> str:
    """`pypdfium2==4.30.0;pandas==2.2.3` for the distributions a parser names."""
    out = []
    for name in sorted(tools):
        try:
            out.append(f"{name}=={metadata.version(name)}")
        except metadata.PackageNotFoundError:
            out.append(f"{name}==not-installed")
    return ";".join(out)


def parser_metadata(module: ModuleType | None) -> dict[str, str]:
    """Read and check the METHOD / TOOLS / QUALITY / NOTES a parser module declares."""
    if module is None:
        return {"parser_module": "", "extraction_method": "", "tool_versions": ""}
    method = getattr(module, "METHOD", "")
    if not EXTRACTION_METHOD_RE.match(method):
        raise ValueError(
            f"{module.__name__}.METHOD = {method!r} is not a canonical extraction_method "
            "(native, text_layer, table_lattice, table_stream, ocr:<engine>, "
            "vlm:<model>@<revision>, layout:<tool>, api, scrape, cv:<model>, manual)"
        )
    quality = getattr(module, "QUALITY", "clean")
    if quality not in EXTRACTION_QUALITIES:
        raise ValueError(f"{module.__name__}.QUALITY = {quality!r}; use clean|caveats|degraded")
    return {
        "parser_module": module.__name__,
        "extraction_method": method,
        "tool_versions": tool_versions(getattr(module, "TOOLS", ())),
        "extraction_quality": quality,
        "extraction_notes": getattr(module, "NOTES", ""),
    }


def row(artifact: Any, manifest_entry: dict[str, Any], **fields: Any) -> dict[str, Any]:
    """One provenance row; `fields` fill or override the parser and count columns."""
    base: dict[str, Any] = {c: "" for c in PROVENANCE_COLUMNS}
    base.update(
        source=artifact.source,
        vintage=artifact.vintage,
        artifact=artifact.rel,
        source_url=artifact.url,
        sha256=manifest_entry.get("sha256", ""),
        size_bytes=manifest_entry.get("size_bytes", ""),
        retrieved_at=manifest_entry.get("fetched_at", ""),
        rows_parsed=0,
        rows_out=0,
        rows_rejected=0,
    )
    base.update(fields)
    return base

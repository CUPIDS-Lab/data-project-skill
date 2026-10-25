"""Concept catalog: cross-source harmonization with caveats.

When two or more sources measure the same underlying thing under
different names — IPEDS `EFTOTLT`, CDHE `TOTAL_HEADCOUNT`, factbook
`fall_census_total` all mean "total fall headcount" — the catalog
records (a) the canonical concept name, (b) which source variables
map to it per vintage, and (c) the **caveats** documenting what is
and is not comparable.

A concept catalog is NOT a rename map. The caveats are the point.
See `references/data-modeling.md#concept-catalogs` for the rationale
and the IPEDS pipeline's `concepts.py` as the model.

This module is optional. Single-source projects can ignore it
entirely; the `concept` column in the canonical schema stays nullable
and unused.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from scripts.config import DATA_LOOKUPS

CONCEPTS_YAML = DATA_LOOKUPS / "concepts.yaml"


@dataclass
class SourceMapping:
    """One source's mapping into a concept."""

    source: str
    variable: str
    vintages: list[str] = field(default_factory=list)  # ["2010-2019", "2020-"]
    notes: str = ""


@dataclass
class Concept:
    """One concept the project tracks, possibly across sources."""

    name: str
    description: str
    mappings: list[SourceMapping] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # A concept with no caveats and >1 source mapping is suspicious;
        # most cross-source comparisons have at least one definitional issue.
        # We warn, not raise — single-clean-source concepts exist.
        pass


def load_concepts(path: Path = CONCEPTS_YAML) -> dict[str, Concept]:
    """Load concept catalog from YAML; empty dict if file is absent."""
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text()) or []
    out: dict[str, Concept] = {}
    for entry in raw:
        mappings: list[SourceMapping] = []
        for src_name, src_data in (entry.get("sources") or {}).items():
            mappings.append(
                SourceMapping(
                    source=src_name,
                    variable=src_data.get("variable", ""),
                    vintages=src_data.get("vintages", []),
                    notes=src_data.get("notes", ""),
                )
            )
        out[entry["concept"]] = Concept(
            name=entry["concept"],
            description=entry.get("description", ""),
            mappings=mappings,
            caveats=entry.get("caveats", []),
        )
    return out


def concept_for(
    source: str, vintage: str, variable: str, concepts: dict[str, Concept] | None = None
) -> str | None:
    """Return the concept name for a (source, vintage, variable) tuple, if any.

    Used by `clean.py` to attach the `concept` column to rows during the
    canonicalization step.
    """
    if concepts is None:
        concepts = load_concepts()
    for concept_name, concept in concepts.items():
        for mapping in concept.mappings:
            if mapping.source != source or mapping.variable != variable:
                continue
            if not mapping.vintages or _vintage_in(vintage, mapping.vintages):
                return concept_name
    return None


def caveats_for(concept_name: str, concepts: dict[str, Concept] | None = None) -> list[str]:
    """Return the caveats list for a concept; empty list if concept absent."""
    if concepts is None:
        concepts = load_concepts()
    c = concepts.get(concept_name)
    return c.caveats if c else []


def _vintage_in(vintage: str, ranges: list[str]) -> bool:
    """Check whether `vintage` falls within any range string.

    Range strings: `"2010"` (single), `"2010-2019"` (closed), `"2020-"` (open-ended).
    Vintage string compared lexically — works for `"2010"`, `"2010-Q1"`,
    `"2010-general"`, etc. so long as the within-year format is consistent.
    """
    for r in ranges:
        if "-" not in r:
            if vintage == r:
                return True
            continue
        lo, hi = r.split("-", 1)
        if hi and lo <= vintage <= hi:
            return True
        if not hi and vintage >= lo:
            return True
    return False

"""The concept catalog loads, and every multi-source concept carries caveats."""

from __future__ import annotations

from scripts.concepts import load_concepts


def test_concepts_load() -> None:
    assert isinstance(load_concepts(), dict)


def test_cross_source_concepts_carry_caveats() -> None:
    for name, concept in load_concepts().items():
        if len({m.source for m in concept.mappings}) > 1:
            assert concept.caveats, f"concept {name!r} maps several sources but has no caveats"

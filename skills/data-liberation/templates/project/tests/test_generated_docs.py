"""Numbers quoted in README.md and AGENTS.md are generated, and must be current.

`python -m scripts.pipeline audit` rewrites the blocks between
`<!-- BEGIN generated:headline -->` and `<!-- END generated -->` from
`data/audit/headline.json`. This test fails when a block was hand-edited or the
docs were not refreshed after a run.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from scripts.audit import extract_block, headline_numbers, render_generated
from scripts.config import GENERATED_DOCS, HEADLINE_JSON, PROCESSED_CSV


def _headline() -> dict | None:
    return json.loads(HEADLINE_JSON.read_text()) if HEADLINE_JSON.exists() else None


@pytest.mark.parametrize("doc", GENERATED_DOCS, ids=lambda p: p.name)
def test_generated_block_is_current(doc) -> None:
    if not doc.exists():
        pytest.skip(f"{doc.name} not present")
    block = extract_block(doc.read_text())
    assert block is not None, f"{doc.name} lost its generated:headline markers"
    assert block == render_generated(_headline()), (
        f"{doc.name}: generated numbers are stale; run `uv run python -m scripts.pipeline audit`"
    )


def test_headline_matches_the_processed_data() -> None:
    headline = _headline()
    if headline is None or not PROCESSED_CSV.exists():
        pytest.skip("no processed data and headline to compare")
    df = pd.read_csv(PROCESSED_CSV, dtype=str, keep_default_na=False, na_values=[""])
    fresh = headline_numbers(df)
    assert {k: headline[k] for k in fresh} == fresh, "headline.json is stale; re-run audit"

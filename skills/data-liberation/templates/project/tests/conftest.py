"""Shared pytest fixtures.

`good_frame` matches the placeholder schema in `scripts/schema.py`; edit it when you
replace `observation_id` with the real key and measurement columns.
"""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.config import ROOT


@pytest.fixture
def fixtures_dir():
    """`tests/fixtures/`: small real artifacts, one or more per parser."""
    return ROOT / "tests" / "fixtures"


@pytest.fixture
def good_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source": ["example", "example", "example"],
            "vintage": ["2023", "2023", "2024"],
            "observation_id": ["a", "b", "c"],
        }
    )

"""Shared pytest fixtures.

Path fixtures point at the on-disk layout from `scripts.config`. The
`good_frame` fixture is a tiny synthetic DataFrame matching the canonical
schema (`scripts.schema.CanonicalLong`); per-parser tests adapt as needed.
"""

from __future__ import annotations

import pandas as pd
import pytest

from scripts.config import (
    DATA_AUDIT,
    DATA_LOOKUPS,
    DATA_ORIGINAL,
    DATA_PROCESSED,
    DOCS,
    ROOT,
)


@pytest.fixture
def root_dir():
    return ROOT


@pytest.fixture
def data_original():
    return DATA_ORIGINAL


@pytest.fixture
def data_processed():
    return DATA_PROCESSED


@pytest.fixture
def data_audit():
    return DATA_AUDIT


@pytest.fixture
def data_lookups():
    return DATA_LOOKUPS


@pytest.fixture
def docs_dir():
    return DOCS


@pytest.fixture
def fixtures_dir():
    """Path to `tests/fixtures/`. Per-parser tests pin paths under this."""
    return ROOT / "tests" / "fixtures"


@pytest.fixture
def good_frame() -> pd.DataFrame:
    """A minimal frame matching the default canonical schema.

    Edit when extending `scripts.schema.CanonicalLong`. Per-parser tests
    typically build richer frames; this is just the universal floor.
    """
    return pd.DataFrame(
        {
            "source": ["example", "example", "example"],
            "vintage": ["2023", "2023", "2024"],
            "observation_id": ["a", "b", "c"],
            "concept": ["temperature", "temperature", None],
        }
    )

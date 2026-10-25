"""Baseline tests for the canonical schema.

Four checks: (1) a good frame validates, (2) a frame missing a required
column raises, (3) `strict=True` rejects an unknown extra column, (4)
dtype coercion works. These catch schema drift early, before bad data
reaches downstream consumers.

Per-parser tests live in `tests/test_<source>_<vintage>.py` and are
added as parsers are written.
"""

from __future__ import annotations

import pandas as pd
import pandera as pa
import pytest

from scripts.schema import CanonicalLong, normalize_long

# Pandera raises `SchemaError` for a single failure and `SchemaErrors` for
# multiple; both signal that validation rejected the frame.
_SCHEMA_FAILURES = (pa.errors.SchemaError, pa.errors.SchemaErrors)


def test_good_frame_validates(good_frame: pd.DataFrame) -> None:
    """A frame matching the canonical schema passes `normalize_long`."""
    out = normalize_long(good_frame)
    assert len(out) == len(good_frame)
    assert set(out.columns) == set(good_frame.columns)


def test_missing_required_column_raises(good_frame: pd.DataFrame) -> None:
    """Dropping `source` (a required column) must fail normalization."""
    bad = good_frame.drop(columns=["source"])
    with pytest.raises((ValueError, *_SCHEMA_FAILURES)):
        normalize_long(bad)


def test_strict_rejects_extra_column_when_passed_to_validate(good_frame: pd.DataFrame) -> None:
    """`strict=True` rejects unknown columns when validated directly.

    `normalize_long` defends against this by keeping only LONG_COLUMNS, so
    extra columns are silently dropped (a reasonable convenience for parsers
    that produce working columns). Direct validation against the schema
    rejects them — which is what catches drift in schemas Claude/the user
    might extend later.
    """
    bad = good_frame.assign(unexpected_column="oops")
    with pytest.raises(_SCHEMA_FAILURES):
        CanonicalLong.validate(bad)


def test_vintage_coerced_to_string() -> None:
    """`coerce=True` lets us pass int vintage and get string back.

    Years arrive from parsers as ints, strings, even floats. The schema
    coerces; downstream consumers can rely on `vintage` being a string.
    """
    df = pd.DataFrame(
        {
            "source": ["example"],
            "vintage": [2024],  # int — should coerce
            "observation_id": ["a"],
            "concept": [None],
        }
    )
    out = normalize_long(df)
    # Pandera may coerce to either `object` or pandas `StringDtype`; both
    # count as "string-like" — the value is what the parser contract
    # guarantees.
    assert pd.api.types.is_string_dtype(out["vintage"])
    assert out["vintage"].iloc[0] == "2024"

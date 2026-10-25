"""The schema contract: valid frames pass, drift fails, bad rows are set aside.

Per-parser tests live in `tests/test_<source>_<era>.py`, one per parser, each
checking a printed total from a real fixture.
"""

from __future__ import annotations

import pandas as pd
import pandera.pandas as pa
import pytest

from scripts.schema import CanonicalLong, dedupe, normalize_long, split_valid

SCHEMA_FAILURES = (pa.errors.SchemaError, pa.errors.SchemaErrors)


def test_good_frame_validates(good_frame: pd.DataFrame) -> None:
    out = normalize_long(good_frame)
    assert len(out) == len(good_frame)


def test_missing_required_column_raises(good_frame: pd.DataFrame) -> None:
    with pytest.raises((ValueError, *SCHEMA_FAILURES)):
        normalize_long(good_frame.drop(columns=["source"]))


def test_strict_rejects_unknown_column(good_frame: pd.DataFrame) -> None:
    with pytest.raises(SCHEMA_FAILURES):
        CanonicalLong.validate(good_frame.assign(unexpected="oops"))


def test_vintage_is_coerced_to_string() -> None:
    df = pd.DataFrame({"source": ["example"], "vintage": [2024], "observation_id": ["a"]})
    out = normalize_long(df)
    assert pd.api.types.is_string_dtype(out["vintage"])
    assert out["vintage"].iloc[0] == "2024"


def test_dedupe_keeps_the_last_reading(good_frame: pd.DataFrame) -> None:
    repeated = pd.concat([good_frame, good_frame.iloc[[0]]], ignore_index=True)
    out, dropped = dedupe(repeated)
    assert dropped == 1
    assert len(out) == len(good_frame)
    assert out.index[-1] == 3  # the later copy survived


def test_split_valid_routes_bad_rows_to_rejects(good_frame: pd.DataFrame) -> None:
    bad = good_frame.copy()
    bad.loc[1, "observation_id"] = None
    valid, rejected = split_valid(bad)
    assert len(valid) == 2
    assert len(rejected) == 1
    assert "observation_id" in rejected["reject_reason"].iloc[0]

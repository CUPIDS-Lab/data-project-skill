"""Recounts replace whole groups; corrections apply only while they still match."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from scripts import amendments
from scripts.amendments import AmendmentError, apply_corrections, merge_supplements


@pytest.fixture
def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "_artifact": ["base", "base", "base", "recount"],
            "source": "s",
            "vintage": "2023",
            "observation_id": ["x-a", "x-b", "y-a", "x-a"],
            "contest": ["x", "x", "y", "x"],
        }
    )


def test_supplement_replaces_its_groups_whole(frame, monkeypatch) -> None:
    monkeypatch.setattr(amendments, "SUPPLEMENTS", {"recount": "base"})
    monkeypatch.setattr(amendments, "SUPPLEMENT_GROUP", ["contest"])
    merged, replaced = merge_supplements(frame)
    assert replaced == 2  # both base rows of contest x
    assert sorted(merged["_artifact"] + ":" + merged["observation_id"]) == [
        "base:y-a",
        "recount:x-a",
    ]


def test_supplement_group_missing_from_base_fails(frame, monkeypatch) -> None:
    monkeypatch.setattr(amendments, "SUPPLEMENTS", {"recount": "base"})
    monkeypatch.setattr(amendments, "SUPPLEMENT_GROUP", ["contest"])
    frame.loc[3, "contest"] = "z"
    with pytest.raises(AmendmentError, match="no exact match"):
        merge_supplements(frame)


def _corrections(tmp_path, monkeypatch, rows) -> None:
    path = tmp_path / "corrections.csv"
    pd.DataFrame(rows, columns=amendments.CORRECTION_COLUMNS).to_csv(path, index=False)
    monkeypatch.setattr(amendments, "CORRECTIONS_CSV", path)


def test_correction_applies_while_it_matches(frame, tmp_path, monkeypatch) -> None:
    key = json.dumps({"observation_id": "y-a"})
    _corrections(tmp_path, monkeypatch, [[key, "set", "contest", "y", "y2", "url", "typo"]])
    fixed, dropped, applied = apply_corrections(frame)
    assert dropped == 0 and len(applied) == 1
    assert fixed.loc[fixed["observation_id"] == "y-a", "contest"].item() == "y2"


def test_stale_correction_fails_the_build(frame, tmp_path, monkeypatch) -> None:
    key = json.dumps({"observation_id": "y-a"})
    # The published value is no longer what the correction expects: upstream fixed it.
    _corrections(tmp_path, monkeypatch, [[key, "set", "contest", "old", "y2", "url", ""]])
    with pytest.raises(AmendmentError, match="source changed"):
        apply_corrections(frame)
    gone = json.dumps({"observation_id": "nope"})
    _corrections(tmp_path, monkeypatch, [[gone, "drop", "", "", "", "url", ""]])
    with pytest.raises(AmendmentError, match="matches no row"):
        apply_corrections(frame)

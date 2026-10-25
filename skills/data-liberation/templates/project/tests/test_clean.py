"""The build refuses to produce wrong data quietly.

These tests drive `scripts.clean.build` with a stand-in parser, so they check the
machinery (dedup before validation, the reject file, conservation, loud failure on
empty or degenerate output, deterministic provenance) without any real source.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from scripts.clean import build, check_frame
from scripts.runlog import ErrorLog
from scripts.source import Artifact


def _artifacts(tmp_path: Path, n: int = 2) -> list[Artifact]:
    arts = []
    for i in range(n):
        path = tmp_path / f"{2020 + i}" / "file.csv"
        path.parent.mkdir(parents=True)
        path.write_text(f"original {i}\n")
        arts.append(Artifact("example", str(2020 + i), f"https://example.org/{i}.csv", path))
    return arts


def _parser(frames: dict[str, pd.DataFrame]) -> SimpleNamespace:
    return SimpleNamespace(
        __name__="tests.fake_parser",
        METHOD="text_layer",
        TOOLS=("pandas",),
        parse=lambda path: frames[path.parent.name].copy(),
    )


def _build(tmp_path: Path, frames: dict[str, pd.DataFrame]):
    arts = _artifacts(tmp_path, len(frames))
    module = _parser(frames)
    errors = ErrorLog(tmp_path / "errors.json", "clean")
    return build(arts, lambda art: module, {}, errors, show_progress=False)


def test_ledger_balances_with_duplicates_and_rejects(tmp_path: Path) -> None:
    frames = {
        "2020": pd.DataFrame({"observation_id": ["a", "a", "b"]}),  # one duplicate
        "2021": pd.DataFrame({"observation_id": ["c", None]}),  # one row with an empty key
    }
    result = _build(tmp_path, frames)
    ledger = result.ledger
    assert asdict(ledger) == {"parsed": 5, "duplicates_dropped": 1, "rejected": 1, "written": 3}
    assert ledger.balanced()
    assert result.rejected["artifact"].str.endswith("2021/file.csv").all()
    prov = result.provenance.set_index("vintage")
    assert prov.loc["2021", "extraction_quality"] == "caveats"
    assert prov.loc["2020", "extraction_quality"] == "clean"


def test_empty_extraction_is_an_error_not_a_silent_gap(tmp_path: Path) -> None:
    frames = {
        "2020": pd.DataFrame({"observation_id": ["a"]}),
        "2021": pd.DataFrame({"observation_id": pd.Series([], dtype=str)}),
    }
    result = _build(tmp_path, frames)
    assert len(result.errors) == 1
    assert "zero rows" in result.errors[0]["message"]
    assert result.provenance.set_index("vintage").loc["2021", "extraction_quality"] == "degraded"


def test_all_empty_keys_are_degenerate() -> None:
    with pytest.raises(RuntimeError, match="empty key"):
        check_frame(pd.DataFrame({"source": ["x"], "vintage": ["2020"], "observation_id": [None]}))


def test_provenance_is_deterministic(tmp_path: Path) -> None:
    frames = {"2020": pd.DataFrame({"observation_id": ["b", "a"]})}
    first = _build(tmp_path / "one", frames).provenance.drop(columns=["artifact"])
    second = _build(tmp_path / "two", frames).provenance.drop(columns=["artifact"])
    pd.testing.assert_frame_equal(first, second)
    assert first.loc[0, "extraction_method"] == "text_layer"
    assert first.loc[0, "tool_versions"].startswith("pandas==")


def test_unknown_extraction_method_fails_the_artifact(tmp_path: Path) -> None:
    arts = _artifacts(tmp_path, 1)
    module = _parser({"2020": pd.DataFrame({"observation_id": ["a"]})})
    module.METHOD = "pdfplumber"  # a tool, not a method: must be text_layer etc.
    errors = ErrorLog(tmp_path / "errors.json", "clean")
    result = build(arts, lambda art: module, {}, errors, show_progress=False)
    assert result.data.empty
    assert "extraction_method" in result.errors[0]["message"]

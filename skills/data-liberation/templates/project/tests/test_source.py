"""Vintage keys come from the file's own name, never from where it was published."""

from __future__ import annotations

import pytest

from scripts.source import vintage_from_filename


@pytest.mark.parametrize(
    ("name", "vintage"),
    [
        ("annual-report-2024.pdf", "2024"),
        ("permits_2025Q4.csv", "2025Q4"),
        ("sov-2024-11.xlsx", "2024-11"),
        ("report_2019_2020.pdf", "2020"),  # the last year names the period covered
        ("readme.txt", None),
    ],
)
def test_vintage_from_filename(name: str, vintage: str | None) -> None:
    assert vintage_from_filename(name) == vintage


def test_publish_directory_is_ignored() -> None:
    # Q4 files are often posted in the next year's folder.
    assert vintage_from_filename("https://example.gov/2026-02/data-2025Q4.csv") == "2025Q4"

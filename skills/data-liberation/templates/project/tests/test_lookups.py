"""Controlled vocabularies: lookup files, the data dictionary and the data agree.

Convention: `data/lookups/vocab_<column>.csv` has a `value` column listing every
allowed value of `<column>`. The data dictionary's `<column>` entry lists the same
values, in backticks, on its **Vocabulary / units:** line. Every observed value in
the processed data must be in the list.
"""

from __future__ import annotations

import re

import pandas as pd
import pytest

from scripts.config import DATA_LOOKUPS, DOCS, PROCESSED_CSV

VOCAB_FILES = sorted(DATA_LOOKUPS.glob("vocab_*.csv"))
DICTIONARY = DOCS / "data-dictionary.md"


def _dictionary_values(column: str) -> set[str] | None:
    text = DICTIONARY.read_text()
    section = re.search(rf"^## `{re.escape(column)}`\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section:
        return None
    line = re.search(r"\*\*Vocabulary / units:\*\*(.*)", section.group(1))
    return set(re.findall(r"`([^`]+)`", line.group(1))) if line else set()


@pytest.mark.parametrize("vocab", VOCAB_FILES, ids=lambda p: p.stem)
def test_vocabulary_matches_dictionary_and_data(vocab) -> None:
    column = vocab.stem.removeprefix("vocab_")
    allowed = set(pd.read_csv(vocab, dtype=str)["value"].dropna())
    documented = _dictionary_values(column)
    assert documented is not None, f"data-dictionary.md has no entry for `{column}`"
    assert documented == allowed, f"`{column}`: dictionary and {vocab.name} disagree"
    if PROCESSED_CSV.exists():
        observed = set(pd.read_csv(PROCESSED_CSV, dtype=str, usecols=[column])[column].dropna())
        assert observed <= allowed, (
            f"`{column}` has values outside {vocab.name}: {observed - allowed}"
        )

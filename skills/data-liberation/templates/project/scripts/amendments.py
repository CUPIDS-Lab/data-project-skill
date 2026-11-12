"""Amendments: recounts, amended files, and errors in an official publication.

Generated when a source publishes supplements (a recount, an amended file) or when a
published figure is known to be wrong. Both are kept out of the parsers so the
originals stay what the publisher released and every change is reviewable.

* **Supplements.** A recount or amended file is fetched as its own original and
  parsed like any other artifact. `SUPPLEMENTS` says which base artifact it amends and
  `SUPPLEMENT_GROUP` names the unit it replaces (a contest, an office): every group the
  supplement reports replaces that group of the base artifact whole. A supplement
  group with no exact match in its base fails the build, because it means the two
  files disagree about what exists, not just about the numbers.
* **Corrections.** Errors in the publication itself go in the reviewed
  `data/lookups/corrections.csv`, one row per fix: the natural key of the row, the
  action (`set` a column, or `drop` the row), the value as published, the corrected
  value, the evidence and a note. A correction that no longer matches the data
  (the row is gone, or its published value changed upstream) fails the build: the
  publisher has probably fixed it, so review and remove the correction.

`clean` calls `apply()` after parsing and before deduplication; replaced and dropped
rows are counted in the ledger as `amended_out`. The corrections applied are written
to `data/audit/corrections.json` so `reconcile` can report those keys as `corrected`.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from scripts.config import DATA_AUDIT, DATA_LOOKUPS
from scripts.schema import KEY_COLUMNS

CORRECTIONS_CSV = DATA_LOOKUPS / "corrections.csv"
CORRECTIONS_JSON = DATA_AUDIT / "corrections.json"
CORRECTION_COLUMNS = ["key", "action", "column", "published", "corrected", "evidence", "note"]

# Supplement artifact (path relative to data/original/) → the base artifact it amends,
# e.g. {"example_source/2023/recount.csv": "example_source/2023/results.csv"}.
SUPPLEMENTS: dict[str, str] = {}
# The columns that define one replaceable unit, e.g. ["contest"].
SUPPLEMENT_GROUP: list[str] = []


class AmendmentError(RuntimeError):
    """A supplement or correction no longer lines up with the data. Fails the build."""


def merge_supplements(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Replace each base group a supplement reports. Returns (frame, rows replaced)."""
    replaced = 0
    for supp, base in SUPPLEMENTS.items():
        supp_rows = frame[frame["_artifact"] == supp]
        if supp_rows.empty:
            continue  # the supplement isn't fetched yet; the base stands
        if not SUPPLEMENT_GROUP:
            raise AmendmentError("SUPPLEMENTS is set but SUPPLEMENT_GROUP is empty")
        base_mask = frame["_artifact"] == base
        base_groups = frame.loc[base_mask, SUPPLEMENT_GROUP].drop_duplicates()
        supp_groups = supp_rows[SUPPLEMENT_GROUP].drop_duplicates()
        unmatched = supp_groups.merge(base_groups, how="left", indicator=True)
        unmatched = unmatched[unmatched["_merge"] == "left_only"]
        if not unmatched.empty:
            raise AmendmentError(
                f"{supp}: {len(unmatched)} group(s) have no exact match in {base}: "
                f"{unmatched[SUPPLEMENT_GROUP].to_dict('records')[:5]}"
            )
        in_supp = (
            frame[SUPPLEMENT_GROUP].apply(tuple, axis=1).isin(supp_groups.apply(tuple, axis=1))
        )
        drop = base_mask & in_supp
        replaced += int(drop.sum())
        frame = frame[~drop]
    return frame, replaced


def load_corrections() -> pd.DataFrame:
    if not CORRECTIONS_CSV.exists():
        return pd.DataFrame(columns=CORRECTION_COLUMNS)
    corrections = pd.read_csv(CORRECTIONS_CSV, dtype=str, keep_default_na=False)
    missing = [c for c in CORRECTION_COLUMNS if c not in corrections.columns]
    if missing:
        raise AmendmentError(f"{CORRECTIONS_CSV.name} lacks columns {missing}")
    return corrections


def apply_corrections(frame: pd.DataFrame) -> tuple[pd.DataFrame, int, list[dict[str, Any]]]:
    """Apply each reviewed correction. Returns (frame, rows dropped, corrections applied)."""
    dropped, applied = 0, []
    for i, c in load_corrections().iterrows():
        key = json.loads(c["key"])  # {"vintage": "2024", "precinct": "...", ...}
        unknown = [k for k in key if k not in KEY_COLUMNS]
        if unknown:
            raise AmendmentError(f"correction {i + 1}: {unknown} are not key columns")
        mask = pd.Series(True, index=frame.index)
        for col, val in key.items():
            mask &= frame[col].astype(str) == str(val)
        if not mask.any():
            raise AmendmentError(
                f"correction {i + 1} matches no row ({key}); the publisher may have fixed "
                "it. Review it and remove it from data/lookups/corrections.csv."
            )
        if c["action"] == "drop":
            dropped += int(mask.sum())
            frame = frame[~mask]
        elif c["action"] == "set":
            current = frame.loc[mask, c["column"]].astype(str)
            if (current != c["published"]).any():
                raise AmendmentError(
                    f"correction {i + 1}: {c['column']} is {sorted(set(current))}, not the "
                    f"published {c['published']!r}; the source changed. Review the correction."
                )
            frame.loc[mask, c["column"]] = c["corrected"]
        else:
            raise AmendmentError(f"correction {i + 1}: action must be 'set' or 'drop'")
        applied.append({"key": key, "action": c["action"], "column": c["column"]})
    return frame, dropped, applied


def apply(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Merge supplements, then apply corrections. Returns (frame, rows amended out)."""
    frame, replaced = merge_supplements(frame)
    frame, dropped, applied = apply_corrections(frame)
    CORRECTIONS_JSON.write_text(json.dumps(applied, indent=2, sort_keys=True) + "\n")
    return frame, replaced + dropped


def corrected_keys() -> list[dict[str, Any]]:
    """The keys the last `clean` corrected, for reconcilers to label as `corrected`."""
    try:
        return [c["key"] for c in json.loads(CORRECTIONS_JSON.read_text())]
    except FileNotFoundError:
        return []

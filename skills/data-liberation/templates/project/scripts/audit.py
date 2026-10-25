"""Audit the processed deliverable.

Three responsibilities, all written to `data/audit/` or `docs/`:

1. `audit_all()` — Markdown report (`data/audit/summary-<ts>.md`) covering
   source coverage, null rates per column, distinct values for low-cardinality
   columns, and any empty-source warnings.
2. `variables_report()` — auto-generated `docs/variables.md` + `docs/variables.csv`
   describing each column's dtype, distinct count, null rate, sample values.
   The mechanical complement to the hand-edited `docs/data-dictionary.md`.
3. `record_extraction_error()` — append a row to `data/audit/extraction_errors.json`
   whenever a `Source.ingest()` call raises. The pipeline's durable-not-fatal
   error sink.

See `references/discovery-and-audit.md` for the patterns this implements.
"""

from __future__ import annotations

import json
import traceback
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import structlog

from scripts.config import DATA_AUDIT, DOCS, PROCESSED_CSV

log = structlog.get_logger()

VARIABLES_MD = DOCS / "variables.md"
VARIABLES_CSV = DOCS / "variables.csv"
EXTRACTION_ERRORS_JSON = DATA_AUDIT / "extraction_errors.json"


# ─── Markdown summary ────────────────────────────────────────────────────────


def audit_all() -> int:
    """Generate `data/audit/summary-<ts>.md` and `docs/variables.{md,csv}`."""
    if not PROCESSED_CSV.exists():
        log.error("audit_no_processed_csv", path=str(PROCESSED_CSV))
        return 1

    df = pd.read_csv(PROCESSED_CSV, dtype=str)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = DATA_AUDIT / f"summary-{ts}.md"

    lines: list[str] = [f"# Audit Summary — {ts}", "", f"Rows: **{len(df):,}**", ""]
    lines.extend(_section_source_coverage(df))
    lines.extend(_section_null_rates(df))
    lines.extend(_section_low_cardinality(df))
    lines.extend(_section_empty_sources(df))
    lines.extend(_section_extraction_errors())

    out.write_text("\n".join(lines))
    log.info("wrote_audit", path=str(out), rows=len(df))

    variables_report(PROCESSED_CSV, VARIABLES_MD, VARIABLES_CSV)
    return 0


def _section_source_coverage(df: pd.DataFrame) -> list[str]:
    if not {"source", "vintage"}.issubset(df.columns):
        return [
            "## Source coverage",
            "",
            "_`source`/`vintage` columns missing — schema drift?_",
            "",
        ]
    coverage = (
        df.groupby(["source", "vintage"], dropna=False)
        .size()
        .rename("rows")
        .reset_index()
        .sort_values(["source", "vintage"])
    )
    return ["## Source coverage", "", coverage.to_markdown(index=False), ""]


def _section_null_rates(df: pd.DataFrame) -> list[str]:
    null_rates = df.isna().mean().rename("null_rate").reset_index()
    null_rates.columns = ["column", "null_rate"]
    return [
        "## Null rates per column",
        "",
        null_rates.to_markdown(index=False, floatfmt=".3f"),
        "",
    ]


def _section_low_cardinality(df: pd.DataFrame) -> list[str]:
    lines = ["## Distinct values for low-cardinality columns", ""]
    any_found = False
    for col in df.columns:
        n = df[col].nunique(dropna=True)
        if 1 <= n <= 30:
            vals = sorted(str(v) for v in df[col].dropna().unique().tolist())
            lines.append(f"- `{col}` ({n} distinct): {vals}")
            any_found = True
    if not any_found:
        lines.append("_(no columns with between 1 and 30 distinct values)_")
    lines.append("")
    return lines


def _section_empty_sources(df: pd.DataFrame) -> list[str]:
    if not {"source", "vintage"}.issubset(df.columns):
        return []
    coverage = df.groupby(["source", "vintage"], dropna=False).size().rename("rows").reset_index()
    empty = coverage[coverage["rows"] == 0]
    if empty.empty:
        return []
    return ["## ⚠️ Empty sources", "", empty.to_markdown(index=False), ""]


def _section_extraction_errors() -> list[str]:
    if not EXTRACTION_ERRORS_JSON.exists():
        return []
    try:
        errors = json.loads(EXTRACTION_ERRORS_JSON.read_text())
    except json.JSONDecodeError:
        return [
            "## ⚠️ Extraction errors",
            "",
            "_(extraction_errors.json present but unreadable)_",
            "",
        ]
    if not errors:
        return []
    lines = [f"## ⚠️ Extraction errors ({len(errors)})", ""]
    for e in errors[-25:]:
        lines.append(
            f"- **{e.get('source', '?')}** {e.get('artifact_url', '')} — "
            f"`{e.get('error_type', '?')}: {e.get('error_message', '')}`"
        )
    lines.append("")
    return lines


# ─── Variables report ────────────────────────────────────────────────────────


def variables_report(processed_csv: Path, out_md: Path, out_csv: Path) -> None:
    """Emit `docs/variables.md` and `docs/variables.csv`.

    Auto-generated; do not hand-edit. The hand-edited counterpart is
    `docs/data-dictionary.md`. If the dictionary says a column is `Int64`
    but this report says `object`, the dictionary (or the parser) is wrong.
    """
    df = pd.read_csv(processed_csv)
    rows: list[dict[str, Any]] = []
    for col in df.columns:
        s = df[col]
        sample = s.dropna().unique()[:5].tolist()
        is_numeric = pd.api.types.is_numeric_dtype(s)
        rows.append(
            {
                "column": col,
                "dtype": str(s.dtype),
                "distinct": int(s.nunique(dropna=True)),
                "null_rate": float(s.isna().mean()),
                "min": s.min() if is_numeric else "",
                "max": s.max() if is_numeric else "",
                "sample_values": ", ".join(str(v) for v in sample),
            }
        )
    rep = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    rep.to_csv(out_csv, index=False)
    out_md.write_text(
        "# Variables (auto-generated)\n\n"
        "_Generated by `scripts.audit.variables_report`; do not hand-edit. "
        "See `docs/data-dictionary.md` for the human-authored counterpart._\n\n"
        + rep.to_markdown(index=False, floatfmt=".3f")
        + "\n"
    )
    log.info("wrote_variables_report", md=str(out_md), csv=str(out_csv), cols=len(rep))


# ─── Durable error sink ──────────────────────────────────────────────────────


def record_extraction_error(*, source: str, artifact: Any, error: Exception) -> None:
    """Append one record to `data/audit/extraction_errors.json`.

    Called from `clean.py` when a `Source.ingest()` call raises. The
    pipeline continues; the failure is visible in the next audit and
    the JSON is durable for re-investigation.
    """
    EXTRACTION_ERRORS_JSON.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if EXTRACTION_ERRORS_JSON.exists():
        try:
            existing = json.loads(EXTRACTION_ERRORS_JSON.read_text())
            if not isinstance(existing, list):
                existing = []
        except json.JSONDecodeError:
            existing = []

    if is_dataclass(artifact):
        art_dict = asdict(artifact)
    else:
        art_dict = {"repr": repr(artifact)}

    record = {
        "recorded_at": datetime.now(UTC).isoformat(),
        "source": source,
        "artifact_url": art_dict.get("url", ""),
        "artifact_local_path": str(art_dict.get("local_path", "")),
        "artifact_vintage": art_dict.get("vintage", ""),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
    }
    existing.append(record)
    EXTRACTION_ERRORS_JSON.write_text(json.dumps(existing, indent=2, default=str))
    log.warning(
        "extraction_error",
        source=source,
        url=record["artifact_url"],
        error_type=record["error_type"],
        error_message=record["error_message"],
    )

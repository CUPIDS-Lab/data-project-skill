"""Clean: parse every fetched artifact, deduplicate, validate, check, write.

Stages and the row ledger they keep:

    parsed ── dedupe ──► duplicates_dropped
           └─ validate ─► rejected (data/audit/rejected.csv, with a reason)
                       └─► written (data/processed/<name>.csv)

Conservation: `parsed == duplicates_dropped + rejected + written`, or the build
fails. A parser that raises, returns no rows, or returns rows whose key columns are
all empty is recorded in `data/audit/extraction_errors.json` (a fresh log each run)
and the other artifacts carry on. If nothing at all survives, nothing is written:
the previous good outputs stay in place and the command exits non-zero. No step
ever substitutes synthetic, sample or cached rows for a failed artifact.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from types import ModuleType
from typing import Any

import pandas as pd

from scripts import provenance, source
from scripts.config import (
    EXTRACTION_ERRORS_JSON,
    MANIFEST_JSON,
    PROCESSED_CSV,
    PROCESSED_PARQUET,
    PROVENANCE_CSV,
    REJECTED_CSV,
    RUN_JSON,
    SOURCE_LICENSE,
)
from scripts.runlog import ErrorLog, progress
from scripts.schema import KEY_COLUMNS, LONG_COLUMNS, dedupe, split_valid


class ExtractionError(RuntimeError):
    """A parser produced output that must not reach the dataset."""


class ConservationError(RuntimeError):
    """Rows were lost between stages without being counted."""


@dataclass
class Ledger:
    parsed: int = 0
    duplicates_dropped: int = 0
    rejected: int = 0
    written: int = 0

    def balanced(self) -> bool:
        return self.parsed == self.duplicates_dropped + self.rejected + self.written


@dataclass
class CleanResult:
    data: pd.DataFrame
    rejected: pd.DataFrame
    provenance: pd.DataFrame
    errors: list[dict[str, Any]] = field(default_factory=list)
    ledger: Ledger = field(default_factory=Ledger)


def check_frame(frame: pd.DataFrame) -> None:
    """Fail loudly on empty or degenerate parser output."""
    if frame.empty:
        raise ExtractionError("parser returned zero rows")
    missing = [c for c in LONG_COLUMNS if c not in frame.columns]
    if missing:
        raise ExtractionError(f"parser output lacks columns {missing}")
    domain_keys = [c for c in KEY_COLUMNS if c not in ("source", "vintage")]
    if domain_keys and frame[domain_keys].isna().all(axis=None):
        raise ExtractionError(f"every row has an empty key ({', '.join(domain_keys)})")


def build(
    artifacts: Iterable[source.Artifact],
    route: Callable[[source.Artifact], ModuleType],
    manifest: dict[str, dict[str, Any]],
    errors: ErrorLog,
    *,
    show_progress: bool = True,
) -> CleanResult:
    """Parse, deduplicate and validate. Pure apart from reading the originals."""
    arts = list(artifacts)
    frames: list[pd.DataFrame] = []
    prov: dict[str, dict[str, Any]] = {}
    ledger = Ledger()

    for i, art in enumerate(arts, 1):
        progress(i, len(arts), f"clean {art.rel}", enabled=show_progress)
        entry = dict(manifest.get(art.rel, {}))
        if not art.local_path.exists():
            errors.record(art, "not fetched yet: run `python -m scripts.pipeline fetch`")
            continue
        actual = provenance.sha256_file(art.local_path)
        if entry.get("sha256") and entry["sha256"] != actual:
            errors.record(art, "original changed since it was fetched (sha256 mismatch)")
        entry["sha256"] = actual
        entry.setdefault("size_bytes", art.local_path.stat().st_size)
        module = None
        try:
            module = route(art)
            meta = provenance.parser_metadata(module)
            frame = module.parse(art.local_path).assign(source=art.source, vintage=art.vintage)
            check_frame(frame)
        except Exception as exc:  # noqa: BLE001 — recorded, not fatal
            errors.record(art, exc)
            prov[art.rel] = provenance.row(
                art,
                entry,
                parser_module=getattr(module, "__name__", ""),
                extraction_quality="degraded",
                extraction_notes=f"parse failed: {type(exc).__name__}: {exc}",
                source_license=SOURCE_LICENSE,
            )
            continue
        frames.append(frame.assign(_artifact=art.rel))
        ledger.parsed += len(frame)
        prov[art.rel] = provenance.row(
            art, entry, rows_parsed=len(frame), source_license=SOURCE_LICENSE, **meta
        )

    if frames:
        combined = pd.concat(frames, ignore_index=True)
    else:
        combined = pd.DataFrame(columns=[*LONG_COLUMNS, "_artifact"])
    artifact_of = combined["_artifact"]

    deduped, ledger.duplicates_dropped = dedupe(combined)
    valid, rejected = split_valid(deduped)
    ledger.rejected, ledger.written = len(rejected), len(valid)

    out_counts = artifact_of.loc[valid.index].value_counts()
    rej_counts = artifact_of.loc[rejected.index].value_counts()
    for rel, p in prov.items():
        if p["extraction_quality"] == "degraded":
            continue
        p["rows_out"] = int(out_counts.get(rel, 0))
        p["rows_rejected"] = int(rej_counts.get(rel, 0))
        if p["rows_rejected"] and p["extraction_quality"] == "clean":
            p["extraction_quality"] = "caveats"
            note = f"{p['rows_rejected']} rows rejected (see data/audit/rejected.csv)"
            p["extraction_notes"] = "; ".join(x for x in (p["extraction_notes"], note) if x)

    rejected = rejected.assign(artifact=artifact_of.loc[rejected.index].values)
    prov_df = pd.DataFrame(list(prov.values()), columns=provenance.PROVENANCE_COLUMNS)
    return CleanResult(
        data=valid.sort_values(KEY_COLUMNS, kind="stable").reset_index(drop=True),
        rejected=rejected.drop(columns=["_artifact"], errors="ignore"),
        provenance=prov_df.sort_values(["source", "vintage", "artifact"]).reset_index(drop=True),
        errors=errors.records,
        ledger=ledger,
    )


def load_manifest() -> dict[str, dict[str, Any]]:
    try:
        return json.loads(MANIFEST_JSON.read_text())
    except FileNotFoundError:
        return {}


def clean_all(*, strict: bool = False, show_progress: bool = True) -> int:
    """Run `build` on the configured source and write the outputs. Exit codes:
    0 ok · 1 errors or rejects under --strict · 2 nothing to write · 3 rows lost."""
    started = datetime.now(UTC).isoformat()
    errors = ErrorLog(EXTRACTION_ERRORS_JSON, "clean").start()
    arts = source.artifacts()
    if not arts:
        print("No artifacts configured: list them in scripts/source.py.", file=sys.stderr)
        errors.write()
        return 2

    result = build(arts, source.parser_for, load_manifest(), errors, show_progress=show_progress)
    errors.write()
    ledger = result.ledger
    RUN_JSON.write_text(
        json.dumps(
            {"clean": {"started_at": started, "finished_at": datetime.now(UTC).isoformat()}}
            | {"ledger": asdict(ledger), "extraction_errors": len(result.errors)},
            indent=2,
        )
        + "\n"
    )
    if not ledger.balanced():
        print(f"FAIL: rows lost between stages: {asdict(ledger)}", file=sys.stderr)
        return 3
    if result.data.empty:
        print(
            "FAIL: no rows survived; previous outputs left untouched. "
            "See data/audit/extraction_errors.json.",
            file=sys.stderr,
        )
        return 2

    result.data.to_csv(PROCESSED_CSV, index=False)
    result.data.to_parquet(PROCESSED_PARQUET, index=False)
    result.provenance.to_csv(PROVENANCE_CSV, index=False)
    REJECTED_CSV.unlink(missing_ok=True)
    if not result.rejected.empty:
        result.rejected.to_csv(REJECTED_CSV, index=False)

    print(
        f"clean: {ledger.parsed:,} parsed, {ledger.duplicates_dropped:,} duplicates dropped, "
        f"{ledger.rejected:,} rejected, {ledger.written:,} written; "
        f"{len(result.errors)} extraction error(s)."
    )
    if strict and (result.errors or ledger.rejected):
        return 1
    return 0

"""Reconcile: check the published table against totals read independently of the parser.

Turn it on whenever the publisher prints totals or subtotals (statements of vote,
financial reports, enrollment counts): set `SOURCE_PRINTS_TOTALS = True` in
`scripts/config.py` and register a reconciler per source in `RECONCILERS` below.
With that flag on, an empty registry fails instead of quietly passing.

**Reconcile at the grain you publish.** A contest × candidate table is checked
contest × candidate, not only per contest or in total: a top-line match can hide a
missing option, a wrong winner or offsetting errors. Read the expected totals
independently of the parser (the file's own Totals rows, printed totals, or a second
library), so a parser bug can't agree with itself.

**Make it able to fail.** `compare_totals` reports a key the source prints but the
processed data lacks as a mismatch (missing data), and a key only in the processed
data as a documented scope difference. A reconciler that compares nothing fails: a
check that matched zero keys proved nothing, which is how a CSV truncated to its
header passed in one project. Add structural checks with `duplicate_keys` and
`mixed_values` (one option type per contest, one unit per measure).

**Known differences are reviewed, not ignored.** `data/lookups/reconcile-exceptions.csv`
lists differences that are understood (`source`, `label`, `reason`, `evidence`,
`remove_when`). A listed mismatch is reported as `excepted`; an exception whose check
now matches, or no longer exists, is reported as `stale` so it gets removed. Keys a
reviewed correction changed (`scripts/amendments.py`) are reported as `corrected`.

Writes `data/audit/reconcile.md` (committed, deterministic) and `reconcile.json`.
Exit code 2 when any check mismatches or a reconciler compared nothing.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Collection, Iterable, Mapping
from dataclasses import asdict, dataclass, field

import pandas as pd

from scripts.config import DATA_LOOKUPS, RECONCILE_JSON, RECONCILE_MD, SOURCE_PRINTS_TOTALS

EXCEPTIONS_CSV = DATA_LOOKUPS / "reconcile-exceptions.csv"
EXCEPTION_COLUMNS = ["source", "label", "reason", "evidence", "remove_when"]
COMPARED = {"match", "mismatch", "excepted", "corrected"}  # statuses that compared values


@dataclass
class Check:
    label: str
    expected: float | int | str | None
    actual: float | int | str | None
    status: str  # match | mismatch | scope | excepted | corrected | stale
    notes: str = ""


@dataclass
class ReconcileResult:
    source: str
    checks: list[Check] = field(default_factory=list)

    @property
    def mismatches(self) -> list[Check]:
        return [c for c in self.checks if c.status == "mismatch"]

    @property
    def compared(self) -> int:
        return sum(c.status in COMPARED for c in self.checks)


def compare_totals(
    expected: Mapping[str, float],
    actual: Mapping[str, float],
    *,
    prefix: str = "",
    tolerance: float = 0.005,
    corrected: Collection[str] = (),
) -> list[Check]:
    """Compare per-key totals (independent vs recomputed) at the published grain.

    A key in `expected` but not `actual` is missing data (mismatch); a key only in
    `actual` is a scope difference. Keys in `corrected` that match are `corrected`.
    """
    checks = []
    for key in sorted(set(expected) | set(actual)):
        e, a = expected.get(key), actual.get(key)
        label = f"{prefix}{key}"
        if a is None:
            checks.append(Check(label, e, a, "mismatch", "missing from the processed data"))
        elif e is None:
            checks.append(Check(label, e, a, "scope", "only in the processed data"))
        elif abs(float(e) - float(a)) > tolerance:
            checks.append(Check(label, e, a, "mismatch"))
        else:
            checks.append(Check(label, e, a, "corrected" if key in corrected else "match"))
    return checks


def duplicate_keys(df: pd.DataFrame, key: Iterable[str], *, label: str = "duplicate keys") -> Check:
    """Structural check: the published key is unique."""
    key = list(key)
    n = int(df.duplicated(key, keep=False).sum())
    return Check(label, 0, n, "match" if n == 0 else "mismatch", f"on {', '.join(key)}")


def mixed_values(
    df: pd.DataFrame, by: Iterable[str], column: str, *, label: str | None = None
) -> Check:
    """Structural check: each group has one value of `column` (e.g. one option type per contest)."""
    by = list(by)
    counts = df.groupby(by, dropna=False)[column].nunique(dropna=False)
    bad = counts[counts > 1]
    notes = f"{len(bad)} group(s), e.g. {list(bad.index[:3])}" if len(bad) else ""
    return Check(
        label or f"one {column} per {'×'.join(by)}",
        0,
        len(bad),
        "match" if bad.empty else "mismatch",
        notes,
    )


def load_exceptions() -> pd.DataFrame:
    if not EXCEPTIONS_CSV.exists():
        return pd.DataFrame(columns=EXCEPTION_COLUMNS)
    exc = pd.read_csv(EXCEPTIONS_CSV, dtype=str, keep_default_na=False)
    missing = [c for c in EXCEPTION_COLUMNS if c not in exc.columns]
    if missing:
        raise ValueError(f"{EXCEPTIONS_CSV.name} lacks columns {missing}")
    return exc


def apply_exceptions(result: ReconcileResult, exceptions: pd.DataFrame) -> None:
    """Mark listed mismatches `excepted`; report exceptions that no longer apply as `stale`."""
    listed = exceptions[exceptions["source"] == result.source]
    by_label = {c.label: c for c in result.checks}
    for _, row in listed.iterrows():
        check = by_label.get(row["label"])
        if check is not None and check.status == "mismatch":
            check.status = "excepted"
            check.notes = f"{row['reason']} (evidence: {row['evidence']})"
        else:
            result.checks.append(
                Check(
                    row["label"],
                    None,
                    None,
                    "stale",
                    f"listed exception no longer differs; remove it ({row['remove_when']})",
                )
            )


# One entry per source that prints totals, e.g. {"example_source": reconcile_example}.
RECONCILERS: dict[str, Callable[[], ReconcileResult]] = {}


def reconcile_all() -> int:
    if not RECONCILERS:
        if SOURCE_PRINTS_TOTALS:
            print(
                "FAIL: reconcile: the source prints totals but no reconciler is registered "
                "(see scripts/reconcile.py)."
            )
            return 2
        print("reconcile: no reconcilers registered and SOURCE_PRINTS_TOTALS is False; skipped.")
        return 0
    exceptions = load_exceptions()
    results: list[ReconcileResult] = []
    failed = False
    lines = ["# Reconciliation", ""]
    for slug, fn in sorted(RECONCILERS.items()):
        try:
            result = fn()
        except Exception as exc:  # noqa: BLE001 — a crashed reconciler is a failure
            failed = True
            lines += [f"## {slug}: ERROR", "", f"`{type(exc).__name__}: {exc}`", ""]
            continue
        apply_exceptions(result, exceptions)
        results.append(result)
        statuses = ("match", "corrected", "excepted", "mismatch", "scope", "stale")
        n = {s: sum(c.status == s for c in result.checks) for s in statuses}
        failed |= bool(result.mismatches)
        lines += [f"## {slug}: " + ", ".join(f"{n[s]} {s}" for s in statuses), ""]
        if result.compared == 0:
            failed = True
            lines += [
                "**FAIL: this reconciler compared nothing.** An empty or truncated "
                "processed table, or a reader that found no totals, can't pass.",
                "",
            ]
        for c in result.checks:
            if c.status not in ("match", "corrected"):
                lines.append(
                    f"- {c.status}: `{c.label}` expected={c.expected} actual={c.actual} {c.notes}"
                )
        lines.append("")
    RECONCILE_MD.write_text("\n".join(lines))
    RECONCILE_JSON.write_text(
        json.dumps([asdict(r) for r in results], indent=2, default=str) + "\n"
    )
    print(
        f"reconcile: {'mismatches found' if failed else 'all checks match'}; see {RECONCILE_MD.name}"
    )
    return 2 if failed else 0

"""Reconcile: recompute the source's own printed totals from the processed rows.

Opt-in per source, and worth it whenever the publisher prints totals or subtotals
(statements of vote, financial reports, enrollment counts). Each reconciler re-reads the
original independently of the parser, returns a `ReconcileResult`, and is listed
in `RECONCILERS` below.

Reconcile at the finest grain both sides share (per office, per precinct, per
page), not only the grand total: grand totals often cover different scopes (date
windows, entity lists), so a top-line gap can be correct and a top-line match can
hide offsetting errors. `compare_totals` compares the keys both sides have and
reports keys present on only one side as a documented scope difference, not a
mismatch. Each known mismatch is explained in the data dictionary's caveats.

Writes `data/audit/reconcile.md` (committed, deterministic) and `reconcile.json`.
Exit code 2 when any check mismatches; the data written by `clean` stays.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field

from scripts.config import RECONCILE_JSON, RECONCILE_MD


@dataclass
class Check:
    label: str
    expected: float | int | str | None
    actual: float | int | str | None
    status: str  # "match" | "mismatch" | "scope" (key on one side only)
    notes: str = ""


@dataclass
class ReconcileResult:
    source: str
    checks: list[Check] = field(default_factory=list)

    @property
    def mismatches(self) -> list[Check]:
        return [c for c in self.checks if c.status == "mismatch"]


def compare_totals(
    expected: Mapping[str, float],
    actual: Mapping[str, float],
    *,
    prefix: str = "",
    tolerance: float = 0.005,
) -> list[Check]:
    """Compare per-key totals (printed vs recomputed) at their shared grain."""
    checks = []
    for key in sorted(set(expected) | set(actual)):
        e, a = expected.get(key), actual.get(key)
        if e is None or a is None:
            side = "source" if a is None else "processed data"
            checks.append(Check(f"{prefix}{key}", e, a, "scope", f"only in the {side}"))
        else:
            status = "match" if abs(float(e) - float(a)) <= tolerance else "mismatch"
            checks.append(Check(f"{prefix}{key}", e, a, status))
    return checks


# One entry per source that prints totals, e.g. {"example_source": reconcile_example}.
RECONCILERS: dict[str, Callable[[], ReconcileResult]] = {}


def reconcile_all() -> int:
    if not RECONCILERS:
        print("reconcile: no reconcilers registered (see scripts/reconcile.py); skipped.")
        return 0
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
        results.append(result)
        n = {s: sum(c.status == s for c in result.checks) for s in ("match", "mismatch", "scope")}
        failed |= bool(result.mismatches)
        lines += [
            f"## {slug}: {n['match']} match, {n['mismatch']} mismatch, {n['scope']} scope-only",
            "",
        ]
        for c in result.checks:
            if c.status != "match":
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

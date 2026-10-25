"""Reconcile: top-line totals verification (opt-in).

For high-stakes pipelines — election results, financial reports, agency
budgets, anything that will be cited publicly — `reconcile.py` re-opens
each original artifact, computes a small set of authoritative top-line
totals, and compares them to what's in the processed deliverable. A
mismatch is a regression: the run completes (don't lose the data), but
CI fails on the reconcile job and the audit flags it.

Default: stub. Per source, register a callable that returns a
`ReconcileResult` in `RECONCILE_REGISTRY` below.

See `references/discovery-and-audit.md` for the rationale and the
BoulderPublicData/Election-Results 149/150 example.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

from scripts.config import DATA_AUDIT

log = structlog.get_logger()

RECONCILE_JSON = DATA_AUDIT / "reconcile.json"


@dataclass
class Check:
    label: str
    expected: float | int | str
    actual: float | int | str
    match: bool
    delta: float | int | str = ""
    notes: str = ""


@dataclass
class ReconcileResult:
    source: str
    checks: list[Check] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.match)

    @property
    def total(self) -> int:
        return len(self.checks)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "passed": self.passed,
            "total": self.total,
            "checks": [c.__dict__ for c in self.checks],
        }


# Add entries here as you write per-source reconciliation. Keep each
# function fast — these run in CI on every merge.
RECONCILE_REGISTRY: dict[str, Callable[[], ReconcileResult]] = {
    # "boulder_county_sov": reconcile_boulder_sov,
}


def reconcile_all() -> int:
    """Run every registered reconciliation. Returns process exit code."""
    if not RECONCILE_REGISTRY:
        log.info("reconcile_empty_registry", hint="see scripts/reconcile.py")
        print(
            "No reconcilers registered. To enable, define a function returning "
            "a ReconcileResult and add it to RECONCILE_REGISTRY in scripts/reconcile.py."
        )
        return 0

    ts = datetime.now(UTC).isoformat()
    payload: list[dict] = []
    any_mismatch = False

    for slug, fn in RECONCILE_REGISTRY.items():
        try:
            result = fn()
        except Exception as exc:  # noqa: BLE001
            log.error("reconcile_errored", source=slug, error=str(exc))
            payload.append({"source": slug, "error": str(exc), "error_type": type(exc).__name__})
            any_mismatch = True
            continue

        d = result.to_dict()
        payload.append(d)
        log.info("reconcile_done", source=slug, passed=result.passed, total=result.total)
        print(f"[{slug}] {result.passed}/{result.total} checks matched")
        for c in result.checks:
            if not c.match:
                print(
                    f"    ✗ {c.label}: expected={c.expected!r} actual={c.actual!r} delta={c.delta!r}"
                )
                any_mismatch = True

    RECONCILE_JSON.parent.mkdir(parents=True, exist_ok=True)
    RECONCILE_JSON.write_text(
        json.dumps({"recorded_at": ts, "results": payload}, indent=2, default=str)
    )
    log.info("wrote_reconcile_report", path=str(RECONCILE_JSON))

    return 2 if any_mismatch else 0

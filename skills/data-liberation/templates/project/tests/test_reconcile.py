"""Reconciliation compares the grain both sides share and keeps scope gaps separate."""

from __future__ import annotations

from scripts.reconcile import compare_totals


def test_scope_differences_are_not_mismatches() -> None:
    checks = {c.label: c.status for c in compare_totals({"a": 10, "b": 5}, {"a": 10, "c": 1})}
    assert checks == {"a": "match", "b": "scope", "c": "scope"}


def test_mismatch_beyond_tolerance() -> None:
    (check,) = compare_totals({"a": 10.00}, {"a": 10.02})
    assert check.status == "mismatch"

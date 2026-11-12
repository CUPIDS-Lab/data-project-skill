"""Reconciliation compares the published grain and is able to fail."""

from __future__ import annotations

import pandas as pd

from scripts import reconcile
from scripts.reconcile import (
    ReconcileResult,
    apply_exceptions,
    compare_totals,
    duplicate_keys,
    mixed_values,
)


def test_missing_keys_are_mismatches_and_extra_keys_are_scope() -> None:
    checks = {c.label: c.status for c in compare_totals({"a": 10, "b": 5}, {"a": 10, "c": 1})}
    assert checks == {"a": "match", "b": "mismatch", "c": "scope"}


def test_mismatch_beyond_tolerance() -> None:
    (check,) = compare_totals({"a": 10.00}, {"a": 10.02})
    assert check.status == "mismatch"


def test_truncated_processed_table_fails() -> None:
    """A processed CSV truncated to its header must not pass."""
    result = ReconcileResult("s", compare_totals({"a": 10, "b": 5}, {}))
    assert len(result.mismatches) == 2


def test_a_reconciler_that_compares_nothing_fails(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(reconcile, "RECONCILE_MD", tmp_path / "reconcile.md")
    monkeypatch.setattr(reconcile, "RECONCILE_JSON", tmp_path / "reconcile.json")
    monkeypatch.setattr(reconcile, "RECONCILERS", {"s": lambda: ReconcileResult("s", [])})
    assert reconcile.reconcile_all() == 2


def test_empty_registry_fails_when_the_source_prints_totals(monkeypatch) -> None:
    monkeypatch.setattr(reconcile, "RECONCILERS", {})
    monkeypatch.setattr(reconcile, "SOURCE_PRINTS_TOTALS", True)
    assert reconcile.reconcile_all() == 2


def test_structural_checks() -> None:
    df = pd.DataFrame(
        {"contest": ["x", "x", "y"], "option": ["A", "A", "Yes"], "kind": ["cand", "cand", "yesno"]}
    )
    assert duplicate_keys(df, ["contest", "option"]).status == "mismatch"
    assert mixed_values(df, ["contest"], "kind").status == "match"
    df.loc[1, "kind"] = "yesno"
    assert mixed_values(df, ["contest"], "kind").status == "mismatch"


def test_exceptions_are_excepted_then_stale() -> None:
    exceptions = pd.DataFrame(
        [
            {
                "source": "s",
                "label": "a",
                "reason": "known",
                "evidence": "url",
                "remove_when": "fixed",
            }
        ]
    )
    result = ReconcileResult("s", compare_totals({"a": 10}, {"a": 12}))
    apply_exceptions(result, exceptions)
    assert [c.status for c in result.checks] == ["excepted"]
    fixed = ReconcileResult("s", compare_totals({"a": 10}, {"a": 10}))
    apply_exceptions(fixed, exceptions)
    assert [c.status for c in fixed.checks] == ["match", "stale"]
    assert not fixed.mismatches  # stale is reported, not a failure


def test_corrected_keys_are_labelled() -> None:
    (check,) = compare_totals({"a": 7}, {"a": 7}, corrected={"a"})
    assert check.status == "corrected"

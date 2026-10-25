"""Progress reporting and the per-run error log.

Every stage that can fail on one artifact without stopping the others records the
failure here. Each run starts its log empty (`ErrorLog.start` deletes the previous
file), so an old failure can never hide a new one, and the audit summary reports the
count. Records carry no timestamps; run times live in `data/audit/run.json`.
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any

PROGRESS_INTERVAL_S = 2.0
_last_progress = 0.0


def progress(i: int, n: int, label: str, *, enabled: bool = True) -> None:
    """Print `[i/n] label` to stderr: always for the first and last item, otherwise
    at most every PROGRESS_INTERVAL_S seconds, so long runs show they are alive."""
    global _last_progress
    if not enabled:
        return
    now = time.monotonic()
    if i in (1, n) or now - _last_progress >= PROGRESS_INTERVAL_S:
        _last_progress = now
        print(f"[{i}/{n}] {label}", file=sys.stderr, flush=True)


class ErrorLog:
    """A JSON list of failures for one stage of one run."""

    def __init__(self, path: Path, stage: str) -> None:
        self.path = path
        self.stage = stage
        self.records: list[dict[str, Any]] = []

    def start(self) -> ErrorLog:
        self.path.unlink(missing_ok=True)
        return self

    def record(self, artifact: Any, error: BaseException | str) -> dict[str, Any]:
        rec = {
            "stage": self.stage,
            "source": getattr(artifact, "source", ""),
            "vintage": getattr(artifact, "vintage", ""),
            "artifact": getattr(artifact, "rel", str(artifact)),
            "url": getattr(artifact, "url", ""),
            "error_type": type(error).__name__ if isinstance(error, BaseException) else "Error",
            "message": str(error),
        }
        if isinstance(error, BaseException):
            rec["traceback"] = "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
        self.records.append(rec)
        print(f"ERROR [{self.stage}] {rec['artifact']}: {rec['message']}", file=sys.stderr)
        return rec

    def write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.records, indent=2, default=str) + "\n")


def read_errors(path: Path) -> list[dict[str, Any]]:
    """Read an error log written by `ErrorLog.write`; empty if absent or unreadable."""
    try:
        data = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []

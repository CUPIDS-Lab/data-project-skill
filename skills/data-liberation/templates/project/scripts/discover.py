"""Enumerate what's available upstream, without downloading.

Walks every `Source.discover()` in the registry, reports artifacts to
stdout, and writes a timestamped diff target at
`data/audit/discovery-<ts>.txt` so consecutive runs are comparable.

A new vintage appearing in this output is the signal to fetch.

See `references/discovery-and-audit.md` for the patterns this implements.
"""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from scripts.config import DATA_AUDIT, SOURCES

log = structlog.get_logger()


def discover_all() -> int:
    """Run discover() on every registered source. Returns process exit code."""
    if not SOURCES:
        log.info("discover_empty_registry", hint="see scripts/config.py::SOURCES")
        print("No sources registered. Add classes to scripts/config.py::SOURCES.")
        return 0

    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out_lines: list[str] = [f"# Discovery {ts}", ""]

    for slug, cls in SOURCES.items():
        out_lines.append(f"## {slug}")
        try:
            source = cls()
            artifacts = list(source.discover())
        except Exception as exc:  # noqa: BLE001
            log.error("discover_failed", source=slug, error=str(exc))
            out_lines.append(f"  (errored: {type(exc).__name__}: {exc})")
            out_lines.append("")
            continue

        log.info("discovered", source=slug, count=len(artifacts))
        out_lines.append(f"  {len(artifacts)} artifacts:")
        for a in artifacts:
            already = "✓" if a.local_path.exists() else " "
            out_lines.append(f"    [{already}] {a.vintage}: {a.url}")
        out_lines.append("")

    text = "\n".join(out_lines)
    print(text)

    out_path = DATA_AUDIT / f"discovery-{ts}.txt"
    out_path.write_text(text)
    log.info("wrote_discovery", path=str(out_path))
    return 0

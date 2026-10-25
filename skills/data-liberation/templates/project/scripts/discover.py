"""Discover: list every artifact upstream and flag the ones not fetched yet.

For a recurring source, a new vintage appearing here is the signal the refresh
workflow acts on. Writes `data/audit/discovery.md` (committed; no timestamps, so
the file changes only when the upstream list does). Make `artifacts()` in
`scripts/source.py` scrape the publisher's index page when the list of files grows
over time; keep it a static list when the URLs are predictable.

Ephemeral sources (a page that only ever shows today's records) cannot be
backfilled: a missed run is lost for good. For those, fetch on a schedule with a
redundant second run, write one dated file per capture, and let this report show
gaps in the dates; don't rely on one cron run being on time.
"""

from __future__ import annotations

from scripts import source
from scripts.config import DATA_AUDIT

DISCOVERY_MD = DATA_AUDIT / "discovery.md"


def discover_all() -> int:
    arts = source.artifacts()
    if not arts:
        print("No artifacts configured: list them in scripts/source.py.")
        return 2
    new = [a for a in arts if not a.local_path.exists()]
    lines = ["# Discovery", "", f"{len(arts)} artifacts upstream; {len(new)} not fetched yet.", ""]
    lines += ["| vintage | artifact | fetched | url |", "| --- | --- | --- | --- |"]
    for a in arts:
        fetched = "no" if a in new else "yes"
        lines.append(f"| {a.vintage} | `{a.rel}` | {fetched} | {a.url} |")
    DISCOVERY_MD.write_text("\n".join(lines) + "\n")
    print(f"discover: {len(arts)} artifacts upstream, {len(new)} new.")
    return 0

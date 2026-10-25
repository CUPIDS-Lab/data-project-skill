"""Fetch: download every artifact from `scripts.source.artifacts()` that is not on
disk yet, into `data/original/<source>/<vintage>/`, and record it in
`data/original/manifest.json` (URL, sha256, size, fetch time).

* Idempotent: a re-run downloads nothing new and leaves the manifest unchanged.
* `--fresh` re-downloads everything, bypassing the HTTP cache. Identical bytes are a
  no-op; changed bytes replace the file, keep the old hash in `previous_sha256`, and
  are reported loudly, so the change shows up in the refresh PR's manifest diff.
* A missing file whose manifest entry exists (an original kept outside git under the
  storage budget) is re-downloaded and checked against the recorded sha256.
* Failures go to a fresh `data/audit/fetch_errors.json` and the exit code is 1. A
  failed download is never replaced by sample, synthetic or stale data.
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import requests_cache
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from scripts import source
from scripts.config import (
    CACHE_EXPIRE_S,
    CACHE_PATH,
    FETCH_ERRORS_JSON,
    MANIFEST_JSON,
    REQUEST_TIMEOUT_S,
    USER_AGENT,
)
from scripts.provenance import sha256_file
from scripts.runlog import ErrorLog, progress

RETRY_STATUS = {429, 500, 502, 503, 504}


class TransientError(Exception):
    """A response worth retrying with backoff."""


class BadDownload(Exception):
    """The response is not the file we asked for."""


def get_session() -> requests_cache.CachedSession:
    session = requests_cache.CachedSession(
        cache_name=str(CACHE_PATH),
        backend="sqlite",
        expire_after=CACHE_EXPIRE_S,
        allowable_codes=(200,),  # never cache an error page
    )
    session.headers["User-Agent"] = USER_AGENT
    return session


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((TransientError, requests.ConnectionError, requests.Timeout)),
    reraise=True,
)
def download(url: str, dest: Path, session: requests.Session) -> None:
    """Stream `url` to `dest`; raise on an HTTP error, an empty body or a non-PDF
    served for a `.pdf` (usually an HTML error page)."""
    with session.get(url, timeout=REQUEST_TIMEOUT_S, stream=True) as r:
        if r.status_code in RETRY_STATUS:
            raise TransientError(f"HTTP {r.status_code}")
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 16):
                f.write(chunk)
    if dest.stat().st_size == 0:
        raise BadDownload("empty response body")
    if url.lower().endswith(".pdf") and dest.read_bytes()[:5] != b"%PDF-":
        raise BadDownload("expected a PDF but got something else (an error page?)")


def load_manifest() -> dict[str, dict[str, Any]]:
    try:
        return json.loads(MANIFEST_JSON.read_text())
    except FileNotFoundError:
        return {}


def write_manifest(manifest: dict[str, dict[str, Any]]) -> None:
    MANIFEST_JSON.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def fetch_all(*, fresh: bool = False, show_progress: bool = True) -> int:
    """Download missing (or, with `fresh`, all) artifacts. Returns an exit code."""
    errors = ErrorLog(FETCH_ERRORS_JSON, "fetch").start()
    arts = source.artifacts()
    if not arts:
        print("No artifacts configured: probe the source, then list them in scripts/source.py.")
        errors.write()
        return 2

    manifest = load_manifest()
    session = get_session()
    counts = {"downloaded": 0, "unchanged": 0, "present": 0, "changed": 0}

    for i, art in enumerate(arts, 1):
        progress(i, len(arts), f"fetch {art.rel}", enabled=show_progress)
        dest = art.local_path
        if dest.exists() and not fresh:
            counts["present"] += 1
            continue
        recorded = manifest.get(art.rel, {}).get("sha256")
        tmp = dest.with_name(dest.name + ".part")
        try:
            if fresh:
                with session.cache_disabled():
                    download(art.url, tmp, session)
            else:
                download(art.url, tmp, session)
        except Exception as exc:  # noqa: BLE001 — recorded; the run reports failure
            tmp.unlink(missing_ok=True)
            errors.record(art, exc)
            continue

        new_sha = sha256_file(tmp)
        if recorded == new_sha:
            shutil.move(tmp, dest)
            counts["unchanged"] += 1
            continue
        if recorded:
            counts["changed"] += 1
            msg = f"upstream bytes changed (was {recorded[:12]}, now {new_sha[:12]})"
            print(f"WARNING {art.rel}: {msg}")
            if not fresh:
                errors.record(art, msg + "; re-run with --fresh to accept the new version")
        shutil.move(tmp, dest)
        entry = manifest.get(art.rel, {})
        previous = entry.get("previous_sha256", []) + ([recorded] if recorded else [])
        manifest[art.rel] = {
            "url": art.url,
            "sha256": new_sha,
            "size_bytes": dest.stat().st_size,
            "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
            **({"previous_sha256": previous} if previous else {}),
        }
        counts["downloaded"] += 1

    write_manifest(manifest)
    errors.write()
    print(
        "fetch: {downloaded} downloaded ({changed} changed upstream), {present} already "
        "present, {unchanged} re-downloaded unchanged; ".format(**counts)
        + f"{len(errors.records)} error(s)."
    )
    return 1 if errors.records else 0

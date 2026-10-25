"""Idempotent downloader.

Walks each `Source.discover()`, downloads any artifact not already present
under `data/original/<source>/<vintage>/`, and updates a per-source
`manifest.json` recording sha256 / URL / retrieval timestamp / file size.

Idempotence: re-running `fetch` after a no-change interval is a no-op.
`requests-cache` handles the HTTP-layer idempotence; the `force` flag
bypasses both the cache and the file-exists short-circuit.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import requests
import requests_cache
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from scripts.config import (
    CACHE_EXPIRE_S,
    CACHE_PATH,
    DATA_ORIGINAL,
    REQUEST_TIMEOUT_S,
    SOURCES,
    USER_AGENT,
)

log = structlog.get_logger()


def get_session() -> requests_cache.CachedSession:
    """Build a cached, identified HTTP session."""
    session = requests_cache.CachedSession(
        cache_name=str(CACHE_PATH),
        backend="sqlite",
        expire_after=CACHE_EXPIRE_S,
        cache_control=True,
    )
    session.headers["User-Agent"] = USER_AGENT
    return session


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((requests.exceptions.RequestException,)),
    reraise=True,
)
def http_download(url: str, dest: Path, session: requests.Session, force: bool) -> bool:
    """Download `url` to `dest` unless `dest` exists and not `force`.

    Returns True if we wrote a file; False if we short-circuited.
    """
    if dest.exists() and not force:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = session.get(url, timeout=REQUEST_TIMEOUT_S, stream=True)
    r.raise_for_status()
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
    return True


def update_manifest(source_name: str, path: Path, url: str) -> None:
    """Add or update one entry in `data/original/<source>/manifest.json`."""
    manifest_path = DATA_ORIGINAL / source_name / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, dict] = {}
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text())
        except json.JSONDecodeError:
            existing = {}

    rel = str(path.relative_to(DATA_ORIGINAL / source_name))
    existing[rel] = {
        "url": url,
        "sha256": sha256_of(path),
        "fetched_at": datetime.now(UTC).isoformat(),
        "size_bytes": path.stat().st_size,
    }
    manifest_path.write_text(json.dumps(existing, indent=2, sort_keys=True))


def fetch_all(force: bool = False, source: str | None = None) -> int:
    """Download missing artifacts for every (or one) source. Returns exit code."""
    if not SOURCES:
        log.info("fetch_empty_registry", hint="see scripts/config.py::SOURCES")
        print("No sources registered. Add classes to scripts/config.py::SOURCES.")
        return 0

    session = get_session()
    downloaded = 0
    skipped = 0
    errored = 0

    for slug, cls in SOURCES.items():
        if source and slug != source:
            continue
        try:
            src = cls()
            for artifact in src.discover():
                try:
                    wrote = http_download(artifact.url, artifact.local_path, session, force=force)
                    if wrote:
                        downloaded += 1
                        update_manifest(slug, artifact.local_path, artifact.url)
                        log.info(
                            "fetched",
                            source=slug,
                            vintage=artifact.vintage,
                            path=str(artifact.local_path),
                        )
                    else:
                        skipped += 1
                except Exception as exc:  # noqa: BLE001
                    errored += 1
                    log.error(
                        "fetch_failed",
                        source=slug,
                        vintage=artifact.vintage,
                        url=artifact.url,
                        error=str(exc),
                    )
        except Exception as exc:  # noqa: BLE001
            log.error("source_discover_failed", source=slug, error=str(exc))
            errored += 1

    log.info("fetch_summary", downloaded=downloaded, skipped=skipped, errored=errored)
    print(f"Fetched {downloaded} new files; {skipped} already present; {errored} errors.")
    return 0 if errored == 0 else 1

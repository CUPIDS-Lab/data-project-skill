"""Upload source documents to DocumentCloud and write the URLs back into provenance.

The source-document surface, alongside Datasette, Quarto and Git LFS. Part 4 of
`publishing.md` in the data-liberation skill has the design:
https://github.com/CUPIDS-Lab/data-skills/tree/main/skills/data-liberation/references/publishing.md

Upload only what the project's visibility and sensitivity decisions allow a hosted
service to see (`decision-log.md`); `access` defaults to `private` for that reason.

Usage
-----
    # First-time setup: register an account at https://accounts.muckrock.com/
    # then put credentials in .env (gitignored):
    #   DOCUMENTCLOUD_USERNAME=...
    #   DOCUMENTCLOUD_PASSWORD=...

    # Install the optional extra:
    uv sync --extra documentcloud

    # Upload everything under data/original/<source>/ to its DocumentCloud project
    uv run python -m scripts.upload_documentcloud --source example_source

    # Or, upload every source under data/original/ at once:
    uv run python -m scripts.upload_documentcloud --all

Convention: one DocumentCloud project per source slug. Project IDs
live in `data/lookups/documentcloud_projects.yaml` — create the project once
via the web UI, record its ID here, and the script does the rest. Documents
the script uploads default to `access="private"`; set `public` per source in the
same YAML once the project's visibility decision allows it.

The script is idempotent: a file already present in DocumentCloud (matched
by sha256) is skipped rather than re-uploaded.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
import yaml

from scripts.config import DATA_LOOKUPS, DATA_ORIGINAL, MANIFEST_JSON, PROVENANCE_CSV


def _log(event: str, **fields: object) -> None:
    """One line per event on stderr: `event key=value ...`."""
    print(event, *(f"{k}={v}" for k, v in fields.items()), file=sys.stderr)


PROJECTS_YAML = DATA_LOOKUPS / "documentcloud_projects.yaml"


def _load_projects() -> dict[str, dict]:
    """Per-source DocumentCloud project metadata.

    Schema:
        boulder_county_sov:
          project_id: 12345
          access: public        # public | organization | private (default public)
          source_label: "Boulder County Clerk and Recorder"  # optional override
    """
    if not PROJECTS_YAML.exists():
        return {}
    return yaml.safe_load(PROJECTS_YAML.read_text()) or {}


def _client():
    try:
        from documentcloud import DocumentCloud
    except ImportError:
        sys.stderr.write(
            "python-documentcloud is not installed. Run: uv sync --extra documentcloud\n"
        )
        sys.exit(1)
    username = os.environ.get("DOCUMENTCLOUD_USERNAME")
    password = os.environ.get("DOCUMENTCLOUD_PASSWORD")
    if not (username and password):
        sys.stderr.write(
            "Set DOCUMENTCLOUD_USERNAME and DOCUMENTCLOUD_PASSWORD in .env or environment.\n"
        )
        sys.exit(1)
    return DocumentCloud(username, password)


def _already_uploaded(client, sha256: str, project_id: int | None) -> str | None:
    """Return canonical_url if a doc with this sha256 is already in the project."""
    if not sha256:
        return None
    q = f"sha256:{sha256}"
    if project_id:
        q = f"{q} projectid:{project_id}"
    try:
        hits = client.documents.search(q)
    except Exception as exc:  # noqa: BLE001 — DocumentCloud transient errors
        _log("documentcloud_search_failed", error=str(exc))
        return None
    return hits[0].canonical_url if hits else None


def upload_source(slug: str, force: bool = False) -> int:
    """Upload every artifact under data/original/<slug>/ to DocumentCloud."""
    projects = _load_projects()
    meta = projects.get(slug, {})
    project_id = meta.get("project_id")
    access = meta.get("access", "private")
    source_label = meta.get("source_label", slug)

    if not project_id:
        _log(
            "no_project_id",
            source=slug,
            hint=f"add to {PROJECTS_YAML.relative_to(Path.cwd())}",
        )
        return 1

    source_dir = DATA_ORIGINAL / slug
    if not source_dir.exists():
        _log("no_source_dir", source=slug, path=str(source_dir))
        return 1

    manifest = json.loads(MANIFEST_JSON.read_text()) if MANIFEST_JSON.exists() else {}
    client = _client()
    rows: list[dict] = []
    uploaded = skipped = errored = 0

    for path in sorted(source_dir.rglob("*")):
        if path.is_dir() or path.suffix == ".part":
            continue
        vintage = (
            path.relative_to(source_dir).parts[0] if path.relative_to(source_dir).parts else ""
        )
        rel = path.relative_to(DATA_ORIGINAL).as_posix()
        sha256 = manifest.get(rel, {}).get("sha256", "")

        if not force:
            existing = _already_uploaded(client, sha256, project_id)
            if existing:
                _log("already_uploaded", source=slug, file=path.name, url=existing)
                rows.append(
                    {
                        "artifact": rel,
                        "documentcloud_url": existing,
                        "documentcloud_access": access,
                    }
                )
                skipped += 1
                continue

        try:
            doc = client.documents.upload(
                str(path),
                title=f"{source_label} — {vintage} — {path.name}",
                source=source_label,
                project=project_id,
                access=access,
            )
            _log("uploaded", source=slug, file=path.name, url=doc.canonical_url)
            rows.append(
                {
                    "artifact": rel,
                    "documentcloud_url": doc.canonical_url,
                    "documentcloud_access": access,
                }
            )
            uploaded += 1
        except Exception as exc:  # noqa: BLE001
            _log("upload_failed", source=slug, file=path.name, error=str(exc))
            errored += 1

    _log(
        "upload_summary",
        source=slug,
        uploaded=uploaded,
        skipped=skipped,
        errored=errored,
    )
    _merge_into_provenance(rows)
    return 0 if errored == 0 else 1


def _merge_into_provenance(rows: list[dict]) -> None:
    """Merge documentcloud_url + documentcloud_access into provenance.csv."""
    if not PROVENANCE_CSV.exists() or not rows:
        return
    prov = pd.read_csv(PROVENANCE_CSV, dtype=str).fillna("")
    new = pd.DataFrame(rows).drop_duplicates(subset=["artifact"])
    for col in ("documentcloud_url", "documentcloud_access"):
        if col not in prov.columns:
            prov[col] = ""
    prov = prov.merge(new, on=["artifact"], how="left", suffixes=("", "_new"))
    for col in ("documentcloud_url", "documentcloud_access"):
        new_col = f"{col}_new"
        if new_col in prov.columns:
            prov[col] = prov[new_col].where(
                prov[new_col].notna() & (prov[new_col] != ""), prov[col]
            )
            prov = prov.drop(columns=[new_col])
    prov.to_csv(PROVENANCE_CSV, index=False)
    _log("wrote_provenance", path=str(PROVENANCE_CSV))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Upload source documents to DocumentCloud.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--source", help="Source slug (a folder under data/original/)")
    g.add_argument("--all", action="store_true", help="Upload every source under data/original/")
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-upload even if a doc with the same sha256 is already in the project",
    )
    args = p.parse_args(argv)

    if args.all:
        rc = 0
        for slug in sorted(d.name for d in DATA_ORIGINAL.iterdir() if d.is_dir()):
            rc = upload_source(slug, force=args.force) or rc
        return rc
    return upload_source(args.source, force=args.force)


if __name__ == "__main__":
    sys.exit(main())

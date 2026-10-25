# Extract: APIs, BI dashboards and ArcGIS layers

Many civic sources are served by an endpoint rather than a file: a REST or JSON API, an open-data portal (Socrata, CKAN), a BI dashboard (Tableau, Power BI, ArcGIS Dashboards) or an ArcGIS map layer. This file covers Outline section 2 (Acquire) and section 3 (Extract) for them: finding the endpoint, paging it completely, caching every raw response as an original, keeping secrets out of git, and recording provenance for each pull. Rendered HTML with no endpoint behind it is in [`extract-web.md`](extract-web.md); parsing JSON or XML already on disk is in [`extract-documents.md`](extract-documents.md).

## Contents

- [Probe, then extract](#probe-then-extract)
- [Finding the endpoint](#finding-the-endpoint)
- [Paging completely](#paging-completely)
- [Empty is not the same as wrong](#empty-is-not-the-same-as-wrong)
- [Rate limits and etiquette](#rate-limits-and-etiquette)
- [Raw responses are the originals](#raw-responses-are-the-originals)
- [Authentication without committing secrets](#authentication-without-committing-secrets)
- [Open-data portals: Socrata and CKAN](#open-data-portals-socrata-and-ckan)
- [ArcGIS FeatureServer and MapServer layers](#arcgis-featureserver-and-mapserver-layers)
- [BI dashboards](#bi-dashboards)
- [Enumerate the entities first](#enumerate-the-entities-first)
- [Stable keys](#stable-keys)
- [Provenance for API pulls](#provenance-for-api-pulls)
- [Decision table](#decision-table)
- [Common failure modes](#common-failure-modes)
- [What to write in the AGENTS.md](#what-to-write-in-the-agentsmd)

## Probe, then extract

Before writing a fetcher, pull a handful of records by hand and decode the contract: the envelope shape (a bare list, `{"data": [...]}`, GeoJSON), the real field names (the value may be `obs_val`, not `value`), date and time zone conventions, how nulls and empty results look, which parameters are required, and how paging works. Write each surprise down as a numbered finding in the Survey note, and make every parsing rule cite a finding. This loop is what cracked every API quirk in a real multi-pipeline project and worked first time on a new API; skipping it is how a fetcher ends up confidently downloading the wrong thing.

Probe with the same client, headers and parameters the pipeline will use, and save the probe responses under `tests/fixtures/` so the parser has real input to test against.

## Finding the endpoint

Check, in this order:

1. **A bulk download** on the publisher's site or portal (a CSV or ZIP per year). It beats any API for completeness and stability.
2. **Documented APIs**: an `/api/` or `/developer` page, a `data.json` catalog (the Project Open Data standard for US federal agencies), a CKAN portal (`/api/3/action/package_search`), a Socrata portal (`/resource/<id>.json`), an ArcGIS REST directory (`/arcgis/rest/services`), OGC services (`?service=WFS&request=GetCapabilities`).
3. **The request the page makes.** Open DevTools, Network tab, filter to Fetch/XHR, reload, and find the request whose response holds the data. Copy it as cURL, then reproduce it with the fewest headers and parameters that still work. Dashboards and maps almost always have one.
4. **Ask the publisher**, or file a public-records request, when the only route is a rendered view (see [BI dashboards](#bi-dashboards)).

Record which route you used and why the earlier ones failed.

## Paging completely

Most APIs page. Identify the style during the probe, then write one pager per source that stops on an explicit signal and checks its own completeness.

| Style | Signal to continue | Watch for |
|---|---|---|
| Offset / limit | page returned `limit` rows | results shifting between pages when data changes mid-pull; always sort by a stable key |
| Page number | `page < total_pages` | 0- versus 1-based pages |
| Cursor / token | a `next_cursor` or `nextPageToken` is present | a repeated cursor (loop forever); stop on repeat |
| Link | `links.next` in the body, or an RFC 8288 `Link: <...>; rel="next"` header (`response.links` in httpx and requests) | relative URLs; parameters dropped from the next link |
| GraphQL | `pageInfo { hasNextPage endCursor }` | page size caps per field |
| ArcGIS | `exceededTransferLimit: true`, or fewer than the count | see the ArcGIS section |

**Hard caps are silent.** Many endpoints stop at a fixed ceiling (10,000 rows is common) and simply return no more, with no error. Get the total first where the API offers one (`count`, `total`, `returnCountOnly`), compare it with what you received, and fail when they differ. When a cap exists, split the query (by date range, by entity, by geography) so each slice stays under it, and record the slicing.

```python
"""A link-following pager that saves every raw page and checks the total."""
import hashlib
import json
from pathlib import Path

import httpx


def pull(url: str, params: dict, out_dir: Path, client: httpx.Client, max_pages: int = 10_000) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pages, seen_urls, n_records, expected = [], set(), 0, None
    next_url, next_params = url, params
    for i in range(max_pages):
        r = client.get(next_url, params=next_params)
        r.raise_for_status()
        body = r.json()
        path = out_dir / f"page-{i:05d}.json"
        path.write_bytes(r.content)                         # raw bytes, before any parsing
        records = body.get("data", [])
        n_records += len(records)
        expected = body.get("meta", {}).get("total", expected)
        pages.append({"file": path.name, "url": str(r.url), "status": r.status_code,
                      "records": len(records), "sha256": hashlib.sha256(r.content).hexdigest()})
        next_url = body.get("links", {}).get("next") or r.links.get("next", {}).get("url")
        if not next_url or next_url in seen_urls:
            break
        seen_urls.add(next_url)
        next_params = None                                  # the next link carries its own query
    else:
        raise RuntimeError(f"stopped at max_pages={max_pages}: possible paging loop")
    if expected is not None and n_records != expected:
        raise RuntimeError(f"got {n_records} records, API reports {expected}")
    (out_dir / "pages.json").write_text(json.dumps(pages, indent=2))
    return pages
```

Adapt the envelope keys (`data`, `meta.total`, `links.next`) to what the probe found. Log progress every N pages with `flush=True` so a long pull is visibly alive, and make a long pull resumable: skip pages already on disk for the same query, and keep going from the last saved cursor.

## Empty is not the same as wrong

An API that returns nothing may mean "no data", "you asked wrong", or "it's broken". Distinguish them during the probe and encode each in the fetcher:

- **Some APIs return 404 for "zero records".** Treat it as empty only for the endpoints where the probe showed that, and log it as an empty result, not an error.
- **A 200 with an error inside.** ArcGIS and many others return `{"error": {...}}` with HTTP 200. Check the body, not only the status.
- **A misspelled or unsupported filter is often ignored**, returning an unfiltered or default page that looks like data. Probe each filter with a value that should return nothing and confirm it does.
- **Required parameter pairs.** Some endpoints return full history only when both `startDate` and `endDate` are given, and something partial when only one is. Probe both, alone and together.
- **Empty bodies from caches.** An HTTP cache can store an empty or truncated body for a large page and serve it forever. Never cache a response you haven't validated, and give the fetcher a `--fresh` option that bypasses the cache.

Then apply the pipeline rule: an empty or degenerate pull for an entity or period that should have data is an error in the run's error log, never a silent zero.

## Rate limits and etiquette

Read the documented limits and stay under them; with none documented, one request at a time with a short pause is polite. Identify the project in the `User-Agent` with a contact address. On HTTP 429 or 503, honor `Retry-After` and back off exponentially (`tenacity`), slowing the whole run. Use `requests-cache` or `hishel` during development so iteration doesn't re-hit the server, but the pipeline's originals are the saved raw responses, not the HTTP cache. The ethics of automated access (terms of service, robots.txt, public-record status) are the same as for scraping; see [`extract-web.md`](extract-web.md).

## Raw responses are the originals

Save every response body exactly as received, before parsing, under `data/original/<source>/<pull_id>/` (for example `data/original/streamflow/2026-10-25/page-00000.json`), with a manifest listing each file's request URL, status, record count and SHA-256. Parsing reads from those files, never from the network, so the extract is reproducible after the API changes or disappears. Compress large pulls (`.json.gz`) and keep them out of git when they are big, with the manifest committed and the files in external storage. Never overwrite a previous pull: a new pull is a new directory.

## Authentication without committing secrets

- Keep keys and tokens in environment variables, loaded from a gitignored `.env` locally and from repository secrets in CI. Never put them in code, notebooks, `config.py` or committed output.
- Prefer sending a key in a header (`X-App-Token`, `Authorization`) over a query parameter. If it must be a parameter, strip it from every URL before it is logged or written to a manifest or `provenance.csv`.
- Check before committing: run a secret scanner (`gitleaks`, or GitHub's push protection) and look at saved manifests and response files for echoed tokens.
- A key that reached git history is leaked even after you delete it; rotate it first, then clean up.

```python
import os

import httpx

token = os.environ["CENSUS_API_KEY"]                       # KeyError is the right failure if unset
client = httpx.Client(headers={"User-Agent": "my-project/0.1 (+mailto:contact@example.org)"}, timeout=60)
r = client.get("https://api.census.gov/data/2023/acs/acs5",
               params={"get": "NAME,B01003_001E", "for": "county:*", "in": "state:08", "key": token})
logged_url = str(r.url.copy_remove_param("key"))           # what goes into the manifest
```

## Open-data portals: Socrata and CKAN

**Socrata** (Tyler Data & Insights) serves each dataset at `https://<domain>/resource/<id>.json` with SoQL parameters: `$select`, `$where`, `$order`, `$limit`, `$offset`. Page with `$order=:id` (the system row ID) so pages don't shift, and send an app token in `X-App-Token` for higher limits. Dataset metadata, including column types and the last-update time, is at `https://<domain>/api/views/<id>.json`, and the full export at `https://<domain>/api/views/<id>/rows.csv?accessType=DOWNLOAD`. For a complete snapshot the export is simpler than paging; record the metadata's update timestamp with it. Newer API versions on some portals require authentication; check the portal's developer docs.

**CKAN** portals expose an action API under `/api/3/action/`: `package_search?q=...` and `package_show?id=...` list a dataset's resources (usually downloadable files, which you then fetch like any download), and `datastore_search?resource_id=...&limit=...&offset=...` pages through resources loaded into the DataStore. Responses wrap results in `{"success": true, "result": ...}`; check `success`.

## ArcGIS FeatureServer and MapServer layers

City and county GIS portals, ArcGIS Hub sites and ArcGIS Dashboards are backed by layers at URLs like `https://<host>/arcgis/rest/services/<name>/FeatureServer/<layer>` (or `MapServer/<layer>`). The layer's metadata (`?f=json`) tells you what you need:

- `maxRecordCount`: the most features one query returns (often 1,000 or 2,000);
- `advancedQueryCapabilities.supportsPagination`: whether `resultOffset` paging works;
- `objectIdField`, `fields` (names, types, coded-value domains), `geometryType`, and the layer's `spatialReference` (`wkid`);
- `capabilities`: must include `Query`.

Query with `<layer>/query`: `where=1=1` for everything, `outFields=*`, `returnCountOnly=true` for the total, `returnIdsOnly=true` for the object IDs, and `resultOffset` / `resultRecordCount` to page with `orderByFields` set so pages are stable. A response with `exceededTransferLimit: true` means more remain. Ask for coordinates in a known reference with `outSR=4326` (WGS 84 longitude and latitude) or keep the native one and record it; `f=geojson` returns GeoJSON, `f=json` Esri JSON. Errors arrive as HTTP 200 with an `error` object.

```python
"""Page through an ArcGIS layer's query endpoint, saving every raw response."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx


def fetch_layer(layer_url: str, out_dir: Path, sort_field: str, out_sr: int = 4326) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60, headers={"User-Agent": "my-project/0.1 (+mailto:contact@example.org)"}) as client:
        meta = client.get(layer_url, params={"f": "json"}).raise_for_status().json()
        if "error" in meta:
            raise RuntimeError(f"layer metadata: {meta['error']}")      # errors arrive as HTTP 200
        (out_dir / "layer.json").write_text(json.dumps(meta, indent=2))
        page_size = min(meta.get("maxRecordCount") or 1000, 1000)
        if not meta.get("advancedQueryCapabilities", {}).get("supportsPagination"):
            raise RuntimeError("no resultOffset paging: page by object-ID ranges instead")
        count = client.get(f"{layer_url}/query",
                           params={"where": "1=1", "returnCountOnly": "true", "f": "json"}).json()["count"]
        pages, offset, seen = [], 0, 0
        while True:
            params = {
                "where": "1=1", "outFields": "*", "orderByFields": sort_field,
                "resultOffset": offset, "resultRecordCount": page_size,
                "returnGeometry": "true", "outSR": out_sr, "f": "geojson",
            }
            r = client.get(f"{layer_url}/query", params=params).raise_for_status()
            body = r.json()
            if "error" in body:
                raise RuntimeError(f"offset {offset}: {body['error']}")
            path = out_dir / f"page-{offset:07d}.geojson"
            path.write_bytes(r.content)                       # the raw response is the original
            n = len(body.get("features", []))
            pages.append({"file": path.name, "url": str(r.url), "records": n,
                          "sha256": hashlib.sha256(r.content).hexdigest()})
            seen += n
            if n == 0 or seen >= count:
                break
            offset += n
    if seen != count:
        raise RuntimeError(f"expected {count} features, got {seen}")
    manifest = {"layer_url": layer_url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "count": count, "sort_field": sort_field, "out_sr": out_sr, "pages": pages}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
```

This was run on 2026-10-25 against Esri's public sample server (`sampleserver6.arcgisonline.com`, `USA/MapServer/2`) with a forced page size of 20: 51 features in three pages, matching the count. Older servers without pagination support need ID-range paging instead: get all IDs with `returnIdsOnly=true`, then query `where=<objectIdField> IN (...)` or `>`/`<=` ranges in chunks under `maxRecordCount`.

Things that go wrong with layers:

- **Some layers are boundaries only.** A FeatureServer behind a dashboard may hold only the polygons, with the numbers computed elsewhere or held in a separate table layer (check the service's other layers and `/tables`). Probe before planning around it.
- **Coded values.** Fields with a `domain` store codes; map them to labels from the layer metadata, and keep the codes.
- **Dates** come as epoch milliseconds in UTC; convert explicitly and record the time zone you report in.
- **Geometry**: record the spatial reference of what you saved (`outSR` or the layer's `wkid`); GeoJSON is WGS 84. Large polygon layers can be simplified server-side (`maxAllowableOffset`, `geometryPrecision`); never do that silently for data others will measure.
- **Hub download buttons** produce convenient CSV or shapefile exports, but their caching and field handling vary; for a reproducible pipeline, query the layer directly and save the raw pages.

## BI dashboards

A dashboard is a view over data that lives somewhere else. Find that somewhere else before scraping the view.

1. **Look for an export.** Tableau views often offer Download > Data or Crosstab when the author allows it (and appending `.csv` to a Tableau Public view URL often returns the view's data in that case). Power BI shows "Export data" on a visual only when the report owner enables it. ArcGIS Dashboards read from layers you can query directly (above).
2. **Look for the published dataset.** The same agency often publishes the underlying table on its open-data portal, or will provide it on request; a dashboard's footer or "About" panel sometimes names the source.
3. **Use the dashboard's own requests**, with care. Tableau loads data through session-based endpoints, and Power BI "publish to web" reports fetch it with POST requests to a `.../public/reports/querydata` endpoint whose responses use a compressed format (DSR) that needs a decoder. Real projects have hand-built such decoders. If you go this way: save each raw request body and response as an original, test the decoder against a few values you can read off the rendered view, reconcile against any total the dashboard shows, and expect it to break when the vendor changes the format. Commit the decoder's fixtures so a break fails loudly.
4. **When only rendered views exist** (no export, no endpoint you can use, no published dataset), choose between a public-records request for the underlying table and manual transcription. Transcribe into a file where each value carries a `source_id` (dashboard URL, view, filter state, capture time) and a screenshot saved as the original, use `extraction_method = manual`, and double-key any value that feeds a published number. Looker Studio and other report tools without a data API fall here unless the owner shares the source.

Many dashboards show only the current state; if so, follow the snapshot discipline in [`extract-web.md`](extract-web.md) (write-once captures, a redundant schedule, gap detection).

## Enumerate the entities first

When an API is organized by entity (monitoring stations, schools, facilities, precincts), first pull the list of entities from the catalog endpoint and save it as its own original, then pull data per entity. The saved universe lets the audit say which entities returned nothing, which appeared or disappeared since the last pull, and whether a filter silently dropped some. Some APIs' filters are unreliable while their relationship links are not (in JSON:API services, following `location → catalogRecords → catalogItems` has been the dependable path); use whichever path the probe shows to be complete.

## Stable keys

Live layers and APIs renumber records. Republishing an ArcGIS layer can reassign every `OBJECTID`; a portal re-import can change row IDs. One project found that a seeded random sample changed between two pulls of the same city layer because the sample was drawn by row order and the IDs had been renumbered. Key on a natural key (case number, parcel ID, station ID plus timestamp), never on `OBJECTID` or row position; sort by that key before sampling, deduplicating or diffing; and on each new pull, report rows added, removed and changed against the previous pull by natural key.

## Provenance for API pulls

Each pull is one extract, with one row in `provenance.csv`:

| Column | For an API pull |
|---|---|
| `source`, `vintage` | the source slug, and the pull ID or period |
| `source_url` | the base endpoint plus the canonical query (parameters sorted, secrets removed) |
| `retrieved_at` | UTC time the pull started, from the fetch log |
| `sha256` | hash of the pull manifest, which lists each raw page's hash |
| `extraction_method` | `api` (or `manual` for hand transcription from a rendered view) |
| `extraction_quality` | `clean` (count matched, nothing to flag), `caveats` (slicing around a cap, documented empty entities), `degraded` (incomplete pull, or a decoder with known gaps) |
| `extraction_notes` | API version or service `currentVersion`, page count, record count against the reported total, the layer's spatial reference and `outSR`, the dataset's own last-updated stamp, and any `Retry-After` slowdowns |
| `parser_module` | the parser that read the saved pages |

Record the dataset's own "last updated" time (Socrata's `rowsUpdatedAt`, a layer's `editingInfo.lastEditDate`, an `ETag` or `Last-Modified` header) as well as your retrieval time: they answer different questions.

## Decision table

| Source in front of you | Route |
|---|---|
| A portal with a bulk export | Download the export; record the dataset's update stamp |
| A documented REST API | Probe, then a pager with a total check; save raw pages |
| Socrata dataset | `rows.csv` export for snapshots, or `/resource/` with `$order=:id` for incremental pulls |
| CKAN dataset | `package_show` for resources, then download, or `datastore_search` for DataStore tables |
| ArcGIS map, Hub site or Dashboard | Find the layer URL; query with `resultOffset` paging and `outSR`; save GeoJSON pages |
| Tableau or Power BI dashboard | Export if enabled; else the published dataset; else the dashboard's own requests with a tested decoder; else a records request or manual transcription |
| A page that loads JSON after render | Call that request directly, as an API |
| Only rendered HTML | [`extract-web.md`](extract-web.md) |
| Current state only, no history | Any of the above, plus the snapshot discipline in [`extract-web.md`](extract-web.md) |

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Exactly 1,000, 2,000 or 10,000 rows | Silent server cap | Compare with the reported total; page or slice the query |
| Data looks plausible but ignores your filter | Misspelled or unsupported parameter, silently dropped | Probe each filter with a value that should return nothing |
| Only recent history comes back | Endpoint needs both start and end dates | Probe parameter pairs; pass both |
| 404 treated as a failure for an entity with no data | API uses 404 for "zero records" | Encode that convention for that endpoint only, and log it as empty |
| HTTP 200 but `{"error": ...}` | ArcGIS and others put errors in the body | Check the body on every response |
| Paging never ends | The next cursor or link repeats | Stop on a repeated cursor; set a max-pages bound |
| Pages overlap or skip rows | Unsorted offset paging while data changes | `orderByFields` / `$order` on a stable key |
| Big pages come back empty from the cache | Cache stored a bad response | Validate before caching; `--fresh` |
| A seeded sample changes between pulls | Upstream renumbered IDs | Sort by a natural key before sampling |
| An API key appears in a committed manifest | Key passed as a query parameter and logged | Strip it before logging; rotate the key |
| Dashboard decoder suddenly returns nothing | Vendor changed the response format | Fixture tests on the decoder; reconcile against a visible total |

## What to write in the AGENTS.md

- The route chosen for each source (export, API, layer, dashboard requests, transcription) and why the simpler routes failed.
- The numbered probe findings: envelope, field names, empty-result convention, required parameters, paging style, caps.
- Where raw pages and pull manifests live, and the `--fresh` behavior.
- Which environment variables hold credentials, and that keys are stripped from logged URLs.
- For ArcGIS: the layer URL, `maxRecordCount`, the sort field, the spatial reference saved, and any coded-value domains mapped.
- The natural key for each entity, and whether upstream IDs are stable.
- For dashboards: the decoder, its fixtures, and the total it is reconciled against.

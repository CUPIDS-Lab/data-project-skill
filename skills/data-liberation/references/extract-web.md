# Extract: web pages, scraping and archives

This file is for when the data is on a website rather than in a downloadable file: court records, agency results pages, FOIA case trackers, status pages and listings that publish only as HTML. It covers Outline section 2 (Acquire) for web sources, including sources that show only their current state, and the HTML-specific parts of section 3 (Extract). If the page is backed by an API, a BI dashboard or an ArcGIS layer, go to [`extract-api.md`](extract-api.md) instead; parsing saved HTML, XML and JSON is in [`extract-documents.md`](extract-documents.md).

The order loosely follows the CU Information Science *Web Data Science* course ([INFO4871, Fall 2024 edition](https://github.com/cuinfoscience/INFO4871-Fall2024), last updated March 2025): ethics first, then archives (often no live request is needed at all), then HTTP discipline, then dynamic pages, then government sources and ephemeral sources.

## Contents

- [Scraping in the post-API age](#scraping-in-the-post-api-age)
- [Ethics and consent](#ethics-and-consent)
- [Archives: try them first](#archives-try-them-first)
- [Protocols: when you do need to fetch](#protocols-when-you-do-need-to-fetch)
- [Dynamic pages](#dynamic-pages)
- [Government data specifically](#government-data-specifically)
- [Ephemeral sources](#ephemeral-sources)
- [Discovery as scraping's calmer cousin](#discovery-as-scrapings-calmer-cousin)
- [The provenance row](#the-provenance-row)
- [Common failure modes](#common-failure-modes)
- [What to write in the AGENTS.md](#what-to-write-in-the-agentsmd)

## Scraping in the post-API age

For about a decade the canonical research-data move was *use the platform API*. That era is over. Twitter / X shut down free academic access in 2023; Reddit's API repricing in 2023 ended large-scale academic use; Facebook deprecated CrowdTangle and Pages-Public-Content APIs; YouTube and TikTok tightened to single-digit-percent-of-corpus sampling. The aggregate effect, described in the course's [*Post-API Age* week](https://github.com/cuinfoscience/INFO4871-Fall2024/tree/main/Week%2002%20-%20Post-API%20Age), is that scraping has returned to the methodological mainstream for research that needs corpus-scale platform data. Civic sources are different in kind: many government pages are rendered from a bulk file, an open-data portal or an undocumented JSON endpoint, and those are more stable and more polite to use than the HTML.

This shapes the skill's posture:

- **Look for the data behind the page first.** Check for a bulk download, a portal API, or the request the page itself makes (see [`extract-api.md`](extract-api.md)); scrape rendered HTML when none of those exists, which for many civic sources is often.
- **The legal frame matters more than it used to.** Without the consent-by-API-key fiction, the project has to defend each scrape on its own merits — robots.txt, ToS, jurisdiction, public-record statutes. The *Ethics and consent* section below is not optional reading.
- **Archives are the first-class fallback.** When a publisher locks down (or just changes their HTML), the Wayback snapshot is often the only retrievable form. Treat Internet Archive as part of the toolchain, not an emergency.
- **Documentation of method is part of the artifact.** Post-API scraping is contestable in ways API access wasn't; documenting the legal basis, the request budget, and the fixture-pinned selectors *in `AGENTS.md`* is what makes a scrape defensible six months later.

## Ethics and consent

Scraping is a request for access made unilaterally. The legitimacy of any individual scraper turns on a handful of judgments — about who the publisher is, what the data is, how the request load compares to ordinary use, and whether there's a non-scraping path the publisher would prefer.

The defaults worth holding to:

- **Read `robots.txt`** and respect `Disallow` entries on the paths you intend to crawl. The file lives at `<host>/robots.txt`. `Disallow` is not legally binding in the US, but ignoring it is the loudest signal possible that the project isn't operating in good faith. The `urllib.robotparser` standard-library module reads it correctly; the [`robotexclusionrulesparser`](https://pypi.org/project/robotexclusionrulesparser/) package handles edge cases better.
- **Identify the project in the `User-Agent`.** A header like `User-Agent: {project_slug}/0.1 (+https://github.com/{user}/{project}; contact@example.org)` lets a publisher figure out who's hitting them. Anonymous scrapers are read as bad-faith by default; identified ones get a polite email instead of a block.
- **Use a request budget** matched to the publisher's evident expectations. Government sites built for human browsing tolerate one request per 1–2 seconds without strain; a sustained 10/sec is hostile. The polite-request pattern below sets this explicitly.
- **Don't scrape what you can download.** Many agency sites publish bulk CSVs or annual ZIP archives in addition to the per-record web interface. Scraping the search results when the same data is available as a bulk download is wasted effort and unnecessary load.
- **Don't republish content you don't have rights to.** Scraping is a method, not a license. Original journalism, court filings, copyrighted reports — the scrape recovers a corpus, but redistribution is governed by the underlying rights regime. For civic data, the relevant test is usually "is this a public record?" — which a public records lawyer can answer for borderline cases.
- **Watch for terms-of-service language** that addresses automated access. Many sites' ToS prohibit scraping in some form. Whether that prohibition is enforceable against a public-interest research project varies by jurisdiction; the safe move is to consult, document the legal basis in `AGENTS.md`, and proceed if the basis is solid.

The [`hiQ Labs v. LinkedIn`](https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn) line of cases held (in US federal court) that scraping publicly accessible data is generally not a violation of the Computer Fraud and Abuse Act, but the case ended in 2022 with hiQ found to have breached LinkedIn's user agreement, so terms of service still matter. Defensible scraping operates within a documented frame, not on the assumption that public-facing means consequence-free.

## Archives: try them first

Before writing a single line of fetch code, check whether someone else already fetched what you need.

### Wayback Machine

The [Internet Archive's Wayback Machine](https://web.archive.org/) snapshots a large fraction of the public web. For static pages — agency annual reports, archived statements of vote, historical legislative records — there is usually a Wayback snapshot from a usefully recent date. Fetching from Wayback has three advantages: no load on the publisher, stable URLs (the Wayback URL bakes in the snapshot date), and a built-in provenance proof (the snapshot itself is the evidence of what the page contained at that time).

```python
import httpx

# Fetch a specific snapshot of a page
wayback_url = "https://web.archive.org/web/2024/https://example.gov/report.html"
r = httpx.get(wayback_url)
```

To list captures, two endpoints exist. The CDX API (`https://web.archive.org/cdx/search/cdx?url=<url>&output=json`) supports filters and paging but overloads and times out under load; the timemap (`https://web.archive.org/web/timemap/link/<url>`) is simpler and has worked when CDX failed. Either way, make a long capture listing resumable (save progress per year or per page, with a deadline per run) instead of retrying one huge query. Fetch a capture's original bytes, without the Wayback toolbar and rewritten links, by adding `id_` to the timestamp: `https://web.archive.org/web/20240115000000id_/https://example.gov/report.html`. The [`waybackpy`](https://pypi.org/project/waybackpy/) package wraps these calls, including Save Page Now. Record the full capture URL, with its timestamp, as the `source_url` in provenance.

### Common Crawl

For very-large-scale projects (millions of pages), [Common Crawl](https://commoncrawl.org/) publishes monthly snapshots of the public web in WARC format. The processing model is "filter the bulk dump for the URLs that matter," not "crawl yourself." Out of scope for most civic projects but worth knowing about for survey-scale work.

### Project archives and Datasette mirrors

Many civic data projects publish their own archives (BoulderPublicData/Election-Results commits all raw SoV PDFs to the repo; PUDL publishes versioned releases on Zenodo). Before scraping, check whether someone has done the work and made it citable. Crediting an upstream archive is cheaper and more durable than redoing it.

## Protocols: when you do need to fetch

When you do need to make requests, the discipline is the same for every project: identifiable client, polite pacing, idempotent cache, durable retries.

### `httpx` or `requests`, with timeouts

[`httpx`](https://www.python-httpx.org/) is the modern Python HTTP client. It's API-compatible with `requests` but supports HTTP/2, async, and timeouts-by-default (a critical safety property — `requests` silently waits forever without `timeout=`). For sync workflows, `httpx.Client()` is a drop-in `requests.Session()` replacement.

A minimal polite scraper:

```python
import time
import httpx
from urllib.robotparser import RobotFileParser

USER_AGENT = "{project_slug}/0.1 (+https://github.com/{user}/{project})"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = httpx.Timeout(30.0, connect=10.0)
DELAY_BETWEEN_REQUESTS_S = 1.5  # adjust per publisher tolerance

# Check robots.txt once
rp = RobotFileParser()
rp.set_url("https://example.gov/robots.txt")
rp.read()


def polite_get(url: str) -> httpx.Response:
    if not rp.can_fetch(USER_AGENT, url):
        raise RuntimeError(f"robots.txt disallows: {url}")
    with httpx.Client(headers=HEADERS, timeout=TIMEOUT) as client:
        r = client.get(url)
        time.sleep(DELAY_BETWEEN_REQUESTS_S)
        return r
```

### `requests-cache` for idempotence

Every civic-data scrape gets developed iteratively, which means re-fetching the same pages dozens of times. [`requests-cache`](https://requests-cache.readthedocs.io/) makes this cheap: the first request hits the network, every subsequent request for the same URL reads from a local SQLite cache. The cache expires after a configurable interval (24 hours is the usual default for development; longer for stable archives, shorter for live data).

```python
import requests_cache
import requests

session = requests_cache.CachedSession(
    cache_name=".requests-cache",
    backend="sqlite",
    expire_after=86400,  # 24 hours
    cache_control=True,   # honor Cache-Control headers from the server
)
session.headers["User-Agent"] = USER_AGENT
```

The same pattern works with `httpx` via [`hishel`](https://hishel.com/), a transport-level cache.

### `tenacity` for retries

Transient failures (502, 503, connection reset, DNS hiccup) are the norm in any long-running scrape. [`tenacity`](https://tenacity.readthedocs.io/) handles them with exponential backoff:

```python
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout, requests.HTTPError)),
    reraise=True,
)
def fetch_with_retry(url: str) -> requests.Response:
    r = session.get(url, timeout=30)    # the cached session from above
    r.raise_for_status()
    return r
```

Five attempts with exponential backoff (2, 4, 8, 16, 30 seconds) covers nearly all transient failures without becoming a pest. After five failures, the page is genuinely broken or being rate-limited; raise and let the audit catch it. On HTTP 429 or 503, honor a `Retry-After` header if present, and slow the whole run, not only the retried request.

### Don't save error pages as originals

A blocked, rate-limited or broken request often returns a page that looks like content: a 200 with a bot-check page, a login form, a "service unavailable" template. Before writing anything to `data/original/`, check the status code, the content type and a marker you expect in real content (a table id, a heading). A failure is recorded in the run's error log with its status code and page title, not saved as a snapshot. Real projects have saved bot-check pages as data because nothing checked.

Two more rules from real deployments:

- **Never turn off TLS verification.** When a government site serves an incomplete certificate chain, download the missing intermediate certificate, build a CA bundle that adds it, and pass it explicitly (`httpx.Client(verify=ssl.create_default_context(cafile="certs/agency-chain.pem"))`, or `requests.get(url, verify="certs/agency-chain.pem")`). Commit the bundle and note why in `AGENTS.md`.
- **Expect CI runners to be blocked.** Bot protection often blocks cloud IP ranges, including GitHub-hosted runners, while the same request from a laptop works. Record which runner made each fetch (CI or local) in the fetch log, and plan a local re-capture path for the sources that block CI.

### Idempotent fetch pattern

The full `scripts/fetch.py` pattern that combines all four — robots.txt, polite delay, cache, retry — produces an `idempotent fetcher`: running it twice in a row produces identical state. This is the property `scripts/pipeline.py` depends on when running `discover → fetch → clean` after a no-change interval.

## Dynamic pages

When the data isn't in the HTML response — it's loaded by JavaScript after the page renders — a browser-driving tool is required. The default is [Playwright](https://playwright.dev/python/).

### When to reach for Playwright

Signs the page is dynamic:

- View-source on the page doesn't contain the data you see in the rendered view.
- The page does an XHR/fetch to a JSON endpoint after load and renders the response.
- A login or session cookie is required and the cookie is set via JavaScript.
- The data is in a JavaScript framework's state (React, Vue) and only realized in the DOM after render.

For all of these, the cheapest fix is often **not Playwright**: it is finding the JSON endpoint the page itself is calling. Open the browser's DevTools, watch the Network tab while the page loads, identify the request that returns the data, and call that endpoint directly. This is faster, cheaper and more stable than rendering the page; [`extract-api.md`](extract-api.md) covers paging, caching and provenance for it, including BI dashboards and ArcGIS layers.

Reach for Playwright only when:

- The endpoint requires a session token that can only be obtained by clicking through the UI.
- The data is rendered from a complex JS state machine that doesn't surface a clean endpoint.
- The page uses canvas or another non-DOM rendering target.

### Minimal Playwright pattern

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent=USER_AGENT)
    page = context.new_page()
    page.goto("https://example.gov/dashboard")
    page.wait_for_selector("table.results", state="visible")
    page.wait_for_load_state("networkidle")  # ensure XHRs have settled
    html = page.content()
    browser.close()

# Now parse `html` with selectolax or pandas.read_html
```

The two `wait_for_*` calls are not optional: `wait_for_selector` waits for the data-bearing element to exist; `wait_for_load_state("networkidle")` waits for in-flight XHRs to complete. Skipping either gives you the empty pre-render HTML.

For sites that paginate via JS interaction (Next button, infinite scroll), Playwright lets you script the interaction:

```python
for _ in range(MAX_PAGES):
    rows = page.query_selector_all("tr.data-row")
    # extract rows here
    next_btn = page.query_selector("button.next:not([disabled])")
    if next_btn is None:
        break
    next_btn.click()
    page.wait_for_load_state("networkidle")
```

The fragility budget for browser-driven scraping is high — small UI changes break the script. The mitigation is the same as for HTML parsing: commit a saved trace (Playwright's [trace viewer](https://playwright.dev/python/docs/trace-viewer) is excellent for this) as a fixture, and add a test that exercises the interaction sequence.

### Selenium

[Selenium](https://www.selenium.dev/) predates Playwright and is still widely used. For new projects, Playwright is the better default: faster, more reliable auto-wait, better debugging tools. If a project already uses Selenium, no urgency to migrate.

## Government data specifically

A handful of patterns recur often enough in civic-data scraping to be worth naming.

### Bulk downloads first

Many agencies publish per-record search interfaces alongside annual bulk dumps. The bulk dumps are almost always preferable: faster, more complete, less load on the publisher, and usually the same format every year (so parsers are stable). The Secretary of State's annual election archive ZIP, the agency's annual report bulk PDF set, the bureau's quarterly CSV release — find these first; scrape the search interface only for data that genuinely isn't in the bulk releases.

### CORA / FOIA as a scraping alternative

For records not posted online, the records request is often faster than building a scraper for a hostile interface. [MuckRock](https://www.muckrock.com/) tracks request status across agencies; Colorado has [CORA](https://www.coloradoattorneygeneral.gov/the-colorado-open-records-act/) for state and local records. A well-targeted records request returns a structured dataset directly; the alternative is scraping an interface that's likely undocumented and may change without notice.

When a project does both (FOIA for the historical period, scraping for ongoing refreshes), document both paths in `AGENTS.md`.

### API discovery

Many government sites publish data through APIs without advertising them: `/api/` paths, a `data.json` catalog (the Project Open Data standard for US federal agencies), CKAN (`/api/3/action/`), Socrata (`/resource/<id>.json`) and ArcGIS REST services (`/arcgis/rest/services`). Check for these before writing an HTML scraper; [`extract-api.md`](extract-api.md) has the discovery checklist and how to use each.

### Session cookies and CSRF tokens

Search interfaces backed by ASP.NET (still common in court and county records systems) often require a session cookie and a hidden form token (`__VIEWSTATE`, `__EVENTVALIDATION`) on every request. The flow:

1. GET the initial page; extract `__VIEWSTATE` and `__EVENTVALIDATION` from the HTML.
2. POST to the same URL with the form data plus the extracted tokens.
3. The response is the next page (which has new `__VIEWSTATE` for the next request).

```python
import httpx
from selectolax.parser import HTMLParser

client = httpx.Client(headers={"User-Agent": USER_AGENT})
r = client.get("https://court.example.gov/search")
tree = HTMLParser(r.text)
viewstate = tree.css_first("input[name='__VIEWSTATE']").attributes["value"]
event_val = tree.css_first("input[name='__EVENTVALIDATION']").attributes["value"]

r = client.post(
    "https://court.example.gov/search",
    data={
        "__VIEWSTATE": viewstate,
        "__EVENTVALIDATION": event_val,
        "search_field": "smith",
    },
)
```

These interfaces are fragile and tedious; if a records request would yield the same data, prefer that.

## Ephemeral sources

Some sources show only their current state: today's road closures, a current-outages page, a dashboard of "active" cases, a table the publisher overwrites every night. **A missed snapshot is lost for good**: nobody can backfill it later, including you. Say so plainly in the Survey note and the README, so no one assumes the series can be rebuilt from the source.

**Probe for history first.** Before committing to snapshots, check whether the past is reachable after all: date parameters in the URL or API that accept past dates, a publisher archive page, Wayback captures, or an export with a history option. Ask the publisher; some will send the history on request.

**Choose and record a cadence.** Snapshot at least as often as the source changes (check its "as of" stamp over a few days), and record the cadence and its reason in the decision-log. Key each snapshot by the source's own date in the source's time zone (a county's "today" is not the UTC date), not by when the job happened to run.

**Make the scrape write-once per period.** If the snapshot for this period already exists, exit successfully without touching it, so a second scheduled run or a manual rerun can never overwrite or duplicate a capture:

```python
# scripts/snapshot.py: write-once daily capture of a current-state page.
import csv
import hashlib
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

URL = "https://example.gov/closures"
ROOT = Path("data/original/closures")
LOG = Path("data/audit/snapshots.csv")
TZ = ZoneInfo("America/Denver")          # the publisher's time zone
MARKER = 'id="closures-table"'             # present in real content, absent from error pages


def capture() -> None:
    now = datetime.now(TZ)
    dest = ROOT / now.date().isoformat() / "closures.html"
    if dest.exists():
        print(f"{dest} exists; nothing to do", flush=True)   # write-once
        return
    with httpx.Client(headers={"User-Agent": "closures-snapshots/0.1 (+mailto:contact@example.org)"},
                      timeout=60, follow_redirects=True) as client:
        r = client.get(URL)
    ok = r.status_code == 200 and MARKER in r.text
    if ok:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["period", "retrieved_at", "status", "ok", "sha256", "runner"])
        w.writerow([now.date().isoformat(), now.isoformat(), r.status_code, ok,
                    hashlib.sha256(r.content).hexdigest() if ok else "",
                    "ci" if os.environ.get("CI") else "local"])
    if not ok:
        raise SystemExit(f"capture failed: HTTP {r.status_code}")   # fail loudly; never save the error page


if __name__ == "__main__":
    capture()
```

**Don't trust one scheduled run.** GitHub Actions `schedule` events are best-effort: they can be delayed at busy times (especially the top of the hour) or dropped, and scheduled workflows in a public repository are disabled after 60 days without repository activity. Give the job a second, offset schedule (the write-once rule makes the duplicate harmless), a generous `timeout-minutes`, and a manual trigger:

```yaml
on:
  schedule:
    - cron: "17 13 * * *"    # primary (UTC)
    - cron: "47 19 * * *"    # backup; the script is write-once per day
  workflow_dispatch:
```

**Detect gaps.** A daily check compares the expected periods with the snapshots present and the run log, and fails (or opens an issue) when one is missing, so a gap is noticed while Wayback or the publisher might still help. Never fill a gap by copying the neighboring snapshot or interpolating: record it as missing in the data and the dictionary's caveats.

**Recover what you can, and keep the record.** For a missed period, look for a Wayback capture of that day, and consider a public-records request (FOIA, or Colorado's CORA) for the publisher's own record. Keep a table in `ROADMAP.md` of missed periods and the requests filed.

**Archive beyond your own repository.** Submitting each capture to the Wayback Machine's Save Page Now (`https://web.archive.org/save/<url>`, within its rate limits) gives an independent, timestamped witness; it may not capture content rendered by JavaScript, so keep your own copy as the original. When snapshots outgrow git, move them to external storage (a release asset, object storage) with each file's hash and URL in the manifest.

## Discovery as scraping's calmer cousin

`scripts/discover.py` (see `references/pipeline.md`) is fundamentally a scraping operation, but a very small one — just enough HTTP to ask "what's available?" without downloading anything. Treat it with the same discipline: identifiable User-Agent, polite delay, cached fetch, retries. The two operations share most of their infrastructure, which is why `fetch.py` and `discover.py` both end up importing from the same `_http.py` helper module in mature projects.

## The provenance row

One row in `provenance.csv` per captured page (or per crawl batch with a file manifest) and parser run: `source`, `vintage` (or the snapshot period), `source_url` (the live URL, or the full Wayback capture URL), `retrieved_at` (from the fetch log), `sha256` of the saved HTML, `extraction_method = scrape`, `extraction_quality` (`clean`, `caveats` or `degraded`), and `extraction_notes` naming the load-bearing selectors, the runner, and whether the page came live or from an archive.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `httpx.ConnectError` after some delay | DNS or TLS handshake failing intermittently | Wrap in `tenacity` retry; raise the retry count |
| 403 on every request | Default User-Agent matches a known bot pattern | Set an identifiable `User-Agent` with project URL |
| Pagination loops forever | "Next" link always present but returns the same page | Detect repeat by URL or by content hash; break |
| Playwright timeout on `wait_for_selector` | Page renders the element but uses a different selector across vintages | Inspect with `page.pause()` in dev; commit fixtures of each layout variant |
| Cached responses return stale data | `requests-cache` expiration too long; site updated | Lower `expire_after`; clear cache for development of a specific source |
| Scraped table looks right but every numeric cell is the same value | The selector matches a sibling element instead of the row's value | Inspect with DevTools; tighten the selector |
| Long scrape blocked midway by Cloudflare | The publisher uses Cloudflare bot protection | Slow the request rate further; consider whether a records request is preferable |
| Site changed and parser fails silently | UI redesign | Commit the saved HTML as a fixture; the parser test catches the next breakage |
| Months of "snapshots" are bot-check or error pages | Content saved without checking status and a content marker | Check status and an expected marker before saving; log failures instead |
| Works locally, 403 in CI | Bot protection blocks cloud runner IPs | Record the runner; re-capture locally; ask the publisher |
| `SSL: CERTIFICATE_VERIFY_FAILED` on a government site | Incomplete certificate chain | Add the intermediate to a committed CA bundle; never disable verification |
| A daily series has holes | Scheduled run delayed, dropped or disabled | Second offset schedule, write-once capture, daily gap check |
| Wayback CDX queries time out | CDX overloaded | Use the timemap; make listing resumable with a deadline |

---

## What to write in the AGENTS.md

- **Scraped vs downloaded** — which parts of the data come from a live scrape vs a bulk-download or records request.
- **Ethical frame** — rate limit, User-Agent, robots.txt status, legal basis for the underlying records (CORA / FOIA / public-record statute).
- **Auth / session** — cookie or token flow, expiry.
- **Dynamic vs static** — `httpx` + parser, or Playwright (with reason).
- **Fragility points** — the load-bearing selector(s) and the saved-page fixture that pins them.
- **Backup paths** — Wayback snapshot URL pattern, records-request fallback.
- **Ephemeral sources** — that the source shows only current state, the snapshot cadence and time zone, the schedules, the gap check, and where missed periods and records requests are tracked.
- **TLS and runners** — any committed CA bundle and why, and which sources must be captured from a local session.

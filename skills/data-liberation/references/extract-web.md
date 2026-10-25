# Extract: web scraping

This part is for when the data is on a website rather than in a downloadable file. Government dashboards, court records, agency results pages, real-time logs, FOIA case trackers — common civic data sources, many publishing only as HTML.

The structure follows the CU Information Science [INFO4871 *Web Data Science* course](https://github.com/cuinfoscience/INFO4871-Fall2024): ethics first, then archives (often the fastest path involves no live request at all), then protocols (HTTP discipline), then dynamic pages, then government data specifically.

## Scraping in the post-API age

For about a decade the canonical research-data move was *use the platform API*. That era is over. Twitter / X shut down free academic access in 2023; Reddit's API repricing in 2023 ended large-scale academic use; Facebook deprecated CrowdTangle and Pages-Public-Content APIs; YouTube and TikTok tightened to single-digit-percent-of-corpus sampling. The aggregate effect — described in the [INFO4871 *Post-API Age* materials](https://github.com/cuinfoscience/INFO4871-Fall2024/tree/master/Week%2002%20-%20Post-API%20Age) — is that scraping has returned to the methodological mainstream for any research or accountability project that needs corpus-scale public data. The civic-data version of this is even sharper: government APIs were always thin, and the bulk-download alternative was always sparse, so civic projects never left the scraping era.

This shapes the skill's posture:

- **Scraping is the default**, not the fallback. The toolchain decision tree starts with "what's the most polite way to scrape this?" not "is there an API?"
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

The [`hiQ Labs v. LinkedIn`](https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn) line of cases established (in US federal court) that scraping publicly-accessible data is generally not a violation of the Computer Fraud and Abuse Act, but specific facts matter. The point is that defensible scraping operates within a documented frame, not on the assumption that public-facing means consequence-free.

## Archives — try them first

Before writing a single line of fetch code, check whether someone else already fetched what you need.

### Wayback Machine

The [Internet Archive's Wayback Machine](https://web.archive.org/) snapshots a large fraction of the public web. For static pages — agency annual reports, archived statements of vote, historical legislative records — there is usually a Wayback snapshot from a usefully recent date. Fetching from Wayback has three advantages: no load on the publisher, stable URLs (the Wayback URL bakes in the snapshot date), and a built-in provenance proof (the snapshot itself is the evidence of what the page contained at that time).

```python
import httpx

# Fetch a specific snapshot of a page
wayback_url = "https://web.archive.org/web/2024/https://example.gov/report.html"
r = httpx.get(wayback_url)
```

The [`waybackpy`](https://pypi.org/project/waybackpy/) package wraps the Wayback CDX API for programmatic snapshot lookup: "give me all snapshots of this URL," "find the snapshot closest to a date," "save this URL now (Save Page Now)."

### Common Crawl, CommonSearch, etc.

For very-large-scale projects (millions of pages), [Common Crawl](https://commoncrawl.org/) publishes monthly snapshots of the public web in WARC format. The processing model is "filter the bulk dump for the URLs that matter," not "crawl yourself." Out of scope for most civic projects but worth knowing about for survey-scale work.

### Project archives and Datasette mirrors

Many civic data projects publish their own archives (BoulderPublicData/Election-Results commits all raw SoV PDFs to the repo; PUDL publishes versioned releases on Zenodo). Before scraping, check whether someone has done the work and made it citable. Crediting an upstream archive is cheaper and more durable than redoing it.

## Protocols — when you do need to fetch

When you do need to make requests, the discipline is the same for every project: identifiable client, polite pacing, idempotent cache, durable retries.

### `httpx` over `requests` (or with `requests-cache`)

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
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
    reraise=True,
)
def fetch_with_retry(url: str) -> httpx.Response:
    r = session.get(url)
    r.raise_for_status()
    return r
```

Five attempts with exponential backoff (2, 4, 8, 16, 30 seconds) covers nearly all transient failures without becoming a pest. After five failures, the page is genuinely broken or being rate-limited; raise and let the audit catch it.

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

For all of these, the cheapest fix is often **not Playwright** — it's finding the JSON endpoint the page itself is calling. Open the browser's DevTools, watch the Network tab while the page loads, identify the XHR request that returns the data, and call that endpoint directly with `httpx`. This is faster, cheaper, and more stable than rendering the full page.

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

Many government sites publish data through APIs without advertising them prominently:

- **`/api/v1/...`** or `/data/api/` paths.
- A `data.json` at the root of a site (the [Project Open Data](https://project-open-data.cio.gov/) standard, mandated for US federal agencies).
- A CKAN portal (`<host>/api/3/action/...` patterns) — used by many state and city open-data sites.
- A Socrata portal (`<host>/resource/<id>.json`) — used by many municipal data sites.

A quick scan for these before writing any HTML scraper is worth a few minutes; using the API is more polite, more stable, and often returns better-typed data than the HTML version.

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

## Discovery as scraping's calmer cousin

`scripts/discover.py` (see `references/pipeline.md`) is fundamentally a scraping operation, but a very small one — just enough HTTP to ask "what's available?" without downloading anything. Treat it with the same discipline: identifiable User-Agent, polite delay, cached fetch, retries. The two operations share most of their infrastructure, which is why `fetch.py` and `discover.py` both end up importing from the same `_http.py` helper module in mature projects.

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

---

## What to write in the AGENTS.md

- **Scraped vs downloaded** — which parts of the data come from a live scrape vs a bulk-download or records request.
- **Ethical frame** — rate limit, User-Agent, robots.txt status, legal basis for the underlying records (CORA / FOIA / public-record statute).
- **Auth / session** — cookie or token flow, expiry.
- **Dynamic vs static** — `httpx` + parser, or Playwright (with reason).
- **Fragility points** — the load-bearing selector(s) and the saved-page fixture that pins them.
- **Backup paths** — Wayback snapshot URL pattern, records-request fallback.

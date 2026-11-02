#!/usr/bin/env python3
"""
SERP lead engine: Google results are the cheapest, widest lead source — one X-ray query searches LinkedIn posts,
Reddit, Quora, X, Facebook groups, Indie Hackers, Upwork jobs and hiring pages at once. This runs the query library
(built from SELLER-PROFILE.json) through whichever SERP API you have, with a recency filter, several pages and your
target countries, then intent-scores every result and drops sellers, job ads and excluded markets.

Providers (tried in SERP_PROVIDERS order; one that fails or has no key is skipped):
    serper      SERPER_API_KEY      POST https://google.serper.dev/search          (X-API-KEY; ~ $1 / 1,000 searches)
    serpapi     SERPAPI_API_KEY     GET  https://serpapi.com/search.json            (engine=google)
    brightdata  BRIGHTDATA_API_KEY  POST https://api.brightdata.com/request          (SERP zone, parsed_light)
    brave       BRAVE_API_KEY       GET  https://api.search.brave.com/res/v1/web/search (X-Subscription-Token)
    apify       APIFY_TOKEN         apify/google-search-scraper
Default order: serper,serpapi,brightdata,brave,apify.

Usage (every command prints one JSON object):
    python serp.py hunt [--days 7] [--pages 2] [--max-queries 20] [--platform linkedin,reddit] [--save hunt.json]
    python serp.py search 'site:linkedin.com/posts "looking for" "Shopify developer"' [--days 7] [--country us] [--pages 1]
    python serp.py providers          # which providers have keys, in which order, and the cost of a hunt
Signal queries (companies hiring for the role you replace) run with --signals.
"""

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_scan  # noqa: E402
import query_library  # noqa: E402
from sales_common import ApiError, api_json, emit, secret, setting  # noqa: E402

PROVIDERS = {"serper": "SERPER_API_KEY", "serpapi": "SERPAPI_API_KEY", "brightdata": "BRIGHTDATA_API_KEY",
             "brave": "BRAVE_API_KEY", "apify": "APIFY_TOKEN"}
COST_PER_1K = {"serper": 1.0, "serpapi": 15.0, "brightdata": 1.5, "brave": 5.0, "apify": 4.5}   # rough USD, for the estimate


class UserError(Exception):
    pass


def _tbs(days):
    return {1: "qdr:d", 7: "qdr:w", 30: "qdr:m", 365: "qdr:y"}.get(int(days), f"qdr:d{max(1, int(days))}")


def _brave_freshness(days):
    d = int(days)
    return "pd" if d <= 1 else "pw" if d <= 7 else "pm" if d <= 31 else "py"


def _row(url, title, text, posted, query, provider):
    return {"url": url, "title": title or "", "text": text or "", "posted": posted, "query": query, "provider": provider,
            "source": "serp", "platform": intent_scan.platform_of(url or ""), "author": None}


def serper(key, q, days, country, page, call):
    status, d = call("POST", "https://google.serper.dev/search", headers={"X-API-KEY": key}, timeout=30,
                     body={"q": q, "gl": country or "us", "hl": "en", "num": 10, "tbs": _tbs(days), "page": page})
    if status >= 400:
        raise ApiError(status, f"Serper HTTP {status}: {str((d or {}).get('message') or d)[:120]}")
    return [_row(r.get("link"), r.get("title"), r.get("snippet"), r.get("date"), q, "serper") for r in (d or {}).get("organic") or []
            if r.get("link")]


def serpapi(key, q, days, country, page, call):
    status, d = call("GET", "https://serpapi.com/search.json", timeout=40,
                     params={"engine": "google", "q": q, "api_key": key, "gl": country or "us", "hl": "en", "num": 10,
                             "tbs": _tbs(days), "start": (page - 1) * 10})
    if status >= 400 or (d or {}).get("error"):
        raise ApiError(status, f"SerpAPI: {(d or {}).get('error') or 'HTTP ' + str(status)}")
    return [_row(r.get("link"), r.get("title"), r.get("snippet"), r.get("date"), q, "serpapi")
            for r in (d or {}).get("organic_results") or [] if r.get("link")]


def brightdata(key, q, days, country, page, call):
    params = {"q": q, "tbs": _tbs(days), "num": 10, "hl": "en", "start": (page - 1) * 10}
    if country:
        params["gl"] = country
    status, d = call("POST", "https://api.brightdata.com/request", headers={"Authorization": f"Bearer {key}"}, timeout=60,
                     body={"zone": setting("BRIGHTDATA_ZONE", "serp_api1"), "url": "https://www.google.com/search?" + urlencode(params),
                           "format": "raw", "data_format": "parsed_light"})
    if status >= 400 or not isinstance(d, dict) or "organic" not in d:
        raise ApiError(status, f"Bright Data HTTP {status} (is the zone a SERP API zone?)")
    return [_row(r.get("link"), r.get("title"), r.get("description"), None, q, "brightdata") for r in d.get("organic") or []
            if isinstance(r, dict) and r.get("link")]


def brave(key, q, days, country, page, call):
    status, d = call("GET", "https://api.search.brave.com/res/v1/web/search", headers={"X-Subscription-Token": key}, timeout=30,
                     params={"q": q, "count": 20, "offset": page - 1, "freshness": _brave_freshness(days),
                             "country": (country or "us").upper().replace("GB", "GB")})
    if status >= 400:
        raise ApiError(status, f"Brave HTTP {status}")
    return [_row(r.get("url"), r.get("title"), r.get("description"), r.get("age"), q, "brave")
            for r in ((d or {}).get("web") or {}).get("results") or [] if r.get("url")]


def apify(key, q, days, country, page, call):
    import lead_sources
    rows = lead_sources.google([q], country, page, call=call)
    return [{**r, "provider": "apify", "source": "serp"} for r in rows]


FN = {"serper": serper, "serpapi": serpapi, "brightdata": brightdata, "brave": brave, "apify": apify}


def configured():
    order = [x.strip().lower() for x in setting("SERP_PROVIDERS", ",".join(PROVIDERS)).split(",") if x.strip()]
    return [(n, secret(PROVIDERS[n])) for n in order if n in PROVIDERS and secret(PROVIDERS[n])]


def search(q, days=7, country="us", pages=1, call=api_json, providers=None):
    """One query through the first working provider. Returns (rows, provider, errors)."""
    providers = providers if providers is not None else configured()
    if not providers:
        raise UserError("no SERP key — set SERPER_API_KEY (cheapest), SERPAPI_API_KEY, BRIGHTDATA_API_KEY, BRAVE_API_KEY or "
                        "APIFY_TOKEN in ~/.ai-sales-team/.env, or run the queries in your agent's own web search")
    errors = []
    for name, key in providers:
        try:
            rows = []
            for page in range(1, int(pages) + 1):
                got = FN[name](key, q, days, country, page, call)
                rows += got
                if len(got) < 8:                 # last page reached
                    break
            return rows, name, errors
        except ApiError as exc:
            errors.append(f"{name}: {exc}")
            continue
    return [], None, errors


def hunt(days=7, pages=2, max_queries=20, platforms=None, signals=False, call=api_json, lib=None):
    lib = lib or query_library.auto()
    queries = [q for q in lib["google_xray"] if (signals or q["platform"] != "signal")
               and (not platforms or q["platform"] in platforms)]
    countries = lib.get("google_countries") or ["us"]
    providers = configured()
    if not providers:
        raise UserError("no SERP key — set SERPER_API_KEY (cheapest) or another provider; see `serp.py providers`")
    posts, errors, used, calls = [], [], {}, 0
    for i, q in enumerate(queries[:max_queries]):
        country = countries[i % len(countries)]               # spread queries across target countries
        rows, prov, errs = search(q["query"], days, country, pages, call, providers)
        errors += errs
        calls += pages
        if prov:
            used[prov] = used.get(prov, 0) + 1
        for r in rows:
            r["query"] = q["id"]
        posts += rows
        if errs and not prov and all(" 401" in e or " 403" in e or "HTTP 401" in e or "HTTP 403" in e for e in errs):
            errors.append("stopped: every provider refused the key")
            break
    return posts, errors, {"queries_run": min(len(queries), max_queries), "providers_used": used,
                           "approx_calls": calls, "countries": countries}


def main(argv=None):
    ap = argparse.ArgumentParser(description="SERP lead engine: X-ray queries through Serper / SerpAPI / Bright Data / Brave / Apify.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hunt"); h.add_argument("--days", type=int, default=7); h.add_argument("--pages", type=int, default=2)
    h.add_argument("--max-queries", type=int, default=20); h.add_argument("--platform", help="comma list, e.g. linkedin,reddit,quora")
    h.add_argument("--signals", action="store_true", help="also run hiring-signal queries"); h.add_argument("--save")
    h.add_argument("--no-dedupe", action="store_true")
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--days", type=int, default=7)
    s.add_argument("--country", default="us"); s.add_argument("--pages", type=int, default=1)
    s.add_argument("--score", action="store_true", help="intent-score the results")
    sub.add_parser("providers")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "providers":
            prov = configured()
            n = 20 * 2
            out = {"configured": [p for p, _ in prov], "all": list(PROVIDERS), "order_setting": "SERP_PROVIDERS",
                   "hunt_estimate": {p: f"~${COST_PER_1K[p] * n / 1000:.2f} for 20 queries × 2 pages" for p, _ in prov},
                   "next": "Cheapest: SERPER_API_KEY from serper.dev" if not prov else "Ready: python serp.py hunt"}
        elif a.cmd == "search":
            rows, prov, errs = search(a.query, a.days, a.country, a.pages)
            out = {"provider": prov, "results": rows, "errors": errs}
            if a.score:
                import lead_sources
                out = {**lead_sources.finish(rows, errs), "provider": prov}
        else:
            import lead_sources
            plats = [p.strip() for p in a.platform.split(",")] if a.platform else None
            posts, errors, meta = hunt(a.days, a.pages, a.max_queries, plats, a.signals)
            out = {**lead_sources.finish(posts, errors, a.save, not a.no_dedupe), **meta}
        emit({"ok": True, "data": out})
    except (UserError, ApiError) as exc:
        emit({"ok": False, "error": str(exc)}, 2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SERP lead engine: Google results are the cheapest, widest lead source — one X-ray query searches LinkedIn posts,
Reddit, Quora, X, Facebook groups, Indie Hackers, Upwork jobs and hiring pages at once. This runs the query library
(built from SELLER-PROFILE.json) through whichever SERP API you have, with a recency filter, several pages and your
target countries, then intent-scores every result and drops sellers, job ads and excluded markets.

Bright Data is the provider (BRIGHTDATA_API_KEY + a SERP zone in BRIGHTDATA_ZONE). Others stay available only if
you list them yourself in SERP_PROVIDERS (default: brightdata).

Freshness is the point: a buyer who posted an hour ago hasn't hired anyone yet.
  - `--hours N` searches only the last N hours (Google tbs=qdr:hN), `--days N` the last N days; results sorted by date.
  - Every result gets `posted_at` / `age_hours`: exact for LinkedIn posts and X/Twitter (the time is encoded in the
    post ID), else parsed from the snippet ("3 hours ago", "Nov 1, 2026"). Newest first.
  - `watch` runs the profile's queries for the time since the last watch (1-24 h), keeps only results never seen
    before, stores them as fresh leads for today's agenda (`pipeline.py today` shows them first) and prints them.
    Schedule it every 1-2 hours (autopilot.py does it when HUNT_EVERY_HOURS is set).

Providers (tried in SERP_PROVIDERS order; one that fails or has no key is skipped):
    serper      SERPER_API_KEY      POST https://google.serper.dev/search          (X-API-KEY; ~ $1 / 1,000 searches)
    serpapi     SERPAPI_API_KEY     GET  https://serpapi.com/search.json            (engine=google)
    brightdata  BRIGHTDATA_API_KEY  POST https://api.brightdata.com/request          (SERP zone, parsed_light)
    brave       BRAVE_API_KEY       GET  https://api.search.brave.com/res/v1/web/search (X-Subscription-Token)
    apify       APIFY_TOKEN         apify/google-search-scraper
Default: brightdata only.

Usage (every command prints one JSON object):
    python serp.py watch [--max-queries 12] [--pages 1]                 # newest leads since the last watch → agenda
    python serp.py hunt [--hours 24 | --days 7] [--pages 2] [--max-queries 20] [--platform linkedin,reddit] [--save hunt.json]
    python serp.py fresh [--hours 48]                                    # fresh leads waiting to be judged
    python serp.py search 'site:linkedin.com/posts "looking for" "Shopify developer"' [--days 7] [--country us] [--pages 1]
    python serp.py providers          # which providers have keys, in which order, and the cost of a hunt
Signal queries (companies hiring for the role you replace) run with --signals.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
import intent_scan  # noqa: E402
import query_library  # noqa: E402
from sales_common import ApiError, api_json, data_home, emit, secret, setting  # noqa: E402

PROVIDERS = {"serper": "SERPER_API_KEY", "serpapi": "SERPAPI_API_KEY", "brightdata": "BRIGHTDATA_API_KEY",
             "brave": "BRAVE_API_KEY", "apify": "APIFY_TOKEN"}
COST_PER_1K = {"serper": 1.0, "serpapi": 15.0, "brightdata": 1.5, "brave": 5.0, "apify": 4.5}   # rough USD, for the estimate


class UserError(Exception):
    pass


def _tbs(days=None, hours=None, sort_by_date=True):
    if hours:
        base = "qdr:h" if int(hours) <= 1 else f"qdr:h{int(hours)}"
    else:
        base = {1: "qdr:d", 7: "qdr:w", 30: "qdr:m", 365: "qdr:y"}.get(int(days or 7), f"qdr:d{max(1, int(days or 7))}")
    return base + (",sbd:1" if sort_by_date else "")


# ------------------------------------------------------------------------------------------- post time

TWITTER_EPOCH_MS = 1288834974657
REL = re.compile(r"\b(\d+)\s*(minute|min|hour|hr|day|week|month)s?\s+ago\b", re.I)
ABS = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),\s+(\d{4})\b")


def post_time(url, *texts, now=None):
    """(datetime UTC, how) for a result: exact from LinkedIn/X IDs, else from 'N hours ago' / 'Nov 1, 2026' in the snippet."""
    now = now or datetime.now(timezone.utc)
    u = url or ""
    m = re.search(r"linkedin\.com/.*?(?:activity|ugcPost|share)[:-](\d{18,20})", u) or \
        re.search(r"linkedin\.com/posts/[^?]*?-(\d{18,20})(?:-|$|/|\?)", u)
    if m:
        return datetime.fromtimestamp((int(m.group(1)) >> 22) / 1000, timezone.utc), "linkedin-id"
    m = re.search(r"(?:x|twitter)\.com/[^/]+/status/(\d{15,20})", u)
    if m:
        return datetime.fromtimestamp(((int(m.group(1)) >> 22) + TWITTER_EPOCH_MS) / 1000, timezone.utc), "x-id"
    for t in texts:
        if not t:
            continue
        m = REL.search(str(t))
        if m:
            n, unit = int(m.group(1)), m.group(2).lower()
            delta = {"minute": timedelta(minutes=n), "min": timedelta(minutes=n), "hour": timedelta(hours=n), "hr": timedelta(hours=n),
                     "day": timedelta(days=n), "week": timedelta(weeks=n), "month": timedelta(days=30 * n)}[unit]
            return now - delta, "snippet-relative"
        m = ABS.search(str(t))
        if m:
            try:
                return datetime.strptime(f"{m.group(1)[:3]} {m.group(2)} {m.group(3)}", "%b %d %Y").replace(tzinfo=timezone.utc), "snippet-date"
            except ValueError:
                pass
    return None, None


def stamp(rows, now=None):
    """Add posted_at / age_hours / posted_days_ago and sort newest first (unknown ages last)."""
    now = now or datetime.now(timezone.utc)
    for r in rows:
        t, how = post_time(r.get("url"), r.get("posted"), r.get("text"), now=now)
        if t and t <= now + timedelta(minutes=5):
            r["posted_at"], r["age_hours"], r["age_source"] = t.replace(microsecond=0).isoformat(), round((now - t).total_seconds() / 3600, 1), how
            r["posted_days_ago"] = int((now - t).total_seconds() // 86400)
    return sorted(rows, key=lambda r: r.get("age_hours") if r.get("age_hours") is not None else 1e9)


def _brave_freshness(days):
    d = int(days)
    return "pd" if d <= 1 else "pw" if d <= 7 else "pm" if d <= 31 else "py"


def _row(url, title, text, posted, query, provider):
    return {"url": url, "title": title or "", "text": text or "", "posted": posted, "query": query, "provider": provider,
            "source": "serp", "platform": intent_scan.platform_of(url or ""), "author": None}


def serper(key, q, days, country, page, call, hours=None):
    status, d = call("POST", "https://google.serper.dev/search", headers={"X-API-KEY": key}, timeout=30,
                     body={"q": q, "gl": country or "us", "hl": "en", "num": 10, "tbs": _tbs(days, hours), "page": page})
    if status >= 400:
        raise ApiError(status, f"Serper HTTP {status}: {str((d or {}).get('message') or d)[:120]}")
    return [_row(r.get("link"), r.get("title"), r.get("snippet"), r.get("date"), q, "serper") for r in (d or {}).get("organic") or []
            if r.get("link")]


def serpapi(key, q, days, country, page, call, hours=None):
    status, d = call("GET", "https://serpapi.com/search.json", timeout=40,
                     params={"engine": "google", "q": q, "api_key": key, "gl": country or "us", "hl": "en", "num": 10,
                             "tbs": _tbs(days, hours), "start": (page - 1) * 10})
    if status >= 400 or (d or {}).get("error"):
        raise ApiError(status, f"SerpAPI: {(d or {}).get('error') or 'HTTP ' + str(status)}")
    return [_row(r.get("link"), r.get("title"), r.get("snippet"), r.get("date"), q, "serpapi")
            for r in (d or {}).get("organic_results") or [] if r.get("link")]


def brightdata(key, q, days, country, page, call, hours=None):
    params = {"q": q, "tbs": _tbs(days, hours), "num": 10, "hl": "en", "start": (page - 1) * 10}
    if country:
        params["gl"] = country
    status, d = call("POST", "https://api.brightdata.com/request", headers={"Authorization": f"Bearer {key}"}, timeout=60,
                     body={"zone": setting("BRIGHTDATA_ZONE", "serp_api1"), "url": "https://www.google.com/search?" + urlencode(params),
                           "format": "raw", "data_format": "parsed_light"})
    if status >= 400 or not isinstance(d, dict) or "organic" not in d:
        raise ApiError(status, f"Bright Data HTTP {status} (is the zone a SERP API zone?)")
    return [_row(r.get("link"), r.get("title"), r.get("description"), r.get("date") or r.get("extensions"), q, "brightdata")
            for r in d.get("organic") or [] if isinstance(r, dict) and r.get("link")]


def brave(key, q, days, country, page, call, hours=None):
    status, d = call("GET", "https://api.search.brave.com/res/v1/web/search", headers={"X-Subscription-Token": key}, timeout=30,
                     params={"q": q, "count": 20, "offset": page - 1, "freshness": "pd" if hours else _brave_freshness(days),
                             "country": (country or "us").upper().replace("GB", "GB")})
    if status >= 400:
        raise ApiError(status, f"Brave HTTP {status}")
    return [_row(r.get("url"), r.get("title"), r.get("description"), r.get("age"), q, "brave")
            for r in ((d or {}).get("web") or {}).get("results") or [] if r.get("url")]


def apify(key, q, days, country, page, call, hours=None):
    import lead_sources
    rows = lead_sources.google([q], country, page, call=call)
    return [{**r, "provider": "apify", "source": "serp"} for r in rows]


FN = {"serper": serper, "serpapi": serpapi, "brightdata": brightdata, "brave": brave, "apify": apify}


def configured():
    order = [x.strip().lower() for x in setting("SERP_PROVIDERS", "brightdata").split(",") if x.strip()]
    return [(n, secret(PROVIDERS[n])) for n in order if n in PROVIDERS and secret(PROVIDERS[n])]


def search(q, days=7, country="us", pages=1, call=api_json, providers=None, hours=None):
    """One query through the first working provider. Returns (rows, provider, errors)."""
    providers = providers if providers is not None else configured()
    if not providers:
        raise UserError("no SERP key — set BRIGHTDATA_API_KEY (and BRIGHTDATA_ZONE, your SERP API zone) in "
                        "~/.ai-sales-team/.env, or run the queries in your agent's own web search")
    errors = []
    for name, key in providers:
        try:
            rows = []
            for page in range(1, int(pages) + 1):
                got = FN[name](key, q, days, country, page, call, hours)
                rows += got
                if len(got) < 8:                 # last page reached
                    break
            return stamp(rows), name, errors
        except ApiError as exc:
            errors.append(f"{name}: {exc}")
            continue
    return [], None, errors


def hunt(days=7, pages=2, max_queries=20, platforms=None, signals=False, call=api_json, lib=None, hours=None):
    lib = lib or query_library.auto()
    queries = [q for q in lib["google_xray"] if (signals or q["platform"] != "signal")
               and (not platforms or q["platform"] in platforms)]
    # learning loop (learn.py report --apply): skip queries that never produced a positive reply, run winners first
    import learn
    L = learn.learned()
    drop, w = set(L.get("drop_queries") or []), L.get("query_weights") or {}
    dropped = [q["id"] for q in queries if f"serp:{q['id']}" in drop]
    queries = sorted((q for q in queries if f"serp:{q['id']}" not in drop), key=lambda q: -float(w.get(f"serp:{q['id']}", 1.0)))
    countries = lib.get("google_countries") or ["us"]
    providers = configured()
    if not providers:
        raise UserError("no SERP key — set BRIGHTDATA_API_KEY and BRIGHTDATA_ZONE; see `serp.py providers`")
    posts, errors, used, calls = [], [], {}, 0
    for i, q in enumerate(queries[:max_queries]):
        country = countries[i % len(countries)]               # spread queries across target countries
        rows, prov, errs = search(q["query"], days, country, pages, call, providers, hours)
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
    return stamp(posts), errors, {"queries_run": min(len(queries), max_queries), "providers_used": used,
                                  "approx_calls": calls, "countries": countries, "window": f"{hours} h" if hours else f"{days} d",
                                  "dropped_by_learning": dropped}


# ------------------------------------------------------------------------------------------- watch (newest only)

def _store():
    return data_home() / "fresh_leads.json"


def load_fresh():
    try:
        return json.loads(_store().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"last_watch": None, "leads": []}


def save_fresh(st):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    st["leads"] = [x for x in st["leads"] if (x.get("found_at") or "") >= cutoff][-500:]
    _store().write_text(json.dumps(st, indent=1, ensure_ascii=False), encoding="utf-8")


def watch(max_queries=12, pages=1, call=api_json, now=None):
    """Search only the hours since the last watch; keep results nobody has seen; queue them for the agenda."""
    import lead_sources
    now = now or datetime.now(timezone.utc)
    st = load_fresh()
    last = datetime.fromisoformat(st["last_watch"]) if st.get("last_watch") else None
    hours = 24 if not last else max(1, min(24, int((now - last).total_seconds() // 3600) + 1))
    posts, errors, meta = hunt(None, pages, max_queries, None, False, call, hours=hours)
    scored = lead_sources.finish(posts, errors)            # de-dupes against everything seen before, drops sellers/markets
    fresh = [{**c, "found_at": now.replace(microsecond=0).isoformat(), "judged": False} for c in scored["candidates"]]
    st["leads"] += fresh
    st["last_watch"] = now.replace(microsecond=0).isoformat()
    save_fresh(st)
    newest = sorted(fresh, key=lambda c: c.get("age_hours") if c.get("age_hours") is not None else 1e9)
    return {"window_hours": hours, "new_buyers": len(fresh), "rejected": scored["rejected"],
            "excluded_market": scored.get("excluded_market", 0), "duplicates_skipped": scored["duplicates_skipped"],
            "leads": [{k: c.get(k) for k in ("url", "platform", "author", "title", "age_hours", "posted_at", "score", "services",
                                             "intent_phrases", "contact_in_post", "query")} for c in newest],
            **meta, "errors": errors,
            "next": ("Judge these now (vintoria-lead-hunt step 3) — answer the freshest within the hour." if fresh else
                     "No new buyers since the last watch.")}


def fresh_leads(hours=48, include_judged=False):
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    return [x for x in load_fresh()["leads"] if (x.get("found_at") or "") >= cutoff and (include_judged or not x.get("judged"))]


def mark_judged(urls):
    st = load_fresh()
    n = 0
    for x in st["leads"]:
        if x.get("url") in urls and not x.get("judged"):
            x["judged"] = True
            n += 1
    save_fresh(st)
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description="SERP lead engine: X-ray queries through Serper / SerpAPI / Bright Data / Brave / Apify.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("watch"); w.add_argument("--max-queries", type=int, default=int(setting("HUNT_MAX_QUERIES", "12")))
    w.add_argument("--pages", type=int, default=1)
    fr = sub.add_parser("fresh"); fr.add_argument("--hours", type=int, default=48); fr.add_argument("--all", action="store_true")
    jd = sub.add_parser("judged"); jd.add_argument("url", nargs="+", help="mark fresh leads as judged (they leave the agenda)")
    h = sub.add_parser("hunt"); h.add_argument("--days", type=int, default=7); h.add_argument("--hours", type=int)
    h.add_argument("--pages", type=int, default=2)
    h.add_argument("--max-queries", type=int, default=20); h.add_argument("--platform", help="comma list, e.g. linkedin,reddit,quora")
    h.add_argument("--signals", action="store_true", help="also run hiring-signal queries"); h.add_argument("--save")
    h.add_argument("--no-dedupe", action="store_true")
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--days", type=int, default=7); s.add_argument("--hours", type=int)
    s.add_argument("--country", default="us"); s.add_argument("--pages", type=int, default=1)
    s.add_argument("--score", action="store_true", help="intent-score the results")
    sub.add_parser("providers")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "watch":
            out = watch(a.max_queries, a.pages)
        elif a.cmd == "fresh":
            out = {"fresh_leads": fresh_leads(a.hours, a.all)}
        elif a.cmd == "judged":
            out = {"marked": mark_judged(set(a.url))}
        elif a.cmd == "providers":
            prov = configured()
            n = 20 * 2
            out = {"configured": [p for p, _ in prov], "all": list(PROVIDERS), "order_setting": "SERP_PROVIDERS",
                   "hunt_estimate": {p: f"~${COST_PER_1K[p] * n / 1000:.2f} for 20 queries × 2 pages" for p, _ in prov},
                   "next": "Set BRIGHTDATA_API_KEY and BRIGHTDATA_ZONE (your SERP API zone)" if not prov else "Ready: python serp.py watch"}
        elif a.cmd == "search":
            rows, prov, errs = search(a.query, a.days, a.country, a.pages, hours=a.hours)
            out = {"provider": prov, "results": rows, "errors": errs}
            if a.score:
                import lead_sources
                out = {**lead_sources.finish(rows, errs), "provider": prov}
        else:
            import lead_sources
            plats = [p.strip() for p in a.platform.split(",")] if a.platform else None
            posts, errors, meta = hunt(a.days, a.pages, a.max_queries, plats, a.signals, hours=a.hours)
            out = {**lead_sources.finish(posts, errors, a.save, not a.no_dedupe), **meta}
        emit({"ok": True, "data": out})
    except (UserError, ApiError) as exc:
        emit({"ok": False, "error": str(exc)}, 2)


if __name__ == "__main__":
    main()

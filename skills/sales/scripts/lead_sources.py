#!/usr/bin/env python3
"""
Lead sources and internet research through Apify actors (and Bright Data as a fallback for Google).

Finds public posts where people ask for a service — LinkedIn posts (HarvestAPI actor, no cookies), Google
X-ray results, Reddit — normalizes them, and scores them with intent_scan.py in the same run. Also
researches one prospect across the web (reviews, news, social profiles, directories) and saves the results
as evidence the claim checker can use.

Usage (every command prints one JSON object):
    python lead_sources.py linkedin --query "need a website developer" --query "looking for SEO agency" \
        [--posted week] [--max 50] [--save hunt.json]
    python lead_sources.py google --query 'site:linkedin.com/posts "need a website"' [--country in] [--pages 1]
    python lead_sources.py reddit --query "looking for web developer" [--max 50]
    python lead_sources.py hunt [--services web,seo] [--posted week] [--max 30]   # default queries, all sources
    python lead_sources.py actor some-user/some-actor --input input.json         # any Apify actor
    python lead_sources.py research acme.com [--name "Acme Bakery"] [--city Pune]
    python lead_sources.py queries                                               # show the default queries

Keys and settings (env or ~/.ai-sales-team/.env):
    APIFY_TOKEN              required for linkedin / reddit / actor; google uses it if set, else BRIGHTDATA_API_KEY
    APIFY_LINKEDIN_ACTOR     default harvestapi/linkedin-post-search
    APIFY_GOOGLE_ACTOR       default apify/google-search-scraper
    APIFY_REDDIT_ACTOR       default trudax/reddit-scraper-lite
    APIFY_MAX_USD            spend cap per actor run (default 1.00), sent as maxTotalChargeUsd
    APIFY_MAX_RUNS           actor runs per command (default 6)

Apify API: POST https://api.apify.com/v2/acts/<user>~<actor>/run-sync-get-dataset-items (Bearer token),
waits up to 5 minutes and returns the dataset items. Actor inputs differ between publishers; the defaults
below match the actors named above, and every output is read defensively (several field names accepted).
Only public data is collected; nothing is posted or messaged.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_scan  # noqa: E402
from sales_common import ApiError, api_json, domain_slug, emit, secret, setting  # noqa: E402

APIFY = "https://api.apify.com/v2"
DEFAULT_ACTORS = {"linkedin": "harvestapi/linkedin-post-search", "google": "apify/google-search-scraper",
                  "reddit": "trudax/reddit-scraper-lite"}
POSTED = ["1h", "24h", "week", "month", "3months", "6months", "year"]

# Plain keyword searches for LinkedIn/Reddit (their own search, not Google) per service.
SERVICE_QUERIES = {
    "web": ["looking for a web developer", "need a website for my business", "recommend a website designer",
            "website banwana hai", "need a shopify developer"],
    "app": ["looking for an app developer", "need a mobile app developed", "app banwana hai"],
    "seo": ["looking for an SEO agency", "need help with SEO", "recommend SEO expert", "seo karwana hai"],
    "marketing": ["looking for a digital marketing agency", "need a social media manager", "recommend a marketing agency"],
    "design": ["looking for a logo designer", "need a branding agency", "recommend a UI UX designer"],
    "software": ["looking for a CRM developer", "need automation help for my business", "need a software developer for"],
}


class UserError(Exception):
    pass


# ----------------------------------------------------------------------------------------------- Apify

def actor_path(actor):
    a = (actor or "").strip()
    if not re.fullmatch(r"[\w.-]+[/~][\w.-]+|[A-Za-z0-9]{17}", a):
        raise UserError(f"'{actor}' is not an Apify actor id (user/actor-name)")
    return a.replace("/", "~")


def run_actor(actor, actor_input, max_items=None, call=api_json):
    token = secret("APIFY_TOKEN")
    if not token:
        raise UserError("APIFY_TOKEN is not set — add it to ~/.ai-sales-team/.env (console.apify.com → Settings → API)")
    params = {"timeout": 290, "maxTotalChargeUsd": setting("APIFY_MAX_USD", "1.00")}
    if max_items:
        params["maxItems"] = int(max_items)
    status, data = call("POST", f"{APIFY}/acts/{actor_path(actor)}/run-sync-get-dataset-items",
                        headers={"Authorization": f"Bearer {token}"}, body=actor_input, params=params, timeout=300, retries=1)
    if status == 408:
        raise ApiError(status, f"{actor}: run took longer than 5 minutes — lower --max or use fewer queries")
    if status >= 400:
        msg = (data.get("error") or {}).get("message") if isinstance(data, dict) else None
        raise ApiError(status, f"{actor}: Apify HTTP {status}" + (f" — {msg}" if msg else ""))
    if isinstance(data, dict):
        data = data.get("items") or data.get("data") or []
    return [x for x in data if isinstance(x, dict)]


# ----------------------------------------------------------------------------------------------- normalize

def _first(d, *keys):
    for k in keys:
        cur = d
        for part in k.split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
        if cur not in (None, "", [], {}):
            return cur
    return None


def normalize(item, source, query=None):
    """One dataset item → {url, text, title, author, author_url, author_headline, posted, platform, source, query}."""
    text = _first(item, "content", "text", "postText", "body", "commentary", "description", "selftext") or ""
    title = _first(item, "title") or ""
    author = _first(item, "author.name", "authorName", "author.fullName", "username", "user.name", "author")
    if isinstance(author, dict):
        author = _first(author, "name", "fullName", "publicIdentifier")
    url = _first(item, "linkedinUrl", "postUrl", "url", "shareUrl", "link", "permalink")
    return {"url": str(url or ""), "text": str(text)[:3000], "title": str(title)[:300],
            "author": str(author) if author else None,
            "author_url": _first(item, "author.linkedinUrl", "author.url", "authorProfileUrl", "authorUrl", "author.profileUrl"),
            "author_headline": _first(item, "author.info", "author.headline", "author.position", "authorHeadline"),
            "posted": _first(item, "postedAt.date", "postedAt", "postedAgoText", "createdAt", "date", "postedDate", "created_utc"),
            "engagement": _first(item, "engagement", "stats"), "platform": intent_scan.platform_of(str(url or "")),
            "source": source, "query": query}


def google_items(items, query=None):
    """apify/google-search-scraper returns one item per results page with organicResults[]."""
    out = []
    for it in items:
        rows = it.get("organicResults") if isinstance(it.get("organicResults"), list) else [it]
        q = _first(it, "searchQuery.term") or query
        for r in rows:
            if isinstance(r, dict) and (r.get("url") or r.get("link")):
                out.append({"url": r.get("url") or r.get("link"), "title": r.get("title") or "",
                            "text": r.get("description") or r.get("snippet") or "", "posted": r.get("date"),
                            "platform": intent_scan.platform_of(r.get("url") or r.get("link") or ""), "source": "google",
                            "query": q, "author": None})
    return out


# ----------------------------------------------------------------------------------------------- sources

def linkedin(queries, posted="week", max_posts=30, call=api_json):
    if posted not in POSTED:
        raise UserError(f"--posted must be one of {POSTED}")
    actor = setting("APIFY_LINKEDIN_ACTOR", DEFAULT_ACTORS["linkedin"])
    inp = {"searchQueries": list(queries), "maxPosts": int(max_posts), "postedLimit": posted, "sortBy": "date"}
    items = run_actor(actor, inp, max_items=int(max_posts) * len(queries), call=call)
    return [normalize(i, "linkedin", None) for i in items]


def google(queries, country="", pages=1, call=api_json):
    if secret("APIFY_TOKEN"):
        actor = setting("APIFY_GOOGLE_ACTOR", DEFAULT_ACTORS["google"])
        inp = {"queries": "\n".join(queries), "maxPagesPerQuery": int(pages), "resultsPerPage": 10}
        if country:
            inp["countryCode"] = country.lower()
        return google_items(run_actor(actor, inp, call=call))
    if secret("BRIGHTDATA_API_KEY"):
        out = []
        for q in queries:
            for r in intent_scan.serp(q, 30, gl=country, call=call):
                out.append({"url": r["link"], "title": r.get("title", ""), "text": r.get("description", ""), "source": "google",
                            "query": q, "platform": intent_scan.platform_of(r["link"]), "author": None, "posted": None})
        return out
    raise UserError("Google search needs APIFY_TOKEN or BRIGHTDATA_API_KEY — or use your agent's own web search")


def reddit(queries, max_items=30, call=api_json):
    actor = setting("APIFY_REDDIT_ACTOR", DEFAULT_ACTORS["reddit"])
    inp = {"searches": list(queries), "searchPosts": True, "searchComments": False, "searchCommunities": False,
           "searchUsers": False, "sort": "new", "time": "week", "maxItems": int(max_items), "maxPostCount": int(max_items)}
    return [normalize(i, "reddit") for i in run_actor(actor, inp, max_items=max_items, call=call)
            if (i.get("dataType") in (None, "post"))]


def default_queries(services):
    out = []
    for s in services:
        out += SERVICE_QUERIES.get(s, [])
    return out or SERVICE_QUERIES["web"]


def hunt(services, posted="week", max_posts=30, country="", call=api_json):
    """All sources with the default queries; every source that fails is reported, not fatal."""
    max_runs = int(setting("APIFY_MAX_RUNS", "6"))
    kw = default_queries(services)
    posts, errors, runs = [], [], 0
    plan = [("linkedin", lambda: linkedin(kw[:5], posted, max_posts, call)),
            ("google", lambda: google([q["query"] for q in intent_scan.DEFAULT_QUERIES], country, 1, call)),
            ("reddit", lambda: reddit(kw[:3], max_posts, call))]
    for name, fn in plan:
        if runs >= max_runs:
            errors.append(f"{name}: skipped (APIFY_MAX_RUNS={max_runs})")
            continue
        try:
            got = fn()
            runs += 1
            posts += got
        except (UserError, ApiError) as exc:
            errors.append(f"{name}: {exc}")
    return posts, errors


# ----------------------------------------------------------------------------------------------- research

def research_queries(domain, name=None, city=None):
    n = f'"{name}"' if name else f'"{domain}"'
    loc = f" {city}" if city else ""
    return {
        "mentions": f'{n}{loc} -site:{domain}',
        "reviews": f'{n}{loc} reviews OR rating OR "google reviews"',
        "news": f'{n} (launch OR funding OR expands OR opens OR award OR hiring)',
        "linkedin": f'site:linkedin.com/company OR site:linkedin.com/in {n}',
        "social": f'(site:instagram.com OR site:facebook.com OR site:youtube.com) {n}',
        "directories": f'(site:justdial.com OR site:yelp.com OR site:clutch.co OR site:trustpilot.com OR site:indiamart.com) {n}',
        "hiring": f'{n} (hiring OR careers OR "job opening") (marketing OR developer OR designer)',
    }


def research(domain, name=None, city=None, out_dir=None, call=api_json):
    slug = domain_slug(domain)
    qs = research_queries(slug, name, city)
    rows = google(list(qs.values()), call=call)
    by_query = {v: k for k, v in qs.items()}
    sections = {k: [] for k in qs}
    for r in rows:
        k = by_query.get(r.get("query"))
        if k is None:  # some actors rewrite the query; fall back to matching the domain/name
            k = "mentions"
        if len(sections[k]) < 8 and r["url"] not in [x["url"] for x in sections[k]]:
            sections[k].append({"url": r["url"], "title": r["title"], "snippet": r["text"]})
    # Facts in the shape claim_check.py reads: every statement is a search result, quoted with its URL.
    facts = [{"key": f"web_{k}", "statement": f"{x['title']}: {x['snippet']}", "evidence": x["url"]}
             for k, xs in sections.items() for x in xs]
    result = {"domain": slug, "name": name, "searched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
              "queries": qs, "sections": sections, "facts": facts,
              "note": "Search snippets are leads to check, not facts: open a page before stating anything from it."}
    path = Path(out_dir or Path("prospects") / slug) / "WEB-RESEARCH.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    result["saved"] = str(path)
    return result


# ----------------------------------------------------------------------------------------------- CLI

def finish(posts, errors, save=None, dedupe=True):
    out = intent_scan.scan(posts, dedupe=dedupe)
    out["scanned"], out["errors"] = len(posts), errors
    out["by_source"] = {s: sum(1 for p in posts if p.get("source") == s) for s in sorted({p.get("source") for p in posts})}
    if save:
        Path(save).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        out["saved"] = save
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Apify / Google lead sources and prospect web research.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("linkedin", "google", "reddit"):
        s = sub.add_parser(name)
        s.add_argument("--query", action="append", required=True)
        s.add_argument("--max", type=int, default=30)
        s.add_argument("--posted", default="week", choices=POSTED)
        s.add_argument("--country", default="")
        s.add_argument("--pages", type=int, default=1)
        s.add_argument("--save"); s.add_argument("--no-dedupe", action="store_true")
    h = sub.add_parser("hunt"); h.add_argument("--services", default="web"); h.add_argument("--posted", default="week", choices=POSTED)
    h.add_argument("--max", type=int, default=30); h.add_argument("--country", default=""); h.add_argument("--save")
    h.add_argument("--no-dedupe", action="store_true")
    ac = sub.add_parser("actor"); ac.add_argument("actor"); ac.add_argument("--input", required=True, help="JSON file")
    ac.add_argument("--max", type=int); ac.add_argument("--save"); ac.add_argument("--no-dedupe", action="store_true")
    ac.add_argument("--raw", action="store_true", help="return the items as-is instead of intent-scoring them")
    rs = sub.add_parser("research"); rs.add_argument("domain"); rs.add_argument("--name"); rs.add_argument("--city")
    rs.add_argument("--out-dir")
    sub.add_parser("queries")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "queries":
            out = {"keyword_queries": SERVICE_QUERIES, "google_xray": intent_scan.DEFAULT_QUERIES, "actors": {
                k: setting(f"APIFY_{k.upper()}_ACTOR", v) for k, v in DEFAULT_ACTORS.items()}}
        elif a.cmd == "linkedin":
            out = finish(linkedin(a.query, a.posted, a.max), [], a.save, not a.no_dedupe)
        elif a.cmd == "google":
            out = finish(google(a.query, a.country, a.pages), [], a.save, not a.no_dedupe)
        elif a.cmd == "reddit":
            out = finish(reddit(a.query, a.max), [], a.save, not a.no_dedupe)
        elif a.cmd == "hunt":
            posts, errors = hunt([s.strip() for s in a.services.split(",") if s.strip()], a.posted, a.max, a.country)
            out = finish(posts, errors, a.save, not a.no_dedupe)
            if not posts and errors:
                emit({"ok": False, "error": "every source failed", "data": out}, 4)
        elif a.cmd == "actor":
            items = run_actor(a.actor, json.loads(Path(a.input).read_text(encoding="utf-8")), a.max)
            out = {"items": items, "count": len(items)} if a.raw else finish(
                [normalize(i, "apify:" + a.actor) for i in items], [], a.save, not a.no_dedupe)
        else:
            out = research(a.domain, a.name, a.city, a.out_dir)
        emit({"ok": True, "data": out})
    except (UserError, ApiError) as exc:
        emit({"ok": False, "error": str(exc)}, 2)


if __name__ == "__main__":
    main()

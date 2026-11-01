#!/usr/bin/env python3
"""
Lead sources: every place buyers ask for help, plus companies that show a need, and deep web research.

PEOPLE ASKING (intent posts → intent_scan scoring, sellers/job ads/job seekers rejected):
    linkedin     LinkedIn post search — Apify actor harvestapi/linkedin-post-search (no cookies)
    hackernews   Hacker News — free Algolia API: asks + the monthly "Freelancer? Seeking freelancer?" thread
    reddit       Reddit — r/forhire [Hiring], r/smallbusiness, r/startups, r/shopify ... (Apify, or free public JSON)
    x            X/Twitter search — Apify actor (default apidojo/tweet-scraper)
    facebook     Public Facebook groups you name — Apify actor apify/facebook-groups-scraper
    google       Google X-ray across LinkedIn, Reddit, X, FB groups, Quora, Indie Hackers, Upwork jobs, Hinglish
                 (Apify apify/google-search-scraper, or Bright Data)
COMPANIES WITH A NEED (outbound targets with signals):
    maps         Google Maps businesses (Apify compass/crawler-google-places): no website, low rating, few reviews
    producthunt  New Product Hunt launches (PRODUCTHUNT_TOKEN, free developer token) — need growth, SEO, design
ALL AT ONCE:
    hunt         every source you have keys for, with the query library for your services and location
RESEARCH:
    research     one prospect across the web: mentions, reviews, news, LinkedIn, social, directories, hiring

Usage (every command prints one JSON object):
    python lead_sources.py hunt --services web,seo [--location Pune] [--posted week] [--max 30] [--save hunt.json]
    python lead_sources.py linkedin [--query '...'] [--services web] [--posted week] [--max 50]
    python lead_sources.py hackernews [--services web] [--days 30]
    python lead_sources.py reddit [--services web,seo] [--max 30]
    python lead_sources.py x [--services web] [--max 50]
    python lead_sources.py facebook --group-url https://www.facebook.com/groups/... [--max 50]
    python lead_sources.py google [--query '...'] [--services web] [--location Pune] [--country in]
    python lead_sources.py maps --services web --location "Pune" [--max 40] [--add]
    python lead_sources.py producthunt [--days 7] [--max 30] [--add]
    python lead_sources.py actor some-user/some-actor --input input.json [--raw]
    python lead_sources.py research acme.com [--name "Acme Bakery"] [--city Pune]
    python lead_sources.py queries [--services web,seo] [--location Pune]

Keys / settings (env or ~/.ai-sales-team/.env): APIFY_TOKEN, PRODUCTHUNT_TOKEN, BRIGHTDATA_API_KEY;
APIFY_LINKEDIN_ACTOR, APIFY_GOOGLE_ACTOR, APIFY_REDDIT_ACTOR, APIFY_X_ACTOR, APIFY_FACEBOOK_ACTOR,
APIFY_MAPS_ACTOR (override the defaults below), APIFY_MAX_USD (spend cap per actor run, default 1.00),
APIFY_MAX_RUNS (actor runs per hunt, default 8).
Apify: POST https://api.apify.com/v2/acts/<user>~<actor>/run-sync-get-dataset-items (Bearer token, ≤ 5 min).
Hacker News: https://hn.algolia.com/api/v1 (no key). Product Hunt: POST https://api.producthunt.com/v2/api/graphql.
Reddit fallback: https://www.reddit.com/r/<sub>/search.json (no key; Reddit may rate-limit — Apify is steadier).
Only public data; nothing is posted, liked or messaged. Emails/phones written in a post are attached to the lead
(contact_in_post) so no email-finder credits are spent on them.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_scan  # noqa: E402
import query_library  # noqa: E402
from sales_common import ApiError, api_json, domain_slug, emit, secret, setting  # noqa: E402

APIFY = "https://api.apify.com/v2"
HN_API = "https://hn.algolia.com/api/v1"
PH_API = "https://api.producthunt.com/v2/api/graphql"
DEFAULT_ACTORS = {"linkedin": "harvestapi/linkedin-post-search", "google": "apify/google-search-scraper",
                  "reddit": "trudax/reddit-scraper-lite", "x": "apidojo/tweet-scraper",
                  "facebook": "apify/facebook-groups-scraper", "maps": "compass/crawler-google-places"}
POSTED = ["1h", "24h", "week", "month", "3months", "6months", "year"]


class UserError(Exception):
    pass


def actor_for(kind):
    return setting(f"APIFY_{kind.upper()}_ACTOR", DEFAULT_ACTORS[kind])


def _strip_html(s):
    s = re.sub(r"(?i)<br\s*/?>|</p>|<p>", "\n", s or "")
    return unescape(re.sub(r"<[^>]+>", " ", s)).strip()


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
    text = _first(item, "content", "text", "full_text", "fullText", "postText", "body", "commentary", "message",
                  "description", "selftext") or ""
    title = _first(item, "title") or ""
    author = _first(item, "author.name", "authorName", "author.fullName", "author.userName", "user.name", "username", "author")
    if isinstance(author, dict):
        author = _first(author, "name", "fullName", "userName", "publicIdentifier")
    url = _first(item, "linkedinUrl", "postUrl", "url", "twitterUrl", "shareUrl", "link", "permalink", "facebookUrl")
    if url and str(url).startswith("/r/"):
        url = "https://www.reddit.com" + str(url)
    return {"url": str(url or ""), "text": _strip_html(str(text))[:3000], "title": str(title)[:300],
            "author": str(author) if author else None,
            "author_url": _first(item, "author.linkedinUrl", "author.url", "authorProfileUrl", "authorUrl", "author.profileUrl",
                                 "user.profileUrl"),
            "author_headline": _first(item, "author.info", "author.headline", "author.position", "authorHeadline",
                                      "author.description"),
            "posted": _first(item, "postedAt.date", "postedAt", "postedAgoText", "createdAt", "created_at", "time", "date",
                             "postedDate", "created_utc"),
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


def _services(s):
    return [x.strip() for x in (s or "web").split(",") if x.strip()]


# ----------------------------------------------------------------------------------------------- people asking

def linkedin(queries, posted="week", max_posts=30, call=api_json):
    if posted not in POSTED:
        raise UserError(f"--posted must be one of {POSTED}")
    bad = [q for q in queries if not query_library.valid_linkedin(q)]
    if bad:
        raise UserError(f"LinkedIn allows ≤ 5 AND/OR/NOT and ≤ 500 chars per query: {bad[0]}")
    inp = {"searchQueries": list(queries), "maxPosts": int(max_posts), "postedLimit": posted, "sortBy": "date"}
    items = run_actor(actor_for("linkedin"), inp, max_items=int(max_posts) * len(queries), call=call)
    return [normalize(i, "linkedin") for i in items]


def google(queries, country="", pages=1, call=api_json):
    if secret("APIFY_TOKEN"):
        inp = {"queries": "\n".join(queries), "maxPagesPerQuery": int(pages), "resultsPerPage": 10}
        if country:
            inp["countryCode"] = country.lower()
        return google_items(run_actor(actor_for("google"), inp, call=call))
    if secret("BRIGHTDATA_API_KEY"):
        out = []
        for q in queries:
            for r in intent_scan.serp(q, 30, gl=country, call=call):
                out.append({"url": r["link"], "title": r.get("title", ""), "text": r.get("description", ""), "source": "google",
                            "query": q, "platform": intent_scan.platform_of(r["link"]), "author": None, "posted": None})
        return out
    raise UserError("Google search needs APIFY_TOKEN or BRIGHTDATA_API_KEY — or use your agent's own web search")


def reddit(plan, max_items=30, call=api_json):
    """plan = [{subreddit, query}] from query_library.reddit(). Apify if APIFY_TOKEN, else Reddit's public JSON."""
    if secret("APIFY_TOKEN"):
        searches = [f"subreddit:{p['subreddit']} {p['query']}" for p in plan]
        inp = {"searches": searches, "searchPosts": True, "searchComments": False, "searchCommunities": False,
               "searchUsers": False, "sort": "new", "time": "week", "maxItems": int(max_items), "maxPostCount": int(max_items)}
        return [normalize(i, "reddit") for i in run_actor(actor_for("reddit"), inp, max_items=max_items, call=call)
                if i.get("dataType") in (None, "post")]
    out, errors = [], []
    for p in plan:
        status, d = call("GET", f"https://www.reddit.com/r/{p['subreddit']}/search.json", timeout=20, retries=1,
                         params={"q": p["query"], "restrict_sr": 1, "sort": "new", "t": "week", "limit": min(100, max_items)})
        if status >= 400 or not isinstance(d, dict):
            errors.append(f"r/{p['subreddit']}: HTTP {status}")
            if status in (403, 429):
                break
            continue
        for c in (d.get("data") or {}).get("children") or []:
            x = c.get("data") or {}
            out.append({"url": "https://www.reddit.com" + (x.get("permalink") or ""), "title": x.get("title") or "",
                        "text": x.get("selftext") or "", "author": x.get("author"), "source": "reddit", "platform": "reddit",
                        "posted": datetime.fromtimestamp(x["created_utc"], timezone.utc).isoformat() if x.get("created_utc") else None,
                        "query": f"r/{p['subreddit']} {p['query']}", "flair": x.get("link_flair_text")})
    if errors and not out:
        raise UserError("Reddit public JSON blocked (" + "; ".join(errors[:3]) + ") — set APIFY_TOKEN for the Reddit actor")
    return out


def hackernews(queries, days=30, max_hits=50, seeking_thread=True, call=api_json):
    """Hacker News via Algolia (free): comments/stories matching the asks, plus SEEKING FREELANCER posts."""
    since = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    out = []
    for q in queries:
        status, d = call("GET", f"{HN_API}/search_by_date", timeout=20,
                         params={"query": q, "tags": "(story,comment)", "numericFilters": f"created_at_i>{since}",
                                 "hitsPerPage": max_hits})
        if status >= 400:
            raise ApiError(status, f"Hacker News API HTTP {status}")
        out += [_hn_hit(h, q) for h in (d or {}).get("hits") or []]
    if seeking_thread:
        status, d = call("GET", f"{HN_API}/search_by_date", timeout=20,
                         params={"query": '"Freelancer? Seeking freelancer?"', "tags": "story,author_whoishiring", "hitsPerPage": 1})
        hits = ((d or {}).get("hits") or []) if status < 400 else []
        if hits:
            sid = hits[0]["objectID"]
            status, d = call("GET", f"{HN_API}/search", timeout=20,
                             params={"query": "SEEKING FREELANCER", "tags": f"comment,story_{sid}", "hitsPerPage": 200})
            for h in (d or {}).get("hits") or []:
                text = _strip_html(h.get("comment_text") or "")
                if str(h.get("parent_id")) == str(sid) and re.search(r"seeking\s+freelancer", text, re.I):
                    out.append({**_hn_hit(h, "Seeking freelancer thread"), "text": text,
                                "intent_override": "SEEKING FREELANCER post in the monthly HN thread"})
    seen, final = set(), []
    for p in out:
        if p["url"] not in seen:
            seen.add(p["url"])
            final.append(p)
    return final


def _hn_hit(h, q):
    return {"url": f"https://news.ycombinator.com/item?id={h.get('objectID')}", "title": h.get("title") or h.get("story_title") or "",
            "text": _strip_html(h.get("comment_text") or h.get("story_text") or ""), "author": h.get("author"),
            "author_url": f"https://news.ycombinator.com/user?id={h.get('author')}" if h.get("author") else None,
            "posted": h.get("created_at"), "source": "hackernews", "platform": "hackernews", "query": q,
            "external_url": h.get("url") or h.get("story_url")}


def x_posts(queries, max_items=50, call=api_json):
    inp = {"searchTerms": list(queries), "maxItems": int(max_items), "sort": "Latest", "tweetLanguage": "en"}
    return [normalize(i, "x") for i in run_actor(actor_for("x"), inp, max_items=max_items, call=call)]


def facebook(group_urls, max_items=50, call=api_json):
    if not group_urls:
        raise UserError("give at least one public group: --group-url https://www.facebook.com/groups/<id>")
    inp = {"startUrls": [{"url": u} for u in group_urls], "resultsLimit": int(max_items), "viewOption": "CHRONOLOGICAL"}
    return [normalize(i, "facebook") for i in run_actor(actor_for("facebook"), inp, max_items=max_items, call=call)]


# ----------------------------------------------------------------------------------------------- companies with a need

def maps(searches, max_places=40, call=api_json):
    """Google Maps places with need signals for web / SEO / reputation offers."""
    inp = {"searchStringsArray": list(searches), "maxCrawledPlacesPerSearch": int(max_places), "language": "en",
           "skipClosedPlaces": True}
    out = []
    for p in run_actor(actor_for("maps"), inp, max_items=int(max_places) * len(searches), call=call):
        if p.get("permanentlyClosed"):
            continue
        site = p.get("website") or ""
        rating, reviews = p.get("totalScore"), p.get("reviewsCount") or 0
        signals = []
        if not site:
            signals.append("no website on Google Maps")
        elif re.search(r"(facebook|instagram|linktr\.ee|wa\.me|business\.site|wixsite|blogspot)", site, re.I):
            signals.append(f"website is only a social/free page ({site})")
        if rating is not None and rating < 4.0:
            signals.append(f"rating {rating} on Google")
        if reviews < 20:
            signals.append(f"only {reviews} Google reviews")
        need = min(100, 45 * (not site) + 30 * bool(site and "social" in " ".join(signals)) + 20 * (rating is not None and rating < 4)
                   + 15 * (reviews < 20) + 10 * (reviews < 5))
        out.append({"name": p.get("title"), "category": p.get("categoryName"), "website": site or None,
                    "phone": p.get("phone"), "address": p.get("address"), "city": p.get("city"), "rating": rating,
                    "reviews": reviews, "maps_url": p.get("url"), "signals": signals, "need_score": need,
                    "source": "maps", "query": p.get("searchString")})
    return sorted(out, key=lambda x: -x["need_score"])


PH_QUERY = """query($after: DateTime!, $first: Int!) { posts(order: NEWEST, postedAfter: $after, first: $first) { edges { node {
  name tagline description url website votesCount commentsCount createdAt topics(first: 3) { edges { node { name } } }
  makers { name username websiteUrl twitterUsername } } } } }"""


def producthunt(days=7, max_items=30, call=api_json):
    token = secret("PRODUCTHUNT_TOKEN")
    if not token:
        raise UserError("PRODUCTHUNT_TOKEN is not set — create a free developer token at producthunt.com/v2/oauth/applications")
    after = (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat()
    status, d = call("POST", PH_API, headers={"Authorization": f"Bearer {token}"}, timeout=40,
                     body={"query": PH_QUERY, "variables": {"after": after, "first": min(int(max_items), 50)}})
    if status >= 400 or (d or {}).get("errors"):
        raise ApiError(status, f"Product Hunt: {((d or {}).get('errors') or [{}])[0].get('message') or 'HTTP ' + str(status)}")
    out = []
    for e in (((d or {}).get("data") or {}).get("posts") or {}).get("edges") or []:
        n = e.get("node") or {}
        makers = [m for m in n.get("makers") or [] if m.get("name") and "[REDACTED]" not in str(m.get("name"))]
        topics = [t["node"]["name"] for t in (n.get("topics") or {}).get("edges") or [] if t.get("node")]
        signals = ["launched on Product Hunt in the last %d days" % days]
        if (n.get("votesCount") or 0) < 50:
            signals.append(f"only {n.get('votesCount') or 0} upvotes — launch needs marketing")
        out.append({"name": n.get("name"), "tagline": n.get("tagline"), "website": n.get("website"), "ph_url": n.get("url"),
                    "votes": n.get("votesCount"), "comments": n.get("commentsCount"), "launched": n.get("createdAt"),
                    "topics": topics, "makers": makers, "signals": signals, "source": "producthunt",
                    "need_score": 60 if (n.get("votesCount") or 0) < 50 else 40})
    return sorted(out, key=lambda x: -x["need_score"])


def add_companies(companies, source):
    """Put Maps / Product Hunt companies into the pipeline with their signals as a note."""
    import pipeline
    conn = pipeline.connect()
    added = []
    try:
        for c in companies:
            url = c.get("website")
            if url and re.search(r"(facebook|instagram|linktr\.ee|wa\.me)", url, re.I):
                url = None
            tag = c.get("query") or (c.get("topics") or [source])[0]
            r = pipeline.add(conn, url=url, name=c.get("name"), source=f"{source}:{tag}")
            slug = r["prospect"]["slug"]
            p = pipeline.get(conn, slug)
            with conn:
                link = c.get("maps_url") or c.get("ph_url")
                pipeline.event(conn, p["id"], "note", "Signals: " + "; ".join(c.get("signals") or []) +
                               (f" | phone {c['phone']}" if c.get("phone") else "") + (f" | {link}" if link else ""))
            if c.get("phone"):
                pipeline.add_contact(conn, slug, c.get("name") or slug, phone=c["phone"], role="business line")
            added.append({"prospect": slug, "created": r["created"]})
    finally:
        conn.close()
    return added


# ----------------------------------------------------------------------------------------------- all at once

def hunt(services, location=None, posted="week", max_posts=30, country="", call=api_json):
    """Every source you have keys for, best first. A failing source is reported, never fatal."""
    lib = query_library.build(services, location)
    max_runs = int(setting("APIFY_MAX_RUNS", "8"))
    have_apify = bool(secret("APIFY_TOKEN"))
    plan = [("hackernews", False, lambda: hackernews(lib["hackernews"][:6], 30, 30, True, call)),
            ("linkedin", True, lambda: linkedin(lib["linkedin"][:8], posted, max_posts, call)),
            ("reddit", have_apify, lambda: reddit(lib["reddit"][:12], max_posts, call)),
            ("google", True, lambda: google([q["query"] for q in lib["google_xray"] if q["platform"] != "signal"][:12],
                                            country, 1, call)),
            ("x", True, lambda: x_posts(lib["x"][:3], max_posts, call))]
    posts, errors, runs, ran = [], [], 0, []
    for name, uses_apify, fn in plan:
        if uses_apify and runs >= max_runs:
            errors.append(f"{name}: skipped (APIFY_MAX_RUNS={max_runs})")
            continue
        if name in ("linkedin", "x") and not have_apify:
            errors.append(f"{name}: skipped (needs APIFY_TOKEN)")
            continue
        try:
            got = fn()
            runs += uses_apify
            posts += got
            ran.append(f"{name}:{len(got)}")
        except (UserError, ApiError) as exc:
            errors.append(f"{name}: {exc}")
    return posts, errors, ran


# ----------------------------------------------------------------------------------------------- research

def research_queries(domain, name=None, city=None):
    n = f'"{name}"' if name else f'"{domain}"'
    loc = f" {city}" if city else ""
    return {
        "mentions": f'{n}{loc} -site:{domain}',
        "reviews": f'{n}{loc} reviews OR rating OR "google reviews"',
        "complaints": f'{n} (complaint OR "bad experience" OR "not working" OR scam)',
        "news": f'{n} (launch OR funding OR expands OR opens OR award OR partnership)',
        "linkedin": f'site:linkedin.com/company OR site:linkedin.com/in {n}',
        "founder": f'{n} (founder OR owner OR "managing director" OR CEO)',
        "social": f'(site:instagram.com OR site:facebook.com OR site:youtube.com) {n}',
        "directories": f'(site:justdial.com OR site:yelp.com OR site:clutch.co OR site:trustpilot.com OR site:indiamart.com) {n}',
        "hiring": f'{n} (hiring OR careers OR "job opening") (marketing OR developer OR designer OR SEO)',
        "ads": f'{n} ("sponsored" OR "facebook ads library" OR "google ads")',
        "competitors": f'{n} (alternatives OR competitors OR "vs")',
    }


def research(domain, name=None, city=None, out_dir=None, call=api_json):
    slug = domain_slug(domain)
    qs = research_queries(slug, name, city)
    rows = google(list(qs.values()), call=call)
    by_query = {v: k for k, v in qs.items()}
    sections = {k: [] for k in qs}
    for r in rows:
        k = by_query.get(r.get("query")) or "mentions"
        if len(sections[k]) < 8 and r["url"] not in [x["url"] for x in sections[k]]:
            sections[k].append({"url": r["url"], "title": r["title"], "snippet": r["text"]})
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

def finish(posts, errors, save=None, dedupe=True, ran=None):
    for p in posts:            # HN "SEEKING FREELANCER" posts are buyers by definition
        if p.get("intent_override") and "seeking freelancer" not in p["text"].lower()[:200]:
            p["text"] = "Seeking freelancer: " + p["text"]
    out = intent_scan.scan(posts, dedupe=dedupe)
    out["scanned"], out["errors"] = len(posts), errors
    out["by_source"] = {s: sum(1 for p in posts if p.get("source") == s) for s in sorted({str(p.get("source")) for p in posts})}
    out["kept_by_source"] = {s: sum(1 for c in out["candidates"] if c.get("source") == s) for s in out["by_source"]}
    out["with_contact_in_post"] = sum(1 for c in out["candidates"] if c.get("contact_in_post"))
    if ran is not None:
        out["sources_run"] = ran
    if save:
        Path(save).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        out["saved"] = save
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lead sources (LinkedIn, HN, Reddit, X, FB groups, Google, Maps, Product Hunt) and research.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(s, posted=True):
        s.add_argument("--services", default="web"); s.add_argument("--location", "--city", dest="location")
        s.add_argument("--max", type=int, default=30); s.add_argument("--save"); s.add_argument("--no-dedupe", action="store_true")
        if posted:
            s.add_argument("--posted", default="week", choices=POSTED)
    for name in ("linkedin", "google", "x"):
        s = sub.add_parser(name); common(s); s.add_argument("--query", action="append"); s.add_argument("--country", default="")
        s.add_argument("--pages", type=int, default=1)
    rd = sub.add_parser("reddit"); common(rd); rd.add_argument("--subreddit", action="append", help="r/name to search (repeatable)")
    rd.add_argument("--query", default=None)
    hn = sub.add_parser("hackernews"); common(hn, False); hn.add_argument("--query", action="append")
    hn.add_argument("--days", type=int, default=30); hn.add_argument("--no-thread", action="store_true")
    fb = sub.add_parser("facebook"); common(fb, False); fb.add_argument("--group-url", action="append", required=True)
    mp = sub.add_parser("maps"); common(mp, False); mp.add_argument("--search", action="append"); mp.add_argument("--add", action="store_true")
    ph = sub.add_parser("producthunt"); ph.add_argument("--days", type=int, default=7); ph.add_argument("--max", type=int, default=30)
    ph.add_argument("--add", action="store_true"); ph.add_argument("--save")
    h = sub.add_parser("hunt"); common(h); h.add_argument("--country", default="")
    ac = sub.add_parser("actor"); ac.add_argument("actor"); ac.add_argument("--input", required=True, help="JSON file")
    ac.add_argument("--max", type=int); ac.add_argument("--save"); ac.add_argument("--no-dedupe", action="store_true")
    ac.add_argument("--raw", action="store_true", help="return the items as-is instead of intent-scoring them")
    rs = sub.add_parser("research"); rs.add_argument("domain"); rs.add_argument("--name"); rs.add_argument("--city")
    rs.add_argument("--out-dir")
    qq = sub.add_parser("queries"); qq.add_argument("--services", default="web"); qq.add_argument("--location", "--city", dest="location")
    a = ap.parse_args(argv)
    try:
        svc = _services(getattr(a, "services", "web"))
        loc = getattr(a, "location", None)
        if a.cmd == "queries":
            out = {**query_library.build(svc, loc), "actors": {k: actor_for(k) for k in DEFAULT_ACTORS}}
        elif a.cmd == "linkedin":
            out = finish(linkedin(a.query or query_library.linkedin(svc, True, loc)[:8], a.posted, a.max), [], a.save, not a.no_dedupe)
        elif a.cmd == "google":
            qs = a.query or [q["query"] for q in query_library.google_xray(svc, loc) if q["platform"] != "signal"]
            out = finish(google(qs, a.country, a.pages), [], a.save, not a.no_dedupe)
        elif a.cmd == "x":
            out = finish(x_posts(a.query or query_library.x_search(svc, loc), a.max), [], a.save, not a.no_dedupe)
        elif a.cmd == "reddit":
            plan = ([{"subreddit": s.replace("r/", ""), "query": a.query or " OR ".join(query_library.TERMS[svc[0]][:3])}
                     for s in a.subreddit] if a.subreddit else query_library.reddit(svc))
            out = finish(reddit(plan, a.max), [], a.save, not a.no_dedupe)
        elif a.cmd == "hackernews":
            out = finish(hackernews(a.query or query_library.hackernews(svc), a.days, a.max, not a.no_thread), [], a.save,
                         not a.no_dedupe)
        elif a.cmd == "facebook":
            out = finish(facebook(a.group_url, a.max), [], a.save, not a.no_dedupe)
        elif a.cmd == "maps":
            searches = a.search or query_library.maps(svc, loc)[:6]
            if not a.search and not loc:
                raise UserError("give --location (e.g. 'Pune') or --search 'dentist in Pune'")
            companies = maps(searches, a.max)
            out = {"companies": companies, "count": len(companies), "with_need": sum(1 for c in companies if c["signals"])}
            if a.add:
                out["added"] = add_companies([c for c in companies if c["signals"]], "maps")
        elif a.cmd == "producthunt":
            companies = producthunt(a.days, a.max)
            out = {"companies": companies, "count": len(companies)}
            if a.add:
                out["added"] = add_companies(companies, "producthunt")
        elif a.cmd == "hunt":
            posts, errors, ran = hunt(svc, loc, a.posted, a.max, a.country)
            out = finish(posts, errors, a.save, not a.no_dedupe, ran)
            if not posts and errors:
                emit({"ok": False, "error": "every source failed", "data": out}, 4)
        elif a.cmd == "actor":
            items = run_actor(a.actor, json.loads(Path(a.input).read_text(encoding="utf-8")), a.max)
            out = {"items": items, "count": len(items)} if a.raw else finish(
                [normalize(i, "apify:" + a.actor) for i in items], [], a.save, not a.no_dedupe)
        else:
            out = research(a.domain, a.name, a.city, a.out_dir)
        if getattr(a, "save", None) and "companies" in out:
            Path(a.save).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        emit({"ok": True, "data": out})
    except (UserError, ApiError) as exc:
        emit({"ok": False, "error": str(exc)}, 2)


if __name__ == "__main__":
    main()

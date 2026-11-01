#!/usr/bin/env python3
"""
Buying-intent scanner: find public posts where someone ASKS for a service, and score them.

Two inputs:
  1. Bright Data SERP API (optional; BRIGHTDATA_API_KEY in env or <data home>/.env) runs Google
     "X-ray" queries such as site:linkedin.com/posts ("looking for" OR need) ("web developer" OR website)
     with a recency filter (tbs=qdr:w for 7 days, qdr:dN otherwise).
     Verified against docs.brightdata.com SERP API: POST https://api.brightdata.com/request,
     Authorization: Bearer <key>, body {zone, url, format: "raw", data_format: "parsed_light"}
     -> organic[] with link, title, description.
  2. Posts you paste or collect yourself: --file posts.jsonl / .txt (one post per line or JSON objects
     with url/text/author), or --text "...".

Free phrase scoring (English, Hindi, Hinglish): intent phrases + service phrases + question bonus
minus negatives (sellers, portfolios, "open to work", job ads, "we are hiring"). Posts that pass are
candidates for the agent to judge; the score is a filter, not a verdict.

Usage:
    python intent_scan.py --serp --queries default --lookback 7 [--max-calls 10] [--save hits.json]
    python intent_scan.py --serp --query 'site:reddit.com "looking for" "web developer"'
    python intent_scan.py --file posts.jsonl
    python intent_scan.py --text "Need a website for my bakery in Pune, koi developer batao?"
    python intent_scan.py --list-queries

Phrase-scoring approach adapted from yangyixxxx/lead-signal-listener (MIT); new phrase set.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sales_common import ApiError, api_json, data_home, emit, secret  # noqa: E402

INTENT = {
    "looking for": 12, "need a": 8, "need an": 8, "need someone": 12, "need help": 10, "in need of": 10,
    "any recommendations": 12, "can anyone recommend": 15, "recommend a": 10, "recommend an": 10,
    "recommendations for": 10, "suggest a": 8, "suggestions for": 8, "who can build": 12, "can someone build": 12,
    "hire a": 8, "want to hire": 12, "looking to hire": 10, "budget": 6, "quote": 5, "quotation": 6,
    "want a website": 14, "need a website": 15, "need an app": 15, "get a website": 10, "build my": 8,
    "redesign": 6, "revamp": 6, "help me with": 6, "anyone know a": 10, "dm me": 4,
    "seeking freelancer": 15, "looking for a freelancer": 15, "need a freelancer": 15, "hire a freelancer": 12,
    "[hiring]": 10, "seeking agency": 15, "agency recommendations": 15, "recommend an agency": 15,
    "recommend a good": 10, "request for proposal": 12, "rfp": 8, "get quotes": 10, "looking for quotes": 12,
    "who did your website": 12, "who built your website": 12, "who do you use for": 10, "anyone used": 6,
    "looking for help with": 10, "need someone to": 12, "willing to pay": 12, "paid gig": 10, "will pay": 8,
    "chahiye": 12, "banwana hai": 15, "banwani hai": 15, "banvana hai": 15, "banana hai": 8, "koi batao": 12,
    "koi bata": 10, "koi suggest": 12, "suggest karo": 12, "recommend karo": 12, "kisi ko jante": 10,
    "help chahiye": 12, "batao": 8, "bataiye": 8, "suggest kijiye": 10, "karwana hai": 12, "karwani hai": 12,
    "चाहिए": 12, "बनवाना है": 15, "बनवानी है": 15, "कोई बताओ": 12, "सुझाव": 8, "जरूरत": 10, "ज़रूरत": 10,
}
SERVICES = {
    "web": ["website", "web developer", "web development", "web design", "wordpress", "shopify", "landing page",
            "ecommerce site", "e-commerce website", "online store", "webflow", "wix", "वेबसाइट", "web dev"],
    "app": ["app developer", "mobile app", "android app", "ios app", "flutter", "react native", "app development",
            "build an app", "an app", "app for", "app banwana", "app banwani", "ऐप"],
    "seo": ["seo", "google ranking", "rank on google", "rank higher", "local seo", "google business profile", "gmb",
            "ai search", "search engine optimization"],
    "marketing": ["digital marketing", "social media manager", "social media marketing", "meta ads", "facebook ads",
                  "google ads", "ppc", "performance marketing", "instagram marketing", "lead generation", "marketing agency"],
    "design": ["logo", "branding", "ui/ux", "ux designer", "ui designer", "graphic designer", "figma", "brand identity"],
    "software": ["crm", "erp", "automation", "software developer", "saas", "integration", "chatbot", "ai agent"],
}
NEGATIVE = {
    "we are hiring": -30, "we're hiring": -30, "hiring for": -12, "job opening": -25, "job opportunity": -20,
    "full-time": -18, "full time": -15, "salary": -18, "ctc": -18, "apply now": -20, "send your resume": -25,
    "send your cv": -25, "years of experience": -15, "job description": -20, "internship": -20,
    "notice period": -20, "work from office": -15, "#hiring": -25,
    "open to work": -30, "#opentowork": -30, "looking for a job": -30, "looking for opportunities": -25,
    "looking for work": -25, "looking for new opportunities": -25, "available for freelance": -25,
    "available for projects": -20, "hire me": -25, "job chahiye": -30, "kaam chahiye": -25, "naukri": -25,
    "we offer": -18, "our services": -15, "we provide": -15, "we build": -15, "i build": -12, "we design": -12,
    "i am a web developer": -25, "i'm a web developer": -25, "i am a freelance": -25, "check out my": -15,
    "my portfolio": -18, "our portfolio": -15, "dm for": -12, "dm me for": -15, "starting at": -15,
    "starting from": -12, "% off": -18, "discount": -10, "limited offer": -20, "affordable website": -20,
    "hum banate hain": -25, "website banwaye": -20, "contact us today": -15, "book a free": -12,
    "giveaway": -30, "crypto": -20, "airdrop": -30, "[for hire]": -30, "seeking work": -30, "freelancer available": -25,
    "i can help you": -15, "we can help you": -15, "free audit": -10, "hire us": -25,
}
DEFAULT_QUERIES = [
    {"id": "li-web", "query": 'site:linkedin.com/posts ("looking for" OR "need" OR "recommend") ("web developer" OR website OR "app developer" OR "SEO agency")'},
    {"id": "li-marketing", "query": 'site:linkedin.com/posts ("looking for" OR "need") ("digital marketing agency" OR "marketing agency" OR "social media agency")'},
    {"id": "reddit-agency", "query": 'site:reddit.com ("looking for" OR recommend OR "need help") (agency OR developer) (website OR app OR SEO)'},
    {"id": "hinglish-web", "query": '"website banwana hai" OR "website banwani hai" OR "developer chahiye" OR "koi developer batao"'},
    {"id": "hinglish-seo", "query": '"seo karwana hai" OR "seo wala chahiye" OR "marketing agency chahiye"'},
]
MIN_SCORE = 20


def _hits(text, table):
    found, total = [], 0
    for phrase, w in table.items():
        if re.search(r"(?<![\w#])" + re.escape(phrase) + r"(?!\w)", text):
            found.append(phrase)
            total += w
    return found, total


def score_text(text, title=""):
    """Score 0-100 with the phrases that fired. keep=True means 'worth judging'."""
    t = f"{title} {text}".lower()
    intent_f, intent = _hits(t, INTENT)
    neg_f, neg = _hits(t, NEGATIVE)
    services = [s for s, words in SERVICES.items() if any(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", t) for w in words)]
    score = max(0, min(100, min(50, intent) + min(25, 12 * len(services)) + (6 if "?" in t else 0) + neg))
    keep = score >= MIN_SCORE and bool(services) and bool(intent_f)
    why = ("negative: " + ", ".join(neg_f[:3])) if neg_f and not keep else (
        "no service mentioned" if not services else "no asking phrase" if not intent_f else "low score" if not keep else "")
    return {"score": score, "keep": keep, "services": services, "intent_phrases": intent_f, "negative_phrases": neg_f,
            "reject_reason": why or None}


def platform_of(url):
    u = url or ""
    if re.search(r"news\.ycombinator\.com", u, re.I):
        return "hackernews"
    if re.search(r"producthunt\.com", u, re.I):
        return "producthunt"
    if re.search(r"indiehackers\.com", u, re.I):
        return "indiehackers"
    if re.search(r"(google\.[a-z.]+/maps|maps\.google|goo\.gl/maps)", u, re.I):
        return "maps"
    m = re.search(r"https?://(?:[\w-]+\.)*?(linkedin|reddit|facebook|twitter|x|quora|instagram|youtube|upwork|threads)\.(com|net)", u, re.I)
    return (m.group(1).lower().replace("twitter", "x")) if m else "web"


def google_url(query, lookback_days=7, gl=""):
    params = {"q": query, "tbs": "qdr:w" if lookback_days == 7 else f"qdr:d{max(1, int(lookback_days))}", "num": 10, "hl": "en"}
    if gl:
        params["gl"] = gl
    return "https://www.google.com/search?" + urlencode(params)


def serp(query, lookback=7, zone=None, gl="", call=api_json):
    key = secret("BRIGHTDATA_API_KEY")
    if not key:
        raise ApiError(0, "BRIGHTDATA_API_KEY is not set (env or ~/.ai-sales-team/.env)")
    body = {"zone": zone or secret("BRIGHTDATA_ZONE") or "serp_api1", "url": google_url(query, lookback, gl),
            "format": "raw", "data_format": "parsed_light"}
    status, data = call("POST", "https://api.brightdata.com/request", headers={"Authorization": f"Bearer {key}"}, body=body, timeout=60)
    if status >= 400:
        raise ApiError(status, f"Bright Data HTTP {status}: {str(data)[:200]}")
    if not isinstance(data, dict) or "organic" not in data:
        raise ApiError(status, "Bright Data response has no 'organic' field — is the zone a SERP API zone?")
    return [r for r in data["organic"] or [] if isinstance(r, dict) and r.get("link")]


def load_posts(path):
    p = Path(path)
    out = []
    for i, line in enumerate(p.read_text(encoding="utf-8-sig").splitlines()):
        line = line.strip()
        if not line:
            continue
        if line.startswith("{"):
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                o = {"text": line}
        else:
            o = {"text": line}
        o.setdefault("url", "")
        o.setdefault("id", o.get("url") or f"{p.name}:{i + 1}")
        out.append(o)
    return out


def contacts_in(text):
    """Emails, phones, WhatsApp numbers and websites written in the post itself."""
    import find_email
    f = find_email.from_text(text)
    return {k: f[k] for k in ("emails", "phones", "whatsapp", "websites") if f[k]}


def _seen_file():
    return data_home() / "intent_seen.json"


def scan(posts, dedupe=True):
    seen = set(json.loads(_seen_file().read_text(encoding="utf-8"))) if dedupe and _seen_file().exists() else set()
    kept, rejected, dup = [], [], 0
    for post in posts:
        key = hashlib.sha1((post.get("url") or post.get("text", "")).strip().lower().encode()).hexdigest()[:16]
        if dedupe and key in seen:
            dup += 1
            continue
        seen.add(key)
        s = score_text(post.get("text", ""), post.get("title", ""))
        item = {"url": post.get("url"), "platform": post.get("platform") or platform_of(post.get("url", "")),
                "author": post.get("author"), "title": post.get("title"), "text": post.get("text", "")[:1500],
                "query": post.get("query"), **s}
        for k in ("author_url", "author_headline", "posted", "source"):
            if post.get(k):
                item[k] = post[k]
        if s["keep"]:
            c = contacts_in(f"{post.get('title', '')} {post.get('text', '')}")
            if any(c.values()):
                item["contact_in_post"] = c         # email/phone already written in the post: no finder needed
        (kept if s["keep"] else rejected).append(item)
    if dedupe:
        _seen_file().write_text(json.dumps(sorted(seen)), encoding="utf-8")
    kept.sort(key=lambda x: -x["score"])
    return {"candidates": kept, "rejected": len(rejected), "rejected_examples": rejected[:5], "duplicates_skipped": dup,
            "next": "Judge each candidate with references/intent-rubric.md (sales-hunt skill); only real buyers go to the pipeline."}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Find and score buying-intent posts (EN/HI/Hinglish).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--serp", action="store_true", help="run Google X-ray queries through Bright Data")
    src.add_argument("--file", help="posts file (.jsonl with url/text/author, or one post per line)")
    src.add_argument("--text", help="score a single post")
    src.add_argument("--list-queries", action="store_true")
    ap.add_argument("--queries", default="default", help="'default' or a JSON file: [{id, query}]")
    ap.add_argument("--query", action="append", help="custom query (repeatable); overrides --queries")
    ap.add_argument("--lookback", type=int, default=7, help="days (default 7)")
    ap.add_argument("--max-calls", type=int, default=10, help="hard cap on paid SERP calls this run")
    ap.add_argument("--country", default="", help="Google gl= country code, e.g. in, us, uk")
    ap.add_argument("--no-dedupe", action="store_true", help="don't skip posts seen in earlier runs")
    ap.add_argument("--save", help="write the result JSON here too")
    a = ap.parse_args(argv)

    if a.list_queries:
        emit({"ok": True, "data": {"queries": DEFAULT_QUERIES}})
    if a.text:
        emit({"ok": True, "data": score_text(a.text)})
    errors = []
    if a.file:
        posts = load_posts(a.file)
    else:
        queries = [{"id": f"custom-{i + 1}", "query": q} for i, q in enumerate(a.query)] if a.query else (
            DEFAULT_QUERIES if a.queries == "default" else json.loads(Path(a.queries).read_text(encoding="utf-8")))
        posts = []
        for i, q in enumerate(queries):
            if i >= a.max_calls:
                errors.append(f"stopped after --max-calls {a.max_calls}")
                break
            try:
                for r in serp(q["query"], a.lookback, gl=a.country):
                    posts.append({"url": r["link"], "title": r.get("title", ""), "text": r.get("description", ""),
                                  "query": q.get("id")})
            except ApiError as exc:
                errors.append(f"{q.get('id')}: {exc}")
                if exc.status in (0, 401, 403):
                    break
    out = scan(posts, dedupe=not a.no_dedupe)
    out["scanned"] = len(posts)
    out["errors"] = errors
    if a.save:
        Path(a.save).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    emit({"ok": not (errors and not posts), "data": out}, 0 if posts or not errors else 4)


if __name__ == "__main__":
    main()

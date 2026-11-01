#!/usr/bin/env python3
"""
Query library: the searches that find buyers, per service and per platform. Better queries = better leads.

Principles (why these queries work):
  - Pair an ASKING phrase ("looking for", "recommend", "need", "chahiye") with a SERVICE phrase in quotes;
    either alone returns sellers and job ads.
  - Target the words buyers use, not the words agencies use ("need a new website", not "web solutions").
  - One platform per query, exclusions for sellers ("for hire", "open to work"), recency filters on.
  - LinkedIn post search (HarvestAPI): boolean AND / OR / NOT, "quoted phrases", parentheses,
    at most 5 operators and 500 characters per query — enforced by valid_linkedin().
  - Google X-ray: site: operator per platform, OR groups in parentheses, -"exclusions".
  - Add location only when the ICP is local (a city/country term roughly halves noise for local services).

Usage:
    python query_library.py [--services web,seo] [--city Pune] [--country India] [--platform linkedin]
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sales_common import emit  # noqa: E402

SERVICES = ["web", "app", "seo", "marketing", "design", "software", "ecommerce", "video"]

# Service phrases buyers actually write (first ones are the strongest).
TERMS = {
    "web": ['"web developer"', '"website developer"', '"web designer"', '"website designer"', '"wordpress developer"', '"webflow developer"'],
    "app": ['"app developer"', '"mobile app developer"', '"flutter developer"', '"react native developer"', '"iOS developer"'],
    "seo": ['"SEO agency"', '"SEO expert"', '"SEO consultant"', '"local SEO"', '"SEO freelancer"'],
    "marketing": ['"marketing agency"', '"digital marketing agency"', '"social media manager"', '"performance marketer"', '"Meta ads"', '"Google Ads expert"'],
    "design": ['"logo designer"', '"branding agency"', '"UI UX designer"', '"brand designer"', '"graphic designer"'],
    "software": ['"software agency"', '"CRM consultant"', '"automation expert"', '"AI developer"', '"chatbot developer"', '"MVP developer"'],
    "ecommerce": ['"Shopify developer"', '"Shopify expert"', '"WooCommerce developer"', '"ecommerce website"', '"Amazon seller account"'],
    "video": ['"video editor"', '"video production"', '"explainer video"', '"YouTube editor"', '"reels editor"'],
}
# What a buyer says about the outcome (catches people who never name the role).
NEEDS = {
    "web": ['"need a website"', '"need a new website"', '"website redesign"', '"build my website"', '"website for my business"'],
    "app": ['"need an app"', '"build an app"', '"app for my business"', '"MVP built"'],
    "seo": ['"rank on Google"', '"help with SEO"', '"not showing on Google"', '"Google ranking"', '"more organic traffic"'],
    "marketing": ['"run ads"', '"grow our Instagram"', '"more leads"', '"handle our social media"', '"marketing help"'],
    "design": ['"need a logo"', '"rebrand"', '"new branding"', '"redesign our app"'],
    "software": ['"automate"', '"need a CRM"', '"custom software"', '"build a dashboard"', '"AI agent"'],
    "ecommerce": ['"Shopify store"', '"online store"', '"start selling online"', '"ecommerce site"'],
    "video": ['"edit my videos"', '"need a video"', '"product video"', '"YouTube channel"'],
}
HINGLISH = {
    "web": ['"website banwana hai"', '"website banwani hai"', '"website chahiye"', '"developer chahiye"', '"koi developer batao"'],
    "app": ['"app banwana hai"', '"app developer chahiye"', '"app banwani hai"'],
    "seo": ['"seo karwana hai"', '"seo wala chahiye"', '"google pe rank"'],
    "marketing": ['"marketing agency chahiye"', '"ads chalwane hai"', '"social media handle karne"'],
    "design": ['"logo banwana hai"', '"designer chahiye"'],
    "software": ['"software banwana hai"', '"automation karwana hai"'],
    "ecommerce": ['"online store banwana hai"', '"shopify store chahiye"'],
    "video": ['"video editor chahiye"', '"reels edit"'],
}
ASK = ['"looking for"', '"recommend"', '"need"', '"suggestions"', '"anyone know"']
SELLER_EXCLUDE = ['-"for hire"', '-"open to work"', '-"we offer"', '-"our services"', '-"I am a"']

# Communities where buyers post. (subreddit, search query) — flair:Hiring is the buyer flair on r/forhire.
REDDIT = {
    "_all": [("forhire", 'flair:Hiring'), ("hiring", ""), ("smallbusiness", '"looking for"'), ("Entrepreneur", '"recommend"'),
             ("startups", '"looking for"'), ("indianstartups", '"looking for"'), ("SaaS", '"looking for"'), ("india", '"looking for"')],
    "web": [("web_design", '"looking for" OR "need a website"'), ("wordpress", '"looking for" developer'), ("smallbusiness", "website")],
    "app": [("appdev", '"looking for"'), ("startups", '"app developer"')],
    "seo": [("SEO", '"looking for" OR "recommend"'), ("smallbusiness", "SEO"), ("localseo", '"looking for"')],
    "marketing": [("marketing", '"looking for" agency'), ("PPC", '"looking for"'), ("socialmedia", '"looking for"')],
    "design": [("logodesign", '"looking for"'), ("design_critiques", "hire")],
    "software": [("nocode", '"looking for"'), ("automation", '"looking for"'), ("CRM", '"recommend"')],
    "ecommerce": [("shopify", '"looking for" OR "recommend"'), ("ecommerce", '"looking for"'), ("FulfillmentByAmazon", "hire")],
    "video": [("VideoEditing", '"looking for"'), ("NewTubers", "editor")],
}
HN = {
    "_all": ['"looking for a freelancer"', '"recommend an agency"', '"looking for a contractor"', '"need a developer"'],
    "web": ['"looking for a web developer"', '"need a website"'],
    "app": ['"looking for an app developer"', '"mobile developer" contract'],
    "seo": ['"SEO agency" recommend', '"SEO consultant"'],
    "marketing": ['"marketing agency" recommend', '"growth marketer" contract'],
    "design": ['"looking for a designer"', '"design agency" recommend'],
    "software": ['"development agency" recommend', '"fractional CTO"', '"build an MVP"'],
    "ecommerce": ['"Shopify developer"', '"Shopify agency"'],
    "video": ['"video editor" contract'],
}
# Local businesses that buy websites / SEO / marketing (Google Maps searches).
MAPS = {
    "web": ["dentist", "dental clinic", "physiotherapy clinic", "restaurant", "cafe", "bakery", "salon", "gym",
            "interior designer", "real estate agent", "chartered accountant", "coaching institute", "boutique", "hotel"],
    "seo": ["dentist", "dermatologist", "lawyer", "real estate agent", "plumber", "packers and movers", "car service center",
            "IVF clinic", "eye hospital", "wedding photographer"],
    "marketing": ["restaurant", "cafe", "salon", "gym", "clothing store", "furniture store", "jewellery shop", "spa"],
    "design": ["boutique", "cafe", "bakery", "startup", "interior designer"],
    "ecommerce": ["clothing store", "jewellery shop", "handicrafts", "organic store", "furniture store"],
    "app": ["clinic", "gym", "restaurant", "school"],
    "software": ["manufacturer", "logistics company", "distributor", "school", "hospital"],
    "video": ["real estate developer", "restaurant", "gym", "wedding planner"],
}


def op_count(q):
    return len(re.findall(r"\b(AND|OR|NOT)\b", re.sub(r'"[^"]*"', "", q)))


def valid_linkedin(q):
    return op_count(q) <= 5 and len(q) <= 500 and q.count("(") == q.count(")") and q.count('"') % 2 == 0


def _group(terms, n=3):
    t = terms[:n]
    return t[0] if len(t) == 1 else "(" + " OR ".join(t) + ")"


def linkedin(services, hinglish=True, location=None):
    """Boolean queries for LinkedIn post search (≤ 5 operators each)."""
    out = []
    for s in services:
        out += [
            f'"looking for" AND {_group(TERMS[s], 3)}',                       # 3 ops
            f'("can anyone recommend" OR "recommendations for") AND {_group(TERMS[s], 2)}',   # 3 ops
            f'{_group(NEEDS[s], 3)} AND ("looking for" OR help)',             # 4 ops
            f'"need" AND {_group(TERMS[s][2:], 3)} NOT "open to work"',      # ≤4 ops
        ]
        if hinglish:
            out.append(_group(HINGLISH[s], 3))
    out.append('("looking for" OR "recommend") AND (agency OR freelancer) AND "small business"')  # 4 ops
    if location:
        def with_loc(q):
            if op_count(q) > 4:
                return q
            head, sep, tail = q.partition(" NOT ")
            return f'{head} AND "{location}"' + (sep + tail if sep else "")
        out = [with_loc(q) for q in out]
    seen, final = set(), []
    for q in out:
        if q not in seen and valid_linkedin(q):
            seen.add(q)
            final.append(q)
    return final


def google_xray(services, location=None, signals=True):
    """Google X-ray queries: one platform each, asking + service, sellers excluded."""
    loc = f' "{location}"' if location else ""
    ex = " " + " ".join(SELLER_EXCLUDE[:3])
    terms = lambda s, n=3: "(" + " OR ".join(TERMS[s][:n] + NEEDS[s][:1]) + ")"  # noqa: E731
    ask = '("looking for" OR "recommend" OR "need" OR "anyone know")'
    out = []
    for s in services:
        out += [
            {"id": f"li-posts-{s}", "platform": "linkedin", "query": f"site:linkedin.com/posts {ask} {terms(s)}{loc}{ex}"},
            {"id": f"reddit-{s}", "platform": "reddit", "query": f"site:reddit.com {ask} {terms(s)}{loc}{ex}"},
            {"id": f"x-{s}", "platform": "x", "query": f"(site:x.com OR site:twitter.com) {ask} {terms(s, 2)}{loc}{ex}"},
            {"id": f"fb-groups-{s}", "platform": "facebook", "query": f"site:facebook.com/groups {ask} {terms(s, 2)}{loc}"},
            {"id": f"quora-{s}", "platform": "quora", "query": f'site:quora.com ("recommend" OR "best" OR "looking for") {terms(s, 2)}{loc}'},
            {"id": f"indiehackers-{s}", "platform": "indiehackers", "query": f"site:indiehackers.com {ask} {terms(s, 2)}"},
            {"id": f"upwork-jobs-{s}", "platform": "upwork", "query": f"site:upwork.com/freelance-jobs/apply {terms(s, 2)}"},
            {"id": f"hinglish-{s}", "platform": "web", "query": "(" + " OR ".join(HINGLISH[s][:4]) + ")"},
        ]
        if signals:   # companies showing a need without asking: hiring for the role you replace, launches
            out += [
                {"id": f"hiring-signal-{s}", "platform": "signal",
                 "query": f'(site:linkedin.com/jobs OR site:naukri.com OR site:indeed.com) {terms(s, 2)}{loc}'},
            ]
    out.append({"id": "ph-discussions", "platform": "producthunt",
                "query": 'site:producthunt.com/discussions ("looking for" OR "recommend") (agency OR developer OR designer OR SEO)'})
    return out


def x_search(services, location=None):
    """X/Twitter advanced search (for tweet-scraper actors)."""
    loc = f' "{location}"' if location else ""
    return [f'("looking for" OR "need" OR "recommend") ({" OR ".join(TERMS[s][:3])}){loc} -filter:retweets -"for hire" -"DM me"'
            for s in services]


def reddit(services):
    plan = list(REDDIT["_all"])
    for s in services:
        plan += REDDIT.get(s, [])
    terms = " OR ".join(t for s in services for t in TERMS[s][:2])
    out, seen = [], set()
    for sub, q in plan:
        query = q if q else terms
        if q in ('"looking for"', '"recommend"') or q.startswith("flair:"):
            query = f"{q} ({terms})"
        if (sub, query) not in seen:
            seen.add((sub, query))
            out.append({"subreddit": sub, "query": query})
    return out


def hackernews(services):
    out = list(HN["_all"])
    for s in services:
        out += HN.get(s, [])
    return list(dict.fromkeys(out))


def maps(services, location):
    cats = []
    for s in services:
        cats += MAPS.get(s, [])
    return [f"{c} in {location}" if location else c for c in dict.fromkeys(cats)]


def build(services=None, location=None, hinglish=True):
    services = [s for s in (services or ["web"]) if s in SERVICES] or ["web"]
    return {"services": services, "location": location,
            "linkedin": linkedin(services, hinglish, location), "google_xray": google_xray(services, location),
            "x": x_search(services, location), "reddit": reddit(services), "hackernews": hackernews(services),
            "maps": maps(services, location),
            "tips": ["Run linkedin + reddit + hackernews first (people asking), then maps/producthunt (companies with a need).",
                     "Keep the queries that produce meetings (pipeline.py report → by_source); drop the rest.",
                     "Add your niche words (e.g. 'clinic', 'D2C', 'SaaS') to a query when the ICP is narrow."]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Show the lead-finding queries for your services.")
    ap.add_argument("--services", default="web")
    ap.add_argument("--location", "--city", dest="location")
    ap.add_argument("--platform", choices=["linkedin", "google_xray", "x", "reddit", "hackernews", "maps"])
    ap.add_argument("--no-hinglish", action="store_true")
    a = ap.parse_args(argv)
    out = build([s.strip() for s in a.services.split(",")], a.location, not a.no_hinglish)
    emit({"ok": True, "data": out[a.platform] if a.platform else out})


if __name__ == "__main__":
    main()

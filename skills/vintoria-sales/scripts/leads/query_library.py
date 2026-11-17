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

  - With a seller profile (SELLER-PROFILE.json, see seller_profile.py) the queries are built from YOUR niches,
    platforms, buyer pains, buying triggers, tools clients leave, buyer titles and target countries — that is
    what makes them sharp. Without one, generic service queries are used.
  - English only by default (international clients); Hinglish only if the profile's languages include it.

Usage:
    python query_library.py                       # from SELLER-PROFILE.json if present
    python query_library.py --services web,seo [--location "Austin"] [--platform linkedin] [--no-profile]
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import emit  # noqa: E402

SERVICES = ["web", "app", "seo", "marketing", "design", "software", "ecommerce", "video", "ai", "automation"]

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
    "ai": ['"AI developer"', '"AI agency"', '"chatbot developer"', '"LLM developer"', '"AI consultant"', '"RAG developer"'],
    "automation": ['"automation expert"', '"Zapier expert"', '"Make.com expert"', '"n8n developer"', '"CRM consultant"', '"HubSpot consultant"'],
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
    "ai": ['"AI chatbot"', '"AI agent"', '"add AI to"', '"chatbot for my website"', '"automate with AI"', '"custom GPT"'],
    "automation": ['"automate"', '"need a CRM"', '"connect our tools"', '"manual data entry"', '"workflow automation"'],
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
    "ai": ['"AI chatbot chahiye"', '"chatbot banwana hai"'],
    "automation": ['"automation karwana hai"', '"CRM chahiye"'],
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
    "ai": [("ChatGPT", '"looking for" developer'), ("LocalLLaMA", "hire"), ("smallbusiness", "chatbot")],
    "automation": [("automation", '"looking for"'), ("zapier", '"looking for"'), ("n8n", "hire"), ("CRM", '"recommend"')],
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
    "ai": ['"AI engineer" contract', '"LLM" consultant', '"build an AI agent"'],
    "automation": ['"automation" contractor', '"Zapier" consultant'],
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
    "ai": ["clinic", "real estate agent", "coaching institute", "law firm", "travel agency"],
    "automation": ["manufacturer", "distributor", "logistics company", "accounting firm", "real estate agent"],
}


def op_count(q):
    return len(re.findall(r"\b(AND|OR|NOT)\b", re.sub(r'"[^"]*"', "", q)))


def valid_linkedin(q):
    return op_count(q) <= 5 and len(q) <= 500 and q.count("(") == q.count(")") and q.count('"') % 2 == 0


def _group(terms, n=3):
    t = terms[:n]
    return t[0] if len(t) == 1 else "(" + " OR ".join(t) + ")"


def linkedin(services, hinglish=False, location=None):
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


def google_xray(services, location=None, signals=True, hinglish=False):
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
        ]
        if hinglish:
            out.append({"id": f"hinglish-{s}", "platform": "web", "query": "(" + " OR ".join(HINGLISH[s][:4]) + ")"})
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


def build(services=None, location=None, hinglish=False):
    services = [s for s in (services or ["web"]) if s in SERVICES] or ["web"]
    return {"services": services, "location": location, "profile_used": False,
            "linkedin": linkedin(services, hinglish, location), "google_xray": google_xray(services, location, hinglish=hinglish),
            "x": x_search(services, location), "reddit": reddit(services), "hackernews": hackernews(services),
            "maps": maps(services, location),
            "tips": ["Run linkedin + reddit + hackernews first (people asking), then maps/producthunt (companies with a need).",
                     "Keep the queries that produce meetings (pipeline.py report → by_source); drop the rest.",
                     "Add your niche words (e.g. 'clinic', 'D2C', 'SaaS') to a query when the ICP is narrow."]}


# ------------------------------------------------------------------------------- profile-driven (the sharp ones)

COUNTRIES = {
    "US": {"name": "United States", "gl": "us", "tz": "America/New_York",
           "cities": ["New York", "Los Angeles", "Chicago", "Houston", "Austin", "Miami", "Dallas", "San Diego"]},
    "UK": {"name": "United Kingdom", "gl": "gb", "tz": "Europe/London",
           "cities": ["London", "Manchester", "Birmingham", "Leeds", "Bristol", "Edinburgh"]},
    "CA": {"name": "Canada", "gl": "ca", "tz": "America/Toronto", "cities": ["Toronto", "Vancouver", "Calgary", "Montreal", "Ottawa"]},
    "AU": {"name": "Australia", "gl": "au", "tz": "Australia/Sydney", "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"]},
    "NZ": {"name": "New Zealand", "gl": "nz", "tz": "Pacific/Auckland", "cities": ["Auckland", "Wellington", "Christchurch"]},
    "IE": {"name": "Ireland", "gl": "ie", "tz": "Europe/Dublin", "cities": ["Dublin", "Cork", "Galway"]},
    "AE": {"name": "United Arab Emirates", "gl": "ae", "tz": "Asia/Dubai", "cities": ["Dubai", "Abu Dhabi"]},
    "SG": {"name": "Singapore", "gl": "sg", "tz": "Asia/Singapore", "cities": ["Singapore"]},
    "DE": {"name": "Germany", "gl": "de", "tz": "Europe/Berlin", "cities": ["Berlin", "Munich", "Hamburg"]},
    "NL": {"name": "Netherlands", "gl": "nl", "tz": "Europe/Amsterdam", "cities": ["Amsterdam", "Rotterdam"]},
    "IN": {"name": "India", "gl": "in", "tz": "Asia/Kolkata",
           "cities": ["Mumbai", "Delhi", "Bengaluru", "Pune", "Hyderabad", "Chennai", "Ahmedabad", "Kolkata", "Jaipur", "Noida"]},
}
ALIASES = {"USA": "US", "UNITED STATES": "US", "AMERICA": "US", "GB": "UK", "UNITED KINGDOM": "UK", "ENGLAND": "UK",
           "BRITAIN": "UK", "CANADA": "CA", "AUSTRALIA": "AU", "NEW ZEALAND": "NZ", "IRELAND": "IE", "UAE": "AE",
           "DUBAI": "AE", "SINGAPORE": "SG", "GERMANY": "DE", "NETHERLANDS": "NL", "INDIA": "IN", "BHARAT": "IN"}
# Words that betray a market you excluded (used to drop leads, e.g. Indian posts when you target the US/UK).
MARKET_MARKERS = {
    "India": ["india", "indian", "mumbai", "delhi", "new delhi", "bangalore", "bengaluru", "pune", "hyderabad", "chennai",
              "kolkata", "ahmedabad", "noida", "gurgaon", "gurugram", "jaipur", "lucknow", "chandigarh", "indore", "kochi",
              "₹", "inr", "lakh", "lakhs", "crore", "rupees", "rs."],
    "Pakistan": ["pakistan", "karachi", "lahore", "islamabad", "pkr"],
    "Bangladesh": ["bangladesh", "dhaka", "bdt", "taka"],
}
# niche word → communities where those business owners talk
NICHE_SUBS = {
    "dent": ["Dentistry"], "real estate": ["realtors", "RealEstate"], "realtor": ["realtors"], "law": ["LawFirm", "Lawyertalk"],
    "attorney": ["LawFirm"], "restaurant": ["restaurateur", "restaurantowners"], "cafe": ["restaurateur", "cafe"],
    "coffee": ["roasters", "smallbusiness"], "salon": ["salons", "Hair"], "spa": ["Esthetics", "MassageTherapists"],
    "med spa": ["MedSpa"], "gym": ["gymowner", "personaltraining"], "fitness": ["personaltraining", "gymowner"],
    "coach": ["lifecoaching", "coaching"], "consult": ["consulting"], "saas": ["SaaS", "microsaas", "startups"],
    "startup": ["startups", "Entrepreneur", "indiehackers"], "ecommerce": ["ecommerce", "shopify", "FulfillmentByAmazon"],
    "shopify": ["shopify", "ecommerce"], "dtc": ["DTC", "ecommerce", "shopify"], "skincare": ["SkincareAddiction", "ecommerce"],
    "beauty": ["ecommerce", "shopify"], "supplement": ["ecommerce", "supplements"], "fashion": ["ecommerce", "shopify"],
    "contractor": ["Contractor", "Construction"], "construction": ["Construction", "Contractor"], "roof": ["Roofing"],
    "hvac": ["HVAC"], "plumb": ["Plumbing"], "landscap": ["landscaping"], "clean": ["CleaningTips", "smallbusiness"],
    "therap": ["therapists", "privatepractice"], "chiro": ["Chiropractic"], "vet": ["Veterinary"], "account": ["Accounting", "taxpros"],
    "cpa": ["taxpros", "Accounting"], "insurance": ["InsuranceAgent", "Insurance"], "nonprofit": ["nonprofit"],
    "photograph": ["WeddingPhotography", "photography"], "wedding": ["weddingplanning", "WeddingPhotography"],
    "hotel": ["hotels", "hospitality"], "travel": ["travel", "TravelAgents"], "school": ["Teachers", "edtech"],
    "edtech": ["edtech"], "course": ["onlinecourses", "Entrepreneur"], "podcast": ["podcasting"], "youtube": ["NewTubers"],
    "agency": ["agency", "marketing"], "b2b": ["b2bmarketing", "sales"],
}
LOCAL_WORDS = ["dent", "clinic", "restaurant", "cafe", "salon", "spa", "gym", "law", "attorney", "realtor", "real estate",
               "plumb", "hvac", "roof", "contractor", "chiro", "vet", "hotel", "school", "account", "cpa", "therap",
               "landscap", "clean", "bakery", "florist", "auto", "garage", "physio", "optomet", "pharmacy"]
SIZE_RANGES = {"1-10": ["1,10"], "1-50": ["1,10", "11,20", "21,50"], "11-50": ["11,20", "21,50"], "1-200": ["1,10", "11,20", "21,50", "51,100", "101,200"],
               "51-200": ["51,100", "101,200"], "201-1000": ["201,500", "501,1000"]}


def _q(t):
    t = str(t).strip().strip('"')
    return f'"{t}"' if " " in t or "-" in t else t


def _or(items, n=3):
    items = [_q(x) for x in items if str(x).strip()][:n]
    if not items:
        return ""
    return items[0] if len(items) == 1 else "(" + " OR ".join(items) + ")"


def country_codes(profile):
    out = []
    for c in (profile.get("targets") or {}).get("countries") or ["US"]:
        k = ALIASES.get(str(c).strip().upper(), str(c).strip().upper())
        if k in COUNTRIES and k not in out:
            out.append(k)
    return out or ["US"]


def excluded_markers(profile):
    out = []
    for c in (profile.get("targets") or {}).get("exclude_countries") or []:
        name = str(c).strip().title()
        out += MARKET_MARKERS.get(name, [name.lower()])
    return out


def _with_not(q, words):
    """Append NOT <word> while the query stays within LinkedIn's 5 operators."""
    for w in words:
        cand = f"{q} NOT {_q(w)}"
        if not valid_linkedin(cand):
            break
        q = cand
    return q


def linkedin_from_profile(profile):
    o, sig, tg = profile.get("offer") or {}, profile.get("signals") or {}, profile.get("targets") or {}
    services = [s for s in o.get("services") or [] if s in SERVICES] or ["web"]
    niches = [n for n in o.get("niches") or [] if n][:6]
    platforms = o.get("platforms") or []
    terms = []
    for s in services:
        terms += TERMS[s]
    terms = list(dict.fromkeys([f'"{p} developer"' for p in platforms[:2]] + [f'"{p} expert"' for p in platforms[:1]] + terms))
    excl = ["India"] if any(str(c).lower() == "india" for c in tg.get("exclude_countries") or []) else []
    out = []
    for n in niches:                                   # niche × service: the sharpest queries
        out.append(f'"looking for" AND {_or(terms, 2)} AND {_or([n], 1)}')
        out.append(f'("recommend" OR "recommendations") AND {_or(terms, 2)} AND {_or([n], 1)}')
    out.append(f'"looking for" AND {_or(terms, 3)}')
    out.append(f'("can anyone recommend" OR "recommendations for") AND {_or(terms, 2)}')
    for s in services:
        out.append(f'{_or(NEEDS[s], 3)} AND ("looking for" OR help)')
    if sig.get("pains"):
        out.append(f'{_or(sig["pains"], 3)} AND ("our website" OR "our store" OR help)')
    if sig.get("triggers"):
        out.append(f'{_or(sig["triggers"], 3)} AND ("looking for" OR need)')
    if sig.get("tools_they_leave"):
        tools = sig["tools_they_leave"][:2]
        out.append("(" + " OR ".join(f'"moving from {t}" OR "migrate from {t}"' for t in tools[:1]) +
                   (f' OR "switching from {tools[1]}"' if len(tools) > 1 else "") + ") AND (help OR developer)")
    if o.get("outcomes"):
        out.append(f'"need help" AND {_or(o["outcomes"], 3)}')
    final, seen = [], set()
    for q in out:
        q = _with_not(q, excl)
        if q not in seen and valid_linkedin(q):
            seen.add(q)
            final.append(q)
    return final


def xray_from_profile(profile):
    o, sig = profile.get("offer") or {}, profile.get("signals") or {}
    services = [s for s in o.get("services") or [] if s in SERVICES] or ["web"]
    base = google_xray(services, None, signals=True)
    niches = o.get("niches") or []
    excl = " ".join(f"-{_q(w)}" for w in ["India", "Indian"] if any(
        str(c).lower() == "india" for c in (profile.get("targets") or {}).get("exclude_countries") or []))
    ask = '("looking for" OR "recommend" OR "need" OR "anyone know")'
    extra = []
    for n in niches[:4]:
        svc = " OR ".join(TERMS[services[0]][:2] + NEEDS[services[0]][:1])
        extra += [{"id": f"li-niche-{n}", "platform": "linkedin", "query": f"site:linkedin.com/posts {ask} ({svc}) {_q(n)}"},
                  {"id": f"reddit-niche-{n}", "platform": "reddit", "query": f"site:reddit.com {ask} ({svc}) {_q(n)}"}]
    if sig.get("pains"):
        extra.append({"id": "pain-posts", "platform": "web", "query": f"(site:reddit.com OR site:linkedin.com/posts) {_or(sig['pains'], 4)}"})
    if sig.get("tools_they_leave"):
        t = sig["tools_they_leave"][0]
        extra.append({"id": f"switch-{t}", "platform": "web",
                      "query": f'(site:reddit.com OR site:linkedin.com/posts) ("moving from {t}" OR "migrate from {t}" OR "leaving {t}" OR "outgrown {t}")'})
    out = extra + base
    for q in out:
        if excl and q["platform"] != "signal":
            q["query"] = f"{q['query']} {excl}"
    return out


def apollo_urls(profile, max_urls=4):
    """Apollo people-search URLs for the Apify Apollo actor. Open one in Apollo once to check the filters."""
    tg, o = profile.get("targets") or {}, profile.get("offer") or {}
    titles = tg.get("buyer_titles") or ["Founder", "Owner", "CEO"]
    locs = [COUNTRIES[c]["name"] for c in country_codes(profile)]
    sizes = SIZE_RANGES.get(str(tg.get("company_size") or "").replace(" ", "").replace("employees", ""), [])
    niches = o.get("niches") or [""]
    urls = []
    for n in niches[:max_urls]:
        parts = ["page=1"] + [f"personTitles[]={quote(t)}" for t in titles[:6]] + [f"personLocations[]={quote(l)}" for l in locs]
        parts += [f"organizationNumEmployeesRanges[]={quote(r)}" for r in sizes]
        if n:
            parts += [f"qOrganizationKeywordTags[]={quote(n)}", "includedOrganizationKeywordFields[]=tags",
                      "includedOrganizationKeywordFields[]=name"]
        parts.append("contactEmailStatusV2[]=verified")
        urls.append({"niche": n or None, "url": "https://app.apollo.io/#/people?" + "&".join(parts)})
    return urls


def people_search(profile):
    """Filters for people databases (LinkedIn profile search, Leads Finder)."""
    tg, o = profile.get("targets") or {}, profile.get("offer") or {}
    titles = tg.get("buyer_titles") or ["Founder", "Owner", "CEO"]
    locs = [COUNTRIES[c]["name"] for c in country_codes(profile)]
    niches = o.get("niches") or []
    return {"linkedin_people": [{"searchQuery": n[:300], "locations": locs, "currentJobTitles": titles[:6]} for n in niches[:4]]
            or [{"searchQuery": " ".join(titles[:2]), "locations": locs, "currentJobTitles": titles[:6]}],
            "apollo_api": {"person_titles": titles[:8], "person_locations": locs,
                           "organization_num_employees_ranges": SIZE_RANGES.get(
                               str(tg.get("company_size") or "").replace(" ", "").replace("employees", ""), []),
                           "q_organization_keyword_tags": niches[:8]},
            "leads_finder": {"contact_job_title": titles[:8], "contact_location": [l.lower() for l in locs],
                             "company_keywords": niches[:8], "email_status": ["validated"]}}


def reddit_from_profile(profile):
    o = profile.get("offer") or {}
    services = [s for s in o.get("services") or [] if s in SERVICES] or ["web"]
    plan = reddit(services)
    terms = " OR ".join(t for s in services for t in TERMS[s][:2])
    seen = {(p["subreddit"], p["query"]) for p in plan}
    for n in o.get("niches") or []:
        for key, subs in NICHE_SUBS.items():
            if key in str(n).lower():
                for sub in subs:
                    q = f'("looking for" OR "recommend" OR need) ({terms})'
                    if (sub, q) not in seen:
                        seen.add((sub, q))
                        plan.insert(0, {"subreddit": sub, "query": q})
    return plan


def maps_from_profile(profile):
    o, tg = profile.get("offer") or {}, profile.get("targets") or {}
    local = [n for n in o.get("niches") or [] if any(w in str(n).lower() for w in LOCAL_WORDS)]
    if not local:
        return []
    cities = tg.get("cities") or [city for c in country_codes(profile) for city in COUNTRIES[c]["cities"][:2]]
    return [f"{n} in {c}" for n in local[:4] for c in cities[:6]]


def from_profile(profile):
    o, tg = profile.get("offer") or {}, profile.get("targets") or {}
    services = [s for s in o.get("services") or [] if s in SERVICES] or ["web"]
    langs = [str(x).lower() for x in tg.get("languages") or ["en"]]
    codes = country_codes(profile)
    li = linkedin_from_profile(profile)
    if "hinglish" in langs:
        li += [_or(HINGLISH[s], 3) for s in services]
    return {"services": services, "profile_used": True, "countries": codes,
            "google_countries": [COUNTRIES[c]["gl"] for c in codes], "timezones": {c: COUNTRIES[c]["tz"] for c in codes},
            "exclude_markers": excluded_markers(profile), "languages": langs,
            "linkedin": li, "google_xray": xray_from_profile(profile), "x": x_search(services) + [
                f'("looking for" OR "recommend") ({" OR ".join(TERMS[services[0]][:2])}) {_q(n)} -filter:retweets -"for hire"'
                for n in (o.get("niches") or [])[:3]],
            "reddit": reddit_from_profile(profile), "hackernews": hackernews(services), "maps": maps_from_profile(profile),
            "apollo_urls": apollo_urls(profile), **people_search(profile),
            "tips": ["Niche × service queries come first — they convert best. Check by_source after a week.",
                     "Apollo / LinkedIn people searches give lists (no intent): pair them with a dossier and a strong first line.",
                     "Edit SELLER-PROFILE.json (niches, pains, triggers, tools_they_leave) to change every query at once."]}


def auto(services=None, location=None, use_profile=True):
    """Profile-driven queries if a seller profile exists (and no explicit --services), else generic ones."""
    if use_profile and not services:
        import seller_profile
        prof = seller_profile.load()
        if prof and (prof.get("offer") or {}).get("services"):
            return from_profile(prof)
    return build(services, location)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Show the lead-finding queries for your services.")
    ap.add_argument("--services")
    ap.add_argument("--location", "--city", dest="location")
    ap.add_argument("--platform", choices=["linkedin", "google_xray", "x", "reddit", "hackernews", "maps", "apollo_urls",
                                           "linkedin_people", "leads_finder"])
    ap.add_argument("--no-profile", action="store_true")
    a = ap.parse_args(argv)
    out = auto([s.strip() for s in a.services.split(",")] if a.services else None, a.location, not a.no_profile)
    emit({"ok": True, "data": out[a.platform] if a.platform else out})


if __name__ == "__main__":
    main()

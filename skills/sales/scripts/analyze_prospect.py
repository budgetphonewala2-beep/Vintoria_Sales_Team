#!/usr/bin/env python3
"""
Prospect Analyzer — AI Sales Team for Claude Code
Fetches a company website and extracts structured, machine-readable signals for
prospect analysis: name, description, industry, tech stack, socials, team,
pricing tiers, hiring, contact info, size and funding signals.

Everything here is heuristic. Treat output as leads to verify, not facts.

Usage:
    python analyze_prospect.py --url https://example.com
    python analyze_prospect.py --url example.com --timeout 15
"""

import argparse
import json
import re
import sys
from urllib.parse import urlparse

from sales_common import (base_of, domain_slug, fetch_many, fetch_url, ld_types,
                          looks_like_soft_404, normalize_url, parse_html,
                          subpage_urls, text_fingerprint)

try:
    from contact_finder import (classify_department, classify_seniority,
                                extract_json_ld_people, extract_people,
                                predict_buying_role)
except ImportError:  # contact_finder.py should sit next to this file
    extract_people = None

# ---------------------------------------------------------------------------
# Signatures
# ---------------------------------------------------------------------------

# Patterns are matched against raw HTML + script URLs. Keep them specific to
# vendor domains / globals so ordinary words ("stripe", "drift") don't match.
TECH_SIGNATURES = {
    "WordPress":        [r"/wp-content/", r"/wp-includes/", r'content="WordPress'],
    "Shopify":          [r"cdn\.shopify\.com", r"Shopify\.theme"],
    "Webflow":          [r"website-files\.com", r"data-wf-page=", r"webflow\.js"],
    "Squarespace":      [r"static1\.squarespace\.com", r"squarespace-cdn\.com"],
    "Wix":              [r"static\.wixstatic\.com", r"parastorage\.com"],
    "Framer":           [r"framerusercontent\.com", r"framer\.com/m/"],
    "Next.js":          [r"/_next/static/", r"__NEXT_DATA__"],
    "Nuxt":             [r"/_nuxt/", r"__NUXT__"],
    "Gatsby":           [r"___gatsby", r"/page-data/app-data\.json"],
    "React":            [r"react(?:-dom)?(?:\.production)?(?:\.min)?\.js", r"/react@\d", r"data-reactroot", r"__NEXT_DATA__"],
    "Vue.js":           [r"vue(?:\.runtime)?(?:\.global)?(?:\.prod)?(?:\.min)?\.js", r"\sdata-v-[0-9a-f]{8}"],
    "Angular":          [r"\sng-version=", r"angular(?:\.min)?\.js"],
    "Google Analytics": [r"google-analytics\.com/", r"googletagmanager\.com/gtag/js"],
    "Google Tag Manager": [r"googletagmanager\.com/gtm\.js", r"GTM-[A-Z0-9]{4,}"],
    "Segment":          [r"cdn\.segment\.com", r"api\.segment\.io"],
    "Mixpanel":         [r"cdn\.mxpnl\.com", r"mixpanel\.init\("],
    "Amplitude":        [r"cdn\.amplitude\.com", r"amplitude\.getInstance\("],
    "Heap":             [r"cdn\.heapanalytics\.com"],
    "Hotjar":           [r"static\.hotjar\.com"],
    "HubSpot":          [r"js\.hs-scripts\.com", r"js\.hsforms\.net", r"js\.hs-analytics\.net", r"hbspt\.forms"],
    "Marketo":          [r"munchkin\.marketo\.net", r"\.mktoweb\.com"],
    "Pardot":           [r"pi\.pardot\.com", r"piAId\s*="],
    "Salesforce":       [r"\.force\.com/", r"salesforceliveagent\.com", r"service\.force\.com"],
    "Intercom":         [r"widget\.intercom\.io", r"js\.intercomcdn\.com", r"intercomSettings"],
    "Drift":            [r"js\.driftt\.com"],
    "Zendesk":          [r"static\.zdassets\.com", r"\.zendesk\.com/embeddable"],
    "Crisp":            [r"client\.crisp\.chat"],
    "Calendly":         [r"assets\.calendly\.com", r"calendly\.com/[\w-]+"],
    "Stripe":           [r"js\.stripe\.com"],
    "Facebook Pixel":   [r"connect\.facebook\.net/[\w_]+/fbevents\.js"],
    "LinkedIn Insight": [r"snap\.licdn\.com/li\.lms-analytics"],
    "Cloudflare":       [r"/cdn-cgi/", r"cdnjs\.cloudflare\.com"],
    "Sentry":           [r"browser\.sentry-cdn\.com", r"\.ingest\.sentry\.io"],
    "Optimizely":       [r"cdn\.optimizely\.com"],
}

ATS_SIGNATURES = {
    "Greenhouse": r"boards\.greenhouse\.io|job-boards\.greenhouse\.io|greenhouse\.io/embed",
    "Lever":      r"jobs\.lever\.co",
    "Ashby":      r"jobs\.ashbyhq\.com",
    "Workable":   r"apply\.workable\.com",
    "SmartRecruiters": r"jobs\.smartrecruiters\.com",
    "BambooHR":   r"\.bamboohr\.com/(?:jobs|careers)",
    "Workday":    r"myworkdayjobs\.com",
    "Recruitee":  r"\.recruitee\.com",
    "Teamtailor": r"\.teamtailor\.com",
    "Wellfound":  r"wellfound\.com/company",
}

SOCIAL_PATTERNS = {
    "linkedin":  r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/company/[\w%.-]+",
    "twitter":   r"https?://(?:www\.)?(?:twitter|x)\.com/(?!share|intent|home|search|hashtag|i/)[A-Za-z0-9_]{1,15}\b",
    "facebook":  r"https?://(?:www\.)?facebook\.com/(?!sharer|share|dialog|plugins|tr\b)[\w.-]+",
    "instagram": r"https?://(?:www\.)?instagram\.com/(?!p/|explore)[\w.]+",
    "youtube":   r"https?://(?:www\.)?youtube\.com/(?:c/|channel/|user/|@)[\w.-]+",
    "github":    r"https?://(?:www\.)?github\.com/(?!features|pricing|login|about|site)[\w-]+",
    "crunchbase": r"https?://(?:www\.)?crunchbase\.com/organization/[\w-]+",
}

# Whole-word / phrase keywords, matched against VISIBLE text + title + meta description.
INDUSTRY_KEYWORDS = {
    "SaaS":          ["saas", "software as a service", "cloud platform", "cloud-based", "free trial", "per seat"],
    "Fintech":       ["fintech", "financial technology", "payments", "payment processing", "banking", "lending", "invoicing"],
    "Healthcare":    ["healthcare", "health tech", "healthtech", "medical", "patients", "clinical", "hipaa", "telehealth"],
    "E-commerce":    ["ecommerce", "e-commerce", "online store", "add to cart", "free shipping", "shop now", "dtc"],
    "EdTech":        ["edtech", "learning platform", "online courses", "students", "teachers", "curriculum"],
    "Cybersecurity": ["cybersecurity", "threat detection", "vulnerability", "zero trust", "siem", "endpoint security"],
    "AI/ML":         ["artificial intelligence", "machine learning", "ai-powered", "generative ai", "llm", "ai agents"],
    "DevTools":      ["for developers", "developer platform", "developer tools", "sdk", "open source", "ci/cd", "devops", "api-first"],
    "MarTech":       ["marketing automation", "martech", "email marketing", "campaigns", "lead generation", "seo"],
    "HRTech":        ["hr software", "human resources", "recruiting", "payroll", "talent acquisition", "onboarding employees"],
    "Real Estate":   ["real estate", "property management", "proptech", "listings", "tenants", "brokerage"],
    "Logistics":     ["logistics", "supply chain", "freight", "fleet management", "warehouse", "last-mile"],
    "Agency/Services": ["agency", "our services", "consulting firm", "our clients", "we help brands", "retainer"],
    "Project/Work Mgmt": ["project management", "task management", "roadmaps", "issue tracking", "collaboration", "to-dos"],
    "Manufacturing": ["manufacturing", "industrial", "factory", "oem", "machinery"],
}

TIER_NAMES = ["Free", "Hobby", "Starter", "Basic", "Essential", "Essentials", "Standard", "Plus",
              "Pro", "Professional", "Team", "Teams", "Business", "Growth", "Scale", "Premium",
              "Advanced", "Ultimate", "Enterprise", "Custom", "Startup", "Personal", "Individual"]
_TIER_RE = re.compile(r"^(?:the\s+)?(" + "|".join(TIER_NAMES) + r")(?:\s+plan)?$", re.IGNORECASE)
_PRICE_RE = re.compile(
    r"(?P<cur>[$€£₹¥]|USD|EUR|GBP|INR)\s?(?P<amt>\d{1,3}(?:[,.]\d{3})*(?:[.,]\d{1,2})?|\d+(?:\.\d{1,2})?)"
    r"(?:\s*(?:/|per)\s*(?P<per>mo(?:nth)?|yr|year|annum|user|seat|member)\b)?",
    re.IGNORECASE)
_CUSTOM_PRICE_RE = re.compile(r"\b(contact (?:us|sales)|custom pricing|talk to sales|get a quote|let.s talk|book a demo)\b", re.I)

_JOB_SIGNALS = re.compile(
    r"\b(open (?:positions|roles)|job openings|we.re hiring|now hiring|current openings|"
    r"view (?:all )?(?:open )?(?:jobs|roles|positions)|apply now|join our team)\b", re.I)


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

def extract_company_name(parsed, slug=""):
    for item in parsed.json_ld():
        if any(t in ld_types(item) for t in ("organization", "corporation", "localbusiness")):
            if isinstance(item.get("name"), str) and item["name"].strip():
                return item["name"].strip()
    for key in ("og:site_name", "application-name", "apple-mobile-web-app-title"):
        if parsed.meta.get(key):
            return parsed.meta[key]
    title = (parsed.title or "").strip()
    if title:
        # split on separators surrounded by spaces so "Coca-Cola" survives
        parts = [p.strip() for p in re.split(r"\s[|·•–—-]\s|\s:\s", title) if p.strip()]
        root = re.sub(r"[^a-z0-9]", "", slug.split(".")[0]) if slug else ""
        for part in parts:  # prefer the segment that matches the domain ("Home | Acme" -> "Acme")
            squashed = re.sub(r"[^a-z0-9]", "", part.lower())
            if root and squashed and (root in squashed or squashed in root):
                return part
        if parts:
            return parts[0]
    for h in parsed.headings:
        if h["level"] == "h1":
            return h["text"]
    return ""


def extract_description(parsed):
    for key in ("description", "og:description", "twitter:description"):
        if parsed.meta.get(key):
            return parsed.meta[key]
    return ""


def detect_tech_stack(html, parsed):
    haystack = html + "\n" + "\n".join(parsed.scripts)
    detected = [tech for tech, pats in TECH_SIGNATURES.items()
                if any(re.search(p, haystack) for p in pats)]
    gen = parsed.meta.get("generator", "")
    if gen:
        name = re.split(r"[\s/]\d", gen)[0].strip()
        if name and not any(name.lower().startswith(d.lower()) for d in detected):
            detected.append(name)
    return sorted(set(detected))


def detect_ats(html):
    return sorted({name for name, pat in ATS_SIGNATURES.items() if re.search(pat, html, re.I)})


def extract_social_links(html):
    found = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        urls = []
        for m in re.findall(pattern, html, re.IGNORECASE):
            u = m.rstrip("/.\"'")
            if u.lower() not in (x.lower() for x in urls):
                urls.append(u)
        if urls:
            found[platform] = urls[:3]
    return found


def detect_industry(parsed):
    text = " ".join([parsed.title, parsed.meta.get("description", ""), parsed.text]).lower()
    scores = {}
    for industry, kws in INDUSTRY_KEYWORDS.items():
        hits = sum(len(re.findall(r"(?<![\w-])" + re.escape(kw) + r"(?![\w-])", text)) for kw in kws)
        distinct = sum(1 for kw in kws if re.search(r"(?<![\w-])" + re.escape(kw) + r"(?![\w-])", text))
        if distinct:
            scores[industry] = distinct * 3 + min(hits, 15)
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return [{"industry": k, "score": v} for k, v in ranked[:3]]


def extract_pricing_info(parsed):
    """Walk visible text in order: a line that is exactly a tier name starts a tier; the next
    price (or 'contact sales') before the next tier name belongs to it."""
    lines = parsed.lines
    tiers, current = [], None
    for line in lines:
        m = _TIER_RE.match(line.strip())
        if m:
            name = m.group(1).title()
            if current and current["price"] is None:
                current["price"] = "Not listed"
            if any(t["tier"].lower() == name.lower() for t in tiers):
                current = None  # repeated (e.g. comparison table) — ignore
                continue
            current = {"tier": name, "price": "$0" if name.lower() == "free" else None}
            tiers.append(current)
            continue
        if current and current["price"] is None:
            pm = _PRICE_RE.search(line)
            if pm:
                per = pm.group("per")
                current["price"] = pm.group("cur") + pm.group("amt") + (f"/{per}" if per else "")
            elif _CUSTOM_PRICE_RE.search(line):
                current["price"] = "Custom / Contact sales"
            elif current["tier"].lower() == "free" and re.search(r"\bfree\b|\$0\b", line, re.I):
                current["price"] = "$0"
    for t in tiers:
        if t["price"] is None:
            t["price"] = "$0" if t["tier"].lower() == "free" else "Not listed"
    # A pricing page without recognisable tier headings: report raw prices seen
    if not tiers:
        prices = []
        for m in _PRICE_RE.finditer(parsed.text):
            p = m.group(0).strip()
            if p not in prices:
                prices.append(p)
        tiers = [{"tier": f"Price point {i + 1}", "price": p} for i, p in enumerate(prices[:5])]
    return tiers[:8]


_ASSET_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".avif", ".css", ".js", ".ico")
_JUNK_EMAIL_DOMAINS = ("example.com", "domain.com", "email.com", "sentry.io", "wixpress.com",
                       "sentry-next.wixpress.com", "yourcompany.com", "company.com")


def extract_contact_info(html, parsed):
    emails = []
    sources = re.findall(r"mailto:([^\"'?>\s]+)", html, re.I) + \
        re.findall(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-zA-Z]{2,24}\b", parsed.text)
    for e in sources:
        e = e.strip().strip(".").lower()
        local, _, dom = e.partition("@")
        if not local or not dom or e.endswith(_ASSET_EXT) or dom in _JUNK_EMAIL_DOMAINS:
            continue
        if re.search(r"\d+\.\d+", dom) or not re.search(r"\.[a-z]{2,24}$", dom):
            continue  # package@1.2.3 etc.
        if e not in emails:
            emails.append(e)

    phones = []
    for t in re.findall(r"href=[\"']tel:([^\"']+)", html, re.I):
        t = re.sub(r"[^\d+]", "", t)
        if 7 <= len(re.sub(r"\D", "", t)) <= 15 and t not in phones:
            phones.append(t)
    # Visible-text phones must have separators or a leading +, so IDs/timestamps don't match
    for m in re.finditer(r"(?<![\w.])(\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)\s?|\d{2,4}[\s.-])\d{3,4}[\s.-]\d{3,5}(?!\w|\.\d)",
                         parsed.text):
        p = m.group(0).strip()
        digits = re.sub(r"\D", "", p)
        if 7 <= len(digits) <= 15 and not re.match(r"^(19|20)\d{2}[\s.-]", p) \
                and all(re.sub(r"\D", "", x) != digits for x in phones):
            phones.append(p)
    return {"emails": emails[:6], "phones": phones[:4]}


_CUSTOMER_CONTEXT = re.compile(r"\b(customers?|users?|clients?|companies|businesses|brands|teams use|"
                               r"trust|rely|organizations|developers|members|students|downloads)\b", re.I)


def estimate_company_size(parsed):
    signals = {}
    for item in parsed.json_ld():
        n = item.get("numberOfEmployees")
        if isinstance(n, dict):
            n = n.get("value") or n.get("maxValue") or n.get("minValue")
        if n:
            signals["employees_jsonld"] = str(n)
            break
    text = parsed.text
    # "people" only counts with team context ("team of 45 people", "120 people strong");
    # "employees"/"staff"/"team members" count on their own.
    for m in re.finditer(r"(?:team of|over|more than|nearly|about|almost|~)?\s*(\d[\d,]*)\+?\s*"
                         r"(?:employees|team members|staff|teammates|full-time employees|"
                         r"people (?:strong|on our team|work(?:ing)? (?:at|here|across)))\b"
                         r"|team of\s+(\d[\d,]*)\+?\s*(?:people|humans|engineers|experts)\b",
                         text, re.I):
        before = text[max(0, m.start() - 30):m.start()]
        after = text[m.end():m.end() + 40]
        if _CUSTOMER_CONTEXT.search(after) or re.search(
                r"\b(used by|trusted by|loved by|serving|serves|helped|helping|join)\s*$", before, re.I):
            continue
        signals["employees_stated"] = m.group(0).strip()
        break

    stages = []
    for pat, label in [(r"\bSeries ([A-H])\b", None), (r"\bpre-seed\b", "Pre-seed"),
                       (r"\bseed (?:round|funding|stage)\b", "Seed"),
                       (r"\bY Combinator\b|\bYC [WS]\d{2}\b", "Y Combinator-backed"),
                       (r"\b(?:NASDAQ|NYSE|LSE|NSE|BSE|TSX)\s*:\s*[A-Z.]{1,6}\b", "Public company"),
                       (r"\bbootstrapped\b", "Bootstrapped")]:
        for m in re.finditer(pat, text, re.I if label else 0):
            lab = label or f"Series {m.group(1)}"
            if lab not in stages:
                stages.append(lab)
    if stages:
        signals["funding_mentions"] = stages
    m = re.search(r"\b(?:raised|funding of|secured)\s+(?:a\s+)?([$€£₹]\s?\d+(?:\.\d+)?\s?(?:[MBK]|million|billion))",
                  text, re.I)
    if m:
        signals["funding_amount_mentioned"] = m.group(1)

    locs = []
    for item in parsed.json_ld():
        addr = item.get("address")
        for a in (addr if isinstance(addr, list) else [addr]):
            if isinstance(a, dict):
                loc = ", ".join(x for x in (a.get("addressLocality"), a.get("addressRegion"),
                                            a.get("addressCountry") if isinstance(a.get("addressCountry"), str) else "")
                                if x)
                if loc and loc not in locs:
                    locs.append(loc)
    for m in re.finditer(r"\b(?i:headquartered|based|offices?) in ((?:[A-Z][a-zA-Z]+)(?:,? (?:[A-Z][a-zA-Z]+)){0,3})",
                         text):
        loc = m.group(1).strip(" ,")
        if loc not in locs:
            locs.append(loc)
    if locs:
        signals["locations_mentioned"] = locs[:5]
    m = re.search(r"\b(?:founded|established|since)\s+(?:in\s+)?((?:19|20)\d{2})\b", text, re.I)
    if m:
        signals["founded_year"] = m.group(1)
    return signals


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

SUBPAGES = {
    "about":    ["/about", "/about-us", "/company"],
    "team":     ["/team", "/our-team", "/leadership", "/people"],
    "pricing":  ["/pricing", "/plans"],
    "careers":  ["/careers", "/jobs", "/join-us"],
    "customers": ["/customers", "/case-studies"],
    "blog":     ["/blog"],
    "contact":  ["/contact", "/contact-us"],
}


def analyze(url, timeout=10):
    url = normalize_url(url)
    result = {
        "url": url,
        "slug": domain_slug(url),
        "company_name": "",
        "description": "",
        "industry_signals": [],
        "tech_stack": [],
        "social_links": {},
        "team_members": [],
        "pricing_tiers": [],
        "has_job_postings": False,
        "ats_detected": [],
        "contact_info": {"emails": [], "phones": []},
        "company_size_signals": {},
        "pages_analyzed": [],
        "pages_found": {},
        "warnings": [],
        "errors": [],
    }

    home = fetch_url(url, timeout=timeout)
    if not home["html"] and urlparse(url).netloc and not urlparse(url).netloc.startswith("www."):
        alt = url.replace("://", "://www.", 1)
        home2 = fetch_url(alt, timeout=timeout)
        if home2["html"]:
            home = home2
    if not home["html"]:
        result["errors"].append(f"Failed to fetch homepage: {home['error'] or ('HTTP ' + str(home['status']))}")
        return result

    base = base_of(home["final_url"])
    result["final_url"] = home["final_url"]
    hp = parse_html(home["html"])
    home_fp = text_fingerprint(hp)
    result["pages_analyzed"].append(home["final_url"])
    result["company_name"] = extract_company_name(hp, result["slug"])
    result["description"] = extract_description(hp)

    if len(hp.text) < 300:
        result["warnings"].append(
            "Homepage has very little server-rendered text (likely a JavaScript app). "
            "Script results will be thin — rely on WebFetch/WebSearch for this prospect.")

    # Fetch all candidate subpages concurrently
    flat = [(kind, path) for kind, paths in SUBPAGES.items() for path in paths]
    pages = fetch_many(subpage_urls(base, [p for _, p in flat]), timeout=max(4, timeout - 2))

    all_html, all_parsed = [home["html"]], [hp]
    # Homepages are full of testimonials/investor quotes: only trust structured data there
    people = extract_json_ld_people(hp) if extract_people else []
    for (kind, _path), page in zip(flat, pages):
        if page["status"] != 200 or not page["html"]:
            continue
        parsed = parse_html(page["html"])
        if looks_like_soft_404(parsed, home_fp):
            continue
        if page["final_url"] in result["pages_analyzed"]:
            continue
        result["pages_analyzed"].append(page["final_url"])
        result["pages_found"].setdefault(kind, page["final_url"])
        all_html.append(page["html"])
        all_parsed.append(parsed)
        if kind in ("about", "team") and extract_people:
            people.extend(extract_people(page["html"], parsed))
        if kind == "pricing" and not result["pricing_tiers"]:
            result["pricing_tiers"] = extract_pricing_info(parsed)
        if kind == "careers":
            if _JOB_SIGNALS.search(parsed.text) or detect_ats(page["html"]):
                result["has_job_postings"] = True
        if kind == "contact":
            ci = extract_contact_info(page["html"], parsed)
            for k in ("emails", "phones"):
                for v in ci[k]:
                    if v not in result["contact_info"][k]:
                        result["contact_info"][k].append(v)

    combined_html = "\n".join(all_html)
    result["tech_stack"] = detect_tech_stack(home["html"], hp)
    result["ats_detected"] = detect_ats(combined_html)
    if result["ats_detected"]:
        result["has_job_postings"] = True
    result["social_links"] = extract_social_links(combined_html)
    result["industry_signals"] = detect_industry(hp)

    home_ci = extract_contact_info(home["html"], hp)
    for k in ("emails", "phones"):
        result["contact_info"][k] = list(dict.fromkeys(home_ci[k] + result["contact_info"][k]))[:6]

    size = {}
    for parsed in all_parsed:
        for k, v in estimate_company_size(parsed).items():
            if k == "funding_mentions":
                size.setdefault(k, [])
                size[k] += [x for x in v if x not in size[k]]
            elif k == "locations_mentioned":
                size.setdefault(k, [])
                size[k] += [x for x in v if x not in size[k]]
                size[k] = size[k][:5]
            else:
                size.setdefault(k, v)
    result["company_size_signals"] = size

    seen, team = set(), []
    for p in people:
        key = p["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        s = classify_seniority(p["title"])
        team.append({"name": p["name"], "title": p["title"], "seniority": s,
                     "department": classify_department(p["title"]),
                     "buying_role": predict_buying_role(p["title"], s),
                     "linkedin": p["linkedin"]})
    result["team_members"] = team[:25]

    if "pricing" not in result["pages_found"]:
        result["warnings"].append("No pricing page found at common paths.")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Prospect Analyzer — fetch and analyze a company website for sales intelligence.",
        epilog="Example: python analyze_prospect.py --url https://example.com",
    )
    parser.add_argument("--url", required=True, help="Company website URL to analyze")
    parser.add_argument("--output", choices=["json"], default="json", help="Output format (json)")
    parser.add_argument("--timeout", type=int, default=10, help="Per-request timeout in seconds (default 10)")
    args = parser.parse_args()

    result = analyze(args.url, timeout=args.timeout)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(1 if result["errors"] and not result["pages_analyzed"] else 0)


if __name__ == "__main__":
    main()

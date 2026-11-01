#!/usr/bin/env python3
"""
Contact Finder — AI Sales Team for Claude Code
Extracts leadership and team members from a company's public website and
classifies each person by seniority, department, and likely buying role.

Results are heuristic leads, not verified facts: confirm names/titles on
LinkedIn or the company site before using them in outreach.

Usage:
    python contact_finder.py --url https://example.com
    python contact_finder.py --url example.com --timeout 12
    python contact_finder.py --title "Director of Marketing"   # classify one title
"""

import argparse
import json
import re
import sys
from urllib.parse import urlparse

from sales_common import (base_of, domain_slug, fetch_many, fetch_url, ld_types,
                          looks_like_soft_404, normalize_url, parse_html,
                          subpage_urls, text_fingerprint)

TEAM_PATHS = ["/about", "/about-us", "/team", "/our-team", "/leadership",
              "/people", "/company", "/company/team", "/company/leadership",
              "/about/team", "/management", "/founders"]

# ---------------------------------------------------------------------------
# Title classification — ordered rules, whole-word matching
# ---------------------------------------------------------------------------

_C_LEVEL = r"\bc(?:e|t|f|m|p|r|i|s|d|o|h?r)o\b"   # ceo cto cfo cmo cpo cro cio cso cdo coo chro

SENIORITY_RULES = [
    ("Manager",  r"\bproduct owner\b"),
    ("VP",       r"\bchief of staff\b"),
    ("C-Suite",  r"\bchief\b|" + _C_LEVEL + r"|\bciso\b|\bco-?founder\b|\bfounder\b|"
                 r"\bfounding (?:ceo|partner)\b|\bmanaging (?:director|partner)\b|"
                 r"\bgeneral partner\b|\bgeneral counsel\b|\bowner\b|\bproprietor\b"),
    ("VP",       r"\bvice[\s-]+president\b|\b[se]?vp\b|\bavp\b|\bhead of\b|\bgeneral manager\b"),
    # "Partner" as a rank (law/VC/agency), not "Partner Marketing Manager"
    ("C-Suite",  r"\bpresident\b|^(?:senior |founding |equity )?partner\s*(?:$|[,&@(]|at\b)"),
    ("Board",    r"\bboard (?:member|director|observer)\b|\bboard of directors\b|\bnon-executive\b|\bindependent director\b|\badvis[oe]r\b|"
                 r"\binvestor\b|\bchair(?:man|woman|person)?\b"),
    ("Director", r"\bdirector\b"),
    ("Manager",  r"\bmanager\b|\bteam lead\b|\blead\b|\bsupervisor\b|\bhead\b"),
    ("IC",       r"\b(?:engineer|developer|analyst|specialist|coordinator|designer|associate|"
                 r"consultant|architect|scientist|representative|account executive|recruiter|"
                 r"writer|marketer|administrator|assistant|intern|advocate|strategist|"
                 r"researcher|editor|accountant|officer)\b"),
]

# Order matters for ties: earlier = preferred (e.g. "Sales Engineer" -> Sales).
DEPARTMENT_RULES = [
    ("Sales",            r"\bsales\b|\bbusiness development\b|\b[bs]dr\b|\baccount executive\b|"
                         r"\baccount manager\b|\brevenue\b|\bcro\b|\bpartnerships?\b|\bchannel\b|\balliances\b"),
    ("Marketing",        r"\bmarketing\b|\bgrowth\b|\bbrand\b|\bcontent\b|\bcmo\b|\bcommunications\b|"
                         r"\bdemand gen(?:eration)?\b|\bpr\b|\bpublic relations\b|\bseo\b|\bsocial media\b|\bcommunity\b"),
    ("Customer Success", r"\bcustomer (?:success|support|advocacy|advocate|care)\b|\bescalations?\b|\bsupport\b|\bclient services\b|"
                         r"\bcustomer experience\b|\bcx\b|\bonboarding\b"),
    ("Product",          r"\bproduct\b|\bcpo\b|\bux\b|\bui\b|\bdesign(?:er)?\b|\buser research\b"),
    ("Engineering",      r"\bengineering\b|\bengineer\b|\bdeveloper\b|\bsoftware\b|\bdevops\b|\binfrastructure\b|"
                         r"\bplatform\b|\barchitect\b|\bcto\b|\btechnical\b|\btechnology\b|\bfrontend\b|"
                         r"\bbackend\b|\bsre\b|\bsecurity\b|\bciso\b"),
    ("Data",             r"\bdata\b|\banalytics\b|\bmachine learning\b|\bml\b|\bai\b|\bbusiness intelligence\b|\bcdo\b"),
    ("IT",               r"\bit\b|\binformation technology\b|\bcio\b|\bsystems administrator\b|\bhelpdesk\b"),
    ("Finance",          r"\bfinance\b|\bfinancial\b|\bcfo\b|\baccounting\b|\baccountant\b|\bcontroller\b|"
                         r"\btreasurer\b|\binvestor relations\b|\bfp&a\b"),
    ("HR",               r"\bhuman resources\b|\bhr\b|\bpeople\b|\btalent\b|\brecruit(?:er|ing|ment)\b|"
                         r"\bculture\b|\bchro\b"),
    ("Legal",            r"\blegal\b|\bcounsel\b|\bcompliance\b|\bprivacy\b|\bclo\b|\battorney\b|\blawyer\b"),
    ("Operations",       r"\boperations\b|\bcoo\b|\bops\b|\bsupply chain\b|\blogistics\b|\bprocurement\b|\bpurchasing\b"),
]
_EXECUTIVE = r"\bceo\b|\bfounder\b|\bco-?founder\b|\bpresident\b|\bmanaging director\b|\bowner\b|\bchair"
_BLOCKER = r"\blegal\b|\bcounsel\b|\bcompliance\b|\bprocurement\b|\bpurchasing\b|\bvendor management\b|\bprivacy\b"


def classify_seniority(title):
    t = (title or "").lower()
    for level, pattern in SENIORITY_RULES:
        if re.search(pattern, t):
            return level
    return "Unknown"


def classify_department(title):
    t = (title or "").lower()
    best, best_hits = None, 0
    for dept, pattern in DEPARTMENT_RULES:
        hits = len(set(re.findall(pattern, t)))
        if hits > best_hits:
            best, best_hits = dept, hits
    if best:
        return best
    if re.search(_EXECUTIVE, t):
        return "Executive"
    return "Unknown"


def predict_buying_role(title, seniority=None):
    """Title-based guess at the person's role in a B2B purchase."""
    t = (title or "").lower()
    seniority = seniority or classify_seniority(title)
    if re.search(_BLOCKER, t):
        return "Blocker"
    return {
        "C-Suite": "Economic Buyer",
        "VP": "Champion",
        "Director": "Champion",
        "Board": "Influencer",
        "Manager": "Evaluator",
        "IC": "End User",
    }.get(seniority, "Unknown")


# ---------------------------------------------------------------------------
# Name / title validation
# ---------------------------------------------------------------------------

_PARTICLES = {"de", "da", "di", "del", "della", "van", "von", "der", "den", "la", "le",
              "du", "bin", "binti", "al", "el", "ben", "dos", "das", "st."}
_NOT_NAME_WORDS = {
    "our", "the", "about", "team", "meet", "leadership", "contact", "products", "product",
    "company", "careers", "career", "blog", "join", "read", "more", "learn", "board",
    "directors", "advisors", "investors", "customer", "customers", "success", "sales",
    "marketing", "engineering", "head", "chief", "officer", "vice", "president", "senior",
    "manager", "director", "inc", "inc.", "llc", "ltd", "ltd.", "gmbh", "pricing", "home",
    "privacy", "policy", "terms", "service", "services", "solutions", "platform", "get",
    "started", "sign", "login", "book", "demo", "new", "view", "all", "open", "roles",
    "people", "values", "mission", "story", "news", "press", "partners", "support", "help",
    "resources", "features", "case", "studies", "and", "&", "of", "for", "with", "us",
    "founders", "founder", "co-founder", "executive", "management", "office", "offices",
    "global", "free", "trial", "enterprise", "business", "plan", "plans", "faq", "why",
    "how", "what", "who", "we", "you", "your", "linkedin", "twitter", "github", "email",
    # common heading words that are capitalised like names
    "website", "project", "projects", "design", "redesign", "getting", "real", "message",
    "guide", "playbook", "tools", "tool", "developer", "developers", "skills", "agent",
    "agents", "ai", "data", "cloud", "app", "apps", "mobile", "web", "software", "work",
    "workflow", "workflows", "automation", "integrations", "integration", "security",
    "analytics", "reports", "report", "templates", "template", "tips", "best", "practices",
    "introducing", "announcing", "launch", "update", "updates", "release", "changelog",
    "docs", "documentation", "community", "events", "event", "webinar", "podcast", "jobs",
    "hiring", "remote", "culture", "benefits", "perks", "history", "vision", "principles",
    "manifesto", "shape", "up", "now", "today", "is", "are", "to", "in", "on", "by", "at",
    "a", "an", "it", "this", "that", "all-in-one", "online", "digital", "smart", "first",
    "next", "one", "two", "three", "world", "studio", "labs", "lab", "inc", "group", "fund",
    "ventures", "capital", "partners", "holdings", "foundation", "university", "school",
    "start", "page", "pages", "assistant", "made", "built",
}
_NAME_TOKEN = re.compile(
    r"^(?:[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]*(?:['’-][A-ZÀ-ÖØ-Þ]?[a-zà-öø-ÿ]+)*"   # Jane, O'Neil, Mary-Jane
    r"|[A-Z][a-z]*[A-Z][a-z]+"                                          # McKenzie, DeShawn
    r"|[A-Z]\.(?:[A-Z]\.)*)$"                                           # J. / J.R.
)
# Titles of people who are NOT employees (testimonials, investors, alumni)
_EXTERNAL_TITLE = re.compile(r"\bat\s+[A-Z0-9]|^(?:former|ex-|previously)\b|\bformerly\b", re.I)
_NOT_TITLE_WORDS = re.compile(
    r"\b(playbook|guide|book|project|template|templates|report|course|podcast|webinar|"
    r"feature|features|integration|board game|message board|kanban|dashboard)\b", re.I)


def looks_like_name(text):
    text = (text or "").strip()
    if not (4 <= len(text) <= 40) or re.search(r"[\d@/|:;!?(),\[\]{}<>=+#]", text):
        return False
    tokens = text.split()
    if not (2 <= len(tokens) <= 4):
        return False
    core = 0
    for tok in tokens:
        low = tok.lower()
        if low in _NOT_NAME_WORDS:
            return False
        if low in _PARTICLES:
            continue
        if not _NAME_TOKEN.match(tok):
            return False
        core += 1
    # need at least two real name tokens (initials and particles alone are not enough)
    return core >= 2


def looks_like_title(text):
    text = (text or "").strip()
    if not (2 <= len(text) <= 90) or len(text.split()) > 12:
        return False
    if re.search(r"https?://|@|\.(?:com|io|ai)\b", text) or _NOT_TITLE_WORDS.search(text):
        return False
    if _EXTERNAL_TITLE.search(text):
        return False  # "VP Sales at OtherCo" / "Former CEO, Slack" = testimonial or investor
    return classify_seniority(text) != "Unknown"


_SPLIT_RE = re.compile(r"^(.{4,40}?)\s*(?:[,|–—:]|\s-\s)\s*(.{2,90})$")


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def _person(name, title, linkedin="", source=""):
    return {"name": name.strip(), "title": (title or "").strip(),
            "linkedin": linkedin or "", "source": source}


def extract_json_ld_people(parsed):
    people = []

    def _from(item, default_title=""):
        if not isinstance(item, dict):
            return
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            return
        title = item.get("jobTitle") or item.get("roleName") or default_title
        if isinstance(title, list):
            title = ", ".join(str(t) for t in title)
        same_as = item.get("sameAs") or []
        if isinstance(same_as, str):
            same_as = [same_as]
        linkedin = next((s for s in same_as if isinstance(s, str) and "linkedin.com/in/" in s), "")
        people.append(_person(name, str(title), linkedin, "json-ld"))

    for item in parsed.json_ld():
        types = ld_types(item)
        if "person" in types:
            _from(item)
        if any(t in types for t in ("organization", "corporation", "localbusiness", "aboutpage")):
            for key in ("founder", "founders", "employee", "employees", "member", "members"):
                val = item.get(key)
                for v in (val if isinstance(val, list) else [val]):
                    _from(v, "Founder" if key.startswith("founder") else "")
    return people


def extract_text_people(parsed):
    """Name on one line followed by a title on the next (the most common team-card layout),
    or 'Name, Title' / 'Name — Title' on a single line."""
    people = []
    lines = parsed.element_lines
    i = 0
    while i < len(lines):
        line = lines[i]
        if looks_like_name(line):
            for j in (i + 1, i + 2):
                if j < len(lines) and looks_like_title(lines[j]) and not looks_like_name(lines[j]):
                    people.append(_person(line, lines[j], source="page"))
                    i = j
                    break
        else:
            m = _SPLIT_RE.match(line)
            if m and looks_like_name(m.group(1)) and looks_like_title(m.group(2)):
                people.append(_person(m.group(1), m.group(2), source="page"))
        i += 1
    return people


def attach_linkedin(people, html):
    """Find each person's LinkedIn URL inside their own card only: the region between their
    name and the next person's name. Prefer URLs whose slug contains the person's name."""
    if not html:
        return
    positions = []
    for p in people:
        idx = html.find(p["name"])
        positions.append(idx if idx >= 0 else None)
    order = sorted((pos, k) for k, pos in enumerate(positions) if pos is not None)
    for n, (pos, k) in enumerate(order):
        if people[k]["linkedin"]:
            continue
        end = order[n + 1][0] if n + 1 < len(order) else pos + 2500
        window = html[pos:min(end, pos + 2500)]
        urls = list(dict.fromkeys(re.findall(r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/[\w%-]+/?", window)))
        if not urls:
            continue
        tokens = [t.lower() for t in re.split(r"[\s.'’-]+", people[k]["name"]) if len(t) >= 3]
        named = [u for u in urls if any(t in u.lower() for t in tokens)]
        if named:
            people[k]["linkedin"] = named[0]
        elif len(urls) == 1:
            people[k]["linkedin"] = urls[0]


def extract_people(html, parsed=None):
    """All people found on one page (deduplicated, with LinkedIn attached)."""
    parsed = parsed or parse_html(html)
    people = extract_json_ld_people(parsed) + extract_text_people(parsed)
    seen, unique = set(), []
    for p in people:
        key = re.sub(r"\s+", " ", p["name"].lower())
        if key in seen:
            # keep the richer record (e.g. JSON-LD without title + page with title)
            for u in unique:
                if u["name"].lower() == key and not u["title"] and p["title"]:
                    u["title"] = p["title"]
            continue
        seen.add(key)
        unique.append(p)
    attach_linkedin(unique, html)
    return unique


def _discover_team_links(home_parsed, base):
    """Team-like pages linked from the homepage nav/footer (same host only)."""
    host = urlparse(base).netloc
    found = []
    for link in home_parsed.links:
        href = link["href"] or ""
        if not href or href.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        full = href if href.startswith("http") else base + "/" + href.lstrip("/")
        p = urlparse(full)
        if p.netloc != host:
            continue
        if re.search(r"(?:^|/)(?:team|our-team|leadership|people|founders|management|about|"
                     r"about-us|our-story|who-we-are)(?:/|$)", p.path.lower()):
            path = p.path.rstrip("/") or "/"
            if path != "/" and path not in found:
                found.append(path)
    return found[:5]


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

SENIORITY_ORDER = {"C-Suite": 0, "VP": 1, "Director": 2, "Board": 3, "Manager": 4, "IC": 5, "Unknown": 6}


def find_contacts(url, timeout=10):
    url = normalize_url(url)
    base = base_of(url)
    result = {"url": url, "slug": domain_slug(url), "pages_checked": [], "contacts": [],
              "total_found": 0, "errors": [], "warnings": [
                  "Heuristic extraction: verify every name/title before outreach. "
                  "buying_role is a title-based guess."]}

    home = fetch_url(url, timeout=timeout)
    if not home["html"]:
        result["errors"].append(f"Homepage unreachable: {home['error'] or home['status']}")
        return result
    home_parsed = parse_html(home["html"])
    home_fp = text_fingerprint(home_parsed)
    base = base_of(home["final_url"]) or base

    paths = list(dict.fromkeys(TEAM_PATHS + _discover_team_links(home_parsed, base)))
    pages = fetch_many(subpage_urls(base, paths), timeout=timeout)

    # Homepages are full of testimonials, so only trust structured data there
    all_people = extract_json_ld_people(home_parsed)
    for page in pages:
        if page["status"] == 200 and page["html"]:
            parsed = parse_html(page["html"])
            final = page["final_url"].split("#")[0]
            if looks_like_soft_404(parsed, home_fp) or final in result["pages_checked"]:
                continue
            result["pages_checked"].append(final)
            all_people.extend(extract_people(page["html"], parsed))
        elif page["status"] and page["status"] not in (404, 410):
            result["errors"].append(f"{page['url']}: {page['error'] or page['status']}")

    if len(home_parsed.text) < 300 and not result["pages_checked"]:
        result["warnings"].append(
            "Site appears to be JavaScript-rendered; little HTML content was available. "
            "Use WebFetch/WebSearch (e.g. LinkedIn, press releases) for leadership data.")

    seen, unique = set(), []
    for p in all_people:
        key = p["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        seniority = classify_seniority(p["title"])
        unique.append({
            "name": p["name"],
            "title": p["title"],
            "seniority": seniority,
            "department": classify_department(p["title"]),
            "buying_role": predict_buying_role(p["title"], seniority),
            "linkedin": p["linkedin"],
            "source": p["source"],
        })
    unique.sort(key=lambda x: SENIORITY_ORDER.get(x["seniority"], 6))
    result["contacts"] = unique[:40]
    result["total_found"] = len(unique)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Contact Finder — extract leadership/team info from a company website.",
        epilog="Example: python contact_finder.py --url https://example.com",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Company website URL")
    group.add_argument("--title", help="Classify a single job title and exit")
    parser.add_argument("--output", choices=["json"], default="json", help="Output format (json)")
    parser.add_argument("--timeout", type=int, default=10, help="Per-request timeout in seconds (default 10)")
    args = parser.parse_args()

    if args.title:
        s = classify_seniority(args.title)
        out = {"title": args.title, "seniority": s,
               "department": classify_department(args.title),
               "buying_role": predict_buying_role(args.title, s)}
    else:
        out = find_contacts(args.url, timeout=args.timeout)
    sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

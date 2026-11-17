#!/usr/bin/env python3
"""
Seller profile: everything about YOU that the agents need before they hunt, write or price anything.
Any agent that picks up these skills reads it first; if it's missing or thin, the agent interviews you
(vintoria-setup skill) and saves the answers here. Queries, ICP, emails and proposals are all built from it.

Location: ./SELLER-PROFILE.json (working folder), else <data home>/seller-profile.json.

Usage:
    python seller_profile.py init [--force]       # write an empty template to fill
    python seller_profile.py init --preset vintoria   # start from the Vintoria preset (catalog facts; the rest is asked)
    python seller_profile.py check                # completeness score + the exact questions still to ask
    python seller_profile.py questions            # the full intake interview, grouped
    python seller_profile.py show                 # the profile as loaded (with defaults applied)
    python seller_profile.py set offer.niches '["dental clinics", "med spas"]'    # set one field (JSON value or text)
"""

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import data_home, emit  # noqa: E402

FILE = "SELLER-PROFILE.json"
PRESETS = Path(__file__).resolve().parent / "presets"
SERVICE_CODES = ["web", "app", "seo", "marketing", "design", "software", "ecommerce", "video", "ai", "automation"]

TEMPLATE = {
    "seller": {"name": "", "company": "", "website": "", "email": "", "country": "", "timezone": "",
               "postal_address": "", "booking_url": "", "meeting_link": "", "linkedin": ""},
    "offer": {"services": [], "service_details": "", "niches": [], "platforms": [], "outcomes": [],
              "deal_size": {"min": None, "typical": None, "currency": "USD"}, "pricing_model": "",
              "delivery_time": "", "capacity_per_month": None},
    "targets": {"countries": ["US", "UK", "CA", "AU"], "cities": [], "company_size": "", "buyer_titles": [],
                "exclude_countries": ["India"], "exclude": ["agencies", "freelancers", "job seekers"], "languages": ["en"],
                "remote_ok": True},
    "proof": {"case_studies": [], "testimonials": [], "portfolio_url": "", "years_in_business": None,
              "projects_done": None, "team_size": None, "notable_clients": []},
    "positioning": {"differentiators": [], "guarantees": [], "why_us": ""},
    "signals": {"pains": [], "triggers": [], "tools_they_leave": [], "competitor_agencies": [], "niche_terms": []},
    "channels": {"email": True, "linkedin_manual": True, "public_replies_manual": True, "whatsapp": False, "calls": False},
}

# field path → (required?, question, why it matters, example)
QUESTIONS = [
    ("seller.company", True, "What's your agency/business name and website?", "used in every signature and proposal", "Pixelcraft Studio — pixelcraft.io"),
    ("seller.name", True, "Your name as it should appear when you email clients?", "sender identity (CAN-SPAM: truthful From)", "Ravi Sharma"),
    ("seller.email", True, "Which email address will you send from?", "sending + reply detection", "ravi@pixelcraft.io"),
    ("seller.postal_address", True, "Your business postal address for email signatures?", "required in US commercial email (CAN-SPAM)", "12 MG Road, Pune 411001, India"),
    ("seller.timezone", True, "Your time zone?", "meeting slots in both zones", "Asia/Kolkata"),
    ("offer.services", True, "Which services do you sell? (web, app, seo, marketing, design, software, ecommerce, video, ai, automation)", "drives every search query", "web, ecommerce"),
    ("offer.service_details", True, "Describe the offer in one or two lines — what exactly do you deliver?", "the email's 'what we do' line", "Shopify stores and redesigns for DTC brands, 3-6 weeks"),
    ("offer.niches", True, "Which industries/niches are your best fit? (top 1-5)", "niche words make queries 5-10x sharper", "DTC skincare, coffee brands, supplements"),
    ("offer.platforms", False, "Which platforms/tools do you specialise in?", "platform queries (\"Shopify developer\") and switch triggers", "Shopify, Klaviyo"),
    ("offer.outcomes", True, "What outcome do clients buy from you, in their words?", "subject lines and first lines", "faster store, higher conversion, launch on time"),
    ("offer.deal_size", True, "Typical project size and minimum you accept (with currency)?", "qualification + proposal options", "min 2000, typical 5000 USD"),
    ("offer.pricing_model", False, "Fixed price, monthly retainer, hourly?", "proposal structure", "fixed + optional retainer"),
    ("offer.delivery_time", False, "Typical delivery time?", "proposal timeline", "4 weeks"),
    ("targets.countries", True, "Which countries do you want clients from?", "geo filters, send times, compliance", "US, UK, CA, AU"),
    ("targets.cities", False, "Any cities to focus on (for local businesses)?", "Google Maps + local queries", "New York, Austin, London, Sydney"),
    ("targets.company_size", False, "Client size (employees or revenue)?", "Apollo/LinkedIn filters", "1-50 employees"),
    ("targets.buyer_titles", True, "Who signs off — which job titles?", "people search (Apollo, LinkedIn)", "Founder, Owner, CEO, Head of E-commerce"),
    ("targets.exclude_countries", False, "Any countries/markets to exclude?", "leads from these are dropped", "India"),
    ("proof.case_studies", True, "2-3 real results you can mention (client, result, link)?", "the only proof emails may cite — never invented", "Brew Co: store rebuilt in 4 weeks, conversion 1.8% → 2.6%"),
    ("proof.portfolio_url", False, "Portfolio / case-study link?", "follow-up email 3", "pixelcraft.io/work"),
    ("proof.years_in_business", False, "Years in business, projects done, team size?", "credibility line", "6 years, 120 projects, team of 8"),
    ("positioning.differentiators", True, "Why you over other agencies? (2-3 concrete reasons)", "objection handling + proposals", "Shopify Partner, US-hours availability, fixed price"),
    ("positioning.guarantees", False, "Any guarantee you really offer?", "risk reversal (only if true)", "free revisions for 30 days"),
    ("signals.pains", True, "What problems do clients have right before they hire you?", "pain-language queries", "slow store, low conversion, outdated design"),
    ("signals.triggers", False, "What events make them buy? (launch, funding, rebrand, migration...)", "trigger queries", "new product launch, rebrand, moving off Wix"),
    ("signals.tools_they_leave", False, "Which tools/platforms do clients move away from?", "switching queries", "Wix, Squarespace, WooCommerce"),
    ("seller.booking_url", False, "Booking link (Cal.com / Calendly)?", "sent only after a prospect says yes", "cal.com/ravi/20min"),
]


def path():
    local = Path(FILE)
    return local if local.exists() else data_home() / "seller-profile.json"


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load(p=None):
    p = Path(p) if p else path()
    if not p.exists():
        return None
    return _merge(TEMPLATE, json.loads(p.read_text(encoding="utf-8-sig")))


def get(profile, dotted):
    cur = profile
    for part in dotted.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def _filled(v):
    if isinstance(v, dict):
        return any(_filled(x) for x in v.values())
    return v not in (None, "", [], {})


def check(profile):
    if profile is None:
        return {"exists": False, "complete_pct": 0, "missing_required": [q[0] for q in QUESTIONS if q[1]],
                "ask": [q[2] for q in QUESTIONS if q[1]],
                "next": "No seller profile yet — run the vintoria-setup interview before hunting or writing anything."}
    req = [q for q in QUESTIONS if q[1]]
    missing = [q for q in req if not _filled(get(profile, q[0]))]
    optional_missing = [q for q in QUESTIONS if not q[1] and not _filled(get(profile, q[0]))]
    bad_services = [s for s in get(profile, "offer.services") or [] if s not in SERVICE_CODES]
    pct = round(100 * (len(req) - len(missing)) / len(req))
    return {"exists": True, "file": str(path()), "complete_pct": pct, "missing_required": [q[0] for q in missing],
            "ask": [q[2] for q in missing], "nice_to_have": [q[2] for q in optional_missing][:6],
            "problems": [f"unknown service code(s) {bad_services}; use {SERVICE_CODES}"] if bad_services else [],
            "next": "Ready." if not missing and not bad_services else "Ask the questions in 'ask' (one message), then save."}


def set_field(profile, dotted, raw):
    try:
        value = json.loads(raw)
    except ValueError:
        value = raw
    cur = profile
    parts = dotted.split(".")
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value
    return profile


def save(profile, p=None):
    p = Path(p) if p else (path() if path().exists() else Path(FILE))
    p.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(p)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Seller profile: who you are and what you sell (read by every skill).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init"); i.add_argument("--force", action="store_true")
    i.add_argument("--preset", choices=sorted(p.stem for p in PRESETS.glob("*.json")), help="start from a preset profile")
    sub.add_parser("check"); sub.add_parser("questions"); sub.add_parser("show")
    s = sub.add_parser("set"); s.add_argument("field"); s.add_argument("value")
    a = ap.parse_args(argv)
    if a.cmd == "init":
        if Path(FILE).exists() and not a.force:
            emit({"ok": False, "error": f"{FILE} exists — use --force to overwrite, or 'set' to change fields"}, 2)
        start = TEMPLATE
        if a.preset:
            preset = json.loads((PRESETS / f"{a.preset}.json").read_text(encoding="utf-8"))
            preset.pop("_about", None)
            start = _merge(TEMPLATE, preset)
        Path(FILE).write_text(json.dumps(start, indent=2) + "\n", encoding="utf-8")
        emit({"ok": True, "data": {"created": FILE, "next": "Fill it via the vintoria-setup interview, then run check."}})
    if a.cmd == "questions":
        emit({"ok": True, "data": {"questions": [{"field": f, "required": r, "ask": q, "why": w, "example": e}
                                                  for f, r, q, w, e in QUESTIONS]}})
    prof = load()
    if a.cmd == "check":
        emit({"ok": True, "data": check(prof)})
    if prof is None:
        emit({"ok": False, "error": "no seller profile — run: python seller_profile.py init (then the vintoria-setup interview)"}, 2)
    if a.cmd == "show":
        emit({"ok": True, "data": prof})
    prof = set_field(prof, a.field, a.value)
    emit({"ok": True, "data": {"saved": save(prof), "field": a.field, "value": get(prof, a.field)}})


if __name__ == "__main__":
    main()

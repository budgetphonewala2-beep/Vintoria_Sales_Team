#!/usr/bin/env python3
"""
From a buyer's post to a ready-to-write dossier, in one run — for every lead the hunt keeps, not just the top few.

  1. the post itself: the exact text, and any email / phone / WhatsApp / website written in it (free, always first)
  2. the person who wrote it: their LinkedIn profile (headline, company, company site, location, about) via an Apify
     profile scraper when APIFY_TOKEN is set, else their public profile snippet from a Google search
  3. their company's website, found in this order and never guessed:
       --site  →  a website written in the post  →  the company site on their profile  →
       a search for the company named in their headline, kept only when the result's domain matches that name
  4. with a website: the full deep scan (prospect_scan.py — audit, PageSpeed, company, people, best email, web research,
     ranked hooks), with the person's profile added to the dossier as evidence;
     without one: a dossier built from the post and the profile, the email/phone from the post, and the next step
     (reply under the post / DM — the user sends it)
Everything lands in prospects/<slug>/DOSSIER.json + .md and in the pipeline, so vintoria-outreach writes from facts.

Usage:
    python post_lead.py --post-url <url> --post-text "..." [--author "Jane Doe"] [--author-url <profile url>]
        [--headline "Founder at Glow Skin"] [--site glowskin.com] [--source serp:<query-id>] [--quote "<exact words>"]
        [--no-web] [--no-api] [--no-profile] [--no-pagespeed]
    python post_lead.py --hunt hunt.json [--only <url>,<url>] [--top 10]   # the buyers you kept from a hunt / watch file

Settings: APIFY_PROFILE_ACTOR (default harvestapi/linkedin-profile-scraper), APIFY_PROFILE_INPUT_KEY (the actor's
input field for the profile URL list, default "urls" — "queries" and "profileUrls" are sent too unless this is set).
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
import find_email  # noqa: E402
import lead_sources  # noqa: E402
import pipeline  # noqa: E402
import prospect_scan  # noqa: E402
from sales_common import api_json, domain_slug, emit, secret, setting  # noqa: E402

PROFILE_ACTOR = "harvestapi/linkedin-profile-scraper"
NOT_A_COMPANY_SITE = find_email.PLATFORMS | {
    "crunchbase.com", "glassdoor.com", "indeed.com", "bloomberg.com", "zoominfo.com", "apollo.io", "rocketreach.co",
    "clutch.co", "g2.com", "trustpilot.com", "bbb.org", "yelp.com", "yell.com", "pitchbook.com", "dnb.com", "owler.com",
    "signalhire.com", "lusha.com", "contactout.com", "theorg.com", "wellfound.com", "angel.co", "tiktok.com", "pinterest.com",
    "linktr.ee", "beacons.ai", "calendly.com", "cal.com", "notion.site", "substack.com", "producthunt.com", "ycombinator.com"}
ROLE_WORDS = re.compile(r"\b(founder|co-?founder|ceo|cto|coo|cmo|owner|director|head|vp|manager|lead|partner|president|"
                        r"principal|consultant|marketing|growth|operations|e-?commerce|product|sales|chief|officer|i help|helping)\b", re.I)


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def company_from_headline(headline):
    """'Founder at Glow Skin | DTC skincare' → 'Glow Skin'. Only what the headline literally says; None otherwise."""
    h = (headline or "").strip()
    m = re.search(r"(?:\bat\b|@)\s*([^|,·•\n()]+)", h, re.I)
    if m:
        name = m.group(1).strip(" -–—.")
        return name if 1 < len(name) <= 60 else None
    parts = [p.strip() for p in re.split(r"[|·•,]| - | – | — ", h) if p.strip()]
    if len(parts) >= 2 and ROLE_WORDS.search(parts[0]) and not ROLE_WORDS.search(parts[1]) and len(parts[1]) <= 40:
        return parts[1]
    return None


def is_company_site(domain):
    d = find_email._bare(domain)
    return bool(d) and "." in d and d not in find_email.WEBMAIL and not any(d == x or d.endswith("." + x) for x in NOT_A_COMPANY_SITE)


def domain_matches(domain, company):
    """The site's name must contain the company name (or the other way round) — 'glowskin.com' for 'Glow Skin'."""
    stem, name = _norm(find_email._bare(domain).split(".")[0]), _norm(re.sub(r"\b(inc|llc|ltd|limited|co|corp|gmbh|plc|the)\b\.?", "",
                                                                           company or "", flags=re.I))
    return bool(stem and name and len(min(stem, name, key=len)) >= 3 and (stem in name or name in stem))


# ----------------------------------------------------------------------------------------------- the person

def normalize_profile(item):
    """Profile-scraper item → {name, headline, company, company_site, company_linkedin, location, about, email, linkedin}."""
    f = lead_sources._first
    exp = item.get("experience") or item.get("positions") or item.get("currentPosition") or []
    cur = exp[0] if isinstance(exp, list) and exp else (exp if isinstance(exp, dict) else {})
    loc = f(item, "location.linkedinText", "location.default", "location.parsed.text", "location", "geoLocationName", "addressWithCountry")
    if isinstance(loc, dict):
        loc = f(loc, "linkedinText", "text", "name", "city")
    name = f(item, "fullName", "name") or " ".join(x for x in (f(item, "firstName"), f(item, "lastName")) if x) or None
    company = f(cur, "companyName", "company", "companyName.name") or f(item, "companyName", "company", "currentCompany.name")
    if isinstance(company, dict):
        company = company.get("name")
    return {"name": name, "first": f(item, "firstName"), "last": f(item, "lastName"),
            "headline": f(item, "headline", "occupation", "title", "jobTitle"),
            "company": company,
            "company_site": f(cur, "companyWebsite", "companyUrl.website") or f(item, "companyWebsite", "company_website",
                                                                               "currentCompany.website", "website"),
            "company_linkedin": f(cur, "companyLinkedinUrl", "companyUrl", "companyLink") or f(item, "companyLinkedinUrl"),
            "location": loc, "about": (f(item, "about", "summary", "description") or "")[:1500] or None,
            "email": f(item, "email", "emails.0.email", "emails.0"), "linkedin": f(item, "linkedinUrl", "url", "profileUrl")}


def scrape_profile(url, call=api_json):
    key = setting("APIFY_PROFILE_INPUT_KEY")
    inp = {key: [url]} if key else {"urls": [url], "queries": [url], "profileUrls": [url]}
    items = lead_sources.run_actor(setting("APIFY_PROFILE_ACTOR", PROFILE_ACTOR), inp, max_items=1, call=call)
    return normalize_profile(items[0]) if items else None


def profile_from_search(author, author_url=None, call=api_json):
    """No Apify: the public profile's Google result (title 'Jane Doe - Founder - Glow Skin | LinkedIn' + snippet)."""
    if not author:
        return None
    rows = lead_sources.google([f'site:linkedin.com/in "{author}"'], call=call)
    want = (author_url or "").split("?")[0].rstrip("/").lower()
    for r in rows:
        u = (r.get("url") or "").split("?")[0].rstrip("/").lower()
        if "linkedin.com/in/" not in u or (want and u != want and want.split("/in/")[-1] not in u):
            continue
        title = re.sub(r"\s*\|\s*LinkedIn\s*$", "", r.get("title") or "", flags=re.I)
        parts = [p.strip() for p in re.split(r" [-–—] ", title) if p.strip()]
        if not parts or _norm(parts[0]) != _norm(author):          # someone else with a similar name: not them
            continue
        return {"name": parts[0], "headline": " - ".join(parts[1:]) or None, "company": parts[-1] if len(parts) >= 3 else None,
                "company_site": None, "location": None, "about": r.get("text") or None, "email": None, "linkedin": r.get("url"),
                "from": "search snippet"}
    return None


# ----------------------------------------------------------------------------------------------- the company site

def find_company_site(company, call=api_json):
    if not company:
        return None
    for r in lead_sources.google([f'"{company}" official website', f'"{company}"'], call=call):
        d = domain_slug(r.get("url") or "")
        if is_company_site(d) and domain_matches(d, company):
            return {"site": d, "evidence": r.get("url"), "how": f"search for \"{company}\" — the domain matches the name"}
    return None


def resolve_site(post_text, person, headline, site=None, web=True, call=api_json):
    if site:
        return {"site": domain_slug(site), "how": "given", "evidence": site}
    for d in find_email.from_text(post_text)["websites"]:
        if is_company_site(d):
            return {"site": d, "how": "written in their post", "evidence": "their post"}
    if person and person.get("company_site") and is_company_site(domain_slug(person["company_site"])):
        return {"site": domain_slug(person["company_site"]), "how": "company website on their LinkedIn profile",
                "evidence": person.get("linkedin") or "their LinkedIn profile"}
    company = (person or {}).get("company") or company_from_headline(headline or (person or {}).get("headline"))
    if web and company:
        try:
            return find_company_site(company, call)
        except Exception:  # noqa: BLE001 - no search key: not resolved, never guessed
            return None
    return None


# ----------------------------------------------------------------------------------------------- the lead

def person_facts(person, author_url):
    if not person:
        return []
    ev = person.get("linkedin") or author_url or "their profile"
    tag = " (search snippet)" if person.get("from") == "search snippet" else ""
    out = []
    line = " — ".join(x for x in (person.get("name"), person.get("headline")) if x)
    if line:
        out.append({"key": "person_profile", "value": person.get("name"), "statement": line + (f" · {person['location']}" if person.get("location") else ""),
                    "evidence": ev})
    if person.get("company"):
        out.append({"key": "person_company", "value": person["company"], "statement": f"{person.get('name') or 'They'} works at {person['company']}",
                    "evidence": ev})
    if person.get("about"):
        out.append({"key": "person_about", "value": True, "statement": person["about"], "evidence": ev})
    if tag:                                       # a snippet is a lead, not proof — claim_check treats web_* keys as snippets
        for x in out:
            x["key"] = "web_" + x["key"]
    return out


def _split(name):
    parts = (name or "").split()
    return (parts[0], parts[-1] if len(parts) > 1 else "") if parts else ("", "")


def lead(post_url, post_text, author=None, author_url=None, headline=None, site=None, source=None, quote=None,
         web=True, use_api=True, profile=True, pagespeed=True, call=api_json, scan=prospect_scan.scan):
    post_text = (post_text or "").strip()
    if not post_text:
        raise ValueError("the post text is required — it is the evidence every email is written from")
    steps, person = {}, None
    if profile and author_url and "linkedin.com/in/" in author_url and secret("APIFY_TOKEN") and use_api:
        try:
            person = scrape_profile(author_url, call)
            steps["profile"] = "ok (Apify profile scraper)" if person else "no data"
        except Exception as exc:  # noqa: BLE001
            steps["profile"] = f"failed: {type(exc).__name__}: {exc}"[:200]
    if not person and profile and web and author:
        try:
            person = profile_from_search(author, author_url, call)
            steps["profile"] = steps.get("profile", "") + ("; " if steps.get("profile") else "") + \
                ("search snippet" if person else "not found in search")
        except Exception as exc:  # noqa: BLE001
            steps["profile"] = f"search failed: {type(exc).__name__}"[:200]
    author = author or (person or {}).get("name")
    headline = headline or (person or {}).get("headline")
    found = resolve_site(post_text, person, headline, site, web, call)
    first, last = _split(author)
    pfacts = person_facts(person, author_url)
    in_post = find_email.from_text(post_text)

    if found:
        d = scan(found["site"], name=(person or {}).get("company") or company_from_headline(headline), first=first or None,
                 last=last or None, post=post_text, post_url=post_url, web=web, use_api=use_api, source=source, pagespeed=pagespeed)
        folder = Path("prospects") / d["slug"]
        dj = folder / "DOSSIER.json"
        full = json.loads(dj.read_text(encoding="utf-8")) if dj.exists() else d
    else:
        slug = pipeline.platform_slug(post_url, author)
        folder = Path("prospects") / slug
        folder.mkdir(parents=True, exist_ok=True)
        em = None
        try:
            em = find_email.find("", first, last, post_text, use_api)
        except Exception as exc:  # noqa: BLE001
            steps["email"] = f"failed: {type(exc).__name__}"
        best = (em or {}).get("best")
        full = {"slug": slug, "url": post_url, "scanned_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "company": {"name": (person or {}).get("company") or author or slug}, "people": [], "audit_facts": [],
                "decision_maker": {"name": author, "first": first, "last": last, "title": headline, "linkedin": author_url,
                                   "source": "post author"} if author else None,
                "post": {"text": post_text[:3000], "url": post_url, "contacts": {k: v for k, v in in_post.items() if v}},
                "email": None if not em else {"best": best, "label": em.get("label"), "phone": em.get("phone"),
                                               "finders_skipped": em.get("finders_skipped"), "candidates": em.get("candidates")},
                "web": None, "errors": [], "steps": {},
                "facts": [{"key": "their_post", "value": True, "statement": post_text[:3000], "evidence": post_url or "their post"}],
                "hooks": prospect_scan.rank_hooks([], post_text, None)}
        full["readiness"] = {"verified_email": bool(best and best.get("status") == "verified"), "hooks": len(full["hooks"]),
                             "has_post": True, "web_research": False,
                             "next": "Email them (vintoria-outreach) — the address came from their post" if best else
                                     "No website or email: write a 2-line public reply or DM for the user to send from their own account"}
        conn = pipeline.connect()
        try:
            pipeline.add(conn, url=post_url, name=author, source=source, quote=quote, post=post_text if quote else None)
            if author or best:
                pipeline.add_contact(conn, slug, author or best["email"], title=headline, email=(best or {}).get("email"),
                                     email_status=(best or {}).get("status"), email_source=(best or {}).get("source"),
                                     linkedin=author_url if author_url and "/in/" in author_url else None, phone=(em or {}).get("phone"))
        finally:
            conn.close()
        quote = None                               # recorded above

    full["author"] = {"name": author, "url": author_url, "headline": headline, "profile": person}
    full["website_found"] = found or {"site": None, "how": "not found — no site in the post, on the profile, or a search result whose "
                                                           "domain matches the company name (never guessed)"}
    known = {(f.get("key"), f.get("statement")) for f in full.get("facts", [])}
    full["facts"] = full.get("facts", []) + [f for f in pfacts if (f["key"], f["statement"]) not in known]
    full.setdefault("steps", {}).update({f"lead_{k}": v for k, v in steps.items()})
    (folder / "DOSSIER.json").write_text(json.dumps(full, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (folder / "DOSSIER.md").write_text(prospect_scan.render_md(full), encoding="utf-8")
    if quote and found:
        conn = pipeline.connect()
        try:
            pipeline.add(conn, url=found["site"], quote=quote, post=post_text, source=source)
        finally:
            conn.close()
    return {"slug": full["slug"], "website": full["website_found"], "author": full["author"],
            "email": ((full.get("email") or {}).get("best")), "hooks": [h.get("observation") for h in full.get("hooks", [])[:4]],
            "readiness": full.get("readiness"), "saved": [str(folder / "DOSSIER.json"), str(folder / "DOSSIER.md")]}


def from_hunt(path, top=10, min_score=0.0, only=None, **kw):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("data", data) if isinstance(data, dict) else data
    rows = rows.get("posts") or rows.get("leads") or rows.get("candidates") or [] if isinstance(rows, dict) else rows
    rows = [r for r in rows if (r.get("intent_score") or r.get("score") or 1) >= min_score and (not only or r.get("url") in only)]
    rows.sort(key=lambda r: (r.get("age_hours") is None, r.get("age_hours") or 0))      # newest first
    out = []
    for r in rows[:top]:
        try:
            out.append(lead(r.get("url"), r.get("text") or r.get("title"), r.get("author"), r.get("author_url"),
                            r.get("author_headline"), source=(f"serp:{r['query']}" if r.get("query") and (r.get("provider") or r.get("source") in (None, "serp", "google"))
                                   else r.get("source")), **kw))
        except Exception as exc:  # noqa: BLE001 - one bad lead must not stop the batch
            out.append({"url": r.get("url"), "error": f"{type(exc).__name__}: {exc}"[:200]})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="A buyer's post → their profile, company site, deep scan, email → DOSSIER + pipeline.")
    ap.add_argument("--post-url"); g = ap.add_mutually_exclusive_group(); g.add_argument("--post-text"); g.add_argument("--post-file")
    ap.add_argument("--hunt", help="a hunt/watch JSON file: process every kept candidate (newest first)")
    ap.add_argument("--top", type=int, default=10); ap.add_argument("--min-score", type=float, default=0.0)
    ap.add_argument("--only", help="with --hunt: comma-separated post URLs you judged to be buyers (default: all candidates)")
    ap.add_argument("--author"); ap.add_argument("--author-url"); ap.add_argument("--headline"); ap.add_argument("--site")
    ap.add_argument("--source"); ap.add_argument("--quote", help="exact words from the post that prove intent (checked verbatim)")
    ap.add_argument("--no-web", action="store_true"); ap.add_argument("--no-api", action="store_true")
    ap.add_argument("--no-profile", action="store_true"); ap.add_argument("--no-pagespeed", action="store_true")
    a = ap.parse_args(argv)
    kw = {"web": not a.no_web, "use_api": not a.no_api, "profile": not a.no_profile, "pagespeed": not a.no_pagespeed}
    try:
        if a.hunt:
            only = {u.strip() for u in a.only.split(",") if u.strip()} if a.only else None
            emit({"ok": True, "data": {"leads": from_hunt(a.hunt, a.top, a.min_score, only, **kw)}})
        text = Path(a.post_file).read_text(encoding="utf-8-sig") if a.post_file else a.post_text
        if not (a.post_url and text):
            emit({"ok": False, "error": "give --post-url and --post-text/--post-file (or --hunt <file>)"}, 2)
        emit({"ok": True, "data": lead(a.post_url, text, a.author, a.author_url, a.headline, a.site, a.source, a.quote, **kw)})
    except (ValueError, pipeline.UserError, lead_sources.UserError) as exc:
        emit({"ok": False, "error": str(exc)}, 2)


if __name__ == "__main__":
    main()

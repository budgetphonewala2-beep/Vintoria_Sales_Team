#!/usr/bin/env python3
"""
Find and verify a contact email. A guessed address is NEVER reported as verified.

Waterfall (stops at the first verified address):
  1. text you pass with --text (e.g. the prospect's post): emails, phones, wa.me numbers, websites
  2. the company website: /, /contact, /contact-us, /about, /about-us (robots.txt respected):
     mailto: links, visible emails, tel:, wa.me, JSON-LD Organization/Person
  3. Hunter email-finder (first + last + domain)            — only if HUNTER_API_KEY is set
  4. Hunter email-verifier on the best unverified candidate — only if HUNTER_API_KEY is set
  5. no key and a name: pattern guesses, clearly labelled "pattern-guessed — verify before sending"

Statuses: verified | catch_all | unverified | invalid | pattern-guessed.
Hunter API v2 (hunter.io/api-documentation/v2): GET /v2/email-finder?domain&first_name&last_name,
GET /v2/email-verifier?email (202 = still verifying, poll again); auth header X-API-KEY.

Usage:
    python find_email.py --domain acme.com [--first Priya --last Mehta] [--text "post text"] [--no-hunter]
"""

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sales_common import api_json, emit, fetch_many, parse_html, ld_types, secret  # noqa: E402

EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,24}(?![\w-])")
WA_RE = re.compile(r"(?:https?://)?(?:wa\.me|api\.whatsapp\.com/send\?phone=)/?\+?(\d{8,15})", re.I)
PHONE_RE = re.compile(r"(?<![\w.])(\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)\s?|\d{2,5}[\s.-])\d{3,5}(?:[\s.-]?\d{3,5})?(?!\w|\.\d)")
URL_RE = re.compile(r"(?:https?://)?(?:www\.)?([a-z0-9][a-z0-9-]{0,62}(?:\.[a-z0-9-]{1,63})*\.[a-z]{2,24})", re.I)
PLATFORMS = {"linkedin.com", "lnkd.in", "reddit.com", "facebook.com", "instagram.com", "x.com", "twitter.com", "t.co",
             "youtube.com", "youtu.be", "wa.me", "whatsapp.com", "google.com", "bit.ly", "medium.com", "github.com",
             "upwork.com", "fiverr.com", "justdial.com", "indiamart.com", "wikipedia.org", "amazon.com", "amazon.in"}
WEBMAIL = {"gmail.com", "googlemail.com", "yahoo.com", "yahoo.in", "yahoo.co.in", "outlook.com", "hotmail.com", "live.com",
           "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com", "rediffmail.com", "zoho.com", "gmx.com"}
GENERIC = {"info", "contact", "hello", "hi", "sales", "support", "admin", "enquiry", "enquiries", "inquiry", "office",
           "team", "mail", "help", "care", "business", "booking", "bookings"}
NOREPLY = re.compile(r"^(no-?reply|donotreply|mailer-daemon|postmaster|bounce|abuse|privacy|legal|webmaster)")
RANK = {"verified": 4, "catch_all": 3, "unverified": 2, "pattern-guessed": 1, "invalid": 0}
HUNTER = "https://api.hunter.io/v2"
HUNTER_MAP = {"valid": "verified", "accept_all": "catch_all", "invalid": "invalid", "disposable": "invalid",
              "webmail": "unverified", "unknown": "unverified"}


def _bare(host):
    host = (host or "").lower().strip(".")
    return host[4:] if host.startswith("www.") else host


def _is_platform(d):
    d = _bare(d)
    return any(d == p or d.endswith("." + p) for p in PLATFORMS)


def clean_emails(cands):
    out = []
    for e in cands:
        e = e.strip().strip(".").lower()
        local, _, dom = e.partition("@")
        if not local or not dom or NOREPLY.match(local) or e.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")):
            continue
        if re.search(r"\d+\.\d+", dom) or dom in ("example.com", "domain.com", "email.com", "sentry.io"):
            continue
        if e not in out:
            out.append(e)
    return out


def from_text(text):
    text = text or ""
    emails = clean_emails(EMAIL_RE.findall(text))
    wa = list(dict.fromkeys("+" + m for m in WA_RE.findall(text)))
    phones = [m.group(0).strip() for m in PHONE_RE.finditer(text) if 8 <= len(re.sub(r"\D", "", m.group(0))) <= 15]
    sites = []
    for m in URL_RE.finditer(text):
        d = _bare(m.group(1))
        if m.start() > 0 and text[m.start() - 1] == "@":
            continue
        if "." in d and not _is_platform(d) and d not in WEBMAIL and not re.fullmatch(r"[\d.]+", d) and d not in sites:
            sites.append(d)
    for e in emails:
        d = e.split("@")[1]
        if d not in WEBMAIL and not _is_platform(d) and d not in sites:
            sites.append(d)
    return {"emails": emails, "phones": list(dict.fromkeys(phones))[:3], "whatsapp": wa[:2], "websites": sites[:3]}


def from_html(html):
    p = parse_html(html)
    emails, phones = [], []
    for l in p.links:
        h = l["href"].strip()
        if h.lower().startswith("mailto:"):
            emails.append(h[7:].split("?")[0])
        elif h.lower().startswith("tel:"):
            phones.append(re.sub(r"[^\d+]", "", h[4:]))
    emails += EMAIL_RE.findall(p.text)
    org, people = {}, []
    for item in p.json_ld():
        t = ld_types(item)
        if any(x in ("organization", "localbusiness", "corporation", "professionalservice", "store") for x in t):
            for k in ("name", "email", "telephone", "url"):
                if item.get(k) and k not in org:
                    org[k] = str(item[k])
            if item.get("email"):
                emails.append(str(item["email"]).replace("mailto:", ""))
            if item.get("telephone"):
                phones.append(str(item["telephone"]))
        if "person" in t and item.get("name"):
            people.append({"name": str(item["name"]), "jobTitle": str(item.get("jobTitle") or "")})
            if item.get("email"):
                emails.append(str(item["email"]).replace("mailto:", ""))
    return {"emails": clean_emails(emails), "phones": list(dict.fromkeys(x for x in phones if x))[:3],
            "whatsapp": list(dict.fromkeys("+" + m for m in WA_RE.findall(html or "")))[:2], "organization": org, "people": people}


def rank_emails(emails, domain, first="", last=""):
    first, last = (first or "").lower(), (last or "").lower()

    def key(e):
        local, dom = e.split("@")
        on = _bare(dom) == _bare(domain) or _bare(dom).endswith("." + _bare(domain))
        personal = (first and first in local) or (len(last) > 2 and last in local)
        return (0 if on else 1, 0 if personal else (1 if local in GENERIC else 2))
    return sorted(emails, key=key)


def patterns(first, last, domain):
    f, l = re.sub(r"[^a-z]", "", first.lower()), re.sub(r"[^a-z]", "", last.lower())
    if not f or not domain:
        return []
    out = [f"{f}@{domain}"]
    if l:
        out = [f"{f}.{l}@{domain}", f"{f}@{domain}", f"{f}{l}@{domain}", f"{f[0]}{l}@{domain}", f"{f}{l[0]}@{domain}"]
    return out


def hunter_finder(key, first, last, domain, call=api_json):
    status, d = call("GET", f"{HUNTER}/email-finder", headers={"X-API-KEY": key},
                     params={"domain": domain, "first_name": first, "last_name": last}, timeout=40)
    if status in (400, 404):
        return None
    if status >= 400:
        raise RuntimeError(f"Hunter email-finder HTTP {status}")
    data = (d or {}).get("data") or {}
    if not data.get("email"):
        return None
    hs = (data.get("verification") or {}).get("status") or "unknown"
    return {"email": data["email"].lower(), "status": HUNTER_MAP.get(hs, "unverified"), "hunter_status": hs, "score": data.get("score")}


def hunter_verify(key, email, call=api_json, sleep=time.sleep, polls=3):
    for i in range(polls + 1):
        status, d = call("GET", f"{HUNTER}/email-verifier", headers={"X-API-KEY": key}, params={"email": email}, timeout=40)
        if status in (202, 222) and i < polls:
            sleep(5)
            continue
        if status >= 400:
            raise RuntimeError(f"Hunter email-verifier HTTP {status}")
        data = (d or {}).get("data") or {}
        hs = data.get("status") or "unknown"
        return {"status": HUNTER_MAP.get(hs, "unverified"), "hunter_status": hs, "score": data.get("score")}
    return {"status": "unverified", "hunter_status": "in_progress", "score": None}


def find(domain="", first="", last="", text="", use_hunter=True, fetch=fetch_many, call=api_json):
    steps, cands = [], []

    def add(email, status, source):
        for c in cands:
            if c["email"] == email:
                if RANK[status] > RANK[c["status"]]:
                    c["status"] = status
                return
        cands.append({"email": email, "status": status, "source": source})

    found = from_text(text)
    steps.append({"step": "text", **found})
    for e in found["emails"]:
        add(e, "unverified", "text")
    domain = _bare(domain) or (found["websites"][0] if found["websites"] else "")
    phone = (found["whatsapp"] + found["phones"] or [None])[0]
    if domain:
        from site_audit import Robots
        robots = Robots(f"https://{domain}")
        pages = [u for u in (urljoin(f"https://{domain}", p) for p in ("/", "/contact", "/contact-us", "/about", "/about-us"))
                 if robots.allowed(u)]
        site = {"emails": [], "phones": [], "whatsapp": [], "pages": [], "organization": {}, "people": []}
        for r in fetch(pages):
            if r.get("status") != 200 or not r.get("html"):
                continue
            site["pages"].append(r.get("final_url"))
            ex = from_html(r["html"])
            for k in ("emails", "phones", "whatsapp"):
                site[k] = list(dict.fromkeys(site[k] + ex[k]))
            site["organization"] = site["organization"] or ex["organization"]
            site["people"] += [p for p in ex["people"] if p not in site["people"]]
        site["emails"] = rank_emails(site["emails"], domain, first, last)
        steps.append({"step": "website", "domain": domain, **site})
        for e in site["emails"][:4]:
            add(e, "unverified", "website")
        phone = phone or (site["whatsapp"] + site["phones"] or [None])[0]
    key = secret("HUNTER_API_KEY") if use_hunter else None
    have = lambda: any(c["status"] == "verified" for c in cands)  # noqa: E731
    if key and domain and first and last and domain not in WEBMAIL and not have():
        try:
            hf = hunter_finder(key, first, last, domain, call)
            steps.append({"step": "hunter_finder", "result": hf})
            if hf:
                add(hf["email"], hf["status"], "hunter_finder")
        except RuntimeError as exc:
            steps.append({"step": "hunter_finder", "error": str(exc)})
    if key and not have():
        for c in [c for c in cands if c["status"] == "unverified"][:3]:
            try:
                v = hunter_verify(key, c["email"], call)
            except RuntimeError as exc:
                steps.append({"step": "hunter_verifier", "email": c["email"], "error": str(exc)})
                break
            steps.append({"step": "hunter_verifier", "email": c["email"], **v})
            c["status"] = v["status"]
            if c["status"] == "verified":
                break
    if not key and not cands and first and domain:
        for e in patterns(first, last, domain):
            add(e, "pattern-guessed", "pattern")
        steps.append({"step": "patterns", "note": "No HUNTER_API_KEY — these are guesses, NOT verified. Verify before sending."})
    order = {"text": 0, "website": 1, "hunter_finder": 2, "pattern": 3}
    best = sorted(cands, key=lambda c: (-RANK[c["status"]], order.get(c["source"], 9)))[0] if cands else None
    return {"domain": domain or None, "best": best, "candidates": cands, "phone": phone, "steps": steps,
            "verifier_available": bool(key),
            "label": None if not best else {"verified": "verified", "catch_all": "catch-all domain — deliverability uncertain",
                                            "unverified": "unverified — verify before sending",
                                            "pattern-guessed": "pattern-guessed — verify before sending",
                                            "invalid": "invalid — do not send"}[best["status"]]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Find and verify a contact email (never reports guesses as verified).")
    ap.add_argument("--domain", default="")
    ap.add_argument("--first", default="")
    ap.add_argument("--last", default="")
    ap.add_argument("--text", default="", help="text to mine first (e.g. the prospect's post)")
    ap.add_argument("--no-hunter", action="store_true", help="don't use Hunter even if a key is set")
    a = ap.parse_args(argv)
    if not (a.domain or a.text):
        emit({"ok": False, "error": "give --domain and/or --text"}, 2)
    emit({"ok": True, "data": find(a.domain, a.first, a.last, a.text, not a.no_hunter)})


if __name__ == "__main__":
    main()


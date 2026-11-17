#!/usr/bin/env python3
"""
Find and verify a contact email. A guessed address is NEVER reported as verified.

Waterfall (stops at the first verified address; every paid step only runs if its key is set):
  1. text you pass with --text (e.g. the prospect's post): emails, phones, wa.me numbers, websites
  2. the company website: /, /contact, /contact-us, /about, /about-us (robots.txt respected):
     mailto: links, visible emails, tel:, wa.me, JSON-LD Organization/Person
  3. finders, in EMAIL_FINDERS order (default prospeo,findymail,hunter,apollo), with first + last + domain:
       prospeo    PROSPEO_API_KEY    POST api.prospeo.io/enrich-person   (X-KEY; only_verified_email)
       findymail  FINDYMAIL_API_KEY  POST app.findymail.com/api/search/name (Bearer; returns verified emails)
       hunter     HUNTER_API_KEY     GET  api.hunter.io/v2/email-finder   (X-API-KEY)
       apollo     APOLLO_API_KEY     POST api.apollo.io/api/v1/people/match (X-Api-Key)
  4. verifiers, in EMAIL_VERIFIERS order (default millionverifier,zerobounce,neverbounce,hunter), on the
     best unverified candidates — and, when nothing was found, on the likely name patterns:
       millionverifier MILLIONVERIFIER_API_KEY · zerobounce ZEROBOUNCE_API_KEY · neverbounce NEVERBOUNCE_API_KEY · hunter
  5. no verifier and a name: pattern guesses, clearly labelled "pattern-guessed — verify before sending"
A provider that errors (no credits, HTTP 4xx/5xx) is skipped and the next one is tried.
No credits are spent on finders when the address is already known: an email written in the post itself, or
(for the named person) a personal address on their website, skips step 3 — it is only verified.

Statuses: verified | catch_all | unverified | invalid | pattern-guessed.
Hunter API v2 (hunter.io/api-documentation/v2): GET /v2/email-finder?domain&first_name&last_name,
GET /v2/email-verifier?email (202 = still verifying, poll again); auth header X-API-KEY.

Usage:
    python find_email.py --domain acme.com [--first Priya --last Mehta] [--text "post text"] [--no-api]
    python find_email.py --providers        # which finders/verifiers have keys, in which order
"""

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import api_json, emit, fetch_many, parse_html, ld_types, secret, setting  # noqa: E402

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


def _check(name, status, d):
    if status in (400, 404, 422):
        return False
    if status >= 400:
        raise RuntimeError(f"{name} HTTP {status}")
    return True


def prospeo_finder(key, first, last, domain, call=api_json):
    status, d = call("POST", "https://api.prospeo.io/enrich-person", headers={"X-KEY": key}, timeout=40,
                     body={"only_verified_email": True, "data": {"first_name": first, "last_name": last, "company_website": domain}})
    if not _check("Prospeo", status, d) or (d or {}).get("error"):
        code = (d or {}).get("error_code")
        if code and code not in ("NO_MATCH", "INVALID_DATAPOINTS"):
            raise RuntimeError(f"Prospeo {code}")
        return None
    em = ((d or {}).get("person") or {}).get("email") or {}
    addr = em.get("email") if isinstance(em, dict) else em
    if not addr:
        return None
    st = (em.get("status") if isinstance(em, dict) else "") or ""
    return {"email": addr.lower(), "status": "verified" if st.upper() == "VERIFIED" else "unverified", "provider_status": st}


def findymail_finder(key, first, last, domain, call=api_json):
    status, d = call("POST", "https://app.findymail.com/api/search/name", headers={"Authorization": f"Bearer {key}"},
                     body={"name": f"{first} {last}".strip(), "domain": domain}, timeout=60)
    if not _check("Findymail", status, d):
        return None
    c = (d or {}).get("contact") or {}
    if not c.get("email"):
        return None
    return {"email": c["email"].lower(), "status": "verified", "provider_status": "verified by Findymail"}


def apollo_finder(key, first, last, domain, call=api_json):
    status, d = call("POST", "https://api.apollo.io/api/v1/people/match", headers={"X-Api-Key": key}, timeout=40,
                     body={"first_name": first, "last_name": last, "domain": domain, "reveal_personal_emails": False})
    if not _check("Apollo", status, d):
        return None
    person = (d or {}).get("person") or {}
    if not person.get("email") or "email_not_unlocked" in person["email"]:
        return None
    st = (person.get("email_status") or "").lower()
    return {"email": person["email"].lower(), "status": "verified" if st == "verified" else "unverified", "provider_status": st,
            "title": person.get("title"), "linkedin": person.get("linkedin_url")}


def hunter_finder_step(key, first, last, domain, call=api_json):
    return hunter_finder(key, first, last, domain, call)


MV_MAP = {"ok": "verified", "catch_all": "catch_all", "invalid": "invalid", "disposable": "invalid", "unknown": "unverified"}
ZB_MAP = {"valid": "verified", "catch-all": "catch_all", "invalid": "invalid", "spamtrap": "invalid", "abuse": "invalid",
          "do_not_mail": "invalid", "unknown": "unverified"}
NB_MAP = {"valid": "verified", "catchall": "catch_all", "invalid": "invalid", "disposable": "invalid", "unknown": "unverified"}


def millionverifier(key, email, call=api_json):
    status, d = call("GET", "https://api.millionverifier.com/api/v3/", params={"api": key, "email": email, "timeout": 20}, timeout=40)
    if status >= 400 or (d or {}).get("error"):
        raise RuntimeError(f"MillionVerifier {(d or {}).get('error') or 'HTTP ' + str(status)}")
    r = (d or {}).get("result") or "unknown"
    return {"status": MV_MAP.get(r, "unverified"), "provider_status": r}


def zerobounce(key, email, call=api_json):
    status, d = call("GET", "https://api.zerobounce.net/v2/validate", params={"api_key": key, "email": email, "ip_address": ""},
                     timeout=40)
    if status >= 400 or (d or {}).get("error"):
        raise RuntimeError(f"ZeroBounce {(d or {}).get('error') or 'HTTP ' + str(status)}")
    r = ((d or {}).get("status") or "unknown").lower()
    return {"status": ZB_MAP.get(r, "unverified"), "provider_status": r}


def neverbounce(key, email, call=api_json):
    status, d = call("GET", "https://api.neverbounce.com/v4/single/check", params={"key": key, "email": email}, timeout=40)
    if status >= 400 or (d or {}).get("status") not in (None, "success"):
        raise RuntimeError(f"NeverBounce {(d or {}).get('message') or 'HTTP ' + str(status)}")
    r = (d or {}).get("result") or "unknown"
    return {"status": NB_MAP.get(r, "unverified"), "provider_status": r}


def hunter_verifier_step(key, email, call=api_json):
    v = hunter_verify(key, email, call)
    return {"status": v["status"], "provider_status": v["hunter_status"], "score": v.get("score")}


FINDERS = {"prospeo": ("PROSPEO_API_KEY", prospeo_finder), "findymail": ("FINDYMAIL_API_KEY", findymail_finder),
           "hunter": ("HUNTER_API_KEY", hunter_finder_step), "apollo": ("APOLLO_API_KEY", apollo_finder)}
VERIFIERS = {"millionverifier": ("MILLIONVERIFIER_API_KEY", millionverifier), "zerobounce": ("ZEROBOUNCE_API_KEY", zerobounce),
             "neverbounce": ("NEVERBOUNCE_API_KEY", neverbounce), "hunter": ("HUNTER_API_KEY", hunter_verifier_step)}


def providers(kind):
    table, default = (FINDERS, "prospeo,findymail,hunter,apollo") if kind == "finders" else \
                     (VERIFIERS, "millionverifier,zerobounce,neverbounce,hunter")
    order = [x.strip().lower() for x in setting(f"EMAIL_{kind.upper()}", default).split(",") if x.strip()]
    out = []
    for name in order:
        if name in table:
            key = secret(table[name][0])
            if key:
                out.append((name, key, table[name][1]))
    return out


def log_verification(email, status, provider):
    """Append-only record of every real verification result. pipeline.py trusts 'verified' only when it is in here —
    an agent cannot mark an address verified just by typing it."""
    import json as _json
    from datetime import datetime, timezone
    from sales_common import data_home
    with open(data_home() / "verifications.jsonl", "a", encoding="utf-8") as f:
        f.write(_json.dumps({"email": email.lower(), "status": status, "provider": provider,
                             "at": datetime.now(timezone.utc).replace(microsecond=0).isoformat()}) + "\n")


def verified_in_log(email):
    import json as _json
    from sales_common import data_home
    path = data_home() / "verifications.jsonl"
    if not path.exists():
        return False
    last = None
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = _json.loads(line)
        except ValueError:
            continue
        if r.get("email") == (email or "").lower():
            last = r
    return bool(last and last.get("status") == "verified")


def verify_only(email, call=api_json):
    """Run the verifier chain on one known address (e.g. from Apollo or a post). No finder credits."""
    steps = []
    for name, key, fn in providers("verifiers"):
        try:
            v = fn(key, email, call)
        except RuntimeError as exc:
            steps.append({"verifier": name, "error": str(exc)})
            continue
        log_verification(email, v["status"], name)
        return {"email": email.lower(), "status": v["status"], "verified_by": name, "provider_status": v.get("provider_status"),
                "steps": steps}
    return {"email": email.lower(), "status": "unverified", "verified_by": None, "steps": steps,
            "note": "no verifier key (or all failed) — set MILLIONVERIFIER_API_KEY / ZEROBOUNCE_API_KEY / NEVERBOUNCE_API_KEY"}


def find(domain="", first="", last="", text="", use_hunter=True, fetch=fetch_many, call=api_json, max_verifications=4):
    """use_hunter=False disables every paid API (kept as the parameter name for compatibility)."""
    steps, cands = [], []

    def add(email, status, source, **extra):
        for c in cands:
            if c["email"] == email:
                if RANK[status] > RANK[c["status"]]:
                    c["status"] = status
                c.update({k: v for k, v in extra.items() if v})
                return
        cands.append({"email": email, "status": status, "source": source, **{k: v for k, v in extra.items() if v}})

    found = from_text(text)
    steps.append({"step": "text", **found})
    for e in found["emails"]:
        add(e, "unverified", "post")
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
    finders = providers("finders") if use_hunter else []
    verifiers = providers("verifiers") if use_hunter else []
    have = lambda: any(c["status"] == "verified" for c in cands)  # noqa: E731
    personal = lambda: any(first and first.lower() in c["email"].split("@")[0] and c["status"] == "verified" for c in cands)  # noqa: E731
    skip_reason = None
    if any(c["source"] == "post" for c in cands):
        skip_reason = "email already in the post — no finder credits spent"
    elif first and any(c["source"] == "website" and first.lower() in c["email"].split("@")[0] for c in cands):
        skip_reason = f"personal address for {first} already on their website — no finder credits spent"
    elif not first and any(c["source"] == "website" for c in cands):
        skip_reason = "no person named and the website lists an address — no finder credits spent"
    if skip_reason:
        steps.append({"step": "finders_skipped", "reason": skip_reason})
    if domain and first and last and domain not in WEBMAIL and not skip_reason:
        for name, key, fn in finders:
            if personal():
                break
            try:
                res = fn(key, first, last, domain, call)
                steps.append({"step": f"{name}_finder", "result": res})
                if res:
                    log_verification(res["email"], res["status"], f"{name}_finder")
                    add(res["email"], res["status"], f"{name}_finder", provider_status=res.get("provider_status"),
                        title=res.get("title"), linkedin=res.get("linkedin"))
            except RuntimeError as exc:
                steps.append({"step": f"{name}_finder", "error": str(exc)})
    used = 0
    if verifiers and not have():
        todo = [c for c in cands if c["status"] == "unverified"]
        if not todo and first and domain and domain not in WEBMAIL:      # nothing found: test the likely patterns
            for e in patterns(first, last, domain)[:3]:
                add(e, "unverified", "pattern")
            todo = [c for c in cands if c["source"] == "pattern"]
        for c in todo:
            if used >= max_verifications or have():
                break
            for name, key, fn in verifiers:
                try:
                    v = fn(key, c["email"], call)
                except RuntimeError as exc:
                    steps.append({"step": f"{name}_verifier", "email": c["email"], "error": str(exc)})
                    continue
                used += 1
                steps.append({"step": f"{name}_verifier", "email": c["email"], **v})
                c["status"], c["verified_by"] = v["status"], name
                log_verification(c["email"], v["status"], name)
                break
        for c in cands:      # an unverified pattern is still just a guess
            if c["source"] == "pattern" and c["status"] == "unverified":
                c["status"] = "pattern-guessed"
    if not verifiers and not cands and first and domain:
        for e in patterns(first, last, domain):
            add(e, "pattern-guessed", "pattern")
        steps.append({"step": "patterns", "note": "No verifier key — these are guesses, NOT verified. Verify before sending."})
    order = {"post": 0, "website": 1, "pattern": 9}
    best = sorted(cands, key=lambda c: (-RANK[c["status"]], order.get(c["source"], 2)))[0] if cands else None
    return {"domain": domain or None, "best": best, "candidates": cands, "phone": phone, "steps": steps,
            "finders_used": [n for n, _, _ in finders], "verifiers_used": [n for n, _, _ in verifiers],
            "verifier_available": bool(verifiers), "verifications": used, "finders_skipped": skip_reason,
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
    ap.add_argument("--no-api", "--no-hunter", dest="no_api", action="store_true", help="don't call any paid API")
    ap.add_argument("--providers", action="store_true", help="show configured finders/verifiers and exit")
    ap.add_argument("--email", help="you already have the address: only verify it (no finder credits)")
    a = ap.parse_args(argv)
    if a.email:
        emit({"ok": True, "data": verify_only(a.email)})
    if a.providers:
        emit({"ok": True, "data": {"finders": [n for n, _, _ in providers("finders")],
                                   "verifiers": [n for n, _, _ in providers("verifiers")],
                                   "all_finders": list(FINDERS), "all_verifiers": list(VERIFIERS),
                                   "order": "set EMAIL_FINDERS / EMAIL_VERIFIERS in ~/.ai-sales-team/.env"}})
    if not (a.domain or a.text):
        emit({"ok": False, "error": "give --domain and/or --text"}, 2)
    emit({"ok": True, "data": find(a.domain, a.first, a.last, a.text, not a.no_api)})


if __name__ == "__main__":
    main()


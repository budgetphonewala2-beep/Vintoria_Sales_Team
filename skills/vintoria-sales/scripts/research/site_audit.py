#!/usr/bin/env python3
"""
Fact-only website audit — proof-of-work for outreach. Standard library only.

Every fact has a `statement` (a sentence an email may reuse) and the `evidence` that proves it.
No opinions. robots.txt is respected. Outreach drafts are checked against these facts by
claim_check.py, so an email can only say what the audit actually observed.

Usage:
    python site_audit.py --url https://example.com [--no-links] [--save prospects/example.com/SITE-AUDIT.json]

Facts: HTTP status, HTTPS + http->https redirect, homepage download time, HTML size, title, meta
description, mobile viewport, H1 count, contact form, click-to-call, WhatsApp link, call-to-action,
images without alt, tech hints (WordPress, Shopify, Wix, Webflow, Squarespace, Next.js, ...),
footer copyright year, resource counts, first 20 internal links checked for 4xx/5xx.
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import urldefrag, urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import USER_AGENT, ApiError, api_json, emit, fetch_url, normalize_url, parse_html, secret  # noqa: E402

CTA_RE = re.compile(
    r"\b(get (?:a |your )?(?:free )?(?:quote|estimate|started)|contact us|book (?:a |an |now|online)|call (?:us|now)|"
    r"enquire|enquiry|inquire|request (?:a )?(?:quote|call|demo)|schedule|shop now|buy now|order now|sign up|"
    r"get in touch|whatsapp us|chat with us|free consultation)\b", re.I)
TECH = [
    ("WordPress", r"wp-content/|wp-includes/|generator[^>]+wordpress"), ("WooCommerce", r"woocommerce"),
    ("Shopify", r"cdn\.shopify\.com|Shopify\.theme|myshopify\.com"), ("Wix", r"static\.wixstatic\.com|generator[^>]+wix"),
    ("Webflow", r"data-wf-page|webflow\.js|website-files\.com"), ("Squarespace", r"static1\.squarespace|squarespace\.com"),
    ("Next.js", r"__NEXT_DATA__|/_next/static/"), ("Elementor", r"elementor"),
    ("Google Analytics", r"googletagmanager\.com/gtag|google-analytics\.com"),
    ("Google Tag Manager", r"googletagmanager\.com/gtm\.js"), ("Meta Pixel", r"connect\.facebook\.net/[^\"']+/fbevents\.js"),
]
COPYRIGHT_RE = re.compile(r"(?:©|\(c\)|copyright)\s*(?:[^0-9\n]{0,30}?)((?:19|20)\d{2})(?:\s*[-–—]\s*((?:19|20)\d{2}))?", re.I)


def fact(key, value, statement, evidence):
    return {"key": key, "value": value, "statement": statement, "evidence": str(evidence or "")[:300]}


def _attrs(tag):
    return {m.group(1).lower(): m.group(3) if m.group(3) is not None else (m.group(4) or "")
            for m in re.finditer(r'([\w:-]+)\s*(?:=\s*(?:(["\'])(.*?)\2|([^\s>]+)))?', tag[1:])}


def analyse_html(html, final_url):
    """Pure analysis of the homepage HTML (no network)."""
    p = parse_html(html)
    facts = []
    title = re.sub(r"\s+", " ", p.title).strip()
    facts.append(fact("title", title or None, f'The homepage title is "{title}".' if title else "The homepage has no title tag.",
                      f"<title>{title}</title>" if title else "no <title> element"))
    desc = p.meta.get("description", "")
    facts.append(fact("meta_description", desc or None,
                      f'The homepage meta description is "{desc[:160]}".' if desc else "The homepage has no meta description.",
                      f'<meta name="description" content="{desc[:200]}">' if desc else "no <meta name=description>"))
    vp = p.meta.get("viewport")
    facts.append(fact("viewport", bool(vp), "The homepage sets a mobile viewport meta tag." if vp else
                      "The homepage has no mobile viewport meta tag.", f'viewport="{vp}"' if vp else "no <meta name=viewport>"))
    h1 = [h["text"] for h in p.headings if h["level"] == "h1"]
    facts.append(fact("h1_count", len(h1), f"The homepage has {len(h1)} H1 heading{'s' if len(h1) != 1 else ''}.",
                      "; ".join(f"<h1>{h[:60]}</h1>" for h in h1[:3]) or "no <h1>"))

    forms = re.findall(r"<form\b.*?</form>", html, re.I | re.S)
    contact_forms = [f for f in forms if re.search(r"<textarea|type=[\"']?email|name=[\"'][^\"']*(email|phone|mobile)", f, re.I)]
    facts.append(fact("contact_form", bool(contact_forms), "The homepage has a contact form." if contact_forms else
                      "The homepage has no contact form.", f"{len(contact_forms)} form(s) with email/phone/message fields"
                      if contact_forms else f"{len(forms)} <form> element(s), none with email/phone/message fields"))
    hrefs = [l["href"].strip() for l in p.links]
    tel = [h for h in hrefs if h.lower().startswith("tel:")]
    wa = [h for h in hrefs if re.search(r"wa\.me/|api\.whatsapp\.com|whatsapp://", h, re.I)]
    facts.append(fact("click_to_call", bool(tel), "The homepage has a click-to-call phone link." if tel else
                      "The homepage has no click-to-call (tel:) link.", tel[0] if tel else "no tel: links"))
    facts.append(fact("whatsapp_link", bool(wa), "The homepage has a WhatsApp chat link." if wa else
                      "The homepage has no WhatsApp link.", wa[0] if wa else "no wa.me / api.whatsapp.com links"))
    ctas = list(dict.fromkeys(l["text"] for l in p.links if l["text"] and len(l["text"]) <= 60 and CTA_RE.search(l["text"])))
    ctas += [t for t in re.findall(r"<button\b[^>]*>(.*?)</button>", html, re.I | re.S)
             if CTA_RE.search(re.sub(r"<[^>]+>", " ", t)) and t not in ctas]
    ctas = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in ctas]
    facts.append(fact("cta", bool(ctas), f'The homepage has a call-to-action button ("{ctas[0]}").' if ctas else
                      'The homepage has no clear call-to-action button such as "Get a quote" or "Book now".',
                      "; ".join(ctas[:4]) or "no button/link text matching quote/contact/book/call/shop"))
    imgs = [_attrs(t) for t in re.findall(r"<img\b[^>]*>", html, re.I)]
    no_alt = [i for i in imgs if "alt" not in i]
    facts.append(fact("images_missing_alt", len(no_alt), f"{len(no_alt)} of {len(imgs)} images on the homepage have no alt attribute.",
                      ", ".join(i.get("src", "")[:60] for i in no_alt[:3]) or f"{len(imgs)} images, all with alt"))
    techs = [name for name, rx in TECH if re.search(rx, html, re.I)]
    gen = p.meta.get("generator", "")
    if techs or gen:
        facts.append(fact("tech", techs, ("The site appears to be built with " + ", ".join(techs) + ".") if techs else
                          f'The site reports generator "{gen}".', (f'generator="{gen}"; ' if gen else "") + "markers: " + ", ".join(techs)))
    years = [(max(int(m.group(1)), int(m.group(2) or 0)), m.group(0)) for m in COPYRIGHT_RE.finditer(p.text)]
    if years:
        y, ev = max(years)
        facts.append(fact("copyright_year", y, f"The footer copyright year is {y}.", ev.strip()))
    scripts = len(re.findall(r"<script\b[^>]*\bsrc=", html, re.I))
    css = len(re.findall(r"<link\b[^>]*rel=[\"']?stylesheet", html, re.I))
    facts.append(fact("resources", {"scripts": scripts, "stylesheets": css, "images": len(imgs)},
                      f"The homepage loads {scripts} external scripts, {css} stylesheets and {len(imgs)} images.",
                      f"<script src> x{scripts}, <link rel=stylesheet> x{css}, <img> x{len(imgs)}"))
    return facts


def internal_links(html, base_url, limit=20):
    p = parse_html(html)
    host = (urlparse(base_url).hostname or "").lower().removeprefix("www.")
    out = []
    for l in p.links:
        h = l["href"].strip()
        if not h or h.startswith(("#", "mailto:", "tel:", "javascript:", "whatsapp:")):
            continue
        u = urldefrag(urljoin(base_url, h))[0]
        pu = urlparse(u)
        if pu.scheme not in ("http", "https") or (pu.hostname or "").lower().removeprefix("www.") != host:
            continue
        if re.search(r"\.(pdf|jpe?g|png|gif|svg|webp|zip|mp4|mp3)$", pu.path, re.I) or u.rstrip("/") == base_url.rstrip("/") or u in out:
            continue
        out.append(u)
        if len(out) >= limit:
            break
    return out


class Robots:
    def __init__(self, base, fetch=fetch_url):
        self.rp = robotparser.RobotFileParser()
        r = fetch(base.rstrip("/") + "/robots.txt", timeout=8)
        if r.get("status") in (401, 403):
            self.rp.disallow_all = True
            self.ok = True
        elif r.get("html") and (r.get("status") or 0) < 400:
            self.rp.parse(r["html"].splitlines())
            self.ok = True
        else:
            self.ok = False   # no robots.txt = everything allowed

    def allowed(self, url):
        return True if not self.ok else self.rp.can_fetch(USER_AGENT, url)


PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def pagespeed(url, strategy="mobile", call=api_json):
    """Google PageSpeed Insights (free; PAGESPEED_API_KEY optional, raises the quota): lab score, LCP, CLS, TBT, and the
    Chrome UX Report verdict from real users when Google has it. Facts are Google's numbers, quoted as Google's."""
    params = {"url": url, "strategy": strategy, "category": "performance"}
    key = secret("PAGESPEED_API_KEY")
    if key:
        params["key"] = key
    status, d = call("GET", PSI, params=params, timeout=90, retries=1)
    if status >= 400 or not isinstance(d, dict) or "lighthouseResult" not in d:
        msg = ((d or {}).get("error") or {}).get("message") if isinstance(d, dict) else None
        raise ApiError(status, f"PageSpeed Insights HTTP {status}" + (f": {msg}" if msg else ""))
    lr = d["lighthouseResult"]
    audits = lr.get("audits") or {}
    when = (lr.get("fetchTime") or "")[:10]
    ev = f"Google PageSpeed Insights, {strategy}, {when}"
    facts = []
    score = (((lr.get("categories") or {}).get("performance") or {}).get("score"))
    if score is not None:
        sc = round(score * 100)
        facts.append(fact("pagespeed_score", sc, f"Google PageSpeed Insights gives the homepage a {strategy} performance score of {sc}/100.",
                          ev))
    lcp = (audits.get("largest-contentful-paint") or {}).get("numericValue")
    if lcp is not None:
        facts.append(fact("pagespeed_lcp_ms", round(lcp), f"In Google's {strategy} test the largest element took {lcp / 1000:.1f} s to "
                          "appear (Google's 'good' threshold is 2.5 s).", ev))
    cls = (audits.get("cumulative-layout-shift") or {}).get("numericValue")
    if cls is not None and cls > 0.1:
        facts.append(fact("pagespeed_cls", round(cls, 2), f"Google measured a layout shift score of {cls:.2f} on {strategy} (good is "
                          "under 0.1): the page jumps while loading.", ev))
    tbt = (audits.get("total-blocking-time") or {}).get("numericValue")
    if tbt is not None and tbt > 600:
        facts.append(fact("pagespeed_tbt_ms", round(tbt), f"Google measured {tbt / 1000:.1f} s of total blocking time on {strategy} "
                          "(good is under 0.2 s).", ev))
    crux = (d.get("loadingExperience") or {}).get("overall_category")
    if crux in ("SLOW", "AVERAGE", "FAST"):
        facts.append(fact("crux_overall", crux, f"Real Chrome users' loading experience for the page is rated {crux} in Google's "
                          "Chrome UX Report.", ev + " (CrUX field data)"))
    return facts


def audit(url, check_links=True, fetch=fetch_url, with_pagespeed=False, call=api_json):
    url = normalize_url(url)
    pu = urlparse(url)
    if not pu.hostname or "." not in pu.hostname:
        raise ValueError(f"not a website URL: {url}")
    base = f"{pu.scheme}://{pu.netloc}"
    robots = Robots(base, fetch)
    if not robots.allowed(url):
        return {"url": url, "facts": [], "note": "robots.txt disallows fetching this page; nothing audited."}
    t0 = time.monotonic()
    r = fetch(url, timeout=15)
    ms = int((time.monotonic() - t0) * 1000)
    facts = []
    status = r.get("status")
    facts.append(fact("http_status", status, f"The homepage returned HTTP {status}." if status else "The homepage could not be reached.",
                      f"GET {url} -> {status or r.get('error')}"))
    if not r.get("html") or (status or 0) >= 400:
        return {"url": url, "final_url": r.get("final_url"), "audited_at": _now(), "facts": facts,
                "note": "Homepage unavailable — only that fact is reported."}
    final = r.get("final_url") or url
    https = final.lower().startswith("https://")
    facts.append(fact("https", https, "The site loads over HTTPS." if https else "The site does not load over HTTPS.", f"final URL {final}"))
    plain = fetch(f"http://{urlparse(final).hostname}/", timeout=10)
    if plain.get("final_url"):
        red = str(plain["final_url"]).lower().startswith("https://")
        facts.append(fact("http_redirects_to_https", red, "The http:// version redirects to HTTPS." if red else
                          "The http:// version does not redirect to HTTPS.", f"http://{urlparse(final).hostname}/ -> {plain['final_url']}"))
    facts.append(fact("response_time_ms", ms, f"The homepage HTML took {ms / 1000:.1f} seconds to download in our test.", f"{ms} ms"))
    size = len(r["html"].encode("utf-8"))
    facts.append(fact("html_kb", round(size / 1024, 1), f"The homepage HTML document is {size / 1024:.0f} KB.",
                      f"{size} bytes (HTML only, excluding images/scripts)"))
    facts.extend(analyse_html(r["html"], final))
    if check_links:
        broken, checked, skipped = [], 0, 0
        for u in internal_links(r["html"], final):
            if not robots.allowed(u):
                skipped += 1
                continue
            lr = fetch(u, timeout=10)
            if not lr.get("status"):
                # No HTTP answer (timeout, TLS failure on this machine, reset): not proof the link is broken.
                skipped += 1
                continue
            checked += 1
            if lr["status"] >= 400:
                broken.append(f"{u} -> {lr['status']}")
        facts.append(fact("broken_internal_links", len(broken),
                          f"{len(broken)} of the first {checked} internal links on the homepage return an error." if broken
                          else f"All {checked} internal links we checked on the homepage load.",
                          ("; ".join(broken[:5]) or f"{checked} links checked, none 4xx/5xx")
                          + (f"; {skipped} skipped (robots or no HTTP answer)" if skipped else "")))
    if with_pagespeed:
        try:
            facts.extend(pagespeed(final, call=call))
        except ApiError as exc:
            pagespeed_error = str(exc)
        else:
            pagespeed_error = None
    # Certificate problems are NOT reported as facts: verification also fails when the auditing
    # machine lacks CA certificates, so it can't be stated about the prospect with certainty.
    out = {"url": url, "final_url": final, "audited_at": _now(), "facts": facts}
    if with_pagespeed and pagespeed_error:
        out["pagespeed_error"] = pagespeed_error
    return out


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fact-only website audit (facts + evidence, no opinions).")
    ap.add_argument("--url", required=True)
    ap.add_argument("--no-links", action="store_true", help="skip checking internal links")
    ap.add_argument("--save", help="also write the JSON to this file")
    ap.add_argument("--pagespeed", action="store_true", help="add Google PageSpeed Insights facts (mobile score, LCP, CLS, real-user data)")
    a = ap.parse_args(argv)
    try:
        out = audit(a.url, check_links=not a.no_links, with_pagespeed=a.pagespeed)
    except ValueError as exc:
        emit({"ok": False, "error": str(exc)}, 2)
    if a.save:
        Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        Path(a.save).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        out["saved"] = a.save
    emit({"ok": True, "data": out})


if __name__ == "__main__":
    main()

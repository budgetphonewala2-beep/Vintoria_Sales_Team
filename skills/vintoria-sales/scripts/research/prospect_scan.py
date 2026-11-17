#!/usr/bin/env python3
"""
Deep prospect scan: everything the internet says about one prospect, in one run, saved as a dossier that
every email is written from (and claim-checked against).

Runs, in order (each step is optional and never fatal):
  1. their post (if they asked publicly): the exact quote, plus any email/phone/site written in it
  2. site_audit.py      — fact-only homepage audit (mobile, HTTPS, CTA, forms, speed, broken links, copyright...) plus
                          Google PageSpeed Insights (mobile score, LCP, CLS, real-user CrUX verdict; skip with --no-pagespeed)
  3. analyze_prospect.py — company name, description, industry, tech, pricing, hiring, socials, size signals
  4. contact_finder.py  — team / leadership with seniority and buying role
  5. find_email.py      — best address for the decision maker; skipped when the post or site already has one
  6. lead_sources.py research — reviews, complaints, news, LinkedIn, founder, social, directories, hiring, ads
     (needs APIFY_TOKEN or BRIGHTDATA_API_KEY; skip with --no-web)
Then ranks the strongest outreach hooks (facts, never guesses), writes prospects/<slug>/DOSSIER.json + DOSSIER.md
and records the prospect, contact and files in the pipeline.

Usage:
    python prospect_scan.py https://acme.com [--name "Acme"] [--first Priya --last Mehta]
        [--post-text "..." | --post-file post.txt] [--post-url <url>] [--city Pune] [--source hunt:li-web]
        [--no-web] [--no-api] [--no-links]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
import analyze_prospect  # noqa: E402
import contact_finder  # noqa: E402
import find_email  # noqa: E402
import lead_sources  # noqa: E402
import pipeline  # noqa: E402
import site_audit  # noqa: E402
from sales_common import domain_slug, emit, normalize_url  # noqa: E402

THIS_YEAR = datetime.now(timezone.utc).year

# fact key → (test on the value, weight, angle). The angle is a suggestion for the user, not a claim.
HOOKS = [
    ("pagespeed_score", lambda v: v is not None and v < 50, 5, "Google itself scores their mobile speed low — offer speed work (most of their buyers are on phones)"),
    ("pagespeed_lcp_ms", lambda v: (v or 0) > 4000, 4, "Main content takes 4 s+ to appear on mobile in Google's test — visitors leave"),
    ("crux_overall", lambda v: v == "SLOW", 4, "Real Chrome users rate the site SLOW (Google's own field data)"),
    ("pagespeed_cls", lambda v: (v or 0) > 0.25, 2, "The page jumps around while loading on mobile — fixable"),
    ("http_status", lambda v: v is not None and v >= 400, 5, "Site returns an error — offer a quick fix/rebuild"),
    ("https", lambda v: v is False, 4, "No HTTPS — browsers show 'Not secure'; offer SSL + trust fixes"),
    ("viewport", lambda v: v is False, 4, "Not mobile-friendly — most visitors are on phones; offer a mobile fix"),
    ("broken_internal_links", lambda v: (v or 0) > 0, 3, "Broken links on the homepage — offer a quick clean-up"),
    ("cta", lambda v: v is False, 3, "No clear call-to-action — offer a conversion-focused homepage"),
    ("contact_form", lambda v: v is False, 2, "No contact form on the homepage — enquiries are being lost"),
    ("click_to_call", lambda v: v is False, 2, "No tap-to-call link — easy win for mobile enquiries"),
    ("whatsapp_link", lambda v: v is False, 1, "No chat/WhatsApp button — an easy extra enquiry channel"),
    ("copyright_year", lambda v: isinstance(v, int) and v < THIS_YEAR - 1, 2, "Old footer year — site looks unmaintained"),
    ("response_time_ms", lambda v: (v or 0) > 3000, 2, "Slow first load — offer speed optimisation"),
    ("meta_description", lambda v: not v, 1, "No meta description — weak Google snippet; SEO quick win"),
    ("title", lambda v: not v, 2, "No page title — invisible in Google results; SEO quick win"),
    ("h1_count", lambda v: v == 0, 1, "No H1 heading — basic on-page SEO gap"),
    ("images_missing_alt", lambda v: (v or 0) >= 3, 1, "Images without alt text — SEO + accessibility gap"),
]


def rank_hooks(facts, post=None, research=None):
    by = {f["key"]: f for f in facts}
    hooks = []
    if post:
        hooks.append({"weight": 10, "key": "their_post", "observation": f'They posted: "{post[:220]}"',
                      "angle": "Answer exactly what they asked for — this is the strongest opener", "evidence": "their post"})
    for key, test, w, angle in HOOKS:
        f = by.get(key)
        if f is not None:
            try:
                hit = test(f["value"])
            except TypeError:
                hit = False
            if hit:
                hooks.append({"weight": w, "key": key, "observation": f["statement"], "angle": angle, "evidence": f["evidence"]})
    for sec, w, angle in (("news", 3, "Congratulate on the news, connect it to their next need"),
                          ("hiring", 3, "They're hiring for this role — offer to cover it faster/cheaper"),
                          ("reviews", 2, "Reference their reviews (good: build on them; few: offer review growth)"),
                          ("complaints", 2, "Public complaints mention their site/service — handle with care")):
        for x in ((research or {}).get("sections") or {}).get(sec, [])[:1]:
            hooks.append({"weight": w, "key": f"web_{sec}", "observation": f"{x['title']}: {x['snippet']}"[:300],
                          "angle": angle + " (open the page and confirm first)", "evidence": x["url"]})
    return sorted(hooks, key=lambda h: -h["weight"])


def decision_maker(people, first=None, last=None):
    if first:
        return {"name": f"{first} {last or ''}".strip(), "first": first, "last": last or "", "title": None, "source": "given"}
    for p in people or []:
        if p.get("seniority") in ("C-Suite", "VP", "Director") or "Economic Buyer" in str(p.get("buying_role")):
            parts = p["name"].split()
            return {"name": p["name"], "first": parts[0], "last": parts[-1] if len(parts) > 1 else "", "title": p.get("title"),
                    "linkedin": p.get("linkedin"), "source": "website"}
    if people:
        parts = people[0]["name"].split()
        return {"name": people[0]["name"], "first": parts[0], "last": parts[-1] if len(parts) > 1 else "",
                "title": people[0].get("title"), "source": "website"}
    return None


def scan(url, name=None, first=None, last=None, post=None, post_url=None, city=None, web=True, use_api=True, links=True,
         out_dir=None, record=True, source=None, pagespeed=True):
    url = normalize_url(url)
    if pipeline.platform_of_url(url):
        raise ValueError(f"{url} is a post/profile on a platform, not the prospect's website — pass their own site "
                         "(or use find_email.py --text '<post>' when they have none)")
    slug = domain_slug(url)
    folder = Path(out_dir or Path("prospects") / slug)
    folder.mkdir(parents=True, exist_ok=True)
    d = {"slug": slug, "url": url, "scanned_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
         "steps": {}, "errors": []}

    def step(label, fn):
        try:
            r = fn()
            d["steps"][label] = "ok"
            return r
        except Exception as exc:  # noqa: BLE001 - one failing source must not stop the scan
            d["steps"][label] = f"failed: {type(exc).__name__}: {exc}"[:200]
            d["errors"].append(d["steps"][label])
            return None

    if post:
        d["post"] = {"text": post[:3000], "url": post_url, "contacts": {k: v for k, v in find_email.from_text(post).items() if v}}
    audit = step("site_audit", lambda: site_audit.audit(url, check_links=links, with_pagespeed=pagespeed)) or {"facts": []}
    company = step("analyze", lambda: analyze_prospect.analyze(url)) or {}
    team = step("contacts", lambda: contact_finder.find_contacts(url)) or {}
    people = team.get("contacts") or []
    dm = decision_maker(people, first, last)
    em = step("email", lambda: find_email.find(slug, (dm or {}).get("first", ""), (dm or {}).get("last", ""), post or "", use_api))
    research = None
    if web:
        research = step("web_research", lambda: lead_sources.research(slug, name or company.get("company_name"), city, folder))
    else:
        d["steps"]["web_research"] = "skipped (--no-web)"

    d["company"] = {k: company.get(k) for k in ("company_name", "description", "industry_signals", "tech_stack", "social_links",
                                                 "pricing_tiers", "has_job_postings", "company_size_signals", "contact_info")
                    if company.get(k)}
    d["company"]["name"] = name or company.get("company_name") or slug
    d["people"] = people[:10]
    d["decision_maker"] = dm
    d["email"] = None if not em else {"best": em.get("best"), "label": em.get("label"), "phone": em.get("phone"),
                                       "finders_skipped": em.get("finders_skipped"), "candidates": em.get("candidates")}
    d["audit_facts"] = audit.get("facts", [])
    d["web"] = None if not research else {k: research[k] for k in ("sections", "queries")}
    d["hooks"] = rank_hooks(d["audit_facts"], post, research)[:8]
    facts = list(d["audit_facts"])
    if post:
        facts.append({"key": "their_post", "value": True, "statement": post[:3000], "evidence": post_url or "their post"})
    if company.get("description"):
        facts.append({"key": "site_description", "value": True, "statement": company["description"], "evidence": url})
    for p in people[:10]:
        facts.append({"key": "person", "value": p["name"], "statement": f"{p['name']} — {p.get('title') or ''}", "evidence": p.get("source")})
    facts += (research or {}).get("facts", [])
    d["facts"] = facts                      # claim_check.py reads this list as evidence
    d["readiness"] = {
        "verified_email": bool(em and em.get("best") and em["best"]["status"] == "verified"),
        "hooks": len(d["hooks"]), "has_post": bool(post), "web_research": bool(research),
        "next": ("Write the first email from the top hook (vintoria-outreach)" if d["hooks"] and em and em.get("best") and
                 em["best"]["status"] == "verified" else
                 "Find a verified email (vintoria-prospect-research) or reach out where they posted" if d["hooks"] else
                 "Few hooks found — research manually or deprioritise"),
    }
    (folder / "DOSSIER.json").write_text(json.dumps(d, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (folder / "DOSSIER.md").write_text(render_md(d), encoding="utf-8")
    d["saved"] = [str(folder / "DOSSIER.json"), str(folder / "DOSSIER.md")]
    if record:
        step("pipeline", lambda: _record(d, source))
    return d


def _record(d, source=None):
    conn = pipeline.connect()
    try:
        nm = d["company"].get("name")
        pipeline.add(conn, url=d["url"], name=None if nm in (None, d["slug"]) else nm, source=source)   # never overwrite a real name with the slug
        found_something = bool(d["hooks"]) or bool(((d.get("email") or {}).get("best") or {}).get("email"))
        if pipeline.get(conn, d["slug"])["stage"] == "new" and found_something:   # an unreachable site isn't "researched"
            pipeline.set_stage(conn, d["slug"], "researched", "deep scan done")
        best = (d.get("email") or {}).get("best")
        dm = d.get("decision_maker")
        if dm or best:
            pipeline.add_contact(conn, d["slug"], (dm or {}).get("name") or (best or {}).get("email"), title=(dm or {}).get("title"),
                                 email=(best or {}).get("email"), email_status=(best or {}).get("status"),
                                 email_source=(best or {}).get("source"), linkedin=(dm or {}).get("linkedin"),
                                 phone=(d.get("email") or {}).get("phone"))
        for f in d["saved"]:
            with conn:
                conn.execute("INSERT OR REPLACE INTO artifacts(prospect_id, kind, path, created_at) VALUES (?,?,?,?)",
                             (pipeline.get(conn, d["slug"])["id"], "dossier", f, pipeline.now()))
    finally:
        conn.close()


def render_md(d):
    c = d["company"]
    L = [f"# Dossier — {c.get('name')}", "", f"{d['url']} · scanned {d['scanned_at']}", ""]
    if d.get("post"):
        L += ["## Their post", "", f"> {d['post']['text'][:600]}", "", f"Source: {d['post'].get('url') or 'pasted'}", ""]
    au = d.get("author") or {}
    if au.get("name") or au.get("profile"):
        pr = au.get("profile") or {}
        L += ["## Who wrote it", "", f"- {au.get('name') or pr.get('name')}" + (f" — {au.get('headline')}" if au.get("headline") else ""),
              f"- Company: {pr.get('company') or 'Not found'} · Location: {pr.get('location') or 'Not found'}",
              f"- Profile: {au.get('url') or pr.get('linkedin') or 'Not found'}" + (" (from a search snippet — confirm)" if pr.get("from") else "")]
        if pr.get("about"):
            L.append(f"- About (their words): {pr['about'][:400]}")
        wf = d.get("website_found") or {}
        L += [f"- Website: {wf.get('site') or 'Not found'} — {wf.get('how', '')}", ""]
    L += ["## Best hooks (facts → angle)", ""]
    for h in d["hooks"] or [{"observation": "None found", "angle": "", "weight": 0}]:
        L.append(f"- **{h['observation']}** — {h['angle']}" + (f" _(evidence: {h.get('evidence')})_" if h.get("evidence") else ""))
    L += ["", "## Company", ""]
    for k in ("description", "industry_signals", "tech_stack", "pricing_tiers", "has_job_postings", "social_links"):
        if c.get(k):
            L.append(f"- {k.replace('_', ' ')}: {c[k] if not isinstance(c[k], (list, dict)) else json.dumps(c[k], ensure_ascii=False)[:300]}")
    dm, em = d.get("decision_maker"), d.get("email") or {}
    best = em.get("best") or {}
    L += ["", "## Who to contact", "", f"- Decision maker: {dm['name'] + (' — ' + dm['title'] if dm.get('title') else '') if dm else 'Not found'}",
          f"- Email: {best.get('email', 'Not found')} ({em.get('label') or 'n/a'})" + (f" — {em['finders_skipped']}" if em.get("finders_skipped") else ""),
          f"- Phone/WhatsApp: {em.get('phone') or 'Not found'}"]
    if d["people"]:
        L += ["- Others: " + "; ".join(f"{p['name']} ({p.get('title') or '?'})" for p in d["people"][1:6])]
    L += ["", "## Website audit (facts)", ""] + [f"- {f['statement']}" for f in d["audit_facts"]]
    if d.get("web"):
        L += ["", "## On the web (search snippets — confirm before using)", ""]
        for sec, xs in d["web"]["sections"].items():
            for x in xs[:3]:
                L.append(f"- [{sec}] {x['title']} — {x['url']}")
    L += ["", "## Readiness", "", f"- {d['readiness']['next']}", ""]
    if d["errors"]:
        L += ["## Steps that failed", ""] + [f"- {e}" for e in d["errors"]] + [""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deep scan of one prospect → DOSSIER.json/.md + pipeline.")
    ap.add_argument("url")
    ap.add_argument("--name"); ap.add_argument("--first"); ap.add_argument("--last"); ap.add_argument("--city")
    g = ap.add_mutually_exclusive_group(); g.add_argument("--post-text"); g.add_argument("--post-file")
    ap.add_argument("--post-url"); ap.add_argument("--source")
    ap.add_argument("--no-web", action="store_true"); ap.add_argument("--no-api", action="store_true")
    ap.add_argument("--no-links", action="store_true"); ap.add_argument("--out-dir")
    ap.add_argument("--no-pagespeed", action="store_true", help="skip Google PageSpeed Insights (it adds ~20 s)")
    a = ap.parse_args(argv)
    post = Path(a.post_file).read_text(encoding="utf-8-sig") if a.post_file else a.post_text
    if pipeline.platform_of_url(a.url):
        emit({"ok": False, "error": f"{a.url} is a platform post/profile, not a website — pass the prospect's own site"}, 2)
    d = scan(a.url, a.name, a.first, a.last, post, a.post_url, a.city, not a.no_web, not a.no_api, not a.no_links, a.out_dir,
             source=a.source, pagespeed=not a.no_pagespeed)
    emit({"ok": True, "data": {k: d[k] for k in ("slug", "company", "decision_maker", "email", "hooks", "readiness", "steps",
                                                 "errors", "saved")}})


if __name__ == "__main__":
    main()

"""Tests for the helper scripts in skills/sales/scripts (no network: fetch and API calls are faked)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import claim_check  # noqa: E402
import contact_finder  # noqa: E402
import find_email  # noqa: E402
import intent_scan  # noqa: E402
import lead_scorer  # noqa: E402
import pipeline  # noqa: E402
import sales_common  # noqa: E402
import site_audit  # noqa: E402
import web_search  # noqa: E402


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    h = tmp_path / "sales home"           # space on purpose (Windows paths)
    monkeypatch.setenv("AI_SALES_HOME", str(h))
    for k in ("BRIGHTDATA_API_KEY", "HUNTER_API_KEY", "BRIGHTDATA_ZONE"):
        monkeypatch.delenv(k, raising=False)
    return h


def run(script, *args, stdin=None):
    r = subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True,
                       encoding="utf-8", input=stdin)
    return r.returncode, (json.loads(r.stdout) if r.stdout.strip().startswith(("{", "[")) else r.stdout)


# ---------------------------------------------------------------- pipeline

def test_pipeline_flow(tmp_path):
    conn = pipeline.connect(tmp_path / "p.db")
    assert pipeline.add(conn, "https://www.Acme.com/about", "Acme", "hunt:li-web", "web,seo")["created"]
    assert not pipeline.add(conn, "acme.com")["created"]           # same slug -> update, not duplicate
    pipeline.set_score(conn, "acme.com", 82, {"company_fit": 80})
    pipeline.set_stage(conn, "acme.com", "contacted", "email 1")
    pipeline.set_stage(conn, "acme.com", "replied", "interested")
    pipeline.add_contact(conn, "acme.com", "Priya Mehta", title="Founder", email="priya@acme.com", email_status="verified")
    pipeline.add_contact(conn, "acme.com", "Priya Mehta", phone="+91 98")              # merge, keeps email
    p = pipeline.show(conn, "acme.com")
    assert p["grade"] == "A" and p["contacts"][0]["email"] == "priya@acme.com" and p["contacts"][0]["phone"] == "+91 98"
    assert [h["to_stage"] for h in p["history"] if h["kind"] == "stage"] == ["new", "contacted", "replied"]
    rep = pipeline.report(conn)
    assert rep["conversion"]["reply_rate_pct"] == 100.0 and rep["by_source"]["hunt"]["prospects"] == 1
    pdf = pipeline.pdf_input(conn)
    assert pdf["prospects"][0]["company"] == "Acme" and pdf["prospects"][0]["component_scores"] == {"company_fit": 80}
    with pytest.raises(pipeline.UserError):
        pipeline.set_stage(conn, "acme.com", "flying")
    with pytest.raises(pipeline.UserError):
        pipeline.add_contact(conn, "acme.com", "X", email_status="probably")


def test_pipeline_cli(home):
    code, out = run("pipeline.py", "add", "--url", "bakery.in", "--name", "Bakery")
    assert code == 0 and out["data"]["prospect"]["slug"] == "bakery.in"
    assert (home / "pipeline.db").exists()
    code, out = run("pipeline.py", "next", "bakery.in", "Call Thursday", "--due", "2000-01-01")
    code, out = run("pipeline.py", "report", "--pdf-input", str(home / "pdf in.json"))
    assert out["data"]["due_today"][0]["prospect"] == "bakery.in" and (home / "pdf in.json").exists()
    code, out = run("pipeline.py", "show", "missing.com")
    assert code == 2 and out["ok"] is False


# ---------------------------------------------------------------- intent

@pytest.mark.parametrize("text,keep", [
    ("Need a website for my bakery in Pune, koi developer batao?", True),
    ("Can anyone recommend an SEO agency for a dental clinic?", True),
    ("Mujhe apne restaurant ke liye website banwani hai", True),
    ("We are hiring a full-time web developer, salary 6 LPA, apply now", False),
    ("#OpenToWork — I'm a web developer looking for opportunities", False),
    ("We build stunning websites starting at $299, DM for a discount!", False),
    ("Looking for a good biryani place in Hyderabad", False),
])
def test_intent_scoring(text, keep):
    assert intent_scan.score_text(text)["keep"] is keep


def test_intent_serp_and_dedupe(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    calls = []

    def fake(method, url, headers=None, body=None, **kw):
        calls.append((url, headers, body))
        return 200, {"organic": [{"link": "https://www.linkedin.com/posts/x_activity-1", "title": "Priya on LinkedIn",
                                  "description": "Looking for a web developer to build our clinic website"}]}
    res = intent_scan.serp("site:linkedin.com/posts web developer", 7, call=fake)
    assert calls[0][1]["Authorization"] == "Bearer bd_test_key_123"
    assert calls[0][2]["data_format"] == "parsed_light" and "tbs=qdr%3Aw" in calls[0][2]["url"]
    posts = [{"url": r["link"], "text": r["description"]} for r in res]
    assert len(intent_scan.scan(posts)["candidates"]) == 1
    assert intent_scan.scan(posts)["duplicates_skipped"] == 1          # seen in the earlier run
    assert intent_scan.google_url("q", 3).endswith("tbs=qdr%3Ad3&num=10&hl=en")


def test_intent_cli_file(tmp_path):
    f = tmp_path / "posts.jsonl"
    f.write_text('{"url": "https://reddit.com/r/a/comments/1", "text": "Need an app for my gym, any recommendations?"}\n'
                 "We are hiring interns, apply now\n", encoding="utf-8")
    code, out = run("intent_scan.py", "--file", str(f))
    assert code == 0 and len(out["data"]["candidates"]) == 1 and out["data"]["rejected"] == 1
    code, out = run("intent_scan.py", "--serp", "--query", "x")
    assert code == 4 and "BRIGHTDATA_API_KEY" in out["data"]["errors"][0]


# ---------------------------------------------------------------- claim check

def test_claim_check_flags_invented_numbers_and_placeholders():
    src = claim_check.load_sources(None, ["Looking for a web developer to redo our bakery website, budget 50k",
                                          "The homepage has no mobile viewport meta tag."])
    draft = ("Hi Anita,\n\nSaw your post about needing a web developer for your bakery website. Your homepage has no "
             "mobile viewport meta tag. We helped 47 bakeries double their orders. [ADD REAL CUSTOMER RESULT]\n\n"
             "Would a 15-minute call this week help?")
    r = claim_check.check(draft, src)
    assert not r["ok"] and [u["text"][:10] for u in r["unsupported"]] == ["We helped "]
    assert r["placeholders"] == ["[ADD REAL CUSTOMER RESULT]"] and r["supported"] == 3


def test_claim_check_quotes_audit_json_and_hinglish(tmp_path):
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps({"ok": True, "data": {"facts": [
        {"statement": "The footer copyright year is 2019.", "evidence": "© 2019 Sweet Crumbs"}]}}), encoding="utf-8")
    src = claim_check.load_sources([str(audit)], ["Need an app for my gym members", "bakery ke liye website banwani hai"])
    assert claim_check.check("Your footer still says 2019.", src)["ok"]
    assert not claim_check.check("Your footer still says 2018.", src)["ok"]
    assert claim_check.check('You wrote "an app for my gym members" in your post.', src)["ok"]
    assert not claim_check.check('You wrote "an app for my yoga studio" in your post.', src)["ok"]
    assert claim_check.check("Aapki post dekhi — bakery ke liye website banwani hai.", src)["ok"]
    code, out = run("claim_check.py", "--draft-text", "We have 200 clients.", "--evidence-text", "x")
    assert code == 1
    code, out = run("claim_check.py", "--draft-text", "x", "--evidence", str(tmp_path / "nope.md"))
    assert code == 2


# ---------------------------------------------------------------- site audit

HOME_HTML = """<html><head><title>Chai Cafe Pune</title><meta name="description" content="Best chai in Pune">
<meta name="generator" content="WordPress 6.4"><script src="/wp-includes/js/x.js"></script></head>
<body><h1>Welcome</h1><h1>Menu</h1><a href="/menu">Menu</a><a href="/old">Old</a><a href="/private/x">P</a>
<a href="https://other.com/">o</a><a href="tel:+919800000000">Call</a><img src="/a.jpg"><img src="/b.jpg" alt="cup">
<footer>© 2019 Chai Cafe</footer></body></html>"""


def fake_fetch(pages):
    def fetch(url, timeout=10):
        status, html = pages.get(url, (404, ""))
        final = url
        if isinstance(html, tuple):              # redirect
            final, html = html
        return {"url": url, "final_url": final, "status": status, "html": html or None, "error": None, "tls_error": False}
    return fetch


def test_site_audit_facts_robots_and_links():
    pages = {"https://chai.in/robots.txt": (200, "User-agent: *\nDisallow: /private/"),
             "https://chai.in/": (200, HOME_HTML), "http://chai.in/": (200, ("https://chai.in/", HOME_HTML)),
             "https://chai.in/menu": (200, "<p>menu</p>"), "https://chai.in/old": (404, "")}
    r = site_audit.audit("https://chai.in/", fetch=fake_fetch(pages))
    f = {x["key"]: x for x in r["facts"]}
    assert f["viewport"]["value"] is False and f["h1_count"]["value"] == 2 and f["click_to_call"]["value"] is True
    assert f["cta"]["value"] is False and f["images_missing_alt"]["value"] == 1 and "WordPress" in f["tech"]["value"]
    assert f["copyright_year"]["value"] == 2019 and f["http_redirects_to_https"]["value"] is True
    assert f["broken_internal_links"]["value"] == 1 and "skipped (robots" in f["broken_internal_links"]["evidence"]
    assert all(x["statement"] and x["evidence"] for x in r["facts"])
    assert "tls_certificate" not in f                                   # never claimed about the prospect


def test_site_audit_robots_blocks_and_errors():
    r = site_audit.audit("blocked.in", fetch=fake_fetch({"https://blocked.in/robots.txt": (200, "User-agent: *\nDisallow: /")}))
    assert r["facts"] == [] and "robots.txt" in r["note"]
    r = site_audit.audit("down.in", fetch=fake_fetch({}))
    assert [x["key"] for x in r["facts"]] == ["http_status"]
    with pytest.raises(ValueError):
        site_audit.audit("not a url")


# ---------------------------------------------------------------- find email

def test_find_email_site_then_hunter_verify(monkeypatch):
    monkeypatch.setenv("HUNTER_API_KEY", "hunter_test_key_1")
    site = {"https://acme.in/": "<a href='mailto:info@acme.in'>m</a>",
            "https://acme.in/contact": '<script type="application/ld+json">{"@type":"LocalBusiness","name":"Acme",'
                                       '"email":"priya@acme.in","telephone":"+91 22 5555 0101"}</script>'}
    monkeypatch.setattr(site_audit, "fetch_url", fake_fetch({"https://acme.in/robots.txt": (404, "")}))

    def fetch(urls):
        return [{"url": u, "final_url": u, "status": 200 if u in site else 404, "html": site.get(u)} for u in urls]
    calls = []

    def api(method, url, headers=None, params=None, **kw):
        calls.append((url, params, headers))
        if url.endswith("email-finder"):
            return 200, {"data": {"email": "priya@acme.in", "verification": {"status": "accept_all"}}}
        return 200, {"data": {"status": "valid", "score": 95}}
    r = find_email.find("acme.in", "Priya", "Mehta", "", True, fetch, api)
    by = {c["email"]: c["status"] for c in r["candidates"]}
    # priya@ is on their own site, so no finder credits are spent: it is only verified
    assert by == {"priya@acme.in": "verified", "info@acme.in": "unverified"} and "website" in r["finders_skipped"]
    assert r["best"]["email"] == "priya@acme.in" and r["label"] == "verified"
    assert not any(u.endswith("email-finder") for u, _, _ in calls)
    assert calls[0][2] == {"X-API-KEY": "hunter_test_key_1"} and "api_key" not in calls[0][0]
    assert any(s["step"] == "hunter_verifier" for s in r["steps"]) and r["phone"]
    # nobody personal on the site → the finder runs
    calls.clear()
    site.pop("https://acme.in/contact")
    r = find_email.find("acme.in", "Priya", "Mehta", "", True, fetch, api)
    assert any(u.endswith("email-finder") for u, _, _ in calls) and r["finders_skipped"] is None


def test_find_email_post_email_skips_finders(monkeypatch):
    monkeypatch.setenv("HUNTER_API_KEY", "hunter_test_key_1")
    monkeypatch.setattr(site_audit, "fetch_url", fake_fetch({}))
    calls = []

    def api(method, url, headers=None, params=None, **kw):
        calls.append(url)
        return 200, {"data": {"status": "valid", "score": 90}}
    r = find_email.find("", "Priya", "Mehta", "Need a website for Chai Cafe, mail me priya@chaicafe.in", True, lambda u: [], api)
    assert r["best"]["email"] == "priya@chaicafe.in" and r["best"]["source"] == "post" and r["best"]["status"] == "verified"
    assert "post" in r["finders_skipped"] and not any("email-finder" in u for u in calls)


def test_find_email_no_key_labels_guesses(monkeypatch):
    monkeypatch.setattr(site_audit, "fetch_url", fake_fetch({}))
    r = find_email.find("acme.in", "Priya", "Mehta", "", True, lambda urls: [], None)
    assert r["best"]["status"] == "pattern-guessed" and "verify before sending" in r["label"]
    t = find_email.from_text("Mail me at Priya.M@chaicafe.in or https://wa.me/919876543210, site chaicafe.in, see linkedin.com/in/p")
    assert t["emails"] == ["priya.m@chaicafe.in"] and t["whatsapp"] == ["+919876543210"] and t["websites"] == ["chaicafe.in"]
    assert find_email.clean_emails(["logo@2x.png", "noreply@x.com", "a@example.com", "ok@real.in"]) == ["ok@real.in"]


# ---------------------------------------------------------------- scorers, contacts, common

def test_lead_scorer_agency_and_bant(tmp_path):
    a = lead_scorer.score_agency(lead_scorer.EXAMPLE_AGENCY)
    assert a["lead_grade"] == "A" and sum(v["max"] for v in a["breakdown"].values()) == 100
    cold = lead_scorer.score_agency({"intent_confidence": 0.4})
    assert cold["lead_grade"] in ("C", "D") and "find_email.py" in cold["recommended_action"]
    f = tmp_path / "in.json"
    f.write_text("﻿" + json.dumps(lead_scorer.EXAMPLE), encoding="utf-8")   # BOM tolerated
    code, out = run("lead_scorer.py", str(f))
    assert code == 0 and out["lead_grade"] in ("A+", "A", "B", "C", "D")
    code, out = run("lead_scorer.py", stdin=json.dumps({"company": "Feff Inc"}))   # old lstrip('Feff') bug
    assert code == 0 and out["company"] == "Feff Inc"


@pytest.mark.parametrize("title,seniority", [("Director of Marketing", "Director"), ("Marketing Coordinator", "IC"),
                                             ("VP of Sales", "VP"), ("Chief Technology Officer", "C-Suite")])
def test_title_classifier_regressions(title, seniority):
    assert contact_finder.classify_seniority(title) == seniority


def test_secrets_redacted(home, monkeypatch):
    home.mkdir(parents=True, exist_ok=True)
    (home / ".env").write_text("# keys\nHUNTER_API_KEY=\"secret_from_env_file\"\n", encoding="utf-8")
    assert sales_common.secret("HUNTER_API_KEY") == "secret_from_env_file"
    assert "secret_from_env_file" not in sales_common.redact("url?key=secret_from_env_file")
    assert sales_common.domain_slug("https://www.Acme.com/about") == "acme.com"
    with pytest.raises(sales_common.ApiError):
        web_search.search("x")


def test_pdf_from_pipeline(tmp_path, home):
    pytest.importorskip("reportlab")
    run("pipeline.py", "add", "--url", "acme.com", "--name", "Acme")
    run("pipeline.py", "score", "acme.com", "77", "--breakdown", '{"company_fit": 80, "contact_access": 70}')
    inp = tmp_path / "in.json"
    run("pipeline.py", "report", "--pdf-input", str(inp))
    out = tmp_path / "r.pdf"
    r = subprocess.run([sys.executable, str(SCRIPTS / "generate_pdf_report.py"), str(inp), str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert out.read_bytes()[:4] == b"%PDF"

"""Tests for query_library.py, the new lead sources (Hacker News, Reddit JSON, Maps, Product Hunt, X, Facebook)
and prospect_scan.py. No network: every API call is faked."""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import analyze_prospect  # noqa: E402
import contact_finder  # noqa: E402
import find_email  # noqa: E402
import intent_scan  # noqa: E402
import lead_sources  # noqa: E402
import pipeline  # noqa: E402
import prospect_scan  # noqa: E402
import query_library as ql  # noqa: E402
import site_audit  # noqa: E402

KEYS = ["APIFY_TOKEN", "BRIGHTDATA_API_KEY", "PRODUCTHUNT_TOKEN", "HUNTER_API_KEY", "PROSPEO_API_KEY", "FINDYMAIL_API_KEY",
        "APOLLO_API_KEY", "MILLIONVERIFIER_API_KEY", "ZEROBOUNCE_API_KEY", "NEVERBOUNCE_API_KEY"]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


# ------------------------------------------------------------------ query library

def test_every_linkedin_query_fits_harvestapi_limits():
    for loc in (None, "Pune", "New York"):
        qs = ql.linkedin(ql.SERVICES, True, loc)
        assert len(qs) >= 30
        for q in qs:
            assert ql.valid_linkedin(q), q
            assert ql.op_count(q) <= 5 and len(q) <= 500
            assert " NOT " not in q or q.index(" NOT ") > q.rfind(" AND ")      # NOT always last


def test_queries_pair_asking_with_service_and_exclude_sellers():
    x = ql.google_xray(["seo"], "Pune")
    li = next(q for q in x if q["id"] == "li-posts-seo")["query"]
    assert li.startswith("site:linkedin.com/posts") and '"looking for"' in li and '"SEO agency"' in li and '"Pune"' in li
    assert '-"for hire"' in li and '-"open to work"' in li
    assert {q["platform"] for q in x} >= {"linkedin", "reddit", "x", "facebook", "quora", "indiehackers", "upwork", "signal"}
    assert ql.reddit(["web"])[0] == {"subreddit": "forhire", "query": 'flair:Hiring ("web developer" OR "website developer")'}
    assert any('"looking for a freelancer"' == q for q in ql.hackernews(["web"]))
    assert "dentist in Pune" in ql.maps(["web"], "Pune")
    assert all("-filter:retweets" in q for q in ql.x_search(["app"]))


def test_new_intent_phrases():
    assert intent_scan.score_text("[Hiring] Need a freelancer to build a WordPress website, will pay $500")["keep"]
    assert not intent_scan.score_text("[For Hire] I build WordPress websites, DM me for my portfolio")["keep"]
    assert intent_scan.platform_of("https://news.ycombinator.com/item?id=1") == "hackernews"
    assert intent_scan.platform_of("https://www.upwork.com/freelance-jobs/apply/x") == "upwork"


def test_contact_in_post_is_attached():
    out = intent_scan.scan([{"url": "u1", "text": "Looking for a web developer for my clinic website, email dr.rao@raoclinic.in"}])
    assert out["candidates"][0]["contact_in_post"]["emails"] == ["dr.rao@raoclinic.in"]


# ------------------------------------------------------------------ sources

def test_hackernews_asks_and_seeking_freelancer_thread():
    calls = []

    def call(method, url, params=None, **kw):
        calls.append((url, params))
        if params.get("tags") == "story,author_whoishiring":
            return 200, {"hits": [{"objectID": "999"}]}
        if params.get("tags") == "comment,story_999":
            return 200, {"hits": [
                {"objectID": "1", "parent_id": 999, "author": "acme", "created_at": "2026-11-01",
                 "comment_text": "SEEKING FREELANCER | Remote<p>Need a web developer to rebuild our Shopify store. Email jobs@acme.io"},
                {"objectID": "2", "parent_id": 999, "author": "dev", "comment_text": "SEEKING WORK | React developer"},
                {"objectID": "3", "parent_id": 1, "author": "x", "comment_text": "SEEKING FREELANCER reply in a sub-thread"}]}
        return 200, {"hits": [{"objectID": "5", "author": "bob", "comment_text": "Can anyone recommend an agency? Looking for a web developer.",
                               "story_title": "Ask HN", "created_at": "2026-10-30"}]}
    posts = lead_sources.hackernews(['"looking for a web developer"'], call=call)
    assert calls[0][0].endswith("/search_by_date") and "created_at_i>" in calls[0][1]["numericFilters"]
    assert [p["url"].split("=")[1] for p in posts] == ["5", "1"]
    out = lead_sources.finish(posts, [])
    assert {c["url"].split("=")[1] for c in out["candidates"]} == {"1", "5"}
    seeker = next(c for c in out["candidates"] if c["url"].endswith("=1"))
    assert seeker["contact_in_post"]["emails"] == ["jobs@acme.io"]


def test_reddit_public_json_fallback_and_block_message():
    def call(method, url, params=None, **kw):
        assert url == "https://www.reddit.com/r/forhire/search.json" and params["restrict_sr"] == 1 and params["t"] == "week"
        return 200, {"data": {"children": [{"data": {"permalink": "/r/forhire/comments/abc/hiring_web_dev/",
                                                      "title": "[Hiring] Web developer for a bakery website",
                                                      "selftext": "Need someone to build a website, budget $400", "author": "baker",
                                                      "created_utc": 1793500000, "link_flair_text": "Hiring"}}]}}
    posts = lead_sources.reddit([{"subreddit": "forhire", "query": "flair:Hiring website"}], call=call)
    assert posts[0]["url"].startswith("https://www.reddit.com/r/forhire/") and posts[0]["flair"] == "Hiring"
    with pytest.raises(lead_sources.UserError):
        lead_sources.reddit([{"subreddit": "x", "query": "y"}], call=lambda *a, **k: (429, {}))


def test_maps_need_signals_and_add_to_pipeline(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    items = [{"title": "Smile Dental", "website": "", "phone": "+91 98100 00001", "totalScore": 4.6, "reviewsCount": 12,
              "categoryName": "Dentist", "url": "https://maps.google.com/?cid=1", "searchString": "dentist in Pune"},
             {"title": "Big Dental", "website": "https://bigdental.in", "totalScore": 4.8, "reviewsCount": 900},
             {"title": "Insta Cafe", "website": "https://instagram.com/instacafe", "totalScore": 3.7, "reviewsCount": 40},
             {"title": "Closed Co", "permanentlyClosed": True}]

    def call(method, url, body=None, **kw):
        assert "compass~crawler-google-places" in url and body["searchStringsArray"] == ["dentist in Pune"]
        return 201, items
    cs = lead_sources.maps(["dentist in Pune"], call=call)
    assert [c["name"] for c in cs][:2] == ["Smile Dental", "Insta Cafe"] and len(cs) == 3
    assert "no website on Google Maps" in cs[0]["signals"] and cs[-1]["signals"] == []
    added = lead_sources.add_companies([c for c in cs if c["signals"]], "maps")
    assert len(added) == 2
    conn = pipeline.connect()
    p = pipeline.show(conn, added[0]["prospect"])
    assert p["source"] == "maps:dentist in Pune" and p["contacts"][0]["phone"] == "+91 98100 00001"
    assert any("no website" in (h["text"] or "") for h in p["history"])
    conn.close()


def test_producthunt_launches(monkeypatch):
    with pytest.raises(lead_sources.UserError):
        lead_sources.producthunt()
    monkeypatch.setenv("PRODUCTHUNT_TOKEN", "ph_test_token_1")

    def call(method, url, headers=None, body=None, **kw):
        assert url == lead_sources.PH_API and headers == {"Authorization": "Bearer ph_test_token_1"} and "postedAfter" in body["query"]
        return 200, {"data": {"posts": {"edges": [{"node": {"name": "Tiny CRM", "tagline": "CRM for clinics", "website": "https://tinycrm.io",
                                                            "votesCount": 12, "makers": [{"name": "[REDACTED]"}],
                                                            "topics": {"edges": [{"node": {"name": "SaaS"}}]}}}]}}}
    cs = lead_sources.producthunt(call=call)
    assert cs[0]["name"] == "Tiny CRM" and cs[0]["makers"] == [] and cs[0]["topics"] == ["SaaS"]
    assert any("upvotes" in s for s in cs[0]["signals"])


def test_x_and_facebook_actor_inputs(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    seen = {}

    def call(method, url, body=None, **kw):
        seen[url.split("/acts/")[1].split("/")[0]] = body
        return 201, [{"text": "Looking for a web developer for my startup website", "url": "https://x.com/a/status/1",
                      "author": {"userName": "founder_a"}}]
    xs = lead_sources.x_posts(["q"], 10, call=call)
    assert xs[0]["author"] == "founder_a" and xs[0]["platform"] == "x"
    assert seen["apidojo~tweet-scraper"]["searchTerms"] == ["q"]
    lead_sources.facebook(["https://www.facebook.com/groups/123"], 5, call=call)
    assert seen["apify~facebook-groups-scraper"]["startUrls"] == [{"url": "https://www.facebook.com/groups/123"}]
    with pytest.raises(lead_sources.UserError):
        lead_sources.facebook([])


def test_linkedin_rejects_overlong_boolean(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    with pytest.raises(lead_sources.UserError):
        lead_sources.linkedin(["a OR b OR c OR d OR e OR f OR g"], call=lambda *a, **k: (201, []))


# ------------------------------------------------------------------ deep scan

HOME = """<html><head><title>Rao Clinic</title></head><body><h1>Rao Clinic</h1>
<p>Family dental care in Pune since 2009.</p><footer>© 2018 Rao Clinic</footer></body></html>"""


def test_prospect_scan_dossier_hooks_and_pipeline(monkeypatch, tmp_path):
    def fake_fetch(u, timeout=10):
        ok = u.rstrip("/").endswith("raoclinic.in")
        return {"url": u, "final_url": u, "status": 200 if ok else 404, "html": HOME if ok else None, "error": None, "tls_error": False}
    monkeypatch.setattr(site_audit, "fetch_url", fake_fetch)
    real_audit = site_audit.audit
    monkeypatch.setattr(site_audit, "audit", lambda url, check_links=True, **kw: real_audit(url, check_links, fetch=fake_fetch))
    monkeypatch.setattr(analyze_prospect, "analyze", lambda url, timeout=10: {"company_name": "Rao Clinic",
                                                                          "description": "Family dental care in Pune"})
    monkeypatch.setattr(contact_finder, "find_contacts", lambda url, timeout=10: {"contacts": [
        {"name": "Asha Kulkarni", "title": "Receptionist", "seniority": "IC", "buying_role": "User"},
        {"name": "Dr Vikram Rao", "title": "Founder", "seniority": "C-Suite", "buying_role": "Economic Buyer"}]})
    called = {}
    real_find = find_email.find

    def fake_find(domain, first, last, text, use_api):
        called["args"] = (domain, first, last, text)
        return real_find(domain, first, last, text, False, lambda urls: [], None)
    monkeypatch.setattr(find_email, "find", fake_find)
    post = "Looking for someone to redo our clinic website, mail me at vikram@raoclinic.in"
    d = prospect_scan.scan("raoclinic.in", post=post, post_url="https://linkedin.com/posts/x", web=False, links=False,
                           source="hunt:li-web")
    assert called["args"][:3] == ("raoclinic.in", "Dr", "Rao")              # decision maker picked, not the receptionist
    assert d["email"]["best"]["email"] == "vikram@raoclinic.in" and "post" in d["email"]["finders_skipped"]
    keys = [h["key"] for h in d["hooks"]]
    assert keys[0] == "their_post" and "viewport" in keys and "copyright_year" in keys and "cta" in keys
    saved = json.loads(Path(d["saved"][0]).read_text(encoding="utf-8"))
    assert any(f["key"] == "their_post" for f in saved["facts"]) and "## Best hooks" in Path(d["saved"][1]).read_text(encoding="utf-8")
    conn = pipeline.connect()
    p = pipeline.show(conn, "raoclinic.in")
    assert p["stage"] == "researched" and p["source"] == "hunt:li-web"
    assert p["contacts"][0]["email"] == "vikram@raoclinic.in" and {a["kind"] for a in p["artifacts"]} == {"dossier"}
    conn.close()
    import claim_check
    cc = claim_check.check("I saw you're looking for someone to redo your clinic website.",
                           claim_check.load_sources([d["saved"][0]], []))
    assert cc["ok"], cc


def test_prospect_scan_survives_failing_steps(monkeypatch):
    def boom(*a, **k):
        raise OSError("network down")
    monkeypatch.setattr(site_audit, "audit", boom)
    monkeypatch.setattr(analyze_prospect, "analyze", boom)
    monkeypatch.setattr(contact_finder, "find_contacts", boom)
    monkeypatch.setattr(find_email, "find", boom)
    d = prospect_scan.scan("down.in", web=False, record=False)
    assert len(d["errors"]) == 4 and d["hooks"] == [] and "Few hooks" in d["readiness"]["next"]

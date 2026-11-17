"""Tests for seller_profile.py, profile-driven queries, Apollo / Leads Finder / LinkedIn people sources,
excluded-market filtering and verify-only email checks. No network."""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "vintoria-sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import find_email  # noqa: E402
import lead_sources  # noqa: E402
import pipeline  # noqa: E402
import query_library as ql  # noqa: E402
import seller_profile as sp  # noqa: E402

PROFILE = {
    "seller": {"name": "Ravi Sharma", "company": "Pixelcraft", "email": "ravi@pixelcraft.io", "timezone": "Asia/Kolkata",
               "postal_address": "12 MG Road, Pune", "website": "pixelcraft.io"},
    "offer": {"services": ["ecommerce", "web"], "service_details": "Shopify stores for DTC brands",
              "niches": ["DTC skincare", "specialty coffee", "dental clinics"], "platforms": ["Shopify"],
              "outcomes": ["faster store", "higher conversion"], "deal_size": {"min": 2000, "typical": 6000, "currency": "USD"}},
    "targets": {"countries": ["USA", "UK", "AU"], "buyer_titles": ["Founder", "CEO", "Head of Ecommerce"], "company_size": "1-50",
                "exclude_countries": ["India"], "cities": ["Austin", "London"]},
    "proof": {"case_studies": [{"client": "Brew Co", "result": "conversion 1.8% to 2.6%"}]},
    "positioning": {"differentiators": ["Shopify Partner"]},
    "signals": {"pains": ["store is slow", "low conversion", "theme looks dated"], "triggers": ["product launch", "rebrand"],
                "tools_they_leave": ["Wix", "Squarespace"]},
}
KEYS = ["APIFY_TOKEN", "MILLIONVERIFIER_API_KEY", "ZEROBOUNCE_API_KEY", "NEVERBOUNCE_API_KEY", "HUNTER_API_KEY"]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


def write_profile(data=PROFILE):
    Path(sp.FILE).write_text(json.dumps(data), encoding="utf-8")


# ------------------------------------------------------------------ profile

def test_profile_check_asks_the_missing_questions_and_set_saves():
    assert sp.check(None)["exists"] is False and sp.check(None)["ask"]
    Path(sp.FILE).write_text(json.dumps(sp.TEMPLATE), encoding="utf-8")
    c = sp.check(sp.load())
    assert c["complete_pct"] < 20 and "offer.niches" in c["missing_required"]
    assert any("niches" in q for q in c["ask"])
    prof = sp.set_field(sp.load(), "offer.niches", '["DTC skincare"]')
    sp.save(prof)
    assert sp.load()["offer"]["niches"] == ["DTC skincare"]
    write_profile()
    assert sp.check(sp.load())["next"] == "Ready."
    bad = json.loads(json.dumps(PROFILE)); bad["offer"]["services"] = ["websites"]
    write_profile(bad)
    assert sp.check(sp.load())["problems"]


def test_profile_defaults_are_international_english():
    t = sp.TEMPLATE["targets"]
    assert t["countries"] == ["US", "UK", "CA", "AU"] and t["languages"] == ["en"] and "India" in t["exclude_countries"]


# ------------------------------------------------------------------ profile-driven queries

def test_profile_queries_are_niche_pain_trigger_switch_and_valid():
    q = ql.from_profile(PROFILE)
    li = q["linkedin"]
    assert all(ql.valid_linkedin(x) for x in li) and len(li) >= 10
    assert li[0] == '"looking for" AND ("Shopify developer" OR "Shopify expert") AND "DTC skincare" NOT India'
    joined = " | ".join(li)
    assert '"store is slow"' in joined and '"product launch"' in joined and '"moving from Wix"' in joined
    assert not any(h.strip('"') in joined for s in ql.HINGLISH.values() for h in s)          # English only
    assert q["countries"] == ["US", "UK", "AU"] and q["google_countries"] == ["us", "gb", "au"]
    assert all("-India" in x["query"] for x in q["google_xray"] if x["platform"] != "signal")
    assert "india" in q["exclude_markers"] and "mumbai" in q["exclude_markers"]
    subs = [r["subreddit"] for r in q["reddit"]]
    assert "Dentistry" in subs and "roasters" in subs and subs.index("Dentistry") < subs.index("forhire")
    assert q["maps"] == ["dental clinics in Austin", "dental clinics in London"]


def test_apollo_url_and_people_filters_from_profile():
    q = ql.from_profile(PROFILE)
    url = q["apollo_urls"][0]["url"]
    assert url.startswith("https://app.apollo.io/#/people?")
    for part in ("personTitles[]=Founder", "personLocations[]=United%20States", "personLocations[]=United%20Kingdom",
                 "organizationNumEmployeesRanges[]=1%2C10", "qOrganizationKeywordTags[]=DTC%20skincare",
                 "contactEmailStatusV2[]=verified"):
        assert part in url, part
    assert q["linkedin_people"][0] == {"searchQuery": "DTC skincare", "locations": ["United States", "United Kingdom", "Australia"],
                                       "currentJobTitles": ["Founder", "CEO", "Head of Ecommerce"]}
    assert q["leads_finder"]["contact_job_title"][0] == "Founder" and q["leads_finder"]["email_status"] == ["validated"]


def test_auto_uses_profile_only_without_explicit_services():
    assert ql.auto()["profile_used"] is False
    write_profile()
    assert ql.auto()["profile_used"] is True
    assert ql.auto(["seo"])["profile_used"] is False


# ------------------------------------------------------------------ people databases

APOLLO_ITEMS = [
    {"first_name": "Jane", "last_name": "Doe", "title": "Founder", "email": "jane@glowskin.com", "email_status": "verified",
     "linkedin_url": "https://linkedin.com/in/jane", "organization": {"name": "Glow Skin", "website_url": "https://glowskin.com"},
     "city": "Austin"},
    {"name": "Raj K", "title": "CEO", "organization_name": "Desi Brew", "organization_website_url": "https://desibrew.in",
     "location": "Mumbai, Maharashtra, India"},
    {"first_name": "Jane", "last_name": "Doe", "email": "jane@glowskin.com", "organization": {"name": "Glow Skin"}},
]


def test_apollo_actor_input_normalize_dedupe_and_exclude(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    seen = {}

    def call(method, url, body=None, **kw):
        seen["url"], seen["body"] = url, body
        return 201, APOLLO_ITEMS
    rows = lead_sources.apollo(["https://app.apollo.io/#/people?personTitles[]=Founder"], 50, call=call)
    assert "code_crafter~apollo-scraper" in seen["url"] and seen["body"]["url"].startswith("https://app.apollo.io")
    assert seen["body"]["totalRecords"] == 50
    assert rows[0]["name"] == "Jane Doe" and rows[0]["company"] == "Glow Skin" and rows[0]["website"] == "https://glowskin.com"
    kept, dropped = lead_sources.dedupe_people(rows, ql.excluded_markers(PROFILE))
    assert [r["name"] for r in kept] == ["Jane Doe"] and dropped == 1
    with pytest.raises(lead_sources.UserError):
        lead_sources.apollo(["https://example.com/search"], call=call)


def test_people_and_leads_inputs(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    got = {}

    def call(method, url, body=None, **kw):
        got[url.split("/acts/")[1].split("/")[0]] = body
        return 201, [{"firstName": "Tom", "lastName": "Lee", "headline": "Founder at Bean Co", "linkedinUrl": "https://linkedin.com/in/tom",
                      "currentPosition": [{"companyName": "Bean Co"}], "location": {"linkedinText": "Seattle, Washington"}}]
    q = ql.from_profile(PROFILE)
    rows = lead_sources.people(q["linkedin_people"][:1], 25, call=call)
    assert got["harvestapi~linkedin-profile-search"]["searchQuery"] == "DTC skincare"
    assert got["harvestapi~linkedin-profile-search"]["maxItems"] == 25
    assert rows[0]["company"] == "Bean Co" and rows[0]["title"] == "Founder at Bean Co" and rows[0]["location"] == "Seattle, Washington"
    lead_sources.leads_finder(q["leads_finder"], 40, call=call)
    assert got["code_crafter~leads-finder"]["fetch_count"] == 40 and got["code_crafter~leads-finder"]["contact_job_title"]
    lead_sources.employees(["https://www.linkedin.com/company/beanco"], ["Founder"], None, 5, call=call)
    assert got["harvestapi~linkedin-company-employees"]["companies"] == ["https://www.linkedin.com/company/beanco"]


def test_add_people_verifies_emails(monkeypatch):
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "zb_test_key_1")
    rows = [lead_sources.normalize_person(APOLLO_ITEMS[0], "apollo")]
    added = lead_sources.add_people(rows, "apollo", verify=True, call=lambda *a, **k: (200, {"status": "valid"}))
    assert added == [{"prospect": "glowskin.com", "person": "Jane Doe", "email": "jane@glowskin.com", "email_status": "verified"}]
    conn = pipeline.connect()
    c = pipeline.contacts(conn, pipeline.get(conn, "glowskin.com")["id"])[0]
    assert c["email_status"] == "verified" and c["email_source"] == "apollo"
    conn.close()


def test_verify_only_without_keys_stays_unverified():
    r = find_email.verify_only("jane@glowskin.com")
    assert r["status"] == "unverified" and "no verifier key" in r["note"]


# ------------------------------------------------------------------ excluded markets in intent leads

def test_finish_drops_excluded_market_posts():
    write_profile()
    posts = [{"url": "a", "text": "Looking for a Shopify developer for our skincare brand in Austin, budget $5k"},
             {"url": "b", "text": "Looking for a Shopify developer for my store in Mumbai, budget 50k INR"}]
    out = lead_sources.finish(posts, [])
    assert [c["url"] for c in out["candidates"]] == ["a"] and out["excluded_market"] == 1
    assert out["excluded_examples"][0]["marker"] == "mumbai"

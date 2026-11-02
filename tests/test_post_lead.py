"""A buyer's post → their profile, their real company site (never guessed), the deep scan, and premium-email checks."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "sales" / "scripts"))

import email_lint  # noqa: E402
import post_lead  # noqa: E402

POST = "Relaunching our Shopify store before Black Friday and need a developer who knows Klaviyo. Recommendations?"


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)


def fake_scan(seen):
    def scan(site, **kw):
        seen.update(site=site, **kw)
        f = Path("prospects") / site
        f.mkdir(parents=True, exist_ok=True)
        d = {"slug": site, "url": "https://" + site, "scanned_at": "now", "company": {"name": kw.get("name") or site}, "hooks": [],
             "audit_facts": [], "people": [], "facts": [], "readiness": {"next": "write"}, "errors": []}
        (f / "DOSSIER.json").write_text(json.dumps(d))
        return d
    return scan


def test_headline_and_domain_rules():
    assert post_lead.company_from_headline("Founder at Glow Skin | DTC skincare") == "Glow Skin"
    assert post_lead.company_from_headline("CEO | Brew Co") == "Brew Co"
    assert post_lead.company_from_headline("Helping brands grow") is None
    assert post_lead.domain_matches("glowskin.com", "Glow Skin") and not post_lead.domain_matches("glowup.io", "Glow Skin")
    assert not post_lead.is_company_site("crunchbase.com") and not post_lead.is_company_site("gmail.com")


def test_profile_gives_company_site_and_person_facts(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test")
    item = {"fullName": "Jane Doe", "headline": "Founder at Glow Skin", "location": {"linkedinText": "Austin, Texas"},
            "experience": [{"companyName": "Glow Skin", "companyWebsite": "https://glowskin.com"}], "about": "Clean skincare from Austin."}
    seen = {}
    r = post_lead.lead("https://www.linkedin.com/posts/jane-doe_1", POST, "Jane Doe", "https://www.linkedin.com/in/jane-doe",
                       call=lambda *a, **k: (201, [item]), scan=fake_scan(seen))
    assert r["website"]["site"] == "glowskin.com" and "LinkedIn profile" in r["website"]["how"]
    assert (seen["first"], seen["last"], seen["post"]) == ("Jane", "Doe", POST)
    d = json.loads(Path("prospects/glowskin.com/DOSSIER.json").read_text())
    assert {f["key"] for f in d["facts"]} >= {"person_profile", "person_company", "person_about"}
    assert "## Who wrote it" in Path("prospects/glowskin.com/DOSSIER.md").read_text()


def test_site_in_the_post_wins_and_search_needs_a_name_match(monkeypatch):
    seen = {}
    r = post_lead.lead("https://www.reddit.com/r/shopify/comments/abc/x", "Need a Shopify dev, email mark@brewco.com", "Mark",
                       web=False, use_api=False, scan=fake_scan(seen))
    assert r["website"]["site"] == "brewco.com" and r["website"]["how"] == "written in their post"
    rows = [{"url": "https://www.crunchbase.com/organization/glow-skin"}, {"url": "https://glowup.io"}, {"url": "https://glowskin.com/"}]
    monkeypatch.setattr(post_lead.lead_sources, "google", lambda qs, **k: rows)
    assert post_lead.find_company_site("Glow Skin")["site"] == "glowskin.com"
    monkeypatch.setattr(post_lead.lead_sources, "google", lambda qs, **k: rows[:2])
    assert post_lead.find_company_site("Glow Skin") is None          # nothing matches the name: not guessed


def test_no_site_builds_a_post_dossier_and_says_what_to_do():
    r = post_lead.lead("https://www.reddit.com/r/shopify/comments/abd/x", "Need a Shopify dev, DM me", "Sam Lee",
                       web=False, use_api=False, scan=fake_scan({}))
    assert r["slug"] == "sam-lee@reddit" and r["website"]["site"] is None and "never guessed" in r["website"]["how"]
    assert "reply" in r["readiness"]["next"]
    d = json.loads(Path("prospects/sam-lee@reddit/DOSSIER.json").read_text())
    assert d["facts"][0]["key"] == "their_post"


def test_premium_checks_specific_first_lines_short_sentences_and_no_repeats(tmp_path):
    f = Path("prospects/glowskin.com")
    f.mkdir(parents=True)
    (f / "DOSSIER.json").write_text(json.dumps({"company": {"name": "Glow Skin"}, "post": {"text": POST},
                                                "hooks": [{"observation": "Homepage took 4.2 seconds to download"}]}))
    terms = email_lint.dossier_terms("glowskin.com")
    generic = ("Hi Jane,\n\nNoticed your store and wanted to share an idea.\nWe build Shopify stores for DTC brands and rebuilt "
               "Brew Co's in 4 weeks.\n\nWorth a look?\n\nRavi")
    specific = ("Hi Jane,\n\nSaw you're relaunching the Glow Skin store before Black Friday and want Klaviyo help.\nWe build Shopify "
                "stores for DTC brands and rebuilt Brew Co's in 4 weeks.\n\nWorth a look?\n\nRavi")
    g, s = email_lint.lint(generic, "glow skin relaunch", 1, terms=terms), email_lint.lint(specific, "glow skin relaunch", 1, terms=terms)
    assert any("could go to anyone" in i for i in g["issues"]) and s["score"] > g["score"]
    long = "Hi Jane,\n\n" + " ".join(["word"] * 32) + ".\n\nWorth a look?"
    assert any("word sentence" in i for i in email_lint.lint(long, "x y", 2)["issues"])
    fu = "Your homepage took 4.2 seconds to download in my test, here is one fix idea for the hero image. Worth sending?"
    r = email_lint.lint(fu, None, 3, previous=[fu])
    assert any("repeats email 1" in i for i in r["issues"])


def test_hunt_file_only_processes_the_buyers_you_kept(monkeypatch):
    Path("hunt.json").write_text(json.dumps({"candidates": [
        {"url": "https://www.reddit.com/r/a/comments/1/x", "text": "Need a Shopify dev, email ann@annco.com", "author": "Ann", "age_hours": 5},
        {"url": "https://www.reddit.com/r/a/comments/2/x", "text": "I'm a Shopify dev for hire", "author": "Bob", "age_hours": 1}]}))
    seen = {}
    out = post_lead.from_hunt("hunt.json", only={"https://www.reddit.com/r/a/comments/1/x"}, web=False, use_api=False, scan=fake_scan(seen))
    assert len(out) == 1 and out[0]["website"]["site"] == "annco.com"

"""Every place an agent could invent facts, and the guard that stops it (see skills/sales/references/truth-rules.md).
Each adversarial sentence below passed the v3.8 claim checker; each must now be blocked, while true sentences pass."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import claim_check  # noqa: E402
import find_email  # noqa: E402
import lead_sources  # noqa: E402
import outreach  # noqa: E402
import pipeline  # noqa: E402

FIX = ROOT / "skills" / "sales-outreach" / "evals" / "glowskin-sequence-from-dossier" / "files"


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    (tmp_path / "SELLER-PROFILE.json").write_text((FIX / "SELLER-PROFILE.json").read_text())
    (tmp_path / "prospects" / "glowskin.com").mkdir(parents=True)
    for f in ("DOSSIER.json", "DOSSIER.md"):
        (tmp_path / "prospects" / "glowskin.com" / f).write_text((FIX / "prospects" / "glowskin.com" / f).read_text())


def src():
    return claim_check.load_sources([], [], slug="glowskin.com")


@pytest.mark.parametrize("sentence,why", [
    ("Your competitors are already doing this better than you.", ""),
    ("Your homepage sets a mobile viewport meta tag.", "contradicts"),
    ("We recently rebuilt the store for Sephora on Shopify.", "sephora"),
    ("Your homepage runs on WordPress and Elementor.", "wordpress"),
    ("WordPress powers your site.", "wordpress"),
    ("Most of your visitors shop on their phones.", ""),
    ("We guarantee you'll double your sales before Black Friday.", "guarantee"),
    ("We specialise in skincare brands like yours.", ""),
    ("Your customers are frustrated with checkout.", ""),
    ("Your homepage took 9.8 seconds to download in my test.", "9"),
    ('You wrote "we need it done by Christmas" in your post.', "quoted"),
    ("We rebuilt the Brew Co store in 4 weeks and doubled their revenue.", "part of this sentence"),
    ("Your homepage took 4.2 seconds to download and your customers hate it.", "part of this sentence"),
    ("I think your checkout is losing you thousands every month.", ""),
    ("Worth fixing, since Google penalises slow stores.", "google"),
    ("Saw your post about relaunching before Black Friday, and congrats on the new funding.", "part of this sentence"),
])
def test_invented_claims_are_blocked(sentence, why):
    r = claim_check.check(sentence, src())
    assert not r["ok"], sentence
    assert why.lower() in r["unsupported"][0]["why"].lower()


@pytest.mark.parametrize("sentence", [
    "Your homepage took 4.2 seconds to download in my test.",
    "Your homepage doesn't set a mobile viewport meta tag.",
    "We rebuilt the Brew Co store in 4 weeks.",
    "Saw your post: you're relaunching the Glow Skin store before Black Friday.",
    "Your homepage took 4.2 seconds to download, so phone visitors may wait even longer.",
    "Happy to send the exact fix if useful.",
    "Worth a quick call this week?",
    "Ravi Sharma\n12 MG Road, Pune 411001, India",
    "We rebuilt the Brew Co store in 4 weeks, and checkout conversion went from 1.8% to 2.6%.",
    "Coffee, not skincare, but the same DTC Shopify setup you're relaunching.",
    "Our Shopify rebuilds start at 2000 USD and typically run 6000 USD, with delivery in 4-6 weeks.",
])
def test_true_and_harmless_sentences_pass(sentence):
    r = claim_check.check(sentence, src())
    assert r["ok"], (sentence, r["unsupported"])


def test_agent_written_documents_are_never_evidence():
    d = Path("prospects/glowskin.com")
    (d / "COMPANY-RESEARCH.md").write_text("Glow Skin raised a $2M seed round from Sequoia in 2025.")
    (d / "DECISION-MAKERS.md").write_text("Mark Chen is the CMO of Glow Skin.")
    s = claim_check.load_sources([str(d / "*.md")], [], slug="glowskin.com")
    assert not claim_check.check("Congrats on the $2M seed round from Sequoia.", s)["ok"]
    assert not claim_check.check("Mark Chen runs marketing at Glow Skin.", s)["ok"]
    assert any("COMPANY-RESEARCH" in x for x in claim_check.SKIPPED)


def test_search_snippets_alone_never_prove_a_claim_but_saved_pages_do(tmp_path):
    d = Path("prospects/glowskin.com")
    (d / "WEB-RESEARCH.json").write_text(json.dumps({"facts": [
        {"key": "web_news", "statement": "Glow Skin raises $3M to expand into Canada", "evidence": "https://news.example.com/glow"}]}))
    r = claim_check.check("Congrats on raising $3M to expand into Canada.", claim_check.load_sources([], [], slug="glowskin.com"))
    assert not r["ok"] and "search snippet" in r["unsupported"][0]["why"]
    (d / "sources").mkdir()
    (d / "sources" / "news-example-com-glow.txt").write_text(
        "URL: https://news.example.com/glow\nFETCHED: 2026-11-02\n\nGlow Skin raises $3M to expand into Canada, the founder said.")
    r = claim_check.check("Congrats on raising $3M to expand into Canada.", claim_check.load_sources([], [], slug="glowskin.com"))
    assert r["ok"] and r["claims"][0]["tier"] == "page"


def test_prospect_replies_are_evidence():
    c = pipeline.connect()
    pipeline.add(c, url="https://glowskin.com", name="Glow Skin")
    import reply_triage
    reply_triage.apply(c, "glowskin.com", reply_triage.classify("Thanks Ravi. We're based in Austin and want to launch in January."))
    c.close()
    assert claim_check.check("You mentioned you want to launch in January.", src())["ok"]
    assert not claim_check.check("You mentioned you want to launch in March.", src())["ok"]


def test_research_results_about_another_company_are_not_evidence(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    qs = lead_sources.research_queries("glowskin.com", "Glow Skin")

    def call(method, url, body=None, **kw):
        return 201, [{"searchQuery": {"term": qs["news"]}, "organicResults": [
            {"title": "Glow Skin wins award", "url": "https://press.com/a", "description": "Glow Skin (glowskin.com) won..."},
            {"title": "GlowUp Labs raises $5M", "url": "https://tech.com/b", "description": "GlowUp Labs, a cosmetics startup"}]}]
    r = lead_sources.research("glowskin.com", "Glow Skin", call=call)
    flags = {x["title"]: x["about_prospect"] for x in r["sections"]["news"]}
    assert flags == {"Glow Skin wins award": True, "GlowUp Labs raises $5M": False}
    assert [f["evidence"] for f in r["facts"]] == ["https://press.com/a"]


def test_an_agent_cannot_mark_an_email_verified_by_typing_it(monkeypatch):
    monkeypatch.delenv("AI_SALES_TRUST_VERIFIED", raising=False)
    c = pipeline.connect()
    pipeline.add(c, url="https://glowskin.com")
    r = pipeline.add_contact(c, "glowskin.com", "Jane Doe", email="jane@glowskin.com", email_status="verified")
    assert r["contacts"][0]["email_status"] == "unverified" and "no verification on record" in r["warnings"][0]
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "zb_test_key_1")
    find_email.verify_only("jane@glowskin.com", call=lambda *a, **k: (200, {"status": "valid"}))
    r = pipeline.add_contact(c, "glowskin.com", "Jane Doe", email="jane@glowskin.com", email_status="verified")
    assert r["contacts"][0]["email_status"] == "verified" and "warnings" not in r
    c.close()


def test_quotes_must_be_word_for_word():
    c = pipeline.connect()
    post = "We're relaunching our store before Black Friday and looking for a Shopify developer. Recommendations?"
    with pytest.raises(pipeline.UserError):
        pipeline.add(c, url="https://www.linkedin.com/posts/jane_1", name="Jane", quote="need a Shopify expert urgently", post=post)
    with pytest.raises(pipeline.UserError):
        pipeline.add(c, url="https://www.linkedin.com/posts/jane_1", name="Jane", quote="looking for a Shopify developer")
    r = pipeline.add(c, url="https://www.linkedin.com/posts/jane_1", name="Jane", quote="Looking for a  Shopify developer", post=post)
    notes = [h["text"] for h in pipeline.show(c, r["prospect"]["slug"])["history"] if h["kind"] == "note"]
    assert "verified verbatim" in notes[0]
    c.close()


def test_wrong_name_in_greeting_is_caught():
    c = pipeline.connect()
    pipeline.add(c, url="https://glowskin.com")
    pipeline.add_contact(c, "glowskin.com", "Jane Doe", email="jane@glowskin.com", email_status="verified")
    body = "Hi Jessica,\n\nYour homepage took 4.2 seconds to download in my test.\n\nNot relevant? Reply 'no' and I won't follow up."
    probs, _ = outreach.preflight(c, "glowskin.com", "jane@glowskin.com", "glow skin", body)
    assert any("wrong name" in p for p in probs)
    probs, _ = outreach.preflight(c, "glowskin.com", "jane@glowskin.com", "glow skin", body.replace("Jessica", "Jane"))
    assert not any("wrong name" in p for p in probs)
    c.close()


def test_fetch_page_save_writes_evidence_with_url_and_time(tmp_path, monkeypatch):
    import fetch_page
    import site_audit
    html = "<html><head><title>Glow Skin</title></head><body><p>Glow Skin raises $3M.</p></body></html>"
    monkeypatch.setattr(fetch_page, "fetch_many", lambda urls: [{"url": u, "final_url": u, "status": 200, "html": html} for u in urls])
    monkeypatch.setattr(site_audit.Robots, "allowed", lambda self, u: True)
    with pytest.raises(SystemExit):
        fetch_page.main(["https://news.example.com/glow", "--save", "prospects/glowskin.com/sources"])
    f = next(Path("prospects/glowskin.com/sources").glob("*.txt"))
    t = f.read_text()
    assert t.startswith("URL: https://news.example.com/glow\nFETCHED: ") and "raises $3M" in t

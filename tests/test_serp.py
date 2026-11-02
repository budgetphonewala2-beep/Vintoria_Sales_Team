"""Tests for serp.py (SERP lead engine across providers) and the scorer's unknown-input handling. No network."""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lead_scorer  # noqa: E402
import lead_sources  # noqa: E402
import serp  # noqa: E402

KEYS = ["SERPER_API_KEY", "SERPAPI_API_KEY", "BRIGHTDATA_API_KEY", "BRAVE_API_KEY", "APIFY_TOKEN", "SERP_PROVIDERS"]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


def test_no_key_is_a_clear_error():
    with pytest.raises(serp.UserError):
        serp.search("q")
    assert serp.configured() == []


def test_serper_request_shape_recency_and_pages(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "serper_test_key")
    calls = []

    def call(method, url, headers=None, body=None, params=None, **kw):
        calls.append((method, url, headers, body))
        organic = [{"link": f"https://www.reddit.com/r/forhire/comments/{body['page']}{i}/x/", "title": "[Hiring] web dev",
                    "snippet": "Looking for a web developer"} for i in range(10 if body["page"] == 1 else 3)]
        return 200, {"organic": organic}
    rows, prov, errs = serp.search('site:reddit.com "looking for" "web developer"', days=7, country="gb", pages=3, call=call)
    assert prov == "serper" and len(rows) == 13 and len(calls) == 2                 # stopped after the short page
    m, url, h, b = calls[0]
    assert m == "POST" and url == "https://google.serper.dev/search" and h == {"X-API-KEY": "serper_test_key"}
    assert b["tbs"] == "qdr:w" and b["gl"] == "gb" and b["page"] == 1
    assert rows[0]["platform"] == "reddit" and rows[0]["provider"] == "serper"


def test_falls_through_to_the_next_provider(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "serper_test_key")
    monkeypatch.setenv("SERPAPI_API_KEY", "serpapi_test_key")

    def call(method, url, params=None, **kw):
        if "serper.dev" in url:
            return 403, {"message": "Unauthorized"}
        assert params["engine"] == "google" and params["tbs"] == "qdr:m" and params["api_key"] == "serpapi_test_key"
        return 200, {"organic_results": [{"link": "https://www.linkedin.com/posts/x_1", "title": "t", "snippet": "s"}]}
    rows, prov, errs = serp.search("q", days=30, call=call)
    assert prov == "serpapi" and len(rows) == 1 and "serper" in errs[0]


def test_brave_and_order_setting(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "brave_test_key")
    monkeypatch.setenv("SERPER_API_KEY", "serper_test_key")
    monkeypatch.setenv("SERP_PROVIDERS", "brave,serper")

    def call(method, url, headers=None, params=None, **kw):
        assert "brave.com" in url and headers == {"X-Subscription-Token": "brave_test_key"} and params["freshness"] == "pw"
        return 200, {"web": {"results": [{"url": "https://www.quora.com/q", "title": "t", "description": "d"}]}}
    rows, prov, _ = serp.search("q", days=7, call=call)
    assert prov == "brave" and rows[0]["platform"] == "quora"


def test_hunt_runs_profile_queries_across_countries_and_scores(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "serper_test_key")
    Path("SELLER-PROFILE.json").write_text(json.dumps({
        "offer": {"services": ["ecommerce"], "niches": ["DTC skincare"], "platforms": ["Shopify"]},
        "targets": {"countries": ["US", "UK"], "exclude_countries": ["India"]}}))
    seen = []

    def call(method, url, body=None, **kw):
        seen.append(body)
        if len(seen) == 1:
            return 200, {"organic": [
                {"link": "https://www.linkedin.com/posts/a_1", "title": "Need help", "snippet": "Looking for a Shopify developer for our skincare brand"},
                {"link": "https://www.linkedin.com/posts/b_2", "title": "Agency", "snippet": "We build Shopify stores starting at $499, DM me"},
                {"link": "https://www.linkedin.com/posts/c_3", "title": "Help", "snippet": "Looking for a Shopify developer in Mumbai, budget 50k INR"}]}
        return 200, {"organic": []}
    posts, errors, meta = serp.hunt(days=7, pages=1, max_queries=4, call=call)
    assert meta["queries_run"] == 4 and {b["gl"] for b in seen} == {"us", "gb"}
    assert all("-India" in b["q"] for b in seen)
    out = lead_sources.finish(posts, errors)
    assert [c["url"] for c in out["candidates"]] == ["https://www.linkedin.com/posts/a_1"] and out["excluded_market"] == 1


def test_scorer_treats_unknown_age_and_comments_as_neutral():
    unknown = lead_scorer.score_agency({"intent_confidence": 0.9, "urgency": "high"})["breakdown"]
    known = lead_scorer.score_agency({"intent_confidence": 0.9, "urgency": "high", "posted_days_ago": 0, "comments": 0})["breakdown"]
    assert unknown["freshness"]["score"] == 7 and unknown["low_competition"]["score"] == 5
    assert known["freshness"]["score"] == 15 and known["low_competition"]["score"] == 10

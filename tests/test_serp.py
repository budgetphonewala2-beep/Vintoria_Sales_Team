"""Tests for serp.py — Bright Data SERP, freshness (hours, exact post times, newest first), watch mode — and the
scorer's unknown-input handling. No network."""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "vintoria-sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lead_scorer  # noqa: E402
import lead_sources  # noqa: E402
import pipeline  # noqa: E402
import serp  # noqa: E402

KEYS = ["SERPER_API_KEY", "SERPAPI_API_KEY", "BRIGHTDATA_API_KEY", "BRIGHTDATA_ZONE", "BRAVE_API_KEY", "APIFY_TOKEN", "SERP_PROVIDERS"]
NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


def li_url(dt, handle="jane-doe"):
    """A LinkedIn post URL whose activity id encodes dt (id = ms << 22)."""
    return f"https://www.linkedin.com/posts/{handle}_need-a-shopify-dev-activity-{int(dt.timestamp() * 1000) << 22}-AbCd"


def test_brightdata_is_the_default_and_other_keys_are_ignored(monkeypatch):
    monkeypatch.setenv("SERPER_API_KEY", "serper_test_key")
    assert serp.configured() == []                          # Serper key alone does nothing by default
    with pytest.raises(serp.UserError):
        serp.search("q")
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    assert [n for n, _ in serp.configured()] == ["brightdata"]
    monkeypatch.setenv("SERP_PROVIDERS", "brightdata,serper")   # opt-in only
    assert [n for n, _ in serp.configured()] == ["brightdata", "serper"]


def test_brightdata_request_hours_sort_by_date_and_pages(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    monkeypatch.setenv("BRIGHTDATA_ZONE", "my_serp_zone")
    calls = []

    def call(method, url, headers=None, body=None, **kw):
        calls.append(body)
        n = 10 if len(calls) == 1 else 2
        return 200, {"organic": [{"link": f"https://www.reddit.com/r/forhire/comments/{len(calls)}{i}/x/", "title": "[Hiring] dev",
                                  "description": "3 hours ago — Looking for a web developer"} for i in range(n)]}
    rows, prov, _ = serp.search('site:reddit.com "looking for" "web developer"', country="gb", pages=3, call=call, hours=6)
    assert prov == "brightdata" and len(rows) == 12 and len(calls) == 2
    assert calls[0]["zone"] == "my_serp_zone" and "tbs=qdr%3Ah6%2Csbd%3A1" in calls[0]["url"] and "gl=gb" in calls[0]["url"]
    assert "start=10" in calls[1]["url"]
    assert rows[0]["age_source"] == "snippet-relative" and 2.9 < rows[0]["age_hours"] < 3.1


def test_exact_post_time_from_linkedin_and_x_ids():
    t = NOW - timedelta(hours=2, minutes=30)
    got, how = serp.post_time(li_url(t), now=NOW)
    assert how == "linkedin-id" and abs((got - t).total_seconds()) < 1
    tw_id = (int(t.timestamp() * 1000) - serp.TWITTER_EPOCH_MS) << 22
    got, how = serp.post_time(f"https://x.com/founder_jane/status/{tw_id}", now=NOW)
    assert how == "x-id" and abs((got - t).total_seconds()) < 1
    got, how = serp.post_time("https://www.quora.com/q", "Nov 1, 2026 — need a dev", now=NOW)
    assert how == "snippet-date" and got.date().isoformat() == "2026-11-01"
    assert serp.post_time("https://example.com", "no date here", now=NOW) == (None, None)


def test_stamp_sorts_newest_first_and_sets_days_for_the_scorer():
    rows = [{"url": li_url(NOW - timedelta(days=3)), "text": ""}, {"url": "https://q.com", "text": "no date"},
            {"url": li_url(NOW - timedelta(hours=1), "b"), "text": ""}]
    out = serp.stamp(rows, now=NOW)
    assert [r.get("age_hours") for r in out] == [1.0, 72.0, None]
    assert out[1]["posted_days_ago"] == 3 and "posted_days_ago" not in out[2]


def test_watch_returns_only_new_leads_and_feeds_the_agenda(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    Path("SELLER-PROFILE.json").write_text(json.dumps({
        "offer": {"services": ["ecommerce"], "niches": ["DTC skincare"], "platforms": ["Shopify"]},
        "targets": {"countries": ["US"], "exclude_countries": ["India"]}}))
    fresh = li_url(datetime.now(timezone.utc) - timedelta(minutes=40), "sarah-kim")
    urls_seen = []

    def call(method, url, body=None, **kw):
        urls_seen.append(body["url"])
        if len(urls_seen) == 1:
            return 200, {"organic": [
                {"link": fresh, "title": "Help", "description": "Looking for a Shopify developer for our skincare brand, store is slow"},
                {"link": "https://www.linkedin.com/posts/agency_x", "title": "Agency", "description": "We build Shopify stores starting at $499, DM me"}]}
        return 200, {"organic": []}
    r = serp.watch(max_queries=3, call=call)
    assert r["window_hours"] == 24 and "qdr%3Ah24" in urls_seen[0]
    assert r["new_buyers"] == 1 and r["leads"][0]["url"] == fresh and r["leads"][0]["age_hours"] < 1
    urls_seen.clear()
    r2 = serp.watch(max_queries=3, call=call)                       # same result again → not new
    assert r2["new_buyers"] == 0 and r2["window_hours"] == 1 and "qdr%3Ah" in urls_seen[0]
    c = pipeline.connect()
    items = pipeline.today_agenda(c)["items"]
    assert items[0]["kind"] == "fresh-leads" and "1 fresh" in items[0]["action"]
    serp.mark_judged({fresh})
    assert not any(i["kind"] == "fresh-leads" for i in pipeline.today_agenda(c)["items"])
    c.close()


def test_opt_in_fallthrough(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    monkeypatch.setenv("SERPAPI_API_KEY", "serpapi_test_key")
    monkeypatch.setenv("SERP_PROVIDERS", "brightdata,serpapi")

    def call(method, url, params=None, **kw):
        if "brightdata" in url:
            return 401, {}
        assert params["engine"] == "google" and params["tbs"] == "qdr:m,sbd:1"
        return 200, {"organic_results": [{"link": "https://www.linkedin.com/posts/x_1", "title": "t", "snippet": "s"}]}
    rows, prov, errs = serp.search("q", days=30, call=call)
    assert prov == "serpapi" and "brightdata" in errs[0]


def test_hunt_spreads_countries_and_excludes_markets(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    Path("SELLER-PROFILE.json").write_text(json.dumps({
        "offer": {"services": ["ecommerce"], "niches": ["DTC skincare"], "platforms": ["Shopify"]},
        "targets": {"countries": ["US", "UK"], "exclude_countries": ["India"]}}))
    seen = []

    def call(method, url, body=None, **kw):
        seen.append(body["url"])
        if len(seen) == 1:
            return 200, {"organic": [
                {"link": "https://www.linkedin.com/posts/a_1", "title": "Need help", "description": "Looking for a Shopify developer for our skincare brand"},
                {"link": "https://www.linkedin.com/posts/c_3", "title": "Help", "description": "Looking for a Shopify developer in Mumbai, budget 50k INR"}]}
        return 200, {"organic": []}
    posts, errors, meta = serp.hunt(days=7, pages=1, max_queries=4, call=call)
    assert {("gl=us" in u, "gl=gb" in u) for u in seen} == {(True, False), (False, True)}
    out = lead_sources.finish(posts, errors)
    assert [c["url"] for c in out["candidates"]] == ["https://www.linkedin.com/posts/a_1"] and out["excluded_market"] == 1


def test_scorer_treats_unknown_age_and_comments_as_neutral():
    unknown = lead_scorer.score_agency({"intent_confidence": 0.9, "urgency": "high"})["breakdown"]
    known = lead_scorer.score_agency({"intent_confidence": 0.9, "urgency": "high", "posted_days_ago": 0, "comments": 0})["breakdown"]
    assert unknown["freshness"]["score"] == 7 and unknown["low_competition"]["score"] == 5
    assert known["freshness"]["score"] == 15 and known["low_competition"]["score"] == 10

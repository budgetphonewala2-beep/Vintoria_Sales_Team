"""Tests for lead_sources.py (Apify), the find_email.py provider waterfall, inbox.py and autopilot.py.
No network: API calls, IMAP and SMTP are faked."""

import sys
from datetime import date, datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import autopilot  # noqa: E402
import find_email  # noqa: E402
import inbox  # noqa: E402
import intent_scan  # noqa: E402
import lead_sources  # noqa: E402
import outreach  # noqa: E402
import pipeline  # noqa: E402
import site_audit  # noqa: E402

KEYS = ["APIFY_TOKEN", "BRIGHTDATA_API_KEY", "HUNTER_API_KEY", "PROSPEO_API_KEY", "FINDYMAIL_API_KEY", "APOLLO_API_KEY",
        "MILLIONVERIFIER_API_KEY", "ZEROBOUNCE_API_KEY", "NEVERBOUNCE_API_KEY", "EMAIL_FINDERS", "EMAIL_VERIFIERS",
        "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SENDER_EMAIL", "SENDER_NAME", "SENDER_ADDRESS", "BOOKING_URL",
        "IMAP_HOST", "IMAP_USER", "IMAP_PASSWORD", "AUTO_REPLY_CATEGORIES", "SEND_HOURS", "TIMEZONE", "DAILY_SEND_LIMIT",
        "APIFY_LINKEDIN_ACTOR", "CADENCE_DAYS"]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


# ------------------------------------------------------------------ Apify sources

LI_ITEMS = [
    {"type": "post", "linkedinUrl": "https://www.linkedin.com/posts/anita_need-website-123",
     "content": "Looking for a web developer to build a website for my bakery in Pune. Any recommendations?",
     "author": {"name": "Anita Desai", "info": "Founder at Sweet Crumbs", "linkedinUrl": "https://www.linkedin.com/in/anita"},
     "postedAt": {"date": "2026-10-30T10:00:00Z"}},
    {"linkedinUrl": "https://www.linkedin.com/posts/agency_we-build-456",
     "content": "We build affordable websites starting at ₹9999! DM me for our portfolio.", "author": {"name": "Cheap Agency"}},
]


def test_linkedin_runs_harvestapi_actor_and_scores(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    calls = []

    def call(method, url, headers=None, body=None, params=None, **kw):
        calls.append((method, url, headers, body, params))
        return 201, LI_ITEMS
    posts = lead_sources.linkedin(["need a website"], "week", 20, call=call)
    method, url, headers, body, params = calls[0]
    assert method == "POST" and url.endswith("/acts/harvestapi~linkedin-post-search/run-sync-get-dataset-items")
    assert headers == {"Authorization": "Bearer apify_api_test_token"} and "token" not in url
    assert body == {"searchQueries": ["need a website"], "maxPosts": 20, "postedLimit": "week", "sortBy": "date"}
    assert params["maxTotalChargeUsd"] == "1.00" and params["maxItems"] == 20
    assert posts[0]["author"] == "Anita Desai" and posts[0]["author_headline"].startswith("Founder")
    assert posts[0]["posted"] == "2026-10-30T10:00:00Z" and posts[0]["platform"] == "linkedin"
    out = lead_sources.finish(posts, [])
    assert [c["author"] for c in out["candidates"]] == ["Anita Desai"] and out["rejected"] == 1


def test_apify_errors_and_missing_token(monkeypatch):
    with pytest.raises(lead_sources.UserError):
        lead_sources.linkedin(["x"], call=lambda *a, **k: (200, []))
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    with pytest.raises(lead_sources.ApiError) as e:
        lead_sources.run_actor("a/b", {}, call=lambda *a, **k: (402, {"error": {"message": "Not enough credit"}}))
    assert "Not enough credit" in str(e.value)
    with pytest.raises(lead_sources.UserError):
        lead_sources.actor_path("not an actor")


def test_google_items_and_research(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")
    qs = lead_sources.research_queries("sweetcrumbs.in", "Sweet Crumbs", "Pune")

    def call(method, url, headers=None, body=None, params=None, **kw):
        assert "google-search-scraper" in url and body["queries"].count("\n") == len(qs) - 1
        return 201, [{"searchQuery": {"term": qs["reviews"]},
                      "organicResults": [{"title": "Sweet Crumbs - 4.2 stars", "url": "https://g.co/r1", "description": "48 reviews"}]},
                     {"searchQuery": {"term": qs["hiring"]},
                      "organicResults": [{"title": "Sweet Crumbs hiring", "url": "https://jobs/x", "description": "Marketing intern"}]}]
    r = lead_sources.research("https://www.sweetcrumbs.in", "Sweet Crumbs", "Pune", call=call)
    assert r["sections"]["reviews"][0]["url"] == "https://g.co/r1" and r["sections"]["hiring"]
    assert Path(r["saved"]).exists() and r["facts"][0]["evidence"].startswith("https://")


def test_google_falls_back_to_brightdata(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    got = lead_sources.google(["q"], call=lambda *a, **k: (200, {"organic": [{"link": "https://reddit.com/r/x", "title": "t",
                                                                              "description": "d"}]}))
    assert got[0]["platform"] == "reddit" and got[0]["source"] == "google"
    monkeypatch.delenv("BRIGHTDATA_API_KEY")
    with pytest.raises(lead_sources.UserError):
        lead_sources.google(["q"])


def test_hunt_reports_failed_sources_without_crashing(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "apify_api_test_token")

    def call(method, url, **kw):
        if "linkedin" in url:
            return 201, LI_ITEMS
        return 500, {"error": {"message": "boom"}}
    posts, errors = lead_sources.hunt(["web"], call=call)
    assert len(posts) == 2 and len(errors) == 2 and all("boom" in e for e in errors)


# ------------------------------------------------------------------ email waterfall

def _no_site(monkeypatch):
    monkeypatch.setattr(site_audit, "fetch_url", lambda u, timeout=10: {"url": u, "final_url": u, "status": 404, "html": None,
                                                                         "error": None, "tls_error": False})
    return lambda urls: []


def test_waterfall_order_and_fallthrough(monkeypatch):
    fetch = _no_site(monkeypatch)
    monkeypatch.setenv("PROSPEO_API_KEY", "prospeo_test_1")
    monkeypatch.setenv("FINDYMAIL_API_KEY", "findy_test_1")
    seen = []

    def call(method, url, headers=None, body=None, params=None, **kw):
        seen.append(url)
        if "prospeo" in url:
            assert headers == {"X-KEY": "prospeo_test_1"} and body["only_verified_email"] is True
            return 200, {"error": True, "error_code": "NO_MATCH"}
        if "findymail" in url:
            assert body == {"name": "Priya Mehta", "domain": "acme.in"}
            return 200, {"contact": {"email": "Priya@acme.in", "name": "Priya Mehta"}}
        raise AssertionError(url)
    r = find_email.find("acme.in", "Priya", "Mehta", "", True, fetch, call)
    assert r["best"] == {"email": "priya@acme.in", "status": "verified", "source": "findymail_finder",
                         "provider_status": "verified by Findymail"}
    assert r["finders_used"] == ["prospeo", "findymail"] and "prospeo" in seen[0]


def test_provider_errors_are_skipped_and_order_is_configurable(monkeypatch):
    fetch = _no_site(monkeypatch)
    monkeypatch.setenv("PROSPEO_API_KEY", "prospeo_test_1")
    monkeypatch.setenv("APOLLO_API_KEY", "apollo_test_1")
    monkeypatch.setenv("EMAIL_FINDERS", "apollo,prospeo")

    def call(method, url, headers=None, body=None, **kw):
        if "apollo" in url:
            return 429, {}
        return 200, {"error": False, "person": {"email": {"email": "priya@acme.in", "status": "VERIFIED"}}}
    r = find_email.find("acme.in", "Priya", "Mehta", "", True, fetch, call)
    assert r["best"]["source"] == "prospeo_finder" and r["best"]["status"] == "verified"
    assert any(s.get("error") == "Apollo HTTP 429" for s in r["steps"])


def test_verifier_chain_tests_patterns_when_nothing_found(monkeypatch):
    fetch = _no_site(monkeypatch)
    monkeypatch.setenv("MILLIONVERIFIER_API_KEY", "mv_test_key_1")
    monkeypatch.setenv("ZEROBOUNCE_API_KEY", "zb_test_key_1")
    tried = []

    def call(method, url, params=None, **kw):
        tried.append((url, params["email"]))
        if "millionverifier" in url:
            return 200, {"error": "insufficient credits"}
        return 200, {"status": "valid" if params["email"] == "priya@acme.in" else "invalid"}
    r = find_email.find("acme.in", "Priya", "Mehta", "", True, fetch, call)
    assert r["best"]["email"] == "priya@acme.in" and r["best"]["status"] == "verified" and r["best"]["verified_by"] == "zerobounce"
    statuses = {c["email"]: c["status"] for c in r["candidates"]}
    assert statuses == {"priya.mehta@acme.in": "invalid", "priya@acme.in": "verified", "priyamehta@acme.in": "pattern-guessed"}
    assert any("millionverifier" in u for u, _ in tried)          # tried first, failed, fell through


def test_no_api_flag_disables_everything(monkeypatch):
    fetch = _no_site(monkeypatch)
    monkeypatch.setenv("PROSPEO_API_KEY", "prospeo_test_1")
    r = find_email.find("acme.in", "Priya", "Mehta", "", False, fetch, None)
    assert r["best"]["status"] == "pattern-guessed" and r["finders_used"] == []


# ------------------------------------------------------------------ inbox + autopilot

BODY = ("Hi Priya,\n\nI saw your post looking for a new website for Acme.\nYour homepage has no mobile viewport tag.\n\n"
        "Worth a 15-minute call this week?\n\nNot relevant? Reply 'no' and I won't follow up.\n\nRavi\n")
EVIDENCE = ["looking for a new website for Acme", "The homepage has no mobile viewport tag."]


class FakeSMTP:
    sent = []

    class _S:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self, context=None):
            pass

        def login(self, u, p):
            pass

        def send_message(self, msg):
            FakeSMTP.sent.append(msg)

    SMTP = SMTP_SSL = _S


def mail(frm, subject, text, in_reply_to=None, mid="<r1@acme.com>", name="Priya Mehta"):
    m = EmailMessage()
    m["From"] = f"{name} <{frm}>"
    m["To"] = "ravi@agency.in"
    m["Subject"] = subject
    m["Message-ID"] = mid
    if in_reply_to:
        m["In-Reply-To"] = in_reply_to
    m.set_content(text)
    return m.as_bytes()


@pytest.fixture
def live(monkeypatch, tmp_path):
    for k, v in {"SMTP_HOST": "smtp.gmail.com", "SMTP_PASSWORD": "app-password-123", "SENDER_EMAIL": "ravi@agency.in",
                 "SENDER_NAME": "Ravi", "SEND_HOURS": "00:00-24:00", "TIMEZONE": "UTC", "BOOKING_URL": "https://cal.com/ravi/15min"}.items():
        monkeypatch.setenv(k, v)
    FakeSMTP.sent = []
    c = pipeline.connect()
    pipeline.add(c, url="https://acme.com", name="Acme")
    pipeline.add_contact(c, "acme.com", "Priya", email="priya@acme.com", email_status="verified")
    steps = [{"step": 1, "subject": "Acme website", "body": BODY},
             {"step": 2, "subject": "", "body": "Hi Priya,\n\nYour homepage has no mobile viewport tag.\n\nNot relevant? Reply 'no' and I won't follow up.\n\nRavi"}]
    assert outreach.approve(c, "acme.com", "priya@acme.com", steps, evidence_text=EVIDENCE, today=date(2026, 11, 2))["approved"]
    yield c
    c.close()


def test_inbox_config_derives_imap_host(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_USER", "ravi@agency.in")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password-123")
    cfg = inbox.config()
    assert cfg["host"] == "imap.gmail.com" and cfg["user"] == "ravi@agency.in" and cfg["port"] == 993
    monkeypatch.delenv("SMTP_PASSWORD")
    with pytest.raises(inbox.UserError):
        inbox.config()


def test_reply_in_thread_stops_sequence_and_auto_sends_booking_link(live):
    mon = datetime(2026, 11, 2, 6, tzinfo=timezone.utc)
    first = outreach.run(live, True, now=mon, smtp=FakeSMTP)["sent"][0]
    reply = mail("priya@acme.com", "Re: Acme website", "Sounds great, can we talk Thursday 4pm?\n\nOn Mon Ravi wrote:\n> hi",
                 in_reply_to=first["message_id"])
    noise = mail("news@shop.com", "Sale!", "50% off", mid="<n1@shop.com>", name="Shop")
    out = inbox.check(live, [reply, noise, reply], apply=True, auto_reply=True, smtp=FakeSMTP, now=mon)
    assert out["matched"][0]["category"] == "meeting_request" and out["matched"][0]["matched_by"] == "thread"
    assert out["ignored"] == 1 and out["already_seen"] == 1
    assert out["auto_replies"][0]["sent"], out["auto_replies"]
    link_mail = FakeSMTP.sent[-1]
    assert "https://cal.com/ravi/15min" in link_mail.get_content() and link_mail["In-Reply-To"] == "<r1@acme.com>"
    assert "Thursday 4pm" in link_mail.get_content()
    assert pipeline.get(live, "acme.com")["stage"] == "meeting"
    assert [q["status"] for q in outreach.queue(live, "acme.com")] == ["sent", "cancelled"]


def test_auto_reply_only_for_configured_categories(live):
    mon = datetime(2026, 11, 2, 6, tzinfo=timezone.utc)
    outreach.run(live, True, now=mon, smtp=FakeSMTP)
    q = mail("priya@acme.com", "Re: Acme website", "How much would a 5 page site cost?", mid="<q1@acme.com>")
    out = inbox.check(live, [q], apply=True, auto_reply=True, smtp=FakeSMTP, now=mon)
    assert out["matched"][0]["category"] == "interested" and out["auto_replies"] == [] and len(FakeSMTP.sent) == 1


def test_bounce_marks_contact_invalid(live):
    b = mail("mailer-daemon@googlemail.com", "Delivery Status Notification (Failure)",
             "Address not found. Your message wasn't delivered to priya@acme.com", mid="<b1@google>", name="Mail Delivery Subsystem")
    out = inbox.check(live, [b], apply=True)
    assert out["matched"][0]["category"] == "bounce" and pipeline.contacts(live, 1)[0]["email_status"] == "invalid"


def test_autopilot_never_sends_without_inbox(live):
    def no_inbox():
        raise inbox.UserError("inbox not configured")

    def broken():
        raise OSError("connection refused")
    for fetch, note in ((no_inbox, "NOT sending"), (broken, "not sending this run")):
        r = autopilot.tick(live, send=True, fetch=fetch, smtp=FakeSMTP, now=datetime(2026, 11, 2, 6, tzinfo=timezone.utc))
        assert any(note in n for n in r["notes"]) and not r["sequences"]["sent"] and not FakeSMTP.sent


def test_autopilot_tick_checks_inbox_then_sends(live):
    r = autopilot.tick(live, send=True, fetch=lambda: [], smtp=FakeSMTP, now=datetime(2026, 11, 2, 6, tzinfo=timezone.utc))
    assert r["inbox"]["scanned"] == 0 and len(r["sequences"]["sent"]) == 1 and len(FakeSMTP.sent) == 1
    assert "linux_mac_cron" in autopilot.schedule_lines()


def test_intent_scan_still_dedupes_across_sources():
    posts = [lead_sources.normalize(LI_ITEMS[0], "linkedin")]
    assert len(intent_scan.scan(posts)["candidates"]) == 1
    assert intent_scan.scan(posts)["duplicates_skipped"] == 1

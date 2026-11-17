"""Tests for v3.8: learning loop + subject A/B, mailbox rotation, alerts, PageSpeed facts. No network."""

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "vintoria-sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import autopilot  # noqa: E402
import learn  # noqa: E402
import mailboxes  # noqa: E402
import notify  # noqa: E402
import outreach  # noqa: E402
import pipeline  # noqa: E402
import prospect_scan  # noqa: E402
import reply_triage  # noqa: E402
import site_audit  # noqa: E402

ENV = ["SMTP_HOST", "SMTP_PASSWORD", "SENDER_EMAIL", "SENDER_NAME", "SEND_HOURS", "TIMEZONE", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
       "SLACK_WEBHOOK_URL", "DISCORD_WEBHOOK_URL", "ALERT_ON", "PW_A", "PW_B", "DAILY_SEND_LIMIT", "PAGESPEED_API_KEY", "SENDER_ADDRESS"]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in ENV:
        monkeypatch.delenv(k, raising=False)


BODY = "Hi,\n\nYour homepage has no viewport tag.\n\nWorth a look?\n\nNot relevant? Reply 'no' and I won't follow up.\n\nRavi"


class SMTP:
    sent = []

    class _S:
        def __init__(self, host, *a, **k):
            self.host = host

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self, context=None):
            pass

        def login(self, u, p):
            SMTP.logins.append((self.host, u, p))

        def send_message(self, msg):
            SMTP.sent.append(msg)

    SMTP = SMTP_SSL = _S
    logins = []


# ------------------------------------------------------------------ learning loop

def _contact(c, slug, source, hook, variant, replied=None, meeting=False, won=False, quality=85, subject="glow skin store"):
    pipeline.add(c, url=f"https://{slug}", source=source)
    pid = pipeline.get(c, slug)["id"]
    with c:
        c.execute("INSERT INTO sequence_steps(prospect_id, step, recipient, subject, body, status, created_at, variant, hook, quality) "
                  "VALUES (?,?,?,?,?,?,?,?,?,?)", (pid, 1, f"x@{slug}", subject, "b", "sent", "now", variant, hook, quality))
    outreach.log_touch(c, slug, "email", step=1, to=f"x@{slug}", schedule=False)
    if replied:
        reply_triage.apply(c, slug, reply_triage.classify(replied))
    if meeting:                   # a real booking, as meeting.book / the inbox booking detector record it
        with c:
            c.execute("INSERT INTO meetings(prospect_id, starts_at, minutes, status, created_at) VALUES (?,?,?,?,?)",
                      (pid, "2026-11-20T15:00:00+00:00", 30, "scheduled", "now"))
    if won:
        pipeline.set_stage(c, slug, "won", "signed")
        pipeline.set_value(c, slug, 5000)


def test_learning_report_ranks_queries_hooks_and_writes_weights():
    c = pipeline.connect()
    for i in range(6):            # query A: replies and meetings
        _contact(c, f"a{i}.com", "serp:li-niche-skincare", "their_post", "A" if i % 2 else "B",
                 replied="Sounds good, can we talk Thursday 4pm?" if i < 3 else None, meeting=i < 2, won=i == 0)
    for i in range(16):           # query B: nothing
        _contact(c, f"b{i}.com", "serp:reddit-web", "viewport", "A", quality=60)
    r = learn.report(c, min_n=5, apply=True)
    q = {g["query"]: g for g in r["by"]["query"]}
    assert q["serp:li-niche-skincare"]["meetings"] == 2 and q["serp:li-niche-skincare"]["positive"] == 3
    assert r["by"]["query"][0]["query"] == "serp:li-niche-skincare"
    assert any("Drop serp:reddit-web" in x for x in r["recommendations"])
    assert any("Double down on serp:li-niche-skincare" in x for x in r["recommendations"])
    assert r["by"]["hook"][0]["hook"] == "their_post" and r["won"] == 1
    L = learn.learned()
    assert "serp:reddit-web" in L["drop_queries"] and L["query_weights"]["serp:li-niche-skincare"] > 0
    c.close()


def test_ab_test_needs_data_then_names_a_winner():
    c = pipeline.connect()
    for i in range(25):
        _contact(c, f"x{i}.com", "serp:q", "h", "A", replied="Sounds good, can we talk tomorrow?" if i < 10 else None, subject="glow skin relaunch")
        _contact(c, f"y{i}.com", "serp:q", "h", "B", replied="Sounds good, can we talk tomorrow?" if i < 2 else None, subject="quick idea")
    ab = learn.ab(learn.rows(c), 20)
    assert ab["A"]["positive_pct"] == 40.0 and ab["B"]["positive_pct"] == 8.0 and ab["verdict"].startswith("A wins")
    assert "not enough data" in learn.ab(learn.rows(c), 50)["verdict"]
    c.close()


def test_approve_assigns_ab_variant_hook_and_quality(tmp_path):
    c = pipeline.connect()
    seq = tmp_path / "seq.json"
    seq.write_text(json.dumps([{"step": 1, "subject": "glow skin relaunch", "subject_b": "your mobile store", "hook": "pagespeed_score",
                                "body": BODY}]))
    variants = set()
    for d in ("one.com", "two.com", "three.com", "four.com", "five.com", "six.com"):
        pipeline.add(c, url=f"https://{d}")
        pipeline.add_contact(c, d, "X", email=f"x@{d}", email_status="verified")
        assert outreach.approve(c, d, f"x@{d}", outreach.parse_sequence(str(seq)), evidence_text=[BODY], today=date(2026, 11, 2))["approved"]
        row = c.execute("SELECT variant, hook, subject, quality FROM sequence_steps WHERE prospect_id = ?", (pipeline.get(c, d)["id"],)).fetchone()
        variants.add(row["variant"])
        assert row["hook"] == "pagespeed_score" and row["quality"] is not None
        assert row["subject"] == ("your mobile store" if row["variant"] == "B" else "glow skin relaunch")
    assert variants == {"A", "B"}
    c.close()


def test_serp_hunt_skips_dropped_queries_and_runs_winners_first(monkeypatch):
    import serp
    monkeypatch.setenv("BRIGHTDATA_API_KEY", "bd_test_key_123")
    Path("SELLER-PROFILE.json").write_text(json.dumps({"offer": {"services": ["web"], "niches": ["dental clinics"]},
                                                       "targets": {"countries": ["US"]}}))
    import query_library
    ids = [q["id"] for q in query_library.auto()["google_xray"] if q["platform"] != "signal"]
    (pipeline.data_home() / "learned.json").write_text(json.dumps({"drop_queries": [f"serp:{ids[0]}"],
                                                                   "query_weights": {f"serp:{ids[3]}": 50}}))
    seen = []

    def call(method, url, body=None, **kw):
        seen.append(body["url"])
        return 200, {"organic": []}
    _, _, meta = serp.hunt(days=7, pages=1, max_queries=2, call=call)
    assert meta["dropped_by_learning"] == [ids[0]]
    q3 = [q for q in query_library.auto()["google_xray"] if q["id"] == ids[3]][0]["query"]
    from urllib.parse import quote_plus
    assert quote_plus(q3)[:40] in seen[0]                                   # the winner ran first


# ------------------------------------------------------------------ mailbox rotation

def _boxes(monkeypatch, started_b=None):
    monkeypatch.setenv("PW_A", "app-pass-a-123")
    monkeypatch.setenv("PW_B", "app-pass-b-123")
    (pipeline.data_home() / "mailboxes.json").write_text(json.dumps([
        {"email": "ravi@getpixel.com", "smtp_host": "smtp.a.com", "password_env": "PW_A", "daily_limit": 2, "imap_host": "imap.a.com"},
        {"email": "ravi@trypixel.com", "smtp_host": "smtp.b.com", "password_env": "PW_B", "daily_limit": 3, "started": started_b}]))


def test_rotation_is_sticky_and_respects_each_mailbox_limit(monkeypatch):
    _boxes(monkeypatch)
    monkeypatch.setenv("SEND_HOURS", "00:00-24:00")
    SMTP.sent, SMTP.logins = [], []
    c = pipeline.connect()
    assert outreach.daily_limit() == 5 and [m["email"] for m in mailboxes.load()] == ["ravi@getpixel.com", "ravi@trypixel.com"]
    for d in ("p1.com", "p2.com", "p3.com"):
        pipeline.add(c, url=f"https://{d}")
        pipeline.add_contact(c, d, "X", email=f"x@{d}", email_status="verified")
        r = outreach.send(c, d, f"x@{d}", "hello there", BODY, evidence_text=[BODY], really=True, smtp=SMTP)
        assert r["sent"], r
    senders = [m["From"] for m in SMTP.sent]
    assert senders[0].endswith("trypixel.com") and senders[1].endswith("getpixel.com")   # most room first, then rotates
    cap = {x["email"]: x for x in mailboxes.capacity(c)}
    assert cap["ravi@trypixel.com"]["sent_today"] + cap["ravi@getpixel.com"]["sent_today"] == 3
    first_sender = c.execute("SELECT sender FROM touches WHERE prospect_id = 1").fetchone()[0]
    box, why = mailboxes.pick(c, 1)
    assert box["email"] == first_sender and "same mailbox" in why                          # sticky
    assert SMTP.logins[0][0] in ("smtp.a.com", "smtp.b.com") and all(p.startswith("app-pass") for _, _, p in SMTP.logins)
    c.close()


def test_new_mailbox_warms_up_and_full_mailbox_makes_thread_wait(monkeypatch):
    _boxes(monkeypatch, started_b=datetime.now(timezone.utc).date().isoformat())
    m = {x["email"]: x for x in mailboxes.load()}
    assert mailboxes.limit_today(m["ravi@trypixel.com"]) == 3                                # min(cap 3, warm-up 5)
    c = pipeline.connect()
    pipeline.add(c, url="https://q.com")
    for i in range(2):
        outreach.log_touch(c, "q.com", "email", step=i + 1, status="sent", sender="ravi@getpixel.com", schedule=False)
    box, why = mailboxes.pick(c, 1)
    assert box is None and "waits a day" in why
    assert {x["email"] for x in __import__("inbox").configs()} == {"ravi@getpixel.com", "ravi@trypixel.com"}  # imap host derived
    c.close()


def test_single_mailbox_fallback_still_works(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password-123")
    monkeypatch.setenv("SENDER_EMAIL", "ravi@pixel.io")
    assert [m["email"] for m in mailboxes.load()] == ["ravi@pixel.io"]
    assert outreach.doctor()["mode"] == "autopilot"


# ------------------------------------------------------------------ alerts

def test_alerts_go_to_every_channel_and_never_raise(monkeypatch):
    assert notify.channels() == []
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc_test_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T/B/x")
    calls = []

    def call(method, url, body=None, **kw):
        calls.append((url, body))
        if "slack" in url:
            raise OSError("down")
        return 200, {"ok": True}
    res = notify.send("hello", call=call)
    assert res["telegram"] == "ok" and "OSError" in res["slack"]
    assert calls[0][0].endswith("/bot123:abc_test_token/sendMessage") and calls[0][1]["chat_id"] == "42"
    leads = [{"age_hours": 0.7, "author": "Sarah Kim", "title": "Need a Shopify dev", "url": "https://x/1"}]
    assert "0.7h ago" in notify.fresh_leads_text(leads) and "Sarah Kim" in notify.fresh_leads_text(leads)


def test_autopilot_alerts_on_fresh_leads_and_replies(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T/B/x")
    sent = []
    out = {"hunt": {"new_buyers": 1, "leads": [{"age_hours": 1, "url": "u", "title": "t"}]},
           "inbox": {"matched": [{"prospect": "a.com", "category": "interested", "excerpt": "tell me more"},
                                 {"prospect": "b.com", "category": "bounce"}], "bookings": []}}
    res = autopilot.alert(out, call=lambda m, url, body=None, **k: (sent.append(body["text"]) or (200, {})))
    assert set(res) == {"fresh_leads", "replies"} and "1 fresh buyer post" in sent[0] and "a.com" in sent[1] and "b.com" not in sent[1]
    monkeypatch.setenv("ALERT_ON", "replies")
    sent.clear()
    assert set(autopilot.alert(out, call=lambda m, url, body=None, **k: (sent.append(1) or (200, {})))) == {"replies"}


# ------------------------------------------------------------------ PageSpeed

PSI = {"lighthouseResult": {"fetchTime": "2026-11-02T10:00:00Z",
                            "categories": {"performance": {"score": 0.38}},
                            "audits": {"largest-contentful-paint": {"numericValue": 6100}, "cumulative-layout-shift": {"numericValue": 0.31},
                                       "total-blocking-time": {"numericValue": 900}}},
       "loadingExperience": {"overall_category": "SLOW"}}


def test_pagespeed_facts_and_hooks(monkeypatch):
    calls = []

    def call(method, url, params=None, **kw):
        calls.append(params)
        return 200, PSI
    facts = {f["key"]: f for f in site_audit.pagespeed("https://glowskin.com", call=call)}
    assert calls[0]["strategy"] == "mobile" and "key" not in calls[0]
    assert facts["pagespeed_score"]["value"] == 38 and "38/100" in facts["pagespeed_score"]["statement"]
    assert facts["pagespeed_lcp_ms"]["value"] == 6100 and "6.1 s" in facts["pagespeed_lcp_ms"]["statement"]
    assert facts["crux_overall"]["value"] == "SLOW" and facts["pagespeed_cls"]["value"] == 0.31
    hooks = prospect_scan.rank_hooks(list(facts.values()))
    assert hooks[0]["key"] == "pagespeed_score" and {h["key"] for h in hooks} >= {"pagespeed_lcp_ms", "crux_overall"}
    import claim_check
    src = claim_check.load_sources([], [f["statement"] + " " + f["evidence"] for f in facts.values()], profile=False)
    assert claim_check.check("Google PageSpeed Insights gives your homepage a mobile performance score of 38/100.", src)["ok"]
    with pytest.raises(site_audit.ApiError):
        site_audit.pagespeed("https://x.com", call=lambda *a, **k: (429, {"error": {"message": "Quota exceeded"}}))

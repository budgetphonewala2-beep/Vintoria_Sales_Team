"""Tests for the v3.7 learnings: email quality score + gate, deliverability stop-loss, over-contact limit, new reply
categories and out-of-office pause, no-show policy, two-slot booking, pipeline status. No network."""

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "vintoria-sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import email_lint  # noqa: E402
import meeting  # noqa: E402
import outreach  # noqa: E402
import pipeline  # noqa: E402
import reply_triage  # noqa: E402

GOOD = ("Hi Jane,\n\nSaw your post: you're relaunching the Glow Skin store before Black Friday and want a Shopify developer "
        "who has done DTC before.\n\nYour homepage took 4.2 seconds to load in my test, so some of the mobile slowness starts "
        "before the theme loads.\n\nWe build Shopify stores for DTC brands; for Brew Co we rebuilt the store in 4 weeks.\n\n"
        "Worth a quick call to see what's realistic before Black Friday?\n\nRavi Sharma\nPixelcraft Studio\n12 MG Road, Pune\n\n"
        "Not relevant? Reply \"no\" and I won't follow up.")
BAD = ("Hi John,\n\nI hope this email finds you well. My name is Raj and we are a leading provider of innovative solutions. "
       "We leverage cutting-edge tech to supercharge your growth — it's not just about websites, it's about results!! "
       "See www.a.com/x and https://b.com/y.\n\nCan we schedule a 30 minute call this week?\n\nThanks")


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in ("SENDER_ADDRESS", "SMTP_HOST", "SMTP_PASSWORD", "SENDER_EMAIL", "BOUNCE_STOP_PCT", "MAX_TOUCHES_PER_WEEK"):
        monkeypatch.delenv(k, raising=False)


def test_good_email_ships_bad_email_is_rewritten_with_reasons():
    g = email_lint.lint(GOOD, "glow skin relaunch", 1)
    assert g["verdict"] in ("ship", "premium") and g["score"] >= 80, g
    b = email_lint.lint(BAD, "Quick question!", 1)
    assert b["verdict"] == "rewrite" and b["score"] < 50
    text = " | ".join(b["issues"])
    for needle in ("opens with I/we", "30 minute call", "subject", "hope this", "leverag", "em dash", "links"):
        assert needle in text, needle


def test_follow_up_rules_differ_from_first_email():
    weak = email_lint.lint("Hi Jane,\n\nJust checking in on my last email. Any update?\n\nRavi", None, 2)
    assert any("just checking in" in i for i in weak["issues"]) and weak["score"] < 80
    useful = email_lint.lint("Hi Jane,\n\nOne more thing I noticed: your homepage has no mobile viewport tag, so phones may get "
                             "the desktop layout. The fix is one line in theme.liquid.\n\nWant me to send the exact line?\n\nRavi", None, 2)
    assert useful["verdict"] in ("ship", "premium"), useful
    breakup = email_lint.lint("Hi Jane,\n\nI'll close the file on my side for now. If the relaunch is still on your list, "
                              "just reply here.\n\nRavi", None, 5)
    assert breakup["score"] >= 75, breakup


def test_quality_gate_blocks_weak_sequences(monkeypatch):
    monkeypatch.setenv("LINT_MIN_SCORE", "65")
    c = pipeline.connect()
    pipeline.add(c, url="https://acme.com")
    pipeline.add_contact(c, "acme.com", "John", email="john@acme.com", email_status="verified")
    r = outreach.approve(c, "acme.com", "john@acme.com", [{"step": 1, "subject": "Quick question!",
                                                            "body": BAD + "\n\nNot relevant? Reply 'no' and I won't follow up."}],
                         evidence_text=[BAD], check_only=True)
    assert not r.get("check_passed") and any("quality score" in p for p in r["steps"][0]["problems"])
    assert r["steps"][0]["quality"]["verdict"] == "rewrite"
    c.close()


def _sent(c, pid, n, at):
    for i in range(n):
        c.execute("INSERT INTO touches(prospect_id, channel, step, recipient, status, at) VALUES (?,?,?,?,?,?)",
                  (pid, "email", 1, f"x{i}@a.com", "sent", at))


def test_stop_loss_pauses_on_bounces_and_warns_on_low_replies():
    c = pipeline.connect()
    pipeline.add(c, url="https://a.com")
    pipeline.add_contact(c, "a.com", "A", email="a@a.com", email_status="verified")
    now = datetime.now(timezone.utc)
    with c:
        _sent(c, 1, 30, now.replace(microsecond=0).isoformat())
        for _ in range(2):
            pipeline.event(c, 1, "reply", "[bounce] Delivery has failed")
    sl = outreach.stop_loss(c)
    assert sl["paused"] and sl["bounce_rate_pct"] == 6.7
    probs, _ = outreach.preflight(c, "a.com", "a@a.com", "hi", "Hi\n\nNot relevant? Reply 'no' and I won't follow up.",
                                  evidence_text=["Hi"])
    assert any("stop-loss" in p for p in probs)
    assert "PAUSED" in outreach.doctor(c)["warnings"][0]
    with c:
        _sent(c, 1, 300, (now - timedelta(days=30)).replace(microsecond=0).isoformat())
    assert "reply rate" in outreach.stop_loss(c)["warning"]
    c.close()


def test_over_contact_limit():
    c = pipeline.connect()
    pipeline.add(c, url="https://b.com")
    pipeline.add_contact(c, "b.com", "B", email="b@b.com", email_status="verified")
    for ch in ("email", "linkedin", "linkedin", "whatsapp"):
        outreach.log_touch(c, "b.com", ch, schedule=False)
    probs, _ = outreach.preflight(c, "b.com", "b@b.com", "hi", "Hi\n\nNot relevant? Reply 'no' and I won't follow up.",
                                  evidence_text=["Hi"])
    assert any("over-contact" in p for p in probs)
    c.close()


@pytest.mark.parametrize("text,cat", [
    ("How did you get my email address?", "how_got_email"),
    ("Can you send me a few case studies?", "send_info"),
    ("Not my area, sorry.", "wrong_person"),
    ("Not my area — talk to my colleague Sam, cc'ing her", "referral"),
])
def test_new_reply_categories(text, cat):
    assert reply_triage.classify(text)["category"] == cat


def test_out_of_office_moves_the_queue_to_after_return(monkeypatch):
    assert reply_triage.return_date("I'm away until 10 November", date(2026, 11, 2)) == date(2026, 11, 10)
    assert reply_triage.return_date("back on Nov 9", date(2026, 11, 2)) == date(2026, 11, 9)
    assert reply_triage.return_date("returning 1/5", date(2026, 12, 20)) == date(2027, 1, 5)
    c = pipeline.connect()
    pipeline.add(c, url="https://c.com")
    pipeline.add_contact(c, "c.com", "C", email="c@c.com", email_status="verified")
    with c:
        c.execute("INSERT INTO sequence_steps(prospect_id, step, recipient, body, status, due, created_at) VALUES (1, 2, 'c@c.com', 'x', "
                  "'approved', ?, 'now')", (date.today().isoformat(),))
    res = reply_triage.classify("Thanks for your email. I am out of the office until 30 December with limited access.")
    done = reply_triage.apply(c, "c.com", res, "c@c.com")
    due = c.execute("SELECT due FROM sequence_steps").fetchone()[0]
    assert due > date.today().isoformat() and any("paused until" in d for d in done)
    c.close()


def test_second_no_show_goes_to_nurture_and_two_slots_by_default():
    c = pipeline.connect()
    pipeline.add(c, url="https://d.com")
    now = datetime.now(timezone.utc) + timedelta(days=2)
    ids = []
    for h in (10, 14):
        r = meeting.book(c, "d.com", now.replace(hour=h, minute=0).strftime("%Y-%m-%d %H:%M"), "UTC", 30)
        ids.append(r["meeting_id"])
    first = meeting.outcome(c, ids[0], "no_show")
    assert "TODAY" in first["next_action"] and pipeline.get(c, "d.com")["stage"] == "meeting"
    second = meeting.outcome(c, ids[1], "no_show")
    assert "nurture" in second["next_action"] and pipeline.get(c, "d.com")["stage"] == "nurture"
    assert len(meeting.propose(c, "UTC", my_tz="UTC")["slots"]) == 2
    c.close()


def test_status_is_the_single_starting_point():
    c = pipeline.connect()
    s = pipeline.status(c)
    assert s["profile"]["ready"] is False and "vintoria-setup" in s["next_action"]
    Path("SELLER-PROFILE.json").write_text(json.dumps({
        "seller": {"name": "R", "company": "P", "email": "r@p.io", "postal_address": "x", "timezone": "UTC"},
        "offer": {"services": ["web"], "service_details": "x", "niches": ["dental"], "outcomes": ["x"], "deal_size": {"min": 1}},
        "targets": {"countries": ["US"], "buyer_titles": ["Owner"]}, "proof": {"case_studies": ["x"]},
        "positioning": {"differentiators": ["x"]}, "signals": {"pains": ["x"]}}))
    s = pipeline.status(c)
    assert s["profile"]["ready"] and "BRIGHTDATA_API_KEY" in s["next_action"] and s["sending"]["mode"] == "manual"
    c.close()

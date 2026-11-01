"""Tests for the end-to-end scripts: outreach.py (touches, cadence, send gates), reply_triage.py, meeting.py,
and pipeline.py today/suppress. No network: SMTP is faked."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import meeting  # noqa: E402
import outreach  # noqa: E402
import pipeline  # noqa: E402
import reply_triage  # noqa: E402

BODY = ("Hi Priya,\n\nI saw your post looking for a new website for Acme.\nYour homepage has no mobile viewport tag.\n\n"
        "Worth a 15-minute call this week?\n\nNot relevant? Reply 'no' and I won't follow up.\n\nRavi\n")
EVIDENCE = ["looking for a new website for Acme", "The homepage has no mobile viewport tag."]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_PORT", "SENDER_EMAIL", "SENDER_NAME", "SENDER_ADDRESS",
              "TIMEZONE", "WORK_HOURS", "WORK_DAYS", "EXTENDED_HOURS", "BOOKING_URL", "MEETING_LINK", "CADENCE_DAYS",
              "DAILY_SEND_LIMIT", "MEETING_MINUTES", "REPLY_TO"):
        monkeypatch.delenv(k, raising=False)


@pytest.fixture
def conn():
    c = pipeline.connect()
    pipeline.add(c, url="https://acme.com", name="Acme")
    pipeline.add_contact(c, "acme.com", "Priya", email="priya@acme.com", email_status="verified")
    yield c
    c.close()


# ------------------------------------------------------------------ outreach

def test_log_touch_moves_stage_and_schedules_cadence(conn):
    out = outreach.log_touch(conn, "acme.com", "email", to="priya@acme.com", subject="Hi", today=date(2026, 11, 6))  # Friday
    assert out["stage"] == "contacted" and out["step"] == 1
    assert out["next_due"] == "2026-11-09"                       # day 3 = Sunday -> Monday
    def log(day):                                 # the sandbox clock may be earlier than these dates: pin them
        conn.execute("UPDATE touches SET at = '2026-11-06T05:00:00+00:00'")
        return outreach.log_touch(conn, "acme.com", "email", today=date(2026, 11, day) if day < 32 else date(2026, 12, day - 30))
    assert log(9)["next_due"] == "2026-11-13"     # day 7
    assert log(13)["next_due"] == "2026-11-20"    # day 14
    out = log(20)
    assert out["next_due"] == "2026-12-04" and "breakup" in out["next_action"]                                # day 28
    assert "nurture" in log(34)["next_action"]
    outreach.stop(conn, "acme.com", "replied")
    assert pipeline.get(conn, "acme.com")["next_due"] is None


def test_followup_due_is_never_in_the_past():
    assert outreach.followup_due(date(2026, 11, 2), 1) == date(2026, 11, 5)
    assert outreach.followup_due(date(2026, 11, 2), 2, today=date(2026, 11, 20)) == date(2026, 11, 23)   # late run
    assert outreach.followup_due(date(2026, 11, 2), 5) is None


def test_cadence_override(monkeypatch):
    monkeypatch.setenv("CADENCE_DAYS", "2,5")
    assert outreach.cadence() == [2, 5]
    monkeypatch.setenv("CADENCE_DAYS", "x,0")
    assert outreach.cadence() == outreach.DEFAULT_CADENCE == [3, 7, 14, 28]
    monkeypatch.setenv("CADENCE_DAYS", "7,3")                    # must increase
    assert outreach.cadence() == [3, 7, 14, 28]


def test_send_dry_run_passes_and_gates_block(conn):
    ok = outreach.send(conn, "acme.com", "priya@acme.com", "Acme website", BODY, evidence_text=EVIDENCE)
    assert ok["problems"] == [] and ok["dry_run"] and not ok["sent"]
    # unverified address, missing opt-out, unsupported claim, fake Re:
    pipeline.add_contact(conn, "acme.com", "Raj", email="raj@acme.com", email_status="pattern-guessed")
    bad = outreach.send(conn, "acme.com", "raj@acme.com", "Re: website",
                        "We grew traffic 300% for 40 clients.\n\nRavi", evidence_text=EVIDENCE)
    text = " | ".join(bad["problems"])
    assert not bad["sent"] and "pattern-guessed" in text and "opt-out" in text and "unsupported claim" in text and "Re:" in text
    pipeline.suppress(conn, "acme.com", "asked")
    assert any("do-not-contact" in p for p in outreach.send(conn, "acme.com", "priya@acme.com", "x", BODY,
                                                             evidence_text=EVIDENCE)["problems"])


def test_send_requires_smtp_and_postal_address(conn, monkeypatch):
    r = outreach.send(conn, "acme.com", "priya@acme.com", "Acme website", BODY, evidence_text=EVIDENCE, really=True)
    assert not r["sent"] and any("SMTP not configured" in p for p in r["problems"])
    monkeypatch.setenv("SENDER_ADDRESS", "12 MG Road, Pune 411001, India")
    r = outreach.send(conn, "acme.com", "priya@acme.com", "Acme website", BODY, evidence_text=EVIDENCE)
    assert any("postal address" in p for p in r["problems"])


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
            assert p == "app-password-123"

        def send_message(self, msg):
            FakeSMTP.sent.append(msg)

    SMTP = SMTP_SSL = _S


def test_send_really_sends_logs_and_enforces_limits(conn, monkeypatch):
    for k, v in {"SMTP_HOST": "smtp.example.com", "SMTP_PASSWORD": "app-password-123", "SENDER_EMAIL": "ravi@agency.in",
                 "SENDER_NAME": "Ravi", "DAILY_SEND_LIMIT": "1"}.items():
        monkeypatch.setenv(k, v)
    FakeSMTP.sent = []
    r = outreach.send(conn, "acme.com", "priya@acme.com", "Acme website", BODY, evidence_text=EVIDENCE, really=True,
                      smtp=FakeSMTP)
    assert r["sent"] and r["message_id"] and len(FakeSMTP.sent) == 1
    msg = FakeSMTP.sent[0]
    assert msg["To"] == "priya@acme.com" and "unsubscribe" in msg["List-Unsubscribe"] and msg.get_content_type() == "text/plain"
    assert pipeline.get(conn, "acme.com")["stage"] == "contacted"
    again = outreach.send(conn, "acme.com", "priya@acme.com", "Acme website", BODY, evidence_text=EVIDENCE, really=True,
                          smtp=FakeSMTP)
    text = " | ".join(again["problems"])
    assert not again["sent"] and "daily send limit" in text and "already emailed" in text and len(FakeSMTP.sent) == 1


def test_booking_link_only_after_interest(conn, monkeypatch):
    monkeypatch.setenv("BOOKING_URL", "https://cal.com/ravi/15min")
    pitch = BODY.replace("Worth a 15-minute call this week?", "Book a call: https://cal.com/ravi/15min")
    r = outreach.send(conn, "acme.com", "priya@acme.com", "Acme website", pitch, evidence_text=EVIDENCE + ["https://cal.com/ravi/15min"])
    assert any("booking link" in p for p in r["problems"])
    calendly = BODY + "\nhttps://calendly.com/ravi\n"
    assert any("booking link" in p for p in outreach.send(conn, "acme.com", "priya@acme.com", "x", calendly,
                                                          evidence_text=EVIDENCE)["problems"])
    reply_triage.apply(conn, "acme.com", reply_triage.classify("Sounds interesting, tell me more"))
    r = outreach.send(conn, "acme.com", "priya@acme.com", "Re: Acme website", pitch, evidence_text=EVIDENCE + ["https://cal.com/ravi/15min"])
    assert not any("booking link" in p for p in r["problems"])
    pipeline.add(conn, url="https://cold.in")
    pipeline.add_contact(conn, "cold.in", "Raj", email="raj@cold.in", email_status="verified")
    reply_triage.apply(conn, "cold.in", reply_triage.classify("Not interested right now, maybe after Diwali"))
    assert not outreach.ready_for_link(conn, pipeline.get(conn, "cold.in"))       # nurture != ready


SEQ = [{"step": 1, "subject": "Acme website", "body": BODY},
       {"step": 2, "body": "Hi Priya,\n\nOne more thing: your homepage has no mobile viewport tag.\n\nNot relevant? Reply 'no' and I won't follow up.\n\nRavi"},
       {"step": 3, "body": "Hi Priya,\n\nShould I close the loop on this?\n\nNot relevant? Reply 'no' and I won't follow up.\n\nRavi"}]


def _smtp_env(monkeypatch, limit="30"):
    for k, v in {"SMTP_HOST": "smtp.example.com", "SMTP_PASSWORD": "app-password-123", "SENDER_EMAIL": "ravi@agency.in",
                 "DAILY_SEND_LIMIT": limit, "SEND_HOURS": "00:00-24:00", "TIMEZONE": "UTC"}.items():
        monkeypatch.setenv(k, v)


def test_approved_sequence_sends_on_schedule_in_thread_and_stops_on_reply(conn, monkeypatch, tmp_path):
    _smtp_env(monkeypatch)
    FakeSMTP.sent = []
    seq = tmp_path / "seq.json"
    seq.write_text(__import__("json").dumps(SEQ), encoding="utf-8")
    steps = outreach.parse_sequence(str(seq))
    bad = outreach.approve(conn, "acme.com", "priya@acme.com", [{**steps[0], "body": "We grew 40 clients 300%."}] + steps[1:],
                           evidence_text=EVIDENCE)
    assert not bad["approved"] and not outreach.queue(conn)                       # nothing queued when a step fails
    ok = outreach.approve(conn, "acme.com", "priya@acme.com", steps, evidence_text=EVIDENCE, today=date(2026, 11, 2))
    assert ok["approved"] and len(outreach.queue(conn, "acme.com")) == 3
    mon = datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc)
    dry = outreach.run(conn, False, now=mon)
    assert len(dry["would_send"]) == 1 and not FakeSMTP.sent
    r = outreach.run(conn, True, now=mon, smtp=FakeSMTP)
    assert len(r["sent"]) == 1 and r["sent"][0]["next_due"] == "2026-11-05"      # day 3
    assert outreach.run(conn, True, now=datetime(2026, 11, 4, 6, tzinfo=timezone.utc), smtp=FakeSMTP)["due"] == 0
    conn.execute("UPDATE touches SET at = '2026-10-01T00:00:00+00:00'")          # pretend email 1 was days ago
    conn.execute("UPDATE touches SET at = '2026-11-02T06:00:00+00:00'")
    r = outreach.run(conn, True, now=datetime(2026, 11, 5, 6, tzinfo=timezone.utc), smtp=FakeSMTP)
    assert len(r["sent"]) == 1 and r["sent"][0]["subject"] == "Re: Acme website" and r["sent"][0]["next_due"] == "2026-11-09"
    second = FakeSMTP.sent[1]
    assert second["In-Reply-To"] == FakeSMTP.sent[0]["Message-ID"]               # same thread
    reply_triage.apply(conn, "acme.com", reply_triage.classify("Thanks, can we talk next week?"))
    r = outreach.run(conn, True, now=datetime(2026, 11, 9, 6, tzinfo=timezone.utc), smtp=FakeSMTP)
    assert not r["sent"] and len(FakeSMTP.sent) == 2
    assert [q["status"] for q in outreach.queue(conn, "acme.com")] == ["sent", "sent", "cancelled"]


def test_run_respects_send_window_and_markdown_sequences(conn, monkeypatch, tmp_path):
    _smtp_env(monkeypatch)
    monkeypatch.setenv("SEND_HOURS", "09:00-18:00")
    md = tmp_path / "seq.md"
    md.write_text("## Email 1\nSubject: Acme website\n\n" + BODY + "\n## Email 2\n\n" + SEQ[1]["body"], encoding="utf-8")
    steps = outreach.parse_sequence(str(md))
    assert [s["step"] for s in steps] == [1, 2] and steps[0]["subject"] == "Acme website" and "Subject" not in steps[0]["body"]
    outreach.approve(conn, "acme.com", "priya@acme.com", steps, evidence_text=EVIDENCE, today=date(2026, 11, 2))
    night = outreach.run(conn, True, now=datetime(2026, 11, 2, 23, 0, tzinfo=timezone.utc), smtp=FakeSMTP)
    assert not night["in_window"] and not night["sent"] and "Outside SEND_HOURS" in night["note"]
    with pytest.raises(outreach.UserError):
        bad = tmp_path / "bad.json"
        bad.write_text('[{"step": 2, "body": "x"}]', encoding="utf-8")
        outreach.parse_sequence(str(bad))


def test_whatsapp_link():
    assert outreach.whatsapp_link("+91 98100-00000", "Namaste ji") == "https://wa.me/919810000000?text=Namaste%20ji"
    with pytest.raises(outreach.UserError):
        outreach.whatsapp_link("98100 00000", "x")              # no country code


# ------------------------------------------------------------------ reply triage

@pytest.mark.parametrize("text,cat", [
    ("Sounds interesting! Can we talk Thursday 4pm IST?", "meeting_request"),
    ("Haan bilkul interested, kal call karte hain 5 baje", "meeting_request"),
    ("Not interested, thanks.", "not_interested"),
    ("Please remove me from your list", "unsubscribe"),
    ("No", "unsubscribe"),
    ("Bhai bahut mehenga hai", "objection_price"),
    ("We already have an agency handling this", "objection_has_vendor"),
    ("Not interested right now, maybe after Diwali", "objection_timing"),
    ("abhi nahi, agle mahine baat karte hain", "objection_timing"),
    ("You should talk to my partner Rahul, cc'ing him", "referral"),
    ("How much would a 5 page site cost?", "interested"),
    ("I am out of the office until Nov 10", "out_of_office"),
    ("Delivery has failed to these recipients", "bounce"),
    ("Do you also do Shopify?", "question"),
    ("ok", "unclear"),
])
def test_reply_classification(text, cat):
    assert reply_triage.classify(text)["category"] == cat


def test_reply_ignores_quoted_thread():
    r = reply_triage.classify("Let's set up a call\n\nOn Mon, Nov 2, 2026 at 10:00 Ravi <r@x.in> wrote:\n> unsubscribe me")
    assert r["category"] == "meeting_request"


def test_reply_apply_updates_pipeline(conn):
    outreach.log_touch(conn, "acme.com", "email", to="priya@acme.com")
    r = reply_triage.classify("Sounds good, can we talk tomorrow 11am?")
    done = reply_triage.apply(conn, "acme.com", r, "priya@acme.com")
    p = pipeline.get(conn, "acme.com")
    assert p["stage"] == "meeting" and "follow-ups stopped" in done and "Book it" in p["next_action"]
    pipeline.add(conn, url="https://beta.in")
    reply_triage.apply(conn, "beta.in", reply_triage.classify("unsubscribe"), "boss@beta.in")
    assert pipeline.is_suppressed(conn, "boss@beta.in") and pipeline.get(conn, "beta.in")["stage"] == "lost"
    reply_triage.apply(conn, "acme.com", reply_triage.classify("Mail delivery failed: user unknown"), "priya@acme.com")
    assert pipeline.contacts(conn, 1)[0]["email_status"] == "invalid"


def test_reply_never_moves_deal_backwards(conn):
    pipeline.set_stage(conn, "acme.com", "proposal")
    reply_triage.apply(conn, "acme.com", reply_triage.classify("Do you also do Shopify?"))
    assert pipeline.get(conn, "acme.com")["stage"] == "proposal"


# ------------------------------------------------------------------ meetings

NOW = datetime(2026, 11, 2, 3, 0, tzinfo=timezone.utc)   # Monday 08:30 IST


def test_slots_same_zone_and_cross_zone(conn):
    r = meeting.propose(conn, "Asia/Kolkata", count=3, now=NOW, my_tz="Asia/Kolkata")
    assert len(r["slots"]) == 3 and len({s["start_utc"][:10] for s in r["slots"]}) == 3      # spread over days
    assert not any(s["outside_your_work_hours"] for s in r["slots"])
    us = meeting.propose(conn, "EST", count=2, now=NOW, my_tz="IST")
    assert len(us["slots"]) == 2 and all(s["outside_your_work_hours"] for s in us["slots"])  # India <-> US
    assert all(("AM EST" in s["theirs"] or "PM EST" in s["theirs"]) for s in us["slots"])
    assert "EST" in us["message"] and us["note"]
    with pytest.raises(meeting.UserError):
        meeting.tz("Mars/Olympus")


def test_book_writes_ics_updates_pipeline_and_blocks_clash(conn, tmp_path):
    outreach.log_touch(conn, "acme.com", "email", to="priya@acme.com")
    r = meeting.book(conn, "acme.com", "2026-11-05 4:30 PM", "Asia/Kolkata", 30, "priya@acme.com", "Priya Mehta",
                     "https://meet.google.com/abc-defg-hij", "Website plan", today=NOW, prospect_tz="Europe/London")
    ics = Path(r["ics"]).read_bytes().decode()
    assert "DTSTART:20261105T110000Z" in ics and "DTEND:20261105T113000Z" in ics and "\r\n" in ics
    assert "ATTENDEE;CN=Priya Mehta" in ics and "METHOD:REQUEST" in ics
    assert all(len(line.encode()) <= 75 for line in ics.split("\r\n"))
    assert r["start_theirs"].startswith("Thu 05 Nov, 11:00 AM GMT") and r["warning"] is None
    p = pipeline.get(conn, "acme.com")
    assert p["stage"] == "meeting" and p["next_due"] == "2026-11-04" and "Prep" in p["next_action"]
    with pytest.raises(meeting.UserError):
        meeting.book(conn, "acme.com", "2026-11-05 16:45", "Asia/Kolkata", 30, today=NOW)        # overlaps
    with pytest.raises(meeting.UserError):
        meeting.book(conn, "acme.com", "2020-01-01 10:00", "Asia/Kolkata", today=NOW)          # past
    free = meeting.propose(conn, "Asia/Kolkata", count=20, days=4, now=NOW, my_tz="Asia/Kolkata")
    assert not any(s["start_utc"] == "2026-11-05T11:00:00+00:00" for s in free["slots"])       # booked time not offered
    out = meeting.outcome(conn, r["meeting_id"], "held", "budget 60k")
    assert out["suggested_stage"] == "proposal" and "proposal" in out["next_action"]
    assert meeting.listing(conn) == [] and meeting.listing(conn, all_=True)[0]["status"] == "held"


# ------------------------------------------------------------------ today agenda

def test_today_agenda_priorities(conn):
    pipeline.add(conn, url="https://fresh.in", name="Fresh")
    pipeline.set_score(conn, "fresh.in", 82)
    outreach.log_touch(conn, "acme.com", "email", to="priya@acme.com", today=date(2026, 10, 20))
    conn.execute("UPDATE touches SET at = '2026-10-20T05:00:00+00:00'")
    reply_triage.apply(conn, "acme.com", reply_triage.classify("Tell me more, what would it cost?"))
    agenda = pipeline.today_agenda(conn, datetime(2026, 11, 2, 6, 0, tzinfo=timezone.utc))
    kinds = [i["kind"] for i in agenda["items"]]
    assert kinds[0] == "reply" and agenda["items"][0]["skill"] == "sales-reply"
    assert "new-lead" in kinds and agenda["items"][-1]["prospect"] == "fresh.in"
    assert agenda["tip"] and agenda["open_leads"] == 2


def test_suppression_matches_domain(conn):
    pipeline.suppress(conn, "Acme.com", "competitor")
    assert pipeline.is_suppressed(conn, "anyone@acme.com")["value"] == "acme.com"
    assert pipeline.is_suppressed(conn, "x@other.com") is None

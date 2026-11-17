"""The whole sales loop in one test — profile → lead → dossier → sequence → sends → reply → booking link →
Calendly booking → meeting → outcome → deal value → won → forecast — plus the v3.5 fixes. No network."""

import json
import sys
from datetime import date, datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "vintoria-sales" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import claim_check  # noqa: E402
import inbox  # noqa: E402
import lead_sources  # noqa: E402
import meeting  # noqa: E402
import outreach  # noqa: E402
import pipeline  # noqa: E402
import sales_common  # noqa: E402

PROFILE = {
    "seller": {"name": "Ravi Sharma", "company": "Pixelcraft", "email": "ravi@pixelcraft.io", "timezone": "Asia/Kolkata",
               "postal_address": "12 MG Road, Pune", "booking_url": "https://cal.com/ravi/20min", "website": "pixelcraft.io"},
    "offer": {"services": ["ecommerce"], "service_details": "Shopify stores for DTC brands", "niches": ["DTC skincare"],
              "platforms": ["Shopify"], "outcomes": ["faster store"], "deal_size": {"min": 2000, "typical": 6000, "currency": "USD"}},
    "targets": {"countries": ["US"], "buyer_titles": ["Founder"], "exclude_countries": ["India"]},
    "proof": {"case_studies": [{"client": "Brew Co", "result": "store rebuilt in 4 weeks, checkout conversion 1.8% to 2.6%"}],
              "years_in_business": 6},
    "positioning": {"differentiators": ["Shopify Partner"]},
    "signals": {"pains": ["store is slow"]},
}
ENV = ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SENDER_EMAIL", "SENDER_NAME", "SENDER_ADDRESS", "BOOKING_URL", "TIMEZONE",
       "SEND_HOURS", "DAILY_SEND_LIMIT", "SENDING_STARTED", "CADENCE_DAYS", "APOLLO_API_KEY", "APIFY_TOKEN", "AUTO_REPLY_CATEGORIES",
       "MILLIONVERIFIER_API_KEY", "ZEROBOUNCE_API_KEY", "NEVERBOUNCE_API_KEY", "HUNTER_API_KEY", "PROSPECT_DEFAULT_TZ"]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_SALES_HOME", str(tmp_path / "home"))
    monkeypatch.chdir(tmp_path)
    for k in ENV:
        monkeypatch.delenv(k, raising=False)
    Path("SELLER-PROFILE.json").write_text(json.dumps(PROFILE), encoding="utf-8")


class SMTP:
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
            SMTP.sent.append(msg)

    SMTP = SMTP_SSL = _S


def mail(frm, subject, text, mid, in_reply_to=None, name="Jane Doe", ics=None):
    m = EmailMessage()
    m["From"], m["To"], m["Subject"], m["Message-ID"] = f"{name} <{frm}>", "ravi@pixelcraft.io", subject, mid
    if in_reply_to:
        m["In-Reply-To"] = in_reply_to
    m.set_content(text)
    if ics:
        m.add_attachment(ics.encode(), maintype="text", subtype="calendar", filename="invite.ics")
    return m.as_bytes()


BODY1 = ("Hi Jane,\n\nI saw your post looking for a Shopify developer for Glow Skin.\n"
         "Your homepage has no mobile viewport tag.\n\nWe rebuilt the Brew Co store in 4 weeks.\n\n"
         "Worth a quick call?\n\nNot relevant? Reply 'no' and I won't follow up.\n\nRavi Sharma\n12 MG Road, Pune\n")
BODY2 = ("Hi Jane,\n\nOne more thing: your homepage has no mobile viewport tag, so phones may get the desktop layout.\n\n"
         "Not relevant? Reply 'no' and I won't follow up.\n\nRavi Sharma\n12 MG Road, Pune\n")


def test_full_loop(monkeypatch):
    for k, v in {"SMTP_HOST": "smtp.gmail.com", "SMTP_PASSWORD": "app-password-123", "SEND_HOURS": "09:00-17:00"}.items():
        monkeypatch.setenv(k, v)
    SMTP.sent = []
    assert sales_common.setting("SENDER_EMAIL") == "ravi@pixelcraft.io"           # from the profile, no .env needed
    assert sales_common.setting("BOOKING_URL") == "https://cal.com/ravi/20min"
    conn = pipeline.connect()

    # 1. a lead from a post, with its research (what prospect_scan would have saved)
    pipeline.add(conn, url="https://glowskin.com", name="Glow Skin", source="hunt:li-niche-DTC skincare")
    pipeline.add_contact(conn, "glowskin.com", "Jane Doe", title="Founder", email="jane@glowskin.com", email_status="verified")
    pipeline.set_where(conn, "glowskin.com", "US", "America/New_York")
    folder = Path("prospects/glowskin.com"); folder.mkdir(parents=True)
    (folder / "DOSSIER.json").write_text(json.dumps({"facts": [
        {"key": "their_post", "statement": "Looking for a Shopify developer for Glow Skin, our store is slow", "evidence": "post"},
        {"key": "viewport", "statement": "The homepage does not set a mobile viewport meta tag.", "evidence": "no meta viewport"}]}))
    (folder / "OUTREACH-SEQUENCE.md").write_text("We grew Glow Skin revenue 900% for 40 clients.")   # a draft: never evidence
    pipeline.set_stage(conn, "glowskin.com", "researched", "dossier")

    # 2. the sequence: approved once, evidence found automatically (dossier + profile proof), drafts ignored
    bad = outreach.approve(conn, "glowskin.com", "jane@glowskin.com",
                           [{"step": 1, "subject": "glow skin store", "body": BODY1.replace("Brew Co store in 4 weeks", "Glow Skin revenue 900% for 40 clients")}])
    assert not bad["approved"]
    steps = [{"step": 1, "subject": "glow skin store", "body": BODY1}, {"step": 2, "subject": "", "body": BODY2}]
    ok = outreach.approve(conn, "glowskin.com", "jane@glowskin.com", steps, today=date(2026, 11, 2))
    assert ok["approved"], ok

    # 3. day 0 send in THEIR morning, day 3 follow-up in the same thread
    r = outreach.run(conn, True, now=datetime(2026, 11, 2, 15, 0, tzinfo=timezone.utc), smtp=SMTP)   # 10:00 New York
    assert len(r["sent"]) == 1 and r["sent"][0]["next_due"] == "2026-11-05"
    conn.execute("UPDATE touches SET at = '2026-11-02T15:00:00+00:00'")
    r = outreach.run(conn, True, now=datetime(2026, 11, 5, 15, 0, tzinfo=timezone.utc), smtp=SMTP)
    assert len(r["sent"]) == 1 and SMTP.sent[1]["In-Reply-To"] == SMTP.sent[0]["Message-ID"]

    # 4. reply "let's talk" → instant booking link (first time a link is allowed)
    reply = mail("jane@glowskin.com", "Re: glow skin store", "Yes! Can we talk Thursday 11am?", "<r1@glow>",
                 in_reply_to=SMTP.sent[1]["Message-ID"])
    out = inbox.check(conn, [reply], apply=True, auto_reply=True, smtp=SMTP, now=datetime(2026, 11, 5, 16, tzinfo=timezone.utc))
    assert out["auto_replies"][0]["sent"], out
    assert "https://cal.com/ravi/20min" in SMTP.sent[-1].get_content()

    # 5. she books through Cal.com → meeting recorded, prep scheduled, nothing manual
    note = mail("bookings@cal.com", "New Event: Jane Doe - 20 min", "Jane Doe (jane@glowskin.com) booked a 20 min meeting.",
                "<cal1@cal.com>", name="Cal.com",
                ics="BEGIN:VCALENDAR\r\nMETHOD:REQUEST\r\nBEGIN:VEVENT\r\nDTSTART;TZID=America/New_York:20261112T110000\r\n"
                    "DTEND;TZID=America/New_York:20261112T112000\r\nSUMMARY:Intro call\r\nATTENDEE;CN=Jane:mailto:jane@glowskin.com\r\n"
                    "ORGANIZER:mailto:ravi@pixelcraft.io\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")
    out = inbox.check(conn, [note], apply=True)
    assert out["bookings"][0]["start_utc"] == "2026-11-12T16:00:00+00:00"
    m = meeting.listing(conn)[0]
    assert m["minutes"] == 20 and pipeline.get(conn, "glowskin.com")["stage"] == "meeting"
    assert pipeline.get(conn, "glowskin.com")["next_due"] == "2026-11-11"

    # 6. meeting held → value → proposal → won → forecast
    meeting.outcome(conn, m["id"], "held", "wants a rebuild, budget ~$6k")
    pipeline.set_value(conn, "glowskin.com", 6000, "usd")
    pipeline.set_stage(conn, "glowskin.com", "proposal", "sent")
    assert pipeline.report(conn)["forecast"]["USD"] == {"open": 6000.0, "weighted": 3000.0, "won": 0.0, "deals_with_value": 1}
    pipeline.set_stage(conn, "glowskin.com", "won", "signed")
    rep = pipeline.report(conn)
    assert rep["forecast"]["USD"]["won"] == 6000.0 and rep["conversion"]["meeting_rate_pct"] == 100.0
    conn.close()


# ------------------------------------------------------------------ the fixes, one by one

def test_drafts_are_never_evidence():
    Path("prospects/a.com").mkdir(parents=True)
    Path("prospects/a.com/OUTREACH-SEQUENCE.md").write_text("We grew your traffic 300% in 2 weeks.")
    Path("prospects/a.com/notes.md").write_text("Their homepage has no contact form.")
    src = claim_check.load_sources(["prospects/a.com/*.md"], [], profile=False)
    r = claim_check.check("We grew your traffic 300% in 2 weeks.", src)
    assert not r["ok"] and any("OUTREACH-SEQUENCE" in x for x in r["drafts_not_used_as_evidence"])
    assert claim_check.check("I noticed your homepage has no contact form.", src)["ok"]


def test_profile_proof_supports_claims_about_you_only_when_real():
    src = claim_check.load_sources([], [])
    assert claim_check.check("We rebuilt the Brew Co store in 4 weeks.", src)["ok"]
    assert not claim_check.check("We rebuilt 300 stores for Nike in 2 weeks.", src)["ok"]


def test_warmup_ramp(monkeypatch):
    monkeypatch.setenv("DAILY_SEND_LIMIT", "40")
    monkeypatch.setenv("SENDING_STARTED", "2026-11-02")
    assert outreach.daily_limit(datetime(2026, 11, 3, tzinfo=timezone.utc)) == 5       # weeks 1-2
    assert outreach.daily_limit(datetime(2026, 11, 10, tzinfo=timezone.utc)) == 5
    assert outreach.daily_limit(datetime(2026, 11, 17, tzinfo=timezone.utc)) == 10      # week 3: +5 per week
    assert outreach.daily_limit(datetime(2027, 3, 1, tzinfo=timezone.utc)) == 40


def test_agenda_tells_each_lead_its_exact_next_step():
    c = pipeline.connect()
    for d, score in (("a.com", 90), ("b.com", 80), ("c.com", 70)):
        pipeline.add(c, url=f"https://{d}")
        pipeline.set_score(c, d, score)
    with c:
        c.execute("INSERT INTO artifacts(prospect_id, kind, path, created_at) VALUES (2, 'dossier', 'x', 'now')")
        c.execute("INSERT INTO artifacts(prospect_id, kind, path, created_at) VALUES (3, 'dossier', 'y', 'now')")
    pipeline.set_stage(c, "b.com", "researched")
    pipeline.set_stage(c, "c.com", "researched")
    pipeline.add_contact(c, "c.com", "Tom", email="tom@c.com", email_status="verified")
    items = {i["prospect"]: i for i in pipeline.today_agenda(c)["items"] if i["kind"] == "new-lead"}
    assert "Deep scan" in items["a.com"]["action"]
    assert items["b.com"]["skill"] == "vintoria-prospect-research"
    assert items["c.com"]["skill"] == "vintoria-outreach" and "tom@c.com" in items["c.com"]["action"]
    c.close()


def test_official_apollo_api(monkeypatch):
    with pytest.raises(lead_sources.UserError):
        lead_sources.apollo_api({"person_titles": ["Founder"]})
    monkeypatch.setenv("APOLLO_API_KEY", "apollo_test_key_1")
    seen = []

    def call(method, url, headers=None, body=None, **kw):
        seen.append(body)
        assert url == "https://api.apollo.io/api/v1/mixed_people/api_search" and headers == {"X-Api-Key": "apollo_test_key_1"}
        return 200, {"people": [{"first_name": "Jane", "last_name": "Doe", "title": "Founder",
                                 "organization": {"name": "Glow Skin", "website_url": "http://glowskin.com"}}]}
    rows = lead_sources.apollo_api({"person_titles": ["Founder"], "person_locations": ["United States"]}, 50, call=call)
    assert rows[0]["company"] == "Glow Skin" and seen[0]["per_page"] == 50 and seen[0]["page"] == 1
    import query_library
    f = query_library.from_profile(PROFILE)["apollo_api"]
    assert f["person_titles"] == ["Founder"] and f["person_locations"] == ["United States"] and f["q_organization_keyword_tags"]


def test_ics_parsing_and_cancelled_invites():
    ics = ("BEGIN:VCALENDAR\r\nMETHOD:REQUEST\r\nBEGIN:VEVENT\r\nDTSTART:20261112T160000Z\r\nDTEND:20261112T163000Z\r\n"
           "ATTENDEE;CN=A:mailto:a@x.com\r\nSTATUS:CONFIRMED\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")
    r = inbox.parse_ics(ics)
    assert r["start_utc"].isoformat() == "2026-11-12T16:00:00+00:00" and r["minutes"] == 30 and r["attendees"] == ["a@x.com"]
    c = pipeline.connect()
    pipeline.add(c, url="https://x.com")
    pipeline.add_contact(c, "x.com", "A", email="a@x.com", email_status="verified")
    cancelled = inbox.parse(mail("a@x.com", "Cancelled: call", "cancelled", "<c1@x>", ics=ics.replace("CONFIRMED", "CANCELLED")))
    assert inbox.booking_of(c, cancelled) is None
    c.close()


def test_hedged_consequence_is_opinion_unhedged_must_be_proven():
    src = claim_check.load_sources([], ["The homepage does not set a mobile viewport meta tag."], profile=False)
    assert claim_check.check("Your homepage has no mobile viewport tag, so phone visitors may see the desktop layout.", src)["ok"]
    assert not claim_check.check("Your homepage has no mobile viewport tag, so you are losing 40% of sales.", src)["ok"]


def test_signature_address_is_not_a_false_claim():
    src = claim_check.load_sources([], [])
    assert claim_check.check("Ravi Sharma\n12 MG Road, Pune", src)["ok"]


def test_command_checker_catches_wrong_flags(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("vs", Path(__file__).resolve().parents[1] / "tools" / "validate_skills.py")
    vs = importlib.util.module_from_spec(spec); spec.loader.exec_module(vs)
    d = tmp_path / "fake-skill"; d.mkdir()
    (d / "SKILL.md").write_text("Run `python <SCRIPTS>/core/pipeline.py add --url x --colour red` then "
                                "`python <SCRIPTS>/outreach/outreach.py teleport acme.com`.", encoding="utf-8")
    probs = vs.check_commands(d)
    assert any("--colour" in p for p in probs) and any("teleport" in p for p in probs)


def test_platform_leads_never_merge():
    c = pipeline.connect()
    a = pipeline.add(c, url="https://www.linkedin.com/posts/anita-desai_need-site-1", name="Anita Desai")["prospect"]
    b = pipeline.add(c, url="https://www.linkedin.com/posts/bob-lee_seo-2", name="Bob Lee")["prospect"]
    h = pipeline.add(c, url="https://news.ycombinator.com/item?id=4242")["prospect"]
    r = pipeline.add(c, url="https://www.reddit.com/r/forhire/comments/abc123/hiring/")["prospect"]
    assert [a["slug"], b["slug"], h["slug"], r["slug"]] == ["anita-desai@linkedin", "bob-lee@linkedin", "post-4242@hn", "post-abc123@reddit"]
    assert a["url"].startswith("https://www.linkedin.com/posts/") and pipeline.get(c, "anita-desai@linkedin")["name"] == "Anita Desai"
    assert pipeline.add(c, url="https://glowskin.com")["prospect"]["slug"] == "glowskin.com"
    pipeline.add_contact(c, "bob-lee@linkedin", "Bob Lee", email="bob@leeco.com")
    assert [m["slug"] for m in pipeline.find(c, "bob@leeco.com")] == ["bob-lee@linkedin"]
    assert [m["slug"] for m in pipeline.find(c, "Anita")] == ["anita-desai@linkedin"]
    c.close()
    import prospect_scan
    with pytest.raises(ValueError):
        prospect_scan.scan("https://www.linkedin.com/posts/anita-desai_need-site-1", web=False, record=False)


def test_doctor_modes_and_approve_check(monkeypatch):
    assert outreach.doctor()["mode"] == "manual"
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "app-password-123")
    d = outreach.doctor()
    assert d["mode"] == "autopilot" and d["checks"]["imap_reply_detection"]          # IMAP derived from SMTP + profile email
    c = pipeline.connect()
    pipeline.add(c, url="https://glowskin.com")
    pipeline.add_contact(c, "glowskin.com", "Jane", email="jane@glowskin.com", email_status="verified")
    folder = Path("prospects/glowskin.com"); folder.mkdir(parents=True)
    (folder / "DOSSIER.json").write_text(json.dumps({"facts": [
        {"key": "their_post", "statement": "Looking for a Shopify developer for Glow Skin", "evidence": "post"},
        {"key": "viewport", "statement": "The homepage does not set a mobile viewport meta tag.", "evidence": "x"}]}))
    r = outreach.approve(c, "glowskin.com", "jane@glowskin.com", [{"step": 1, "subject": "glow skin store", "body": BODY1}],
                         check_only=True)
    assert r["check_passed"] and not outreach.queue(c, "glowskin.com")              # checked, nothing queued
    c.close()

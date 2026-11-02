#!/usr/bin/env python3
"""
Meeting booking: propose free slots in both time zones, create a calendar invite (.ics) that works in
Google Calendar, Outlook and Apple Calendar, track meetings in the pipeline and record what happened.

Usage (every command prints one JSON object):
    python meeting.py slots --prospect-tz America/New_York [--count 3] [--minutes 30] [--days 7]
    python meeting.py book acme.com --start "2026-11-04 11:00" [--tz Asia/Kolkata] [--minutes 30] \
        --attendee priya@acme.com [--attendee-name "Priya Mehta"] [--link https://meet.google.com/...] \
        [--agenda "Website plan for Acme"] [--prospect-tz America/New_York] [--out prospects/acme.com/MEETING-2026-11-04.ics]
    python meeting.py list [--all]
    python meeting.py outcome 3 held --notes "Wants 3-page site, budget ~₹60k, decides Friday"
    python meeting.py outcome 3 no_show | rescheduled | cancelled

Your settings (in ~/.ai-sales-team/.env, all optional):
    TIMEZONE=Asia/Kolkata        WORK_HOURS=10:00-18:00     WORK_DAYS=Mon-Fri    MEETING_MINUTES=30
    BOOKING_URL=https://cal.com/you/15min    MEETING_LINK=https://meet.google.com/xxx-xxxx-xxx
    SENDER_NAME=...   SENDER_EMAIL=...
Slots avoid meetings already booked here, the next 2 hours, and land inside 09:00-18:00 for the prospect too.
"""

import argparse
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import outreach  # noqa: E402
import pipeline  # noqa: E402
from sales_common import emit, setting  # noqa: E402

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover - Python < 3.9
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
TZ_ALIASES = {"ist": "Asia/Kolkata", "india": "Asia/Kolkata", "est": "America/New_York", "edt": "America/New_York",
              "et": "America/New_York", "cst": "America/Chicago", "ct": "America/Chicago", "mst": "America/Denver",
              "pst": "America/Los_Angeles", "pdt": "America/Los_Angeles", "pt": "America/Los_Angeles",
              "gmt": "Europe/London", "bst": "Europe/London", "uk": "Europe/London", "cet": "Europe/Berlin",
              "aest": "Australia/Sydney", "aedt": "Australia/Sydney", "sydney": "Australia/Sydney",
              "melbourne": "Australia/Melbourne", "perth": "Australia/Perth", "gst": "Asia/Dubai", "dubai": "Asia/Dubai",
              "sgt": "Asia/Singapore", "utc": "UTC"}
STATUSES = ["scheduled", "held", "no_show", "rescheduled", "cancelled"]
PROSPECT_HOURS = (9, 18)


class UserError(Exception):
    pass


def tz(name):
    if ZoneInfo is None:
        raise UserError("time zones need Python 3.9+")
    key = TZ_ALIASES.get((name or "").strip().lower(), (name or "").strip())
    try:
        return ZoneInfo(key)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        raise UserError(f"unknown time zone '{name}' — use an IANA name like Asia/Kolkata, America/New_York, "
                        "Europe/London, Australia/Sydney (on Windows: pip install tzdata)")


def _hours(spec):
    m = re.fullmatch(r"\s*(\d{1,2})(?::(\d{2}))?\s*-\s*(\d{1,2})(?::(\d{2}))?\s*", spec or "")
    if not m:
        raise UserError(f"WORK_HOURS '{spec}' must look like 10:00-18:00")
    start = int(m.group(1)) * 60 + int(m.group(2) or 0)
    end = int(m.group(3)) * 60 + int(m.group(4) or 0)
    if not 0 <= start < end <= 24 * 60:
        raise UserError(f"WORK_HOURS '{spec}' is not a valid range")
    return start, end


def _days(spec):
    s = (spec or "mon-fri").lower().replace(" ", "")
    out = set()
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            i, j = DAYS.index(a[:3]), DAYS.index(b[:3])
            out.update(range(i, j + 1) if i <= j else list(range(i, 7)) + list(range(0, j + 1)))
        elif part:
            out.add(DAYS.index(part[:3]))
    return out


def busy(conn):
    out = []
    for r in conn.execute("SELECT starts_at, minutes FROM meetings WHERE status = 'scheduled'"):
        s = datetime.fromisoformat(r["starts_at"])
        out.append((s, s + timedelta(minutes=r["minutes"])))
    return out


def fmt(dt):
    return dt.strftime("%a %d %b, ") + dt.strftime("%I:%M %p").lstrip("0") + " " + (dt.tzname() or "")


def _scan(day0, days, wd, start_min, end_min, minutes, theirs, earliest, taken, step):
    per_day = {}
    day = day0
    for _ in range(days + 1):
        if day.weekday() in wd:
            t = start_min
            while t + minutes <= end_min:
                s = day.replace(hour=t // 60, minute=t % 60)
                e = s + timedelta(minutes=minutes)
                ts, te = s.astimezone(theirs), e.astimezone(theirs)
                if (s >= earliest and ts.weekday() < 5 and PROSPECT_HOURS[0] * 60 <= ts.hour * 60 + ts.minute
                        and te.hour * 60 + te.minute <= PROSPECT_HOURS[1] * 60 and ts.date() == te.date()
                        and not any(s < b_end and e > b_start for b_start, b_end in taken)):
                    per_day.setdefault(s.date(), []).append(s)
                t += step
        day = (day + timedelta(days=1)).replace(hour=0, minute=0)
    return per_day


def _pick(per_day, count, key, found):
    for d in sorted(per_day):                     # one slot per day first, the best by `key`
        if len(found) >= count:
            break
        best = min(per_day[d], key=key)
        if best not in found:
            found.append(best)
    for d in sorted(per_day):
        for s in per_day[d]:
            if len(found) >= count:
                return found
            if s not in found:
                found.append(s)
    return found


def propose(conn, prospect_tz, count=2, minutes=None, days=7, now=None, my_tz=None, hours=None, workdays=None, step=30):
    mine = tz(my_tz or setting("TIMEZONE", "Asia/Kolkata"))
    theirs = tz(prospect_tz) if prospect_tz else mine
    minutes = int(minutes or setting("MEETING_MINUTES", "30"))
    start_min, end_min = _hours(hours or setting("WORK_HOURS", "10:00-18:00"))
    ext_start, ext_end = _hours(setting("EXTENDED_HOURS", "07:00-23:00"))
    wd = _days(workdays or setting("WORK_DAYS", "Mon-Fri"))
    now = (now or datetime.now(timezone.utc)).astimezone(mine)
    earliest = now + timedelta(hours=2)
    taken = busy(conn) if conn is not None else []
    day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
    found = _pick(_scan(day0, days, wd, start_min, end_min, minutes, theirs, earliest, taken, step), count,
                  lambda s: abs(s.astimezone(theirs).hour - 11), [])          # mid-morning for them
    normal = set(found)
    if len(found) < count:
        # time zones barely overlap (e.g. India <-> US): stretch YOUR day, never the prospect's
        found = _pick(_scan(day0, days, wd, min(ext_start, start_min), max(ext_end, end_min), minutes, theirs, earliest,
                            taken, step), count,
                      lambda s: max(start_min - (s.hour * 60 + s.minute), (s.hour * 60 + s.minute) - end_min, 0), found)
    found.sort()
    slots = [{"start_utc": s.astimezone(timezone.utc).isoformat(), "yours": fmt(s), "theirs": fmt(s.astimezone(theirs)),
              "minutes": minutes, "outside_your_work_hours": s not in normal} for s in found[:count]]
    booking = setting("BOOKING_URL")
    lines = [f"- {x['theirs']}" + (f" ({x['yours']} for me)" if prospect_tz and theirs.key != mine.key else "") for x in slots]
    msg = (f"Would one of these work for a quick {minutes}-minute call?\n" + "\n".join(lines) +
           (f"\nOr pick any time that suits you here: {booking}" if booking else "") +
           "\nIf none fit, tell me a time that does and I'll make it work.")
    note = None
    if not slots:
        note = "No free slot found — widen --days, WORK_HOURS or EXTENDED_HOURS."
    elif any(x["outside_your_work_hours"] for x in slots):
        note = "Some slots are outside your WORK_HOURS (little overlap with their time zone) — confirm you can do them."
    out = {"your_tz": mine.key, "prospect_tz": theirs.key, "slots": slots, "message": msg, "note": note}
    try:   # remembered so the claim checker can verify the times written in a reply
        from sales_common import data_home
        import json as _json
        (data_home() / "last_slots.json").write_text(_json.dumps(out), encoding="utf-8")
    except OSError:
        pass
    return out


def parse_start(start, zone):
    s = (start or "").strip().replace("T", " ")
    for f in ("%Y-%m-%d %H:%M", "%Y-%m-%d %I:%M %p", "%Y-%m-%d %I %p", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s.upper(), f).replace(tzinfo=zone)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(start)
        return dt if dt.tzinfo else dt.replace(tzinfo=zone)
    except ValueError:
        raise UserError(f"--start '{start}' must look like 2026-11-04 11:00 (24h) or 2026-11-04 4:30 PM")


def _esc(v):
    return (v or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r\n", "\\n").replace("\n", "\\n")


def _fold(line):
    raw, out = line.encode("utf-8"), []
    while len(raw) > 75:
        cut = 75 if not out else 74
        while cut > 0 and (raw[cut] & 0xC0) == 0x80:  # don't split a UTF-8 character
            cut -= 1
        out.append(raw[:cut].decode("utf-8"))
        raw = raw[cut:]
    out.append(raw.decode("utf-8"))
    return "\r\n ".join(out)


def ics(uid, start_utc, minutes, title, description, organizer_email=None, organizer_name=None, attendee=None,
        attendee_name=None, location=None, method="REQUEST", sequence=0, status="CONFIRMED"):
    z = lambda d: d.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")  # noqa: E731
    end = start_utc + timedelta(minutes=minutes)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AI Sales Team//meeting.py//EN", "CALSCALE:GREGORIAN",
             f"METHOD:{method}", "BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{z(datetime.now(timezone.utc))}",
             f"DTSTART:{z(start_utc)}", f"DTEND:{z(end)}", f"SUMMARY:{_esc(title)}", f"DESCRIPTION:{_esc(description)}",
             f"SEQUENCE:{sequence}", f"STATUS:{status}"]
    if location:
        lines += [f"LOCATION:{_esc(location)}", f"URL:{location}" if location.startswith("http") else ""]
    if organizer_email:
        lines.append(f"ORGANIZER;CN={_esc(organizer_name or organizer_email)}:mailto:{organizer_email}")
    if attendee:
        lines.append(f"ATTENDEE;CN={_esc(attendee_name or attendee)};ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{attendee}")
    lines += ["BEGIN:VALARM", "TRIGGER:-PT15M", "ACTION:DISPLAY", "DESCRIPTION:Reminder", "END:VALARM",
              "END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(_fold(x) for x in lines if x) + "\r\n"


def book(conn, key, start, zone_name=None, minutes=None, attendee=None, attendee_name=None, link=None, agenda=None,
         out=None, today=None, prospect_tz=None):
    p = pipeline.get(conn, key)
    zone = tz(zone_name or setting("TIMEZONE", "Asia/Kolkata"))
    st = parse_start(start, zone)
    now_dt = today or datetime.now(timezone.utc)
    if st < now_dt:
        raise UserError(f"{st.isoformat()} is in the past")
    minutes = int(minutes or setting("MEETING_MINUTES", "30"))
    clash = [b for b in busy(conn) if st < b[1] and st + timedelta(minutes=minutes) > b[0]]
    if clash:
        raise UserError(f"clashes with another meeting at {clash[0][0].isoformat()} — pick another slot")
    link = link or setting("MEETING_LINK")
    me = setting("SENDER_NAME")
    company = p["name"] or p["slug"]
    title = (f"{company} <> {me}" if me else f"{company} — intro call") + (f" — {agenda}" if agenda else "")
    desc = "\n".join(x for x in [agenda and f"Agenda: {agenda}", link and f"Join: {link}",
                                  "Reply to this email if you need to move it."] if x)
    uid = f"{uuid.uuid4()}@ai-sales-team"
    body = ics(uid, st, minutes, title, desc, setting("SENDER_EMAIL"), setting("SENDER_NAME"), attendee, attendee_name, link)
    path = Path(out or Path("prospects") / p["slug"] / f"MEETING-{st.date().isoformat()}.ics")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode("utf-8"))
    start_utc = st.astimezone(timezone.utc).replace(microsecond=0).isoformat()
    with conn:
        cur = conn.execute("INSERT INTO meetings(prospect_id, starts_at, minutes, tz, title, attendee, link, status, ics_path, "
                           "uid, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                           (p["id"], start_utc, minutes, (tz(prospect_tz) if prospect_tz else zone).key, title, attendee, link,
                            "scheduled", str(path), uid, pipeline.now()))
        conn.execute("INSERT OR REPLACE INTO artifacts(prospect_id, kind, path, created_at) VALUES (?,?,?,?)",
                     (p["id"], "meeting-invite", str(path), pipeline.now()))
    pipeline.set_stage(conn, p["slug"], "meeting", f"meeting booked for {start_utc}")
    outreach.stop(conn, p["slug"], "meeting booked")
    prep_due = (st - timedelta(days=1)).date().isoformat()
    with conn:
        conn.execute("UPDATE prospects SET next_action = ?, next_due = ? WHERE id = ?",
                     ("Prep the meeting brief (sales-prep) and send a reminder the day before", prep_due, p["id"]))
    yours = fmt(st)
    their_dt = st.astimezone(tz(prospect_tz)) if prospect_tz else st
    their = fmt(their_dt)
    warn = None
    if prospect_tz and not (PROSPECT_HOURS[0] <= their_dt.hour < PROSPECT_HOURS[1] and their_dt.weekday() < 5):
        warn = f"{their} is outside normal business hours for the prospect — double-check this is the time they asked for."
    return {"meeting_id": cur.lastrowid, "prospect": p["slug"], "start_utc": start_utc, "start_yours": yours,
            "start_theirs": their,
            "minutes": minutes, "ics": str(path), "link": link, "warning": warn,
            "confirmation_message": f"Booked: {their} ({minutes} min)." + (f" Link: {link}." if link else "") +
                                    " I've attached a calendar invite — reply if you need to move it.",
            "reminder_message": f"Looking forward to our call at {their}. "
                                + (f"Join here: {link}. " if link else "") + "Anything specific you'd like me to look at before then?",
            "next": [f"Send the confirmation with {path.name} attached (the user sends it)",
                     f"Run sales-prep before {prep_due}", "After the call: meeting.py outcome <id> held --notes ..."]}


def outcome(conn, meeting_id, status, notes=""):
    if status not in STATUSES[1:]:
        raise UserError(f"outcome must be one of {STATUSES[1:]}")
    m = conn.execute("SELECT * FROM meetings WHERE id = ?", (int(meeting_id),)).fetchone()
    if not m:
        raise UserError(f"meeting {meeting_id} not found (meeting.py list)")
    p = conn.execute("SELECT * FROM prospects WHERE id = ?", (m["prospect_id"],)).fetchone()
    with conn:
        conn.execute("UPDATE meetings SET status = ?, notes = COALESCE(notes, '') || ? WHERE id = ?",
                     (status, f"\n{status}: {notes}" if notes else f"\n{status}", m["id"]))
        pipeline.event(conn, p["id"], "meeting", f"meeting #{m['id']} {status}" + (f": {notes}" if notes else ""))
    today = datetime.now(timezone.utc).date()
    prior_no_shows = conn.execute("SELECT COUNT(*) FROM meetings WHERE prospect_id = ? AND status = 'no_show' AND id != ?",
                                  (p["id"], m["id"])).fetchone()[0]
    plan = {"held": ("Send recap + proposal within 24-48h (sales-followup post-meeting, then sales-proposal); "
                     "set the deal value: pipeline.py value <slug> <amount> --currency USD", 1),
            "no_show": ("Send a friendly 'sorry we missed each other' with 2 new slots (meeting.py slots)", 0),
            "rescheduled": ("Book the new time: meeting.py book ...", 0),
            "cancelled": ("Ask whether to rebook later; otherwise move to nurture", 2)}[status]
    if status == "no_show" and prior_no_shows >= 1:      # second no-show: stop chasing, back to nurture
        plan = ("Second no-show — moved to nurture; one friendly note, then check back in a month", 0)
        pipeline.set_stage(conn, p["slug"], "nurture", "second no-show")
    elif status == "no_show":
        plan = ("No-show: send a warm 'sorry we missed each other' TODAY with 2 new times (meeting.py slots --count 2)", 0)
    due = outreach.add_business_days(today, plan[1]).isoformat() if plan[1] else today.isoformat()
    with conn:
        conn.execute("UPDATE prospects SET next_action = ?, next_due = ?, updated_at = ? WHERE id = ?",
                     (plan[0], due, pipeline.now(), p["id"]))
    return {"meeting_id": m["id"], "prospect": p["slug"], "status": status, "next_action": plan[0], "due": due,
            "suggested_stage": "proposal" if status == "held" else None}


def listing(conn, all_=False):
    q = ("SELECT m.id, p.slug AS prospect, m.starts_at, m.minutes, m.tz, m.attendee, m.status, m.link, m.ics_path "
         "FROM meetings m JOIN prospects p ON p.id = m.prospect_id")
    if not all_:
        q += " WHERE m.status = 'scheduled'"
    out = []
    for r in conn.execute(q + " ORDER BY m.starts_at"):
        d = dict(r)
        try:
            d["local"] = fmt(datetime.fromisoformat(d["starts_at"]).astimezone(tz(d["tz"])))
        except UserError:
            pass
        out.append(d)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Propose slots, book meetings with .ics invites, record outcomes.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sl = sub.add_parser("slots"); sl.add_argument("--prospect-tz"); sl.add_argument("--count", type=int, default=2)
    sl.add_argument("--minutes", type=int); sl.add_argument("--days", type=int, default=7)
    bk = sub.add_parser("book"); bk.add_argument("prospect"); bk.add_argument("--start", required=True); bk.add_argument("--tz")
    bk.add_argument("--minutes", type=int); bk.add_argument("--attendee"); bk.add_argument("--attendee-name")
    bk.add_argument("--link"); bk.add_argument("--agenda"); bk.add_argument("--out")
    bk.add_argument("--prospect-tz", help="show the time in the prospect's zone in the messages")
    ls = sub.add_parser("list"); ls.add_argument("--all", action="store_true")
    oc = sub.add_parser("outcome"); oc.add_argument("meeting_id"); oc.add_argument("status", choices=STATUSES[1:])
    oc.add_argument("--notes", default="")
    a = ap.parse_args(argv)
    conn = pipeline.connect()
    try:
        if a.cmd == "slots":
            out = propose(conn, a.prospect_tz, a.count, a.minutes, a.days)
        elif a.cmd == "book":
            out = book(conn, a.prospect, a.start, a.tz, a.minutes, a.attendee, a.attendee_name, a.link, a.agenda, a.out,
                       prospect_tz=a.prospect_tz)
        elif a.cmd == "list":
            out = {"meetings": listing(conn, a.all)}
        else:
            out = outcome(conn, a.meeting_id, a.status, a.notes)
        emit({"ok": True, "data": out})
    except (UserError, pipeline.UserError) as exc:
        emit({"ok": False, "error": str(exc)}, 2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

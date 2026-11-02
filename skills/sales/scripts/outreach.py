#!/usr/bin/env python3
"""
Outreach execution: log every touch, run the follow-up cadence, optionally send email over SMTP with hard
safety gates, and build WhatsApp click-to-chat links. Writes to the same pipeline database as pipeline.py.

Usage (every command prints one JSON object):
    python outreach.py log acme.com --channel email --step 1 --to priya@acme.com --subject "Quick idea"
    python outreach.py log acme.com --channel linkedin --note "connection request with note"
    python outreach.py cadence                         # show the follow-up schedule in use
    python outreach.py stop acme.com --reason "replied" # cancel pending follow-ups
    python outreach.py send acme.com --to priya@acme.com --subject "Quick idea" --body-file email1.txt \
        --evidence "prospects/acme.com/*.md" [--evidence-text "<their post>"] [--step 1]     # dry run (preview)
    python outreach.py send ... --send                 # really send — only after the user approved THIS email
    python outreach.py whatsapp +91 98100 00000 --text-file msg.txt [--prospect acme.com]

  Approved sequences (send themselves on schedule until the prospect replies):
    python outreach.py approve acme.com --to priya@acme.com --file prospects/acme.com/SEQUENCE.json \
        --evidence "prospects/acme.com/*.md" --evidence prospects/acme.com/SITE-AUDIT.json [--start 2026-11-03]
    python outreach.py approve ... --check             # validate every email of the sequence, queue nothing
    python outreach.py doctor                          # is sending ready? which mode: autopilot / send-one-by-one / manual
    python outreach.py queue [acme.com]                # what is approved and when each email is due
    python outreach.py run                             # dry run: what would go out now
    python outreach.py run --send [--limit 20]         # send every due, still-valid step (cron/Task Scheduler)
    python outreach.py cancel acme.com                 # cancel the rest of a sequence

Cadence: follow-ups on day 3, 7, 14 and 28 after email 1 (calendar days; a weekend date moves to Monday) —
5 emails, the last a polite breakup. Override with CADENCE_DAYS=3,7,14,28 in ~/.ai-sales-team/.env.
Sequence file: JSON list [{"step": 1, "subject": "...", "body": "..."}, ...] or Markdown with "## Email 1"
headings and a "Subject: ..." line. Follow-ups are sent as replies in the same thread ("Re: <subject 1>").
Booking links (BOOKING_URL, Calendly, Cal.com, ...) are refused until the prospect has replied with
interest: the link goes out only when they're ready to talk.

Sending gates (all must pass, otherwise nothing is sent):
  - --send given (default is a dry-run preview), SMTP_HOST/SMTP_USER/SMTP_PASSWORD/SENDER_EMAIL configured;
  - recipient is on file with email_status=verified (catch_all only with --allow-catch-all; never
    pattern-guessed / unverified / invalid), and neither the address nor its domain is suppressed;
  - the body passes claim_check.py against the evidence you give, has no [PLACEHOLDER], has an opt-out line,
    and (cold email to the US) the SENDER_ADDRESS postal address;
  - today's sends are under DAILY_SEND_LIMIT (default 30) and this prospect wasn't emailed in the last 2 days;
  - no booking link before the prospect has shown interest (see above).
Queued emails go out only inside SEND_HOURS (default 09:00-17:00) on weekdays in the PROSPECT's time zone
(their tz → their country → PROSPECT_DEFAULT_TZ → your first target country), so a US prospect gets it in
their morning, not yours.
Plain text only, no tracking pixels, List-Unsubscribe header set.
"""

import argparse
import json
import re
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claim_check  # noqa: E402
import email_lint  # noqa: E402
import mailboxes  # noqa: E402
import pipeline  # noqa: E402
from sales_common import emit, secret, setting, tls_context  # noqa: E402

CHANNELS = ["email", "linkedin", "whatsapp", "call", "sms", "other"]
DEFAULT_CADENCE = [3, 7, 14, 28]
BOOKING_RE = re.compile(r"(calendly\.com|cal\.com/|savvycal\.com|tidycal\.com|zcal\.co|meetings\.hubspot\.com|"
                        r"calendar\.app\.google|calendar\.google\.com/calendar/appointments|outlook\.office\.com/bookwithme|"
                        r"youcanbook\.me|koalendar\.com|doodle\.com/bp)", re.I)
READY_STAGES = ("replied", "meeting", "proposal", "won")
READY_REPLIES = ("meeting_request", "interested", "question", "referral", "objection_price", "objection_has_vendor")
OPT_OUT = re.compile(r"(reply\s+['\"“]?(no|stop|unsubscribe)|not\s+relevant\?|won'?t\s+(follow\s+up|email)|unsubscribe|opt[\s-]?out|"
                     r"let me know if you'?d rather not|mat bhejo|nahi chahiye to bata)", re.I)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)


class UserError(Exception):
    pass


def cadence():
    """Day offsets after email 1 for each follow-up (strictly increasing), default 3, 7, 14, 28."""
    raw = setting("CADENCE_DAYS")
    if raw:
        try:
            days = [int(x) for x in raw.replace(" ", "").split(",") if x]
            if days and all(d > 0 for d in days) and days == sorted(set(days)):
                return days
        except ValueError:
            pass
    return list(DEFAULT_CADENCE)


def weekday_on_or_after(d):
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def followup_due(first_date, step, today=None):
    """Due date of the email after `step` (1 = email 1 was just sent), or None when the sequence is done."""
    offs = cadence()
    if step < 1 or step > len(offs):
        return None
    due = weekday_on_or_after(first_date + timedelta(days=offs[step - 1]))
    floor = (today or first_date) + timedelta(days=1)
    return max(due, weekday_on_or_after(floor))


def _first_email_date(conn, pid):
    r = conn.execute("SELECT MIN(at) FROM touches WHERE prospect_id = ? AND channel = 'email' AND status IN ('sent','logged')",
                     (pid,)).fetchone()[0]
    return datetime.fromisoformat(r).date() if r else None


def ready_for_link(conn, p):
    """True once the prospect has replied with interest (or the deal is past 'replied')."""
    if p["stage"] in READY_STAGES:
        last = conn.execute("SELECT text FROM events WHERE prospect_id = ? AND kind = 'reply' ORDER BY id DESC LIMIT 1",
                            (p["id"],)).fetchone()
        if p["stage"] != "replied" or not last:
            return True
        m = re.match(r"\[(\w+)\]", last["text"] or "")
        return (m.group(1) if m else "") in READY_REPLIES
    return False


def has_booking_link(body):
    url = setting("BOOKING_URL")
    return bool(BOOKING_RE.search(body or "") or (url and url.lower().rstrip("/") in (body or "").lower()))


def add_business_days(start, n):
    d = start
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def _touch_count(conn, pid, channel="email"):
    return conn.execute("SELECT COUNT(*) FROM touches WHERE prospect_id = ? AND channel = ? AND status IN ('sent','logged')",
                        (pid, channel)).fetchone()[0]


def log_touch(conn, key, channel, step=None, to=None, subject=None, body_path=None, note=None, status="logged",
              message_id=None, schedule=True, today=None, sender=None):
    if channel not in CHANNELS:
        raise UserError(f"channel must be one of {CHANNELS}")
    p = pipeline.get(conn, key)
    if step is None and channel == "email":
        step = _touch_count(conn, p["id"]) + 1
    ts = pipeline.now()
    first_before = _first_email_date(conn, p["id"])
    out = {"prospect": p["slug"], "channel": channel, "step": step, "status": status}
    with conn:
        conn.execute("INSERT INTO touches(prospect_id, channel, step, recipient, subject, body_path, status, message_id, at, sender) "
                     "VALUES (?,?,?,?,?,?,?,?,?,?)", (p["id"], channel, step, to, subject, body_path, status, message_id, ts,
                                                      (sender or "").lower() or None))
        pipeline.event(conn, p["id"], "touch", f"{channel}" + (f" #{step}" if step else "") + (f" to {to}" if to else "")
                       + (f": {subject}" if subject else "") + (f" — {note}" if note else ""))
        if p["stage"] in ("new", "researched", "qualified"):
            conn.execute("UPDATE prospects SET stage = 'contacted' WHERE id = ?", (p["id"],))
            pipeline.event(conn, p["id"], "stage", f"first {channel} touch", p["stage"], "contacted")
            out["stage"] = "contacted"
        if schedule and channel == "email" and p["stage"] in ("new", "researched", "qualified", "contacted", "nurture"):
            base = today or datetime.now(timezone.utc).date()
            first = base if (step == 1 or not first_before) else first_before
            nd = followup_due(first, step or 1, base)
            offs = cadence()
            if nd:
                last = step == len(offs)
                due = nd.isoformat()
                action = (f"Send follow-up #{step} (day {offs[step - 1]}" + (", final polite breakup)" if last else ")")) + \
                         " — new value, not 'just checking in'"
            else:
                due = (base + timedelta(days=30)).isoformat()
                action = "Sequence finished with no reply — move to nurture (stage nurture) or lost"
            conn.execute("UPDATE prospects SET next_action = ?, next_due = ? WHERE id = ?", (action, due, p["id"]))
            pipeline.event(conn, p["id"], "next", f"{action} (due {due})")
            out["next_action"], out["next_due"] = action, due
        pipeline.touch(conn, p["id"])
    return out


def stop(conn, key, reason=""):
    p = pipeline.get(conn, key)
    with conn:
        conn.execute("UPDATE prospects SET next_action = NULL, next_due = NULL, updated_at = ? WHERE id = ?",
                     (pipeline.now(), p["id"]))
        pipeline.event(conn, p["id"], "cadence", f"follow-ups stopped: {reason}".strip(": "))
        n = conn.execute("UPDATE sequence_steps SET status = 'cancelled', note = ? WHERE prospect_id = ? AND status = 'approved'",
                         (reason, p["id"])).rowcount
    return {"prospect": p["slug"], "cadence": "stopped", "reason": reason, "queued_emails_cancelled": n}


def _contact(conn, pid, email):
    r = conn.execute("SELECT * FROM contacts WHERE prospect_id = ? AND lower(email) = lower(?)", (pid, email)).fetchone()
    return dict(r) if r else None


def stop_loss(conn, now_dt=None):
    """Deliverability stop-loss over the last 14 days: pause cold sends when bounces pass 2% (≥ 20 sends);
    warn when the reply rate stays under 1% after 300 sends (the targeting or offer is wrong, not the volume)."""
    now_dt = now_dt or datetime.now(timezone.utc)
    since = (now_dt - timedelta(days=14)).replace(microsecond=0).isoformat()
    sent = conn.execute("SELECT COUNT(*) FROM touches WHERE channel = 'email' AND status = 'sent' AND at >= ?", (since,)).fetchone()[0]
    bounces = conn.execute("SELECT COUNT(*) FROM events WHERE kind = 'reply' AND text LIKE '[bounce]%' AND at >= ?", (since,)).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM touches WHERE channel = 'email' AND status = 'sent'").fetchone()[0]
    replied = conn.execute("SELECT COUNT(DISTINCT prospect_id) FROM events WHERE kind = 'reply' AND text NOT LIKE '[bounce]%' "
                           "AND text NOT LIKE '[out_of_office]%'").fetchone()[0]
    out = {"sent_14d": sent, "bounces_14d": bounces, "bounce_rate_pct": round(100 * bounces / sent, 1) if sent else 0.0,
           "sent_total": total, "reply_rate_pct": round(100 * replied / total, 1) if total else None, "paused": False, "reason": None,
           "warning": None}
    limit = float(setting("BOUNCE_STOP_PCT", "2"))
    if sent >= 20 and out["bounce_rate_pct"] > limit:
        out["paused"] = True
        out["reason"] = (f"bounce rate {out['bounce_rate_pct']}% over the last {sent} sends (> {limit:g}%) — re-verify the "
                         "list (find_email.py --email) and check the domain before sending more")
    if total >= 300 and (out["reply_rate_pct"] or 0) < 1:
        out["warning"] = f"reply rate {out['reply_rate_pct']}% after {total} sends — change targeting/offer, more volume makes it worse"
    return out


def daily_limit(now_dt=None):
    """DAILY_SEND_LIMIT, ramped while a new inbox warms up (SENDING_STARTED=YYYY-MM-DD): 5/day in weeks 1-2, then +5 per
    week. Practitioners keep 20-30 cold sends per mailbox per day once warm."""
    if mailboxes._file().exists():
        return sum(mailboxes.limit_today(m, now_dt) for m in mailboxes.load()) or 0
    cap = int(setting("DAILY_SEND_LIMIT", "30"))
    start = setting("SENDING_STARTED")
    if start:
        try:
            weeks = max(0, ((now_dt or datetime.now(timezone.utc)).date() - datetime.fromisoformat(start).date()).days // 7)
            return min(cap, 5 if weeks < 2 else 5 + 5 * (weeks - 1))
        except ValueError:
            pass
    return cap


def preflight(conn, key, to, subject, body, evidence=None, evidence_text=None, allow_catch_all=False, today=None):
    """Every gate that must pass before an email may be sent. Returns (problems, info)."""
    problems, info = [], {}
    p = pipeline.get(conn, key)
    info["prospect"] = p["slug"]
    if not to or not EMAIL_RE.match(to):
        problems.append(f"'{to}' is not an email address")
    if not (subject or "").strip():
        problems.append("subject is empty")
    elif re.match(r"^\s*(re|fwd?)\s*:", subject, re.I) and not _touch_count(conn, p["id"]):
        problems.append("fake 'Re:'/'Fwd:' subject on a first email (illegal under CAN-SPAM, and spammy)")
    c = _contact(conn, p["id"], to or "")
    status = (c or {}).get("email_status")
    info["email_status"] = status or "not on file"
    if not c:
        problems.append(f"{to} is not a saved contact — save it first: pipeline.py contact {p['slug']} --name ... "
                        f"--email {to} --email-status <status>")
    elif status == "catch_all" and not allow_catch_all:
        problems.append("address is catch_all (may bounce) — pass --allow-catch-all only if the user accepts the risk")
    elif status not in ("verified", "catch_all"):
        problems.append(f"email status is '{status}' — only verified addresses are sent to (run find_email.py)")
    sup = pipeline.is_suppressed(conn, to or "")
    if sup:
        problems.append(f"{sup['value']} is on the do-not-contact list ({sup['reason'] or 'no reason'})")
    if p["stage"] in ("won", "lost", "disqualified"):
        problems.append(f"prospect stage is '{p['stage']}'")
    if not OPT_OUT.search(body or "") and p["stage"] in ("new", "researched", "qualified", "contacted", "nurture"):
        problems.append("no opt-out line (e.g. \"Not relevant? Reply 'no' and I won't follow up.\")")
    if has_booking_link(body) and not ready_for_link(conn, p):
        problems.append("booking link in an email to someone who hasn't shown interest yet — ask for a reply first; "
                        "send the link once they're ready (sales-reply / sales-book)")
    address = setting("SENDER_ADDRESS")
    if address and address.split(",")[0].strip().lower() not in (body or "").lower():
        problems.append("signature is missing your postal address (SENDER_ADDRESS) — required for US cold email")
    sources = claim_check.load_sources(evidence or [], evidence_text or [], slug=p["slug"])
    cc = claim_check.check(body, sources)
    info["claim_check"] = {"ok": cc["ok"], "checked": cc["checked"], "supported": cc["supported"]}
    if not cc["ok"]:
        problems.extend(f"unsupported claim: {u['text']}" for u in cc["unsupported"])
        problems.extend(f"placeholder not filled: {h}" for h in cc["placeholders"])
    now_dt = today or datetime.now(timezone.utc)
    cold = p["stage"] in ("new", "researched", "qualified", "contacted", "nurture")   # answering a reply is never "too soon"
    limit = daily_limit(now_dt)
    sent_today = conn.execute("SELECT COUNT(*) FROM touches WHERE status = 'sent' AND at >= ?",
                              (now_dt.date().isoformat(),)).fetchone()[0]
    info["sent_today"], info["daily_limit"] = sent_today, limit
    if sent_today >= limit:
        problems.append(f"daily send limit reached ({sent_today}/{limit}) — protects your domain's reputation")
    sl = stop_loss(conn, now_dt)
    if sl["paused"] and cold:
        problems.append("stop-loss: " + sl["reason"])
    week_ago = (now_dt - timedelta(days=7)).replace(microsecond=0).isoformat()
    touches7 = conn.execute("SELECT COUNT(*) FROM touches WHERE prospect_id = ? AND at >= ?", (p["id"], week_ago)).fetchone()[0]
    if cold and touches7 >= int(setting("MAX_TOUCHES_PER_WEEK", "4")):
        problems.append(f"{touches7} touches to this prospect in 7 days across channels — over-contact; wait")
    recent = conn.execute("SELECT MAX(at) FROM touches WHERE prospect_id = ? AND channel = 'email' AND status = 'sent'",
                          (p["id"],)).fetchone()[0]
    if cold and recent and recent >= (now_dt - timedelta(days=2)).replace(microsecond=0).isoformat():
        problems.append(f"this prospect was already emailed at {recent} — wait at least 2 days")
    return problems, info


def build_message(to, subject, body, sender_email, sender_name=None, reply_to=None, in_reply_to=None):
    msg = EmailMessage()
    msg["From"] = f"{sender_name} <{sender_email}>" if sender_name else sender_email
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = format_datetime(datetime.now(timezone.utc))
    msg["Message-ID"] = make_msgid(domain=sender_email.split("@")[-1])
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["List-Unsubscribe"] = f"<mailto:{reply_to or sender_email}?subject=unsubscribe>"
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to
    msg.set_content(body)
    return msg


def smtp_send(msg, host, port, user, password, smtp=smtplib):
    port = int(port)
    if port == 465:
        with smtp.SMTP_SSL(host, port, context=tls_context(), timeout=30) as s:
            s.login(user, password)
            s.send_message(msg)
    else:
        with smtp.SMTP(host, port, timeout=30) as s:
            s.starttls(context=tls_context())
            s.login(user, password)
            s.send_message(msg)


def send(conn, key, to, subject, body, evidence=None, evidence_text=None, step=None, really=False,
         allow_catch_all=False, body_path=None, smtp=smtplib, in_reply_to=None, schedule=True, now=None):
    problems, info = preflight(conn, key, to, subject, body, evidence, evidence_text, allow_catch_all, now)
    box, why = mailboxes.pick(conn, pipeline.get(conn, key)["id"], now)
    info["mailbox"] = box["email"] if box else None
    if really and not box:
        problems.append("no mailbox can send: " + why if "configured" not in why else
                        "SMTP not configured — add SMTP_HOST, SMTP_PASSWORD, SENDER_EMAIL to ~/.ai-sales-team/.env (or mailboxes.json)")
    out = {**info, "to": to, "subject": subject, "words": len(re.findall(r"\w+", body or "")), "problems": problems}
    if problems:
        out["sent"] = False
        out["next"] = "Fix every problem above, then run again. Nothing was sent."
        return out
    if not really:
        out.update(sent=False, dry_run=True, preview=body,
                   next="All checks passed. Show the user this exact email; send only after they approve, by adding --send.")
        return out
    msg = build_message(to, subject, body, box["email"], box.get("name"), box.get("reply_to"), in_reply_to)
    smtp_send(msg, box["smtp_host"], box["smtp_port"], box["smtp_user"], box["password"], smtp=smtp)
    logged = log_touch(conn, key, "email", step=step, to=to, subject=subject, body_path=body_path, status="sent",
                       message_id=msg["Message-ID"], schedule=schedule, today=now.date() if now else None, sender=box["email"])
    out.update(sent=True, message_id=msg["Message-ID"], mailbox=box["email"],
               **{k: v for k, v in logged.items() if k.startswith("next")})
    return out


# ----------------------------------------------------------------------------------------------- sequences

def parse_sequence(path):
    raw = Path(path).read_text(encoding="utf-8-sig")
    steps = []
    if path.lower().endswith(".json"):
        data = json.loads(raw)
        data = data.get("emails", data) if isinstance(data, dict) else data
        for i, e in enumerate(data):
            steps.append({"step": int(e.get("step", i + 1)), "subject": (e.get("subject") or "").strip(),
                          "body": (e.get("body") or "").strip(), "subject_b": (e.get("subject_b") or "").strip() or None,
                          "hook": (e.get("hook") or "").strip() or None})
    else:
        for i, block in enumerate(re.split(r"(?m)^#{1,3}\s*(?:email|mail|step)\s*#?\s*\d+[^\n]*\n", raw, flags=re.I)[1:]):
            m = re.search(r"(?mi)^\**subject\**\s*:\s*(.+)$", block)
            body = (block[:m.start()] + block[m.end():]) if m else block
            mb = re.search(r"(?mi)^\**subject\s*b\**\s*:\s*(.+)$", body)
            if mb:
                body = body[:mb.start()] + body[mb.end():]
            steps.append({"step": i + 1, "subject": (m.group(1).strip() if m else ""), "body": body.strip().strip("-").strip(),
                          "subject_b": mb.group(1).strip() if mb else None, "hook": None})
    steps.sort(key=lambda x: x["step"])
    if not steps or [x["step"] for x in steps] != list(range(1, len(steps) + 1)):
        raise UserError("sequence must have emails numbered 1, 2, 3 ... (JSON list or '## Email 1' headings)")
    if len(steps) > len(cadence()) + 1:
        raise UserError(f"{len(steps)} emails but the cadence has only {len(cadence()) + 1} slots (CADENCE_DAYS)")
    return steps


def doctor(conn=None):
    """Is sending ready, and which delivery mode should the agent use?"""
    import inbox
    boxes = mailboxes.load()
    smtp = {"SMTP_HOST": bool(boxes) or bool(setting("SMTP_HOST")), "SMTP_PASSWORD": bool(boxes) or bool(secret("SMTP_PASSWORD")),
            "SENDER_EMAIL": bool(boxes) or bool(setting("SENDER_EMAIL"))}
    imap = bool(inbox.configs())
    smtp_ok = bool(boxes)
    checks = {"smtp": smtp_ok, "imap_reply_detection": imap, "sender_address": bool(setting("SENDER_ADDRESS")),
              "booking_url": bool(setting("BOOKING_URL")), "daily_limit_today": daily_limit(),
              "warmup_ramp": bool(setting("SENDING_STARTED")), "cadence_days": cadence(),
              "send_hours_prospect_tz": setting("SEND_HOURS", "09:00-17:00")}
    if conn is not None and boxes:
        checks["mailboxes"] = mailboxes.capacity(conn)
    if smtp_ok and imap:
        mode = "autopilot"
        how = ("Write SEQUENCE.json → outreach.py approve --check → show the user → outreach.py approve. "
               "autopilot.py tick --send (scheduled) sends each email on its day and stops on any reply.")
    elif smtp_ok:
        mode = "send-one-by-one"
        how = ("SMTP works but replies can't be detected: send approved emails with outreach.py send (dry run, then --send) "
               "and paste every reply into sales-reply before the next follow-up. Don't queue sequences.")
    else:
        mode = "manual"
        how = "The user sends each email from their own mailbox; you log it with outreach.py log so follow-ups are scheduled."
    missing = [k for k, v in {**smtp, "IMAP": imap}.items() if not v]
    warn = []
    if not checks["sender_address"]:
        warn.append("SENDER_ADDRESS / seller.postal_address missing — required for US cold email (CAN-SPAM)")
    if smtp_ok and not checks["warmup_ramp"]:
        warn.append("set SENDING_STARTED=YYYY-MM-DD for a new inbox so volume ramps up (10/day, +5/week)")
    if conn is not None:
        sl = stop_loss(conn)
        checks["stop_loss"] = sl
        if sl["paused"]:
            warn.insert(0, "SENDING PAUSED — " + sl["reason"])
        if sl["warning"]:
            warn.append(sl["warning"])
    return {"mode": mode, "how": how, "checks": checks, "missing_for_autopilot": missing, "warnings": warn}


def approve(conn, key, to, steps, evidence=None, evidence_text=None, start=None, allow_catch_all=False, today=None,
            check_only=False):
    """Check every email of a sequence now; store them as approved. Step 1 is due on `start` (default today)."""
    p = pipeline.get(conn, key)
    report, bad = [], 0
    for st in steps:
        subj = st["subject"] or (f"Re: {steps[0]['subject']}" if st["step"] > 1 else "")
        problems, info = preflight(conn, key, to, subj if st["step"] == 1 else steps[0]["subject"], st["body"], evidence,
                                   evidence_text, allow_catch_all)
        problems = [x for x in problems if "daily send limit" not in x and "already emailed" not in x and "stop-loss" not in x
                    and "contacted" not in x]
        q = email_lint.lint(st["body"], subj if st["step"] == 1 else None, int(st["step"]))
        floor = int(setting("LINT_MIN_SCORE", "65"))
        if q["score"] < floor:
            problems.append(f"quality score {q['score']}/100 (< {floor}): " + "; ".join(q["issues"][:4]))
        bad += bool(problems)
        report.append({"step": st["step"], "subject": subj, "words": len(re.findall(r"\w+", st["body"])), "problems": problems,
                       "claim_check": info.get("claim_check"), "quality": {"score": q["score"], "verdict": q["verdict"],
                                                                           "issues": q["issues"]}})
    if bad:
        return {"approved": False, "prospect": p["slug"], "steps": report,
                "next": "Fix the problems in the listed emails and run approve again. Nothing was queued."}
    if check_only:
        return {"approved": False, "check_passed": True, "prospect": p["slug"], "steps": report,
                "next": "All emails pass. Show them to the user; after they approve, run the same command without --check."}
    d0 = (datetime.fromisoformat(start).date() if start else (today or datetime.now(timezone.utc).date()))
    # A/B: email 1's subject_b goes to every second prospect (stable by slug), so results can be compared fairly
    import hashlib
    variant_b = bool(steps[0].get("subject_b")) and int(hashlib.sha1(p["slug"].encode()).hexdigest(), 16) % 2 == 1
    quality = {r["step"]: (r.get("quality") or {}).get("score") for r in report}
    with conn:
        conn.execute("UPDATE sequence_steps SET status = 'cancelled' WHERE prospect_id = ? AND status = 'approved'", (p["id"],))
        for st in steps:
            due = d0 if st["step"] == 1 else None          # follow-up dates are set when email 1 actually goes out
            subj = st["subject"] or None
            variant = None
            if st["step"] == 1 and st.get("subject_b"):
                variant = "B" if variant_b else "A"
                subj = st["subject_b"] if variant_b else st["subject"]
            conn.execute("INSERT INTO sequence_steps(prospect_id, step, recipient, subject, body, status, due, evidence_json, "
                         "created_at, variant, hook, quality) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (p["id"], st["step"], to, subj, st["body"], "approved", due and due.isoformat(),
                          json.dumps({"files": evidence or [], "texts": evidence_text or []}), pipeline.now(), variant,
                          st.get("hook"), quality.get(st["step"])))
        pipeline.event(conn, p["id"], "sequence", f"{len(steps)}-email sequence approved for {to}, email 1 due {d0.isoformat()}")
        conn.execute("UPDATE prospects SET next_action = ?, next_due = ? WHERE id = ?",
                     ("Email 1 queued (outreach.py run --send)", d0.isoformat(), p["id"]))
    offs = cadence()
    return {"approved": True, "prospect": p["slug"], "to": to, "steps": report,
            "schedule": [f"email 1: {d0.isoformat()}"] + [f"email {i + 2}: day {o} after email 1" for i, o in enumerate(offs[:len(steps) - 1])],
            "next": "Run outreach.py run --send now or let the scheduled run send it. Stops automatically on any reply."}


def queue(conn, key=None):
    q = ("SELECT s.id, p.slug AS prospect, p.stage, s.step, s.recipient, COALESCE(s.subject, '(Re: email 1)') AS subject, "
         "s.status, s.due, s.sent_at FROM sequence_steps s JOIN prospects p ON p.id = s.prospect_id")
    args = ()
    if key:
        q += " WHERE p.id = ?"
        args = (pipeline.get(conn, key)["id"],)
    return [dict(r) for r in conn.execute(q + " ORDER BY p.slug, s.step", args)]


def cancel(conn, key, reason="cancelled by user"):
    p = pipeline.get(conn, key)
    with conn:
        n = conn.execute("UPDATE sequence_steps SET status = 'cancelled' WHERE prospect_id = ? AND status = 'approved'",
                         (p["id"],)).rowcount
        if n:
            pipeline.event(conn, p["id"], "sequence", f"{n} queued email(s) cancelled: {reason}")
    return {"prospect": p["slug"], "cancelled": n, "reason": reason}


def _blocked(conn, p, row):
    """Why a queued step must not go out any more (None = still valid)."""
    if p["stage"] not in ("new", "researched", "qualified", "contacted", "nurture"):
        return f"stage is {p['stage']}"
    first = conn.execute("SELECT MIN(created_at) FROM sequence_steps WHERE prospect_id = ? AND step = 1 AND status IN ('approved','sent')",
                         (p["id"],)).fetchone()[0] or row["created_at"]
    if conn.execute("SELECT 1 FROM events WHERE prospect_id = ? AND kind = 'reply' AND at >= ?", (p["id"], first)).fetchone():
        return "prospect replied"
    if pipeline.is_suppressed(conn, row["recipient"]):
        return "recipient is on the do-not-contact list"
    if row["step"] > 1:
        prev = conn.execute("SELECT status FROM sequence_steps WHERE prospect_id = ? AND step = ? ORDER BY id DESC LIMIT 1",
                            (p["id"], row["step"] - 1)).fetchone()
        if not prev or prev["status"] != "sent":
            return "previous email not sent"
    return None


def prospect_tz(p):
    """The prospect's time zone: their own (pipeline.py where), else their country's, else your first target country's."""
    import meeting
    import query_library
    for cand in (p.get("tz"), (query_library.COUNTRIES.get((p.get("country") or "").upper()) or {}).get("tz"),
                 setting("PROSPECT_DEFAULT_TZ"), _profile_tz()):
        if cand:
            try:
                meeting.tz(cand)
                return cand
            except Exception:  # noqa: BLE001
                continue
    return setting("TIMEZONE", "UTC")


def _profile_tz():
    try:
        import query_library
        import seller_profile
        prof = seller_profile.load()
        return query_library.COUNTRIES[query_library.country_codes(prof)[0]]["tz"] if prof else None
    except Exception:  # noqa: BLE001
        return None


def send_window(p, now, hours):
    import meeting
    zone = prospect_tz(p)
    local = now.astimezone(meeting.tz(zone))
    try:
        h0, h1 = meeting._hours(hours)
    except Exception:  # noqa: BLE001
        h0, h1 = 9 * 60, 17 * 60
    return zone, local, (h0 <= local.hour * 60 + local.minute < h1 and local.weekday() < 5)


def run(conn, really=False, limit=None, now=None, smtp=smtplib):
    """Send every due approved step that is still valid. Dry run unless really=True."""
    now = now or datetime.now(timezone.utc)
    today = now.date()
    hours = setting("SEND_HOURS", "09:00-17:00")
    rows = [dict(r) for r in conn.execute("SELECT * FROM sequence_steps WHERE status = 'approved' AND due IS NOT NULL AND due <= ? "
                                          "ORDER BY due, step", ((today + timedelta(days=1)).isoformat(),))]
    out = {"due": 0, "sent": [], "would_send": [], "skipped": [], "errors": [], "waiting_for_window": [],
           "window": f"{hours} in each prospect's own time zone, Mon-Fri"}
    for row in rows:
        if limit and len(out["sent"]) >= limit:
            break
        p = dict(conn.execute("SELECT * FROM prospects WHERE id = ?", (row["prospect_id"],)).fetchone())
        zone, local, ok = send_window(p, now, hours)
        if row["due"] > local.date().isoformat():       # not due yet in THEIR calendar
            continue
        out["due"] += 1
        if not ok:
            out["waiting_for_window"].append({"prospect": p["slug"], "step": row["step"], "their_time": local.strftime("%a %H:%M"),
                                              "tz": zone})
            continue
        why = _blocked(conn, p, row)
        if why:
            with conn:
                conn.execute("UPDATE sequence_steps SET status = 'skipped', note = ? WHERE id = ?", (why, row["id"]))
                conn.execute("UPDATE sequence_steps SET status = 'cancelled', note = ? WHERE prospect_id = ? AND status = 'approved' "
                             "AND step > ?", (why, p["id"], row["step"]))
            out["skipped"].append({"prospect": p["slug"], "step": row["step"], "why": why})
            continue
        first = conn.execute("SELECT subject, message_id FROM sequence_steps WHERE prospect_id = ? AND step = 1 AND status = 'sent' "
                             "ORDER BY id DESC LIMIT 1", (p["id"],)).fetchone()
        subject = row["subject"] or (f"Re: {first['subject']}" if first else None)
        thread = first["message_id"] if (first and row["step"] > 1) else None
        ev = json.loads(row["evidence_json"] or "{}")
        item = {"prospect": p["slug"], "step": row["step"], "to": row["recipient"], "subject": subject}
        if not really:
            problems, _ = preflight(conn, p["slug"], row["recipient"], subject, row["body"], ev.get("files"), ev.get("texts"),
                                    today=now)
            item["problems"] = problems
            out["would_send"].append(item)
            continue
        try:
            res = send(conn, p["slug"], row["recipient"], subject, row["body"], ev.get("files"), ev.get("texts"), row["step"],
                       True, smtp=smtp, in_reply_to=thread, now=now)
        except (smtplib.SMTPException, OSError) as exc:
            out["errors"].append({**item, "error": f"{type(exc).__name__}: {exc}"})
            break                                         # SMTP trouble: stop the run, retry next time
        if not res.get("sent"):
            out["errors"].append({**item, "problems": res["problems"]})
            if any("daily send limit" in x for x in res["problems"]):
                break
            continue
        their_today = local.date()
        first_date = their_today if row["step"] == 1 else (_first_email_date(conn, p["id"]) or their_today)
        nxt = followup_due(first_date, row["step"], their_today)
        with conn:
            conn.execute("UPDATE sequence_steps SET status = 'sent', sent_at = ?, message_id = ?, subject = ? WHERE id = ?",
                         (pipeline.now(), res["message_id"], subject, row["id"]))
            if nxt:
                conn.execute("UPDATE sequence_steps SET due = ? WHERE prospect_id = ? AND step = ? AND status = 'approved'",
                             (nxt.isoformat(), p["id"], row["step"] + 1))
        out["sent"].append({**item, "message_id": res["message_id"], "next_due": nxt and nxt.isoformat()})
    out["next"] = ("Dry run — add --send to send these." if not really else
                   f"Sent {len(out['sent'])}. Schedule this command (cron / Task Scheduler) to keep sequences running.")
    return out


def whatsapp_link(phone, text):
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) < 10 or len(digits) > 15:
        raise UserError(f"'{phone}' doesn't look like a full international number (country code + number)")
    if len(digits) == 10:
        raise UserError("add the country code (e.g. +91 for India, +1 US, +44 UK, +61 Australia)")
    return f"https://wa.me/{digits}?text={quote(text or '')}"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Log touches, run the follow-up cadence, send email safely, WhatsApp links.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log"); lg.add_argument("prospect"); lg.add_argument("--channel", default="email", choices=CHANNELS)
    lg.add_argument("--step", type=int); lg.add_argument("--to"); lg.add_argument("--subject"); lg.add_argument("--file")
    lg.add_argument("--note"); lg.add_argument("--no-schedule", action="store_true")
    sub.add_parser("cadence")
    st = sub.add_parser("stop"); st.add_argument("prospect"); st.add_argument("--reason", default="")
    sd = sub.add_parser("send"); sd.add_argument("prospect"); sd.add_argument("--to", required=True)
    sd.add_argument("--subject", required=True); sd.add_argument("--body-file", required=True)
    sd.add_argument("--evidence", action="append"); sd.add_argument("--evidence-text", action="append")
    sd.add_argument("--step", type=int); sd.add_argument("--send", action="store_true", help="really send (default: dry run)")
    sd.add_argument("--allow-catch-all", action="store_true")
    apv = sub.add_parser("approve"); apv.add_argument("prospect"); apv.add_argument("--to", required=True)
    apv.add_argument("--file", required=True); apv.add_argument("--evidence", action="append")
    apv.add_argument("--evidence-text", action="append"); apv.add_argument("--start"); apv.add_argument("--allow-catch-all", action="store_true")
    apv.add_argument("--check", action="store_true", help="validate every email, queue nothing (run before showing the user)")
    sub.add_parser("doctor")
    qu = sub.add_parser("queue"); qu.add_argument("prospect", nargs="?")
    rn = sub.add_parser("run"); rn.add_argument("--send", action="store_true"); rn.add_argument("--limit", type=int)
    cn = sub.add_parser("cancel"); cn.add_argument("prospect"); cn.add_argument("--reason", default="cancelled by user")
    wa = sub.add_parser("whatsapp"); wa.add_argument("phone", nargs="+"); wa.add_argument("--text"); wa.add_argument("--text-file")
    wa.add_argument("--prospect")
    a = ap.parse_args(argv)
    conn = pipeline.connect()
    try:
        if a.cmd == "log":
            out = log_touch(conn, a.prospect, a.channel, a.step, a.to, a.subject, a.file, a.note, schedule=not a.no_schedule)
        elif a.cmd == "cadence":
            offs = cadence()
            out = {"days_after_email_1": offs, "emails": len(offs) + 1,
                   "schedule": ["email 1: day 0"] + [f"email {i + 2}: day {o}" for i, o in enumerate(offs)],
                   "rules": "weekend dates move to Monday; stops on any reply, opt-out, bounce or booked meeting",
                   "override": "CADENCE_DAYS=3,7,14,28 in ~/.ai-sales-team/.env"}
        elif a.cmd == "approve":
            try:
                out = approve(conn, a.prospect, a.to, parse_sequence(a.file), a.evidence, a.evidence_text, a.start,
                              a.allow_catch_all, check_only=a.check)
            except FileNotFoundError as exc:
                raise UserError(str(exc))
            emit({"ok": True, "data": out}, 0 if out["approved"] or out.get("check_passed") else 1)
        elif a.cmd == "doctor":
            out = doctor(conn)
        elif a.cmd == "queue":
            out = {"queue": queue(conn, a.prospect)}
        elif a.cmd == "run":
            out = run(conn, a.send, a.limit)
        elif a.cmd == "cancel":
            out = cancel(conn, a.prospect, a.reason)
        elif a.cmd == "stop":
            out = stop(conn, a.prospect, a.reason)
        elif a.cmd == "send":
            body = Path(a.body_file).read_text(encoding="utf-8-sig")
            try:
                out = send(conn, a.prospect, a.to, a.subject, body, a.evidence, a.evidence_text, a.step, a.send,
                           a.allow_catch_all, a.body_file)
            except FileNotFoundError as exc:
                raise UserError(str(exc))
            except (smtplib.SMTPException, OSError) as exc:
                emit({"ok": False, "error": f"SMTP error, nothing sent: {type(exc).__name__}: {exc}"}, 1)
            emit({"ok": True, "data": out}, 0 if out.get("sent") or out.get("dry_run") else 1)
        elif a.cmd == "whatsapp":
            text = Path(a.text_file).read_text(encoding="utf-8-sig") if a.text_file else (a.text or "")
            phone = " ".join(a.phone)
            if pipeline.is_suppressed(conn, re.sub(r"\D", "", phone)):
                raise UserError("this number is on the do-not-contact list")
            out = {"link": whatsapp_link(phone, text), "chars": len(text),
                   "next": "The user opens the link and sends it themselves, then: outreach.py log <slug> --channel whatsapp"}
            if a.prospect:
                out["prospect"] = pipeline.get(conn, a.prospect)["slug"]
        emit({"ok": True, "data": out})
    except (UserError, pipeline.UserError) as exc:
        emit({"ok": False, "error": str(exc)}, 2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

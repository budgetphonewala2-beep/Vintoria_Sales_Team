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

Cadence: business days after the previous touch, default "3,4,7,7" → email 1, then follow-ups on day
+3, +4, +7, +7 (5 touches, the last a polite breakup). Override with CADENCE_DAYS=3,4,7,7 in ~/.ai-sales-team/.env.

Sending gates (all must pass, otherwise nothing is sent):
  - --send given (default is a dry-run preview), SMTP_HOST/SMTP_USER/SMTP_PASSWORD/SENDER_EMAIL configured;
  - recipient is on file with email_status=verified (catch_all only with --allow-catch-all; never
    pattern-guessed / unverified / invalid), and neither the address nor its domain is suppressed;
  - the body passes claim_check.py against the evidence you give, has no [PLACEHOLDER], has an opt-out line,
    and (cold email to the US) the SENDER_ADDRESS postal address;
  - today's sends are under DAILY_SEND_LIMIT (default 30) and this prospect wasn't emailed in the last 2 days.
Plain text only, no tracking pixels, List-Unsubscribe header set.
"""

import argparse
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
import pipeline  # noqa: E402
from sales_common import emit, secret, setting, tls_context  # noqa: E402

CHANNELS = ["email", "linkedin", "whatsapp", "call", "sms", "other"]
DEFAULT_CADENCE = [3, 4, 7, 7]
OPT_OUT = re.compile(r"(reply\s+['\"“]?(no|stop|unsubscribe)|not\s+relevant\?|won'?t\s+(follow\s+up|email)|unsubscribe|opt[\s-]?out|"
                     r"let me know if you'?d rather not|mat bhejo|nahi chahiye to bata)", re.I)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)


class UserError(Exception):
    pass


def cadence():
    raw = setting("CADENCE_DAYS")
    if raw:
        try:
            days = [int(x) for x in raw.replace(" ", "").split(",") if x]
            if days and all(d > 0 for d in days):
                return days
        except ValueError:
            pass
    return list(DEFAULT_CADENCE)


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
              message_id=None, schedule=True, today=None):
    if channel not in CHANNELS:
        raise UserError(f"channel must be one of {CHANNELS}")
    p = pipeline.get(conn, key)
    if step is None and channel == "email":
        step = _touch_count(conn, p["id"]) + 1
    ts = pipeline.now()
    out = {"prospect": p["slug"], "channel": channel, "step": step, "status": status}
    with conn:
        conn.execute("INSERT INTO touches(prospect_id, channel, step, recipient, subject, body_path, status, message_id, at) "
                     "VALUES (?,?,?,?,?,?,?,?,?)", (p["id"], channel, step, to, subject, body_path, status, message_id, ts))
        pipeline.event(conn, p["id"], "touch", f"{channel}" + (f" #{step}" if step else "") + (f" to {to}" if to else "")
                       + (f": {subject}" if subject else "") + (f" — {note}" if note else ""))
        if p["stage"] in ("new", "researched", "qualified"):
            conn.execute("UPDATE prospects SET stage = 'contacted' WHERE id = ?", (p["id"],))
            pipeline.event(conn, p["id"], "stage", f"first {channel} touch", p["stage"], "contacted")
            out["stage"] = "contacted"
        if schedule and channel == "email" and p["stage"] in ("new", "researched", "qualified", "contacted", "nurture"):
            gaps = cadence()
            base = today or datetime.now(timezone.utc).date()
            if step and step <= len(gaps):
                due = add_business_days(base, gaps[step - 1]).isoformat()
                last = step == len(gaps)
                action = (f"Send follow-up #{step} (final, polite breakup)" if last else f"Send follow-up #{step}") + \
                         " — new value, not 'just checking in'"
            else:
                due = add_business_days(base, 30).isoformat()
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
    return {"prospect": p["slug"], "cadence": "stopped", "reason": reason}


def _contact(conn, pid, email):
    r = conn.execute("SELECT * FROM contacts WHERE prospect_id = ? AND lower(email) = lower(?)", (pid, email)).fetchone()
    return dict(r) if r else None


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
    address = setting("SENDER_ADDRESS")
    if address and address.split(",")[0].strip().lower() not in (body or "").lower():
        problems.append("signature is missing your postal address (SENDER_ADDRESS) — required for US cold email")
    sources = claim_check.load_sources(evidence or [], evidence_text or [])
    cc = claim_check.check(body, sources)
    info["claim_check"] = {"ok": cc["ok"], "checked": cc["checked"], "supported": cc["supported"]}
    if not cc["ok"]:
        problems.extend(f"unsupported claim: {u['text']}" for u in cc["unsupported"])
        problems.extend(f"placeholder not filled: {h}" for h in cc["placeholders"])
    now_dt = today or datetime.now(timezone.utc)
    limit = int(setting("DAILY_SEND_LIMIT", "30"))
    sent_today = conn.execute("SELECT COUNT(*) FROM touches WHERE status = 'sent' AND at >= ?",
                              (now_dt.date().isoformat(),)).fetchone()[0]
    info["sent_today"], info["daily_limit"] = sent_today, limit
    if sent_today >= limit:
        problems.append(f"daily send limit reached ({sent_today}/{limit}) — protects your domain's reputation")
    recent = conn.execute("SELECT MAX(at) FROM touches WHERE prospect_id = ? AND channel = 'email' AND status = 'sent'",
                          (p["id"],)).fetchone()[0]
    if recent and recent >= (now_dt - timedelta(days=2)).replace(microsecond=0).isoformat():
        problems.append(f"this prospect was already emailed at {recent} — wait at least 2 days")
    return problems, info


def build_message(to, subject, body, sender_email, sender_name=None, reply_to=None):
    msg = EmailMessage()
    msg["From"] = f"{sender_name} <{sender_email}>" if sender_name else sender_email
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = format_datetime(datetime.now(timezone.utc))
    msg["Message-ID"] = make_msgid(domain=sender_email.split("@")[-1])
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["List-Unsubscribe"] = f"<mailto:{reply_to or sender_email}?subject=unsubscribe>"
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
         allow_catch_all=False, body_path=None, smtp=smtplib):
    problems, info = preflight(conn, key, to, subject, body, evidence, evidence_text, allow_catch_all)
    sender = setting("SENDER_EMAIL")
    cfg = {"SMTP_HOST": setting("SMTP_HOST"), "SMTP_USER": setting("SMTP_USER") or sender,
           "SMTP_PASSWORD": secret("SMTP_PASSWORD"), "SENDER_EMAIL": sender}
    missing = [k for k, v in cfg.items() if not v]
    if really and missing:
        problems.append("SMTP not configured — add to ~/.ai-sales-team/.env: " + ", ".join(missing))
    out = {**info, "to": to, "subject": subject, "words": len(re.findall(r"\w+", body or "")), "problems": problems}
    if problems:
        out["sent"] = False
        out["next"] = "Fix every problem above, then run again. Nothing was sent."
        return out
    if not really:
        out.update(sent=False, dry_run=True, preview=body,
                   next="All checks passed. Show the user this exact email; send only after they approve, by adding --send.")
        return out
    msg = build_message(to, subject, body, sender, setting("SENDER_NAME"), setting("REPLY_TO"))
    smtp_send(msg, cfg["SMTP_HOST"], setting("SMTP_PORT", "587"), cfg["SMTP_USER"], cfg["SMTP_PASSWORD"], smtp=smtp)
    logged = log_touch(conn, key, "email", step=step, to=to, subject=subject, body_path=body_path, status="sent",
                       message_id=msg["Message-ID"])
    out.update(sent=True, message_id=msg["Message-ID"], **{k: v for k, v in logged.items() if k.startswith("next")})
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
    wa = sub.add_parser("whatsapp"); wa.add_argument("phone", nargs="+"); wa.add_argument("--text"); wa.add_argument("--text-file")
    wa.add_argument("--prospect")
    a = ap.parse_args(argv)
    conn = pipeline.connect()
    try:
        if a.cmd == "log":
            out = log_touch(conn, a.prospect, a.channel, a.step, a.to, a.subject, a.file, a.note, schedule=not a.no_schedule)
        elif a.cmd == "cadence":
            gaps = cadence()
            out = {"business_days_between_emails": gaps, "touches": len(gaps) + 1,
                   "schedule": ["email 1: day 0"] + [f"email {i + 2}: +{g} business days" for i, g in enumerate(gaps)],
                   "override": "CADENCE_DAYS=3,4,7,7 in ~/.ai-sales-team/.env"}
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

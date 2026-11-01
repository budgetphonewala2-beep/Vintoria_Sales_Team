#!/usr/bin/env python3
"""
Inbox watcher: reads your mailbox over IMAP (read-only — nothing is marked read, moved or deleted), finds
replies and bounces from prospects, classifies them with reply_triage.py and updates the pipeline: the
sequence stops, opt-outs are suppressed, bounced addresses are marked invalid, interested prospects are
put at the top of today's agenda.

Optionally (--auto-reply, or AUTO_REPLY=1) it answers "let's talk" replies at once with your booking link —
the only moment the link is ever sent. Every other reply waits for you (sales-reply).

Usage:
    python inbox.py check [--days 7] [--apply] [--auto-reply] [--limit 300]

Settings (env or ~/.ai-sales-team/.env):
    IMAP_HOST (default: derived from SMTP_HOST, e.g. smtp.gmail.com → imap.gmail.com)   IMAP_PORT=993
    IMAP_USER (default SMTP_USER / SENDER_EMAIL)    IMAP_PASSWORD (default SMTP_PASSWORD)    IMAP_FOLDER=INBOX
    AUTO_REPLY_CATEGORIES=meeting_request          BOOKING_URL=https://cal.com/you/15min (needed for auto-reply)
Gmail / Google Workspace: enable IMAP and use an App Password. Outlook/Microsoft 365 needs IMAP enabled for the mailbox.
Matching: In-Reply-To/References → a message we sent; else the sender is a saved contact; else the sender's domain
is a prospect's domain (not for webmail). Bounces are matched by the failed address in the bounce body.
"""

import argparse
import email
import imaplib
import re
import sys
from datetime import datetime, timedelta, timezone
from email import policy
from email.utils import getaddresses, parseaddr
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import outreach  # noqa: E402
import pipeline  # noqa: E402
import reply_triage  # noqa: E402
from sales_common import emit, secret, setting, tls_context  # noqa: E402

WEBMAIL = {"gmail.com", "googlemail.com", "yahoo.com", "yahoo.in", "yahoo.co.in", "outlook.com", "hotmail.com", "live.com",
           "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com", "rediffmail.com", "zoho.com", "gmx.com"}
BOUNCE_FROM = re.compile(r"^(mailer-daemon|postmaster|mail-daemon|bounce)", re.I)
BOUNCE_SUBJ = re.compile(r"(undeliver|delivery status notification|delivery (has )?failed|returned mail|failure notice|"
                         r"mail delivery (failed|subsystem))", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


class UserError(Exception):
    pass


def config():
    smtp_host = setting("SMTP_HOST") or ""
    host = setting("IMAP_HOST") or (re.sub(r"^smtp\.", "imap.", smtp_host) if smtp_host.startswith("smtp.") else None)
    user = setting("IMAP_USER") or setting("SMTP_USER") or setting("SENDER_EMAIL")
    pw = secret("IMAP_PASSWORD") or secret("SMTP_PASSWORD")
    missing = [k for k, v in {"IMAP_HOST": host, "IMAP_USER": user, "IMAP_PASSWORD": pw}.items() if not v]
    if missing:
        raise UserError("inbox not configured — add to ~/.ai-sales-team/.env: " + ", ".join(missing))
    return {"host": host, "port": int(setting("IMAP_PORT", "993")), "user": user, "password": pw,
            "folder": setting("IMAP_FOLDER", "INBOX")}


def fetch_messages(cfg, days=7, limit=300, imap=imaplib):
    """Raw RFC 822 bytes of recent messages, newest first. Read-only."""
    conn = imap.IMAP4_SSL(cfg["host"], cfg["port"], ssl_context=tls_context())
    try:
        conn.login(cfg["user"], cfg["password"])
        typ, _ = conn.select(cfg["folder"], readonly=True)
        if typ != "OK":
            raise UserError(f"can't open folder {cfg['folder']}")
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%d-%b-%Y")
        typ, data = conn.search(None, "SINCE", since)
        ids = (data[0].split() if data and data[0] else [])[::-1][:limit]
        out = []
        for i in ids:
            typ, parts = conn.fetch(i, "(BODY.PEEK[])")
            for part in parts or []:
                if isinstance(part, tuple) and len(part) > 1:
                    out.append(part[1])
        return out
    finally:
        try:
            conn.logout()
        except Exception:  # noqa: BLE001
            pass


def text_of(msg):
    try:
        body = msg.get_body(preferencelist=("plain", "html"))
    except Exception:  # noqa: BLE001
        body = None
    if body is None:
        parts = [p for p in msg.walk() if p.get_content_maintype() == "text"]
        body = parts[0] if parts else None
    if body is None:
        return ""
    try:
        content = body.get_content()
    except Exception:  # noqa: BLE001
        content = (body.get_payload(decode=True) or b"").decode("utf-8", "replace")
    if body.get_content_subtype() == "html":
        content = re.sub(r"(?is)<(script|style).*?</\1>", " ", content)
        content = re.sub(r"(?i)<br\s*/?>|</p>|</div>", "\n", content)
        content = unescape(re.sub(r"<[^>]+>", " ", content))
    return re.sub(r"[ \t]+", " ", content).strip()


def parse(raw):
    msg = email.message_from_bytes(raw, policy=policy.default)
    refs = " ".join(str(msg.get(h, "")) for h in ("In-Reply-To", "References"))
    name, addr = parseaddr(str(msg.get("From", "")))
    return {"message_id": str(msg.get("Message-ID", "")).strip(), "from": addr.lower(), "from_name": name,
            "subject": str(msg.get("Subject", "")), "date": str(msg.get("Date", "")),
            "refs": re.findall(r"<[^>]+>", refs), "text": text_of(msg),
            "to": [a.lower() for _, a in getaddresses([str(msg.get("To", ""))])]}


def match(conn, m):
    """(prospect row, the prospect's address this is about, how) or (None, None, None)."""
    is_bounce = bool(BOUNCE_FROM.match(m["from"]) or BOUNCE_SUBJ.search(m["subject"]))
    for ref in m["refs"]:
        r = conn.execute("SELECT p.*, t.recipient FROM touches t JOIN prospects p ON p.id = t.prospect_id WHERE t.message_id = ?",
                         (ref,)).fetchone()
        if r:
            return dict(r), (r["recipient"] if is_bounce else m["from"]) or m["from"], "thread"
    if is_bounce:
        for addr in dict.fromkeys(a.lower() for a in EMAIL_RE.findall(m["text"])):
            r = conn.execute("SELECT p.* FROM contacts c JOIN prospects p ON p.id = c.prospect_id WHERE lower(c.email) = ?",
                             (addr,)).fetchone()
            if r:
                return dict(r), addr, "bounce"
        return None, None, None
    r = conn.execute("SELECT p.* FROM contacts c JOIN prospects p ON p.id = c.prospect_id WHERE lower(c.email) = ?",
                     (m["from"],)).fetchone()
    if r:
        return dict(r), m["from"], "contact"
    dom = m["from"].split("@")[-1]
    if dom and dom not in WEBMAIL:
        r = conn.execute("SELECT * FROM prospects WHERE slug = ?", (dom,)).fetchone()
        if r:
            return dict(r), m["from"], "domain"
    return None, None, None


def booking_reply(m, result, prospect):
    url = setting("BOOKING_URL")
    first = (m["from_name"] or "").split(" ")[0].strip('"') or "there"
    lines = [f"Hi {first},", "", "Great, thanks for getting back to me. Here's my calendar so you can pick a time "
             f"that suits you: {url}"]
    if result["mentioned_times"]:
        lines += ["", f"If {result['mentioned_times'][0]} still works for you, just pick it there, or reply \"confirmed\" "
                      "and I'll send the invite."]
    sig = [x for x in (setting("SENDER_NAME"), setting("SENDER_ADDRESS")) if x]
    lines += [""] + (sig or ["Thanks"])
    subj = m["subject"] if m["subject"].lower().startswith("re:") else f"Re: {m['subject']}"
    return subj, "\n".join(lines) + "\n"


def check(conn, messages, apply=False, auto_reply=False, smtp=None, now=None):
    me = (setting("SENDER_EMAIL") or "").lower()
    cats = [c.strip() for c in setting("AUTO_REPLY_CATEGORIES", "meeting_request").split(",") if c.strip()]
    out = {"scanned": len(messages), "matched": [], "ignored": 0, "already_seen": 0, "auto_replies": [], "errors": []}
    for raw in messages:
        m = parse(raw) if isinstance(raw, (bytes, bytearray)) else raw
        if not m["message_id"] or m["from"] == me:
            out["ignored"] += 1
            continue
        if conn.execute("SELECT 1 FROM inbox_seen WHERE message_id = ?", (m["message_id"],)).fetchone():
            out["already_seen"] += 1
            continue
        p, addr, how = match(conn, m)
        if not p:
            out["ignored"] += 1
            continue
        res = reply_triage.classify(m["text"] if how != "bounce" else "Delivery has failed " + m["text"])
        item = {"prospect": p["slug"], "from": m["from"], "subject": m["subject"], "matched_by": how,
                "category": res["category"], "next_action": res["next_action"], "next_skill": res["next_skill"],
                "excerpt": res["reply_excerpt"][:200]}
        if apply:
            item["applied"] = reply_triage.apply(conn, p["slug"], res, addr)
            with conn:
                conn.execute("INSERT OR IGNORE INTO inbox_seen(message_id, prospect_id, category, at) VALUES (?,?,?,?)",
                             (m["message_id"], p["id"], res["category"], pipeline.now()))
            if auto_reply and res["category"] in cats:
                if not setting("BOOKING_URL"):
                    out["errors"].append(f"{p['slug']}: auto-reply skipped — set BOOKING_URL")
                else:
                    subj, body = booking_reply(m, res, p)
                    try:
                        sent = outreach.send(conn, p["slug"], addr, subj, body, evidence_text=[m["text"], body], really=True,
                                             smtp=smtp or outreach.smtplib, in_reply_to=m["message_id"], schedule=False, now=now)
                    except (outreach.smtplib.SMTPException, OSError) as exc:
                        sent = {"sent": False, "problems": [f"SMTP: {exc}"]}
                    out["auto_replies"].append({"prospect": p["slug"], "to": addr, "sent": sent.get("sent"),
                                                "problems": sent.get("problems")})
                    if sent.get("sent"):
                        with conn:
                            conn.execute("UPDATE prospects SET next_action = ?, next_due = date('now') WHERE id = ?",
                                         ("Booking link sent — when they pick a time, run meeting.py book", p["id"]))
        out["matched"].append(item)
    out["next"] = ("Dry run — add --apply to update the pipeline." if not apply else
                   "Pipeline updated. Replies that need you are at the top of pipeline.py today.")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read replies and bounces from your inbox (read-only) and update the pipeline.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("--days", type=int, default=7); c.add_argument("--limit", type=int, default=300)
    c.add_argument("--apply", action="store_true"); c.add_argument("--auto-reply", action="store_true")
    a = ap.parse_args(argv)
    conn = pipeline.connect()
    try:
        msgs = fetch_messages(config(), a.days, a.limit)
        auto = a.auto_reply or setting("AUTO_REPLY", "0") in ("1", "true", "yes", "on")
        emit({"ok": True, "data": check(conn, msgs, a.apply, auto and a.apply)})
    except UserError as exc:
        emit({"ok": False, "error": str(exc)}, 2)
    except (imaplib.IMAP4.error, OSError) as exc:
        emit({"ok": False, "error": f"IMAP error: {type(exc).__name__}: {exc}"}, 1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

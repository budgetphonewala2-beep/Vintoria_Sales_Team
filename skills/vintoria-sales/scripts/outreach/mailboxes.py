#!/usr/bin/env python3
"""
Sending mailboxes: rotate cold email across several inboxes (on secondary domains) so volume grows without burning
one address. Each mailbox has its own daily limit and warm-up; a prospect always hears from the SAME mailbox (the
thread stays intact); new prospects go to the mailbox with the most room left today.

Config: <data home>/mailboxes.json — passwords are never stored there, only the NAME of the env/.env variable:
    [{"email": "ravi@getpixelcraft.com", "name": "Ravi Sharma", "smtp_host": "smtp.gmail.com", "smtp_port": 587,
      "password_env": "PW_RAVI_GETPIXELCRAFT", "daily_limit": 25, "started": "2026-10-20",
      "imap_host": "imap.gmail.com"}, ...]
Without the file, the single mailbox from SMTP_HOST / SMTP_USER / SMTP_PASSWORD / SENDER_EMAIL is used (as before).

Usage:
    python mailboxes.py list            # mailboxes, today's limit (with warm-up), sent today, room left
    python mailboxes.py example         # print an example mailboxes.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import data_home, emit, secret, setting  # noqa: E402

EXAMPLE = [{"email": "ravi@getpixelcraft.com", "name": "Ravi Sharma", "smtp_host": "smtp.gmail.com", "smtp_port": 587,
            "password_env": "PW_RAVI_GETPIXELCRAFT", "daily_limit": 25, "started": "2026-10-20", "imap_host": "imap.gmail.com"},
           {"email": "ravi@trypixelcraft.com", "name": "Ravi Sharma", "smtp_host": "smtp.gmail.com", "smtp_port": 587,
            "password_env": "PW_RAVI_TRYPIXELCRAFT", "daily_limit": 25, "started": "2026-11-02", "imap_host": "imap.gmail.com"}]


def _file():
    return data_home() / "mailboxes.json"


def load():
    """All configured mailboxes with their secrets resolved. [] when nothing is configured."""
    f = _file()
    if f.exists():
        try:
            items = json.loads(f.read_text(encoding="utf-8-sig"))
        except ValueError as exc:
            raise ValueError(f"{f} is not valid JSON: {exc}")
        out = []
        for m in items:
            pw = secret(m.get("password_env") or "") if m.get("password_env") else None
            out.append({"email": m["email"].lower(), "name": m.get("name") or setting("SENDER_NAME"),
                        "smtp_host": m.get("smtp_host"), "smtp_port": int(m.get("smtp_port") or 587),
                        "smtp_user": m.get("smtp_user") or m["email"], "password": pw,
                        "imap_host": m.get("imap_host") or (m.get("smtp_host") or "").replace("smtp.", "imap.", 1) or None,
                        "imap_port": int(m.get("imap_port") or 993), "imap_user": m.get("imap_user") or m.get("smtp_user") or m["email"],
                        "imap_password": secret(m["imap_password_env"]) if m.get("imap_password_env") else pw,
                        "daily_limit": int(m.get("daily_limit") or setting("DAILY_SEND_LIMIT", "30")),
                        "started": m.get("started"), "reply_to": m.get("reply_to")})
        return [m for m in out if m["smtp_host"] and m["password"]]
    sender = setting("SENDER_EMAIL")
    host, pw = setting("SMTP_HOST"), secret("SMTP_PASSWORD")
    if not (sender and host and pw):
        return []
    return [{"email": sender.lower(), "name": setting("SENDER_NAME"), "smtp_host": host, "smtp_port": int(setting("SMTP_PORT", "587")),
             "smtp_user": setting("SMTP_USER") or sender, "password": pw, "imap_host": None, "imap_port": 993, "imap_user": None,
             "imap_password": None, "daily_limit": int(setting("DAILY_SEND_LIMIT", "30")), "started": setting("SENDING_STARTED"),
             "reply_to": setting("REPLY_TO")}]


def limit_today(m, now=None):
    """The mailbox's limit today: 5/day for its first two weeks, then +5 per week, up to its daily_limit."""
    cap = int(m["daily_limit"])
    if m.get("started"):
        try:
            weeks = max(0, ((now or datetime.now(timezone.utc)).date() - datetime.fromisoformat(m["started"]).date()).days // 7)
            return min(cap, 5 if weeks < 2 else 5 + 5 * (weeks - 1))
        except ValueError:
            pass
    return cap


def sent_today(conn, email, now=None):
    day = (now or datetime.now(timezone.utc)).date().isoformat()
    return conn.execute("SELECT COUNT(*) FROM touches WHERE status = 'sent' AND lower(COALESCE(sender, '')) = ? AND at >= ?",
                        (email.lower(), day)).fetchone()[0]


def capacity(conn, now=None):
    out = []
    for m in load():
        lim, used = limit_today(m, now), sent_today(conn, m["email"], now)
        out.append({"email": m["email"], "limit_today": lim, "sent_today": used, "room": max(0, lim - used),
                    "imap": bool(m.get("imap_host") and m.get("imap_password"))})
    return out


def pick(conn, prospect_id, now=None):
    """(mailbox, reason). Sticky: a prospect already emailed keeps its mailbox (or waits if it's full today)."""
    boxes = {m["email"]: m for m in load()}
    if not boxes:
        return None, "no mailbox configured (SMTP_* in .env, or mailboxes.json)"
    last = conn.execute("SELECT sender FROM touches WHERE prospect_id = ? AND channel = 'email' AND status = 'sent' AND sender IS NOT NULL "
                        "ORDER BY id DESC LIMIT 1", (prospect_id,)).fetchone()
    if last and last[0] and last[0].lower() in boxes:
        m = boxes[last[0].lower()]
        if sent_today(conn, m["email"], now) >= limit_today(m, now):
            return None, f"{m['email']} (this prospect's mailbox) is at today's limit — the follow-up waits a day"
        return m, "same mailbox as earlier emails to this prospect"
    room = sorted(((limit_today(m, now) - sent_today(conn, m["email"], now), m) for m in boxes.values()), key=lambda x: -x[0])
    if room[0][0] <= 0:
        return None, "every mailbox is at today's limit"
    return room[0][1], f"most room left today ({room[0][0]})"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sending mailboxes: rotation, per-mailbox limits and warm-up.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list"); sub.add_parser("example")
    a = ap.parse_args(argv)
    if a.cmd == "example":
        emit({"ok": True, "data": {"file": str(_file()), "example": EXAMPLE,
                                   "note": "Put each password in ~/.ai-sales-team/.env under the password_env name (app passwords)."}})
    import pipeline
    conn = pipeline.connect()
    try:
        emit({"ok": True, "data": {"mailboxes": capacity(conn), "file": str(_file()) if _file().exists() else None}})
    finally:
        conn.close()


if __name__ == "__main__":
    main()

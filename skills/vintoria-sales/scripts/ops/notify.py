#!/usr/bin/env python3
"""
Instant alerts to your phone: a fresh buyer post, a reply, a booked meeting — the moments where minutes decide the
deal. Sends a short message to Telegram, Slack and/or Discord (whichever is configured). Nothing else leaves the
machine: lead text is trimmed to a one-line preview plus its link.

Settings (env or ~/.ai-sales-team/.env):
    TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID   (create a bot with @BotFather; send it a message; chat id via getUpdates)
    SLACK_WEBHOOK_URL                       (Slack → Apps → Incoming Webhooks)
    DISCORD_WEBHOOK_URL                     (Channel settings → Integrations → Webhooks)
    ALERT_ON=fresh_leads,replies,bookings   (default: all three)

Usage:
    python notify.py test                   # send a test message to every configured channel
    python notify.py send "text"            # send any message
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import api_json, emit, secret, setting  # noqa: E402


def channels():
    out = []
    if secret("TELEGRAM_BOT_TOKEN") and setting("TELEGRAM_CHAT_ID"):
        out.append("telegram")
    if secret("SLACK_WEBHOOK_URL"):
        out.append("slack")
    if secret("DISCORD_WEBHOOK_URL"):
        out.append("discord")
    return out


def enabled(kind):
    on = [x.strip() for x in setting("ALERT_ON", "fresh_leads,replies,bookings").split(",")]
    return kind in on


def send(text, call=api_json):
    """Send to every configured channel. Returns {channel: 'ok' | error}. Never raises."""
    text = (text or "")[:3500]
    res = {}
    for ch in channels():
        try:
            if ch == "telegram":
                st, d = call("POST", f"https://api.telegram.org/bot{secret('TELEGRAM_BOT_TOKEN')}/sendMessage", timeout=20, retries=1,
                             body={"chat_id": setting("TELEGRAM_CHAT_ID"), "text": text, "disable_web_page_preview": True})
            elif ch == "slack":
                st, d = call("POST", secret("SLACK_WEBHOOK_URL"), body={"text": text}, timeout=20, retries=1)
            else:
                st, d = call("POST", secret("DISCORD_WEBHOOK_URL"), body={"content": text[:1900]}, timeout=20, retries=1)
            res[ch] = "ok" if st < 300 else f"HTTP {st}"
        except Exception as exc:  # noqa: BLE001 - an alert must never break the run that sent it
            res[ch] = f"{type(exc).__name__}: {exc}"
    return res


def fresh_leads_text(leads, limit=5):
    lines = [f"🔥 {len(leads)} fresh buyer post{'s' if len(leads) != 1 else ''}"]
    for x in leads[:limit]:
        age = f"{x['age_hours']:g}h ago" if x.get("age_hours") is not None else "age ?"
        who = x.get("author") or x.get("platform") or ""
        preview = (x.get("title") or "")[:80]
        lines.append(f"• {age} · {who} · {preview}\n  {x.get('url')}")
    lines.append("Judge them now: vintoria-lead-hunt (pipeline.py today).")
    return "\n".join(lines)


def replies_text(items):
    lines = [f"📬 {len(items)} new repl{'ies' if len(items) != 1 else 'y'}"]
    for i in items[:6]:
        lines.append(f"• {i.get('prospect')} — {i.get('category')}: {(i.get('excerpt') or '')[:90]}")
    lines.append("Answer within the hour: vintoria-reply-book.")
    return "\n".join(lines)


def bookings_text(items):
    return "\n".join([f"📅 {len(items)} meeting{'s' if len(items) != 1 else ''} booked"] +
                     [f"• {i.get('prospect')} via {i.get('tool')} at {i.get('start_utc') or 'time to confirm'}" for i in items])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Alerts to Telegram / Slack / Discord.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("test")
    s = sub.add_parser("send"); s.add_argument("text")
    a = ap.parse_args(argv)
    if not channels():
        emit({"ok": False, "error": "no alert channel — set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID, SLACK_WEBHOOK_URL or DISCORD_WEBHOOK_URL"}, 2)
    text = "✅ AI Sales Team alerts are working." if a.cmd == "test" else a.text
    emit({"ok": True, "data": {"sent": send(text)}})


if __name__ == "__main__":
    main()

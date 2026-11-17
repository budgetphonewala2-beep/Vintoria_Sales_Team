#!/usr/bin/env python3
"""
One command to keep the machine running — schedule it every 30-60 minutes:

    python autopilot.py tick            # check inbox (apply), then dry-run the due sequence emails
    python autopilot.py tick --send     # ... and really send the due, pre-approved emails (or AUTO_SEND=1)
    python autopilot.py schedule        # print the cron / Windows Task Scheduler line for this machine

Each tick, in this order (a reply always wins over a follow-up):
  1. inbox.py   — new replies/bounces → pipeline (sequences stop, opt-outs suppressed); with AUTO_REPLY=1 a
                  "let's talk" reply gets your booking link straight away
  2. serp.py watch — every HUNT_EVERY_HOURS (default 2, needs BRIGHTDATA_API_KEY; 0 = off): the newest posts from
                  buyers since the last watch, queued as fresh leads at the top of the agenda (HUNT_MAX_QUERIES per run)
  3. outreach.py run — every approved sequence email that is due, inside SEND_HOURS, under DAILY_SEND_LIMIT
  4. notify.py — a Telegram / Slack / Discord ping for fresh leads, replies and bookings (if configured)
  5. pipeline.py today — what still needs you (replies, fresh leads to judge, meetings to prep, new leads)
Only emails you approved with `outreach.py approve` are ever sent. A lock file stops overlapping runs.
"""

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
import inbox  # noqa: E402
import outreach  # noqa: E402
import pipeline  # noqa: E402
from sales_common import data_home, emit, setting  # noqa: E402

ON = ("1", "true", "yes", "on")


def _lock():
    path = data_home() / "autopilot.lock"
    if path.exists() and time.time() - path.stat().st_mtime < 30 * 60:
        return None
    path.write_text(str(os.getpid()), encoding="utf-8")
    return path


def hunt_if_due(now=None, call=None):
    """Run serp.py watch when HUNT_EVERY_HOURS have passed since the last watch."""
    import serp
    from datetime import datetime, timezone
    every = float(setting("HUNT_EVERY_HOURS", "2") or 0)
    if every <= 0:
        return {"skipped": "HUNT_EVERY_HOURS=0"}
    if not serp.configured():
        return {"skipped": "no BRIGHTDATA_API_KEY"}
    now = now or datetime.now(timezone.utc)
    last = serp.load_fresh().get("last_watch")
    if last and (now - datetime.fromisoformat(last)).total_seconds() < every * 3600:
        return {"skipped": f"last watch {last}, next after {every:g} h"}
    try:
        kw = {"call": call} if call else {}
        r = serp.watch(int(setting("HUNT_MAX_QUERIES", "12")), 1, now=now, **kw)
        return {k: r[k] for k in ("window_hours", "new_buyers", "rejected", "excluded_market", "queries_run", "errors", "leads")}
    except Exception as exc:  # noqa: BLE001 - a hunting problem must never stop replies or sends
        return {"error": f"{type(exc).__name__}: {exc}"}


def alert(out, call=None):
    """Telegram / Slack / Discord ping for fresh leads, replies and bookings found in this tick."""
    import notify
    if not notify.channels():
        return None
    kw = {"call": call} if call else {}
    sent = {}
    h = out.get("hunt") or {}
    if h.get("new_buyers") and notify.enabled("fresh_leads"):
        sent["fresh_leads"] = notify.send(notify.fresh_leads_text(h.get("leads") or []), **kw)
    ib = out.get("inbox") or {}
    reps = [m for m in ib.get("matched") or [] if m.get("category") not in ("meeting_booked", "out_of_office", "bounce")]
    if reps and notify.enabled("replies"):
        sent["replies"] = notify.send(notify.replies_text(reps), **kw)
    if ib.get("bookings") and notify.enabled("bookings"):
        sent["bookings"] = notify.send(notify.bookings_text(ib["bookings"]), **kw)
    return sent or None


def tick(conn, send=False, auto_reply=False, fetch=None, smtp=None, now=None, hunt_call=None, alert_call=None):
    out = {"inbox": None, "hunt": None, "sequences": None, "today": None, "notes": []}
    try:
        msgs = fetch() if fetch else inbox.fetch_all(days=int(setting("INBOX_DAYS", "7")))
        out["inbox"] = inbox.check(conn, msgs, apply=True, auto_reply=auto_reply, smtp=smtp, now=now)
    except inbox.UserError as exc:
        out["notes"].append(f"inbox skipped: {exc} — paste replies into vintoria-reply-book instead, or sequences can't stop on reply")
        if send:
            out["notes"].append("NOT sending: without an inbox check a prospect who replied could get a follow-up. "
                                "Configure IMAP or run outreach.py run --send yourself after checking replies.")
            send = False
    except Exception as exc:  # noqa: BLE001 - IMAP/network errors: never send blind
        out["notes"].append(f"inbox error: {type(exc).__name__}: {exc} — not sending this run")
        send = False
    out["hunt"] = hunt_if_due(now=now, call=hunt_call)
    out["alerts"] = alert(out, alert_call)
    out["sequences"] = outreach.run(conn, really=send, now=now, smtp=smtp or outreach.smtplib)
    agenda = pipeline.today_agenda(conn)
    out["today"] = {"counts": agenda["counts"], "top": agenda["items"][:8], "tip": agenda["tip"]}
    return out


def schedule_lines():
    py = sys.executable
    me = str(Path(__file__).resolve())
    return {
        "linux_mac_cron": f"*/30 * * * * \"{py}\" \"{me}\" tick --send >> ~/.ai-sales-team/autopilot.log 2>&1",
        "how_cron": "crontab -e, paste the line, save. Remove --send for dry runs.",
        "windows": f'schtasks /Create /SC MINUTE /MO 30 /TN "AI Sales Autopilot" /TR "\\"{py}\\" \\"{me}\\" tick --send"',
        "how_windows": "Run once in Command Prompt. Delete with: schtasks /Delete /TN \"AI Sales Autopilot\"",
        "note": "The computer must be on. For always-on, run it on a small VPS with the same ~/.ai-sales-team folder.",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Inbox → due sequence emails → today's agenda, in one run.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick"); t.add_argument("--send", action="store_true"); t.add_argument("--auto-reply", action="store_true")
    sub.add_parser("schedule")
    a = ap.parse_args(argv)
    if a.cmd == "schedule":
        emit({"ok": True, "data": schedule_lines()})
    lock = _lock()
    if not lock:
        emit({"ok": True, "data": {"skipped": "another autopilot run is in progress (lock < 30 min old)"}})
    conn = pipeline.connect()
    try:
        send = a.send or setting("AUTO_SEND", "0").lower() in ON
        auto = a.auto_reply or setting("AUTO_REPLY", "0").lower() in ON
        emit({"ok": True, "data": tick(conn, send, auto)})
    finally:
        conn.close()
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Persistent sales pipeline (SQLite, standard library only).

Every skill records what it learns here, so the pipeline survives across sessions and agents
instead of living only in loose Markdown files. Database: <data home>/pipeline.db where the data
home is $AI_SALES_HOME or ~/.ai-sales-team.

Usage (every command prints one JSON object):
    python pipeline.py add --url https://acme.com [--name "Acme"] [--source hunt:li-posts] [--services web,seo]
    python pipeline.py list [--stage contacted] [--min-score 60]
    python pipeline.py show acme.com
    python pipeline.py stage acme.com contacted --reason "first email sent"
    python pipeline.py score acme.com 78 --breakdown '{"company_fit": 80, "contact_access": 70}'
    python pipeline.py note acme.com "Owner prefers WhatsApp"
    python pipeline.py contact acme.com --name "Priya Mehta" --title Founder --email priya@acme.com \
        --email-status verified --source hunter
    python pipeline.py attach acme.com prospects/acme.com/PROSPECT-ANALYSIS.md --kind prospect-analysis
    python pipeline.py next acme.com "Send follow-up #1 on Thursday" [--due 2026-11-06]
    python pipeline.py report [--pdf-input out.json]     # funnel + stale deals + next actions
    python pipeline.py remove acme.com                   # delete a prospect and its records
    python pipeline.py status                            # START HERE: setup, keys, funnel, queue, sending health, next action
    python pipeline.py today                             # the day's agenda: replies, meetings, follow-ups, new leads
    python pipeline.py find priya@acme.com               # which prospect is this? (email, name, domain)
    python pipeline.py where acme.com --country US --tz America/Chicago   # where they are (send times, slots)
    python pipeline.py value acme.com 6000 --currency USD                  # deal value → forecast in the report
    python pipeline.py suppress priya@acme.com --reason "asked not to be contacted"   # or a whole domain: acme.com
    python pipeline.py suppressed                        # list the do-not-contact list

Touches (emails/DMs/calls) are logged with outreach.py, meetings with meeting.py, replies with reply_triage.py —
all in this same database.

Stages: new, researched, qualified, contacted, replied, meeting, proposal, won, lost, nurture,
disqualified. Any move is allowed (sales is messy) but every move is recorded with a reason.
"""

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _vpath  # noqa: E402,F401  (puts every scripts/<group>/ folder on sys.path)
from sales_common import data_home, domain_slug, emit  # noqa: E402

STAGES = ["new", "researched", "qualified", "contacted", "replied", "meeting", "proposal",
          "won", "lost", "nurture", "disqualified"]
OPEN = ["new", "researched", "qualified", "contacted", "replied", "meeting", "proposal", "nurture"]
EMAIL_STATUS = ["verified", "catch_all", "unverified", "pattern-guessed", "invalid"]
STALE_DAYS = {"contacted": 7, "replied": 2, "meeting": 3, "proposal": 5, "qualified": 5, "researched": 7}

SCHEMA = """
CREATE TABLE IF NOT EXISTS prospects (
    id INTEGER PRIMARY KEY, slug TEXT UNIQUE NOT NULL, name TEXT, url TEXT, stage TEXT NOT NULL DEFAULT 'new',
    score REAL, grade TEXT, breakdown_json TEXT, source TEXT, services TEXT, next_action TEXT, next_due TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY, prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    name TEXT, title TEXT, email TEXT, email_status TEXT, email_source TEXT, linkedin TEXT, phone TEXT, role TEXT,
    created_at TEXT NOT NULL, UNIQUE(prospect_id, name));
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY, prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    kind TEXT NOT NULL, from_stage TEXT, to_stage TEXT, text TEXT, at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY, prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    kind TEXT, path TEXT, created_at TEXT NOT NULL, UNIQUE(prospect_id, path));
CREATE TABLE IF NOT EXISTS touches (
    id INTEGER PRIMARY KEY, prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    channel TEXT NOT NULL, step INTEGER, recipient TEXT, subject TEXT, body_path TEXT, status TEXT NOT NULL,
    message_id TEXT, at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY, prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    starts_at TEXT NOT NULL, minutes INTEGER NOT NULL, tz TEXT, title TEXT, attendee TEXT, link TEXT,
    status TEXT NOT NULL DEFAULT 'scheduled', ics_path TEXT, uid TEXT, notes TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sequence_steps (
    id INTEGER PRIMARY KEY, prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    step INTEGER NOT NULL, recipient TEXT NOT NULL, subject TEXT, body TEXT NOT NULL, status TEXT NOT NULL,
    due TEXT, evidence_json TEXT, message_id TEXT, sent_at TEXT, note TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS inbox_seen (
    message_id TEXT PRIMARY KEY, prospect_id INTEGER, category TEXT, at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS suppression (
    value TEXT PRIMARY KEY, reason TEXT, at TEXT NOT NULL);
"""


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def grade_for(score):
    s = float(score)
    return "A+" if s >= 90 else "A" if s >= 75 else "B" if s >= 60 else "C" if s >= 40 else "D"


def connect(path=None):
    conn = sqlite3.connect(str(path or data_home() / "pipeline.db"), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(prospects)")}
    for col, typ in (("country", "TEXT"), ("tz", "TEXT"), ("value", "REAL"), ("currency", "TEXT")):  # migrate in place
        if col not in cols:
            conn.execute(f"ALTER TABLE prospects ADD COLUMN {col} {typ}")
    for table, col, typ in (("sequence_steps", "variant", "TEXT"), ("sequence_steps", "hook", "TEXT"),
                            ("sequence_steps", "quality", "INTEGER"), ("touches", "sender", "TEXT"),
                            ("sequence_steps", "sender", "TEXT")):
        if col not in {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
    return conn


TLD_COUNTRY = {".co.uk": "UK", ".uk": "UK", ".com.au": "AU", ".au": "AU", ".ca": "CA", ".co.nz": "NZ", ".nz": "NZ",
               ".ie": "IE", ".ae": "AE", ".sg": "SG", ".de": "DE", ".nl": "NL", ".in": "IN", ".co.in": "IN", ".us": "US"}


def infer_country(slug):
    s = (slug or "").lower()
    for tld in sorted(TLD_COUNTRY, key=len, reverse=True):
        if s.endswith(tld):
            return TLD_COUNTRY[tld]
    return None


# Probability a deal at this stage closes (for the weighted forecast). Rough agency defaults; override with STAGE_ODDS.
STAGE_ODDS = {"new": 0.01, "researched": 0.02, "qualified": 0.05, "contacted": 0.05, "replied": 0.15, "meeting": 0.3,
              "proposal": 0.5, "nurture": 0.03, "won": 1.0, "lost": 0.0, "disqualified": 0.0}


def set_value(conn, key, value, currency=None):
    v = float(value)
    if v < 0:
        raise UserError("value must be ≥ 0")
    p = get(conn, key)
    cur = (currency or p.get("currency") or "USD").upper()
    with conn:
        conn.execute("UPDATE prospects SET value = ?, currency = ?, updated_at = ? WHERE id = ?", (v, cur, now(), p["id"]))
        event(conn, p["id"], "value", f"{v:g} {cur}")
    return {"prospect": p["slug"], "value": v, "currency": cur}


def forecast(rows):
    out = {}
    for r in rows:
        if not r.get("value"):
            continue
        c = out.setdefault(r.get("currency") or "USD", {"open": 0.0, "weighted": 0.0, "won": 0.0, "deals_with_value": 0})
        c["deals_with_value"] += 1
        if r["stage"] == "won":
            c["won"] += r["value"]
        elif r["stage"] in OPEN:
            c["open"] += r["value"]
            c["weighted"] += r["value"] * STAGE_ODDS.get(r["stage"], 0)
    return {k: {kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in out.items()}


def set_where(conn, key, country=None, tz=None):
    p = get(conn, key)
    if tz:
        import meeting
        tz = meeting.tz(tz).key
    with conn:
        conn.execute("UPDATE prospects SET country = COALESCE(?, country), tz = COALESCE(?, tz), updated_at = ? WHERE id = ?",
                     ((country or "").upper() or None, tz, now(), p["id"]))
    return {"prospect": p["slug"], "country": (country or "").upper() or p.get("country"), "tz": tz or p.get("tz")}


class UserError(Exception):
    pass


# Hosts that are platforms, not the prospect's own website: a post URL there must never become the prospect's
# identity (every LinkedIn lead would otherwise merge into one prospect called "linkedin.com").
PLATFORM_HOSTS = {"linkedin.com": "linkedin", "lnkd.in": "linkedin", "reddit.com": "reddit", "x.com": "x", "twitter.com": "x",
                  "facebook.com": "facebook", "fb.com": "facebook", "instagram.com": "instagram", "news.ycombinator.com": "hn",
                  "producthunt.com": "producthunt", "upwork.com": "upwork", "quora.com": "quora", "indiehackers.com": "indiehackers",
                  "youtube.com": "youtube", "medium.com": "medium", "github.com": "github", "threads.net": "threads",
                  "google.com": "google", "maps.google.com": "google", "goo.gl": "google", "t.co": "x", "wa.me": "whatsapp"}


def platform_of_url(value):
    v = (value or "").strip()
    if "." not in v or " " in v:
        return None
    host = domain_slug(v)
    return next((tag for h, tag in PLATFORM_HOSTS.items() if host == h or host.endswith("." + h)), None)


def _name_slug(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def platform_slug(url, name=None):
    """'https://linkedin.com/posts/anita-desai_need-…' + 'Anita Desai' → 'anita-desai@linkedin'."""
    tag = platform_of_url(url)
    base = _name_slug(name)
    if not base:
        u = url.split("://")[-1]
        rules = [r"linkedin\.com/(?:posts|in|company)/([^/_?]+)", r"reddit\.com/(?:r/[^/]+/)?comments/([a-z0-9]+)",
                 r"reddit\.com/u(?:ser)?/([^/?]+)", r"(?:x|twitter)\.com/([^/?]+)/status", r"ycombinator\.com/item\?id=(\d+)",
                 r"ycombinator\.com/user\?id=([^&]+)", r"upwork\.com/.*?(~[0-9a-f]+)", r"producthunt\.com/(?:posts|products)/([^/?]+)",
                 r"facebook\.com/groups/[^/]+/(?:posts|permalink)/(\d+)", r"[^/]+/([^/?#]+)"]
        m = next((re.search(rx, u, re.I) for rx in rules if re.search(rx, u, re.I)), None)
        tok = m.group(1) if m else "lead"
        base = (f"post-{tok}" if tok.isdigit() or ("reddit" in u and "comments" in u) else _name_slug(tok))[:48] or "lead"
    return f"{base}@{tag}"


def _slug(value):
    v = (value or "").strip()
    if not v:
        raise UserError("prospect is required (domain, URL or id)")
    if v.isdigit() or "@" in v and "." not in v.split("@")[-1]:
        return v.lower()                                     # id, or an existing platform slug like anita-desai@linkedin
    if platform_of_url(v):
        return platform_slug(v)
    return domain_slug(v) if "." in v and " " not in v else _name_slug(v)


def get(conn, key):
    k = _slug(key)
    r = conn.execute("SELECT * FROM prospects WHERE id = ? OR slug = ?", (int(k) if k.isdigit() else -1, k)).fetchone()
    if not r:
        raise UserError(f"prospect '{key}' not found — add it first: pipeline.py add --url <url>")
    return dict(r)


def event(conn, pid, kind, text="", frm=None, to=None):
    conn.execute("INSERT INTO events(prospect_id, kind, from_stage, to_stage, text, at) VALUES (?,?,?,?,?,?)",
                 (pid, kind, frm, to, text, now()))


def touch(conn, pid):
    conn.execute("UPDATE prospects SET updated_at = ? WHERE id = ?", (now(), pid))


def _qnorm(t):
    t = (t or "").lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s'$%.,-]", " ", t)).strip()


def quote_in(post, quote):
    """True when the quote appears word for word in the post (case, quotes and spacing ignored)."""
    q = _qnorm(quote).strip(" .,")
    return bool(q) and q in _qnorm(post)


def add(conn, url=None, name=None, source=None, services=None, stage="new", quote=None, post=None):
    if not url and not name:
        raise UserError("give --url or --name")
    if quote is not None:
        if not post:
            raise UserError("--quote needs the post itself (--post-text or --post-file) so the quote can be checked")
        if not quote_in(post, quote):
            raise UserError("the quote is not word-for-word in the post — copy it exactly (no paraphrase); nothing was saved")
    if stage not in STAGES:
        raise UserError(f"stage must be one of {STAGES}")
    slug = platform_slug(url, name) if url and platform_of_url(url) else _slug(url or name)
    r = conn.execute("SELECT * FROM prospects WHERE slug = ?", (slug,)).fetchone()
    if r:
        with conn:
            conn.execute("""UPDATE prospects SET name = COALESCE(?, name), url = COALESCE(?, url),
                            source = COALESCE(source, ?), services = COALESCE(?, services), updated_at = ? WHERE id = ?""",
                         (name, url, source, services, now(), r["id"]))
        return {"created": False, "prospect": get(conn, slug)}
    ts = now()
    with conn:
        cur = conn.execute("""INSERT INTO prospects(slug, name, url, stage, source, services, created_at, updated_at, country)
                              VALUES (?,?,?,?,?,?,?,?,?)""", (slug, name, url, stage, source, services, ts, ts, infer_country(slug)))
        event(conn, cur.lastrowid, "stage", "added" + (f" from {source}" if source else ""), None, stage)
        if quote:
            event(conn, cur.lastrowid, "note", f"Post: {url or ''} — quote (verified verbatim): \"{quote.strip()}\"")
    return {"created": True, "prospect": get(conn, slug)}


def set_stage(conn, key, stage, reason=""):
    if stage not in STAGES:
        raise UserError(f"stage must be one of {STAGES}")
    p = get(conn, key)
    if p["stage"] == stage:
        return {"changed": False, "prospect": p}
    with conn:
        conn.execute("UPDATE prospects SET stage = ?, updated_at = ? WHERE id = ?", (stage, now(), p["id"]))
        event(conn, p["id"], "stage", reason, p["stage"], stage)
    return {"changed": True, "from": p["stage"], "to": stage, "prospect": get(conn, key)}


def set_score(conn, key, score, breakdown=None):
    s = float(score)
    if not 0 <= s <= 100:
        raise UserError("score must be 0-100")
    p = get(conn, key)
    with conn:
        conn.execute("UPDATE prospects SET score = ?, grade = ?, breakdown_json = COALESCE(?, breakdown_json), updated_at = ? "
                     "WHERE id = ?", (s, grade_for(s), json.dumps(breakdown) if breakdown else None, now(), p["id"]))
        event(conn, p["id"], "score", f"{s:g} ({grade_for(s)})")
    return {"prospect": get(conn, key)}


def add_contact(conn, key, name, **fields):
    if fields.get("email_status") and fields["email_status"] not in EMAIL_STATUS:
        raise UserError(f"email-status must be one of {EMAIL_STATUS}")
    warnings = []
    if fields.get("email_status") == "verified" and fields.get("email"):
        import os
        import find_email
        if not find_email.verified_in_log(fields["email"]) and os.environ.get("AI_SALES_TRUST_VERIFIED") != "1":
            fields["email_status"] = "unverified"     # 'verified' must come from a verifier, not from whoever typed it
            warnings.append(f"{fields['email']} has no verification on record — saved as unverified; run "
                            "find_email.py --email <address> to verify it")
    p = get(conn, key)
    cols = ["title", "email", "email_status", "email_source", "linkedin", "phone", "role"]
    vals = [fields.get(c) for c in cols]
    with conn:
        conn.execute(f"""INSERT INTO contacts(prospect_id, name, {', '.join(cols)}, created_at) VALUES (?,?,{','.join('?' * len(cols))},?)
                         ON CONFLICT(prospect_id, name) DO UPDATE SET """ +
                     ", ".join(f"{c} = COALESCE(excluded.{c}, {c})" for c in cols),
                     (p["id"], name, *vals, now()))
        touch(conn, p["id"])
    out = {"prospect": p["slug"], "contacts": contacts(conn, p["id"])}
    if warnings:
        out["warnings"] = warnings
    return out


def contacts(conn, pid):
    return [dict(r) for r in conn.execute("SELECT * FROM contacts WHERE prospect_id = ? ORDER BY id", (pid,))]


def show(conn, key):
    p = get(conn, key)
    p["breakdown"] = json.loads(p.pop("breakdown_json") or "null")
    p["contacts"] = contacts(conn, p["id"])
    p["artifacts"] = [dict(r) for r in conn.execute("SELECT kind, path, created_at FROM artifacts WHERE prospect_id = ?", (p["id"],))]
    p["history"] = [dict(r) for r in conn.execute("SELECT kind, from_stage, to_stage, text, at FROM events WHERE prospect_id = ? "
                                                  "ORDER BY id", (p["id"],))]
    return p


def listing(conn, stage=None, min_score=None):
    q, params = "SELECT id, slug, name, stage, score, grade, next_action, next_due, updated_at FROM prospects WHERE 1=1", []
    if stage:
        q += " AND stage = ?"
        params.append(stage)
    if min_score is not None:
        q += " AND COALESCE(score, 0) >= ?"
        params.append(min_score)
    return [dict(r) for r in conn.execute(q + " ORDER BY COALESCE(score, -1) DESC, updated_at DESC", params)]


def report(conn, today=None):
    today = today or datetime.now(timezone.utc)
    rows = [dict(r) for r in conn.execute("SELECT * FROM prospects")]
    funnel = {s: sum(1 for r in rows if r["stage"] == s) for s in STAGES}
    stale, due = [], []
    for r in rows:
        limit = STALE_DAYS.get(r["stage"])
        age = (today - datetime.fromisoformat(r["updated_at"])).days
        if limit and age >= limit:
            stale.append({"prospect": r["slug"], "stage": r["stage"], "days_idle": age})
        if r["next_due"] and r["next_due"] <= today.date().isoformat() and r["stage"] in OPEN:
            due.append({"prospect": r["slug"], "next_action": r["next_action"], "due": r["next_due"]})
    scored = [r for r in rows if r["score"] is not None]
    reached = {}
    for e in conn.execute("SELECT prospect_id, to_stage FROM events WHERE kind = 'stage'"):
        reached.setdefault(e["to_stage"], set()).add(e["prospect_id"])
    contacted = len(reached.get("contacted", set()))
    conv = {"reply_rate_pct": round(100 * len(reached.get("replied", set())) / contacted, 1) if contacted else None,
            "meeting_rate_pct": round(100 * len(reached.get("meeting", set())) / contacted, 1) if contacted else None,
            "win_rate_pct": round(100 * funnel["won"] / max(1, funnel["won"] + funnel["lost"]), 1) if funnel["won"] + funnel["lost"] else None}
    by_source = {}
    for r in rows:
        src = (r["source"] or "manual").split(":")[0]
        b = by_source.setdefault(src, {"prospects": 0, "meetings": 0, "won": 0})
        b["prospects"] += 1
        b["meetings"] += int(r["id"] in reached.get("meeting", set()))
        b["won"] += int(r["stage"] == "won")
    week_ago = (today - timedelta(days=7)).replace(microsecond=0).isoformat()
    activity = {"touches_7d": conn.execute("SELECT COUNT(*) FROM touches WHERE at >= ?", (week_ago,)).fetchone()[0],
                "meetings_booked_7d": conn.execute("SELECT COUNT(*) FROM meetings WHERE created_at >= ?", (week_ago,)).fetchone()[0],
                "meetings_upcoming": conn.execute("SELECT COUNT(*) FROM meetings WHERE status = 'scheduled' AND starts_at >= ?",
                                                  (today.replace(microsecond=0).isoformat(),)).fetchone()[0]}
    return {"total": len(rows), "open": sum(funnel[s] for s in OPEN), "funnel": funnel, "conversion": conv,
            "activity": activity, "forecast": forecast(rows),
            "avg_score": round(sum(r["score"] for r in scored) / len(scored), 1) if scored else None,
            "grades": {g: sum(1 for r in scored if r["grade"] == g) for g in ("A+", "A", "B", "C", "D")},
            "stale": sorted(stale, key=lambda x: -x["days_idle"]), "due_today": due, "by_source": by_source,
            "top": [{"prospect": r["slug"], "score": r["score"], "grade": r["grade"], "stage": r["stage"],
                     "next_action": r["next_action"]} for r in sorted(scored, key=lambda r: -r["score"])[:10]]}


def find(conn, text):
    """Prospects matching a slug, name, domain, contact name or contact email (e.g. the sender of a reply)."""
    t = f"%{(text or '').strip().lower()}%"
    rows = conn.execute("""SELECT DISTINCT p.id, p.slug, p.name, p.stage, p.url FROM prospects p LEFT JOIN contacts c ON c.prospect_id = p.id
                           WHERE lower(p.slug) LIKE ? OR lower(COALESCE(p.name,'')) LIKE ? OR lower(COALESCE(p.url,'')) LIKE ?
                           OR lower(COALESCE(c.email,'')) LIKE ? OR lower(COALESCE(c.name,'')) LIKE ? ORDER BY p.updated_at DESC LIMIT 10""",
                        (t, t, t, t, t)).fetchall()
    email_dom = text.split("@")[-1].lower() if "@" in (text or "") else None
    out = [dict(r) for r in rows]
    if not out and email_dom:
        out = [dict(r) for r in conn.execute("SELECT id, slug, name, stage, url FROM prospects WHERE slug = ?", (email_dom,))]
    return out


def suppress(conn, value, reason=""):
    v = (value or "").strip().lower()
    if not v:
        raise UserError("give an email address or a domain")
    with conn:
        conn.execute("INSERT OR REPLACE INTO suppression(value, reason, at) VALUES (?,?,?)", (v, reason, now()))
    return {"suppressed": v, "reason": reason}


def is_suppressed(conn, email_or_domain):
    """True if the address or its domain is on the do-not-contact list."""
    v = (email_or_domain or "").strip().lower()
    dom = v.split("@", 1)[1] if "@" in v else v
    r = conn.execute("SELECT value, reason FROM suppression WHERE value IN (?, ?)", (v, dom)).fetchone()
    return dict(r) if r else None


def today_agenda(conn, today=None):
    """Everything to do today, most valuable first: replies, meetings, follow-ups, stale deals, new leads."""
    now_dt = today or datetime.now(timezone.utc)
    d = now_dt.date().isoformat()
    tomorrow = (now_dt + timedelta(days=1)).date().isoformat()
    rows = {r["id"]: dict(r) for r in conn.execute("SELECT * FROM prospects")}
    items = []

    def add_item(priority, kind, p, action, skill, **extra):
        items.append({"priority": priority, "kind": kind, "prospect": p["slug"], "stage": p["stage"],
                      "action": action, "skill": skill, **extra})

    # 1. replies not answered yet (last reply event newer than the last touch)
    for pid, p in rows.items():
        last_reply = conn.execute("SELECT text, at FROM events WHERE prospect_id = ? AND kind = 'reply' ORDER BY id DESC LIMIT 1",
                                  (pid,)).fetchone()
        if not last_reply or p["stage"] in ("won", "lost", "disqualified"):
            continue
        last_touch = conn.execute("SELECT MAX(at) FROM touches WHERE prospect_id = ?", (pid,)).fetchone()[0]
        booked = conn.execute("SELECT 1 FROM meetings WHERE prospect_id = ? AND created_at >= ?", (pid, last_reply["at"])).fetchone()
        if not booked and (not last_touch or last_touch < last_reply["at"]):
            add_item(1, "reply", p, "Answer their reply — aim to book a call", "vintoria-reply-book",
                     reply=(last_reply["text"] or "")[:160])
    # 1b. fresh leads found by serp.py watch and not judged yet — minutes matter, so they come right after replies
    try:
        import serp
        fresh = serp.fresh_leads(48)
    except Exception:  # noqa: BLE001 - the agenda must never fail because of the lead store
        fresh = []
    if fresh:
        ages = [f.get("age_hours") for f in fresh if f.get("age_hours") is not None]
        newest = f"newest {min(ages):g} h old" if ages else "age unknown"
        items.append({"priority": 1, "kind": "fresh-leads", "prospect": None, "stage": None,
                      "action": f"Judge {len(fresh)} fresh lead{'s' if len(fresh) != 1 else ''} from serp.py watch ({newest}) — "
                                "answer real buyers within the hour", "skill": "vintoria-lead-hunt", "count": len(fresh)})
    # 2. meetings today / tomorrow (prep), meetings that happened with no outcome
    for m in conn.execute("SELECT * FROM meetings WHERE status = 'scheduled' ORDER BY starts_at"):
        p = rows.get(m["prospect_id"])
        if not p:
            continue
        day = m["starts_at"][:10]
        has_prep = conn.execute("SELECT 1 FROM artifacts WHERE prospect_id = ? AND kind = 'meeting-prep'", (p["id"],)).fetchone()
        if m["starts_at"] < now_dt.replace(microsecond=0).isoformat() and day <= d:
            add_item(2, "meeting-outcome", p, f"Meeting #{m['id']} ({m['starts_at']}) — record the outcome",
                     "vintoria-reply-book", meeting_id=m["id"])
        elif day in (d, tomorrow):
            add_item(2, "meeting", p, f"Meeting #{m['id']} at {m['starts_at']} UTC" + ("" if has_prep else " — prep brief missing"),
                     "vintoria-close" if not has_prep else "vintoria-reply-book", meeting_id=m["id"])
    # 3. due / overdue next actions (follow-ups from the cadence, proposals, ...)
    for p in rows.values():
        if p["next_due"] and p["next_due"] <= d and p["stage"] in OPEN:
            skill = "vintoria-outreach" if p["stage"] in ("contacted", "proposal") else \
                    "vintoria-outreach" if p["stage"] in ("new", "researched", "qualified") else "vintoria-sales"
            add_item(3, "due", p, p["next_action"] or "Next step", skill, due=p["next_due"],
                     overdue_days=(now_dt.date() - datetime.fromisoformat(p["next_due"]).date()).days)
    # 4. stale deals with nothing scheduled
    for s in report(conn, now_dt)["stale"]:
        p = next(r for r in rows.values() if r["slug"] == s["prospect"])
        if not (p["next_due"] and p["next_due"] >= d):
            add_item(4, "stale", p, f"Idle {s['days_idle']} days in {s['stage']} — re-engage or move to nurture/lost",
                     "vintoria-outreach")
    # 5. best untouched leads: the exact next step for each (scan → verify email → approve sequence)
    fresh = [p for p in rows.values() if p["stage"] in ("new", "researched", "qualified") and not p["next_due"]]
    for p in sorted(fresh, key=lambda r: -(r["score"] or 0))[:8]:
        cs = contacts(conn, p["id"])
        has_dossier = conn.execute("SELECT 1 FROM artifacts WHERE prospect_id = ? AND kind = 'dossier'", (p["id"],)).fetchone()
        queued = conn.execute("SELECT COUNT(*) FROM sequence_steps WHERE prospect_id = ? AND status IN ('approved','sent')",
                              (p["id"],)).fetchone()[0]
        verified = [c for c in cs if c.get("email_status") == "verified"]
        if queued:
            continue
        if not has_dossier and p["stage"] == "new":
            step = ("Deep scan: prospect_scan.py <url> (dossier + email + hooks)", "vintoria-prospect-research")
        elif not verified:
            step = ("Find/verify a decision-maker email (or reply where they posted)", "vintoria-prospect-research")
        else:
            step = (f"Write the 5-email sequence for {verified[0]['email']} and approve it", "vintoria-outreach")
        add_item(5, "new-lead", p, step[0], step[1], score=p["score"])
    seen, out = set(), []
    for it in sorted(items, key=lambda x: (x["priority"], -(x.get("overdue_days") or 0))):
        key = (it["kind"], it["prospect"], it.get("meeting_id"))
        if key not in seen:
            seen.add(key)
            out.append(it)
    sent_today = conn.execute("SELECT COUNT(*) FROM touches WHERE status = 'sent' AND at >= ?", (d,)).fetchone()[0]
    leads_open = sum(1 for p in rows.values() if p["stage"] in OPEN)
    tip = None
    if leads_open < 20:
        tip = f"Only {leads_open} open leads — run vintoria-lead-hunt to refill the top of the funnel."
    return {"date": d, "items": out, "counts": {k: sum(1 for i in out if i["kind"] == k) for k in
            ("reply", "fresh-leads", "meeting", "meeting-outcome", "due", "stale", "new-lead")},
            "emails_sent_today": sent_today, "open_leads": leads_open, "tip": tip}


def status(conn):
    """One call that never spends or blocks: setup, keys, funnel, queue, sending health, fresh leads, and the next action.
    Start here whenever you are unsure what state the user is in."""
    out = {"profile": None, "keys": {}, "funnel": {}, "queue": {}, "sending": None, "fresh_leads": 0, "next_action": None}
    try:
        import seller_profile
        c = seller_profile.check(seller_profile.load())
        out["profile"] = {"ready": c.get("next") == "Ready.", "complete_pct": c.get("complete_pct"), "missing": c.get("missing_required")}
    except Exception as exc:  # noqa: BLE001
        out["profile"] = {"error": str(exc)}
    from sales_common import secret
    out["keys"] = {"bright_data_serp": bool(secret("BRIGHTDATA_API_KEY")), "apify": bool(secret("APIFY_TOKEN")),
                   "apollo": bool(secret("APOLLO_API_KEY")),
                   "email_finder": any(secret(k) for k in ("PROSPEO_API_KEY", "FINDYMAIL_API_KEY", "HUNTER_API_KEY", "APOLLO_API_KEY")),
                   "email_verifier": any(secret(k) for k in ("MILLIONVERIFIER_API_KEY", "ZEROBOUNCE_API_KEY", "NEVERBOUNCE_API_KEY", "HUNTER_API_KEY"))}
    rep = report(conn)
    out["funnel"] = {k: v for k, v in rep["funnel"].items() if v}
    out["queue"] = {r["status"]: r["n"] for r in conn.execute("SELECT status, COUNT(*) n FROM sequence_steps GROUP BY status")}
    try:
        import outreach
        d = outreach.doctor(conn)
        out["sending"] = {"mode": d["mode"], "daily_limit_today": d["checks"]["daily_limit_today"], "warnings": d["warnings"]}
    except Exception as exc:  # noqa: BLE001
        out["sending"] = {"error": str(exc)}
    try:
        import serp
        out["fresh_leads"] = len(serp.fresh_leads(48))
        out["last_watch"] = serp.load_fresh().get("last_watch")
    except Exception:  # noqa: BLE001
        pass
    agenda = today_agenda(conn)
    if out["profile"] and not out["profile"].get("ready"):
        out["next_action"] = "Run vintoria-setup: the seller profile is incomplete"
    elif out["sending"] and any("PAUSED" in w for w in out["sending"].get("warnings") or []):
        out["next_action"] = out["sending"]["warnings"][0]
    elif agenda["items"]:
        i = agenda["items"][0]
        out["next_action"] = f"{i['action']} ({i['skill']})" + (f" — {i['prospect']}" if i.get("prospect") else "")
    elif not out["keys"]["bright_data_serp"] and not out["keys"]["apify"]:
        out["next_action"] = "Add BRIGHTDATA_API_KEY (SERP) to find leads, or paste posts into vintoria-lead-hunt"
    else:
        out["next_action"] = "Funnel is quiet: run serp.py watch (or vintoria-lead-hunt) for fresh leads"
    out["agenda_counts"] = agenda["counts"]
    return out


def pdf_input(conn):
    """Data in the shape generate_pdf_report.py expects."""
    rep = report(conn)
    prospects = []
    for r in conn.execute("SELECT * FROM prospects WHERE score IS NOT NULL ORDER BY score DESC"):
        prospects.append({"company": r["name"] or r["slug"], "url": r["url"] or f"https://{r['slug']}",
                          "score": r["score"], "grade": r["grade"], "stage": r["stage"],
                          "next_action": r["next_action"] or "", "component_scores": json.loads(r["breakdown_json"] or "{}")})
    actions = [{"company": d["prospect"], "action": d["next_action"], "urgency": "today"} for d in rep["due_today"]]
    actions += [{"company": s["prospect"], "action": f"Re-engage — idle {s['days_idle']} days in {s['stage']}", "urgency": "this week"}
                for s in rep["stale"][:8]]
    return {"date": datetime.now().date().isoformat(), "total_prospects": rep["total"], "prospects": prospects,
            "action_items": actions}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Persistent sales pipeline (SQLite).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("--url"); a.add_argument("--name"); a.add_argument("--source")
    a.add_argument("--quote", help="exact words from their post that prove intent (checked against --post-text/--post-file)")
    a.add_argument("--post-text"); a.add_argument("--post-file")
    a.add_argument("--services"); a.add_argument("--stage", default="new")
    l = sub.add_parser("list"); l.add_argument("--stage"); l.add_argument("--min-score", type=float)
    s = sub.add_parser("show"); s.add_argument("prospect")
    st = sub.add_parser("stage"); st.add_argument("prospect"); st.add_argument("stage"); st.add_argument("--reason", default="")
    sc = sub.add_parser("score"); sc.add_argument("prospect"); sc.add_argument("score", type=float); sc.add_argument("--breakdown")
    n = sub.add_parser("note"); n.add_argument("prospect"); n.add_argument("text")
    c = sub.add_parser("contact"); c.add_argument("prospect"); c.add_argument("--name", required=True)
    for f in ("title", "email", "email-status", "source", "linkedin", "phone", "role"):
        c.add_argument(f"--{f}")
    at = sub.add_parser("attach"); at.add_argument("prospect"); at.add_argument("path"); at.add_argument("--kind", default="file")
    nx = sub.add_parser("next"); nx.add_argument("prospect"); nx.add_argument("action"); nx.add_argument("--due")
    r = sub.add_parser("report"); r.add_argument("--pdf-input", help="also write generate_pdf_report.py input JSON here")
    rm = sub.add_parser("remove"); rm.add_argument("prospect")
    sub.add_parser("today")
    sub.add_parser("status")
    fd = sub.add_parser("find"); fd.add_argument("text", help="email, name, domain or part of it")
    va = sub.add_parser("value"); va.add_argument("prospect"); va.add_argument("value", type=float); va.add_argument("--currency")
    wh = sub.add_parser("where"); wh.add_argument("prospect"); wh.add_argument("--country"); wh.add_argument("--tz")
    su = sub.add_parser("suppress"); su.add_argument("value", help="email address or domain"); su.add_argument("--reason", default="")
    sub.add_parser("suppressed")
    args = ap.parse_args(argv)
    conn = connect()
    try:
        if args.cmd == "add":
            post = Path(args.post_file).read_text(encoding="utf-8-sig") if args.post_file else args.post_text
            out = add(conn, args.url, args.name, args.source, args.services, args.stage, args.quote, post)
        elif args.cmd == "list":
            out = {"prospects": listing(conn, args.stage, args.min_score)}
        elif args.cmd == "show":
            out = show(conn, args.prospect)
        elif args.cmd == "stage":
            out = set_stage(conn, args.prospect, args.stage, args.reason)
        elif args.cmd == "score":
            try:
                bd = json.loads(args.breakdown) if args.breakdown else None
            except json.JSONDecodeError as exc:
                raise UserError(f"--breakdown is not valid JSON: {exc}")
            out = set_score(conn, args.prospect, args.score, bd)
        elif args.cmd == "note":
            p = get(conn, args.prospect)
            with conn:
                event(conn, p["id"], "note", args.text)
                touch(conn, p["id"])
            out = {"prospect": p["slug"], "noted": args.text}
        elif args.cmd == "contact":
            out = add_contact(conn, args.prospect, args.name, title=args.title, email=args.email,
                              email_status=args.email_status, email_source=args.source, linkedin=args.linkedin,
                              phone=args.phone, role=args.role)
        elif args.cmd == "attach":
            p = get(conn, args.prospect)
            with conn:
                conn.execute("INSERT OR REPLACE INTO artifacts(prospect_id, kind, path, created_at) VALUES (?,?,?,?)",
                             (p["id"], args.kind, str(Path(args.path)), now()))
                touch(conn, p["id"])
            out = {"prospect": p["slug"], "attached": args.path}
        elif args.cmd == "next":
            p = get(conn, args.prospect)
            with conn:
                conn.execute("UPDATE prospects SET next_action = ?, next_due = ?, updated_at = ? WHERE id = ?",
                             (args.action, args.due, now(), p["id"]))
                event(conn, p["id"], "next", f"{args.action}" + (f" (due {args.due})" if args.due else ""))
            out = {"prospect": p["slug"], "next_action": args.action, "due": args.due}
        elif args.cmd == "report":
            out = report(conn)
            if args.pdf_input:
                Path(args.pdf_input).write_text(json.dumps(pdf_input(conn), indent=2), encoding="utf-8")
                out["pdf_input"] = args.pdf_input
        elif args.cmd == "remove":
            p = get(conn, args.prospect)
            with conn:
                conn.execute("DELETE FROM prospects WHERE id = ?", (p["id"],))
            out = {"removed": p["slug"]}
        elif args.cmd == "value":
            out = set_value(conn, args.prospect, args.value, args.currency)
        elif args.cmd == "where":
            try:
                out = set_where(conn, args.prospect, args.country, args.tz)
            except Exception as exc:  # noqa: BLE001 - bad time zone name
                raise UserError(str(exc))
        elif args.cmd == "status":
            out = status(conn)
        elif args.cmd == "find":
            out = {"matches": find(conn, args.text)}
        elif args.cmd == "today":
            out = today_agenda(conn)
        elif args.cmd == "suppress":
            out = suppress(conn, args.value, args.reason)
        elif args.cmd == "suppressed":
            out = {"suppressed": [dict(r) for r in conn.execute("SELECT * FROM suppression ORDER BY at DESC")]}
        emit({"ok": True, "data": out})
    except UserError as exc:
        emit({"ok": False, "error": str(exc)}, 2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

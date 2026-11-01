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

Stages: new, researched, qualified, contacted, replied, meeting, proposal, won, lost, nurture,
disqualified. Any move is allowed (sales is messy) but every move is recorded with a reason.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
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
    return conn


class UserError(Exception):
    pass


def _slug(value):
    v = (value or "").strip()
    if not v:
        raise UserError("prospect is required (domain, URL or id)")
    return v if v.isdigit() else (domain_slug(v) if "." in v else v.lower().replace(" ", "-"))


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


def add(conn, url=None, name=None, source=None, services=None, stage="new"):
    if not url and not name:
        raise UserError("give --url or --name")
    if stage not in STAGES:
        raise UserError(f"stage must be one of {STAGES}")
    slug = _slug(url or name)
    r = conn.execute("SELECT * FROM prospects WHERE slug = ?", (slug,)).fetchone()
    if r:
        with conn:
            conn.execute("""UPDATE prospects SET name = COALESCE(?, name), url = COALESCE(?, url),
                            source = COALESCE(source, ?), services = COALESCE(?, services), updated_at = ? WHERE id = ?""",
                         (name, url, source, services, now(), r["id"]))
        return {"created": False, "prospect": get(conn, slug)}
    ts = now()
    with conn:
        cur = conn.execute("""INSERT INTO prospects(slug, name, url, stage, source, services, created_at, updated_at)
                              VALUES (?,?,?,?,?,?,?,?)""", (slug, name, url, stage, source, services, ts, ts))
        event(conn, cur.lastrowid, "stage", "added" + (f" from {source}" if source else ""), None, stage)
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
    p = get(conn, key)
    cols = ["title", "email", "email_status", "email_source", "linkedin", "phone", "role"]
    vals = [fields.get(c) for c in cols]
    with conn:
        conn.execute(f"""INSERT INTO contacts(prospect_id, name, {', '.join(cols)}, created_at) VALUES (?,?,{','.join('?' * len(cols))},?)
                         ON CONFLICT(prospect_id, name) DO UPDATE SET """ +
                     ", ".join(f"{c} = COALESCE(excluded.{c}, {c})" for c in cols),
                     (p["id"], name, *vals, now()))
        touch(conn, p["id"])
    return {"prospect": p["slug"], "contacts": contacts(conn, p["id"])}


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
    return {"total": len(rows), "open": sum(funnel[s] for s in OPEN), "funnel": funnel, "conversion": conv,
            "avg_score": round(sum(r["score"] for r in scored) / len(scored), 1) if scored else None,
            "grades": {g: sum(1 for r in scored if r["grade"] == g) for g in ("A+", "A", "B", "C", "D")},
            "stale": sorted(stale, key=lambda x: -x["days_idle"]), "due_today": due, "by_source": by_source,
            "top": [{"prospect": r["slug"], "score": r["score"], "grade": r["grade"], "stage": r["stage"],
                     "next_action": r["next_action"]} for r in sorted(scored, key=lambda r: -r["score"])[:10]]}


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
    args = ap.parse_args(argv)
    conn = connect()
    try:
        if args.cmd == "add":
            out = add(conn, args.url, args.name, args.source, args.services, args.stage)
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
        emit({"ok": True, "data": out})
    except UserError as exc:
        emit({"ok": False, "error": str(exc)}, 2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

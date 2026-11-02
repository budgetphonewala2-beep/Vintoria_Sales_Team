#!/usr/bin/env python3
"""
Learning loop: which sources, queries, hooks, subject lines and steps actually turn into replies, meetings and wins —
and feed that back so the next hunt runs the winners first and stops paying for the losers.

Everything comes from the pipeline: prospects (source "serp:<query-id>", "maps:<search>", "apollo" ...), the approved
sequences (email 1's subject variant A/B, hook, quality score), touches, replies and meetings.

Usage:
    python learn.py report [--min 5]          # rates by source, query, platform, hook, subject variant, reply step, quality, country
    python learn.py report --apply            # also write learned.json: query weights + queries to drop (serp.py uses them)
    python learn.py ab                        # just the subject A/B test (two-proportion z-test)

A "positive" reply is meeting_request, interested, question, send_info or referral. Rates are per contacted prospect.
Small samples are flagged: nothing under --min contacted gets a verdict.
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline  # noqa: E402
from sales_common import data_home, emit  # noqa: E402

POSITIVE = ("meeting_request", "interested", "question", "send_info", "referral")
IGNORE = ("bounce", "out_of_office")


def rows(conn):
    """One record per contacted prospect with everything we can learn from."""
    out = []
    for p in conn.execute("SELECT * FROM prospects"):
        p = dict(p)
        first = conn.execute("SELECT MIN(at) FROM touches WHERE prospect_id = ? AND status IN ('sent','logged')",
                             (p["id"],)).fetchone()[0]
        if not first:
            continue
        s1 = conn.execute("SELECT * FROM sequence_steps WHERE prospect_id = ? AND step = 1 ORDER BY id DESC LIMIT 1",
                          (p["id"],)).fetchone()
        s1 = dict(s1) if s1 else {}
        replies = [dict(r) for r in conn.execute("SELECT text, at FROM events WHERE prospect_id = ? AND kind = 'reply' ORDER BY id",
                                                 (p["id"],))]
        cats = [(re.match(r"\[(\w+)\]", r["text"] or "") or [None, "unclear"])[1] for r in replies]
        real = [(c, r) for c, r in zip(cats, replies) if c not in IGNORE]
        reply_step = None
        if real:
            reply_step = conn.execute("SELECT MAX(step) FROM touches WHERE prospect_id = ? AND channel = 'email' AND at <= ?",
                                      (p["id"], real[0][1]["at"])).fetchone()[0]
        met = conn.execute("SELECT 1 FROM meetings WHERE prospect_id = ? LIMIT 1", (p["id"],)).fetchone() is not None or \
            conn.execute("SELECT 1 FROM events WHERE prospect_id = ? AND kind = 'stage' AND (to_stage IN ('proposal','won') OR "
                         "(to_stage = 'meeting' AND COALESCE(text, '') NOT LIKE 'reply:%'))", (p["id"],)).fetchone() is not None
        # (a "let's talk" reply moves the stage to meeting before anything is booked — that is a positive reply, not a meeting)
        src = p.get("source") or "manual"
        fam, _, query = src.partition(":")
        platform = p["slug"].split("@")[1] if "@" in p["slug"] else (fam if fam in ("maps", "producthunt", "apollo", "apollo-api",
                                                                                     "leads", "linkedin-people") else "website")
        q = s1.get("quality")
        out.append({"slug": p["slug"], "source": fam, "query": f"{fam}:{query}" if query else None, "platform": platform,
                    "hook": s1.get("hook") or "unknown", "variant": s1.get("variant"), "subject": s1.get("subject"),
                    "quality": None if q is None else ("80+" if q >= 80 else "65-79" if q >= 65 else "<65"),
                    "country": p.get("country") or "unknown", "replied": bool(real),
                    "positive": any(c in POSITIVE for c, _ in real), "reply_step": reply_step, "meeting": met,
                    "won": p["stage"] == "won", "value": p.get("value") if p["stage"] == "won" else 0})
    return out


def group(data, key, min_n):
    buckets = {}
    for r in data:
        k = r.get(key)
        if k is None:
            continue
        b = buckets.setdefault(str(k), {"contacted": 0, "replied": 0, "positive": 0, "meetings": 0, "won": 0, "won_value": 0.0})
        b["contacted"] += 1
        b["replied"] += r["replied"]
        b["positive"] += r["positive"]
        b["meetings"] += r["meeting"]
        b["won"] += r["won"]
        b["won_value"] += float(r["value"] or 0)
    out = []
    for k, b in buckets.items():
        n = b["contacted"]
        out.append({key: k, **b, "reply_pct": round(100 * b["replied"] / n, 1), "positive_pct": round(100 * b["positive"] / n, 1),
                    "meeting_pct": round(100 * b["meetings"] / n, 1), "enough_data": n >= min_n})
    return sorted(out, key=lambda x: (x["enough_data"], x["meeting_pct"], x["positive_pct"], x["contacted"]), reverse=True)


def z_test(a_pos, a_n, b_pos, b_n):
    if not a_n or not b_n:
        return None
    p1, p2 = a_pos / a_n, b_pos / b_n
    p = (a_pos + b_pos) / (a_n + b_n)
    se = math.sqrt(p * (1 - p) * (1 / a_n + 1 / b_n)) if 0 < p < 1 else 0
    if not se:
        return 1.0
    z = abs(p1 - p2) / se
    return round(math.erfc(z / math.sqrt(2)), 3)        # two-sided p-value


def ab(data, min_n=20):
    a = [r for r in data if r["variant"] == "A"]
    b = [r for r in data if r["variant"] == "B"]
    res = {"A": {"contacted": len(a), "positive": sum(r["positive"] for r in a), "subjects": sorted({r["subject"] for r in a if r["subject"]})[:3]},
           "B": {"contacted": len(b), "positive": sum(r["positive"] for r in b), "subjects": sorted({r["subject"] for r in b if r["subject"]})[:3]}}
    for v in ("A", "B"):
        n = res[v]["contacted"]
        res[v]["positive_pct"] = round(100 * res[v]["positive"] / n, 1) if n else None
    pv = z_test(res["A"]["positive"], len(a), res["B"]["positive"], len(b))
    res["p_value"] = pv
    if len(a) < min_n or len(b) < min_n:
        res["verdict"] = f"not enough data yet (need {min_n} per variant; have {len(a)} / {len(b)})"
    elif pv is not None and pv < 0.1:
        win = "A" if res["A"]["positive_pct"] > res["B"]["positive_pct"] else "B"
        res["verdict"] = f"{win} wins (p = {pv}) — use its subject style for the next sequences"
    else:
        res["verdict"] = f"no real difference yet (p = {pv})"
    return res


def recommend(groups, min_n):
    recs, drop, weights = [], [], {}
    for g in groups["query"]:
        q = g["query"]
        if g["contacted"] >= max(min_n, 15) and g["positive"] == 0:
            drop.append(q)
            recs.append(f"Drop {q}: {g['contacted']} contacted, no positive reply.")
        if g["enough_data"]:
            weights[q] = round(g["meeting_pct"] * 2 + g["positive_pct"], 1)
    best = [g for g in groups["query"] if g["enough_data"] and g["meetings"]]
    if best:
        recs.append(f"Double down on {best[0]['query']}: {best[0]['meeting_pct']}% of contacted booked a meeting — write 2 more "
                    "queries like it (same niche/pain, different wording).")
    hooks = [g for g in groups["hook"] if g["enough_data"] and g["hook"] != "unknown"]
    if len(hooks) >= 2:
        recs.append(f"Best first-email hook: {hooks[0]['hook']} ({hooks[0]['positive_pct']}% positive) vs worst "
                    f"{hooks[-1]['hook']} ({hooks[-1]['positive_pct']}%). Lead with the best one when the dossier has it.")
    steps = [g for g in groups["reply_step"] if g["contacted"]]
    if steps:
        total = sum(g["contacted"] for g in steps)
        later = sum(g["contacted"] for g in steps if g["reply_step"] not in ("1",))
        recs.append(f"{round(100 * later / total)}% of replies came after a follow-up — keep the full 5-email sequence."
                    if later else "All replies came on email 1 so far — follow-ups aren't adding replies yet; give them a new angle.")
    q80 = next((g for g in groups["quality"] if g["quality"] == "80+"), None)
    qlow = next((g for g in groups["quality"] if g["quality"] == "<65"), None)
    if q80 and qlow and q80["enough_data"] and qlow["enough_data"]:
        recs.append(f"Emails scoring 80+ got {q80['positive_pct']}% positive replies vs {qlow['positive_pct']}% under 65.")
    return recs, drop, weights


def report(conn, min_n=5, apply=False):
    data = rows(conn)
    dims = ["source", "query", "platform", "hook", "variant", "reply_step", "quality", "country"]
    groups = {d: group(data, d, min_n) for d in dims}
    recs, drop, weights = recommend(groups, min_n)
    out = {"contacted": len(data), "replied": sum(r["replied"] for r in data), "positive": sum(r["positive"] for r in data),
           "meetings": sum(r["meeting"] for r in data), "won": sum(r["won"] for r in data), "by": groups, "ab_test": ab(data),
           "recommendations": recs or ["Not enough outcomes yet — keep going; this report gets useful after ~30 contacted prospects."]}
    if apply:
        learned = {"updated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "query_weights": weights,
                   "drop_queries": drop, "min_n": min_n}
        path = data_home() / "learned.json"
        path.write_text(json.dumps(learned, indent=2), encoding="utf-8")
        out["applied"] = {"file": str(path), "weights": len(weights), "dropped": drop}
    return out


def learned():
    try:
        return json.loads((data_home() / "learned.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"query_weights": {}, "drop_queries": []}


def main(argv=None):
    ap = argparse.ArgumentParser(description="What works: rates by source, query, hook, subject, step — and feed it back.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report"); r.add_argument("--min", type=int, default=5); r.add_argument("--apply", action="store_true")
    a = sub.add_parser("ab"); a.add_argument("--min", type=int, default=20)
    args = ap.parse_args(argv)
    conn = pipeline.connect()
    try:
        out = report(conn, args.min, args.apply) if args.cmd == "report" else ab(rows(conn), args.min)
        emit({"ok": True, "data": out})
    finally:
        conn.close()


if __name__ == "__main__":
    main()

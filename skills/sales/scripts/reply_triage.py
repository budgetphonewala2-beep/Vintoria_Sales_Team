#!/usr/bin/env python3
"""
Reply triage: classify a prospect's reply (English, Hindi, Hinglish), pull out times/phones/emails it
mentions, and say exactly what to do next. With --apply it updates the pipeline: logs the reply, moves the
stage, stops the follow-up cadence, suppresses opt-outs and marks bounced addresses invalid.

Usage:
    python reply_triage.py --text "Sounds good, can we talk Thursday 4pm?"
    python reply_triage.py --file reply.txt --apply acme.com [--from priya@acme.com]

Categories (first match by priority): bounce, unsubscribe, out_of_office, not_interested, meeting_request,
interested, referral, objection_price, objection_has_vendor, objection_timing, question, unclear.
("Not interested right now" counts as objection_timing → nurture, not lost.)
Deterministic keyword rules on purpose — the agent reads the reply too and can override.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import outreach  # noqa: E402
import pipeline  # noqa: E402
from sales_common import emit  # noqa: E402

R = lambda *pats: re.compile("|".join(pats), re.I)  # noqa: E731

RULES = [
    ("bounce", R(r"delivery (status notification|has failed|to the following recipients? failed)", r"undeliverable",
                 r"mailbox (unavailable|not found|full)", r"address (not found|couldn'?t be found)", r"user unknown",
                 r"mail delivery (subsystem|failed)", r"\b550[ -]5\.\d\.\d")),
    ("unsubscribe", R(r"\bunsubscribe\b", r"remove me", r"stop (emailing|contacting|messaging|sending)", r"do not (contact|email)",
                      r"don'?t (contact|email|message) me", r"take me off", r"\bopt[ -]?out\b", r"^\s*(no|stop)\s*[.!]?\s*$",
                      r"mat bhej", r"message mat kar", r"band karo", r"dobara (mat|na)", r"spam mat")),
    ("out_of_office", R(r"out of (the )?office", r"\bOOO\b", r"on (annual |parental |sick )?leave", r"away until",
                        r"limited access to (my )?email", r"auto(matic)?[- ]?reply", r"currently travell?ing")),
    ("not_interested", R(r"\bnot interested\b", r"\bno thanks?\b", r"\bnot (a )?(fit|for us|relevant)\b", r"\bwe'?re (good|fine|all set)\b",
                         r"\bnahi chahiye\b", r"\bzaroorat nahi\b", r"\binterested nahi\b", r"\bnhi chahiye\b")),
    ("meeting_request", R(r"(let'?s|can we|could we|shall we|happy to|open to|free to|available (for|to)) (a )?(talk|chat|call|meet|connect|speak|hop on)",
                          r"(book|schedule|set up|arrange) (a )?(call|meeting|time|demo)", r"send (me )?(a |an )?(invite|calendar|link)",
                          r"what time works", r"when are you (free|available)", r"\b(calendly|cal\.com|zoom|google meet|teams)\b",
                          r"call (kar|karte|karo|karlo|kare)", r"baat (kar|karte|karo|karlo|kare|ho)", r"mil(te|ke|na) (hain|hai|ho)",
                          r"(kal|parso|aaj) (call|baat|mil)", r"time (do|bata|batao)", r"meeting (rakh|fix|set)")),
    ("interested", R(r"\b(interested|sounds (good|great|interesting)|tell me more|go ahead|let'?s do (it|this))\b",
                     r"\bsend (me )?(details|more info|the proposal|a quote|pricing|your portfolio|samples)\b",
                     r"\bwhat would (it|this) cost\b", r"\bhow much (would|does|for)\b", r"\bkitna (lagega|hoga|charge)",
                     r"\bdetails? (bhejo|bhej do|share karo)", r"\b(haan|ha|ji) (bilkul|zaroor|interested)", r"\bachha (laga|idea)\b",
                     r"\bportfolio (bhejo|dikhao)", r"\bquote (bhejo|do)")),
    ("referral", R(r"\b(talk|speak|reach out|write) to (my|our) \w+", r"\bcc'?ing\b", r"\bloop(ing)? in\b", r"\bthe right person\b",
                   r"\b(handles|in charge of|responsible for) (this|that|marketing|the website)", r"\bforward(ed|ing)? (this|your email) to\b",
                   r"\b(unse|inse|usse) baat karo\b")),
    ("objection_price", R(r"\btoo (expensive|costly|pricey|much)\b", r"\bout of (our|my) budget\b", r"\bno budget\b", r"\bcan'?t afford\b",
                          r"\bcheaper\b", r"\bbahut (mehenga|mehnga|zyada)\b", r"\bbudget (nahi|kam|nhi)\b", r"\bmehenga\b")),
    ("objection_has_vendor", R(r"\b(already|currently) (have|has|use|using|work(ing)? with)\b", r"\bwe have (an?|our own) (agency|developer|team|guy|freelancer)",
                               r"\bin[- ]house\b", r"\bpehle se (hai|hain|agency|developer)\b", r"\bapna (developer|banda|team)\b")),
    ("objection_timing", R(r"\bnot (right )?now\b", r"\b(maybe|try|check back|reach out|circle back) (later|next (month|quarter|year))\b",
                           r"\bnext (month|quarter|year)\b", r"\bafter (diwali|the holidays|the festive season|q[1-4]|the launch)\b",
                           r"\btoo busy\b", r"\bbaad mein\b", r"\babhi nahi\b", r"\babhi (time|busy)\b", r"\bagle (mahine|saal)\b")),
    ("question", R(r"\?\s*$", r"\?\s", r"\b(how|what|which|who|why|can you|do you|have you)\b.*\?", r"\b(kaise|kya|kitne|kaun)\b")),
]

PLAN = {
    "bounce": ("contacted", "Address bounced — find another verified contact (sales-contacts)", "sales-contacts", True, False),
    "unsubscribe": ("lost", "Opted out — suppressed, never contact again", None, True, True),
    "out_of_office": (None, "Auto-reply — follow up the day after they return", "sales-followup", False, False),
    "meeting_request": ("meeting", "Book it now: propose 2-3 slots or send the booking link", "sales-book", True, False),
    "interested": ("replied", "Answer in 1-2 lines and ask for a 15-minute call with 2-3 slots", "sales-book", True, False),
    "referral": ("replied", "Thank them, then write to the person they named (mention who referred you)", "sales-outreach", True, False),
    "objection_price": ("replied", "Handle the price objection, then offer a smaller first step + a call", "sales-objections", True, False),
    "objection_has_vendor": ("replied", "Acknowledge their vendor; offer a second opinion/audit, low pressure", "sales-objections", True, False),
    "objection_timing": ("nurture", "Agree a date to come back; set it as the next action", "sales-followup", True, False),
    "question": ("replied", "Answer the question briefly and truthfully, then suggest a call", "sales-reply", True, False),
    "not_interested": ("lost", "Thank them, close politely, no further follow-ups", None, True, False),
    "unclear": ("replied", "Read it yourself and decide; reply within the same business day", "sales-reply", True, False),
}

DAY = r"(mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?|sun)(day)?|today|tomorrow|next week|this week|kal|parso|aaj|somvar|mangalvar|budhvar|guruvar|shukravar|shanivar|ravivar"
TIME_RE = re.compile(rf"\b(({DAY})\b[^.\n?!]{{0,25}}?\b\d{{1,2}}(:\d{{2}})?\s*(am|pm|baje)?|\d{{1,2}}(:\d{{2}})?\s*(am|pm|baje)\b[^.\n?!]{{0,15}}?\b({DAY})?|({DAY}))\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\s-]{8,15}\d)(?!\d)")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def strip_quoted(text):
    """Drop the quoted thread under the reply (lines starting with '>' and everything after 'On ... wrote:')."""
    out = []
    for line in (text or "").splitlines():
        if re.match(r"^\s*(on .{5,120} wrote:|-----\s*original message|from:\s.+@)", line, re.I):
            break
        if not line.lstrip().startswith(">"):
            out.append(line)
    return "\n".join(out).strip()


def classify(text):
    body = strip_quoted(text)
    hits = {}
    for cat, rx in RULES:
        found = [m.group(0) for m in rx.finditer(body)]
        if found:
            hits[cat] = found[:3]
    cat = next((c for c, _ in RULES if c in hits), "unclear")
    # a reply that asks to talk outranks a polite "not now" or price question in the same message
    if cat in ("objection_price", "objection_timing", "question", "interested") and "meeting_request" in hits:
        cat = "meeting_request"
    times = [m.group(0).strip() for m in TIME_RE.finditer(body)]
    if cat == "not_interested" and "objection_timing" in hits:
        cat = "objection_timing"
    # "not now, let's talk next month" is a timing objection unless they name a concrete day/time
    if cat == "meeting_request" and "objection_timing" in hits and not any(re.search(r"\d", t) for t in times):
        cat = "objection_timing"
    stage, action, skill, stop, supp = PLAN[cat]
    return {"category": cat, "signals": hits.get(cat, []), "also_matched": [c for c in hits if c != cat],
            "suggested_stage": stage, "next_action": action, "next_skill": skill, "stop_followups": stop, "suppress": supp,
            "mentioned_times": list(dict.fromkeys(t for t in times if t))[:5],
            "phones": list(dict.fromkeys(p.strip() for p in PHONE_RE.findall(body)))[:3],
            "emails": list(dict.fromkeys(EMAIL_RE.findall(body)))[:5],
            "reply_excerpt": body[:400], "respond_within": "1 business hour" if cat in ("meeting_request", "interested") else "same day"}


def apply(conn, key, result, sender=None):
    p = pipeline.get(conn, key)
    done = []
    with conn:
        pipeline.event(conn, p["id"], "reply", f"[{result['category']}] {result['reply_excerpt'][:300]}")
        if result["category"] == "bounce" and sender:
            conn.execute("UPDATE contacts SET email_status = 'invalid' WHERE prospect_id = ? AND lower(email) = lower(?)",
                         (p["id"], sender))
            done.append(f"{sender} marked invalid")
        pipeline.touch(conn, p["id"])
    if result["suppress"]:
        target = sender or next(iter(result["emails"]), None)
        pipeline.suppress(conn, target or p["slug"], "opted out by reply")
        done.append(f"suppressed {target or p['slug']}")
    if result["stop_followups"]:
        outreach.stop(conn, p["slug"], f"reply: {result['category']}")
        done.append("follow-ups stopped")
    st = result["suggested_stage"]
    order = pipeline.STAGES
    # never move a deal backwards automatically (e.g. a question during 'proposal' stays in 'proposal')
    if st and st != p["stage"] and not (st in ("replied", "contacted") and p["stage"] in order[order.index("replied"):]):
        pipeline.set_stage(conn, p["slug"], st, f"reply: {result['category']}")
        done.append(f"stage {p['stage']} → {st}")
    if result["next_skill"] or result["category"] == "out_of_office":
        with conn:
            conn.execute("UPDATE prospects SET next_action = ?, next_due = date('now') WHERE id = ?",
                         (result["next_action"], p["id"]))
        done.append("next action set for today")
    return done


def main(argv=None):
    ap = argparse.ArgumentParser(description="Classify a prospect's reply and plan the next step.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text"); g.add_argument("--file")
    ap.add_argument("--apply", metavar="PROSPECT", help="update the pipeline for this prospect")
    ap.add_argument("--from", dest="sender", help="the address the reply came from (for bounces/opt-outs)")
    a = ap.parse_args(argv)
    text = Path(a.file).read_text(encoding="utf-8-sig") if a.file else a.text
    res = classify(text)
    if a.apply:
        conn = pipeline.connect()
        try:
            res["applied"] = apply(conn, a.apply, res, a.sender)
        except pipeline.UserError as exc:
            emit({"ok": False, "error": str(exc)}, 2)
        finally:
            conn.close()
    emit({"ok": True, "data": res})


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Cold-email quality score (0-100), deterministic, so every agent judges a draft the same way before a human sees it.
The claim checker asks "is it true?"; this asks "will a busy buyer reply?".

Rubric (adapted from gtmagents/gtm-agents cold-email-personalization, Apache-2.0; AI-tell list after coreyhaines31/marketingskills
cold-email, MIT — see THIRD_PARTY_NOTICES.md):
  situation  25  email 1: the first lines are about THEM (a specific observation, their post); follow-ups: still about them
  value      20  what you do in one line + a concrete proof (a number or a named result)
  you_ratio  10  sentences about them vs sentences only about you, target ≥ 2:1
  cta        15  one low-effort question they can answer in a few words; no "15 minutes?" ask in a first email
  length     15  by step: email 1 50-120 words, follow-ups 25-90, breakup ≤ 60 (body, without the signature)
  subject     5  2-5 words, lower-case, no hype, no fake Re:/Fwd: (email 1 only)
  clean      10  no AI tells, banned openers, jargon, exclamation runs, em dashes, more than one link
Score ≥ 80 ship · 65-79 one more pass · < 65 rewrite. Every deduction comes with the reason and the exact phrase.

Usage:
    python email_lint.py --file email.txt [--subject "glow skin relaunch"] [--step 1]
    python email_lint.py --sequence prospects/acme.com/SEQUENCE.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sales_common import emit  # noqa: E402

BANNED_OPENERS = [r"i hope (this|you|your)", r"hope this (email )?finds you", r"my name is", r"i wanted to reach out", r"i am reaching out",
                  r"i'?m reaching out", r"i came across your (profile|company|website)", r"allow me to introduce", r"just wanted to introduce",
                  r"i trust this", r"greetings"]
AI_TELLS = [r"here'?s the thing", r"i'?ll be honest", r"\bunlock\b", r"take (it|your \w+) to the next level", r"say goodbye to",
            r"in today'?s (fast-paced|digital|competitive)", r"game[- ]changer", r"\bseamless(ly)?\b", r"\brevolutioni[sz]e", r"\belevate\b",
            r"\bsupercharge", r"\bdelve\b", r"\btapestry\b", r"\bunleash", r"it'?s not (just )?about \w+[^.]*, it'?s about",
            r"\bthe result\?", r"\bthe best part\?", r"\bthe catch\?", r"look no further"]
JARGON = [r"\bsynerg", r"\bleverag", r"best[- ]in[- ]class", r"\bcutting[- ]edge", r"world[- ]class", r"\bcircle back", r"\btouch base",
          r"\bholistic", r"\bparadigm", r"\bend[- ]to[- ]end solution", r"leading provider", r"\binnovative solution", r"\bkindly\b",
          r"\brevert\b", r"do the needful", r"\bvalue[- ]add"]
WEAK_FOLLOWUP = [r"just (checking|following) (in|up)", r"bumping this", r"circling back", r"any update", r"did you get a chance"]
BIG_ASK = [r"\b(15|20|30|45|60)[- ]?min(ute)?s?\b.*\?", r"schedule a (call|meeting|demo)", r"book a (call|demo|meeting)", r"hop on a call"]
LOW_EFFORT_CTA = re.compile(r"(worth|open to|interested|make sense|would (it|that|this) help|should i|want me to|useful|"
                            r"is that (right|the case)|curious|fair|any (chance|interest)|ok if i|shall i|still a priority)", re.I)
HYPE_SUBJECT = re.compile(r"(!|free|guarantee|urgent|act now|limited|\$\$|%|amazing|exclusive|last chance|quick question)", re.I)
SIGNATURE_START = re.compile(r"\n\s*(best|thanks|cheers|regards|warmly|—|--)[,!]?\s*\n|\n(not relevant\?|if this isn'?t relevant)", re.I)


def body_of(text):
    """Body without the signature / opt-out block (that is fixed text and shouldn't count against length)."""
    t = (text or "").strip()
    lines = t.split("\n")
    out = []
    for ln in lines:
        if re.match(r"^\s*(not relevant\?|if this isn'?t relevant|unsubscribe|reply ['\"]?no)", ln, re.I):
            break
        out.append(ln)
    t = "\n".join(out)
    # drop a trailing signature block: the last paragraph if it is short lines without a question/sentence verb
    paras = [p for p in re.split(r"\n\s*\n", t) if p.strip()]
    while len(paras) > 1 and len(paras[-1].split()) <= 14 and "?" not in paras[-1] and not re.search(r"[.!]\s*$", paras[-1].split("\n")[0]):
        paras.pop()
    return "\n\n".join(paras)


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", t) if len(s.strip()) > 2]


def words(t):
    return len(re.findall(r"[A-Za-z0-9$%'’.,-]+", t))


def _hits(patterns, t):
    return [m.group(0) for p in patterns for m in [re.search(p, t, re.I)] if m]


def lint(text, subject=None, step=1, evidence_hint=None):
    body = body_of(text)
    b = body.lower()
    sents = sentences(re.sub(r"^\s*(hi|hello|hey|dear)[^\n,]*,?\s*\n", "", body, flags=re.I))
    issues, parts = [], {}
    first = " ".join(sents[:2]).lower()

    # situation (25): opens on them
    about_them = re.search(r"\b(you|your|you'?re)\b", first) is not None
    about_me = re.match(r"^\s*(i|we|our|my)\b", sents[0].lower()) is not None if sents else True
    specific = bool(re.search(r"\b(saw|noticed|read|your (post|site|homepage|store|launch|team|hiring)|you (posted|mentioned|said|asked|are))", first)) \
        or bool(re.search(r"\d", first)) or bool(evidence_hint and evidence_hint.lower()[:30] in first)
    breakup = step >= 5 or bool(re.search(r"(close (the|your|this) (file|loop)|leave it (there|here)|last (note|email)|stop (emailing|following))", b))
    if step == 1:
        parts["situation"] = 25 if (about_them and specific and not about_me) else 15 if about_them and not about_me else 5 if not about_me else 0
        if about_me:
            issues.append("opens with I/we — start with their world (their post, their site), not yours")
        elif not specific:
            issues.append("first lines aren't specific to them — open on the strongest dossier hook")
    else:                                  # a follow-up only has to stay about them
        them_any = re.search(r"\b(you|your|you'?re)\b", b) is not None
        parts["situation"] = 25 if them_any and not about_me else 18 if them_any else 10 if breakup else 5
        if not them_any and not breakup:
            issues.append("follow-up never mentions them — tie it to their site, post or goal")

    # value (20): what + proof
    proof = bool(re.search(r"\d", b)) and bool(re.search(r"\b(we|our)\b", b))
    what = bool(re.search(r"\b(we|i) (build|design|help|fix|run|rebuild|redesign|make|grow|get)\b", b))
    new_value = bool(re.search(r"\b(fix|idea|example|teardown|one (line|change|thing)|noticed|found|checked|case|result|tip|"
                               r"here'?s how|send (you|over|the)|\d)", b))
    if step == 1:
        parts["value"] = 20 if (what and proof) else 12 if (what or proof) else 0
        if not what:
            issues.append("no plain line saying what you do")
    elif breakup:
        parts["value"] = 20
    else:
        parts["value"] = 20 if new_value else 8
        if not new_value:
            issues.append("follow-up adds nothing new — bring a second fact, a fix idea, an example or a result")

    # you ratio (10)
    them_s = sum(1 for x in sents if re.search(r"\b(you|your|you'?re|yours)\b", x, re.I))
    us_s = sum(1 for x in sents if re.search(r"\b(i|we|our|my|us|i'?m|we'?re|we'?ve)\b", x, re.I)
               and not re.search(r"\b(you|your|you'?re)\b", x, re.I))
    ratio = them_s / max(1, us_s)
    parts["you_ratio"] = 10 if ratio >= 2 else 8 if ratio >= 1 else 5 if ratio >= 0.5 else (6 if breakup else 0)
    if ratio < 1 and not breakup:
        issues.append(f"more sentences about you than about them ({them_s} vs {us_s}) — rewrite from their side")

    # cta (15)
    qs = [s for s in sents if s.endswith("?")]
    big = _hits(BIG_ASK, b) if step == 1 else []
    low = bool(qs) and bool(LOW_EFFORT_CTA.search(qs[-1]))
    parts["cta"] = 15 if (len(qs) == 1 and low and not big) else 10 if (qs and not big) else 5 if qs else (8 if step >= 5 else 0)
    if big:
        issues.append(f"asks for a meeting slot in a first email ({big[0]!r}) — ask an interest question instead")
    if len(qs) > 2:
        issues.append(f"{len(qs)} questions — keep one clear ask")
    if not qs and step < 5:
        issues.append("no question to reply to")

    # length (15)
    n = words(body)
    lo, hi = (50, 120) if step == 1 else (10, 60) if step >= 5 else (25, 90)
    parts["length"] = 15 if lo <= n <= hi else 8 if (n <= hi * 1.25 and n >= lo * 0.6) else 0
    if n > hi:
        issues.append(f"{n} words — aim for {lo}-{hi} for this step (a busy buyer reads it on a phone)")
    elif n < lo:
        issues.append(f"{n} words — too thin to stand on its own")

    # subject (5)
    if step == 1:
        s = (subject or "").strip()
        sw = len(s.split())
        ok = 2 <= sw <= 5 and not HYPE_SUBJECT.search(s) and not re.match(r"^\s*(re|fwd?):", s, re.I) and s == s.lower()
        parts["subject"] = 5 if ok else 2 if s and 1 <= sw <= 7 and not HYPE_SUBJECT.search(s) else 0
        if not s:
            issues.append("no subject line")
        elif not ok:
            issues.append(f"subject {s!r}: 2-5 words, lower-case, plain, internal-looking")
    else:
        parts["subject"] = 5

    # clean (10)
    bad = _hits(BANNED_OPENERS, b) + _hits(AI_TELLS, b) + _hits(JARGON, b) + (_hits(WEAK_FOLLOWUP, b) if step > 1 else [])
    links = len(re.findall(r"https?://|www\.|\b[\w-]+\.(com|io|co|net|org|app)/\S+", body))
    marks = []
    if "—" in body or " -- " in body:
        marks.append("em dash")
    if re.search(r"!{1,}", body) and len(re.findall(r"!", body)) >= 2:
        marks.append("exclamation marks")
    if links > 1:
        marks.append(f"{links} links")
    if re.search(r"\*\*|__|<[a-z]+>", body):
        marks.append("formatting (bold/HTML) — send plain text")
    deduct = 3 * len(bad) + 2 * len(marks)
    parts["clean"] = max(0, 10 - deduct)
    for x in bad:
        issues.append(f"cut {x!r} — reads as template/AI/jargon")
    for x in marks:
        issues.append(f"remove {x}")

    score = sum(parts.values())
    verdict = "ship" if score >= 80 else "one more pass" if score >= 65 else "rewrite"
    return {"score": score, "verdict": verdict, "step": step, "words": n, "parts": parts, "issues": issues,
            "personalization_test": "Delete the first two sentences: if the email still makes sense, the personalization isn't doing its job."}


def lint_sequence(steps):
    out = []
    for st in steps:
        out.append({"step": st["step"], **lint(st.get("body", ""), st.get("subject"), int(st["step"]))})
    return {"emails": out, "min_score": min((e["score"] for e in out), default=0),
            "average": round(sum(e["score"] for e in out) / max(1, len(out)), 1)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score a cold email (0-100) for reply-worthiness, with the exact fixes.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file"); g.add_argument("--text"); g.add_argument("--sequence", help="SEQUENCE.json")
    ap.add_argument("--subject"); ap.add_argument("--step", type=int, default=1)
    a = ap.parse_args(argv)
    if a.sequence:
        import outreach
        emit({"ok": True, "data": lint_sequence(outreach.parse_sequence(a.sequence))})
    text = Path(a.file).read_text(encoding="utf-8-sig") if a.file else a.text
    emit({"ok": True, "data": lint(text, a.subject, a.step)})


if __name__ == "__main__":
    main()

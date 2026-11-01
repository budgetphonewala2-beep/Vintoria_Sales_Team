#!/usr/bin/env python3
"""
Claim checker for outreach, follow-ups and proposals: every factual sentence must be backed by
evidence you actually collected. Deterministic on purpose — a checker that can hallucinate is useless.

Evidence = any files you pass: the prospect's post, site_audit.py JSON (facts + evidence),
research Markdown in prospects/<slug>/, IDEAL-CUSTOMER-PROFILE.md / your offer notes (claims about
YOU), replies from the prospect.

Rules:
- A sentence is a claim if it has a factual anchor (a number, an observation word like "noticed",
  "your site", "homepage", "clients", "results", "%", "₹", ...). Greetings, sign-offs and pure
  questions/CTAs are not claims.
- Numbers are a hard gate: one single source must contain every number in the sentence.
- "Quoted text" must appear verbatim in one source.
- Otherwise >= 50% of the sentence's content words must appear in one source.
- A hedged consequence ("..., so phone visitors may see the desktop layout") is an opinion: only the part before
  it is checked. An unhedged one ("..., so you are losing 40% of sales") must be proven like any claim.
- Placeholders like [ADD REAL CUSTOMER RESULT] are reported separately (must be filled before sending).

Drafts are never evidence: OUTREACH-SEQUENCE.md, FOLLOWUP-SEQUENCE.md, CLIENT-PROPOSAL.md, SEQUENCE.json, MEETING-PREP.md,
*DRAFT*/*EMAIL* files and the draft itself are skipped even when a glob matches them (a draft would prove itself).
--prospect <slug> adds that prospect's DOSSIER.json, SITE-AUDIT.json, WEB-RESEARCH.json and research notes;
claims about YOU are checked against the real proof in SELLER-PROFILE.json (case studies, years, clients ...).

Usage:
    python claim_check.py --draft email.txt --prospect acme.com [--evidence-text "their post"]
    python claim_check.py --draft email.txt --evidence prospects/acme.com/*.md --evidence audit.json
    python claim_check.py --draft-text "..." --evidence-text "their post text" --evidence ICP.md
Exit code 0 = all claims supported, 1 = unsupported claims or open placeholders.

Approach adapted from RodricDib06/autonomous-sdr provenance.py (MIT): unicode tokens (Hindi/Hinglish),
light stemming, verbatim-quote gate and agency/outreach vocabulary added.
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sales_common import data_home, emit  # noqa: E402

SKIPPED = []   # draft files left out of the evidence in the last load_sources() call

THRESHOLD = 0.5
STOP = frozenset("""a an and are as at be been but by can could did do does for from had has have he her his how i if in
into is it its just me more most my no not of on or our out she so some than that the their them then there these they
this to up us was we were what when which who will with would you your yours hi hello hey dear best regards thanks thank
cheers team really very quick question call chat minute minutes worth make sense happy let know im ive id well get got
like also any anything here sure glad hope today ji hai hain ka ki ke ko se saw see seen noticed post posts posted about
mentioned came across read wrote said shared new recently""".split())
ANCHOR = re.compile(
    r"""\d | [$€£₹%]
    | \b(noticed|saw|see|seen|came\s+across|read|mentioned|posted|said|wrote|shared|looking\s+for|need(?:ed|s)?|want(?:ed|s)?)\b
    | \b(your|their)\s+(site|website|homepage|page|app|store|shop|brand|business|company|post|team|product|customers?)\b
    | \b(site|website|homepage|page|title|meta|viewport|mobile|https|loads?|loading|seconds?|links?|broken|form|button|alt|images?|copyright|footer|h1|wordpress|shopify|wix|webflow|squarespace|hiring|raised|funding|launched|announced|uses?|using)\b
    | \b(we|i)\s+(have\s+)?(built|build|helped|help|delivered|launched|grew|increased|ranked|designed|worked|saved|reduced)\b
    | \b(clients?|customers?|projects?|results?|revenue|traffic|ranking|leads?|conversions?|years?|price|pricing|cost|budget|timeline|weeks?|months?|guarantee|roi)\b
    """, re.I | re.X)
CTA_ONLY = re.compile(r"^(would|are|is|could|can|shall|do|does|open|worth)\b.*\?$", re.I)
SPLIT = re.compile(r"(?<=[.!?।])\s+|\n+")
NUM = re.compile(r"\d+(?:[.,]\d+)*")
QUOTE = re.compile(r"[\"“”]([^\"“”]{4,200})[\"“”]")
PLACEHOLDER = re.compile(r"\[(?:ADD|TO CONFIRM|INSERT|YOUR|TBD|PLACEHOLDER)[^\]]*\]", re.I)
GREETING = ("hi ", "hello", "hey", "dear", "thanks", "thank you", "best", "regards", "cheers", "warm regards", "namaste", "--")


def _stem(w):
    for suf in ("ing", "ed"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w[:-1] if w.endswith("s") and not w.endswith("ss") and len(w) > 3 else w


def tokens(text):
    return {_stem(w) for w in re.findall(r"[^\W_]+(?:'[^\W_]+)?", (text or "").lower()) if len(w) > 1 and w not in STOP}


def numbers(text):
    return {n.replace(",", "").replace(".", "") for n in NUM.findall(text or "")}


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").lower().replace("’", "'")).strip()


def claims(text):
    out, seen = [], set()
    for sent in SPLIT.split(text or ""):
        s = sent.strip().strip("-–—•* ").strip()
        if not s or PLACEHOLDER.fullmatch(s) or (s.lower().startswith(GREETING) and len(tokens(s)) < 6):
            continue
        if (len(tokens(s)) < 3 and not NUM.search(s)) or not ANCHOR.search(s):
            continue
        if CTA_ONLY.search(s) and not NUM.search(s) and not QUOTE.search(s):
            continue
        k = " ".join(sorted(tokens(s)))
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out


HEDGED = re.compile(r",?\s+(so|which means|meaning|and that means|so that)\s+[^.?!]*\b(may|might|could|probably|likely|possibly)\b[^.?!]*[.?!]?\s*$",
                    re.I)


def factual_part(claim):
    """'X is missing, so phones may get Y' → 'X is missing': a hedged consequence is an opinion, not a fact to prove."""
    return HEDGED.sub("", claim).strip() or claim


def match(claim, sources):
    claim = factual_part(claim)
    ct, cn, quotes = tokens(claim), numbers(claim), [_norm(q) for q in QUOTE.findall(claim)]
    best = {"supported": False, "score": 0.0, "source": None, "why": "no matching evidence"}
    for src in sources:
        text = src["text"]
        if cn and not cn <= numbers(text):
            if best["score"] == 0:
                best["why"] = "number(s) not found in any single source: " + ", ".join(sorted(cn - numbers(text)))
            continue
        if quotes and not all(q in _norm(text) for q in quotes):
            if best["score"] == 0:
                best["why"] = "quoted text not found verbatim in any source"
            continue
        score = len(ct & tokens(text)) / len(ct) if ct else 0.0
        if score > best["score"]:
            best.update(score=round(score, 2), source=src["id"], why=f"{int(score * 100)}% word overlap with {src['id']}")
    best["supported"] = best["score"] >= THRESHOLD
    return best


# Our own drafts are never evidence: a draft would "prove" itself. These files are skipped even inside a glob.
DRAFT_FILE = re.compile(r"(OUTREACH-SEQUENCE|FOLLOWUP-SEQUENCE|CLIENT-PROPOSAL|SEQUENCE|MEETING-PREP|OBJECTION-PLAYBOOK|"
                        r"SALES-REPORT|PROSPECT-ANALYSIS|DRAFT|EMAIL)[\w.-]*\.(md|json|txt)$", re.I)
EVIDENCE_FILES = ["DOSSIER.json", "SITE-AUDIT.json", "WEB-RESEARCH.json", "COMPANY-RESEARCH.md", "DECISION-MAKERS.md",
                  "COMPETITIVE-INTEL.md", "LEAD-QUALIFICATION.md", "REPLIES.md", "MEETING-NOTES.md"]


def seller_facts():
    """Claims about YOU are supported only by real proof in the seller profile."""
    for path in (Path("SELLER-PROFILE.json"), data_home() / "seller-profile.json"):
        if path.exists():
            try:
                prof = json.loads(path.read_text(encoding="utf-8-sig"))
            except ValueError:
                return []
            o, pr, po = prof.get("offer") or {}, prof.get("proof") or {}, prof.get("positioning") or {}
            se = prof.get("seller") or {}
            out = [{"id": "profile:identity", "text": " ".join(str(se.get(k) or "") for k in
                                                               ("name", "company", "website", "email", "postal_address", "linkedin"))}]
            for i, c in enumerate(pr.get("case_studies") or []):
                out.append({"id": f"profile:case{i + 1}", "text": " ".join(str(v) for v in (c.values() if isinstance(c, dict) else [c]))})
            facts = [o.get("service_details"), ", ".join(o.get("platforms") or []), ", ".join(pr.get("notable_clients") or []),
                     f"{pr['years_in_business']} years in business" if pr.get("years_in_business") else None,
                     f"{pr['projects_done']} projects" if pr.get("projects_done") else None,
                     f"team of {pr['team_size']}" if pr.get("team_size") else None,
                     " ".join(po.get("differentiators") or []), " ".join(po.get("guarantees") or []),
                     " ".join(str(t) for t in pr.get("testimonials") or [])]
            out += [{"id": f"profile:{i}", "text": t} for i, t in enumerate(facts) if t]
            return out
    return []


def auto_evidence(slug):
    """Evidence files that exist for this prospect (never drafts)."""
    folder = Path("prospects") / slug
    return [str(folder / f) for f in EVIDENCE_FILES if (folder / f).exists()]


def load_sources(paths, texts, draft_path=None, slug=None, profile=True):
    """Evidence sources. Drafts (OUTREACH-SEQUENCE.md, proposals, the draft itself ...) are always skipped.
    slug= adds that prospect's DOSSIER/SITE-AUDIT/WEB-RESEARCH/... automatically; profile=True adds your real proof."""
    SKIPPED.clear()
    sources = []
    paths = list(paths or []) + [f for f in (auto_evidence(slug) if slug else []) if f not in (paths or [])]
    for pattern in paths or []:
        files = glob.glob(pattern) or [pattern]
        for f in files:
            p = Path(f)
            if DRAFT_FILE.search(p.name) or (draft_path and p.resolve() == Path(draft_path).resolve()):
                SKIPPED.append(str(p))
                continue
            if not p.exists():
                raise FileNotFoundError(f"evidence file not found: {f}")
            raw = p.read_text(encoding="utf-8-sig", errors="replace")
            if p.suffix.lower() == ".json":
                try:
                    data = json.loads(raw)
                    data = data.get("data", data) if isinstance(data, dict) else data
                    facts = data.get("facts") if isinstance(data, dict) else None
                    if facts:
                        for i, fct in enumerate(facts):
                            sources.append({"id": f"{p.name}#fact{i}", "text": f"{fct.get('statement', '')} {fct.get('evidence', '')}"})
                        continue
                    raw = json.dumps(data, ensure_ascii=False)
                except ValueError:
                    pass
            for i, para in enumerate(x for x in re.split(r"\n\s*\n|\n(?=\s*[-*|] )", raw) if x.strip()):
                sources.append({"id": f"{p.name}#{i}", "text": para})
    for i, t in enumerate(texts or []):
        sources.append({"id": f"text{i + 1}", "text": t})
    if profile:
        sources += seller_facts()
    sources.append({"id": "meeting", "text": "15 minute 15-minute 20 minute 30 minute quick intro call video call Google Meet "
                                             "Zoom this week next week chat"})
    return sources


def check(draft, sources):
    results = [{"text": c, **match(c, sources)} for c in claims(draft)]
    unsupported = [{"text": r["text"], "why": r["why"]} for r in results if not r["supported"]]
    holes = PLACEHOLDER.findall(draft or "")
    skipped = list(SKIPPED)
    return {"ok": not unsupported and not holes, "checked": len(results), "supported": len(results) - len(unsupported),
            "unsupported": unsupported, "placeholders": holes, "drafts_not_used_as_evidence": skipped,
            "claims": [{"text": r["text"], "supported": r["supported"], "source": r["source"], "why": r["why"]} for r in results],
            "next": "Ready." if not unsupported and not holes else
                    "Rewrite or delete each unsupported sentence (or add the real evidence), fill placeholders, then re-run."}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check every factual sentence in a draft against your evidence.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--draft", help="draft file (txt/md)")
    g.add_argument("--draft-text")
    ap.add_argument("--evidence", action="append", help="evidence file or glob (repeatable)")
    ap.add_argument("--evidence-text", action="append", help="inline evidence, e.g. the prospect's post (repeatable)")
    ap.add_argument("--prospect", help="slug: also use prospects/<slug>/DOSSIER.json, SITE-AUDIT.json, research files")
    ap.add_argument("--no-profile", action="store_true", help="don't use SELLER-PROFILE.json proof as evidence")
    a = ap.parse_args(argv)
    draft = Path(a.draft).read_text(encoding="utf-8-sig") if a.draft else a.draft_text
    try:
        sources = load_sources(a.evidence, a.evidence_text, draft_path=a.draft, slug=a.prospect, profile=not a.no_profile)
    except FileNotFoundError as exc:
        emit({"ok": False, "error": str(exc)}, 2)
    res = check(draft, sources)
    emit({"ok": True, "data": res}, 0 if res["ok"] else 1)


if __name__ == "__main__":
    main()

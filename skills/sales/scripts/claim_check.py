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
    text = re.sub(r"(?<=\d),(?=\d{3})", "", (text or "").lower())      # "$6,000" is one number, not "6" + "000"
    return {_stem(w) for w in re.findall(r"[^\W_]+(?:'[^\W_]+)?", text) if len(w) > 1 and w not in STOP}


def numbers(text):
    return {n.replace(",", "").replace(".", "") for n in NUM.findall(text or "")}


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").lower().replace("’", "'")).strip()


OFFER = re.compile(r"^(i can|i could|i'?d (be happy|love|like|rather)|happy to|glad to|want me to|if (you|it|that|this|not|so|now)|"
                   r"let me know|feel free|i'?ll|i will|shall i|would it help|should i|we can|we could|ok if i|no worries|"
                   r"no pressure|either way|just reply|reply here|hope (black friday|the|your|it)|good luck|talk soon|speak soon)\b", re.I)
OPT_OUT_LINE = re.compile(r"(not relevant\?|reply ['\"“]?no|won'?t follow up|unsubscribe|opt[ -]?out)", re.I)


def claims(text):
    """Every declarative sentence is a claim, except greetings, sign-offs, the opt-out line, offers and plain questions.
    (Older versions checked only sentences with an 'anchor' word, so 'Your competitors already do this' slipped through.)"""
    out, seen = [], set()
    for sent in SPLIT.split(text or ""):
        s = sent.strip().strip("-–—•* ").strip()
        if not s or PLACEHOLDER.fullmatch(s):
            continue
        low = s.lower()
        if low.startswith(GREETING) and len(tokens(s)) < 6:
            continue
        if OPT_OUT_LINE.search(s) or OFFER.match(s) or re.match(r"^(if|unless|whether)\b", low):
            continue                                    # offers and conditionals ("If the relaunch is still on…") assert nothing
        bare = PLACEHOLDER.sub("", URL.sub("", s))
        if len(bare.split()) <= 3 and not NUM.search(bare) and not entities(bare):
            continue                                    # "Good questions.", "Thanks again."
        if not (NUM.search(bare) or QUOTE.search(bare) or entities(bare) or ABOUT_THEM.search(bare) or ABOUT_US.search(bare)
                or GENERAL.search(bare) or PROMISE.search(bare)):
            continue                                    # general know-how ("The fix is one line in theme.liquid") — no fact about them or you
        words = re.findall(r"[A-Za-z][\w&'.-]*", s)
        if len(s.split()) <= 5 and not NUM.search(s) and words and all(w[0].isupper() or w.lower() in ("and", "of", "at", "&")
                                                                        for w in words):
            continue                                    # signature lines: "Ravi Sharma", "Founder, Pixelcraft Studio"
        if s.endswith("?") and not NUM.search(s) and not QUOTE.search(s) and not entities(s):
            continue                                    # a plain question asserts nothing
        if len(tokens(s)) < 2 and not NUM.search(s):
            continue
        k = " ".join(sorted(tokens(s)))
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out


COMMON_START = set(STOP) | set("""a an and but so then it its they their he she his her what which who how why worth would could should can
will shall do does did is are was were be been not no yes ok okay please looking seeing reading following ps since when if after
before with for as on in at by from here there great thanks congrats congratulations saw noticed happy glad sorry hope quick just
also one many most some every each any all both because while though although once now today tomorrow tonight yesterday sure
honestly really totally different another other loved love enjoyed nice good""".split())
CAPS_OK = set("""i i'm i've i'd i'll am pm ok us uk eu usa uae cst cdt est edt pst pdt mst mdt gmt bst ist aest aedt cet cest utc et pt ct
re fwd""".split())
# Days and months are NOT exempt: "you said March" when they said January is exactly the kind of slip to catch.


def entities(s):
    """Names, brands, tools and places in a sentence (capitalised words) — each must appear in the evidence it relies on.
    This is what stops 'we rebuilt Sephora's store' passing on the strength of a Brew Co case study."""
    out = set()
    words = re.findall(r"[A-Za-z][\w&'.-]*", s)
    for i, w in enumerate(words):
        w2 = w.strip(".'-")
        if not w2 or not w2[0].isupper() or w2.lower() in CAPS_OK:
            continue
        if i == 0:
            nxt = words[i + 1] if i + 1 < len(words) else ""
            brandy = any(ch.isupper() for ch in w2[1:]) or (w2.isupper() and len(w2) > 1)
            if w2.lower() in COMMON_START or not (brandy or (nxt[:1].isupper() and nxt.lower() not in CAPS_OK)):
                continue                   # an ordinary first word ("Aapki", "Loved"), not a name
        if w2.lower() in COMMON_START and not (w2.isupper() and len(w2) > 1):
            continue
        out.add(w2.lower().replace("'s", ""))
    return out


NEG = re.compile(r"\b(no|not|never|none|without|missing|lacks?|cannot)\b|n't\b", re.I)
GENERAL = re.compile(r"\b(most|majority|nearly all|almost all|studies|research shows|data shows|on average|typically|statistically|"
                     r"everyone|nobody|all of your|always|never)\b", re.I)
PROMISE = re.compile(r"\b(guarantee[ds]?|will (double|triple|increase|boost|grow|rank|get you)|you'?ll (get|see|double|triple|rank|have)|"
                     r"100 ?%|risk[- ]free|no risk|instantly|overnight|first page|page one|#1)\b", re.I)


URL = re.compile(r"https?://\S+|\bwww\.\S+|\b[\w-]+\.(?:com|io|co|net|org|app|ai|dev|so|me|us|uk|in)/\S*", re.I)
ABOUT_THEM = re.compile(r"\b(you|your|you're|yours|you've|you'd)\b", re.I)
ABOUT_US = re.compile(r"\b(we|our|ours|we've|we're|i've|i'm|my|us)\b", re.I)
OPINION = re.compile(r"\b(i think|i'd (say|rather|guess|bet)|in my (view|experience|opinion)|to be (honest|upfront|clear)|"
                     r"honest flag|my guess|tight|realistic|feels? like|seems? like|probably|likely|worth (doing|it|fixing|a look)|"
                     r"easy (fix|win)|quick win|low[- ]hanging)\b", re.I)
HEDGED = re.compile(r",?\s+(so|which means|meaning|and that means|so that)\s+[^.?!]*\b(may|might|could|probably|likely|possibly)\b[^.?!]*[.?!]?\s*$",
                    re.I)


def factual_part(claim):
    """'X is missing, so phones may get Y' → 'X is missing': a hedged consequence is an opinion, not a fact to prove."""
    return HEDGED.sub("", claim).strip() or claim


def _best_sentence(claim_tokens, text):
    best, bs = 0.0, ""
    for sent in re.split(r"(?<=[.!?])\s+|\n+", text or ""):
        sc = len(claim_tokens & tokens(sent)) / len(claim_tokens) if claim_tokens else 0
        if sc > best:
            best, bs = sc, sent
    return bs


def _score(claim, src, ct, cn, quotes, ents, shared_text=""):
    """(score, why-if-rejected) of one source for one claim."""
    text = src["text"]
    low = text.lower()
    if cn and not cn <= numbers(text):
        return 0.0, "number(s) not found in any single source: " + ", ".join(sorted(cn - numbers(text)))
    if quotes and not all(q in _norm(text) for q in quotes):
        return 0.0, "quoted text not found verbatim in any source"
    missing = [e for e in ents if e not in low and e not in shared_text]
    if missing:
        return 0.0, "name/brand/place not in the evidence: " + ", ".join(sorted(missing))
    score = len(ct & tokens(text)) / len(ct) if ct else 0.0
    if score >= THRESHOLD and src.get("crisp") and bool(NEG.search(claim)) != bool(NEG.search(_best_sentence(ct, text))):
        return 0.0, f"contradicts {src['id']} (the evidence says the opposite)"
    return score, None


OUTCOME = re.compile(r"\b(los(e|es|ing|t)|revenue|sales|money|thousands|millions|profit|conversions?|customers?|visitors?|traffic|"
                     r"hate|frustrat\w*|complain\w*|churn\w*|bounce\w*|leads?|orders?)\b", re.I)   # their results: never an "opinion"
CLAUSE_SPLIT = re.compile(r",?\s+(?:and|but|plus|while|whereas|since|because|so|which)\s+|;\s+|\s+[—–]\s+", re.I)
MODAL = re.compile(r"\b(may|might|could|probably|likely|possibly|perhaps)\b", re.I)


def unsupported_clause(claim, sources):
    """A true sentence with an invented tail ("…in 4 weeks and doubled their revenue") must not pass on the strength of
    its first half: every clause with real content needs some overlap with some (non-snippet) evidence."""
    parts = CLAUSE_SPLIT.split(claim)
    if len(parts) < 2:
        return None
    for part in parts:
        ct = tokens(part)
        if len(ct) < 2 or MODAL.search(part) or (OPINION.search(part) and not (ABOUT_THEM.search(part) and OUTCOME.search(part))):
            continue
        best = max((len(ct & tokens(x["text"])) / len(ct) for x in sources if x.get("tier") != "snippet"), default=0)
        if best < 0.34:
            return part.strip(" ,.")
    return None


def match(claim, sources):
    claim = factual_part(PLACEHOLDER.sub("", claim)).strip()
    urls = [u.rstrip(".,)") for u in URL.findall(claim)]
    claim = URL.sub("", claim)
    ct, cn, quotes, ents = tokens(claim), numbers(claim), [_norm(q) for q in QUOTE.findall(claim)], entities(claim)
    need = 0.75 if GENERAL.search(claim) else THRESHOLD
    # questions, and opinions that are NOT about the prospect, need only clean names/numbers; an opinion about THEM
    # ("I think your checkout is losing you thousands") is a claim like any other — soften it with may/might instead
    lenient = claim.rstrip().endswith("?") or (bool(OPINION.search(claim)) and not (ABOUT_THEM.search(claim) and OUTCOME.search(claim)))
    promise = bool(PROMISE.search(claim))
    shared = " ".join(x["text"].lower() for x in sources if x.get("tier") in ("profile", "calendar", "guarantee"))
    best = {"supported": False, "score": 0.0, "source": None, "tier": None, "why": "no matching evidence"}
    for u in urls:                                   # a link must be one we have (their site, your booking link ...)
        host = re.sub(r"^https?://(www\.)?", "", u).split("?")[0].rstrip("/").lower()
        if host and not any(host in x["text"].lower() for x in sources):
            best["why"] = f"link not found in any evidence: {u}"
            return best
    snippet_hit, contradiction, closest = None, None, (-1.0, None)
    for src in sources:
        if promise and src.get("tier") != "guarantee":
            continue
        score, why = _score(claim, src, ct, cn, quotes, ents, shared)
        raw = len(ct & tokens(src["text"])) / len(ct) if ct else 0
        if why and "contradicts" in why and not contradiction:
            contradiction = why
        if why and raw > closest[0]:
            closest = (raw, why)
        if src.get("tier") == "snippet":
            if (score >= need or (lenient and why is None)) and not snippet_hit:
                snippet_hit = src["id"]
            continue
        if why is None and lenient and score < need and best["score"] < need:
            score = max(score, need)                 # nothing invented in it: names/numbers all found
        elif why is None and cn and score >= 0.35 and score < need:
            score = need                             # every number sits in this one source: strong, specific support
        if score > best["score"]:
            best.update(score=round(score, 2), source=src["id"], tier=src.get("tier"), why=f"{int(score * 100)}% word overlap with {src['id']}")
    best["supported"] = best["score"] >= need
    if best["supported"] and not lenient:
        bad = unsupported_clause(claim, sources)
        if bad:
            best.update(supported=False, why=f"part of this sentence has no evidence: '{bad}' — cut it, hedge it (may/might) or add the source")
    if not best["supported"]:
        if promise:
            best["why"] = "a promise/guarantee that isn't in your profile's guarantees — remove it or add the real guarantee"
        elif contradiction:
            best["why"] = contradiction
        elif snippet_hit:
            best["why"] = (f"only a search snippet supports this ({snippet_hit}) — open the page with fetch_page.py --save "
                           "prospects/<slug>/sources and re-check, or cut it")
        elif GENERAL.search(claim) and best["score"] >= THRESHOLD:
            best["why"] = "a generalisation ('most', 'studies show', 'always'...) needs a source that says it — cut it or cite it"
        elif closest[1] and best["score"] < 0.3:
            best["why"] = closest[1]
    return best


# Our own drafts are never evidence: a draft would "prove" itself. These files are skipped even inside a glob.
# Agent-written documents are not evidence either: a research note the agent wrote can't prove what the agent writes
# next (that is how an invented "$2M seed round" would launder itself into an email).
DRAFT_FILE = re.compile(r"(OUTREACH-SEQUENCE|FOLLOWUP-SEQUENCE|CLIENT-PROPOSAL|SEQUENCE|MEETING-PREP|OBJECTION-PLAYBOOK|"
                        r"SALES-REPORT|PROSPECT-ANALYSIS|DRAFT|EMAIL|COMPANY-RESEARCH|DECISION-MAKERS|COMPETITIVE-INTEL|"
                        r"LEAD-QUALIFICATION|DOSSIER\.md|SITE-AUDIT\.md|IDEAL-CUSTOMER-PROFILE)[\w.-]*\.(md|json|txt)$", re.I)
EVIDENCE_FILES = ["DOSSIER.json", "SITE-AUDIT.json", "WEB-RESEARCH.json"]   # produced by the scripts, not by the agent


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
                                                               ("name", "company", "website", "email", "postal_address", "linkedin",
                                                                "booking_url", "meeting_link", "country")) + " " + str(pr.get("portfolio_url") or "")}]
            for i, c in enumerate(pr.get("case_studies") or []):
                out.append({"id": f"profile:case{i + 1}", "text": " ".join(str(v) for v in (c.values() if isinstance(c, dict) else [c]))})
            facts = [o.get("service_details"), ", ".join(o.get("platforms") or []), ", ".join(pr.get("notable_clients") or []),
                     f"{pr['years_in_business']} years in business" if pr.get("years_in_business") else None,
                     f"{pr['projects_done']} projects" if pr.get("projects_done") else None,
                     f"team of {pr['team_size']}" if pr.get("team_size") else None,
                     " ".join(po.get("differentiators") or []), " ".join(str(t) for t in pr.get("testimonials") or []),
                     f"based in {se.get('country')}, time zone {se.get('timezone')}" if se.get("country") else None]
            ds = o.get("deal_size") if isinstance(o.get("deal_size"), dict) else {}
            commercial = " ".join(x for x in [  # one source, so a sentence with price AND timeline numbers can be checked
                o.get("service_details") or "",
                f"projects start at {ds.get('min')} {ds.get('currency', '')} and typically run {ds.get('typical')} {ds.get('currency', '')}"
                if ds.get("min") else "", o.get("pricing_model") or "", f"delivery in {o['delivery_time']}" if o.get("delivery_time") else ""] if x)
            if commercial.strip():
                facts.append(commercial)
            out += [{"id": f"profile:{i}", "text": t} for i, t in enumerate(facts) if t]
            if po.get("guarantees"):
                out.append({"id": "profile:guarantees", "tier": "guarantee", "text": " ".join(po["guarantees"])})
            for x in out:
                x.setdefault("tier", "profile")
            return out
    return []


def auto_evidence(slug):
    """Evidence files for this prospect: the scripts' outputs and pages saved with fetch_page.py --save (never drafts,
    never agent-written notes)."""
    folder = Path("prospects") / slug
    files = [str(folder / f) for f in EVIDENCE_FILES if (folder / f).exists()]
    return files + sorted(str(f) for f in (folder / "sources").glob("*.txt")) if (folder / "sources").exists() else files


def pipeline_evidence(slug):
    """What the pipeline knows that nobody invented: the prospect's own replies (from the inbox / triage), and the
    contact names, titles and emails on record."""
    out = []
    try:
        import pipeline
        conn = pipeline.connect()
        try:
            p = pipeline.get(conn, slug)
            for i, r in enumerate(conn.execute("SELECT text FROM events WHERE prospect_id = ? AND kind = 'reply'", (p["id"],))):
                out.append({"id": f"reply{i + 1}", "text": re.sub(r"^\[\w+\]\s*", "", r["text"] or ""), "tier": "prospect"})
            cs = pipeline.contacts(conn, p["id"])
            if cs:
                out.append({"id": "pipeline:contacts", "tier": "tool",
                            "text": " ".join(f"{c['name']} {c.get('title') or ''} {c.get('email') or ''}" for c in cs)})
            if p.get("name") or p.get("url"):
                out.append({"id": "pipeline:prospect", "tier": "tool", "text": f"{p.get('name') or ''} {p.get('url') or ''} {p['slug']}"})
        finally:
            conn.close()
    except Exception:  # noqa: BLE001 - no pipeline record yet
        pass
    return out


def _nth_weekday(year, month, weekday, n):
    from datetime import date, timedelta
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def calendar_facts():
    """Dates nobody needs to invent: today, the shopping/holiday dates sellers mention most, and the meeting slots
    meeting.py last proposed."""
    from datetime import datetime, timedelta, timezone
    d = datetime.now(timezone.utc)
    out = [{"id": "calendar", "tier": "calendar", "text": f"Today is {d.strftime('%A')} {d.day} {d.strftime('%B %Y')} ({d.date().isoformat()})."}]
    for y in (d.year, d.year + 1):
        tg = _nth_weekday(y, 11, 3, 4)
        days = [("Thanksgiving (US)", tg), ("Black Friday", tg + timedelta(days=1)), ("Cyber Monday", tg + timedelta(days=4)),
                ("Christmas Day", datetime(y, 12, 25).date()), ("Boxing Day", datetime(y, 12, 26).date()),
                ("New Year's Day", datetime(y + 1, 1, 1).date()), ("Valentine's Day", datetime(y, 2, 14).date()),
                ("Mother's Day (US)", _nth_weekday(y, 5, 6, 2)), ("Labor Day (US)", _nth_weekday(y, 9, 0, 1)),
                ("Memorial Day (US)", _nth_weekday(y, 6, 0, 1) - timedelta(days=7))]
        for name, dt in days:
            out.append({"id": f"calendar:{name}:{y}", "tier": "calendar",
                        "text": f"{name} {dt.year} is on {dt.strftime('%A')} {dt.day} {dt.strftime('%B')} ({dt.strftime('%b')} {dt.day}, "
                                f"{dt.isoformat()}), {(dt - d.date()).days} days from today."})
    try:
        slots = json.loads((data_home() / "last_slots.json").read_text(encoding="utf-8"))
        out.append({"id": "meeting:slots", "tier": "calendar",
                    "text": " ".join(f"{x.get('theirs')} {x.get('yours')} {x.get('minutes')} minutes" for x in slots.get("slots", []))})
    except (OSError, ValueError):
        pass
    return out


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
                        snippet_file = p.name.upper().startswith("WEB-RESEARCH")
                        for i, fct in enumerate(facts):
                            key = str(fct.get("key", ""))
                            tier = "snippet" if snippet_file or key.startswith("web_") else "tool"
                            sources.append({"id": f"{p.name}#fact{i}", "tier": tier,
                                            # a measured audit fact is crisp: "does not set a viewport" can be contradicted
                                            "crisp": tier == "tool" and key not in ("their_post", "site_description", "person", "person_profile", "person_company", "person_about"),
                                            "text": f"{fct.get('statement', '')} {fct.get('evidence', '')}"})
                        continue
                    raw = json.dumps(data, ensure_ascii=False)
                except ValueError:
                    pass
            tier = "page" if p.parent.name == "sources" else "file"
            for i, para in enumerate(x for x in re.split(r"\n\s*\n|\n(?=\s*[-*|] )", raw) if x.strip()):
                sources.append({"id": f"{p.name}#{i}", "text": para, "tier": tier})
    for i, t in enumerate(texts or []):
        sources.append({"id": f"text{i + 1}", "text": t, "tier": "inline"})
    if slug:
        sources += pipeline_evidence(slug)
    if profile:
        sources += seller_facts()
    sources += calendar_facts()
    sources.append({"id": "meeting", "tier": "calendar", "text": "15 minute 15-minute 20 minute 30 minute quick intro call video call "
                                                                 "this week next week chat"})   # no brand names: they'd become "evidence"
    return sources


def check(draft, sources):
    results = [{"text": c, **match(c, sources)} for c in claims(draft)]
    unsupported = [{"text": r["text"], "why": r["why"]} for r in results if not r["supported"]]
    holes = PLACEHOLDER.findall(draft or "")
    skipped = list(SKIPPED)
    return {"ok": not unsupported and not holes, "checked": len(results), "supported": len(results) - len(unsupported),
            "unsupported": unsupported, "placeholders": holes, "drafts_not_used_as_evidence": skipped,
            "claims": [{"text": r["text"], "supported": r["supported"], "source": r["source"], "tier": r.get("tier"), "why": r["why"]}
                       for r in results],
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

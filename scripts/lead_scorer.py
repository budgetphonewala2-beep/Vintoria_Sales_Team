#!/usr/bin/env python3
"""
Lead Scorer — AI Sales Team for Claude Code
Deterministic BANT (0-100) + MEDDIC completeness scoring from structured signals.
Use it as a cross-check on the qualitative BANT assessment in /sales qualify.

Grade scale (shared by every skill and the PDF report):
    90-100 A+  Hot Lead        75-89 A  Strong        60-74 B  Qualified
    40-59  C   Lukewarm        0-39  D  Poor Fit

Usage:
    python lead_scorer.py input.json
    cat input.json | python lead_scorer.py
    python lead_scorer.py --example        # print a sample input file

Input JSON (every field optional; omit what you don't know — do NOT guess):
{
  "company": "Acme",
  "budget_signals":    {"funding_amount": "$12M", "employee_count": "120",
                        "pricing_visible": true, "tech_spend_indicators": ["HubSpot", "Segment"]},
  "authority_signals": {"decision_makers_found": 3, "c_suite_identified": true, "org_chart_mapped": false},
  "need_signals":      {"pain_points_detected": 2, "job_posts_relevant": true,
                        "reviews_mention_pain": false, "competitor_complaints": 1},
  "timeline_signals":  {"hiring_for_role": true, "recent_funding": true,
                        "contract_renewal": false, "urgency_mentions": 1}
}
"""

import argparse
import json
import re
import sys

EXPECTED_FIELDS = {
    "budget_signals": ["funding_amount", "employee_count", "pricing_visible", "tech_spend_indicators"],
    "authority_signals": ["decision_makers_found", "c_suite_identified", "org_chart_mapped"],
    "need_signals": ["pain_points_detected", "job_posts_relevant", "reviews_mention_pain", "competitor_complaints"],
    "timeline_signals": ["hiring_for_role", "recent_funding", "contract_renewal", "urgency_mentions"],
}

GRADES = [  # (min score, grade, label, action)
    (90, "A+", "Hot Lead", "Prioritize immediately: multi-thread outreach to the buying committee within 24 hours."),
    (75, "A", "Strong Prospect", "Schedule a discovery call — confirm budget and timeline early."),
    (60, "B", "Qualified Lead", "Run the standard outreach sequence; strengthen the weakest MEDDIC area."),
    (40, "C", "Lukewarm", "Nurture with value-add content; fill research gaps before hard selling."),
    (0, "D", "Poor Fit", "Deprioritize — long-term nurture only. Revisit in 90 days or on a trigger event."),
]


# ---------------------------------------------------------------------------
# Input coercion — LLM-produced JSON often has "$10M", "120+", "yes"
# ---------------------------------------------------------------------------

_MULT = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mm": 1e6, "million": 1e6,
         "b": 1e9, "bn": 1e9, "billion": 1e9, "cr": 1e7, "crore": 1e7,
         "l": 1e5, "lakh": 1e5, "lac": 1e5}


def to_number(value):
    """'$12.5M' -> 12500000, '120+' -> 120, '50-200' -> 50 (conservative), None/'' -> 0."""
    if value is None or isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return max(0, value)
    s = str(value).strip().lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(thousand|million|billion|crore|lakh|lac|mm|bn|cr|k|m|b|l)?\b", s)
    if not m:
        return 0
    return float(m.group(1)) * _MULT.get(m.group(2) or "", 1)


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "y", "1", "found", "confirmed")
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return False


def to_list(value):
    if isinstance(value, list):
        return [v for v in value if v]
    if isinstance(value, str) and value.strip():
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


# ---------------------------------------------------------------------------
# BANT (each 0-25)
# ---------------------------------------------------------------------------

def score_budget(s):
    score = 0
    funding = to_number(s.get("funding_amount"))
    score += 10 if funding >= 50e6 else 8 if funding >= 10e6 else 6 if funding >= 5e6 else \
        4 if funding >= 1e6 else 2 if funding > 0 else 0
    emp = to_number(s.get("employee_count"))
    score += 5 if emp >= 500 else 4 if emp >= 100 else 3 if emp >= 50 else 2 if emp >= 10 else 1 if emp > 0 else 0
    if to_bool(s.get("pricing_visible")):
        score += 3
    score += min(len(to_list(s.get("tech_spend_indicators"))) * 2, 7)
    return min(score, 25)


def score_authority(s):
    score = 0
    dm = to_number(s.get("decision_makers_found"))
    score += 10 if dm >= 5 else 8 if dm >= 3 else 5 if dm >= 1 else 0
    if to_bool(s.get("c_suite_identified")):
        score += 8
    if to_bool(s.get("org_chart_mapped")):
        score += 7
    elif dm > 1:
        score += 3
    return min(score, 25)


def score_need(s):
    score = 0
    pains = to_number(s.get("pain_points_detected"))
    score += 8 if pains >= 5 else 6 if pains >= 3 else 3 if pains >= 1 else 0
    if to_bool(s.get("job_posts_relevant")):
        score += 6
    if to_bool(s.get("reviews_mention_pain")):
        score += 5
    complaints = to_number(s.get("competitor_complaints"))
    score += 6 if complaints >= 3 else 4 if complaints >= 1 else 0
    return min(score, 25)


def score_timeline(s):
    score = 0
    if to_bool(s.get("hiring_for_role")):
        score += 7
    if to_bool(s.get("recent_funding")):
        score += 7
    if to_bool(s.get("contract_renewal")):
        score += 6
    urgency = to_number(s.get("urgency_mentions"))
    score += 5 if urgency >= 3 else 3 if urgency >= 1 else 0
    return min(score, 25)


# ---------------------------------------------------------------------------
# MEDDIC completeness (% of evidence present per element)
# ---------------------------------------------------------------------------

def _pct(flags):
    return int(round(sum(1 for f in flags if f) / len(flags) * 100))


def assess_meddic(data):
    b = data.get("budget_signals", {}) or {}
    a = data.get("authority_signals", {}) or {}
    n = data.get("need_signals", {}) or {}
    t = data.get("timeline_signals", {}) or {}
    dm = to_number(a.get("decision_makers_found"))
    m = {
        "metrics": _pct([to_number(b.get("funding_amount")) > 0, to_number(b.get("employee_count")) > 0,
                         to_number(n.get("pain_points_detected")) > 0]),
        "economic_buyer": _pct([to_bool(a.get("c_suite_identified")), dm >= 1]),
        "decision_criteria": _pct([to_bool(b.get("pricing_visible")), len(to_list(b.get("tech_spend_indicators"))) > 0,
                                   to_bool(n.get("reviews_mention_pain"))]),
        "decision_process": _pct([to_bool(a.get("org_chart_mapped")), dm >= 2, to_bool(t.get("contract_renewal"))]),
        "identify_pain": _pct([to_number(n.get("pain_points_detected")) >= 1, to_bool(n.get("job_posts_relevant")),
                               to_number(n.get("competitor_complaints")) >= 1]),
        "champion": _pct([dm >= 1, to_bool(n.get("reviews_mention_pain")), to_bool(t.get("hiring_for_role"))]),
    }
    m["overall"] = int(round(sum(m.values()) / 6))
    return m


# ---------------------------------------------------------------------------
# Grade, confidence, action
# ---------------------------------------------------------------------------

def grade_for(score):
    for floor, grade, label, action in GRADES:
        if score >= floor:
            return grade, label, action
    return GRADES[-1][1:]


def compute_confidence(data):
    """How much of the expected evidence was actually researched (field present and not null).
    A researched 'false' counts as known — confidence is about coverage, not positivity."""
    total = known = 0
    for section, fields in EXPECTED_FIELDS.items():
        sec = data.get(section, {}) or {}
        for f in fields:
            total += 1
            if f in sec and sec[f] is not None and sec[f] != "":
                known += 1
    ratio = known / total
    level = "high" if ratio >= 0.75 else "medium" if ratio >= 0.45 else "low"
    return level, int(round(ratio * 100))


def recommend_action(grade, base_action, meddic):
    gaps = sorted(((k, v) for k, v in meddic.items() if k != "overall"), key=lambda x: x[1])
    weakest = [k.replace("_", " ") for k, v in gaps if v < 50][:3]
    if grade in ("B", "C") and weakest:
        return f"{base_action} Biggest MEDDIC gaps: {', '.join(weakest)}."
    return base_action


def score_lead(data):
    b = score_budget(data.get("budget_signals", {}) or {})
    a = score_authority(data.get("authority_signals", {}) or {})
    n = score_need(data.get("need_signals", {}) or {})
    t = score_timeline(data.get("timeline_signals", {}) or {})
    total = b + a + n + t
    grade, label, base_action = grade_for(total)
    meddic = assess_meddic(data)
    confidence, coverage = compute_confidence(data)
    return {
        "company": data.get("company", "Unknown"),
        "bant_score": total,
        "bant_breakdown": {
            "budget": {"score": b, "max": 25},
            "authority": {"score": a, "max": 25},
            "need": {"score": n, "max": 25},
            "timeline": {"score": t, "max": 25},
        },
        "meddic_completeness": meddic,
        "lead_grade": grade,
        "grade_label": label,
        "confidence_level": confidence,
        "data_coverage_pct": coverage,
        "recommended_action": recommend_action(grade, base_action, meddic),
    }


EXAMPLE = {
    "company": "Acme",
    "budget_signals": {"funding_amount": "$12M", "employee_count": "120", "pricing_visible": True,
                       "tech_spend_indicators": ["HubSpot", "Segment"]},
    "authority_signals": {"decision_makers_found": 3, "c_suite_identified": True, "org_chart_mapped": False},
    "need_signals": {"pain_points_detected": 2, "job_posts_relevant": True, "reviews_mention_pain": False,
                     "competitor_complaints": 1},
    "timeline_signals": {"hiring_for_role": True, "recent_funding": True, "contract_renewal": None,
                         "urgency_mentions": 1},
}


def main():
    parser = argparse.ArgumentParser(
        description="Lead Scorer — BANT + MEDDIC scoring for lead qualification.",
        epilog="Example: python lead_scorer.py input.json   (see --example for the input format)",
    )
    parser.add_argument("input_file", nargs="?", help="Path to input JSON (reads stdin if omitted)")
    parser.add_argument("--example", action="store_true", help="Print an example input JSON and exit")
    args = parser.parse_args()

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    try:
        if args.input_file:
            with open(args.input_file, "r", encoding="utf-8-sig") as f:  # tolerate BOM (PowerShell)
                data = json.load(f)
        else:
            if sys.stdin.isatty():
                parser.error("no input file given and nothing on stdin (try --example)")
            data = json.loads(sys.stdin.read().lstrip("Feff"))
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {args.input_file}")
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: invalid JSON: {exc}")
    if not isinstance(data, dict):
        sys.exit("Error: input must be a JSON object")

    print(json.dumps(score_lead(data), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

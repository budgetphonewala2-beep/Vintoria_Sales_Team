#!/usr/bin/env python3
"""Generates every skills/<name>/SKILL.md from the specs in tools/skill_specs.py, with the shared
portable blocks (scripts, web access, prospect folder, pipeline, honesty, compliance). Run after editing
a spec:  python tools/build_skills.py   — then  python tools/validate_skills.py"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_specs import SKILLS  # noqa: E402

VERSION = "3.0.0"

BEFORE = """## Before you start

1. **Scripts.** `<SCRIPTS>` means the `scripts/` folder of the `sales` skill — `../sales/scripts/` next to this
   skill's folder. Run them with `python` (Windows) or `python3` (macOS/Linux). Every script prints one JSON
   object. Script output is evidence to check, not truth.
2. **Web access.** Use your agent's own web fetch / search if it has them. Otherwise run
   `python <SCRIPTS>/fetch_page.py <url> [<url> ...]` and `python <SCRIPTS>/web_search.py "<query>"`
   (search needs `BRIGHTDATA_API_KEY`). If you can't fetch something, write "Not found" — never fill gaps.
3. **Prospect folder.** Files about one prospect live in `prospects/<slug>/` (slug = domain without `www.`,
   e.g. `acme.com`). Given only a name, look for an existing `prospects/*/` folder first, then find the
   official domain. Never use another prospect's files as context. Shared files (`IDEAL-CUSTOMER-PROFILE.md`,
   `OBJECTION-PLAYBOOK.md`, `SALES-REPORT*`) stay in the working-directory root.
4. **Pipeline.** The pipeline database (`~/.ai-sales-team/pipeline.db`) is the source of truth across
   sessions and agents. Record what you learn with `python <SCRIPTS>/pipeline.py ...` (commands below).
5. **What the user sells.** Read `IDEAL-CUSTOMER-PROFILE.md` if it exists. If it doesn't and you don't know
   the offer, ask once: "What do you sell, and to whom?" If the user sells services (agency, freelancer,
   consultant), judge fit by visible need — site quality, public posts asking for help, hiring for the role,
   ad activity — not by funding or headcount.
6. **Facts, not fiction.** Never invent people, titles, emails, mutual connections, customer results,
   funding or metrics. Unknown = "Not found". Pattern-built emails = `pattern-guessed — verify before
   sending`. A missing proof point = a visible `[ADD REAL CUSTOMER RESULT]` marker.
"""

WRITING = """## Before anything is sent

- Run the claim check on every email/proposal you write and fix it until it passes:
  `python <SCRIPTS>/claim_check.py --draft <file> --evidence "prospects/<slug>/*.md" [--evidence prospects/<slug>/SITE-AUDIT.json] [--evidence-text "<their post>"]`
  Rewrite or delete each unsupported sentence; fill or remove every `[PLACEHOLDER]`.
- Follow `references/compliance.md` (opt-out line, postal address for US, consent rules for UK/EU/Canada/India).
- You write drafts only. The user sends them — never claim an email was sent.
"""

COMPLIANCE = """# Outreach compliance (guidance, not legal advice)

Every sequence must be legal to send:
- Truthful sender identity and subject lines (no fake "Re:"/"Fwd:"), and a working opt-out in every cold
  email (e.g. "Not relevant? Reply 'no' and I won't follow up."). Honour opt-outs immediately.
- **US (CAN-SPAM):** include the sender's physical postal address in the signature.
- **UK (PECR / UK GDPR):** B2B email to corporate addresses is allowed with identification + opt-out; sole
  traders and partnerships need prior consent.
- **EU (GDPR + national ePrivacy laws):** needs a documented legitimate interest and role relevance; Germany
  and some others effectively require prior consent for cold email — flag prospects there.
- **Canada (CASL):** generally requires consent (implied consent only in narrow cases) — flag Canadian prospects.
- **India (DPDP Act 2023):** use business contact details only, state the purpose, honour withdrawal promptly.
- Only mention a mutual connection the user confirmed is real and agreed to be named. Never invent one.
- Never post, comment or DM on social platforms on the user's behalf; suggest the message, the user sends it.
- Deliverability: plain text, at most one link, no tracking pixels, no attachments in the first email,
  verified addresses only (never send to `pattern-guessed` or `invalid`), and warm up new sending domains.
- End the output with a short `Compliance notes` line naming which rules apply to this prospect's country.
"""


def frontmatter(name, description):
    assert len(description) <= 1024, (name, len(description))
    desc = description.replace('"', "'")
    return (f'---\nname: {name}\ndescription: "{desc}"\nlicense: MIT\n'
            'compatibility: "Any agent that supports Agent Skills. Helper scripts need Python 3.9+ (standard library; '
            'reportlab only for PDF). Web access via the agent or the bundled fetch/search scripts."\n'
            f'metadata:\n  author: "Zubair Trabzada (original), Vintoria (portable upgrade)"\n  version: "{VERSION}"\n---\n')


def build(spec):
    parts = [frontmatter(spec["name"], spec["description"]), f"# {spec['title']}\n", spec["intro"].strip() + "\n"]
    if spec.get("before", True):
        parts.append(BEFORE)
    parts.append(spec["body"].strip() + "\n")
    if spec.get("writes_email"):
        parts.append(WRITING)
    if spec.get("refs"):
        parts.append("## References (read when you reach that step)\n\n" +
                     "\n".join(f"- `references/{f}` — {d}" for f, d in spec["refs"]) + "\n")
    return "\n".join(parts)


def main():
    for spec in SKILLS:
        d = ROOT / "skills" / spec["name"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(build(spec), encoding="utf-8", newline="\n")
        if spec.get("writes_email"):
            (d / "references").mkdir(exist_ok=True)
            (d / "references" / "compliance.md").write_text(COMPLIANCE, encoding="utf-8", newline="\n")
        n = (d / "SKILL.md").read_text(encoding="utf-8").count("\n")
        print(f"{spec['name']:<20} {n:>4} lines")


if __name__ == "__main__":
    main()

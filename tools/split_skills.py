#!/usr/bin/env python3
"""One-off migration: move long SKILL.md bodies into references/ (fence-aware) and make the text
agent-neutral. Kept in tools/ so the migration is reproducible; not installed."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAIL_HEADS = ("## Rules", "## Important Rules", "## Quality Standards", "## Terminal Output", "## Error Handling",
              "## Cross-Skill", "## Rules and Constraints")
COMMANDS = ["prospect", "research", "qualify", "contacts", "outreach", "followup", "prep", "proposal", "objections",
            "icp", "competitors", "report-pdf", "report", "quick", "hunt", "audit"]


def neutral(text: str) -> str:
    t = text
    t = re.sub(r"\$HOME/\.claude/skills/sales/templates/([\w-]+)\.md", r"references/template-\1.md", t)
    t = t.replace('"$HOME/.claude/skills/sales/scripts/', '"<SCRIPTS>/').replace("$HOME/.claude/skills/sales/scripts/", "<SCRIPTS>/")
    t = re.sub(r"\bWebFetch\b", "web fetch", t)
    t = re.sub(r"\bWebSearch\b", "web search", t)
    t = t.replace("python3 ", "python ")
    for c in COMMANDS:
        t = re.sub(rf"`/sales {c}([^`]*)`", lambda m, c=c: f"`sales-{c}`" + (f" ({m.group(1).strip()})" if m.group(1).strip() else ""), t)
        t = re.sub(rf"(?<![\w`])/sales {c}\b", f"sales-{c}", t)
    t = t.replace("Claude Code", "your agent")
    return t


def split_sections(lines):
    """Yield (heading_line_index, level) for headings outside code fences."""
    fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence and re.match(r"^#{2} \S", line):
            yield i


def migrate(skill_dir: Path) -> dict:
    src = skill_dir / "SKILL.md"
    text = src.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    body = text[m.end():] if m else text
    lines = body.split("\n")
    heads = list(split_sections(lines))
    # drop the shared-conventions block
    keep_from = 0
    for idx, h in enumerate(heads):
        if lines[h].startswith("## Shared Conventions"):
            keep_from = heads[idx + 1] if idx + 1 < len(heads) else len(lines)
    intro = "\n".join(l for l in lines[:heads[0] if heads else 0] if not l.startswith("<!--")).strip()
    rest = lines[keep_from:]
    rheads = list(split_sections(rest))
    out_i = next((h for h in rheads if re.match(r"^## Output Format", rest[h])), None)
    tail_i = next((h for h in rheads if rest[h].startswith(TAIL_HEADS) and (out_i is None or h > out_i)), None)
    if tail_i is None:
        tail_i = next((h for h in rheads if rest[h].startswith(TAIL_HEADS)), len(rest))
    method_end = out_i if out_i is not None else tail_i
    method = "\n".join(rest[:method_end]).strip()
    output = "\n".join(rest[out_i:tail_i]).strip() if out_i is not None else ""
    tail = "\n".join(rest[tail_i:]).strip()
    ref = skill_dir / "references"
    ref.mkdir(exist_ok=True)
    note = ("> Web access: use your agent's web tools if it has them; otherwise run the scripts in the `sales` skill's\n"
            "> `scripts/` folder (`<SCRIPTS>` = `../sales/scripts/` next to this skill): `fetch_page.py <url>` and\n"
            "> `web_search.py \"<query>\"`. Never invent what you could not fetch — write \"Not found\".\n")
    written = {}
    for name, content in (("playbook.md", method), ("output-format.md", output), ("rules.md", tail)):
        if content:
            title = {"playbook.md": "Playbook", "output-format.md": "Output format", "rules.md": "Rules, errors and integration"}[name]
            (ref / name).write_text(f"# {skill_dir.name} — {title}\n\n{note if name == 'playbook.md' else ''}\n{neutral(content)}\n",
                                    encoding="utf-8")
            written[name] = content.count("\n") + 1
    for t in ref.glob("template-*.md"):
        t.write_text(neutral(t.read_text(encoding="utf-8")), encoding="utf-8")
    return {"skill": skill_dir.name, "intro": intro[:200], **written}


if __name__ == "__main__":
    names = sys.argv[1:] or [p.name for p in sorted((ROOT / "skills").iterdir()) if p.name.startswith("sales-")]
    for n in names:
        print(migrate(ROOT / "skills" / n))

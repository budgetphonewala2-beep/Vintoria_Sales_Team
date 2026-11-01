#!/usr/bin/env python3
"""Validate every skill: the official `skills-ref validate` (if installed) plus stricter portability checks.

Checks: name format == folder, description <= 1024 chars, only standard frontmatter fields, SKILL.md body
< 300 lines, every `references/...` and `<SCRIPTS>/...` file mentioned exists, no agent-specific tools or
paths. Exit 1 on any problem.   Usage: python tools/validate_skills.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SCRIPTS = SKILLS / "sales" / "scripts"
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
FORBIDDEN = [r"\bWebFetch\b", r"\bWebSearch\b", r"Task tool", r"Skill tool", r"subagent_type", r"\$\{CLAUDE_", r"~/\.claude",
             r"\$HOME/\.claude", r"python3 scripts/"]


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fields, cur = {}, None
    for line in m.group(1).split("\n"):
        if re.match(r"^[A-Za-z][\w-]*:", line):
            cur, _, val = line.partition(":")
            fields[cur] = val.strip().strip('"')
        elif cur and line.startswith(" "):
            fields[cur] += "\n" + line
    return fields, text[m.end():]


def check(skill_dir):
    problems = []
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm, body = frontmatter(text)
    if fm is None:
        return ["missing frontmatter"]
    name = fm.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append(f"invalid name '{name}'")
    if name != skill_dir.name:
        problems.append(f"name '{name}' != folder '{skill_dir.name}'")
    desc = fm.get("description", "")
    if not desc or len(desc) > 1024:
        problems.append(f"description length {len(desc)} (must be 1-1024)")
    extra = set(fm) - ALLOWED
    if extra:
        problems.append(f"non-standard frontmatter fields: {sorted(extra)}")
    if body.count("\n") >= 300:
        problems.append(f"body is {body.count(chr(10))} lines (must be < 300)")
    for ref in set(re.findall(r"`references/([\w.-]+\.md)`", text)):
        if not (skill_dir / "references" / ref).exists():
            problems.append(f"missing references/{ref}")
    for script in set(re.findall(r"<SCRIPTS>/([\w-]+\.py)", text)):
        if not (SCRIPTS / script).exists():
            problems.append(f"missing script {script}")
    for f in [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))] if (skill_dir / "references").exists() else [skill_dir / "SKILL.md"]:
        t = f.read_text(encoding="utf-8")
        for pat in FORBIDDEN:
            if re.search(pat, t):
                problems.append(f"{f.relative_to(skill_dir)}: agent-specific text /{pat}/")
    return problems


def official(skill_dir):
    try:
        from skills_ref.validator import validate  # type: ignore
    except ImportError:
        return None
    try:
        errs = validate(skill_dir)
    except Exception as exc:  # noqa: BLE001
        return [f"skills-ref crashed: {exc}"]
    return [str(e) for e in (errs or [])]


def main():
    bad = 0
    for d in sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").exists()):
        probs = check(d)
        off = official(d)
        if off:
            probs += [f"skills-ref: {e}" for e in off]
        status = "ok" if not probs else "FAIL"
        print(f"{status:4} {d.name}" + ("" if off is not None else "  (skills-ref not installed: pip install skills-ref)"))
        for p in probs:
            print(f"     - {p}")
        bad += bool(probs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

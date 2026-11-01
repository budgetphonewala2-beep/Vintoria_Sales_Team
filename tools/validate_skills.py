#!/usr/bin/env python3
"""Validate every skill: the official `skills-ref validate` (if installed) plus stricter portability checks.

Checks: name format == folder, description <= 1024 chars, only standard frontmatter fields, SKILL.md body
< 300 lines, every `references/...` and `<SCRIPTS>/...` file mentioned exists, no agent-specific tools or
paths, and every `python <SCRIPTS>/x.py <subcommand> --flag` written in a skill or reference really exists
(checked against each script's --help), so an agent never runs a command that fails.
Exit 1 on any problem.   Usage: python tools/validate_skills.py
"""

import re
import subprocess
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


_HELP = {}


def _help(args):
    key = tuple(args)
    if key not in _HELP:
        r = subprocess.run([sys.executable, str(SCRIPTS / args[0]), *args[1:], "--help"], capture_output=True, text=True,
                           encoding="utf-8", cwd=str(ROOT))
        _HELP[key] = r.stdout + r.stderr
    return _HELP[key]


def _subcommands(help_text):
    m = re.search(r"positional arguments:\s*\n\s*\{([\w,-]+)\}", help_text)
    return m.group(1).split(",") if m else []


def check_commands(skill_dir):
    """Every python <SCRIPTS>/x.py [sub] --flag mentioned must exist."""
    problems = set()
    files = [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))] if (skill_dir / "references").exists() \
        else [skill_dir / "SKILL.md"]
    for f in files:
        for m in re.finditer(r"python <SCRIPTS>/([\w-]+\.py)([^`\n]*)", f.read_text(encoding="utf-8")):
            script, rest = m.group(1), m.group(2)
            if not (SCRIPTS / script).exists():
                continue                       # reported by check()
            top = _help([script])
            subs = _subcommands(top)
            toks = rest.split()
            sub = toks[0] if toks and toks[0] in subs else None
            if subs and toks and not sub and re.fullmatch(r"[a-z][a-z-]+", toks[0]):
                problems.add(f"{f.name}: {script} has no subcommand '{toks[0]}'")
            h = _help([script, sub]) if sub else top
            for flag in re.findall(r"(?<![\w-])(--[a-z][\w-]*)", rest):
                if not re.search(r"(?<![\w-])" + re.escape(flag) + r"(?![\w-])", h):
                    problems.add(f"{f.name}: {script}{' ' + sub if sub else ''} has no option {flag}")
    return sorted(problems)


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
        probs = check(d) + check_commands(d)
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

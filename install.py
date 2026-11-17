#!/usr/bin/env python3
"""
Cross-platform installer for the Vintoria sales skills (Windows, macOS, Linux). Standard library only.

    python install.py                      # default: ~/.agents/skills + ~/.claude/skills
    python install.py --agent codex        # one agent (see table below); repeatable
    python install.py --agent all --link   # symlink instead of copy (edits in the repo apply immediately)
    python install.py --with-claude-agents # also install the optional Claude Code subagents (parallel roles)
    python install.py --project .          # install into ./.agents/skills of a project instead of your home
    python install.py --uninstall          # remove the skills (and the Claude subagents) again
    python install.py --dry-run            # show what would happen

User-level skill folders (checked against each agent's official docs, 2026-11):
    claude-code  ~/.claude/skills            (code.claude.com/docs/skills)
    codex        ~/.agents/skills            (learn.chatgpt.com/docs/build-skills — Codex reads $HOME/.agents/skills)
    cursor       ~/.cursor/skills            (cursor.com/docs/skills — also reads ~/.agents/skills and ~/.claude/skills)
    gemini       ~/.gemini/skills            (geminicli.com/docs/cli/skills — ~/.agents/skills is an alias)
    opencode     ~/.config/opencode/skills   (opencode.ai/docs/skills — also reads ~/.claude/skills, ~/.agents/skills)
    agents       ~/.agents/skills            (shared folder read by Codex, Cursor, Gemini CLI and OpenCode)

Existing copies of these skills, and the skills and subagents of earlier versions (sales, sales-*), are moved to
~/.ai-sales-team/backups/<timestamp>/ before installing, so an upgrade never leaves stale or duplicate skills
behind and never loses anything.
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
TARGETS = {
    "claude-code": HOME / ".claude" / "skills",
    "codex": HOME / ".agents" / "skills",
    "cursor": HOME / ".cursor" / "skills",
    "gemini": HOME / ".gemini" / "skills",
    "opencode": Path(os.environ.get("XDG_CONFIG_HOME") or HOME / ".config") / "opencode" / "skills",
    "agents": HOME / ".agents" / "skills",
}
CLAUDE_AGENTS = HOME / ".claude" / "agents"
# v3 and earlier shipped these skills / subagents; v4 merged them into the 8 vintoria-* skills.
LEGACY_SKILLS = ["sales", "sales-setup", "sales-icp", "sales-hunt", "sales-audit", "sales-prospect", "sales-research",
                 "sales-qualify", "sales-contacts", "sales-competitors", "sales-outreach", "sales-followup", "sales-reply",
                 "sales-book", "sales-prep", "sales-proposal", "sales-objections", "sales-autopilot", "sales-report",
                 "sales-report-pdf"]
LEGACY_AGENTS = ["sales-company", "sales-contacts", "sales-opportunity", "sales-competitive", "sales-strategy",
                 "sales-hunter", "sales-researcher", "sales-writer", "sales-closer"]


def skills():
    return sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())


def backup_dir():
    return HOME / ".ai-sales-team" / "backups" / datetime.now().strftime("%Y%m%d-%H%M%S")


def _remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def link_or_copy(src, dst, link):
    if link:
        try:
            os.symlink(src, dst, target_is_directory=True)
            return "linked"
        except (OSError, NotImplementedError):
            if os.name == "nt":       # Windows without Developer Mode: a directory junction needs no admin rights
                r = subprocess.run(["cmd", "/c", "mklink", "/J", str(dst), str(src)], capture_output=True, text=True)
                if r.returncode == 0:
                    return "junction"
            print("    (could not link, copying instead)")
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evals"))   # test cases stay in the repo
    return "copied"


def retire_legacy(target, dry, backups):
    """Move the skills of earlier versions out of the way (backed up, never deleted)."""
    for name in LEGACY_SKILLS:
        old = target / name
        if old.exists() or old.is_symlink():
            print(f"  {'would retire' if dry else 'retired'} old skill {name} (backed up)")
            if dry:
                continue
            if old.is_symlink():
                old.unlink()
            else:
                backups.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old), str(backups / f"{target.parent.name}-{name}"))


def install(target, link, dry, backups):
    print(f"\n-> {target}")
    retire_legacy(target, dry, backups)
    for s in skills():
        dst = target / s.name
        if dst.exists() or dst.is_symlink():
            if dry:
                print(f"  would replace {s.name} (old copy backed up)")
                continue
            if dst.is_symlink():
                dst.unlink()
            else:
                backups.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(backups / f"{target.parent.name}-{s.name}"))
        if dry:
            print(f"  would install {s.name}")
            continue
        target.mkdir(parents=True, exist_ok=True)
        print(f"  {link_or_copy(s, dst, link):8} {s.name}")


def uninstall(target, dry):
    for dst in [target / s.name for s in skills()] + [target / n for n in LEGACY_SKILLS]:
        if dst.exists() or dst.is_symlink():
            print(f"  {'would remove' if dry else 'removed'} {dst}")
            if not dry:
                _remove(dst)


def check_python():
    ok = sys.version_info >= (3, 9)
    print(f"Python {sys.version.split()[0]} {'ok' if ok else '— needs 3.9+'}")
    try:
        import reportlab  # noqa: F401  (only checking it is installed)
        print("reportlab installed (PDF reports work)")
    except ImportError:
        print("reportlab not installed — only needed for PDF reports: python -m pip install reportlab")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="Install the Vintoria sales skills into your coding agents.")
    ap.add_argument("--agent", action="append", choices=[*TARGETS, "all"], help="target agent (repeatable; default: agents + claude-code)")
    ap.add_argument("--project", help="install into <project>/.agents/skills instead of your home folder")
    ap.add_argument("--link", action="store_true", help="symlink/junction instead of copying")
    ap.add_argument("--with-claude-agents", action="store_true", help="also install optional Claude Code subagents")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if not check_python():
        sys.exit(1)
    chosen = a.agent or ["agents", "claude-code"]
    if "all" in chosen:
        chosen = ["agents", "claude-code"]
    if a.project:
        targets = [Path(a.project).resolve() / ".agents" / "skills"]
    else:
        targets = list(dict.fromkeys(TARGETS[c] for c in chosen))
    backups = backup_dir()
    for t in targets:
        if a.uninstall:
            print(f"\n-> {t}")
            uninstall(t, a.dry_run)
        else:
            install(t, a.link, a.dry_run, backups)
    for name in LEGACY_AGENTS:
        old = CLAUDE_AGENTS / f"{name}.md"
        if old.exists() and not a.project:
            print(f"  {'would retire' if a.dry_run else 'retired'} old subagent {name}")
            if not a.dry_run:
                backups.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old), str(backups / f"agent-{name}.md"))
    if a.with_claude_agents or a.uninstall:
        src = ROOT / "adapters" / "claude-code" / "agents"
        for f in sorted(src.glob("*.md")):
            dst = CLAUDE_AGENTS / f.name
            if a.uninstall:
                if dst.exists():
                    print(f"  {'would remove' if a.dry_run else 'removed'} {dst}")
                    if not a.dry_run:
                        dst.unlink()
            elif not a.dry_run:
                CLAUDE_AGENTS.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)
                print(f"  subagent {f.stem} -> {CLAUDE_AGENTS}")
    if len(targets) > 1 and not a.project:
        print("\nNote: Cursor and OpenCode read both ~/.agents/skills and ~/.claude/skills. If they list a skill twice,"
              " reinstall with a single --agent.")
    if not a.uninstall and not a.dry_run:
        if backups.exists():
            print(f"\nPrevious copies backed up to {backups}")
        print("\nDone. Restart your agent, then say:  \"use vintoria-setup\" (first run)  or  \"aaj ka kaam batao\".")
        print("Optional API keys go in ~/.ai-sales-team/.env  (BRIGHTDATA_API_KEY, BRIGHTDATA_ZONE, HUNTER_API_KEY).")


if __name__ == "__main__":
    main()

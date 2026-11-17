"""Installer (temp home) and skill validation tests."""

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_skill_valid():
    v = _load("validate_skills", ROOT / "tools" / "validate_skills.py")
    skills = sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())
    assert len(skills) == 8
    for d in skills:
        assert v.check(d) == [], d.name
        assert v.check_commands(d) == [], d.name
        official = v.official(d)
        assert official in (None, []), (d.name, official)


def test_generated_skills_are_up_to_date():
    b = _load("build_skills", ROOT / "tools" / "build_skills.py")
    for spec in b.SKILLS:
        on_disk = (ROOT / "skills" / spec["name"] / "SKILL.md").read_text(encoding="utf-8")
        assert on_disk == b.build(spec), f"{spec['name']}: run python tools/build_skills.py"


def test_installer_copy_backup_uninstall(tmp_path, monkeypatch):
    env = {**__import__("os").environ, "HOME": str(tmp_path), "USERPROFILE": str(tmp_path)}
    old = tmp_path / ".claude" / "skills" / "sales" / "templates"
    old.mkdir(parents=True)
    (old / "stale.md").write_text("old", encoding="utf-8")
    for base in (tmp_path / ".agents" / "skills", tmp_path / ".claude" / "skills"):   # a v3 install to upgrade
        (base / "sales-outreach").mkdir(parents=True)
        (base / "sales-outreach" / "SKILL.md").write_text("---\nname: sales-outreach\n---\nold", encoding="utf-8")
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".claude" / "agents" / "sales-writer.md").write_text("old", encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--with-claude-agents"], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    for base in (tmp_path / ".agents" / "skills", tmp_path / ".claude" / "skills"):
        assert len([p for p in base.iterdir() if (p / "SKILL.md").exists()]) == 8
        assert not (base / "sales-outreach").exists()                               # old v3 skill retired
    assert (tmp_path / ".claude" / "skills" / "vintoria-sales" / "scripts" / "core" / "pipeline.py").exists()
    assert not (tmp_path / ".claude" / "skills" / "sales" / "templates").exists()          # stale files gone
    assert list((tmp_path / ".ai-sales-team" / "backups").glob("*/*sales"))                  # but backed up
    assert len(list((tmp_path / ".claude" / "agents").glob("vintoria-*.md"))) == 9
    assert not list((tmp_path / ".claude" / "agents").glob("sales-*.md"))            # old subagent retired
    r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--uninstall"], env=env, capture_output=True, text=True)
    assert r.returncode == 0 and not list((tmp_path / ".agents" / "skills").iterdir())
    assert not list((tmp_path / ".claude" / "agents").glob("vintoria-*.md"))


def test_installer_project_and_dry_run(tmp_path):
    env = {**__import__("os").environ, "HOME": str(tmp_path), "USERPROFILE": str(tmp_path)}
    proj = tmp_path / "my project"
    r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--project", str(proj), "--dry-run"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0 and "would install vintoria-lead-hunt" in r.stdout and not proj.exists()
    r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--project", str(proj)], env=env, capture_output=True, text=True)
    assert (proj / ".agents" / "skills" / "vintoria-outreach" / "references" / "compliance.md").exists()

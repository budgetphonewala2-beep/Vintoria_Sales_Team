# Changelog

## 3.0.0 — 2026-11-01 (portable upgrade)

### Added
- **Portable Agent Skills**: spec-only frontmatter (name, description, license, compatibility, metadata); all
  16 skills validated with `skills-ref`; English + Hinglish trigger phrases.
- `sales-hunt` — find public posts asking for your service (EN/HI/Hinglish), judge with a 30-example rubric.
- `sales-audit` — fact-only website audit with evidence, and a fact-to-hook guide.
- Scripts: `pipeline.py` (SQLite pipeline), `intent_scan.py` (Bright Data SERP + phrase scoring),
  `site_audit.py`, `find_email.py` (Hunter finder/verifier), `claim_check.py`, `fetch_page.py`, `web_search.py`.
- `lead_scorer.py --mode agency` buyer model.
- Role playbooks for `sales-prospect` (`references/role-*.md`), runnable in any agent.
- `install.py` (Windows/macOS/Linux; claude-code, codex, cursor, gemini, opencode, shared `~/.agents/skills`),
  with backups, `--link`, `--uninstall`, `--dry-run`.
- `references/compliance.md` and a first-email style guide with 10 good/bad examples.
- Tests (`tests/`), `tools/validate_skills.py`, `tools/build_skills.py`, `AUDIT.md`.

### Changed
- SKILL.md bodies cut from 320-850 lines to 50-110; playbooks, output formats and templates moved to `references/`.
- Claude Code subagents moved to `adapters/claude-code/agents/` (optional parallelism).
- TLS verification uses certifi when available; certificate errors are never reported as prospect facts.
- `install.sh` / `uninstall.sh` are thin wrappers around `install.py`.

### Fixed
- `lead_scorer.py` stdin BOM handling (`lstrip("Feff")` stripped letters, not the BOM).
- Plus the interim fixes listed in AUDIT.md (title classifier, pricing tiers, tech detection, PDF crash, grades).

## 2.x — interim fix pass (local)
Frontmatter, per-prospect folders, script bug fixes, compliance notes.

## 1.0 — upstream
Original release by Zubair Trabzada.

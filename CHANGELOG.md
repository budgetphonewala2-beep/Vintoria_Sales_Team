# Changelog

## 3.1.0 — 2026-11-01 (end to end: find → contact → follow up → reply → book)

### Added
- `sales-autopilot` — daily driver: builds today's agenda from the pipeline and works through it end to end.
- `sales-reply` — classify and answer replies; pipeline updated automatically.
- `sales-book` — slots in both time zones, `.ics` invites, prep/reminder scheduling, meeting outcomes.
- `outreach.py` — touch log, business-day follow-up cadence (`CADENCE_DAYS`), optional SMTP sending behind
  gates (verified address, claim check, opt-out, postal address, daily limit, do-not-contact list, dry run
  first, plain text, `List-Unsubscribe`), WhatsApp click-to-chat links.
- `reply_triage.py` — 12 reply categories in English, Hindi and Hinglish; stops follow-ups, suppresses
  opt-outs, marks bounced addresses invalid, never moves a deal backwards.
- `meeting.py` — free-slot finder that respects both parties' hours (stretches only your day for India ↔ US),
  RFC 5545 invites, clash detection, outcomes (held / no-show / rescheduled / cancelled).
- `pipeline.py today`, `suppress`, `suppressed`; `report` now includes activity (touches, meetings booked).
- `examples/env.example`, GitHub Actions CI, `tools/build_skills.py --check`, `tests/test_end_to_end.py`.

### Changed
- Email-writing skills: approve-then-send/log flow replaces "drafts only"; compliance notes cover WhatsApp,
  sending volume and automatic opt-outs.
- `sales-outreach`, `sales-followup`, `sales-prep`, `sales-report` and the router use the new scripts.
- Generated files carry a "do not edit" notice; author metadata updated.

### Fixed
- `fetch_url` no longer retries without TLS verification when a certificate fails (AUDIT #7 was only partly fixed).
- `site_audit.py` no longer counts links that got no HTTP answer (timeout/TLS on the auditing machine) as broken.

### Removed
- `tools/split_skills.py` (one-time v2 → v3 migration helper).

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

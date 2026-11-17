# Optional agent adapters

The skills in `skills/` work in every agent that supports Agent Skills, with no adapter. Adapters only add
agent-specific extras.

## Claude Code — sales team roles + parallel prospect roles
`claude-code/agents/*.md` are Claude Code subagents (frontmatter: name, description, tools):
- **Team roles** — `vintoria-hunter`, `vintoria-researcher`, `vintoria-writer`, `vintoria-closer` (the Manager is the
  main session running `vintoria-sales`). Handoffs and targets: `skills/vintoria-sales/references/team.md`.
- **Prospect roles** — `vintoria-company`, `vintoria-contacts`, `vintoria-opportunity`, `vintoria-competitive`,
  `vintoria-strategy` (same text as `skills/vintoria-prospect-research/references/role-*.md`), so the full analysis in
  `vintoria-prospect-research` can run the four research roles in parallel.
Install: `python install.py --agent claude-code --with-claude-agents` (old `sales-*` subagents are retired and backed up).

## Codex CLI
Codex reads skills from `~/.agents/skills` (and `.agents/skills` in a repo). `python install.py --agent codex`.
Optional `AGENTS.md` snippet for a sales workspace:

```markdown
## Sales work
For prospecting, outreach, follow-ups, proposals or pipeline questions, use the `vintoria-sales` skill and the
`vintoria-*` skills it routes to. Run `vintoria-setup` first if SELLER-PROFILE.json is missing. Record every prospect
in the pipeline (`pipeline.py`). Claim-check every email; send nothing I haven't approved; never post on social media.
```

## Cursor
Cursor reads `~/.cursor/skills`, `~/.agents/skills` and `~/.claude/skills`. Install to ONE of them to avoid
duplicate entries: `python install.py --agent cursor`. Invoke manually with `/` + the skill name.
Optional rule (`.cursor/rules/sales.mdc`):

```markdown
---
description: Sales workflow rules
alwaysApply: false
---
Use the vintoria-* skills for prospecting and outreach. Drafts only — never send. Claim-check every email.
```

## Gemini CLI
Gemini reads `~/.gemini/skills` and the `~/.agents/skills` alias: `python install.py --agent gemini`, then
`/skills list` to confirm. `/skills disable <name>` hides a skill you don't need.

## OpenCode
OpenCode reads `~/.config/opencode/skills` (plus `~/.claude/skills` and `~/.agents/skills`):
`python install.py --agent opencode`.

## Any other agent
If it supports Agent Skills, point it at the `skills/` folder or copy the folders into its skills directory.
If it doesn't, give it `skills/vintoria-sales/SKILL.md` as instructions — the skills only need a shell, files and Python.

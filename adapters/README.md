# Optional agent adapters

The skills in `skills/` work in every agent that supports Agent Skills, with no adapter. Adapters only add
agent-specific extras.

## Claude Code — parallel prospect roles
`claude-code/agents/*.md` are Claude Code subagents (frontmatter: name, description, tools) with the same
text as `skills/sales-prospect/references/role-*.md`. With them installed, `sales-prospect` can run the four
research roles in parallel. Install: `python install.py --agent claude-code --with-claude-agents`.

## Codex CLI
Codex reads skills from `~/.agents/skills` (and `.agents/skills` in a repo). `python install.py --agent codex`.
Optional `AGENTS.md` snippet for a sales workspace:

```markdown
## Sales work
For prospecting, outreach, follow-ups, proposals or pipeline questions, use the `sales` skill and the
`sales-*` skills it routes to. Record every prospect in the pipeline (`pipeline.py`). Never send email or
post on social media; write drafts for me to send. Run claim_check.py on every email before showing it.
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
Use the sales-* skills for prospecting and outreach. Drafts only — never send. Claim-check every email.
```

## Gemini CLI
Gemini reads `~/.gemini/skills` and the `~/.agents/skills` alias: `python install.py --agent gemini`, then
`/skills list` to confirm. `/skills disable <name>` hides a skill you don't need.

## OpenCode
OpenCode reads `~/.config/opencode/skills` (plus `~/.claude/skills` and `~/.agents/skills`):
`python install.py --agent opencode`.

## Any other agent
If it supports Agent Skills, point it at the `skills/` folder or copy the folders into its skills directory.
If it doesn't, give it `skills/sales/SKILL.md` as instructions — the skills only need a shell, files and Python.

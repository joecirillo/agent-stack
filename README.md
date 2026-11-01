# agent-stack

My agent stack (workflow skills, review agents, git guard hooks, and shared
instructions), packaged so it works in **Claude Code and Codex**, locally
and in cloud sessions.

## What's in it

| Path | What | Read by |
| - | - | - |
| `instructions/AGENTS.md` | Shared working conventions | Both (via project `AGENTS.md`) |
| `skills/*/SKILL.md` | Issue → branch → PR workflow skills ([Agent Skills](https://agentskills.io) format) | Both |
| `agents/*.md` | Review and planning subagents | Claude Code |
| `hooks/` | Commit guard (secrets + 50/72), protect-main, quality gate, compaction recap | Claude Code |
| `.claude-plugin/` | Plugin manifest + single-plugin marketplace | Claude Code |

## Two ways to use it

### 1. As a Claude Code plugin (personal machine)

```bash
claude plugin marketplace add joecirillo/agent-stack
claude plugin install agent-stack@agent-stack
```

Components are namespaced, e.g. `/agent-stack:start-issue`.

### 2. Vendored into a project (Codex, cloud sessions, teammates)

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/agent-stack init ~/dev/some-project
```

`init` writes committed files into the project, so cloud sessions get the
stack from the clone itself with no network or private-repo access:

| Project path | Purpose |
| - | - |
| `AGENTS.md` | Stack instructions in a managed block; your own content outside it is kept |
| `CLAUDE.md` | Gets an `@AGENTS.md` import so Claude Code reads the same instructions |
| `.agents/skills/<name>/` | Vendored skills, where Codex discovers them |
| `.claude/skills/<name>` | Relative symlinks to the above, so Claude Code reads the same copy |
| `.claude/agents/` | Subagents |
| `.agent-stack/hooks/` + `.claude/settings.json` | Hook scripts, merged into existing settings |
| `.agent-stack/manifest.json` | Paths `init` owns |

Re-run `init` to update. It only replaces paths listed in the manifest and
refuses to overwrite anything the project created itself. Skills marked
`disable-model-invocation: true` also get a Codex `agents/openai.yaml`
with `allow_implicit_invocation: false`, so they stay manual-only in both
tools.

Hooks need `jq`, `python3`, and `gh` on the machine running the agent.

## Development

```bash
.venv/bin/pytest
claude plugin validate --strict .
```

# agent-stack

My Claude Code agent stack as a plugin: issue-driven workflow skills, review
agents, git guard hooks, and my global instructions. It installs the same way
on my machine and in Claude Code cloud sessions, so projects don't need to
commit any of it.

## What's in it

| Path | What |
| - | - |
| `skills/` | Issue → branch → PR workflow skills |
| `agents/` | Review and planning subagents |
| `hooks/` | Commit guard (secrets + 50/72), protect-main, quality gate, compaction recap |
| `instructions/core.md` | Global instructions for every session: code design, testing, git, quality bar |
| `instructions/interactive.md` | Instructions for sessions I'm watching: about me, teaching, ask-first workflow |
| `instructions/unattended.md` | Replaces the ask-first rules in cloud sessions: proceed on defaults, record assumptions in the PR |
| `cloud/setup.sh` | Setup script for Claude Code cloud environments |
| `.claude-plugin/` | Plugin manifest and a marketplace listing this one plugin |

Plugin components are namespaced, e.g. `/agent-stack:start-issue`.

## Install on your machine

Run from any folder. Both commands write to `~/.claude`, not to a project:

```bash
claude plugin marketplace add joecirillo/agent-stack
claude plugin install agent-stack@agent-stack
```

Plugins can't supply `CLAUDE.md` instructions, so point your global
`~/.claude/CLAUDE.md` at this repo's instruction files with imports:

```markdown
@~/dev/agent-stack/instructions/core.md
@~/dev/agent-stack/instructions/interactive.md
```

## Install in cloud sessions

A cloud session only sees the cloned project repo, and it doesn't install
plugins that a project's `.claude/settings.json` enables. Instead, install the
stack into the cloud VM's user config with the environment's setup script:

1. On [claude.ai/code](https://claude.ai/code), edit the cloud environment.
2. Paste the contents of [`cloud/setup.sh`](cloud/setup.sh) into **Setup script** and save.

The script clones this repo, writes `core.md` plus `unattended.md` to
`~/.claude/CLAUDE.md`, and installs the plugin. Cloud sessions usually run
without anyone watching, so `interactive.md`'s ask-first rules would stall
them. A session then has:

| What | Comes from |
| - | - |
| Global instructions | `~/.claude/CLAUDE.md`, written by the script from `core.md` + `unattended.md` |
| Project instructions | The project's own `CLAUDE.md` |
| Skills, agents, hooks | This plugin |

The script exits non-zero if any step fails, which stops the session from
starting, so a broken install is visible instead of silently missing.

Cloud environments cache the setup result for about seven days. To pick up
changes to this repo sooner, edit and re-save the setup script, which forces a
rebuild.

## Development

Load the working copy into one session without installing it:

```bash
claude --plugin-dir ~/dev/agent-stack
```

Validate before pushing:

```bash
claude plugin validate --strict .
```

The plugin's `version` in `.claude-plugin/plugin.json` controls updates:
installed copies only refresh when it changes, so bump it on each release.

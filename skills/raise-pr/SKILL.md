---
name: raise-pr
description: Use once an issue's implementation is complete and ready to become a PR -- tests passing, nothing left to change. Reviews the current diff, scaled to its size/risk and routed to whichever reviewer(s) fit what it actually touches, then opens a GitHub PR with the review findings included in the description. Can also be invoked manually with /raise-pr.
disable-model-invocation: true
---

You are raising a pull request for the current branch's changes. Follow these steps
in order — do not skip the review step even if the diff looks small or obviously correct.

1. Run `git status` and `git diff` (against the base branch, typically `main`) to see
   the full scope of changes.
2. Run the project's lint and test commands (see the project's CLAUDE.md or AGENTS.md) and confirm they pass. If
   either fails, stop and report the failure — do not proceed to review or PR creation.
3. Decide how much local review this diff needs, and which reviewer(s), based on what
   it actually does — not fixed file paths, since this skill runs across projects with
   very different structures:
   - **Small/low-risk diff** (copy, styling, docs, a small non-behavioral change): run
     the `code-review` skill only. Don't invoke the heavier reviewers below.
   - **Everything else**: run `code-review` as the baseline, plus:
     - the `api-reviewer` subagent, if the diff adds or modifies an API route,
       RPC/tRPC procedure, controller, or endpoint handler.
     - the `security-review` skill, if the diff touches authentication,
       authorization, session/cookie handling, secrets, credential-shaped
       environment variables, database schema, or migrations.
   - These aren't mutually exclusive, and neither api-reviewer nor security-review
     may apply. State out loud which reviewer(s) you're invoking (or that you're
     scaling down to code-review only) and why, so a wrong call is easy to spot
     and correct.
   - `code-review` and `security-review` are Claude Code built-ins, and subagents
     are a Claude Code feature. In a tool without them (e.g. Codex), do each
     review pass inline yourself using the reviewer's checklist instead of
     skipping it.
4. If any invoked reviewer reports **blocking issues**, stop. Report them back and do
   not create the PR. Fixing blocking issues is not part of this skill — that's a
   separate step; this skill only reviews and raises.
5. If there are no blocking issues (should-fix items and notes are fine to include,
   not fine to block on), draft the PR:
   - Title: concise, imperative mood, matches the change being made
   - Body:
     - What changed and why
     - A "Review notes" section listing any should-fix items or notes from the
       reviewer(s) that ran, so the human reviewer sees them without re-running
       the review
     - Reference the originating issue if one exists (`Closes #N`)
6. Create the PR via `gh pr create` (confirm the base branch first — don't assume `main`
   without checking). Do not merge it. Do not mark it ready-for-review if it was drafted
   as a draft — leave that decision to the human reviewer.
7. Report the PR URL back.

This skill produces a PR for human review — it does not replace that review. Its job
is to make sure the PR that lands in front of the human reviewer has already had the
obvious issues caught, without running every reviewer on every change regardless of
size or risk.

In a cloud session, `gh pr create` and `gh pr view` are blocked because they use
GraphQL. Open the PR with the built-in GitHub tools or the REST API
(`gh api repos/{owner}/{repo}/pulls`) instead of stopping.

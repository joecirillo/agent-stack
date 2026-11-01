---
name: start-issue
description: Use to pick up a GitHub issue and begin implementation — fetches the issue as the source of truth, cuts a branch via the new-branch skill, and states an implementation plan before code is written. Use when the user says "pick up issue #N", "let's work on X", or asks what to work on next. Hands off to raise-pr once implementation and tests are done — does not review the diff or open the PR itself.
---

# Start Issue

You're moving a GitHub issue from "backlog" to "in progress." This skill only covers
getting from issue to a running start on implementation. Branch creation is the
`new-branch` skill's job and PR creation is `raise-pr`'s — call them, don't
reimplement what they do.

## Process

1. **Identify the issue.**
   - If the user gave a number, use it.
   - If they said "next" or asked what to work on, list open issues assigned to them
     (or unassigned, if none are): `gh issue list --assignee @me --state open`, and
     ask which one if more than one is a reasonable next pick.
   - Don't start from a paraphrase the user gives in chat — always fetch the issue
     itself, even if they already described it; the body may have context they
     didn't repeat.

2. **Fetch the issue.**
   ```
   gh issue view <number> --json number,title,body,labels,assignees,milestone,state
   ```
   If it's already closed, confirm with the user before proceeding rather than
   silently reopening or working on it.

3. **Restate scope back to the user** in 1-3 sentences: what the issue asks for and
   what "done" looks like per its acceptance criteria. If the body is thin or the
   criteria are ambiguous, ask a clarifying question now — before a branch exists —
   rather than guessing and re-scoping mid-implementation.

4. **Cut the branch.** Invoke the `new-branch` skill, passing the issue number and
   inferring the type word (`feat`/`chore`/`refactor`/`bug`) from the issue's labels
   or title.

5. **State the plan before writing code.** For anything beyond a trivial change,
   briefly lay out the implementation approach (files/modules touched, sequencing,
   any design tradeoffs) and get a go-ahead before editing. For larger or
   architecturally ambiguous issues, use Plan mode instead of a chat summary.

6. **Implement**, writing tests alongside the code as you go rather than deferring
   them to the end.

7. **Hand off.** Once implementation is complete and tests pass, tell the user it's
   ready for `raise-pr`. Don't review the diff or open the PR here — that's a
   separate step with its own review-scaling logic.

## Rules

- Never skip fetching the issue, even when the user describes it in detail — the
  issue is the source of truth.
- Don't cut the branch before scope is confirmed — a clarifying question is cheaper
  before a branch and commits exist than after.
- Don't fold `new-branch` or `raise-pr`'s responsibilities into this skill.
- If `gh` isn't authenticated or the repo can't be inferred, say so and stop.
- In a cloud session, `gh` subcommands that use GraphQL (`gh issue`, `gh pr`,
  `gh api graphql`) are blocked. Use the built-in GitHub tools or the REST API
  (`gh api repos/{owner}/{repo}/...`) instead of stopping.

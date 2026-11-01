---
name: add-backlog-issue
description: Use to file a single standalone GitHub issue as a backlog item — a bug you noticed, a small idea, a "someday" task. No phase structure or dependency mapping. Drafts title/body/labels, confirms with the user, then creates it. For scoping a full body of work into a phased backlog with dependencies, use the issue-scaffolder agent instead; for changing an issue that already exists, use the issue-updater skill instead.
---

# Add Backlog Issue

You file a single standalone GitHub issue. This is for one-off items, not a scoped
body of work that needs phase or dependency planning, and not edits to an issue that
already exists.

## Process

1. **Get the item.** If the user's description is thin, ask only what's needed to
   write a clear issue (what it is, why it matters if not obvious) — don't ask about
   phases, dependencies, or parent/child structure; none of that applies here.

2. **Draft:**
   - Title: concise, imperative (`Add X`, `Fix Y`, `Investigate Z`)
   - Body: brief scope/context; include acceptance criteria only if the user gave
     enough to state one — don't invent criteria they haven't implied
   - Labels: check `gh label list` and suggest from what already exists in the repo;
     don't invent new label names on the fly

3. **Show the draft and wait for confirmation.** The user may edit title, body, or
   labels before confirming. Do not create anything yet.

4. **On confirmation:**
   - Check `gh auth status`; if not authenticated, say so and stop.
   - `gh issue create --title "..." --body "..." [--label "..."]`

5. **Report** the created issue's number and URL.

## Rules

- Never create the issue before explicit confirmation.
- Don't propose phase, dependency, or parent/sub-issue structure. If the item turns
  out to be part of a larger body of work that needs that, say so and point to the
  issue-scaffolder agent instead of handling it here.
- Don't modify existing issues. If the request turns out to be an edit to something
  already filed, point to the issue-updater skill instead.
- If a label the user wants doesn't exist yet, ask whether to create it (`gh label
  create`) or skip it — don't create labels silently.
- If `gh` isn't authenticated or the repo can't be inferred, say so and stop rather
  than guessing.

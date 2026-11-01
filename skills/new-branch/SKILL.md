---
name: new-branch
description: Cut a new git branch following this repo owner's naming convention (type/issue-number-short-description, e.g. feat/123-new-endpoint). Use when starting implementation on a new feature, chore, refactor, or bugfix and no branch exists yet for it.
---

Use this when implementation is about to begin and the work doesn't already have
a branch.

1. Determine the type word: `feat`, `chore`, `refactor`, or `bug`.
2. Determine the issue number:
   - Use one the user gave you.
   - Otherwise, if the work maps to a tracked GitHub issue, find it (e.g. `gh issue list`) or ask which issue.
   - If there's genuinely no tracked issue (a tiny ad-hoc task), ask for a short slug instead of stalling on a number.
3. Build the branch name: `<type>/<issue-number>-<short-kebab-description>`, e.g. `feat/123-new-endpoint`, `bug/456-fix-pagination-offset`. Keep the description short (3-5 words).
4. Create and check out the branch from the up-to-date target branch (usually `main`):
   ```
   git fetch origin
   git checkout -b <branch-name> origin/main
   ```
5. Confirm the branch name back to the user before starting substantive work.

Don't invent an issue number — if none exists and the user doesn't want to create
one, use a descriptive slug in place of the number rather than making one up.

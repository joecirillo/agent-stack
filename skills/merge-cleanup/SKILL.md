---
name: merge-cleanup
description: Clean up after a pull request has merged - delete the feature branch both locally and on the remote, and sync the local target branch. Use once a PR is confirmed merged, not before.
---

Use this after confirming a PR has actually merged (check with `gh pr view <number>`
or `gh pr status` if unsure — don't assume from context alone).

1. Confirm the PR's merge state before deleting anything:
   ```
   gh pr view <number> --json state,mergedAt
   ```
   Stop and ask if it isn't merged yet.
2. Switch to the target branch (usually `main`) and pull the merged changes:
   ```
   git checkout main
   git pull origin main
   ```
3. Delete the feature branch locally and on the remote:
   ```
   git branch -d <branch-name>
   git push origin --delete <branch-name>
   ```
   Use `-D` instead of `-d` only if git refuses due to unmerged commits and you've
   already confirmed the PR merged (e.g. it was squash-merged, so the local branch
   looks "unmerged" to git even though its content landed).
4. Report back which branches were deleted, locally and remotely.

This is cleanup only — it doesn't open or merge PRs. For opening a PR with review
included, use the existing `raise-pr` skill.

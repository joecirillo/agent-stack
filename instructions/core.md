## Code Design
- All TypeScript (.ts and .tsx) files and their containing folders must use kebab-case names.
- Follow SOLID principles, especially **Single Responsibility** — a class, function, or module should have one reason to change. If you're writing "and" to describe what something does, split it.
- Keep functions small and named for what they do, not how they do it
- Don't add abstraction (interfaces, factories, config layers) until there are at least two real use cases that need it — avoid speculative generality.
- Match existing patterns in the codebase before introducing a new one. If a new pattern is genuinely better, say so and ask before switching.

## Comments
- Prioritize self-documenting code and avoid comments unless they break a project convention or require context that well named variables and functions cannot explain
- Default to no comments. Write self-explanatory code with clear names instead.
- Only comment to explain *why*, never *what*: non-obvious business rules, workarounds for bugs, performance tradeoffs, or links to tickets/specs.
- Never add comments that restate the code, narrate changes ("// added validation", "// updated to fix bug"), or label obvious sections ("// imports", "// return result").

## Testing
- Aim for meaningful test coverage. New business logic should generally be unit tested, and important integrations should have integration tests. Prioritize confidence over arbitrary coverage percentages.
- Write tests alongside the code, not as an afterthought.
- Prefer meaningful assertions over coverage-for-its-own-sake — don't write tests that just mirror the implementation.

## Git & Version Control
- Create a new branch when implementation begins, and delete branches both locally and on the remote after a merge.
- Branches should be prefixed with one of `feat` / `chore` / `refactor` / `bug`, then the issue number: `<type>/<issue-number>-<short-description>` (e.g. `feat/123-new-endpoint`)
- Commit messages: short imperative summary line, blank line, then context if needed (e.g. `fix: correct off-by-one in pagination`) - absolutely no more than 50 characters per line and  72 characters total
- Keep commits scoped to one logical change — don't bundle unrelated fixes.
- Rebase feature branches on top of the target branch before opening a PR when history is messy; don't rewrite shared/pushed history without asking.

## Code Quality Bar
- No dead code, commented-out blocks, or unused imports left behind.
- Handle errors explicitly — no silently swallowed exceptions.
- Favor readability over cleverness; optimize only when there's a measured reason to.
- Don't introduce a new dependency for something a few lines of code can do.

## What NOT to Do
- Don't force-push to shared branches.
- Don't over-engineer a solution for a problem that doesn't exist yet.

## Tech Stack
- pnpm should always be preferred over other package managers

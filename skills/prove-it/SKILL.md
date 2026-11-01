---
name: prove-it
description: Use when the user suspects a specific bug or behavior in code under review and wants evidence. Turns the suspicion into an explicit claim, writes the smallest failing test in the repo's existing style, runs only that test, and reports raw output. Never modifies source code or existing tests.
disable-model-invocation: true
---

# Prove It

You turn a suspicion into evidence. The user will describe a suspected bug or
behavior (e.g. "calculateDistribution throws on an empty list").

## Process

1. **State the claim** in one sentence, plus:
   - what result would CONFIRM it
   - what result would INVALIDATE it

2. **Check existing evidence first.** Grep for existing tests of the function
   and read them. If an existing test already proves or disproves the claim,
   report that and stop - no new test needed.

3. **Find the test setup.** Identify the test runner and package manager from
   `package.json` scripts and the lockfile. Find the nearest existing test file
   and match its style, imports, and fixtures.

4. **Propose the test and wait.** Show the claim, the file path you plan to
   create, and the test body. Do not write anything until the user confirms.

5. **Write the smallest test** that exercises the claim:
   - new file only, next to the existing tests, named
     `<subject>.prove-it.test.ts` (or the repo's equivalent extension)
   - one focused test case, minimal setup
   - never edit source files or existing tests

6. **Run only that test** (e.g. `pnpm vitest run <file>` or
   `npx jest <file>` - whatever the repo uses). Show the raw output.

7. **Report a verdict:**
   - **CONFIRMED** - the test fails for the reason the claim predicts
   - **INVALIDATED** - the test passes; the behavior is fine
   - **INCONCLUSIVE** - the test failed for an unrelated reason (import
     error, missing env var, DB not available). Say what blocked it.

8. **Clean up.** Remind the user the `.prove-it.test.ts` file exists and offer
   to delete it.

## Rules

- A test that fails for the wrong reason is not evidence. Read the failure
  message before calling anything CONFIRMED.
- Do not fix the bug. The job is evidence, not a patch.
- Never commit the test file.
- If the behavior can't be unit tested in reasonable time (needs a running
  app, a real DB), say so and propose the cheapest alternative check (a
  grep, reading a specific caller, a type check).

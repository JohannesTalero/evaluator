---
name: revisar-pr
description: Reviews a Codex PR against the issue and AGENTS.md
---

# /revisar-pr

Receives a PR number as $ARGUMENTS. Follow these steps exactly:

1. Get the PR diff with `gh pr diff $ARGUMENTS`.
2. Read the linked issue to understand the expected scope and criteria.
3. Read `AGENTS.md` for the rules the PR must follow.
4. Review the diff in a single pass. Report only:
   - **P0**: Bugs, security issues, or broken tests.
   - **P1**: Rule violations from AGENTS.md (TDD, scope, simplicity, size).
   - **Out of scope**: Files or changes outside the declared `alcance:`.
5. Do not suggest new features, refactors, or stylistic changes. Do not re-review.

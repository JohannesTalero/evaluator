---
name: cerrar-pr
description: Runs final checks and opens a PR with the template
---

# /cerrar-pr

Follow these steps exactly:

1. Run `make check` and confirm it passes. Show the summary.
2. Call the `simplificador` subagent with the current diff — remove anything it flags as unnecessary or out of scope.
3. If the task entry in `tareas/plan.yaml` has `seguridad: true`, run `/security-review` on the diff.
4. Open the PR with `gh pr create` using the project template. Fill in:
   - The `alcance:` line with the globs from the plan entry.
   - The issue number.
   - What the PR does (1-3 lines) and what it does NOT do.
   - How it was tested.
   - The security checklist from `AGENTS.md`.

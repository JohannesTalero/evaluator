---
name: traspaso
description: Generates a handoff note for the current branch
---

# /traspaso

Follow these steps exactly:

1. Run `make traspaso` to generate `progreso/<ID>.md` with the branch, commits, and touched files.
2. Open the generated file and complete the "Que falta" section with the remaining work.
3. Complete the "Siguiente paso concreto" section with the exact next action another agent should take.
4. Commit the handoff note (even if tests are red).
5. Ask for permission to push the branch.

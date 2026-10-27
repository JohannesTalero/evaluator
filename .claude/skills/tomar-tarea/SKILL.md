---
name: tomar-tarea
description: Takes an issue number and starts working on it following AGENTS.md
---

# /tomar-tarea

Receives an issue number as $ARGUMENTS. Follow these steps exactly:

1. Read `progreso/$ID.md` if it exists — it's a handoff from another session or agent.
2. Read the task entry in `tareas/plan.yaml` for this ID. Note the `alcance`, `criterios`, `pruebas_borde`, and `seguridad` fields.
3. Read the corresponding section in `docs/proyecto.md` for the full context (criteria and edge cases).
4. Create or resume the branch `<id>-<slug>` in lowercase (e.g., `d1.2-registro-archivos`). Never work on `main`.
5. Start by writing tests that fail — convert the `pruebas_borde` from the document into test cases.
6. Run the tests and confirm they fail before writing production code.

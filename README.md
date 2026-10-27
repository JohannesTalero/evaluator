# Calificador de Exámenes

Aplicación web para que un profesor suba exámenes manuscritos, la IA proponga notas por criterio con justificación y el profesor las apruebe. Ninguna nota es final sin su aprobación.

Este repositorio arranca con el **sistema de soporte**: las reglas, los rituales y las puertas automáticas para que Claude Code y Codex construyan en paralelo, con PRs pequeños, TDD y seguridad desde el día uno. El código de la aplicación todavía no existe; lo construyen las tareas de `tareas/plan.yaml`.

## Dónde está cada cosa

| Ruta | Para qué |
| --- | --- |
| `docs/proyecto.md` | Documento del proyecto: qué, por qué, criterios y pruebas borde |
| `docs/flujo-de-trabajo.md` | **Empieza aquí.** Cómo se trabaja con los dos agentes |
| `docs/decisiones/` | Decisiones tomadas (ADR) |
| `tareas/plan.yaml` | Las tareas del proyecto partidas en PRs pequeños |
| `AGENTS.md` | Reglas para Claude y Codex (fuente única) |
| `CLAUDE.md` | Importa `AGENTS.md` y añade lo específico de Claude |
| `.claude/` | Permisos, sandbox, hooks, skills y subagentes de Claude Code |
| `.codex/config.toml` | Sandbox y aprobaciones de Codex |
| `.github/` | CI con puertas, plantillas de PR e issue |
| `scripts/` | Verificaciones, traspaso y creación de issues |
| `progreso/` | Notas de traspaso entre sesiones o entre agentes |
| `api/`, `front/`, `infra/`, `evals/`, `contrato/` | Las áreas de la aplicación (vacías al inicio) |

## Primeros pasos

1. Lee `docs/flujo-de-trabajo.md` y haz la instalación de una sola vez.
2. Sube este repo a GitHub y protege `main`.
3. `make issues` para ver los issues que se crearían; `make issues-crear` para crearlos.
4. Asigna los primeros issues desbloqueados a cada agente y arranca.

## Comandos

```bash
make check          # todo lo que exista: lint, tests, escáneres
make check-rapido   # lint y tests
make traspaso       # nota de traspaso de la rama actual
make issues         # simula la creación de issues desde el plan
```

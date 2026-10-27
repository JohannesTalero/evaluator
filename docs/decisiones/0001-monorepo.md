# 0001 — Un solo repositorio para front, API e infraestructura

- Fecha: 2026-10-27
- Estado: aceptada

## Contexto

El documento del proyecto (tarea A2) propone repositorios separados para front, API e infraestructura. El desarrollo lo hacen dos agentes (Claude Code y Codex) que necesitan ver el contrato OpenAPI y el código de ambos lados para no romper la integración, y trabajan con worktrees por tarea.

## Decisión

Un monorepo con `api/`, `front/`, `infra/`, `evals/` y `contrato/`, con un solo CI que ejecuta solo las áreas que existen.

## Consecuencias

- Un agente ve el contrato y los dos lados en el mismo lugar; los cambios de contrato se revisan en un solo PR.
- Un solo juego de reglas (`AGENTS.md`), hooks y CI.
- Los despliegues de cada área se separan por rutas en CI (tarea A2), no por repositorio.
- Para revertir: dividir con `git subtree split` por carpeta.

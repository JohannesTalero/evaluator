# 0002 — Claude Code y Codex construyen en paralelo

- Fecha: 2026-10-27
- Estado: aceptada

## Contexto

El presupuesto es de 40 USD al mes: Claude Pro y ChatGPT Plus (Codex). Cada plan tiene cuota limitada por ventana de 5 horas y por semana, y los límites son independientes.

## Decisión

Los dos agentes construyen tareas del mismo plan. Cada issue tiene un solo dueño (`agente:claude` o `agente:codex`), una rama y un worktree. Se asigna por cuota disponible, no por especialidad. El que no escribió un PR lo revisa. Las reglas viven en `AGENTS.md`; CI es igual para los dos.

## Consecuencias

- Cuando un agente se queda sin cuota, el otro sigue, con traspaso por `progreso/<ID>.md`.
- Cada modelo revisa los puntos ciegos del otro.
- Riesgo de choques en archivos compartidos: se controla con la línea `alcance:`, migraciones de una en una y PRs pequeños.
- Los hooks de Claude no existen en Codex: para Codex, la puerta dura es CI.

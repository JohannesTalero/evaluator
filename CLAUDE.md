@AGENTS.md

## Solo para Claude Code

- Modelo: Sonnet por defecto. Usa `/model opusplan` solo al planear una tarea nueva y grande.
- Skills del proyecto: `/tomar-tarea`, `/cerrar-pr`, `/traspaso`, `/revisar-pr`. Subagente: `simplificador`.
- Hooks activos: no puedes editar código de producción sin haber tocado un test en la rama, y no puedes terminar con `make check-rapido` en rojo. Si un hook bloquea, arregla la causa; si crees que el hook está mal, dilo y detente.
- Usa `/clear` al cambiar de issue.

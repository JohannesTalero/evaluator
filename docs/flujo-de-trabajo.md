# Flujo de trabajo — guía para el humano

Esta guía es para ti, no para los agentes (ellos leen `AGENTS.md`). Explica cómo se mueve una tarea desde el plan hasta `main` con Claude y Codex construyendo en paralelo.

## El sistema de soporte en una imagen

```
 docs/proyecto.md ──► tareas/plan.yaml ──► GitHub Issues (tablero)
   (qué y por qué)     (PRs pequeños)        (estado y dueño)
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
                   Claude Code                                          Codex
             (CLAUDE.md → AGENTS.md)                                (AGENTS.md)
        hooks: TDD + check al terminar                     sandbox workspace-write
                         │                                                 │
                         └──────────► rama <id>-<slug> ◄──────────────────┘
                                            │
                                            ▼
                             PR con plantilla y línea "alcance:"
                                            │
                     CI: tamaño · alcance · lint · tests · escáneres · secretos
                                            │
                  revisión cruzada (el que no escribió revisa) ──► tú haces merge
```

Las capas, de la más suave a la más dura:

1. **Instrucciones** (`AGENTS.md`): el agente las sigue casi siempre.
2. **Skills y subagentes** (`.claude/`): rituales repetibles para no olvidar pasos.
3. **Hooks** (`.claude/hooks/`): bloquean de verdad en Claude; no dependen de que el modelo "se acuerde".
4. **Permisos y sandbox** (`.claude/settings.json`, `.codex/config.toml`): limitan qué puede tocar cada agente.
5. **CI** (`.github/workflows/ci.yml`): la última puerta, igual para los dos agentes. Si CI está en rojo, no hay merge.

## Instalación (una sola vez)

1. Herramientas base: `git`, `gh` (autenticado), `python3`, `make`, `uv`, Node 22, Terraform.
2. Claude Code y Codex CLI, cada uno con su suscripción.
3. En Codex, abre el repo y márcalo como **confiable**; si no, ignora `.codex/config.toml`.
4. Cuota visible:
   - Claude: `ccusage` en la línea de estado (ver su README); dentro de Claude Code, `/usage`.
   - Codex: `/status` en la CLI o Settings > Usage.
5. Opcional, recomendado:
   - **Vibe Kanban** (`npx vibe-kanban`) como tablero que lanza cada tarjeta con el agente que elijas, en su propio worktree.
   - **which-ai-to-use** para el traspaso automático cuando un agente llega al límite.
6. En GitHub:
   - Protege `main`: PR obligatorio, CI en verde y una aprobación.
   - Activa Codex code review en el repo (sin revisión automática: se pide a mano).
   - Crea las etiquetas `agente:claude`, `agente:codex`, `seguridad`, `soporte`, `pr-grande-justificado`.
7. Crea los issues desde el plan: `make issues` (simulación) y luego `make issues-crear`.

## Rutina de cada ronda

1. Mira la cuota de los dos.
2. Elige en el tablero los issues desbloqueados (sus `depende_de` ya están en `main`).
3. Asigna: la tarea grande al agente con más cuota; dos tareas en paralelo solo si sus `alcance` no se cruzan.
4. Lanza cada agente con una frase: "Toma el issue #N". En Claude, `/tomar-tarea N`.
5. Cuando abran PR: pide la revisión cruzada, espera CI y haz merge.

## Ciclo de un PR

1. Tests en rojo (pruebas borde del documento).
2. Código mínimo hasta verde.
3. Pase de simplificación (subagente `simplificador` en Claude).
4. Revisión de seguridad si la entrada tiene `seguridad: true`.
5. `make check` en verde.
6. PR con plantilla → CI → revisión del otro agente → corrección de P0/P1 → merge.

## Cuando algo se atasca

| Situación | Qué hacer |
| --- | --- |
| Un agente se queda sin cuota | `make traspaso`, push de la rama, el otro agente toma el mismo issue leyendo `progreso/<ID>.md` |
| El hook de TDD bloquea | Correcto: falta el test. Si es un archivo que no necesita test (configuración), ajusta el hook en un PR `soporte` |
| CI rechaza por tamaño | Parte el PR. Solo si de verdad no se puede, etiqueta `pr-grande-justificado` y explica por qué |
| CI rechaza por alcance | El agente tocó algo que no debía: que lo revierta, o corrige la línea `alcance:` si el issue estaba mal definido |
| Los dos agentes chocan en un archivo | Señal de mala partición: rebase del que llegó segundo y ajusta el plan |
| El mismo error se repite | No lo corrijas a mano cada vez: conviértelo en regla de `AGENTS.md`, en hook o en test (PR `soporte`) |

## Relevo automático

`make relevo ISSUE=<N>` lanza un agente sin interfaz y, si se queda sin cuota, pasa el turno al otro automáticamente. Variables opcionales: `EMPIEZA=claude|codex` (por defecto claude) y `MAX_RELEVOS=3`.

- **Cuándo usarlo:** un issue a la vez, bien definido, con alcance claro. Ideal para tareas que uno solo no puede terminar por cuota.
- **Qué no hace:** no hace push, no abre PRs, no hace merge. Esos pasos siguen siendo tuyos (o de `/cerrar-pr`).
- **Qué riesgo tiene:** la detección del límite depende de un mensaje de texto que puede cambiar. Si el proveedor cambia el mensaje, el relevo puede fallar.
- **Cómo actualizar los patrones:** edita `scripts/relevo-patrones.txt` (un patrón por línea, ignorando comentarios). No hace falta tocar el código.
- **Candado:** crea `progreso/.relevo-<ID>.lock` para evitar dos relevos simultáneos sobre el mismo issue. Se limpia al salir, incluso con Ctrl+C.
- **Bitácora:** cada acción queda en `progreso/relevo-<ID>.log` con hora, agente, resultado y commit. Nunca registra la salida completa de los agentes.

## Cómo evoluciona este sistema

Cada error repetido de un agente es una señal para endurecer el sistema, no un mal día. Regla práctica:

- Primera vez: lo corriges en la revisión.
- Segunda vez: una línea en `AGENTS.md`.
- Tercera vez: un hook, un test o una puerta de CI.

Mantén `AGENTS.md` corto: si pasa de 150 líneas, mueve el detalle a `docs/` y deja un puntero.

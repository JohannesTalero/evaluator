#!/usr/bin/env bash
set -euo pipefail

# Relevo automatico entre agentes Claude y Codex.
# Uso: make relevo ISSUE=<N> [EMPIEZA=claude|codex] [MAX_RELEVOS=3]
#
# Variables de entorno para testing:
#   RELEVO_CLAUDE_CMD  — comando que reemplaza a claude -p (agente falso)
#   RELEVO_CODEX_CMD   — comando que reemplaza a codex exec (agente falso)

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ISSUE="${ISSUE:-}"
EMPIEZA="${EMPIEZA:-claude}"
MAX_RELEVOS="${MAX_RELEVOS:-3}"

# --- Funciones auxiliares ---

log_bitacora() {
    local id="$1" agente="$2" resultado="$3" commit="${4:-}"
    local logfile="$ROOT/progreso/relevo-${id}.log"
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') agente=$agente resultado=$resultado commit=$commit" >> "$logfile"
}

limpiar() {
    local lockfile="$1"
    if [ -f "$lockfile" ]; then
        rm -f "$lockfile"
    fi
}

cargar_patrones() {
    local archivo="$ROOT/scripts/relevo-patrones.txt"
    if [ ! -f "$archivo" ]; then
        echo ""
        return
    fi
    grep -v '^\s*#' "$archivo" | grep -v '^\s*$' | tr '\n' '|' | sed 's/|$//'
}

es_sin_cuota() {
    local salida="$1"
    local patrones
    patrones="$(cargar_patrones)"
    if [ -z "$patrones" ]; then
        return 1
    fi
    if echo "$salida" | grep -qiE "$patrones"; then
        return 0
    fi
    return 1
}

extraer_id() {
    local issue_num="$1"
    local plan="$ROOT/tareas/plan.yaml"
    if [ ! -f "$plan" ]; then
        echo ""
        return
    fi
    # Busca el id que corresponde al issue number (simplificado: usa el issue como indice)
    # En produccion se buscaria en GitHub; aqui confiamos en que ISSUE corresponde a un id del plan.
    # Para el script, ID se pasa via la variable RELEVO_ID o se extrae de la rama.
    local branch
    branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
    echo "$branch" | sed 's/-.*//'
}

# --- Validaciones ---

if [ -z "$ISSUE" ]; then
    echo "ERROR: falta ISSUE. Uso: make relevo ISSUE=<N>" >&2
    exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
if [ "$BRANCH" = "main" ]; then
    echo "ERROR: no se puede ejecutar relevo en main." >&2
    exit 1
fi

ID="${RELEVO_ID:-$(echo "$BRANCH" | sed 's/-.*//')}"
if [ -z "$ID" ]; then
    echo "ERROR: no se pudo determinar el ID de la tarea." >&2
    exit 1
fi

LOCKFILE="$ROOT/progreso/.relevo-${ID}.lock"
if [ -f "$LOCKFILE" ]; then
    echo "ERROR: ya existe un relevo activo para $ID ($LOCKFILE)." >&2
    exit 1
fi

mkdir -p "$ROOT/progreso"
echo "$$" > "$LOCKFILE"
trap 'limpiar "$LOCKFILE"' EXIT INT TERM

# --- Instruccion para los agentes ---

INSTRUCCION="Toma el issue #${ISSUE} siguiendo AGENTS.md. Si existe progreso/${ID}.md, leelo primero y continua desde 'Siguiente paso concreto'. Cuando make check este en verde y el alcance cumplido, escribe 'estado: listo-para-pr' en progreso/${ID}.md y detente. No hagas push."

# --- Comandos de agentes ---

CMD_CLAUDE="${RELEVO_CLAUDE_CMD:-claude -p \"$INSTRUCCION\" --output-format json --permission-mode acceptEdits}"
CMD_CODEX="${RELEVO_CODEX_CMD:-codex exec --approval-mode full-auto \"$INSTRUCCION\"}"

# --- Bucle de relevo ---

agente_actual="$EMPIEZA"
relevos=0

while [ "$relevos" -lt "$MAX_RELEVOS" ]; do
    relevos=$((relevos + 1))
    echo "=== Relevo $relevos/$MAX_RELEVOS — agente: $agente_actual ==="

    if [ "$agente_actual" = "claude" ]; then
        cmd="$CMD_CLAUDE"
    else
        cmd="$CMD_CODEX"
    fi

    salida=""
    codigo=0
    salida=$(eval "$cmd" 2>&1) || codigo=$?

    # Clasificar resultado
    progreso_file="$ROOT/progreso/${ID}.md"

    # Caso 1: listo-para-pr
    if [ -f "$progreso_file" ] && grep -qi 'estado:.*listo-para-pr' "$progreso_file" 2>/dev/null; then
        # Verificar con make check
        if (cd "$ROOT" && make check-rapido 2>&1); then
            echo "OK: $agente_actual termino con exito."
            log_bitacora "$ID" "$agente_actual" "listo" "$(git rev-parse --short HEAD 2>/dev/null || echo '?')"
            exit 0
        else
            echo "AVISO: $agente_actual dijo listo-para-pr pero make check falla."
            log_bitacora "$ID" "$agente_actual" "listo-check-falla" "$(git rev-parse --short HEAD 2>/dev/null || echo '?')"
            # No se acepta como listo, sigue como error
            echo "ERROR: estado inconsistente. Deteniendo relevo."
            exit 1
        fi
    fi

    # Caso 2: sin cuota
    if es_sin_cuota "$salida"; then
        echo "AVISO: $agente_actual sin cuota. Preparando traspaso..."

        # Ejecutar traspaso
        (cd "$ROOT" && make traspaso 2>&1) || true

        # Commit de lo pendiente
        (cd "$ROOT" && git add -A && git commit -m "wip(relevo): $ID corte de $agente_actual" 2>&1) || true

        commit_hash="$(git rev-parse --short HEAD 2>/dev/null || echo '?')"
        log_bitacora "$ID" "$agente_actual" "sin-cuota" "$commit_hash"

        # Cambiar al otro agente
        if [ "$agente_actual" = "claude" ]; then
            agente_actual="codex"
        else
            agente_actual="claude"
        fi

        # Si ya hicimos todos los relevos, salir
        if [ "$relevos" -ge "$MAX_RELEVOS" ]; then
            echo "MAX_RELEVOS alcanzado ($MAX_RELEVOS). Traspaso escrito, esperando cuota."
            log_bitacora "$ID" "-" "max-relevos" "$commit_hash"
            exit 1
        fi

        continue
    fi

    # Caso 3: error desconocido
    echo "ERROR: $agente_actual termino con estado desconocido (codigo=$codigo)."
    log_bitacora "$ID" "$agente_actual" "error" "$(git rev-parse --short HEAD 2>/dev/null || echo '?')"
    echo "No se pasa el turno. Revisa la salida del agente."
    exit 1
done

echo "MAX_RELEVOS alcanzado ($MAX_RELEVOS). Deteniendo."
exit 1

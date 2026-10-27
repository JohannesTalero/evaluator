#!/usr/bin/env bash
# Generates progreso/<ID>.md from the current branch.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
RAMA=$(git rev-parse --abbrev-ref HEAD)

if [ "$RAMA" = "main" ] || [ "$RAMA" = "HEAD" ]; then
  echo "Error: no puedes generar traspaso desde main." >&2
  exit 1
fi

ID=$(echo "$RAMA" | sed 's/-.*//')
if [ -z "$ID" ]; then
  echo "Error: no se pudo extraer el ID de la rama '$RAMA'." >&2
  echo "Formato esperado: <id>-<slug>, ej: d1.2-registro-archivos" >&2
  exit 1
fi

ARCHIVO="$ROOT/progreso/${ID}.md"
mkdir -p "$ROOT/progreso"

COMMITS=$(git log main..HEAD --oneline 2>/dev/null || echo "(sin commits)")
ARCHIVOS_TOCADOS=$(git diff --name-only main...HEAD 2>/dev/null || echo "(sin cambios)")

CHECK_SALIDA=$(cd "$ROOT" && make check-rapido 2>&1) && CHECK_ESTADO="PASA" || CHECK_ESTADO="FALLA"

cat > "$ARCHIVO" << EOF
# Traspaso: $ID

- **Rama:** $RAMA
- **Ultimo check-rapido:** $CHECK_ESTADO

## Commits frente a main

\`\`\`
$COMMITS
\`\`\`

## Archivos tocados

\`\`\`
$ARCHIVOS_TOCADOS
\`\`\`

## Que falta

<!-- Completar antes del push -->

## Siguiente paso concreto

<!-- Completar antes del push -->
EOF

echo "Traspaso generado: $ARCHIVO"

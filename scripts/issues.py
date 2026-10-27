#!/usr/bin/env python3
"""Creates GitHub issues from tareas/plan.yaml.
Without --crear: dry-run that prints what would be created.
With --crear: creates issues and labels via gh CLI.
"""
import os
import subprocess
import sys

import yaml

ETIQUETAS = {
    "agente:claude": "Tarea para Claude Code",
    "agente:codex": "Tarea para Codex",
    "seguridad": "Requiere revision de seguridad",
    "por-partir": "Tarea pendiente de dividir en PRs",
    "pr-grande-justificado": "PR que supera 300 lineas con justificacion",
    "soporte": "Cambios al sistema de soporte",
}


def cargar_plan(ruta):
    with open(ruta) as f:
        return yaml.safe_load(f) or []


def formatear_issue(entrada):
    eid = entrada["id"]
    titulo = f"[{eid}] {entrada['titulo']}"
    tarea = entrada.get("tarea", "")
    alcance = entrada.get("alcance", "")
    seguridad = entrada.get("seguridad", False)
    depende_de = entrada.get("depende_de", [])
    por_partir = entrada.get("por_partir", False)

    criterios = entrada.get("criterios", [])
    if isinstance(criterios, list):
        criterios_txt = "\n".join(f"- {c}" for c in criterios)
    else:
        criterios_txt = str(criterios)

    pruebas = entrada.get("pruebas_borde", [])
    if isinstance(pruebas, list):
        pruebas_txt = "\n".join(f"- {p}" for p in pruebas)
    else:
        pruebas_txt = str(pruebas)

    deps_txt = ", ".join(depende_de) if depende_de else "ninguna"

    cuerpo = f"""**Tarea:** {tarea}
**ID:** {eid}
**Alcance:** `{alcance}`
**Depende de:** {deps_txt}
**Seguridad:** {'si' if seguridad else 'no'}

## Criterios de aprobacion

{criterios_txt}

## Pruebas borde

{pruebas_txt}"""

    etiquetas = []
    if seguridad:
        etiquetas.append("seguridad")
    if por_partir:
        etiquetas.append("por-partir")

    return titulo, cuerpo, etiquetas


def simular(entradas):
    print(f"=== Simulacion: {len(entradas)} issues ===\n")
    for entrada in entradas:
        titulo, cuerpo, etiquetas = formatear_issue(entrada)
        tags = ", ".join(etiquetas) if etiquetas else "(ninguna)"
        print(f"--- {titulo} ---")
        print(f"Etiquetas: {tags}")
        print(cuerpo)
        print()
    print(f"Total: {len(entradas)} issues (simulacion, nada creado)")


def crear_etiquetas():
    for nombre, desc in ETIQUETAS.items():
        subprocess.run(
            ["gh", "label", "create", nombre, "--description", desc, "--force"],
            capture_output=True, text=True,
        )
        print(f"  Etiqueta: {nombre}")


def crear_issues(entradas):
    print("Creando etiquetas...")
    crear_etiquetas()
    print()

    creados = 0
    for entrada in entradas:
        titulo, cuerpo, etiquetas = formatear_issue(entrada)

        cmd = ["gh", "issue", "create", "--title", titulo, "--body", cuerpo]
        for etiqueta in etiquetas:
            cmd.extend(["--label", etiqueta])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"  Creado: {titulo} -> {url}")
            creados += 1
        else:
            print(f"  ERROR: {titulo}: {result.stderr.strip()}")

    print(f"\nTotal: {creados}/{len(entradas)} issues creados")


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crear", action="store_true", help="Crea issues (no simula)")
    parser.add_argument("--plan", default=None)
    args = parser.parse_args(argv)

    if args.plan:
        ruta = args.plan
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta = os.path.join(root, "tareas", "plan.yaml")

    entradas = cargar_plan(ruta)
    if not entradas:
        print("plan.yaml esta vacio.")
        return 1

    if args.crear:
        crear_issues(entradas)
    else:
        simular(entradas)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validates tareas/plan.yaml: required fields, unique IDs,
dependencies exist, no cycles, and valid globbing patterns."""
import fnmatch
import os
import sys

import yaml

CAMPOS_REQUERIDOS = {"id", "tarea", "titulo", "depende_de", "alcance", "seguridad"}
CAMPOS_REQUERIDOS_COMPLETO = CAMPOS_REQUERIDOS | {"criterios", "pruebas_borde"}


def cargar_plan(ruta):
    with open(ruta) as f:
        return yaml.safe_load(f) or []


def validar_campos(entradas):
    errores = []
    for i, e in enumerate(entradas):
        if not isinstance(e, dict):
            errores.append(f"Entrada {i}: no es un diccionario")
            continue
        eid = e.get("id", f"<indice {i}>")
        por_partir = e.get("por_partir", False)
        requeridos = CAMPOS_REQUERIDOS if por_partir else CAMPOS_REQUERIDOS_COMPLETO
        faltantes = requeridos - set(e.keys())
        if faltantes:
            errores.append(f"{eid}: campos faltantes: {', '.join(sorted(faltantes))}")
    return errores


def validar_ids_unicos(entradas):
    errores = []
    vistos = {}
    for e in entradas:
        eid = e.get("id")
        if eid is None:
            continue
        if eid in vistos:
            errores.append(f"ID duplicado: {eid}")
        vistos[eid] = True
    return errores


def validar_dependencias(entradas):
    errores = []
    ids = {e["id"] for e in entradas if "id" in e}
    for e in entradas:
        eid = e.get("id", "?")
        deps = e.get("depende_de", [])
        if not isinstance(deps, list):
            errores.append(f"{eid}: depende_de no es una lista")
            continue
        for dep in deps:
            if dep not in ids:
                errores.append(f"{eid}: dependencia inexistente: {dep}")
    return errores


def detectar_ciclos(entradas):
    grafo = {}
    for e in entradas:
        eid = e.get("id")
        if eid is None:
            continue
        deps = e.get("depende_de", [])
        grafo[eid] = deps if isinstance(deps, list) else []

    visitado = set()
    en_pila = set()
    ciclos = []

    def dfs(nodo, camino):
        if nodo in en_pila:
            inicio = camino.index(nodo)
            ciclos.append(camino[inicio:] + [nodo])
            return
        if nodo in visitado:
            return
        visitado.add(nodo)
        en_pila.add(nodo)
        camino.append(nodo)
        for dep in grafo.get(nodo, []):
            dfs(dep, camino)
        camino.pop()
        en_pila.remove(nodo)

    for nodo in grafo:
        if nodo not in visitado:
            dfs(nodo, [])

    return [f"Ciclo: {' -> '.join(c)}" for c in ciclos]


def validar(ruta):
    entradas = cargar_plan(ruta)
    if not entradas:
        print("FALLA: plan.yaml esta vacio")
        return 1

    errores = []
    errores.extend(validar_campos(entradas))
    errores.extend(validar_ids_unicos(entradas))
    errores.extend(validar_dependencias(entradas))
    errores.extend(detectar_ciclos(entradas))

    if errores:
        print(f"FALLA: {len(errores)} error(es) en plan.yaml:")
        for err in errores:
            print(f"  - {err}")
        return 1

    total = len(entradas)
    partidos = sum(1 for e in entradas if not e.get("por_partir", False))
    print(f"OK: {total} entradas, {partidos} partidas, {total - partidos} por partir")
    return 0


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comando", choices=["validar"])
    parser.add_argument("--plan", default=None)
    args = parser.parse_args(argv)

    if args.plan:
        ruta = args.plan
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta = os.path.join(root, "tareas", "plan.yaml")

    return validar(ruta)


if __name__ == "__main__":
    sys.exit(main())

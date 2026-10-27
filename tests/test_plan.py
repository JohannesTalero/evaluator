"""Tests for scripts/plan.py — plan.yaml validation."""
import os
import sys
import textwrap

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import plan as plan_mod


def _escribir_plan(tmp_path, entradas):
    ruta = tmp_path / "plan.yaml"
    ruta.write_text(yaml.dump(entradas, allow_unicode=True))
    return str(ruta)


def _entrada_completa(**overrides):
    base = {
        "id": "x1.1",
        "tarea": "X1",
        "titulo": "Titulo de prueba",
        "depende_de": [],
        "alcance": "api/**",
        "seguridad": False,
        "criterios": ["Criterio A"],
        "pruebas_borde": ["Borde A"],
    }
    base.update(overrides)
    return base


class TestValidarCampos:
    def test_entrada_completa_ok(self, tmp_path):
        ruta = _escribir_plan(tmp_path, [_entrada_completa()])
        assert plan_mod.validar(ruta) == 0

    def test_campo_faltante(self):
        entradas = [{"id": "a1", "tarea": "A"}]
        errores = plan_mod.validar_campos(entradas)
        assert len(errores) == 1
        assert "campos faltantes" in errores[0]

    def test_por_partir_no_exige_criterios(self):
        e = {
            "id": "c1", "tarea": "C1", "titulo": "T",
            "depende_de": [], "alcance": "api/**",
            "seguridad": False, "por_partir": True,
        }
        errores = plan_mod.validar_campos([e])
        assert errores == []

    def test_por_partir_sin_campo_basico_falla(self):
        e = {"id": "c1", "por_partir": True}
        errores = plan_mod.validar_campos([e])
        assert len(errores) == 1


class TestIdsUnicos:
    def test_ids_unicos(self):
        entradas = [_entrada_completa(id="a1"), _entrada_completa(id="a2")]
        assert plan_mod.validar_ids_unicos(entradas) == []

    def test_id_duplicado(self):
        entradas = [_entrada_completa(id="a1"), _entrada_completa(id="a1")]
        errores = plan_mod.validar_ids_unicos(entradas)
        assert len(errores) == 1
        assert "duplicado" in errores[0].lower()


class TestDependencias:
    def test_dependencia_existente(self):
        entradas = [
            _entrada_completa(id="a1"),
            _entrada_completa(id="a2", depende_de=["a1"]),
        ]
        assert plan_mod.validar_dependencias(entradas) == []

    def test_dependencia_inexistente(self):
        entradas = [_entrada_completa(id="a1", depende_de=["fantasma"])]
        errores = plan_mod.validar_dependencias(entradas)
        assert len(errores) == 1
        assert "fantasma" in errores[0]

    def test_depende_de_no_es_lista(self):
        entradas = [_entrada_completa(id="a1", depende_de="a2")]
        errores = plan_mod.validar_dependencias(entradas)
        assert len(errores) == 1


class TestCiclos:
    def test_sin_ciclos(self):
        entradas = [
            _entrada_completa(id="a1", depende_de=[]),
            _entrada_completa(id="a2", depende_de=["a1"]),
            _entrada_completa(id="a3", depende_de=["a2"]),
        ]
        assert plan_mod.detectar_ciclos(entradas) == []

    def test_ciclo_directo(self):
        entradas = [
            _entrada_completa(id="a1", depende_de=["a2"]),
            _entrada_completa(id="a2", depende_de=["a1"]),
        ]
        ciclos = plan_mod.detectar_ciclos(entradas)
        assert len(ciclos) >= 1
        assert "Ciclo" in ciclos[0]

    def test_ciclo_transitivo(self):
        entradas = [
            _entrada_completa(id="a1", depende_de=["a3"]),
            _entrada_completa(id="a2", depende_de=["a1"]),
            _entrada_completa(id="a3", depende_de=["a2"]),
        ]
        ciclos = plan_mod.detectar_ciclos(entradas)
        assert len(ciclos) >= 1


class TestValidarIntegral:
    def test_plan_vacio(self, tmp_path):
        ruta = _escribir_plan(tmp_path, [])
        assert plan_mod.validar(ruta) == 1

    def test_plan_valido_muestra_resumen(self, tmp_path, capsys):
        entradas = [
            _entrada_completa(id="a1"),
            _entrada_completa(id="a2", depende_de=["a1"]),
        ]
        ruta = _escribir_plan(tmp_path, entradas)
        assert plan_mod.validar(ruta) == 0
        salida = capsys.readouterr().out
        assert "2 entradas" in salida

    def test_main_con_argumento(self, tmp_path):
        ruta = _escribir_plan(tmp_path, [_entrada_completa()])
        assert plan_mod.main(["validar", "--plan", str(ruta)]) == 0


class TestPlanReal:
    def test_plan_yaml_del_repo_es_valido(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta = os.path.join(root, "tareas", "plan.yaml")
        if not os.path.exists(ruta):
            pytest.skip("plan.yaml no existe todavia")
        assert plan_mod.validar(ruta) == 0

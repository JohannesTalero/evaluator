"""Tests for scripts/issues.py — issue creation from plan.yaml."""
import os
import sys

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import issues as issues_mod


def _escribir_plan(tmp_path, entradas):
    ruta = tmp_path / "plan.yaml"
    ruta.write_text(yaml.dump(entradas, allow_unicode=True))
    return str(ruta)


def _entrada(**overrides):
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


class TestFormatearIssue:
    def test_titulo_incluye_id(self):
        titulo, _, _ = issues_mod.formatear_issue(_entrada(id="d1.2"))
        assert "[d1.2]" in titulo

    def test_cuerpo_incluye_alcance(self):
        _, cuerpo, _ = issues_mod.formatear_issue(_entrada(alcance="front/src/**"))
        assert "front/src/**" in cuerpo

    def test_seguridad_true_agrega_etiqueta(self):
        _, _, etiquetas = issues_mod.formatear_issue(_entrada(seguridad=True))
        assert "seguridad" in etiquetas

    def test_por_partir_agrega_etiqueta(self):
        _, _, etiquetas = issues_mod.formatear_issue(_entrada(por_partir=True))
        assert "por-partir" in etiquetas

    def test_sin_etiquetas_especiales(self):
        _, _, etiquetas = issues_mod.formatear_issue(_entrada())
        assert etiquetas == []

    def test_dependencias_en_cuerpo(self):
        _, cuerpo, _ = issues_mod.formatear_issue(
            _entrada(depende_de=["a1.1", "b1.2"])
        )
        assert "a1.1" in cuerpo
        assert "b1.2" in cuerpo

    def test_sin_dependencias(self):
        _, cuerpo, _ = issues_mod.formatear_issue(_entrada(depende_de=[]))
        assert "ninguna" in cuerpo


class TestSimular:
    def test_simular_imprime_todas(self, tmp_path, capsys):
        entradas = [_entrada(id="a1"), _entrada(id="a2")]
        ruta = _escribir_plan(tmp_path, entradas)
        issues_mod.simular(entradas)
        salida = capsys.readouterr().out
        assert "[a1]" in salida
        assert "[a2]" in salida
        assert "simulacion" in salida.lower()

    def test_main_simulacion_retorna_0(self, tmp_path):
        ruta = _escribir_plan(tmp_path, [_entrada()])
        assert issues_mod.main(["--plan", str(ruta)]) == 0

    def test_plan_vacio_retorna_1(self, tmp_path):
        ruta = _escribir_plan(tmp_path, [])
        assert issues_mod.main(["--plan", str(ruta)]) == 1

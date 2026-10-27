"""Tests for .claude/hooks/ scripts with simulated JSON inputs."""
import json
import os
import subprocess

import pytest

from conftest import GIT_ENV, _git

HOOKS_DIR = os.path.join(os.path.dirname(__file__), "..", ".claude", "hooks")


def _run_hook(hook_name, input_json, cwd, env=None):
    hook_path = os.path.join(HOOKS_DIR, hook_name)
    _env = {**(env or GIT_ENV)}
    result = subprocess.run(
        ["bash", hook_path],
        input=json.dumps(input_json),
        cwd=cwd, env=_env,
        capture_output=True, text=True,
    )
    return result


# --- guardia-tdd.sh ---

class TestGuardiaTDD:
    def test_permite_editar_test(self, repo_tmp):
        """Editing a test file is always allowed."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("guardia-tdd.sh", {
            "tool_input": {"file_path": "api/tests/test_cursos.py"}
        }, repo_tmp)
        assert result.returncode == 0

    def test_bloquea_produccion_sin_test(self, repo_tmp):
        """Editing production code without any test in the diff should block."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("guardia-tdd.sh", {
            "tool_input": {"file_path": "api/routers/cursos.py"}
        }, repo_tmp)
        assert result.returncode == 2
        assert "test" in result.stderr.lower()

    def test_permite_produccion_con_test(self, repo_tmp):
        """Editing production code when a test exists in the diff should pass."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        (repo_tmp / "api").mkdir(exist_ok=True)
        (repo_tmp / "api" / "tests").mkdir(parents=True, exist_ok=True)
        (repo_tmp / "api" / "tests" / "test_cursos.py").write_text("def test_x(): pass\n")
        _git(repo_tmp, "add", ".")
        _git(repo_tmp, "commit", "-m", "add test")
        result = _run_hook("guardia-tdd.sh", {
            "tool_input": {"file_path": "api/routers/cursos.py"}
        }, repo_tmp)
        assert result.returncode == 0

    def test_permite_en_main(self, repo_tmp):
        """On main, the guard does nothing."""
        result = _run_hook("guardia-tdd.sh", {
            "tool_input": {"file_path": "api/main.py"}
        }, repo_tmp)
        assert result.returncode == 0

    def test_permite_archivo_no_produccion(self, repo_tmp):
        """Files outside api/ and front/ are not checked."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("guardia-tdd.sh", {
            "tool_input": {"file_path": "docs/readme.md"}
        }, repo_tmp)
        assert result.returncode == 0


# --- guardia-soporte.sh ---

class TestGuardiaSoporte:
    def test_bloquea_fuera_de_rama_soporte(self, repo_tmp):
        """Editing support files outside soporte-* branch should block."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("guardia-soporte.sh", {
            "tool_input": {"file_path": "AGENTS.md"}
        }, repo_tmp)
        assert result.returncode == 2
        assert "soporte" in result.stderr.lower()

    def test_permite_en_rama_soporte(self, repo_tmp):
        """Editing support files in a soporte-* branch should pass."""
        _git(repo_tmp, "checkout", "-b", "soporte-1-comandos")
        result = _run_hook("guardia-soporte.sh", {
            "tool_input": {"file_path": "AGENTS.md"}
        }, repo_tmp)
        assert result.returncode == 0

    def test_permite_archivo_no_soporte(self, repo_tmp):
        """Editing non-support files in any branch should pass."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("guardia-soporte.sh", {
            "tool_input": {"file_path": "api/main.py"}
        }, repo_tmp)
        assert result.returncode == 0

    def test_bloquea_claude_settings(self, repo_tmp):
        """Editing .claude/ files outside soporte-* should block."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("guardia-soporte.sh", {
            "tool_input": {"file_path": ".claude/settings.json"}
        }, repo_tmp)
        assert result.returncode == 2

    def test_bloquea_scripts(self, repo_tmp):
        """Editing scripts/ outside soporte-* should block."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("guardia-soporte.sh", {
            "tool_input": {"file_path": "scripts/check.sh"}
        }, repo_tmp)
        assert result.returncode == 2


# --- check-al-terminar.sh ---

class TestCheckAlTerminar:
    def test_permite_con_stop_hook_active(self, repo_tmp):
        """When stop_hook_active is true, should exit immediately."""
        _git(repo_tmp, "checkout", "-b", "b3.1-cursos")
        result = _run_hook("check-al-terminar.sh", {
            "stop_hook_active": True
        }, repo_tmp)
        assert result.returncode == 0

    def test_permite_en_main(self, repo_tmp):
        """On main, skip the check."""
        result = _run_hook("check-al-terminar.sh", {
            "stop_hook_active": False
        }, repo_tmp)
        assert result.returncode == 0

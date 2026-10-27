import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "ci"))

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@test.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@test.com",
}


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, env=GIT_ENV,
        capture_output=True, text=True, check=True,
    )


@pytest.fixture
def repo_tmp(tmp_path):
    """A temp git repo on main with one initial commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    (repo / "README.md").write_text("# Test\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")
    return repo

"""Tests for golden set loader."""
import json
from pathlib import Path
import pytest
from evals.loader import load_golden_set
from evals.schema import GoldenSet

MANIFEST = {
    "version": "1.0", "exam_name": "Parcial 1", "exam_pages": ["enunciado.pdf"],
    "rubric": {"scale_max": 5.0, "criteria": [
        {"id": "q1", "question_ref": "1", "description": "Resolver", "max_score": 1.0, "type": "clave"},
    ]},
    "students": [
        {"code": "EST001", "pages": ["e1.jpg"], "grades": [{"criterion_id": "q1", "score": 0.8}]},
        {"code": "EST002", "pages": ["e2.jpg"], "grades": [{"criterion_id": "q1", "score": 0.0}]},
    ],
}


@pytest.fixture()
def sample_dir(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
    for name in ["enunciado.pdf", "e1.jpg", "e2.jpg"]:
        (tmp_path / name).write_bytes(b"fake")
    return tmp_path


def test_load(sample_dir):
    gs = load_golden_set(sample_dir)
    assert isinstance(gs, GoldenSet) and len(gs.students) == 2


def test_missing_manifest(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_golden_set(tmp_path)


def test_missing_file(sample_dir):
    (sample_dir / "e1.jpg").unlink()
    with pytest.raises(FileNotFoundError, match="e1.jpg"):
        load_golden_set(sample_dir)


def test_corrupt_manifest(tmp_path):
    (tmp_path / "manifest.json").write_text("bad", encoding="utf-8")
    with pytest.raises((json.JSONDecodeError, ValueError)):
        load_golden_set(tmp_path)


def test_blank_response(sample_dir):
    gs = load_golden_set(sample_dir)
    blank = [s for s in gs.students if s.code == "EST002"]
    assert blank[0].grades[0].score == 0.0

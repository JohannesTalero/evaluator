"""Tests for the golden set schema."""
import pytest
from evals.schema import Criterion, GoldenSet, Rubric, StudentExam, StudentGrade

C_KWARGS = dict(id="q1", question_ref="1", description="Resolver sistema", max_score=1.0, type="rubrica")


def _golden(**patch):
    base = {
        "version": "1.0", "exam_name": "Parcial 1", "exam_pages": ["e.pdf"],
        "rubric": {"scale_max": 5.0, "criteria": [dict(C_KWARGS)]},
        "students": [{"code": "EST001", "pages": ["p1.jpg"],
                       "grades": [{"criterion_id": "q1", "score": 0.8}]}],
    }
    base.update(patch)
    return base


class TestCriterion:
    def test_valid(self):
        assert Criterion(**C_KWARGS).max_score == 1.0

    def test_negative_score(self):
        with pytest.raises(ValueError):
            Criterion(**{**C_KWARGS, "max_score": -1})

    def test_zero_score(self):
        with pytest.raises(ValueError):
            Criterion(**{**C_KWARGS, "max_score": 0})

    def test_empty_description(self):
        with pytest.raises((TypeError, ValueError)):
            Criterion(**{**C_KWARGS, "description": ""})


class TestRubric:
    def test_valid(self):
        assert Rubric(scale_max=5.0, criteria=[Criterion(**C_KWARGS)]).scale_max == 5.0

    def test_empty_criteria(self):
        with pytest.raises(ValueError):
            Rubric(scale_max=5.0, criteria=[])

    def test_negative_scale(self):
        with pytest.raises(ValueError):
            Rubric(scale_max=-1, criteria=[Criterion(**C_KWARGS)])

    def test_duplicate_ids(self):
        c = Criterion(**C_KWARGS)
        with pytest.raises(ValueError):
            Rubric(scale_max=5.0, criteria=[c, c])


class TestStudentGrade:
    def test_valid(self):
        assert StudentGrade(criterion_id="q1", score=0.8).score == 0.8

    def test_negative(self):
        with pytest.raises(ValueError):
            StudentGrade(criterion_id="q1", score=-0.1)


class TestStudentExam:
    def test_valid(self):
        s = StudentExam(code="E1", pages=["p.jpg"], grades=[StudentGrade("q1", 0.8)])
        assert s.code == "E1"

    def test_no_pages(self):
        with pytest.raises(ValueError):
            StudentExam(code="E1", pages=[], grades=[StudentGrade("q1", 0.8)])

    def test_blank_response(self):
        s = StudentExam(code="E2", pages=["b.jpg"], grades=[StudentGrade("q1", 0.0)])
        assert s.grades[0].score == 0.0


class TestGoldenSet:
    def test_from_dict(self):
        gs = GoldenSet.from_dict(_golden())
        assert gs.exam_name == "Parcial 1"
        assert len(gs.students) == 1

    def test_score_exceeds_max(self):
        d = _golden()
        d["students"][0]["grades"][0]["score"] = 999
        with pytest.raises(ValueError, match="max"):
            GoldenSet.from_dict(d)

    def test_unknown_criterion(self):
        d = _golden()
        d["students"][0]["grades"][0]["criterion_id"] = "nope"
        with pytest.raises(ValueError, match="criterion"):
            GoldenSet.from_dict(d)

    def test_missing_grade(self):
        d = _golden()
        d["rubric"]["criteria"].append({**C_KWARGS, "id": "q2", "question_ref": "2"})
        with pytest.raises(ValueError, match="missing"):
            GoldenSet.from_dict(d)

    def test_crossouts_metadata(self):
        d = _golden()
        d["students"][0]["metadata"] = {"has_crossouts": True}
        gs = GoldenSet.from_dict(d)
        assert gs.students[0].metadata["has_crossouts"]

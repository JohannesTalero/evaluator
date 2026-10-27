"""Golden set schema — data models for the evaluation reference set."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Criterion:
    id: str
    question_ref: str
    description: str
    max_score: float
    type: str

    def __post_init__(self):
        if not self.description:
            raise ValueError("description must not be empty")
        if self.max_score <= 0:
            raise ValueError("max_score must be positive")


@dataclass(frozen=True)
class Rubric:
    scale_max: float
    criteria: list[Criterion]

    def __post_init__(self):
        if self.scale_max <= 0:
            raise ValueError("scale_max must be positive")
        if not self.criteria:
            raise ValueError("criteria must not be empty")
        ids = [c.id for c in self.criteria]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate criterion ids")


@dataclass(frozen=True)
class StudentGrade:
    criterion_id: str
    score: float

    def __post_init__(self):
        if self.score < 0:
            raise ValueError("score must not be negative")


@dataclass(frozen=True)
class StudentExam:
    code: str
    pages: list[str]
    grades: list[StudentGrade]
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.pages:
            raise ValueError("pages must not be empty")


@dataclass
class GoldenSet:
    version: str
    exam_name: str
    exam_pages: list[str]
    rubric: Rubric
    students: list[StudentExam]

    @classmethod
    def from_dict(cls, data: dict) -> GoldenSet:
        criteria = [Criterion(**c) for c in data["rubric"]["criteria"]]
        rubric = Rubric(scale_max=data["rubric"]["scale_max"], criteria=criteria)
        criterion_map = {c.id: c for c in criteria}
        students = []
        for s in data["students"]:
            grades = [StudentGrade(**g) for g in s["grades"]]
            student = StudentExam(
                code=s["code"], pages=s["pages"], grades=grades,
                metadata=s.get("metadata", {}),
            )
            grade_ids = {g.criterion_id for g in grades}
            for g in grades:
                if g.criterion_id not in criterion_map:
                    raise ValueError(f"unknown criterion '{g.criterion_id}'")
                if g.score > criterion_map[g.criterion_id].max_score:
                    raise ValueError(
                        f"score {g.score} exceeds max "
                        f"{criterion_map[g.criterion_id].max_score}"
                    )
            missing = set(criterion_map) - grade_ids
            if missing:
                raise ValueError(f"{student.code} missing grades: {missing}")
            students.append(student)
        return cls(
            version=data["version"], exam_name=data["exam_name"],
            exam_pages=data["exam_pages"], rubric=rubric, students=students,
        )

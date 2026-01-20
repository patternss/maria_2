from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class PracticeQuestion(BaseModel):
    """A stored practice question in the question bank."""

    id: str
    concept_id: str

    question_text: str
    model_answer: str
    rubric: str = Field(description="Short grading criteria")

    created_at: datetime
    updated_at: datetime


class ConceptProgress(BaseModel):
    """Per-concept progress tracking (MVP single user)."""

    concept_id: str

    mastery_streak: int = 0
    last_correct_at: datetime | None = None
    next_due_at: datetime | None = None

    last_attempt_score: float | None = Field(
        default=None,
        description="Last attempt score percentage (0-100). Used for weighting.",
    )


class PracticeAttempt(BaseModel):
    """Record of a single submitted answer."""

    id: str
    concept_id: str
    question_id: str

    user_answer: str
    score: float = Field(description="0-100")
    feedback: str

    created_at: datetime


class QuestionReport(BaseModel):
    """User report about a potentially poor question."""

    id: str
    question_id: str
    reason: str | None = None
    created_at: datetime

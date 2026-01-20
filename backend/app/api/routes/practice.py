from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps.llm import get_ollama_client
from app.api.deps.practice_repos import (
    get_attempts_repo,
    get_concepts_repo,
    get_progress_repo,
    get_question_bank_repo,
)
from app.core.settings import get_settings
from app.domain.practice.models import ConceptProgress, PracticeAttempt, PracticeQuestion
from app.domain.practice.scheduling import utc_now
from app.domain.practice.service import NoConceptsDue, PracticeService
from app.infra.llm.ollama_client import OllamaClient, OllamaUnavailable
from app.infra.repositories.attempts_repository import AttemptsRepository
from app.infra.repositories.concepts_repository import ConceptsRepository
from app.infra.repositories.progress_repository import ProgressRepository
from app.infra.repositories.question_bank_repository import QuestionBankRepository

router = APIRouter(prefix="/practice", tags=["practice"])


class PracticeGenerateResponse(BaseModel):
    concept_id: str
    question: PracticeQuestion


@router.post("/generate", response_model=PracticeGenerateResponse)
def generate(
    concepts_repo: ConceptsRepository = Depends(get_concepts_repo),
    progress_repo: ProgressRepository = Depends(get_progress_repo),
    bank_repo: QuestionBankRepository = Depends(get_question_bank_repo),
    attempts_repo: AttemptsRepository = Depends(get_attempts_repo),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> PracticeGenerateResponse:
    """Generate a single practice question.

    Notes:
        - Blocks if AI is unavailable.
        - Blocks if no concepts are due.
        - Recent tags are currently not tracked in persistence; MVP uses empty set.
    """

    settings = get_settings()
    now = utc_now()

    recent_tags: set[str] = set()
    for attempt in attempts_repo.list_recent(limit=3):
        concept = concepts_repo.get_concept(attempt.concept_id)
        if concept is not None:
            recent_tags.update(concept.tags)

    service = PracticeService(
        concepts_repo=concepts_repo,
        progress_repo=progress_repo,
        bank_repo=bank_repo,
        attempts_repo=attempts_repo,
        ollama=ollama,
        generation_model=settings.ollama_generation_model,
        evaluator_model=settings.ollama_evaluator_model,
        now=now,
    )

    try:
        result = service.generate_one(recent_tags=recent_tags)
    except NoConceptsDue as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "no_concepts_due", "message": str(exc)}},
        ) from exc
    except OllamaUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "ai_unavailable", "message": str(exc)}},
        ) from exc

    return PracticeGenerateResponse(concept_id=result.concept.id, question=result.question)


class PracticeSubmitRequest(BaseModel):
    concept_id: str
    question_id: str
    user_answer: str = Field(min_length=1)


class PracticeSubmitResponse(BaseModel):
    attempt: PracticeAttempt
    progress: ConceptProgress


@router.post("/submit", response_model=PracticeSubmitResponse)
def submit(
    payload: PracticeSubmitRequest,
    concepts_repo: ConceptsRepository = Depends(get_concepts_repo),
    progress_repo: ProgressRepository = Depends(get_progress_repo),
    bank_repo: QuestionBankRepository = Depends(get_question_bank_repo),
    attempts_repo: AttemptsRepository = Depends(get_attempts_repo),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> PracticeSubmitResponse:
    """Submit an answer for grading and update progress."""

    settings = get_settings()
    now = utc_now()

    service = PracticeService(
        concepts_repo=concepts_repo,
        progress_repo=progress_repo,
        bank_repo=bank_repo,
        attempts_repo=attempts_repo,
        ollama=ollama,
        generation_model=settings.ollama_generation_model,
        evaluator_model=settings.ollama_evaluator_model,
        now=now,
    )

    try:
        result = service.submit(
            concept_id=payload.concept_id,
            question_id=payload.question_id,
            user_answer=payload.user_answer,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": str(exc)}},
        ) from exc
    except OllamaUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "ai_unavailable", "message": str(exc)}},
        ) from exc

    return PracticeSubmitResponse(attempt=result.attempt, progress=result.progress)

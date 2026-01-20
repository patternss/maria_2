from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps.llm import get_ollama_client
from app.api.deps.practice_repos import get_concepts_repo, get_question_bank_repo, get_question_reports_repo
from app.core.settings import get_settings
from app.domain.practice.prompts import evaluator_prompt, generation_prompt
from app.domain.practice.scheduling import utc_now
from app.infra.llm.ollama_client import OllamaClient, OllamaUnavailable
from app.infra.repositories.concepts_repository import ConceptsRepository
from app.infra.repositories.question_bank_repository import QuestionBankRepository
from app.infra.repositories.question_reports_repository import QuestionReportsRepository

router = APIRouter(prefix="/questions", tags=["questions"])


class ReportRequest(BaseModel):
    reason: str | None = None


class ReportResponse(BaseModel):
    removed: bool


@router.post("/{question_id}/report", response_model=ReportResponse)
def report_question(
    question_id: str,
    payload: ReportRequest,
    concepts_repo: ConceptsRepository = Depends(get_concepts_repo),
    bank_repo: QuestionBankRepository = Depends(get_question_bank_repo),
    reports_repo: QuestionReportsRepository = Depends(get_question_reports_repo),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> ReportResponse:
    """Report a question as poor.

    Behavior:
        - Always stores the report event.
        - Re-evaluates the question via evaluator model.
        - If evaluator confirms poor (pass=false): remove and return removed=true.
    """

    settings = get_settings()
    now = utc_now()

    reports_repo.append_report(question_id=question_id, reason=payload.reason, now=now)

    question = bank_repo.get_question(question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "question_not_found", "message": "Question not found"}},
        )

    concept = concepts_repo.get_concept(question.concept_id)
    if concept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "concept_not_found", "message": "Concept not found"}},
        )

    candidate = {
        "question_text": question.question_text,
        "model_answer": question.model_answer,
        "rubric": question.rubric,
    }

    try:
        verdict = ollama.generate_json(
            model=settings.ollama_evaluator_model,
            prompt=evaluator_prompt(concept=concept, candidate=candidate),
        )
    except OllamaUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "ai_unavailable", "message": str(exc)}},
        ) from exc

    if bool(verdict.get("pass")):
        return ReportResponse(removed=False)

    removed = bank_repo.remove_question(question_id)
    # Best-effort replacement generation to keep the bank size stable.
    try:
        candidate = ollama.generate_json(
            model=settings.ollama_generation_model,
            prompt=generation_prompt(concept=concept),
        )

        for _ in range(3):
            replacement_verdict = ollama.generate_json(
                model=settings.ollama_evaluator_model,
                prompt=evaluator_prompt(concept=concept, candidate=candidate),
            )
            if bool(replacement_verdict.get("pass")):
                break
            candidate = ollama.generate_json(
                model=settings.ollama_generation_model,
                prompt=generation_prompt(concept=concept),
            )

        if bool(replacement_verdict.get("pass")):
            bank_repo.upsert_question(
                concept_id=concept.id,
                question_text=str(candidate.get("question_text", "")).strip(),
                model_answer=str(candidate.get("model_answer", "")).strip(),
                rubric=str(candidate.get("rubric", "")).strip(),
                now=now,
            )
    except OllamaUnavailable:
        # AI is required for practice, but reporting should still be able to
        # remove known-bad questions even if replacement generation is down.
        pass

    return ReportResponse(removed=removed)

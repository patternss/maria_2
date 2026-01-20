from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

from app.domain.concepts import Concept
from app.domain.practice.models import ConceptProgress, PracticeAttempt, PracticeQuestion
from app.domain.practice.prompts import evaluator_prompt, generation_prompt, grading_prompt
from app.domain.practice.scheduling import compute_cooldown_minutes, compute_next_due_at, update_mastery_streak
from app.domain.practice.selection import pick_due_concept
from app.infra.llm.ollama_client import OllamaClient, OllamaUnavailable
from app.infra.repositories.attempts_repository import AttemptsRepository
from app.infra.repositories.concepts_repository import ConceptsRepository
from app.infra.repositories.progress_repository import ProgressRepository
from app.infra.repositories.question_bank_repository import QuestionBankRepository


class NoConceptsDue(RuntimeError):
    """Raised when practice generation is requested but no concepts are due."""


@dataclass(frozen=True)
class GenerateResult:
    concept: Concept
    question: PracticeQuestion


@dataclass(frozen=True)
class SubmitResult:
    attempt: PracticeAttempt
    progress: ConceptProgress


class PracticeService:
    """Orchestrates practice generation and submission.

    This service coordinates:
        - selecting a due concept
        - selecting/generating a question
        - grading an answer
        - updating progress and persisting attempts

    The service is designed to be called from HTTP endpoints.
    """

    def __init__(
        self,
        *,
        concepts_repo: ConceptsRepository,
        progress_repo: ProgressRepository,
        bank_repo: QuestionBankRepository,
        attempts_repo: AttemptsRepository,
        ollama: OllamaClient,
        generation_model: str,
        evaluator_model: str,
        now: datetime,
        rng: random.Random | None = None,
    ) -> None:
        self._concepts_repo = concepts_repo
        self._progress_repo = progress_repo
        self._bank_repo = bank_repo
        self._attempts_repo = attempts_repo
        self._ollama = ollama
        self._generation_model = generation_model
        self._evaluator_model = evaluator_model
        self._now = now
        self._rng = rng or random.Random()

    def generate_one(self, *, recent_tags: set[str]) -> GenerateResult:
        """Generate or pick a single practice question.

        Raises:
            NoConceptsDue if no concepts are due.
            OllamaUnavailable if AI is down.
        """

        concepts = self._concepts_repo.list_concepts()
        progress_by = self._progress_repo.get_all()

        selection = pick_due_concept(
            concepts=concepts,
            progress_by_concept_id=progress_by,
            recent_tags=recent_tags,
            now=self._now,
            rng=self._rng,
        )

        if selection is None:
            raise NoConceptsDue("No concepts are due")

        concept = self._concepts_repo.get_concept(selection.concept_id)
        if concept is None:
            raise RuntimeError("Selected concept missing")

        p_new, questions = self._bank_repo.get_bank(concept.id)

        should_generate = False
        if len(questions) == 0:
            should_generate = True
        elif len(questions) >= 10:
            should_generate = False
        else:
            should_generate = self._rng.random() < p_new

        if not should_generate:
            question = self._rng.choice(questions)
            return GenerateResult(concept=concept, question=question)

        candidate = self._ollama.generate_json(model=self._generation_model, prompt=generation_prompt(concept=concept))

        # Evaluate candidate (regenerate on failure, capped).
        for _ in range(3):
            verdict = self._ollama.generate_json(
                model=self._evaluator_model, prompt=evaluator_prompt(concept=concept, candidate=candidate)
            )
            if bool(verdict.get("pass")):
                break
            candidate = self._ollama.generate_json(model=self._generation_model, prompt=generation_prompt(concept=concept))
        else:
            raise OllamaUnavailable("Evaluator rejected generated question repeatedly")

        question = self._bank_repo.upsert_question(
            concept_id=concept.id,
            question_text=str(candidate.get("question_text", "")).strip(),
            model_answer=str(candidate.get("model_answer", "")).strip(),
            rubric=str(candidate.get("rubric", "")).strip(),
            now=self._now,
        )

        return GenerateResult(concept=concept, question=question)

    def submit(self, *, concept_id: str, question_id: str, user_answer: str) -> SubmitResult:
        """Grade an answer and update progress.

        Raises:
            OllamaUnavailable if AI is down.
            ValueError if question is unknown.
        """

        concept = self._concepts_repo.get_concept(concept_id)
        if concept is None:
            raise ValueError("Concept not found")

        question = self._bank_repo.get_question(question_id)
        if question is None:
            raise ValueError("Question not found")

        result = self._ollama.generate_json(
            model=self._generation_model,
            prompt=grading_prompt(concept=concept, question=question, user_answer=user_answer),
        )

        score = float(result.get("score", 0.0))
        feedback = str(result.get("feedback", "")).strip()

        attempt = self._attempts_repo.append_attempt(
            concept_id=concept_id,
            question_id=question_id,
            user_answer=user_answer,
            score=score,
            feedback=feedback,
            now=self._now,
        )

        progress = self._progress_repo.get(concept_id) or ConceptProgress(concept_id=concept_id)
        progress.last_attempt_score = score

        mastery_update = update_mastery_streak(progress.mastery_streak, score)
        progress.mastery_streak = mastery_update.mastery_streak

        if score >= 85.0:
            progress.last_correct_at = self._now

        cooldown_minutes = compute_cooldown_minutes(progress.mastery_streak)
        next_due = compute_next_due_at(now=self._now, score=score, cooldown_minutes=cooldown_minutes)
        if next_due is not None:
            progress.next_due_at = next_due

        self._progress_repo.upsert(progress)

        return SubmitResult(attempt=attempt, progress=progress)

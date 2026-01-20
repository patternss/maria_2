from __future__ import annotations

import json

from app.domain.concepts import Concept
from app.domain.practice.models import PracticeQuestion


def _json_schema_block(schema: dict) -> str:
    return json.dumps(schema, indent=2)


def generation_prompt(*, concept: Concept) -> str:
    """Prompt for generating a new question + model answer + rubric.

    Output must be strict JSON.
    """

    schema = {
        "question_text": "string",
        "model_answer": "string",
        "rubric": "string",
    }

    return (
        "You are a learning assistant that creates ONE short-answer practice question.\n"
        "Return ONLY valid JSON matching this schema (no markdown, no extra keys):\n"
        f"{_json_schema_block(schema)}\n\n"
        f"Concept title: {concept.title}\n"
        f"Concept description: {concept.description or ''}\n"
        f"Concept tags: {', '.join(concept.tags) if concept.tags else ''}\n"
    )


def evaluator_prompt(*, concept: Concept, candidate: dict) -> str:
    """Prompt for evaluating a candidate question object.

    Output must be strict JSON.
    """

    schema = {
        "pass": "boolean",
        "reason": "string",
    }

    return (
        "You are an evaluator model for practice questions.\n"
        "Judge if the candidate question is appropriate for the concept.\n"
        "Return ONLY valid JSON matching this schema (no markdown, no extra keys):\n"
        f"{_json_schema_block(schema)}\n\n"
        f"Concept title: {concept.title}\n"
        f"Concept description: {concept.description or ''}\n"
        f"Concept tags: {', '.join(concept.tags) if concept.tags else ''}\n\n"
        f"Candidate: {json.dumps(candidate)}\n"
        "Evaluation rules: relevant, clear, not ambiguous, includes plausible model_answer and rubric."
    )


def grading_prompt(*, concept: Concept, question: PracticeQuestion, user_answer: str) -> str:
    """Prompt for grading a user answer.

    Output must be strict JSON.
    """

    schema = {
        "score": "number (0-100)",
        "feedback": "string",
    }

    return (
        "You are a strict but helpful grader.\n"
        "Grade the user's answer from 0 to 100.\n"
        "Return ONLY valid JSON matching this schema (no markdown, no extra keys):\n"
        f"{_json_schema_block(schema)}\n\n"
        f"Concept title: {concept.title}\n"
        f"Question: {question.question_text}\n"
        f"Model answer: {question.model_answer}\n"
        f"Rubric/criteria: {question.rubric}\n"
        f"User answer: {user_answer}\n"
    )

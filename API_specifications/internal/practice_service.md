# Practice service (internal)

Code: backend/app/domain/practice/service.py

## Purpose
- Orchestrates practice generation and submission.
- Coordinates selection, question bank, Ollama grading, and persistence updates.

## Public API
- `PracticeService.generate_one(recent_tags: set[str]) -> GenerateResult`
  - Raises `NoConceptsDue` when no concepts are due.
  - Raises `OllamaUnavailable` when AI is down or returns invalid JSON.
- `PracticeService.submit(concept_id: str, question_id: str, user_answer: str) -> SubmitResult`
  - Raises `ValueError` for unknown concept/question.
  - Raises `OllamaUnavailable` when AI is down.

## Invariants
- Hard cooldown is enforced at selection time (only due concepts are eligible).
- Question bank cap is 10 per concept.
- New questions are evaluator-gated; capped regeneration attempts.

## Side effects
- Writes YAML via repositories (progress, bank, attempts, reports).
- Network calls to Ollama.

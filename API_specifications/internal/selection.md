# Concept selection (internal)

Code: backend/app/domain/practice/selection.py

## Purpose
- Implements the weighted due-concept selection rules from the spec.

## Public API
- `pick_due_concept(...) -> SelectionResult | None`
- `compute_concept_weight(...) -> float`
- `is_due(progress: ConceptProgress | None, now: datetime) -> bool`

## Invariants
- Hard cooldown: concepts with `next_due_at > now` are excluded.
- Only positive weights are eligible for random choice.

## Notes
- Weight knobs are in `compute_concept_weight` and should stay centralized to avoid drift.

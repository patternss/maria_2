# Scheduling & mastery (internal)

Code: backend/app/domain/practice/scheduling.py

## Purpose
- Implements mastery updates and cooldown calculation per the MVP spec.

## Public API
- `update_mastery_streak(current: int, score: float) -> MasteryUpdateResult`
- `compute_cooldown_minutes(mastery_streak: int) -> float`
- `compute_next_due_at(now: datetime, score: float, cooldown_minutes: float) -> datetime | None`

## Rules summary
- Correct: score ≥ 85% → increases mastery and sets `next_due_at = now + cooldown`.
- Poor: score < 50% → sets `next_due_at = now + 10 minutes`.
- OK: 50–85% → leaves `next_due_at` unchanged.

## Notes
- `utc_now()` is centralized to keep time mocking easy.

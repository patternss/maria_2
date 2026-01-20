from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class MasteryUpdateResult:
    """Result of applying mastery rules for one submission."""

    mastery_streak: int


def compute_cooldown_minutes(mastery_streak: int) -> float:
    """Compute cooldown length in minutes based on mastery.

    Inputs:
        mastery_streak: Non-negative integer.

    Outputs:
        Cooldown length in minutes.

    Rules (from spec):
        - Base: 1440 minutes
        - Multipliers:
            - levels 1–5: *1.3 per increment
            - levels 6+: *3.0 per increment

    Notes:
        This function assumes mastery_streak has already been updated.
    """

    if mastery_streak <= 0:
        return 0.0

    base = 1440.0
    slow_exponent = min(mastery_streak - 1, 4)
    fast_exponent = max(mastery_streak - 5, 0)

    return base * (1.3**slow_exponent) * (3.0**fast_exponent)


def update_mastery_streak(current: int, score: float) -> MasteryUpdateResult:
    """Update mastery streak according to spec.

    Inputs:
        current: Current mastery streak (>=0)
        score: Percentage score 0..100

    Outputs:
        Updated mastery streak.

    Rules:
        - If score >= 85: +1
        - If score in [50, 85) and current >= 3: -1
        - If score < 50 and current >= 3: -3
        - If current < 3 and score < 85: reset to 0
    """

    current = max(0, int(current))

    if score >= 85.0:
        return MasteryUpdateResult(mastery_streak=current + 1)

    if current < 3:
        return MasteryUpdateResult(mastery_streak=0)

    if score < 50.0:
        return MasteryUpdateResult(mastery_streak=max(0, current - 3))

    return MasteryUpdateResult(mastery_streak=max(0, current - 1))


def utc_now() -> datetime:
    """Return current UTC time.

    Centralized clock helper to keep scheduling code testable.
    """

    return datetime.now(timezone.utc)


def compute_next_due_at(*, now: datetime, score: float, cooldown_minutes: float) -> datetime | None:
    """Compute next_due_at based on scoring rules.

    Rules:
        - score >= 85: now + cooldown
        - score < 50: now + 10 minutes
        - score in [50, 85): unchanged (represented as None here; caller may keep existing)
    """

    if score >= 85.0:
        return now + timedelta(minutes=cooldown_minutes)

    if score < 50.0:
        return now + timedelta(minutes=10)

    return None

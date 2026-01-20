from __future__ import annotations

from datetime import datetime, timezone

from app.domain.practice.scheduling import (
    compute_cooldown_minutes,
    compute_next_due_at,
    update_mastery_streak,
)


def test_update_mastery_streak_correct_increments() -> None:
    assert update_mastery_streak(0, 85).mastery_streak == 1
    assert update_mastery_streak(2, 90).mastery_streak == 3


def test_update_mastery_streak_ok_decrements_only_after_three() -> None:
    assert update_mastery_streak(0, 60).mastery_streak == 0
    assert update_mastery_streak(2, 60).mastery_streak == 0
    assert update_mastery_streak(3, 60).mastery_streak == 2
    assert update_mastery_streak(4, 84.999).mastery_streak == 3


def test_update_mastery_streak_poor_decrements_three_only_after_three() -> None:
    assert update_mastery_streak(0, 0).mastery_streak == 0
    assert update_mastery_streak(2, 49.9).mastery_streak == 0
    assert update_mastery_streak(3, 49.9).mastery_streak == 0
    assert update_mastery_streak(6, 10).mastery_streak == 3


def test_compute_cooldown_minutes_matches_spec() -> None:
    # mastery_streak <= 0 => no cooldown
    assert compute_cooldown_minutes(0) == 0.0

    # mastery_streak == 1 => base cooldown
    assert compute_cooldown_minutes(1) == 1440.0

    # mastery_streak == 2 => base * 1.3
    assert compute_cooldown_minutes(2) == 1440.0 * 1.3

    # mastery_streak == 5 => base * 1.3^(4)
    assert compute_cooldown_minutes(5) == 1440.0 * (1.3**4)

    # mastery_streak == 6 => base * 1.3^(4) * 3.0^(1)
    assert compute_cooldown_minutes(6) == 1440.0 * (1.3**4) * 3.0


def test_compute_next_due_at() -> None:
    now = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)

    # Correct
    due = compute_next_due_at(now=now, score=85.0, cooldown_minutes=60.0)
    assert due == datetime(2026, 1, 20, 13, 0, 0, tzinfo=timezone.utc)

    # Poor
    due = compute_next_due_at(now=now, score=0.0, cooldown_minutes=999.0)
    assert due == datetime(2026, 1, 20, 12, 10, 0, tzinfo=timezone.utc)

    # OK => unchanged (None)
    assert compute_next_due_at(now=now, score=60.0, cooldown_minutes=60.0) is None

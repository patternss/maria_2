from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

from app.domain.concepts import Concept
from app.domain.practice.models import ConceptProgress


@dataclass(frozen=True)
class SelectionResult:
    concept_id: str
    weight: float


def _clamp(min_value: float, max_value: float, value: float) -> float:
    return max(min_value, min(max_value, value))


def is_due(progress: ConceptProgress | None, *, now: datetime) -> bool:
    """Return True if a concept is due per hard cooldown rules."""

    if progress is None:
        return True
    if progress.next_due_at is None:
        return True
    return now >= progress.next_due_at


def compute_concept_weight(
    concept: Concept,
    progress: ConceptProgress | None,
    *,
    recent_tags: set[str],
    now: datetime,
) -> float:
    """Compute selection weight for a due concept.

    Matches the tunable defaults in the spec.
    """

    weight = 1.0

    concept_tags = {t for t in concept.tags if t}
    tag_overlap = len(concept_tags.intersection(recent_tags))
    weight *= 1.0 + tag_overlap * 0.5

    if progress is None or progress.last_correct_at is None:
        weight *= 1.5
    else:
        minutes_since = (now - progress.last_correct_at).total_seconds() / 60.0
        weight *= _clamp(1.0, 2.0, minutes_since / 1440.0)

    if progress is not None and progress.last_attempt_score is not None and progress.last_attempt_score < 50.0:
        weight *= 2.0

    mastery_streak = 0 if progress is None else progress.mastery_streak
    weight *= 1.0 / (1.0 + mastery_streak * 0.25)

    return max(0.0, weight)


def pick_due_concept(
    *,
    concepts: list[Concept],
    progress_by_concept_id: dict[str, ConceptProgress],
    recent_tags: set[str],
    now: datetime,
    rng: random.Random | None = None,
) -> SelectionResult | None:
    """Pick one due concept using weighted random selection.

    Returns:
        SelectionResult if at least one concept is due, else None.
    """

    rng = rng or random.Random()

    weighted: list[tuple[str, float]] = []

    for concept in concepts:
        progress = progress_by_concept_id.get(concept.id)
        if not is_due(progress, now=now):
            continue

        w = compute_concept_weight(concept, progress, recent_tags=recent_tags, now=now)
        if w > 0:
            weighted.append((concept.id, w))

    if not weighted:
        return None

    total = sum(w for _, w in weighted)
    roll = rng.random() * total

    upto = 0.0
    for concept_id, w in weighted:
        upto += w
        if upto >= roll:
            return SelectionResult(concept_id=concept_id, weight=w)

    concept_id, w = weighted[-1]
    return SelectionResult(concept_id=concept_id, weight=w)

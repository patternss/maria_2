from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.domain.concepts import Concept
from app.domain.practice.models import ConceptProgress
from app.domain.practice.selection import is_due, pick_due_concept


def _concept(*, concept_id: str, title: str, tags: list[str]) -> Concept:
    now = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
    return Concept(
        id=concept_id,
        title=title,
        description=None,
        tags=tags,
        source_url=None,
        created_at=now,
        updated_at=now,
    )


def test_is_due_default_true() -> None:
    now = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
    assert is_due(None, now=now) is True
    assert is_due(ConceptProgress(concept_id="c1"), now=now) is True


def test_is_due_respects_next_due_at() -> None:
    now = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
    future = now + timedelta(minutes=1)

    progress = ConceptProgress(concept_id="c1")
    progress.next_due_at = future

    assert is_due(progress, now=now) is False
    assert is_due(progress, now=future) is True


def test_pick_due_concept_excludes_cooled_down() -> None:
    now = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)

    concepts = [
        _concept(concept_id="due", title="Due", tags=["a"]),
        _concept(concept_id="cool", title="Cool", tags=["b"]),
    ]

    progress_due = ConceptProgress(concept_id="due")

    progress_cool = ConceptProgress(concept_id="cool")
    progress_cool.next_due_at = now + timedelta(days=1)

    rng = random.Random(123)
    result = pick_due_concept(
        concepts=concepts,
        progress_by_concept_id={"due": progress_due, "cool": progress_cool},
        recent_tags=set(),
        now=now,
        rng=rng,
    )

    assert result is not None
    assert result.concept_id == "due"


def test_pick_due_concept_returns_none_when_none_due() -> None:
    now = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)

    concepts = [_concept(concept_id="c1", title="C1", tags=["a"])]

    progress = ConceptProgress(concept_id="c1")
    progress.next_due_at = now + timedelta(minutes=1)

    result = pick_due_concept(
        concepts=concepts,
        progress_by_concept_id={"c1": progress},
        recent_tags=set(),
        now=now,
        rng=random.Random(1),
    )

    assert result is None

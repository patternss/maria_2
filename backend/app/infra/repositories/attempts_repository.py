from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.practice.models import PracticeAttempt
from app.infra.storage.yaml_store import YamlStore


class AttemptsRepository:
    """Repository for answer attempts.

    Storage:
        YAML file `attempts.yaml`.
    """

    _FILENAME = "attempts.yaml"

    def __init__(self, store: YamlStore) -> None:
        self._store = store

    def list_recent(self, *, limit: int = 3) -> list[PracticeAttempt]:
        """Return the most recent attempts (newest-last in storage order).

        Inputs:
            limit: Maximum number of attempts to return.

        Outputs:
            List of attempts in chronological order (oldest -> newest).

        Notes:
            MVP uses append-only storage, so YAML order reflects time order.
        """

        payload = self._store.read(self._FILENAME, default={"version": 1, "attempts": []})
        raw = payload.get("attempts", [])
        if not raw:
            return []

        models = [PracticeAttempt.model_validate(item) for item in raw]
        limit = max(0, int(limit))
        if limit == 0:
            return []

        return models[-limit:]

    def append_attempt(
        self,
        *,
        concept_id: str,
        question_id: str,
        user_answer: str,
        score: float,
        feedback: str,
        now: datetime | None = None,
    ) -> PracticeAttempt:
        now = now or datetime.now(timezone.utc)

        attempt = PracticeAttempt(
            id=str(uuid4()),
            concept_id=concept_id,
            question_id=question_id,
            user_answer=user_answer,
            score=score,
            feedback=feedback,
            created_at=now,
        )

        payload = self._store.read(self._FILENAME, default={"version": 1, "attempts": []})
        payload.setdefault("version", 1)
        payload.setdefault("attempts", [])
        payload["attempts"].append(attempt.model_dump(mode="json"))

        self._store.write_atomic(self._FILENAME, payload)
        return attempt

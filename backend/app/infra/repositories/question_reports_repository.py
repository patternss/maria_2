from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.practice.models import QuestionReport
from app.infra.storage.yaml_store import YamlStore


class QuestionReportsRepository:
    """Repository for question reports.

    Storage:
        YAML file `question_reports.yaml`.
    """

    _FILENAME = "question_reports.yaml"

    def __init__(self, store: YamlStore) -> None:
        self._store = store

    def append_report(self, *, question_id: str, reason: str | None = None, now: datetime | None = None) -> QuestionReport:
        now = now or datetime.now(timezone.utc)

        report = QuestionReport(
            id=str(uuid4()),
            question_id=question_id,
            reason=reason,
            created_at=now,
        )

        payload = self._store.read(self._FILENAME, default={"version": 1, "reports": []})
        payload.setdefault("version", 1)
        payload.setdefault("reports", [])
        payload["reports"].append(report.model_dump(mode="json"))
        self._store.write_atomic(self._FILENAME, payload)

        return report

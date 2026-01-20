from __future__ import annotations

from datetime import datetime

from app.domain.practice.models import ConceptProgress
from app.infra.storage.yaml_store import YamlStore


class ProgressRepository:
    """Repository for per-concept progress.

    Storage:
        YAML file `progress.yaml`.
    """

    _FILENAME = "progress.yaml"

    def __init__(self, store: YamlStore) -> None:
        self._store = store

    def get_all(self) -> dict[str, ConceptProgress]:
        payload = self._store.read(self._FILENAME, default={"version": 1, "progress": []})
        items = payload.get("progress", [])
        out: dict[str, ConceptProgress] = {}
        for item in items:
            model = ConceptProgress.model_validate(item)
            out[model.concept_id] = model
        return out

    def get(self, concept_id: str) -> ConceptProgress | None:
        return self.get_all().get(concept_id)

    def upsert(self, progress: ConceptProgress) -> None:
        payload = self._store.read(self._FILENAME, default={"version": 1, "progress": []})
        payload.setdefault("version", 1)
        payload.setdefault("progress", [])

        updated: list[dict] = []
        replaced = False
        for item in payload["progress"]:
            if item.get("concept_id") == progress.concept_id:
                updated.append(progress.model_dump(mode="json"))
                replaced = True
            else:
                updated.append(item)

        if not replaced:
            updated.append(progress.model_dump(mode="json"))

        payload["progress"] = updated
        self._store.write_atomic(self._FILENAME, payload)

    def set_last_correct_at(self, concept_id: str, when: datetime) -> None:
        progress = self.get(concept_id) or ConceptProgress(concept_id=concept_id)
        progress.last_correct_at = when
        self.upsert(progress)

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.concepts import Concept, ConceptCreate
from app.infra.storage.yaml_store import YamlStore


class ConceptsRepository:
    """Repository for CRUD operations on concepts.

    Storage:
        YAML file `concepts.yaml` under the configured data directory.

    Notes:
        - This repository does not implement multi-user yet.
        - IDs are UUID4 strings.
    """

    _FILENAME = "concepts.yaml"

    def __init__(self, store: YamlStore) -> None:
        self._store = store

    def list_concepts(self) -> list[Concept]:
        """Return all concepts."""

        payload = self._store.read(self._FILENAME, default={"version": 1, "concepts": []})
        concepts = payload.get("concepts", [])
        return [Concept.model_validate(item) for item in concepts]

    def get_concept(self, concept_id: str) -> Concept | None:
        """Return a concept by ID, or None if missing."""

        for concept in self.list_concepts():
            if concept.id == concept_id:
                return concept
        return None

    def create_concept(self, concept: ConceptCreate) -> Concept:
        """Create and persist a new concept.

        Args:
            concept: Validated concept creation payload.

        Returns:
            Newly created persisted concept.
        """

        now = datetime.now(timezone.utc)

        new_concept = Concept(
            id=str(uuid4()),
            title=concept.title.strip(),
            description=concept.description,
            tags=[tag.strip() for tag in concept.tags if tag.strip()],
            source_url=concept.source_url,
            created_at=now,
            updated_at=now,
        )

        payload = self._store.read(self._FILENAME, default={"version": 1, "concepts": []})
        payload.setdefault("version", 1)
        payload.setdefault("concepts", [])
        payload["concepts"].append(new_concept.model_dump(mode="json"))

        self._store.write_atomic(self._FILENAME, payload)

        return new_concept

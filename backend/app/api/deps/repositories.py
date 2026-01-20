from __future__ import annotations

from functools import lru_cache

from app.core.settings import get_settings
from app.infra.repositories.concepts_repository import ConceptsRepository
from app.infra.storage.yaml_store import YamlStore


@lru_cache
def _store(data_dir: str) -> YamlStore:
    return YamlStore(data_dir)


def get_concepts_repository() -> ConceptsRepository:
    """FastAPI dependency for the concepts repository."""

    settings = get_settings()
    store = _store(settings.data_dir)
    return ConceptsRepository(store)

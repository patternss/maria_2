from __future__ import annotations

from functools import lru_cache

from app.core.settings import get_settings
from app.infra.repositories.attempts_repository import AttemptsRepository
from app.infra.repositories.concepts_repository import ConceptsRepository
from app.infra.repositories.progress_repository import ProgressRepository
from app.infra.repositories.question_bank_repository import QuestionBankRepository
from app.infra.repositories.question_reports_repository import QuestionReportsRepository
from app.infra.storage.yaml_store import YamlStore


@lru_cache
def _store(data_dir: str) -> YamlStore:
    return YamlStore(data_dir)


def get_store() -> YamlStore:
    settings = get_settings()
    return _store(settings.data_dir)


def get_concepts_repo() -> ConceptsRepository:
    return ConceptsRepository(get_store())


def get_progress_repo() -> ProgressRepository:
    return ProgressRepository(get_store())


def get_question_bank_repo() -> QuestionBankRepository:
    return QuestionBankRepository(get_store())


def get_attempts_repo() -> AttemptsRepository:
    return AttemptsRepository(get_store())


def get_question_reports_repo() -> QuestionReportsRepository:
    return QuestionReportsRepository(get_store())

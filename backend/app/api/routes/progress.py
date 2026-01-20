from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps.practice_repos import get_concepts_repo, get_progress_repo
from app.domain.practice.models import ConceptProgress
from app.domain.practice.selection import is_due
from app.domain.practice.scheduling import utc_now
from app.infra.repositories.concepts_repository import ConceptsRepository
from app.infra.repositories.progress_repository import ProgressRepository

router = APIRouter(prefix="", tags=["progress"])


class ProgressItem(BaseModel):
    concept_id: str
    progress: ConceptProgress
    is_due: bool


class ProgressListResponse(BaseModel):
    items: list[ProgressItem]


@router.get("/progress", response_model=ProgressListResponse)
def list_progress(
    concepts_repo: ConceptsRepository = Depends(get_concepts_repo),
    progress_repo: ProgressRepository = Depends(get_progress_repo),
) -> ProgressListResponse:
    """List per-concept progress.

    Notes:
        - Returns progress entries for all concepts.
        - If a concept has no stored progress yet, returns default progress values.
    """

    now = utc_now()
    progress_by = progress_repo.get_all()

    items: list[ProgressItem] = []
    for concept in concepts_repo.list_concepts():
        progress = progress_by.get(concept.id) or ConceptProgress(concept_id=concept.id)
        items.append(
            ProgressItem(
                concept_id=concept.id,
                progress=progress,
                is_due=is_due(progress, now=now),
            )
        )

    return ProgressListResponse(items=items)


class ProgressGetResponse(BaseModel):
    concept_id: str
    progress: ConceptProgress
    is_due: bool


@router.get("/concepts/{concept_id}/progress", response_model=ProgressGetResponse)
def get_concept_progress(
    concept_id: str,
    concepts_repo: ConceptsRepository = Depends(get_concepts_repo),
    progress_repo: ProgressRepository = Depends(get_progress_repo),
) -> ProgressGetResponse:
    """Get progress for a single concept.

    Error cases:
        - 404 if the concept does not exist.
    """

    concept = concepts_repo.get_concept(concept_id)
    if concept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "concept_not_found", "message": "Concept not found"}},
        )

    now = utc_now()
    progress = progress_repo.get(concept_id) or ConceptProgress(concept_id=concept_id)

    return ProgressGetResponse(concept_id=concept_id, progress=progress, is_due=is_due(progress, now=now))

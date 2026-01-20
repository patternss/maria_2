from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps.repositories import get_concepts_repository
from app.domain.concepts import Concept, ConceptCreate
from app.infra.repositories.concepts_repository import ConceptsRepository

router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.post("", response_model=Concept, status_code=status.HTTP_201_CREATED)
def create_concept(
    payload: ConceptCreate,
    repo: ConceptsRepository = Depends(get_concepts_repository),
) -> Concept:
    """Create a new concept.

    Inputs:
        JSON payload containing title, optional description, tags, and source_url.

    Outputs:
        The created concept object, including ID and timestamps.

    Error cases:
        - 400 if validation fails (handled by FastAPI/Pydantic)
    """

    return repo.create_concept(payload)


@router.get("", response_model=list[Concept])
def list_concepts(
    repo: ConceptsRepository = Depends(get_concepts_repository),
) -> list[Concept]:
    """List all concepts."""

    return repo.list_concepts()


@router.get("/{concept_id}", response_model=Concept)
def get_concept(
    concept_id: str,
    repo: ConceptsRepository = Depends(get_concepts_repository),
) -> Concept:
    """Get a concept by ID.

    Inputs:
        concept_id: Concept UUID.

    Outputs:
        Concept object.

    Error cases:
        - 404 if the concept does not exist.
    """

    concept = repo.get_concept(concept_id)
    if concept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "concept_not_found", "message": "Concept not found"}},
        )

    return concept

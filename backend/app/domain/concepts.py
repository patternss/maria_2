from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class ConceptCreate(BaseModel):
    """Input payload for creating a concept."""

    title: Annotated[str, Field(min_length=1, max_length=200)]
    description: str | None = Field(default=None, max_length=2000)
    tags: list[str] = Field(default_factory=list, description="Optional tags/topics")
    source_url: str | None = Field(default=None, description="Optional source link")


class Concept(BaseModel):
    """Stored concept model."""

    id: str
    title: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    source_url: str | None = None

    created_at: datetime
    updated_at: datetime

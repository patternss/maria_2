from __future__ import annotations

from functools import lru_cache

from app.core.settings import get_settings
from app.infra.llm.ollama_client import OllamaClient


@lru_cache
def get_ollama_client() -> OllamaClient:
    settings = get_settings()
    return OllamaClient(base_url=settings.ollama_base_url)

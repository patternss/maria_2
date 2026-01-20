from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.

    This settings object is the single source of truth for runtime configuration.

    Inputs:
        Environment variables and optional `.env` file.

    Outputs:
        Strongly typed configuration values used by the app.

    Notes:
        - We keep settings intentionally minimal in Phase 1.
        - Values can be expanded as we implement storage/LLM integration.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "maria_2"
    api_prefix: str = ""

    data_dir: str = Field(default="../data", description="Path to the YAML data directory")

    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    ollama_generation_model: str = Field(
        default="qwen2.5:14b",
        description="Placeholder generation/grading model name (can be changed later)",
    )
    ollama_evaluator_model: str = Field(
        default="qwen2.5:14b",
        description="Placeholder evaluator model name (can be changed later)",
    )

    cors_allow_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        description="Comma-separated list of allowed CORS origins",
    )


def get_settings() -> Settings:
    """Return the current settings.

    This function exists so future changes (caching, overrides in tests) have a
    single place to hook into.
    """

    return Settings()

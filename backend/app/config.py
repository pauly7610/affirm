"""Application configuration from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://affirm:affirm_dev@localhost:5432/affirm_discovery")
    USE_MOCK_DB: bool = os.getenv("USE_MOCK_DB", "true").lower() == "true"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "none")
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "none")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "none")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    EMBEDDING_DIM: int = 384


@lru_cache()
def get_settings() -> Settings:
    return Settings()

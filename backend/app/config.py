from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: str
    cors_origins: str = "http://localhost:3000"

    # File paths
    tenders_file: str = "data/Tenders_List.json"
    embeddings_cache_file: str = "data/embeddings_cache.json"
    feedback_file: str = "data/feedback.jsonl"

    # OpenAI settings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Feedback settings
    feedback_smoothing_factor: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

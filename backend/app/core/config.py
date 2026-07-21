from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = (
        "Enterprise AI Assistant"
    )

    app_version: str = "1.0.0"

    api_v1_prefix: str = "/api/v1"

    environment: str = "development"

    gemini_api_key: str

    gemini_model: str = (
        "gemini-3.5-flash"
    )

    gemini_embedding_model: str = (
        "gemini-embedding-001"
    )

    chroma_path: str = "./chroma_db"

    chroma_collection: str = (
        "enterprise_documents"
    )

    database_url: str = (
        "sqlite:///./enterprise_ai.db"
    )

    jwt_secret_key: str

    jwt_algorithm: str = "HS256"

    jwt_access_token_expire_minutes: int = 60

    frontend_url: str = (
        "http://localhost:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
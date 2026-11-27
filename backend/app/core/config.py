from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    APP_NAME: str = "CareerPilot AI"
    APP_ENV: str = "development"

    DATABASE_URL: str
    REDIS_URL: str

    GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GREENHOUSE_BOARDS: dict[str, str] = {}

    INGESTION_INTERVAL_SECONDS: int = 21600


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
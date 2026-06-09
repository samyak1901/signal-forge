"""Application configuration."""

from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven application settings."""

    database_url: str = "postgresql+psycopg://signal_forge:signal_forge@localhost:5432/signal_forge"
    sec_base_url: HttpUrl = HttpUrl("https://www.sec.gov")
    sec_data_url: HttpUrl = HttpUrl("https://data.sec.gov")
    sec_user_agent: str = Field(
        default="SignalForge samyak1901@gmail.com",
        description="Declared SEC User-Agent. Replace for sustained usage.",
    )
    sec_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "mlb-fantasy-api"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_version: str = "v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/mlb_fantasy"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "console"] = "json"
    log_output: Literal["stdout", "file"] = "stdout"
    log_file_path: str = "/var/log/mlb-fantasy/api.log"

    # Jobs Service
    jobs_api_url: str = "http://localhost:8001"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

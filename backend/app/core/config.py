"""
Centralized application configuration.

All environment-driven settings live here so the rest of the codebase
never touches os.environ directly. Loaded once as a singleton via
get_settings().
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    # --- Database ---
    database_url: str = Field(
        default="mysql+pymysql://crm_user:crm_password@localhost:3306/ai_crm",
        alias="DATABASE_URL",
    )

    # --- JWT ---
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # --- Groq / AI ---
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    primary_model: str = Field(default="gemma2-9b-it", alias="PRIMARY_MODEL")
    backup_model: str = Field(default="llama-3.3-70b-versatile", alias="BACKUP_MODEL")

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads .env only once per process."""
    return Settings()
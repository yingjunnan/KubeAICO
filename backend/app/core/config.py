from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "kubeaico-backend"
    environment: Literal["dev", "staging", "prod"] = "dev"
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite+aiosqlite:///./kubeaico.db"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    use_mock_data: bool = True

    prometheus_url: str | None = None
    prometheus_timeout_seconds: int = 10

    k8s_api_url: str | None = None
    k8s_bearer_token: str | None = None
    k8s_verify_ssl: bool = False

    overview_stream_interval_seconds: int = 8

    enable_llm: bool = False
    llm_provider: str = "noop"

    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8099
    app_log_level: str = "INFO"
    app_title: str = "Litigation Command Center"

    postgres_host: str = "localhost"
    postgres_port: int = 5499
    postgres_db: str = "litigation_cc"
    postgres_user: str = "lcc"
    postgres_password: str = "lcc"

    redis_host: str = "localhost"
    redis_port: int = 6399
    redis_password: str = "changeme-redis-secret"

    paseto_secret_key: str = "replace-me-with-32-byte-secret!!"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 14

    ollama_base_url: str = "http://ollama:11434"
    ollama_chat_model: str = "qwen2.5:14b"

    cors_allow_origins: str = "http://localhost:3099,http://localhost:8099"

    deadline_warning_hours: int = 72
    deadline_critical_hours: int = 24

    chronology_min_confidence: float = 0.60
    ai_review_timeout_seconds: int = 90

    portfolio_analytics_cache_ttl_seconds: int = 900

    otel_exporter_otlp_endpoint: str = "http://tempo:4317"
    otel_service_name: str = "litigation-command-center-api"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
    app_name: str = "OfferPilot AI"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(min_length=16)
    access_token_expire_minutes: int = Field(default=60 * 24, gt=0)
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "data/uploads"
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_import_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    admin_emails: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def admin_email_set(self) -> set[str]:
        return {item.strip().lower() for item in self.admin_emails.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

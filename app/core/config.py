"""Runtime settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for local and container runs."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Smart Calendar App", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(default="sqlite:///./smart_calendar.db", alias="DATABASE_URL")
    api_v1_prefix: str = Field(default="/api", alias="API_V1_PREFIX")
    default_scan_day: str = Field(default="sun", alias="DEFAULT_SCAN_DAY")
    default_scan_hour: int = Field(default=7, alias="DEFAULT_SCAN_HOUR")
    default_scan_minute: int = Field(default=0, alias="DEFAULT_SCAN_MINUTE")
    public_app_password: str | None = Field(default=None, alias="PUBLIC_APP_PASSWORD")
    auth_cookie_name: str = Field(default="smart_calendar_auth", alias="AUTH_COOKIE_NAME")
    slack_webhook_url: str | None = Field(default=None, alias="SLACK_WEBHOOK_URL")
    microsoft_client_id: str | None = Field(default=None, alias="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: str | None = Field(default=None, alias="MICROSOFT_CLIENT_SECRET")
    microsoft_tenant_id: str | None = Field(default=None, alias="MICROSOFT_TENANT_ID")


@lru_cache
def get_settings() -> Settings:
    """Cache settings so dependency injection stays cheap."""
    return Settings()

"""Slack webhook configuration."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class SlackSettings(SQLModel, table=True):
    """Single-row Slack configuration for the MVP."""

    __tablename__ = "slack_settings"

    id: int | None = Field(default=None, primary_key=True)
    enabled: bool = False
    webhook_url: str | None = None
    channel_label: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


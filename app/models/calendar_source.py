"""Calendar source configuration."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class CalendarSource(SQLModel, table=True):
    """A configured external feed or integration source."""

    __tablename__ = "calendar_sources"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    type: str
    url: str | None = None
    enabled: bool = True
    category: str = "public"
    calendar_type: str = "public"
    scan_frequency: str = "weekly"
    preferred_weight: float = 0.5
    last_scanned_at: datetime | None = None
    config: dict[str, str | int | float | bool | list[str]] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


"""Unified event records aggregated from multiple sources."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class ExternalEvent(SQLModel, table=True):
    """Normalized event data used by API and UI layers."""

    __tablename__ = "external_events"

    id: int | None = Field(default=None, primary_key=True)
    external_id: str
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "UTC"
    location: str | None = None
    url: str | None = None
    source_name: str
    source_type: str
    calendar_type: str
    category: str
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    relevance_score: float = 0.0
    is_saved: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


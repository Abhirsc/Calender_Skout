"""Structured notes associated with saved events."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class EventNote(SQLModel, table=True):
    """Notes and quick links attached to a saved event."""

    __tablename__ = "event_notes"

    id: int | None = Field(default=None, primary_key=True)
    saved_event_id: int = Field(foreign_key="saved_events.id", index=True)
    thoughts: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    why_it_matters: str | None = None
    links: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


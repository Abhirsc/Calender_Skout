"""User save and pin state for external events."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class SavedEvent(SQLModel, table=True):
    """Saved metadata for an event the user wants to track."""

    __tablename__ = "saved_events"

    id: int | None = Field(default=None, primary_key=True)
    external_event_id: int = Field(foreign_key="external_events.id", unique=True, index=True)
    pinned: bool = False
    personal_notes: str | None = None
    follow_up_action: str | None = None
    slack_posted: bool = False
    saved_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


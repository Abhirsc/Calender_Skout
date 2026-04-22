"""API schemas for event endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SaveEventRequest(BaseModel):
    """Input used to save or pin an event."""

    pinned: bool = False
    personal_notes: str | None = None
    follow_up_action: str | None = None
    thoughts: list[str] = Field(default_factory=list)
    why_it_matters: str | None = None
    links: list[str] = Field(default_factory=list)
    post_to_slack: bool = False


class EventFilterParams(BaseModel):
    """Query options for filtering the unified event feed."""

    source: str | None = None
    category: str | None = None
    calendar_type: str | None = None
    saved_only: bool = False
    upcoming_only: bool = True


class NoteUpdateRequest(BaseModel):
    """Inline note edits from the saved events page."""

    personal_notes: str | None = None
    follow_up_action: str | None = None
    thoughts: list[str] = Field(default_factory=list)
    why_it_matters: str | None = None
    links: list[str] = Field(default_factory=list)


class SlackPreviewResponse(BaseModel):
    """Expose Slack payloads for debugging and tests."""

    payload: dict[str, Any]


class CreateEventRequest(BaseModel):
    """Manual event creation input for the unified calendar."""

    title: str
    description: str | None = None
    start_datetime: str
    end_datetime: str
    timezone: str = "Australia/Sydney"
    location: str | None = None
    url: str | None = None
    source_name: str = "Manual Entry"
    source_type: str = "manual"
    calendar_type: str = "personal"
    category: str | None = None
    tags: list[str] = Field(default_factory=list)


class AddScannedEventRequest(BaseModel):
    """Copy a discovered event into a chosen personal calendar layer."""

    calendar_type: str = "personal"
    source_name: str = "Added from scan"

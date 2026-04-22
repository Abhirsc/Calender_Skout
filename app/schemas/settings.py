"""Schemas for settings and source management."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CalendarSourceUpsert(BaseModel):
    """Create or update a calendar source."""

    name: str
    type: str
    url: str | None = None
    enabled: bool = True
    category: str = "public"
    calendar_type: str = "public"
    scan_frequency: str = "weekly"
    preferred_weight: float = 0.5
    config: dict[str, str | int | float | bool | list[str]] = Field(default_factory=dict)


class ScanCriteriaUpdate(BaseModel):
    """Update smart scan criteria."""

    keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)
    preferred_organisations: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    date_horizon_days: int = 180
    event_types: list[str] = Field(default_factory=list)
    minimum_relevance_score: float = 0.35


class SlackSettingsUpdate(BaseModel):
    """Update Slack webhook settings."""

    enabled: bool = False
    webhook_url: str | None = None
    channel_label: str | None = None


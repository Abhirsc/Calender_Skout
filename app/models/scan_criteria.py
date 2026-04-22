"""User-editable smart scan preferences."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class ScanCriteria(SQLModel, table=True):
    """Simple rules controlling event relevance scoring."""

    __tablename__ = "scan_criteria"

    id: int | None = Field(default=None, primary_key=True)
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    excluded_keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    preferred_organisations: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    preferred_locations: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    date_horizon_days: int = 180
    event_types: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    minimum_relevance_score: float = 0.35
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


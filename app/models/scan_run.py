"""Scan run tracking for weekly public source scans."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.core.time import utc_now


class ScanRun(SQLModel, table=True):
    """Stores outcome details for a scheduled or manual scan."""

    __tablename__ = "scan_runs"

    id: int | None = Field(default=None, primary_key=True)
    status: str = "success"
    scanned_sources: int = 0
    new_events_found: int = 0
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime | None = None
    notes: dict[str, str | int | float] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))


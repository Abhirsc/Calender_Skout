"""Calendar ingestion helpers for ICS and future feed types."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from uuid import uuid4

from icalendar import Calendar

from app.models.calendar_source import CalendarSource
from app.models.external_event import ExternalEvent
from app.models.scan_criteria import ScanCriteria
from app.services.relevance import score_event_relevance


def _ensure_datetime(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime.combine(value, time.min, tzinfo=UTC)


def _within_horizon(start_datetime: datetime, criteria: ScanCriteria) -> bool:
    """Keep only upcoming events inside the configured discovery horizon."""
    now = datetime.now(tz=UTC)
    horizon_limit = now + timedelta(days=criteria.date_horizon_days)
    return now <= start_datetime <= horizon_limit


def ingest_ics_text(source: CalendarSource, ics_text: str, criteria: ScanCriteria) -> list[ExternalEvent]:
    """Parse ICS text into unified ExternalEvent records."""
    calendar = Calendar.from_ical(ics_text)
    events: list[ExternalEvent] = []

    for component in calendar.walk("VEVENT"):
        start_raw = component.decoded("dtstart")
        end_raw = component.decoded("dtend", start_raw)
        start_datetime = _ensure_datetime(start_raw)
        end_datetime = _ensure_datetime(end_raw)

        if not _within_horizon(start_datetime, criteria):
            continue

        title = str(component.get("summary", "Untitled event"))
        description = str(component.get("description", "")) or None
        location = str(component.get("location", "")) or None
        url = str(component.get("url", "")) or None
        tags = [str(item) for item in component.get("categories", [])] if component.get("categories") else []

        payload = {
            "title": title,
            "description": description or "",
            "location": location or "",
            "category": source.category,
            "tags": tags,
            "source_name": source.name,
            "start_datetime": start_datetime,
        }
        relevance = score_event_relevance(payload, criteria.model_dump(), source.preferred_weight)

        events.append(
            ExternalEvent(
                external_id=str(component.get("uid", uuid4())),
                title=title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                timezone="UTC",
                location=location,
                url=url,
                source_name=source.name,
                source_type=source.type,
                calendar_type=source.calendar_type,
                category=source.category,
                tags=tags,
                relevance_score=relevance,
            )
        )

    return events

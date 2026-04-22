"""ICS export helpers for user-approved calendar additions."""

from __future__ import annotations

from icalendar import Calendar, Event

from app.models.external_event import ExternalEvent


def build_event_ics(event: ExternalEvent) -> str:
    """Generate a single-event ICS payload."""
    calendar = Calendar()
    calendar.add("prodid", "-//Smart Calendar App//EN")
    calendar.add("version", "2.0")

    item = Event()
    item.add("uid", event.external_id)
    item.add("summary", event.title)
    item.add("dtstart", event.start_datetime)
    item.add("dtend", event.end_datetime)
    item.add("description", event.description or "")
    item.add("location", event.location or "")
    if event.url:
        item.add("url", event.url)
    calendar.add_component(item)

    return calendar.to_ical().decode("utf-8")

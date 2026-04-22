"""Seed the database with editable starter records."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models import CalendarSource, ExternalEvent, ScanCriteria, SlackSettings

EMBEDDED_CONFERENCE_ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Smart Calendar App//EN
BEGIN:VEVENT
UID:ecology-summit-2026@example.com
DTSTAMP:20260323T000000Z
DTSTART:20260618T090000Z
DTEND:20260618T160000Z
SUMMARY:Wildlife Conservation Seminar
DESCRIPTION:Research and networking event focused on biodiversity monitoring.
LOCATION:Sydney Nature Center
URL:https://example.org/wildlife-conservation-seminar
CATEGORIES:conference,biodiversity,conservation
END:VEVENT
BEGIN:VEVENT
UID:giscamp-2026@example.com
DTSTAMP:20260323T000000Z
DTSTART:20260703T000000Z
DTEND:20260703T060000Z
SUMMARY:GIS and Remote Sensing Camp
DESCRIPTION:Hands-on workshop for spatial analysis, GIS, and habitat mapping.
LOCATION:Melbourne Innovation Hub
URL:https://example.org/gis-camp
CATEGORIES:workshop,gis,remote-sensing
END:VEVENT
END:VCALENDAR
"""


def seed_database(session: Session) -> None:
    """Create starter configuration, sources, and sample events only once."""
    criteria = session.exec(select(ScanCriteria)).first()
    if criteria is None:
        session.add(
            ScanCriteria(
                keywords=[
                    "ecology",
                    "environmental science",
                    "biodiversity",
                    "conservation",
                    "species distribution modelling",
                    "gis",
                    "remote sensing",
                    "data science",
                    "machine learning",
                    "conference",
                    "workshop",
                    "webinar",
                ],
                excluded_keywords=["fundraiser", "school holiday"],
                preferred_organisations=["ecological society", "landcare", "atlas of living australia"],
                preferred_locations=["sydney", "melbourne", "online"],
                date_horizon_days=180,
                event_types=["conference", "workshop", "webinar"],
                minimum_relevance_score=0.35,
            )
        )

    slack = session.exec(select(SlackSettings)).first()
    if slack is None:
        session.add(SlackSettings(enabled=False, channel_label="#calendar-saved-events"))

    if not session.exec(select(CalendarSource)).first():
        session.add_all(
            [
                CalendarSource(
                    name="Work Outlook",
                    type="outlook",
                    category="work",
                    calendar_type="work",
                    preferred_weight=0.1,
                    enabled=True,
                ),
                CalendarSource(
                    name="Personal Apple",
                    type="ics",
                    url="webcal://example.org/personal.ics",
                    category="personal",
                    calendar_type="personal",
                    preferred_weight=0.1,
                    enabled=True,
                    config={},
                ),
                CalendarSource(
                    name="Ecology Societies Feed",
                    type="ics",
                    url="https://example.org/ecology-events.ics",
                    category="conferences",
                    calendar_type="conferences",
                    preferred_weight=0.15,
                    enabled=True,
                    config={"embedded_ics": EMBEDDED_CONFERENCE_ICS},
                ),
                CalendarSource(
                    name="Landcare Groups",
                    type="manual",
                    url="https://example.org/landcare",
                    category="public",
                    calendar_type="public",
                    enabled=True,
                ),
                CalendarSource(
                    name="Biodiversity Data Communities",
                    type="manual",
                    url="https://example.org/biodiversity-data",
                    category="public",
                    calendar_type="public",
                    enabled=False,
                ),
            ]
        )

    if not session.exec(select(ExternalEvent)).first():
        session.add_all(
            [
                ExternalEvent(
                    external_id="work-1",
                    title="Team Planning Session",
                    description="Weekly team coordination across devices.",
                    start_datetime=datetime(2026, 3, 24, 0, 0, tzinfo=UTC),
                    end_datetime=datetime(2026, 3, 24, 1, 0, tzinfo=UTC),
                    timezone="UTC",
                    location="Online",
                    url="https://outlook.office.com",
                    source_name="Work Outlook",
                    source_type="outlook",
                    calendar_type="work",
                    category="work",
                    tags=["meeting"],
                    relevance_score=0.42,
                ),
                ExternalEvent(
                    external_id="personal-1",
                    title="Yoga Class",
                    description="Personal wellness session.",
                    start_datetime=datetime(2026, 3, 25, 8, 0, tzinfo=UTC),
                    end_datetime=datetime(2026, 3, 25, 9, 0, tzinfo=UTC),
                    timezone="UTC",
                    location="Neighbourhood Studio",
                    url=None,
                    source_name="Personal Apple",
                    source_type="ics",
                    calendar_type="personal",
                    category="personal",
                    tags=["wellbeing"],
                    relevance_score=0.1,
                ),
            ]
        )

    session.commit()

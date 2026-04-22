from sqlmodel import Session, SQLModel, create_engine

from app.db.seed import EMBEDDED_CONFERENCE_ICS
from app.models import CalendarSource, ScanCriteria
from app.services.public_scan import scan_public_sources

FAR_FUTURE_ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Smart Calendar App//EN
BEGIN:VEVENT
UID:future-event@example.com
DTSTAMP:20260323T000000Z
DTSTART:20280418T090000Z
DTEND:20280418T160000Z
SUMMARY:Very Far Future Ecology Event
DESCRIPTION:Should not be discovered when horizon is short.
LOCATION:Online
URL:https://example.org/future-ecology
CATEGORIES:conference,ecology
END:VEVENT
END:VCALENDAR
"""


def test_public_scan_only_targets_public_and_conference_layers() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(
            ScanCriteria(
                keywords=["conference", "ecology"],
                excluded_keywords=[],
                preferred_organisations=[],
                preferred_locations=[],
                date_horizon_days=180,
                event_types=["conference"],
                minimum_relevance_score=0.2,
            )
        )
        session.add_all(
            [
                CalendarSource(
                    name="Work Outlook",
                    type="outlook",
                    calendar_type="work",
                    category="work",
                    enabled=True,
                ),
                CalendarSource(
                    name="Conference Feed",
                    type="ics",
                    calendar_type="conferences",
                    category="conferences",
                    enabled=True,
                    config={"embedded_ics": EMBEDDED_CONFERENCE_ICS},
                ),
            ]
        )
        session.commit()

        run = scan_public_sources(session)

        assert run.scanned_sources == 1
        assert run.new_events_found >= 1


def test_public_scan_does_not_duplicate_events_on_repeat_runs() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(
            ScanCriteria(
                keywords=["conference", "ecology"],
                excluded_keywords=[],
                preferred_organisations=[],
                preferred_locations=[],
                date_horizon_days=180,
                event_types=["conference"],
                minimum_relevance_score=0.2,
            )
        )
        session.add(
            CalendarSource(
                name="Conference Feed",
                type="ics",
                calendar_type="conferences",
                category="conferences",
                enabled=True,
                config={"embedded_ics": EMBEDDED_CONFERENCE_ICS},
            )
        )
        session.commit()

        first_run = scan_public_sources(session)
        second_run = scan_public_sources(session)

        assert first_run.new_events_found >= 1
        assert second_run.new_events_found == 0


def test_public_scan_respects_hard_date_horizon() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(
            ScanCriteria(
                keywords=["conference", "ecology"],
                excluded_keywords=[],
                preferred_organisations=[],
                preferred_locations=[],
                date_horizon_days=30,
                event_types=["conference"],
                minimum_relevance_score=0.2,
            )
        )
        session.add(
            CalendarSource(
                name="Future Feed",
                type="ics",
                calendar_type="conferences",
                category="conferences",
                enabled=True,
                config={"embedded_ics": FAR_FUTURE_ICS},
            )
        )
        session.commit()

        run = scan_public_sources(session)

        assert run.scanned_sources == 1
        assert run.new_events_found == 0

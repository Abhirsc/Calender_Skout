from datetime import UTC, datetime

from app.services.dedupe import dedupe_events


def test_dedupe_events_uses_title_start_and_source() -> None:
    events = [
        {
            "title": "Wildlife Conservation Seminar",
            "start_datetime": datetime(2026, 6, 18, 9, 0, tzinfo=UTC),
            "source_name": "Ecology Societies Feed",
        },
        {
            "title": " Wildlife   Conservation Seminar ",
            "start_datetime": datetime(2026, 6, 18, 9, 0, tzinfo=UTC),
            "source_name": "Ecology Societies Feed",
        },
        {
            "title": "Wildlife Conservation Seminar",
            "start_datetime": datetime(2026, 6, 18, 9, 0, tzinfo=UTC),
            "source_name": "Different Feed",
        },
    ]

    deduped = dedupe_events(events)
    assert len(deduped) == 2


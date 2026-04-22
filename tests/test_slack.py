from datetime import UTC, datetime

from app.models.external_event import ExternalEvent
from app.models.saved_event import SavedEvent
from app.services.slack import build_slack_payload


def test_slack_payload_contains_expected_sections() -> None:
    event = ExternalEvent(
        id=3,
        external_id="conference-3",
        title="Remote Sensing Workshop",
        start_datetime=datetime(2026, 7, 3, 0, 0, tzinfo=UTC),
        end_datetime=datetime(2026, 7, 3, 6, 0, tzinfo=UTC),
        timezone="UTC",
        location="Melbourne",
        url="https://example.org/workshop",
        source_name="Ecology Societies Feed",
        source_type="ics",
        calendar_type="conferences",
        category="conferences",
        tags=["gis", "remote-sensing"],
    )
    saved = SavedEvent(
        external_event_id=3,
        pinned=True,
        personal_notes="Save for project planning.",
        follow_up_action="Share with team.",
    )

    payload = build_slack_payload(event, saved, ["Strong GIS overlap"], "Directly relevant to habitat work")

    assert payload["text"] == "Saved event: Remote Sensing Workshop"
    assert len(payload["blocks"]) >= 4
    assert any("Save for project planning." in str(block) for block in payload["blocks"])

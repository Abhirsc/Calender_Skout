from fastapi.testclient import TestClient

from app.main import app, settings


def test_scanned_event_can_be_added_to_personal_calendar() -> None:
    original_password = settings.public_app_password
    settings.public_app_password = None
    try:
        client = TestClient(app)

        create_response = client.post(
            "/api/events",
            json={
                "title": "Scanned Ecology Webinar",
                "description": "Candidate event",
                "start_datetime": "2026-04-20T09:00",
                "end_datetime": "2026-04-20T10:00",
                "calendar_type": "conferences",
                "category": "conferences",
                "source_name": "Ecology Feed",
                "source_type": "ics",
                "tags": ["ecology"],
            },
        )
        event_id = create_response.json()["id"]

        add_response = client.post(
            f"/api/events/{event_id}/add-to-calendar",
            json={"calendar_type": "personal", "source_name": "Added from scan"},
        )

        assert add_response.status_code == 200
        payload = add_response.json()
        assert payload["calendar_type"] == "personal"
        assert payload["source_name"] == "Added from scan"
        assert payload["title"] == "Scanned Ecology Webinar"
    finally:
        settings.public_app_password = original_password

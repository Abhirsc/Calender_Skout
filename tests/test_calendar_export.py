from fastapi.testclient import TestClient

from app.main import app, settings


def test_event_can_be_exported_as_ics() -> None:
    original_password = settings.public_app_password
    settings.public_app_password = None

    try:
        client = TestClient(app)
        create_response = client.post(
            "/api/events",
            json={
                "title": "Conference Review Call",
                "start_datetime": "2026-05-01T09:00:00",
                "end_datetime": "2026-05-01T10:00:00",
                "calendar_type": "personal",
            },
        )
        event_id = create_response.json()["id"]

        export_response = client.get(f"/api/events/{event_id}/calendar.ics")

        assert export_response.status_code == 200
        assert export_response.headers["content-type"].startswith("text/calendar")
        assert "BEGIN:VCALENDAR" in export_response.text
        assert "Conference Review Call" in export_response.text
    finally:
        settings.public_app_password = original_password

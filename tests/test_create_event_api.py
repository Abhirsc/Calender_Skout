from fastapi.testclient import TestClient

from app.main import app, settings


def test_create_event_endpoint_creates_manual_event() -> None:
    original_password = settings.public_app_password
    settings.public_app_password = None
    try:
        client = TestClient(app)
        response = client.post(
            "/api/events",
            json={
                "title": "Field Survey Planning",
                "description": "Prepare observations for next week.",
                "start_datetime": "2026-04-01T09:00:00",
                "end_datetime": "2026-04-01T10:00:00",
                "calendar_type": "work",
                "source_name": "Manual Entry",
                "tags": ["planning", "fieldwork"],
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["title"] == "Field Survey Planning"
        assert payload["calendar_type"] == "work"
        assert payload["source_type"] == "manual"
    finally:
        settings.public_app_password = original_password

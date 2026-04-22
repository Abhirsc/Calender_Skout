from fastapi.testclient import TestClient

from app.main import app, settings


def test_ics_file_can_be_uploaded_as_source() -> None:
    original_password = settings.public_app_password
    settings.public_app_password = None
    try:
        client = TestClient(app)

        payload = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Smart Calendar App//EN
BEGIN:VEVENT
UID:upload-event@example.com
DTSTAMP:20260412T000000Z
DTSTART:20260420T090000Z
DTEND:20260420T100000Z
SUMMARY:Uploaded ICS Event
END:VEVENT
END:VCALENDAR
"""

        response = client.post(
            "/api/settings/sources/upload",
            data={
                "name": "Uploaded Feed",
                "calendar_type": "public",
                "category": "public",
                "scan_frequency": "weekly",
                "preferred_weight": "0.5",
            },
            files={"file": ("uploaded.ics", payload, "text/calendar")},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Uploaded Feed"
        assert body["type"] == "ics"
        assert body["config"]["uploaded_filename"] == "uploaded.ics"
    finally:
        settings.public_app_password = original_password

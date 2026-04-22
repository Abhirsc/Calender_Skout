from fastapi.testclient import TestClient

from app.main import app, settings


def test_source_can_be_deleted() -> None:
    original_password = settings.public_app_password
    settings.public_app_password = None
    try:
        client = TestClient(app)

        create_response = client.post(
            "/api/settings/sources",
            json={
                "name": "Temporary Feed",
                "type": "ics",
                "url": "https://example.org/feed.ics",
                "enabled": True,
                "category": "public",
                "calendar_type": "public",
                "scan_frequency": "weekly",
                "preferred_weight": 0.5,
                "config": {},
            },
        )
        source_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/settings/sources/{source_id}")

        assert delete_response.status_code == 200
        assert delete_response.json() == {"status": "deleted", "source_id": source_id}

        list_response = client.get("/api/settings/sources")
        source_ids = {item["id"] for item in list_response.json()}
        assert source_id not in source_ids
    finally:
        settings.public_app_password = original_password

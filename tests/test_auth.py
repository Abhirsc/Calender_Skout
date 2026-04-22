from fastapi.testclient import TestClient

from app.main import app, settings


def test_shared_password_auth_flow() -> None:
    original_password = settings.public_app_password
    settings.public_app_password = "secret-pass"

    try:
      client = TestClient(app)

      status_response = client.get("/api/auth/status")
      assert status_response.status_code == 200
      assert status_response.json() == {"enabled": True, "authenticated": False}

      locked_response = client.get("/api/events")
      assert locked_response.status_code == 401

      bad_login = client.post("/api/auth/login", json={"password": "wrong"})
      assert bad_login.status_code == 401

      login = client.post("/api/auth/login", json={"password": "secret-pass"})
      assert login.status_code == 200
      assert login.json() == {"enabled": True, "authenticated": True}

      unlocked = client.get("/api/events")
      assert unlocked.status_code == 200
    finally:
      settings.public_app_password = original_password

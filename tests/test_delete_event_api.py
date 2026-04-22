from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.session import get_session
from app.main import app, settings
from app.models import EventNote, ExternalEvent, SavedEvent


def test_delete_event_endpoint_removes_saved_metadata() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    original_password = settings.public_app_password
    settings.public_app_password = None
    app.dependency_overrides[get_session] = override_get_session

    try:
        with Session(engine) as session:
            event = ExternalEvent(
                external_id="manual-delete-1",
                title="Delete Me",
                start_datetime=datetime(2026, 4, 13, 9, 0, tzinfo=UTC),
                end_datetime=datetime(2026, 4, 13, 10, 0, tzinfo=UTC),
                timezone="UTC",
                source_name="Manual Entry",
                source_type="manual",
                calendar_type="personal",
                category="personal",
                tags=["test"],
                is_saved=True,
            )
            session.add(event)
            session.commit()
            session.refresh(event)

            saved = SavedEvent(
                external_event_id=event.id,
                pinned=True,
                personal_notes="temporary",
                follow_up_action="remove it",
            )
            session.add(saved)
            session.commit()
            session.refresh(saved)

            note = EventNote(
                saved_event_id=saved.id,
                thoughts=["cleanup"],
                why_it_matters="test coverage",
                links=["https://example.org/delete"],
            )
            session.add(note)
            session.commit()
            event_id = event.id
            saved_id = saved.id
            note_id = note.id

        client = TestClient(app)
        response = client.delete(f"/api/events/{event_id}")

        assert response.status_code == 200
        assert response.json() == {"status": "deleted", "event_id": event_id}

        with Session(engine) as session:
            assert session.get(ExternalEvent, event_id) is None
            assert session.get(SavedEvent, saved_id) is None
            assert session.get(EventNote, note_id) is None
    finally:
        app.dependency_overrides.clear()
        settings.public_app_password = original_password

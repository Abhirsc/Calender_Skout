from datetime import UTC, datetime

from sqlmodel import Session, SQLModel, create_engine

from app.models import EventNote, ExternalEvent, SavedEvent
from app.schemas.events import SaveEventRequest
from app.services.saved_events import save_or_update_event


def test_save_pin_workflow_creates_saved_event_and_note() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        event = ExternalEvent(
            external_id="seed-1",
            title="Data Science for Ecology Webinar",
            start_datetime=datetime(2026, 7, 1, 1, 0, tzinfo=UTC),
            end_datetime=datetime(2026, 7, 1, 2, 0, tzinfo=UTC),
            timezone="UTC",
            source_name="Ecology Societies Feed",
            source_type="ics",
            calendar_type="conferences",
            category="conferences",
            tags=["webinar"],
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        saved, note = save_or_update_event(
            session,
            event,
            SaveEventRequest(
                pinned=True,
                personal_notes="Attend and ask about species distribution models.",
                follow_up_action="Message speaker on LinkedIn.",
                thoughts=["Relevant to current project"],
                why_it_matters="Useful methods crossover",
                links=["https://example.org/slides"],
            ),
        )

        assert saved.pinned is True
        assert saved.personal_notes is not None
        assert note.why_it_matters == "Useful methods crossover"
        assert session.get(SavedEvent, saved.id) is not None
        assert session.get(EventNote, note.id) is not None

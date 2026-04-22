"""Save, pin, and note workflows for events."""

from __future__ import annotations

from sqlmodel import Session, select

from app.core.time import utc_now
from app.models import EventNote, ExternalEvent, SavedEvent
from app.schemas.events import NoteUpdateRequest, SaveEventRequest


def save_or_update_event(session: Session, event: ExternalEvent, payload: SaveEventRequest) -> tuple[SavedEvent, EventNote]:
    """Create or update saved metadata for a unified event."""
    saved = session.exec(select(SavedEvent).where(SavedEvent.external_event_id == event.id)).first()
    if saved is None:
        saved = SavedEvent(external_event_id=event.id or 0)

    saved.pinned = payload.pinned
    saved.personal_notes = payload.personal_notes
    saved.follow_up_action = payload.follow_up_action
    saved.updated_at = utc_now()
    event.is_saved = True

    session.add(saved)
    session.add(event)
    session.commit()
    session.refresh(saved)

    note = session.exec(select(EventNote).where(EventNote.saved_event_id == saved.id)).first()
    if note is None:
        note = EventNote(saved_event_id=saved.id or 0)

    note.thoughts = payload.thoughts
    note.why_it_matters = payload.why_it_matters
    note.links = payload.links
    note.updated_at = utc_now()
    session.add(note)
    session.commit()
    session.refresh(note)
    return saved, note


def update_saved_note(session: Session, saved_event_id: int, payload: NoteUpdateRequest) -> tuple[SavedEvent, EventNote]:
    """Update notes inline from the saved events page."""
    saved = session.get(SavedEvent, saved_event_id)
    if saved is None:
        raise ValueError("Saved event not found.")

    saved.personal_notes = payload.personal_notes
    saved.follow_up_action = payload.follow_up_action
    saved.updated_at = utc_now()
    session.add(saved)

    note = session.exec(select(EventNote).where(EventNote.saved_event_id == saved_event_id)).first()
    if note is None:
        note = EventNote(saved_event_id=saved_event_id)
    note.thoughts = payload.thoughts
    note.why_it_matters = payload.why_it_matters
    note.links = payload.links
    note.updated_at = utc_now()
    session.add(note)
    session.commit()
    session.refresh(saved)
    session.refresh(note)
    return saved, note


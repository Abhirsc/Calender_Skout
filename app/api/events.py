"""Unified event API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlmodel import Session, select

from app.core.time import utc_now
from app.db.session import get_session
from app.models import EventNote, ExternalEvent, SavedEvent, ScanCriteria, SlackSettings
from app.schemas.events import AddScannedEventRequest, CreateEventRequest, NoteUpdateRequest, SaveEventRequest, SlackPreviewResponse
from app.services.calendar_export import build_event_ics
from app.services.saved_events import save_or_update_event, update_saved_note
from app.services.slack import build_slack_payload, send_slack_message

router = APIRouter(prefix="/events", tags=["events"])


def _as_utc_datetime(value: datetime) -> datetime:
    """Normalize DB-loaded datetimes so filtering is safe with SQLite."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


@router.get("")
def list_events(
    session: Session = Depends(get_session),
    source: str | None = Query(default=None),
    category: str | None = Query(default=None),
    calendar_type: str | None = Query(default=None),
    saved_only: bool = Query(default=False),
    upcoming_only: bool = Query(default=True),
) -> list[dict[str, object]]:
    """Return the unified event feed with optional filtering."""
    statement = select(ExternalEvent)
    events = session.exec(statement).all()

    if source:
        events = [event for event in events if event.source_name == source]
    if category:
        events = [event for event in events if event.category == category]
    if calendar_type:
        events = [event for event in events if event.calendar_type == calendar_type]
    if saved_only:
        events = [event for event in events if event.is_saved]
    if upcoming_only:
        now = datetime.now(tz=UTC)
        events = [event for event in events if _as_utc_datetime(event.start_datetime) >= now]

    saved_map = {item.external_event_id: item for item in session.exec(select(SavedEvent)).all()}
    notes_map = {item.saved_event_id: item for item in session.exec(select(EventNote)).all()}

    response: list[dict[str, object]] = []
    for event in sorted(events, key=lambda item: item.start_datetime):
        saved = saved_map.get(event.id)
        note = notes_map.get(saved.id) if saved else None
        response.append(
            {
                **event.model_dump(),
                "saved_event": saved.model_dump() if saved else None,
                "note": note.model_dump() if note else None,
            }
        )
    return response


@router.post("")
def create_event(payload: CreateEventRequest, session: Session = Depends(get_session)) -> dict[str, object]:
    """Create a manual event in the unified event store."""
    try:
        start_datetime = datetime.fromisoformat(payload.start_datetime)
        end_datetime = datetime.fromisoformat(payload.end_datetime)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid datetime format.") from exc

    if end_datetime <= start_datetime:
        raise HTTPException(status_code=400, detail="End time must be after start time.")

    event = ExternalEvent(
        external_id=f"manual-{uuid4()}",
        title=payload.title,
        description=payload.description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        timezone=payload.timezone,
        location=payload.location,
        url=payload.url,
        source_name=payload.source_name,
        source_type=payload.source_type,
        calendar_type=payload.calendar_type,
        category=payload.category or payload.calendar_type,
        tags=payload.tags,
        relevance_score=1.0 if payload.calendar_type in {"work", "personal"} else 0.5,
        updated_at=utc_now(),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event.model_dump()


@router.delete("/{event_id}")
def delete_event(event_id: int, session: Session = Depends(get_session)) -> dict[str, object]:
    """Delete an event and clean up any saved metadata linked to it."""
    event = session.get(ExternalEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")

    saved = session.exec(select(SavedEvent).where(SavedEvent.external_event_id == event_id)).first()
    if saved is not None:
        note = session.exec(select(EventNote).where(EventNote.saved_event_id == saved.id)).first()
        if note is not None:
            session.delete(note)
        session.delete(saved)

    session.delete(event)
    session.commit()
    return {"status": "deleted", "event_id": event_id}


@router.get("/saved")
def list_saved_events(session: Session = Depends(get_session)) -> list[dict[str, object]]:
    """Return saved items with joined event details."""
    saved_items = session.exec(select(SavedEvent)).all()
    notes_map = {item.saved_event_id: item for item in session.exec(select(EventNote)).all()}
    output: list[dict[str, object]] = []
    for saved in saved_items:
        event = session.get(ExternalEvent, saved.external_event_id)
        if event is None:
            continue
        output.append(
            {
                "saved_event": saved.model_dump(),
                "event": event.model_dump(),
                "note": notes_map.get(saved.id).model_dump() if notes_map.get(saved.id) else None,
            }
        )
    return output


@router.delete("/saved/{saved_event_id}")
def delete_saved_event(saved_event_id: int, session: Session = Depends(get_session)) -> dict[str, object]:
    """Remove saved metadata while keeping the underlying event."""
    saved = session.get(SavedEvent, saved_event_id)
    if saved is None:
        raise HTTPException(status_code=404, detail="Saved event not found.")

    event = session.get(ExternalEvent, saved.external_event_id)
    note = session.exec(select(EventNote).where(EventNote.saved_event_id == saved_event_id)).first()

    if note is not None:
        session.delete(note)

    if event is not None:
        event.is_saved = False
        event.updated_at = utc_now()
        session.add(event)

    session.delete(saved)
    session.commit()
    return {"status": "removed", "saved_event_id": saved_event_id}


@router.post("/{event_id}/add-to-calendar")
def add_scanned_event_to_calendar(
    event_id: int,
    payload: AddScannedEventRequest,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Copy a discovered event into the user's own in-app calendar."""
    event = session.get(ExternalEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")

    cloned = ExternalEvent(
        external_id=f"manual-{uuid4()}",
        title=event.title,
        description=event.description,
        start_datetime=event.start_datetime,
        end_datetime=event.end_datetime,
        timezone=event.timezone,
        location=event.location,
        url=event.url,
        source_name=payload.source_name,
        source_type="manual",
        calendar_type=payload.calendar_type,
        category=payload.calendar_type,
        tags=event.tags,
        relevance_score=1.0 if payload.calendar_type in {"work", "personal"} else event.relevance_score,
        updated_at=utc_now(),
    )
    session.add(cloned)
    session.commit()
    session.refresh(cloned)
    return cloned.model_dump()


@router.post("/{event_id}/save")
async def save_event(event_id: int, payload: SaveEventRequest, session: Session = Depends(get_session)) -> dict[str, object]:
    """Save or pin an event and optionally post to Slack."""
    event = session.get(ExternalEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")

    saved, note = save_or_update_event(session, event, payload)

    slack_payload = None
    if payload.post_to_slack:
        slack_settings = session.exec(select(SlackSettings)).first()
        if slack_settings and slack_settings.enabled and slack_settings.webhook_url:
            slack_payload = build_slack_payload(event, saved, note.thoughts, note.why_it_matters)
            saved.slack_posted = await send_slack_message(slack_settings.webhook_url, slack_payload)
            session.add(saved)
            session.commit()

    return {
        "event": event.model_dump(),
        "saved_event": saved.model_dump(),
        "note": note.model_dump(),
        "slack_payload_preview": slack_payload,
    }


@router.put("/saved/{saved_event_id}/notes")
def update_notes(saved_event_id: int, payload: NoteUpdateRequest, session: Session = Depends(get_session)) -> dict[str, object]:
    """Update saved event notes inline."""
    try:
        saved, note = update_saved_note(session, saved_event_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"saved_event": saved.model_dump(), "note": note.model_dump()}


@router.get("/{event_id}/slack-preview", response_model=SlackPreviewResponse)
def slack_preview(event_id: int, session: Session = Depends(get_session)) -> SlackPreviewResponse:
    """Return the formatted Slack payload without sending it."""
    event = session.get(ExternalEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")

    saved = session.exec(select(SavedEvent).where(SavedEvent.external_event_id == event_id)).first()
    if saved is None:
        raise HTTPException(status_code=404, detail="Event has not been saved yet.")

    note = session.exec(select(EventNote).where(EventNote.saved_event_id == saved.id)).first()
    payload = build_slack_payload(event, saved, note.thoughts if note else [], note.why_it_matters if note else None)
    return SlackPreviewResponse(payload=payload)


@router.get("/{event_id}/calendar.ics")
def download_event_ics(event_id: int, session: Session = Depends(get_session)) -> Response:
    """Export an event as an ICS file so users can add it to their own calendar."""
    event = session.get(ExternalEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")

    payload = build_event_ics(event)
    headers = {"Content-Disposition": f'attachment; filename="event-{event_id}.ics"'}
    return Response(content=payload, media_type="text/calendar", headers=headers)


@router.get("/meta/scan-criteria")
def get_scan_criteria(session: Session = Depends(get_session)) -> dict[str, object]:
    """Expose active scan criteria for UI bootstrapping."""
    criteria = session.exec(select(ScanCriteria)).first()
    if criteria is None:
        raise HTTPException(status_code=404, detail="Scan criteria not found.")
    return criteria.model_dump()

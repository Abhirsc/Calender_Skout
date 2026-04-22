"""Public source scan orchestration."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.core.time import utc_now
from app.models import CalendarSource, ExternalEvent, ScanCriteria, ScanRun
from app.services.calendar_ingestion import ingest_ics_text
from app.services.dedupe import dedupe_events


def _scan_key(title: str, start_datetime: datetime, source_name: str) -> tuple[str, str, str]:
    """Normalise scan keys so repeated runs do not create duplicate rows."""
    normalised = start_datetime if start_datetime.tzinfo else start_datetime.replace(tzinfo=UTC)
    return (title.lower().strip(), normalised.astimezone(UTC).isoformat(), source_name.lower().strip())


def scan_public_sources(session: Session) -> ScanRun:
    """Scan enabled ICS sources, dedupe them, and store new events."""
    criteria = session.exec(select(ScanCriteria)).first()
    if criteria is None:
        raise RuntimeError("Scan criteria must exist before running scans.")

    sources = session.exec(
        select(CalendarSource).where(CalendarSource.enabled.is_(True))
    ).all()
    sources = [source for source in sources if source.calendar_type in {"public", "conferences"}]
    run = ScanRun(status="running", scanned_sources=len(sources), new_events_found=0, started_at=utc_now())
    session.add(run)
    session.commit()
    session.refresh(run)

    candidates: list[ExternalEvent] = []

    for source in sources:
        raw_ics = source.config.get("embedded_ics")
        if source.type.lower() == "ics" and isinstance(raw_ics, str):
            candidates.extend(ingest_ics_text(source, raw_ics, criteria))
        source.last_scanned_at = utc_now()
        source.updated_at = utc_now()
        session.add(source)

    existing = session.exec(select(ExternalEvent)).all()
    existing_keys = {_scan_key(item.title, item.start_datetime, item.source_name) for item in existing}

    inserted = 0
    for event in dedupe_events(candidates):
        key = _scan_key(event.title, event.start_datetime, event.source_name)
        if key in existing_keys:
            continue
        session.add(event)
        existing_keys.add(key)
        inserted += 1

    run.status = "success"
    run.new_events_found = inserted
    run.finished_at = utc_now()
    run.notes = {"message": f"Scanned {len(sources)} sources"}
    session.add(run)
    session.commit()
    return run

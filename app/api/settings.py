"""Settings, source management, and scan controls."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.time import utc_now
from app.db.session import get_session
from app.models import CalendarSource, ScanCriteria, ScanRun, SlackSettings
from app.schemas.settings import CalendarSourceUpsert, ScanCriteriaUpdate, SlackSettingsUpdate
from app.services.public_scan import scan_public_sources

router = APIRouter(prefix="/settings", tags=["settings"])
settings = get_settings()


def _serialise_scan_run(run: ScanRun) -> dict[str, object]:
    """Return a JSON-safe scan run payload for the frontend."""
    return {
        "id": run.id,
        "status": run.status,
        "scanned_sources": run.scanned_sources,
        "new_events_found": run.new_events_found,
        "started_at": run.started_at.isoformat(),
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "notes": run.notes,
    }


@router.get("/sources")
def list_sources(session: Session = Depends(get_session)) -> list[dict[str, object]]:
    """Return editable source configuration."""
    sources = session.exec(select(CalendarSource)).all()
    return [source.model_dump() for source in sources]


@router.post("/sources")
def create_source(payload: CalendarSourceUpsert, session: Session = Depends(get_session)) -> dict[str, object]:
    """Create a new calendar source."""
    source = CalendarSource(**payload.model_dump(), updated_at=utc_now())
    session.add(source)
    session.commit()
    session.refresh(source)
    return source.model_dump()


@router.post("/sources/upload")
async def upload_source_file(
    name: str = Form(...),
    calendar_type: str = Form(default="public"),
    category: str = Form(default="public"),
    scan_frequency: str = Form(default="weekly"),
    preferred_weight: float = Form(default=0.5),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Create an ICS source from an uploaded calendar file."""
    filename = file.filename or ""
    if not filename.lower().endswith(".ics"):
        raise HTTPException(status_code=400, detail="Only .ics files are supported.")

    content = (await file.read()).decode("utf-8")
    source = CalendarSource(
        name=name,
        type="ics",
        url=filename,
        enabled=True,
        category=category,
        calendar_type=calendar_type,
        scan_frequency=scan_frequency,
        preferred_weight=preferred_weight,
        config={"embedded_ics": content, "uploaded_filename": filename},
        updated_at=utc_now(),
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source.model_dump()


@router.put("/sources/{source_id}")
def update_source(source_id: int, payload: CalendarSourceUpsert, session: Session = Depends(get_session)) -> dict[str, object]:
    """Update a calendar source."""
    source = session.get(CalendarSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")

    for field, value in payload.model_dump().items():
        setattr(source, field, value)
    source.updated_at = utc_now()
    session.add(source)
    session.commit()
    session.refresh(source)
    return source.model_dump()


@router.delete("/sources/{source_id}")
def delete_source(source_id: int, session: Session = Depends(get_session)) -> dict[str, object]:
    """Delete a configured calendar source."""
    source = session.get(CalendarSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")

    session.delete(source)
    session.commit()
    return {"status": "deleted", "source_id": source_id}


@router.get("/scan-criteria")
def get_scan_criteria(session: Session = Depends(get_session)) -> dict[str, object]:
    """Get the active scan criteria."""
    criteria = session.exec(select(ScanCriteria)).first()
    if criteria is None:
        raise HTTPException(status_code=404, detail="Scan criteria not found.")
    return criteria.model_dump()


@router.put("/scan-criteria")
def update_scan_criteria(payload: ScanCriteriaUpdate, session: Session = Depends(get_session)) -> dict[str, object]:
    """Update the scan criteria record."""
    criteria = session.exec(select(ScanCriteria)).first()
    if criteria is None:
        criteria = ScanCriteria(**payload.model_dump())
    else:
        for field, value in payload.model_dump().items():
            setattr(criteria, field, value)
        criteria.updated_at = utc_now()
    session.add(criteria)
    session.commit()
    session.refresh(criteria)
    return criteria.model_dump()


@router.get("/slack")
def get_slack_settings(session: Session = Depends(get_session)) -> dict[str, object]:
    """Get the saved Slack webhook configuration."""
    slack = session.exec(select(SlackSettings)).first()
    if slack is None:
        raise HTTPException(status_code=404, detail="Slack settings not found.")
    return slack.model_dump()


@router.put("/slack")
def update_slack_settings(payload: SlackSettingsUpdate, session: Session = Depends(get_session)) -> dict[str, object]:
    """Update Slack webhook settings."""
    slack = session.exec(select(SlackSettings)).first()
    if slack is None:
        slack = SlackSettings(**payload.model_dump())
    else:
        for field, value in payload.model_dump().items():
            setattr(slack, field, value)
        slack.updated_at = utc_now()
    session.add(slack)
    session.commit()
    session.refresh(slack)
    return slack.model_dump()


@router.post("/run-scan")
def run_scan(session: Session = Depends(get_session)) -> dict[str, object]:
    """Manually trigger the weekly scan."""
    run = scan_public_sources(session)
    return _serialise_scan_run(run)


@router.get("/scan-runs")
def list_scan_runs(session: Session = Depends(get_session)) -> list[dict[str, object]]:
    """List recent scan history for the status indicator."""
    runs = session.exec(select(ScanRun)).all()
    return [_serialise_scan_run(run) for run in sorted(runs, key=lambda item: item.started_at, reverse=True)]


@router.get("/scan-schedule")
def get_scan_schedule() -> dict[str, object]:
    """Expose the configured weekly public scan schedule."""
    return {
        "enabled": True,
        "target_layers": ["public", "conferences"],
        "frequency": "weekly",
        "day_of_week": settings.default_scan_day,
        "hour_utc": settings.default_scan_hour,
        "minute_utc": settings.default_scan_minute,
    }

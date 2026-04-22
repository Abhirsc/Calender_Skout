"""APScheduler setup for weekly public scans."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session

from app.core.config import get_settings
from app.db.session import engine
from app.services.public_scan import scan_public_sources

settings = get_settings()
_scheduler: BackgroundScheduler | None = None


def _run_weekly_scan() -> None:
    with Session(engine) as session:
        scan_public_sources(session)


def start_scheduler() -> BackgroundScheduler:
    """Start the shared weekly scheduler only once."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_weekly_scan,
        trigger="cron",
        day_of_week=settings.default_scan_day,
        hour=settings.default_scan_hour,
        minute=settings.default_scan_minute,
        id="weekly-public-scan",
        replace_existing=True,
    )
    _scheduler.start()
    return _scheduler


def stop_scheduler() -> None:
    """Stop the scheduler on application shutdown."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


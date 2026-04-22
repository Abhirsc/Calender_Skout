"""Deduplication helpers for merged event sources."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any


def _extract(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _normalise_title(title: str | None) -> str:
    return " ".join((title or "").lower().split())


def _normalise_start(value: datetime | str | None) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value or "")


def dedupe_events(events: Iterable[Any]) -> list[Any]:
    """Remove duplicates using title, start time, and loose source identity."""
    deduped: list[Any] = []
    seen: set[tuple[str, str, str]] = set()

    for event in events:
        key = (
            _normalise_title(_extract(event, "title")),
            _normalise_start(_extract(event, "start_datetime")),
            _normalise_title(_extract(event, "source_name")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)

    return deduped


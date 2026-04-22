"""Scoring logic for smart event discovery."""

from __future__ import annotations

from datetime import UTC, datetime
from math import exp
from typing import Any


def _text_blob(event: dict[str, Any]) -> str:
    parts = [
        event.get("title", ""),
        event.get("description", ""),
        event.get("category", ""),
        " ".join(event.get("tags", [])),
        event.get("location", ""),
        event.get("source_name", ""),
    ]
    return " ".join(part for part in parts if part).lower()


def score_event_relevance(event: dict[str, Any], criteria: dict[str, Any], source_weight: float = 0.0) -> float:
    """Return a simple relevance score between 0 and 1."""
    text = _text_blob(event)
    keywords = [keyword.lower() for keyword in criteria.get("keywords", [])]
    excluded = [keyword.lower() for keyword in criteria.get("excluded_keywords", [])]
    preferred_locations = [item.lower() for item in criteria.get("preferred_locations", [])]
    preferred_orgs = [item.lower() for item in criteria.get("preferred_organisations", [])]
    event_types = [item.lower() for item in criteria.get("event_types", [])]

    if excluded and any(term in text for term in excluded):
        return 0.0

    keyword_hits = sum(1 for term in keywords if term in text)
    keyword_score = min(keyword_hits / max(len(keywords), 1), 1.0) * 0.45

    org_score = 0.15 if any(term in text for term in preferred_orgs) else 0.0
    location_score = 0.1 if any(term in text for term in preferred_locations) else 0.0
    type_score = 0.1 if any(term in text for term in event_types) else 0.0

    horizon = int(criteria.get("date_horizon_days", 180))
    start = event.get("start_datetime")
    if isinstance(start, str):
        start = datetime.fromisoformat(start)
    if start is None:
        date_score = 0.0
    else:
        now = datetime.now(tz=UTC)
        delta_days = max((start - now).days, 0)
        midpoint = max(horizon / 2, 1)
        date_score = 0.2 * (1 / (1 + exp((delta_days - midpoint) / 30)))

    total = keyword_score + org_score + location_score + type_score + date_score + min(source_weight, 0.15)
    return round(min(total, 1.0), 3)


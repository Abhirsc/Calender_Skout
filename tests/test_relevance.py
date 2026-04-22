from datetime import UTC, datetime, timedelta

from app.services.relevance import score_event_relevance


def test_relevance_scoring_rewards_matching_topics() -> None:
    event = {
        "title": "Ecology and GIS Conference",
        "description": "A biodiversity workshop for conservation planners.",
        "location": "Sydney",
        "category": "conferences",
        "tags": ["ecology", "gis", "conference"],
        "source_name": "Ecological Society",
        "start_datetime": datetime.now(tz=UTC) + timedelta(days=14),
    }
    criteria = {
        "keywords": ["ecology", "gis", "biodiversity", "conference"],
        "excluded_keywords": ["fundraiser"],
        "preferred_locations": ["sydney"],
        "preferred_organisations": ["ecological society"],
        "event_types": ["conference"],
        "date_horizon_days": 180,
    }

    score = score_event_relevance(event, criteria, source_weight=0.15)
    assert 0.7 <= score <= 1.0


def test_relevance_scoring_drops_to_zero_for_excluded_terms() -> None:
    event = {
        "title": "School Holiday Fundraiser",
        "description": "Community event",
        "location": "Online",
        "category": "public",
        "tags": [],
        "source_name": "Community Feed",
        "start_datetime": datetime.now(tz=UTC) + timedelta(days=7),
    }
    criteria = {
        "keywords": ["ecology"],
        "excluded_keywords": ["fundraiser"],
        "preferred_locations": [],
        "preferred_organisations": [],
        "event_types": [],
        "date_horizon_days": 180,
    }

    assert score_event_relevance(event, criteria) == 0.0


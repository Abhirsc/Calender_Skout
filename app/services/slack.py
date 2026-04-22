"""Slack payload creation and webhook delivery."""

from __future__ import annotations

from typing import Any

import httpx

from app.models.external_event import ExternalEvent
from app.models.saved_event import SavedEvent


def build_slack_payload(event: ExternalEvent, saved_event: SavedEvent, thoughts: list[str], why_it_matters: str | None) -> dict[str, Any]:
    """Build a simple, readable Slack block payload."""
    notes = saved_event.personal_notes or "No notes added yet."
    follow_up = saved_event.follow_up_action or "No follow-up recorded."
    bullets = "\n".join(f"• {thought}" for thought in thoughts) or "• No quick notes yet."
    reason = why_it_matters or "No reason added yet."

    return {
        "text": f"Saved event: {event.title}",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": event.title}},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*When*\n{event.start_datetime:%a %d %b %Y %H:%M} - {event.end_datetime:%H:%M}"},
                    {"type": "mrkdwn", "text": f"*Source*\n{event.source_name} ({event.calendar_type})"},
                    {"type": "mrkdwn", "text": f"*Location*\n{event.location or 'TBA'}"},
                    {"type": "mrkdwn", "text": f"*Link*\n{event.url or 'No external link'}"},
                ],
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Notes*\n{notes}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Why it matters*\n{reason}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Thoughts*\n{bullets}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Follow-up*\n{follow_up}"}},
        ],
    }


async def send_slack_message(webhook_url: str, payload: dict[str, Any]) -> bool:
    """Send the Slack payload and fail softly when the webhook is unavailable."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(webhook_url, json=payload)
        return response.status_code < 400


"""Microsoft Graph integration stub for future Outlook sync."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OutlookTokenBundle:
    """Token abstraction so storage can change later without touching API code."""

    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None


class OutlookCalendarService:
    """Read-only Outlook sync placeholder for the MVP."""

    def __init__(self, token_bundle: OutlookTokenBundle | None = None) -> None:
        self.token_bundle = token_bundle

    async def list_events(self) -> list[dict[str, str]]:
        """Return an empty list until Microsoft Graph auth is wired up."""
        return []


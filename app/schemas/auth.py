"""Schemas for lightweight shared-password auth."""

from __future__ import annotations

from pydantic import BaseModel


class AuthLoginRequest(BaseModel):
    """Password entry used to unlock the public app."""

    password: str


class AuthStatusResponse(BaseModel):
    """Expose whether the app is locked and whether this client is unlocked."""

    enabled: bool
    authenticated: bool


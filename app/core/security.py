"""Lightweight shared-password helpers for public deployments."""

from __future__ import annotations

from hashlib import sha256
from hmac import compare_digest


def auth_token_from_password(password: str) -> str:
    """Derive a stable token from the configured shared password."""
    return sha256(password.encode("utf-8")).hexdigest()


def is_valid_auth_cookie(password: str | None, cookie_value: str | None) -> bool:
    """Check whether the cookie matches the configured shared password."""
    if not password:
        return True
    if not cookie_value:
        return False
    return compare_digest(auth_token_from_password(password), cookie_value)


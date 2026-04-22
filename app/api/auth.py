"""Simple shared-password auth endpoints for public MVP deployments."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response

from app.core.config import Settings, get_settings
from app.core.security import auth_token_from_password, is_valid_auth_cookie
from app.schemas.auth import AuthLoginRequest, AuthStatusResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status", response_model=AuthStatusResponse)
def auth_status(request: Request, settings: Settings = Depends(get_settings)) -> AuthStatusResponse:
    """Return lock status for the current client."""
    cookie_value = request.cookies.get(settings.auth_cookie_name)
    return AuthStatusResponse(
        enabled=bool(settings.public_app_password),
        authenticated=is_valid_auth_cookie(settings.public_app_password, cookie_value),
    )


@router.post("/login", response_model=AuthStatusResponse)
def auth_login(payload: AuthLoginRequest, response: Response, settings: Settings = Depends(get_settings)) -> AuthStatusResponse:
    """Unlock the app using the configured shared password."""
    if not settings.public_app_password:
        return AuthStatusResponse(enabled=False, authenticated=True)

    if payload.password != settings.public_app_password:
        response.status_code = 401
        return AuthStatusResponse(enabled=True, authenticated=False)

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=auth_token_from_password(settings.public_app_password),
        httponly=True,
        samesite="lax",
        secure=settings.app_env == "production",
        max_age=60 * 60 * 24 * 14,
    )
    return AuthStatusResponse(enabled=True, authenticated=True)


@router.post("/logout", response_model=AuthStatusResponse)
def auth_logout(response: Response, settings: Settings = Depends(get_settings)) -> AuthStatusResponse:
    """Clear the auth cookie."""
    response.delete_cookie(settings.auth_cookie_name)
    return AuthStatusResponse(enabled=bool(settings.public_app_password), authenticated=False)

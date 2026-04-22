"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.health import router as health_router
from app.api.settings import router as settings_router
from app.core.config import get_settings
from app.core.security import is_valid_auth_cookie
from app.db.seed import seed_database
from app.db.session import get_session, init_db
from app.tasks.scheduler import start_scheduler, stop_scheduler

settings = get_settings()
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepare the database and scheduled jobs on startup."""
    init_db()
    session = next(get_session())
    seed_database(session)
    session.close()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def shared_password_lock(request: Request, call_next):
    """Enforce the optional shared-password gate for API access."""
    if not settings.public_app_password:
        return await call_next(request)

    allowed_prefixes = {
        f"{settings.api_v1_prefix}/auth",
        f"{settings.api_v1_prefix}/health",
        "/assets",
        "/favicon.ico",
    }
    if any(request.url.path.startswith(prefix) for prefix in allowed_prefixes):
        return await call_next(request)

    cookie_value = request.cookies.get(settings.auth_cookie_name)
    if is_valid_auth_cookie(settings.public_app_password, cookie_value):
        return await call_next(request)

    if request.url.path.startswith(settings.api_v1_prefix):
        return JSONResponse(status_code=401, content={"detail": "Password required."})

    if frontend_dist.exists():
        return FileResponse(frontend_dist / "index.html")
    return JSONResponse(status_code=401, content={"detail": "Password required."})

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(events_router, prefix=settings.api_v1_prefix)
app.include_router(settings_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    """Lightweight default root for API-first development."""
    return {"message": "Smart Calendar API is running."}


if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="frontend-assets")

    @app.get("/app/{full_path:path}", include_in_schema=False)
    @app.get("/saved", include_in_schema=False)
    @app.get("/sources", include_in_schema=False)
    @app.get("/settings", include_in_schema=False)
    def frontend_app(full_path: str = "") -> FileResponse:
        """Serve the built SPA when available."""
        return FileResponse(frontend_dist / "index.html")

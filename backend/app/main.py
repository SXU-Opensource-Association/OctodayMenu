from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, auth, draws, public, social
from app.core.config import get_settings
from app.core.database import SessionLocal, init_db
from app.services.seed import ensure_super_admin
from app.models import AuditLog


def build_lifespan(run_startup: bool):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if run_startup:
            init_db()
            with SessionLocal() as db:
                ensure_super_admin(db)
        yield

    return lifespan


def create_app(run_startup: bool = True) -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=build_lifespan(run_startup))
    app.state.session_factory = SessionLocal
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_and_audit_middleware(request: Request, call_next):
        if (
            request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and request.cookies.get(settings.auth_cookie_name)
        ):
            origin = request.headers.get("origin")
            if origin and origin not in settings.cors_origins:
                return JSONResponse(status_code=403, content={"detail": "请求来源不受信任"})
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        actor = getattr(request.state, "audit_actor", None)
        if (
            actor is not None
            and request.url.path.startswith("/api/admin")
            and request.method in {"POST", "PATCH", "DELETE"}
        ):
            with request.app.state.session_factory() as db:
                db.add(
                    AuditLog(
                        actor_id=actor["id"],
                        actor_email=actor["email"],
                        actor_role=actor["role"],
                        action=request.method,
                        resource=request.url.path[:500],
                        status_code=response.status_code,
                        ip_address=request.client.host[:64] if request.client else None,
                    )
                )
                db.commit()
        return response

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    app.include_router(auth.router, prefix="/api")
    app.include_router(public.router, prefix="/api")
    app.include_router(draws.router, prefix="/api")
    app.include_router(social.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")
    uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
    return app


app = create_app()

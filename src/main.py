"""FastAPI application entry point for the DB-backed fitness management API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database import get_database_health, new_session
from src.repositories.user_repository import UserRepository
from src.routes import auth, records, search, statistics
from src.services.security_service import hash_password


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Seed default admin account if schema is ready."""
    db: Session = new_session()
    try:
        users = UserRepository(db)
        if users.count_users() == 0:
            users.create(
                {
                    "username": "admin",
                    "display_name": "Administrator",
                    "email": "admin@fitness.local",
                    "phone": "+351900000000",
                    "password_hash": hash_password("admin"),
                }
            )
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "Database schema is not ready. Run 'python -m alembic upgrade head' before starting the API."
        ) from exc
    finally:
        db.close()
    yield


app = FastAPI(
    title="Fitness Management API",
    description="PostgreSQL-backed API with JWT auth and modular routes.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Simple API welcome endpoint."""
    return {"message": "Fitness Management API is running with DB-backed routes."}


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Liveness endpoint for local development checks."""
    return {"status": "ok"}


@app.get("/health/db")
def database_healthcheck() -> dict[str, str | None]:
    """Database readiness endpoint including current Alembic revision."""
    try:
        health = get_database_health()
        return {
            "status": "ok",
            "database": health["database"],
            "alembic_revision": health["alembic_revision"],
        }
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc}") from exc


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(records.router, prefix="/records", tags=["records"])
app.include_router(search.router, prefix="/records", tags=["search"])
app.include_router(statistics.router, prefix="/records", tags=["statistics"])


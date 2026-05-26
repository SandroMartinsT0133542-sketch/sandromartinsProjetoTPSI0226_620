"""SQLAlchemy engine and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

try:
    from src.config import settings
except ModuleNotFoundError:
    from config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def new_session() -> Session:
    """Create a typed SQLAlchemy session instance."""
    return SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """Provide a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_database_health() -> dict[str, str | None]:
    """Check DB connectivity and return current Alembic revision if available."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        revision = db.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar_one_or_none()
        return {"database": "up", "alembic_revision": revision}
    finally:
        db.close()

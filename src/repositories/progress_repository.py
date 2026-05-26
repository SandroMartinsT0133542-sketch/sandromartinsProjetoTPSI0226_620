"""Data access for progress records."""

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from src.models import ProgressEntry
except ModuleNotFoundError:
    from models import ProgressEntry


class ProgressRepository:
    """Repository for progress entry queries and mutations."""

    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: int) -> list[ProgressEntry]:
        stmt = select(ProgressEntry).where(ProgressEntry.user_id == user_id)
        return list(self.db.scalars(stmt).all())

    def get_by_id_for_user(self, record_id: int, user_id: int) -> ProgressEntry | None:
        stmt = select(ProgressEntry).where(
            ProgressEntry.record_id == record_id,
            ProgressEntry.user_id == user_id,
        )
        return self.db.scalar(stmt)

    def create(self, user_id: int, payload: dict[str, str | int | float]) -> ProgressEntry:
        record = ProgressEntry(
            user_id=user_id,
            record_date=str(payload["record_date"]),
            weight_kg=float(payload["weight_kg"]),
            body_fat_pct=float(payload["body_fat_pct"]),
            daily_calories=int(payload["daily_calories"]),
            notes=str(payload["notes"]),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: ProgressEntry, updates: dict[str, str | int | float]) -> ProgressEntry:
        for field, value in updates.items():
            setattr(record, field, value)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: ProgressEntry) -> None:
        self.db.delete(record)
        self.db.commit()

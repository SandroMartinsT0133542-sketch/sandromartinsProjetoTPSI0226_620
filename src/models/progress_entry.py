"""Progress entry model and compatibility helper functions."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
	from src.models.base import Base
except ModuleNotFoundError:
	from models.base import Base


Record = dict[str, Any]


class ProgressEntry(Base):
	"""Stores one fitness progress record for a user."""

	__tablename__ = "progress_entries"

	record_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
	record_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
	weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
	body_fat_pct: Mapped[float] = mapped_column(Float, nullable=False)
	daily_calories: Mapped[int] = mapped_column(Integer, nullable=False)
	notes: Mapped[str] = mapped_column(String(500), default="", nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	user = relationship("User", back_populates="progress_entries")

	def to_dict(self) -> Record:
		"""Return dictionary data compatible with search/sort algorithms."""
		return {
			"record_id": int(self.record_id),
			"user_id": int(self.user_id),
			"record_date": str(self.record_date),
			"weight_kg": float(self.weight_kg),
			"body_fat_pct": float(self.body_fat_pct),
			"daily_calories": int(self.daily_calories),
			"notes": str(self.notes),
		}


def build_progress_entry(
	record_id: int,
	user_id: int,
	record_date: str,
	weight_kg: float,
	body_fat_pct: float,
	daily_calories: int,
	notes: str,
) -> Record:
	"""Build and return a normalized record dictionary."""
	return {
		"record_id": int(record_id),
		"user_id": int(user_id),
		"record_date": str(record_date),
		"weight_kg": float(weight_kg),
		"body_fat_pct": float(body_fat_pct),
		"daily_calories": int(daily_calories),
		"notes": str(notes),
	}


def parse_progress_entry(raw: dict[str, Any]) -> Record:
	"""Normalize/coerce raw persisted data into expected record structure."""
	return build_progress_entry(
		record_id=raw.get("record_id", 0),
		user_id=raw.get("user_id", 0),
		record_date=raw.get("record_date", ""),
		weight_kg=raw.get("weight_kg", 0.0),
		body_fat_pct=raw.get("body_fat_pct", 0.0),
		daily_calories=raw.get("daily_calories", 0),
		notes=raw.get("notes", ""),
	)


def serialize_progress_entry(record: Record) -> Record:
	"""Prepare one record dictionary for JSON persistence output."""
	return parse_progress_entry(record)


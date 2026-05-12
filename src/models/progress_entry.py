"""Record model helpers using dictionaries (no class-based model)."""

from typing import Any


Record = dict[str, Any]


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


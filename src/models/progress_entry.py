"""Record model helpers using dictionaries (no class-based model)."""

from typing import Any


Record = dict[str, Any]


def build_progress_entry(
	record_id: int,
	client_name: str,
	email: str,
	phone: str,
	record_date: str,
	weight_kg: float,
	body_fat_pct: float,
	daily_calories: int,
	password: str,
	notes: str,
) -> Record:
	"""Build and return a normalized record dictionary."""
	return {
		"record_id": int(record_id),
		"client_name": str(client_name),
		"email": str(email),
		"phone": str(phone),
		"record_date": str(record_date),
		"weight_kg": float(weight_kg),
		"body_fat_pct": float(body_fat_pct),
		"daily_calories": int(daily_calories),
		"password": str(password),
		"notes": str(notes),
	}


def parse_progress_entry(raw: dict[str, Any]) -> Record:
	"""Normalize/coerce raw persisted data into expected record structure."""
	return build_progress_entry(
		record_id=raw.get("record_id", 0),
		client_name=raw.get("client_name", ""),
		email=raw.get("email", ""),
		phone=raw.get("phone", ""),
		record_date=raw.get("record_date", ""),
		weight_kg=raw.get("weight_kg", 0.0),
		body_fat_pct=raw.get("body_fat_pct", 0.0),
		daily_calories=raw.get("daily_calories", 0),
		password=raw.get("password", ""),
		notes=raw.get("notes", ""),
	)


def serialize_progress_entry(record: Record) -> Record:
	"""Prepare one record dictionary for JSON persistence output."""
	return parse_progress_entry(record)


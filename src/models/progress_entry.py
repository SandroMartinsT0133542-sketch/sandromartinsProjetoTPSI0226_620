"""Record model helpers using dictionaries (no class-based model)."""


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
) -> dict:
	"""Build and return a normalized record dictionary."""
	pass


def parse_progress_entry(raw: dict) -> dict:
	"""Normalize/coerce raw persisted data into expected record structure."""
	pass


def serialize_progress_entry(record: dict) -> dict:
	"""Prepare one record dictionary for JSON persistence output."""
	pass


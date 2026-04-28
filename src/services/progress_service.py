"""Service layer: business logic for CRUD, search, sorting, and statistics."""

from typing import Any

from algorithms.searching import binary_search, linear_search
from algorithms.sorting import bubble_sort, insertion_sort
from pathlib import Path

from data.storage import initialize_database, load_records, save_records
from models.progress_entry import build_progress_entry, parse_progress_entry, serialize_progress_entry
from services.auth_service import current_user_id


Record = dict[str, Any]



db = Path(__file__).resolve().parents[2] / "data" / "progress_records.json"
records: list[Record] = []
initialized = False


def initialize_service(db_path: Path | None = None) -> None:
	"""Prepare JSON storage and load records into memory once."""
	global db, records, initialized
	if db_path is not None:
		db = db_path
	initialize_database(db)
	records[:] = [parse_progress_entry(record) for record in load_records(db)]
	initialized = True


def ensure_initialized() -> None:
	"""Lazy-load data if the service was not initialized by the CLI yet."""
	if not initialized:
		initialize_service()


def list_records() -> list[Record]:
	"""Return all records for the current user."""
	ensure_initialized()
	user_id = current_user_id() or 0
	return [record.copy() for record in records if record.get("user_id") == user_id]


def list_records_by_user(user_id: int | str) -> list[Record]:
	"""Return all records for a specific user by ID."""
	ensure_initialized()
	user_id_val = int(user_id) if isinstance(user_id, str) else user_id
	return [record.copy() for record in records if record.get("user_id") == user_id_val]


def create_record(payload: dict[str, Any]) -> Record:
	"""Create a new record with an auto-generated unique ID for the current user."""
	ensure_initialized()
	record_id = max((int(record["record_id"]) for record in records), default=0) + 1
	user_id = payload.get("user_id", current_user_id() or 0)
	record = build_progress_entry(
		record_id=record_id,
		user_id=user_id,
		client_name=payload["client_name"],
		email=payload["email"],
		phone=payload["phone"],
		record_date=payload["record_date"],
		weight_kg=payload["weight_kg"],
		body_fat_pct=payload["body_fat_pct"],
		daily_calories=payload["daily_calories"],
		password=payload["password"],
		notes=payload["notes"],
	)
	records.append(record)
	return record.copy()


def find_by_id(record_id: int) -> Record | None:
	"""Find and return one record by ID, or None when not found."""
	ensure_initialized()
	for record in records:
		if record["record_id"] == record_id:
			return record.copy()
	return None


def update_record(record_id: int, updates: dict[str, Any]) -> bool:
	"""Update one record by ID with validated field changes."""
	ensure_initialized()
	for index, record in enumerate(records):
		if record["record_id"] != record_id:
			continue

		updated_record = record.copy()
		updated_record.update(updates)
		records[index] = parse_progress_entry(updated_record)
		return True
	return False


def delete_record(record_id: int) -> bool:
	"""Remove one record by ID and report success/failure."""
	ensure_initialized()
	for index, record in enumerate(records):
		if record["record_id"] == record_id:
			del records[index]
			return True
	return False


def search_records(field: str, target: str | int | float, algorithm: str = "linear") -> list[Record]:
	"""Search records by field using the selected search algorithm."""
	ensure_initialized()
	records = list_records()
	if algorithm == "binary":
		ordered_records = insertion_sort(records, field=field, descending=False)
		return binary_search(ordered_records, field=field, target=target)
	return linear_search(records, field=field, target=target)


def sort_records(field: str, algorithm: str, descending: bool = False) -> list[Record]:
	"""Sort records by field using the selected manual algorithm and order."""
	ensure_initialized()
	records = list_records()
	if algorithm == "bubble":
		return bubble_sort(records, field=field, descending=descending)
	if algorithm == "insertion":
		return insertion_sort(records, field=field, descending=descending)
	raise ValueError("Unknown sorting algorithm.")


def compute_statistics() -> dict[str, int | float]:
	"""Compute totals, averages, min, and max values for reporting."""
	ensure_initialized()
	records = list_records()
	if not records:
		return {
			"count": 0,
			"avg_weight": 0.0,
			"avg_body_fat": 0.0,
			"min_weight": 0.0,
			"max_weight": 0.0,
			"total_calories": 0,
		}

	weights = [float(record["weight_kg"]) for record in records]
	body_fats = [float(record["body_fat_pct"]) for record in records]
	calories = [int(record["daily_calories"]) for record in records]

	return {
		"count": len(records),
		"avg_weight": sum(weights) / len(weights),
		"avg_body_fat": sum(body_fats) / len(body_fats),
		"min_weight": min(weights),
		"max_weight": max(weights),
		"total_calories": sum(calories),
	}


def filter_weight_range(minimum: float, maximum: float) -> list[Record]:
	"""Return records whose weight value is within the given range."""
	ensure_initialized()
	return [record for record in list_records() if minimum <= float(record["weight_kg"]) <= maximum]


def save_state() -> bool:
	"""Persist the current in-memory records to JSON."""
	ensure_initialized()
	return save_records(db, [serialize_progress_entry(record) for record in records])

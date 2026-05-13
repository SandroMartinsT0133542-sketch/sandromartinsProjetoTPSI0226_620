"""Service layer: business logic for CRUD, search, sorting, and statistics."""

from pathlib import Path
from typing import Any, cast

try:
	from algorithms import binary_search, linear_search, bubble_sort, insertion_sort, merge_sort
	from store import initialize_database, load_records, save_records
	from models import build_progress_entry, parse_progress_entry, serialize_progress_entry
	from services.auth_service import current_user_id
except ModuleNotFoundError:
	from src.algorithms import binary_search, linear_search, bubble_sort, insertion_sort, merge_sort
	from src.store import initialize_database, load_records, save_records
	from src.models import build_progress_entry, parse_progress_entry, serialize_progress_entry
	from src.services.auth_service import current_user_id

Record = dict[str, Any]

progress_state: dict[str, list[Record] | bool | Path] = {
	"db": Path(__file__).resolve().parents[2] / "data" / "progress_records.json",
	"records": [],
	"initialized": False,
}


def initialize_service(db_path: Path | None = None) -> None:
	"""Prepare JSON storage and load records into memory once."""
	if db_path is not None:
		progress_state["db"] = db_path
	db: Path = cast(Path, progress_state["db"])
	initialize_database(db)
	progress_state["records"] = [parse_progress_entry(record) for record in load_records(db)]
	progress_state["initialized"] = True


def ensure_initialized() -> None:
	"""Lazy-load data if the service was not initialized by the CLI yet."""
	if not progress_state["initialized"]:
		initialize_service()


def list_records() -> list[Record]:
	"""Return all records for the current user."""
	ensure_initialized()
	records: list[Record] = cast(list[Record], progress_state["records"])
	user_id = current_user_id() or 0
	return [record.copy() for record in records if record.get("user_id") == user_id]


def list_records_by_user(user_id: int | str) -> list[Record]:
	"""Return all records for a specific user by ID."""
	ensure_initialized()
	records: list[Record] = cast(list[Record], progress_state["records"])
	user_id_val = int(user_id) if isinstance(user_id, str) else user_id
	return [record.copy() for record in records if record.get("user_id") == user_id_val]


def create_record(payload: Record) -> Record:
	"""Create a new record with an auto-generated unique ID for the current user."""
	ensure_initialized()
	records = cast(list[Record], progress_state["records"])
	record_id = max((int(record["record_id"]) for record in records), default=0) + 1
	user_id_value = payload.get("user_id", current_user_id() or 0)
	active_user_id = int(user_id_value) if isinstance(user_id_value, str) else int(user_id_value)
	record = build_progress_entry(
		record_id=record_id,
		user_id= active_user_id,
		record_date=payload["record_date"],
		weight_kg=cast(float, payload["weight_kg"]),
		body_fat_pct=cast(float, payload["body_fat_pct"]),
		daily_calories=cast(int, payload["daily_calories"]),
		notes=cast(str, payload["notes"]),
	)
	records.append(record)
	return record.copy()


def find_by_id(record_id: int, user_id: int | str | None = None) -> Record | None:
	"""Find and return one record by ID, or None when not found."""
	ensure_initialized()
	user_id_value = current_user_id() if user_id is None else (int(user_id) if isinstance(user_id, str) else user_id)
	for record in cast(list[Record], progress_state["records"]):
		if record["record_id"] == record_id and (user_id_value is None or record.get("user_id") == user_id_value):
			return record.copy()
	return None


def update_record(record_id: int, updates: Record, user_id: int | str | None = None) -> bool:
	"""Update one record by ID with validated field changes."""
	ensure_initialized()
	records: list[Record] = cast(list[Record], progress_state["records"])
	user_id_value = current_user_id() if user_id is None else (int(user_id) if isinstance(user_id, str) else user_id)
	for index, record in enumerate(records):
		if record["record_id"] != record_id:
			continue
		if user_id_value is not None and record.get("user_id") != user_id_value:
			continue

		updated_record = record.copy()
		updated_record.update(updates)
		records[index] = parse_progress_entry(updated_record)
		return True
	return False


def delete_record(record_id: int, user_id: int | str | None = None) -> bool:
	"""Remove one record by ID and report success/failure."""
	ensure_initialized()
	records: list[Record] = cast(list[Record], progress_state["records"])
	user_id_value = current_user_id() if user_id is None else (int(user_id) if isinstance(user_id, str) else user_id)
	for index, record in enumerate(records):
		if record["record_id"] == record_id and (user_id_value is None or record.get("user_id") == user_id_value):
			del records[index]
			return True
	return False


def _resolve_field_name(field: str) -> str:
	"""Map human-friendly field names to record keys."""
	normalized = field.strip().casefold().replace(" ", "_")
	aliases = {
		"id": "record_id",
		"recordid": "record_id",
		"record_id": "record_id",
		"date": "record_date",
		"record_date": "record_date",
		"weight": "weight_kg",
		"weight_kg": "weight_kg",
		"body_fat": "body_fat_pct",
		"body_fat_pct": "body_fat_pct",
		"calories": "daily_calories",
		"daily_calories": "daily_calories",
		"notes": "notes",
	}
	return aliases.get(normalized, normalized)


def search_records(
	field: str,
	target: str | int | float,
	algorithm: str = "linear",
	operator: str = "equals",
	target_max: str | int | float | None = None,
	records: list[Record] | None = None,
) -> list[Record]:
	"""Search records by field using the selected search algorithm and operator.
	
	Args:
	    field: The record field to search in
	    target: Primary search value (or min for 'between')
	    algorithm: 'linear' or 'binary'
	    operator: 'equals', 'like', 'greater', 'less', 'between', 'any'
	    target_max: Maximum value for 'between' operator
	    records: Optional pre-filtered records; defaults to current user's records
	
	Returns:
	    List of matching records
	"""
	ensure_initialized()
	search_field = _resolve_field_name(field)
	search_space = [record.copy() for record in records] if records is not None else list_records()
	if algorithm == "binary":
		# Binary search requires sorted data; fall back to linear for incompatible operators
		if operator in ("like", "any"):
			return linear_search(search_space, field=search_field, target=target, operator=operator, target_max=target_max)
		ordered_records = insertion_sort(search_space, field=search_field, descending=False)
		return binary_search(ordered_records, field=search_field, target=target, operator=operator, target_max=target_max) # type: ignore
	return linear_search(search_space, field=search_field, target=target, operator=operator, target_max=target_max) # type: ignore


def sort_records(
	field: str,
	algorithm: str,
	descending: bool = False,
	records: list[Record] | None = None,
) -> list[Record]:
	"""Sort records by field using the selected manual algorithm and order."""
	ensure_initialized()
	sort_field = _resolve_field_name(field)
	sort_space = [record.copy() for record in records] if records is not None else list_records()
	if algorithm == "bubble":
		return bubble_sort(sort_space, field=sort_field, descending=descending)
	if algorithm == "insertion":
		return insertion_sort(sort_space, field=sort_field, descending=descending)
	if algorithm == "merge":
		return merge_sort(sort_space, field=sort_field, descending=descending)
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


def _filter_numeric_range(
	field: str,
	minimum: float,
	maximum: float,
	records: list[Record] | None = None,
) -> list[Record]:
	"""Return records whose numeric field falls inside the given range."""
	ensure_initialized()
	filter_field = _resolve_field_name(field)
	search_space = records if records is not None else list_records()
	filtered: list[Record] = []
	for record in search_space:
		try:
			value = float(record.get(filter_field, 0))
		except (TypeError, ValueError):
			continue
		if minimum <= value <= maximum:
			filtered.append(record.copy())
	return filtered


def filter_weight_range(minimum: float, maximum: float, records: list[Record] | None = None) -> list[Record]:
	"""Return records whose weight value is within the given range."""
	return _filter_numeric_range("weight_kg", minimum, maximum, records=records)


def filter_body_fat_range(minimum: float, maximum: float, records: list[Record] | None = None) -> list[Record]:
	"""Return records whose body-fat percentage is within the given range."""
	return _filter_numeric_range("body_fat_pct", minimum, maximum, records=records)


def filter_calories_range(minimum: float, maximum: float, records: list[Record] | None = None) -> list[Record]:
	"""Return records whose daily calories fall within the given range."""
	return _filter_numeric_range("daily_calories", minimum, maximum, records=records)


def save_state() -> bool:
	"""Persist the current in-memory records to JSON."""
	ensure_initialized()
	db: Path = cast(Path, progress_state["db"])
	records: list[Record] = cast(list[Record], progress_state["records"])
	return save_records(db, [serialize_progress_entry(record) for record in records])

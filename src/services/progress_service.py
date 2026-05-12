"""Service layer: business logic for CRUD, search, sorting, and statistics."""

from json import JSONDecodeError, loads
from typing import Any, cast

from algorithms.searching import binary_search, linear_search
from algorithms.sorting import bubble_sort, insertion_sort
from pathlib import Path

from data.storage import initialize_database, save_records
from models.progress_entry import build_progress_entry, parse_progress_entry, serialize_progress_entry
import services.auth_service as auth_service

Record = dict[str, str | int | float]
UserBucket = dict[str, Any]

progress_state: dict[str, list[Record] | bool | Path] = {
	"db": Path(__file__).resolve().parents[2] / "data" / "progress_records.json",
	"records": [],
	"initialized": False,
}


def _load_progress_records(db: Path) -> list[Record]:
	"""Load records from legacy flat JSON or the new per-user bucket structure."""
	try:
		if not db.exists():
			initialize_database(db)
			return []

		raw_data = db.read_text(encoding="utf-8").strip()
		if not raw_data:
			return []

		loaded_data = loads(raw_data)
		if isinstance(loaded_data, list):
			if loaded_data and all(isinstance(item, dict) and "records" in item for item in loaded_data):
				records: list[Record] = []
				for bucket in loaded_data:
					user_id = bucket.get("user_id", 0)
					for item in bucket.get("records", []):
						if not isinstance(item, dict):
							continue
						merged = dict(item)
						merged.setdefault("user_id", user_id)
						records.append(parse_progress_entry(merged))
				return records

			return [parse_progress_entry(item) for item in loaded_data if isinstance(item, dict)]

		if isinstance(loaded_data, dict):
			records = []
			for user_key, bucket in loaded_data.items():
				if not isinstance(bucket, dict):
					continue
				bucket_user_id = bucket.get("user_id", user_key)
				for item in bucket.get("records", []):
					if not isinstance(item, dict):
						continue
					merged = dict(item)
					merged.setdefault("user_id", bucket_user_id)
					records.append(parse_progress_entry(merged))
			return records

		return []
	except (OSError, JSONDecodeError, ValueError, TypeError) as error:
		print(f"[Warning] Could not load progress records: {error}")
		return []


def _group_records_by_user(records: list[Record]) -> list[UserBucket]:
	"""Convert flat in-memory records into the persisted per-user bucket format."""
	buckets: dict[int, UserBucket] = {}
	for record in records:
		user_id = int(record.get("user_id", 0))
		bucket = buckets.setdefault(user_id, {"user_id": user_id, "records": []})
		bucket["records"].append(serialize_progress_entry(record))
	return [buckets[user_id] for user_id in sorted(buckets)]


def initialize_service(db_path: Path | None = None) -> None:
	"""Prepare JSON storage and load records into memory once."""
	if db_path is not None:
		progress_state["db"] = db_path
	db: Path = cast(Path, progress_state["db"])
	initialize_database(db)
	progress_state["records"] = _load_progress_records(db)
	progress_state["initialized"] = True


def ensure_initialized() -> None:
	"""Lazy-load data if the service was not initialized by the CLI yet."""
	if not progress_state["initialized"]:
		initialize_service()


def list_records() -> list[Record]:
	"""Return all records for the current user."""
	ensure_initialized()
	records: list[Record] = cast(list[Record], progress_state["records"])
	user_id = auth_service.current_user_id() or 0
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
	user_id = int(payload.get("user_id", auth_service.current_user_id() or 0))

	record = build_progress_entry(
		record_id=record_id,
		user_id=user_id,
		record_date=cast(str, payload["record_date"]),
		weight_kg=cast(float, payload["weight_kg"]),
		body_fat_pct=cast(float, payload["body_fat_pct"]),
		daily_calories=cast(int, payload["daily_calories"]),
		notes=cast(str, payload.get("notes", "")),
	)
	records.append(record)
	return record.copy()


def find_by_id(record_id: int) -> Record | None:
	"""Find and return one record by ID, or None when not found."""
	ensure_initialized()
	for record in cast(list[Record], progress_state["records"]):
		if record["record_id"] == record_id:
			return record.copy()
	return None


def update_record(record_id: int, updates: Record) -> bool:
	"""Update one record by ID with validated field changes."""
	ensure_initialized()
	records: list[Record] = cast(list[Record], progress_state["records"])
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
	records: list[Record] = cast(list[Record], progress_state["records"])
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
	db: Path = cast(Path, progress_state["db"])
	records: list[Record] = cast(list[Record], progress_state["records"])
	return save_records(db, _group_records_by_user(records))

"""Persistence helpers for loading and saving JSON data."""

from json import JSONDecodeError, dumps, loads
from pathlib import Path
from typing import Any


Record = dict[str, Any]



def initialize_database(db_path: Path) -> None:
	"""Create the JSON storage file if it does not exist."""
	db_path.parent.mkdir(parents=True, exist_ok=True)
	if not db_path.exists():
		db_path.write_text("[]", encoding="utf-8")


def load_records(db_path: Path) -> list[Record]:
	"""Load records from JSON, returning an empty list on failure."""
	try:
		if not db_path.exists():
			initialize_database(db_path)
			return []

		raw_data = db_path.read_text(encoding="utf-8").strip()
		if not raw_data:
			return []

		loaded_data = loads(raw_data)
		if not isinstance(loaded_data, list):
			return []
		return [dict(record) for record in loaded_data if isinstance(record, dict)]
	except (OSError, JSONDecodeError, ValueError, TypeError) as error:
		print(f"[Warning] Could not load records: {error}")
		return []


def save_records(db_path: Path, records: list[Record]) -> bool:
	"""Persist records to JSON and report success/failure."""
	try:
		initialize_database(db_path)
		db_path.write_text(dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
		return True
	except OSError as error:
		print(f"[Error] Could not save records: {error}")
		return False


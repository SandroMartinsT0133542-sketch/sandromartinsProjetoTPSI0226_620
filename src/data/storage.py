"""Persistence helpers for loading and saving JSON data."""

from pathlib import Path


def load_records(file_path: Path) -> list[dict]:
	"""Load records from JSON file, returning an empty list on failure."""
	pass


def save_records(file_path: Path, records: list[dict]) -> bool:
	"""Persist records to JSON file and report success/failure."""
	pass


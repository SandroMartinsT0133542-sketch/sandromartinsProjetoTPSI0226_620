"""Persistence helpers for loading and saving JSON data."""

from json import JSONDecodeError, dumps, loads
from pathlib import Path
from typing import Any, cast

Record = dict[str, int | float | str]


def initialize_database(db_path: Path) -> None:
    """Ensure the JSON file and parent directories exist.

    Args:
        db_path: Path to the JSON file to initialize.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        db_path.write_text("[]", encoding="utf-8")


def load_records(db_path: Path) -> list[Record]:
    """Read JSON from `db_path` and return a flat list of records.

    Args:
        db_path: Path to the JSON file to read.

    Returns:
        A flat list of record dictionaries. For `progress_records.json`, grouped
        user records are flattened into a single list.
    """
    try:
        if not db_path.exists():
            initialize_database(db_path)
            return []

        raw_data = db_path.read_text(encoding="utf-8").strip()
        if not raw_data:
            return []

        loaded_data: Any = loads(raw_data)
        if not isinstance(loaded_data, list):
            return []

        if db_path.name == "progress_records.json":
            records: list[Record] = []
            for raw_item in cast(list[Any], loaded_data):
                if not isinstance(raw_item, dict):
                    continue
                item = cast(dict[str, Any], raw_item)
                group_records = item.get("records")
                if not isinstance(group_records, list):
                    continue
                for raw_record_item in cast(list[Any], group_records):
                    if not isinstance(raw_record_item, dict):
                        continue
                    raw_record = cast(dict[str, Any], raw_record_item)
                    typed_record: Record = {
                        key: value
                        for key, value in raw_record.items()
                        if isinstance(value, (str, int, float))
                    }
                    if typed_record:
                        records.append(typed_record)
            return records

        records: list[Record] = []
        for raw_item in cast(list[Any], loaded_data):
            if not isinstance(raw_item, dict):
                continue
            item = cast(dict[str, Any], raw_item)
            typed_record: Record = {
                key: value
                for key, value in item.items()
                if isinstance(value, (str, int, float))
            }
            if typed_record:
                records.append(typed_record)
        return records
    except (OSError, JSONDecodeError, ValueError, TypeError) as error:
        print(f"[Warning] Could not load records: {error}")
        return []


def save_records(db_path: Path, records: list[Record]) -> bool:
    """Write `records` to `db_path` in JSON format.

    For `progress_records.json` the function groups records by `user_id` and
    persists the grouped structure. For other files it writes the flat list.

    Args:
        db_path: Path to write the JSON data.
        records: List of record dictionaries to persist.

    Returns:
        True on success, False on failure.
    """
    try:
        initialize_database(db_path)
        if db_path.name == "progress_records.json":
            grouped: dict[int, list[Record]] = {}
            for record in records:
                user_id_raw = record.get("user_id", 0)
                try:
                    user_id = int(user_id_raw)
                except (TypeError, ValueError):
                    user_id = 0
                grouped.setdefault(user_id, []).append(record)

            payload: list[dict[str, Any]] = []
            for user_id, user_records in grouped.items():
                payload.append({"user_id": user_id, "records": user_records})
            db_path.write_text(dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            db_path.write_text(dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError as error:
        print(f"[Error] Could not save records: {error}")
        return False


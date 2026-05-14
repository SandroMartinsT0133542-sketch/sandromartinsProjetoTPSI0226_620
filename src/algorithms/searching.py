"""Search algorithms used by the service layer.

Helpers are module-level and intentionally public (no leading underscore).
Each function includes its own docstring that explains behavior and complexity.
"""

from typing import Any, Literal


def to_numeric(value: object) -> float | None:
	"""Convert supported values to float for consistent numeric comparison.

	This helper accepts booleans, ints/floats and strings that parse as numbers.
	Empty strings and values that cannot be converted return ``None``.
	"""
	if isinstance(value, bool):
		return float(value)
	if isinstance(value, (int, float)):
		return float(value)
	if isinstance(value, str):
		raw = value.strip()
		if raw == "":
			return None
		try:
			return float(raw)
		except ValueError:
			return None
	return None


def search_key(value: object) -> tuple[int, float | str]:
	"""Normalize one raw value into a deterministic search key.

	Returns a tuple (priority, normalized_value) to allow consistent
	comparisons across numbers, strings and None.
	"""
	numeric = to_numeric(value)
	if numeric is not None:
		return (0, numeric)
	if value is None:
		return (2, "")
	return (1, str(value).strip().casefold())


def _matches_operator(record_value: Any, operator: str, target: object, target_max: object | None = None) -> bool:
	"""Check if a record value matches the given operator condition.
	
	Args:
	    record_value: The value from the record field
	    operator: One of 'equals', 'like', 'greater', 'less', 'between', 'any'
	    target: Primary target value (or min for 'between')
	    target_max: Maximum value for 'between' operator
	
	Returns:
	    True if the record value matches the condition, False otherwise
	"""
	if operator == "equals":
		record_key = search_key(record_value)
		target_key = search_key(target)
		return record_key == target_key
	
	elif operator == "like":
		if record_value is None:
			return False
		record_text = str(record_value).strip().casefold()
		target_text = str(target).strip().casefold()
		return bool(target_text and target_text in record_text)
	
	elif operator == "greater":
		record_num = to_numeric(record_value)
		target_num = to_numeric(target)
		if record_num is None or target_num is None:
			return False
		return record_num > target_num
	
	elif operator == "less":
		record_num = to_numeric(record_value)
		target_num = to_numeric(target)
		if record_num is None or target_num is None:
			return False
		return record_num < target_num
	
	elif operator == "between":
		record_num = to_numeric(record_value)
		target_min = to_numeric(target)
		target_max_num = to_numeric(target_max) if target_max is not None else None
		if record_num is None or target_min is None or target_max_num is None:
			return False
		return target_min <= record_num <= target_max_num
	
	elif operator == "any":
		if record_value is None:
			return False
		# target is expected to be a comma-separated string
		values = [v.strip().casefold() for v in str(target).split(",")]
		record_text = str(record_value).strip().casefold()
		return record_text in values or any(v in record_text for v in values if v)
	
	return False


def _copy_records(records: list[dict[str, Any]], start: int, end: int) -> list[dict[str, Any]]:
	"""Return copies of the records within the inclusive index range."""
	return [records[index].copy() for index in range(start, end + 1)]


def _binary_search_equals(records: list[dict[str, Any]], field: str, target: object) -> list[dict[str, Any]]:
	"""Return all records that match a value exactly."""
	target_key = search_key(target)
	low = 0
	high = len(records) - 1
	found_index = -1

	while low <= high:
		middle = (low + high) // 2
		middle_key = search_key(records[middle].get(field))
		if middle_key == target_key:
			found_index = middle
			break
		if middle_key < target_key:
			low = middle + 1
		else:
			high = middle - 1

	if found_index < 0:
		return []

	start = found_index
	while start > 0 and search_key(records[start - 1].get(field)) == target_key:
		start -= 1

	end = found_index
	last_index = len(records) - 1
	while end < last_index and search_key(records[end + 1].get(field)) == target_key:
		end += 1

	return _copy_records(records, start, end)


def _binary_search_greater(records: list[dict[str, Any]], field: str, target: object) -> list[dict[str, Any]]:
	"""Return all records whose numeric value is greater than the target."""
	target_num = to_numeric(target)
	if target_num is None:
		return []

	low = 0
	high = len(records) - 1
	first_greater_index = len(records)

	while low <= high:
		middle = (low + high) // 2
		middle_num = to_numeric(records[middle].get(field))
		if middle_num is None:
			low = middle + 1
			continue
		if middle_num > target_num:
			first_greater_index = middle
			high = middle - 1
		else:
			low = middle + 1

	if first_greater_index >= len(records):
		return []
	return _copy_records(records, first_greater_index, len(records) - 1)


def _binary_search_less(records: list[dict[str, Any]], field: str, target: object) -> list[dict[str, Any]]:
	"""Return all records whose numeric value is less than the target."""
	target_num = to_numeric(target)
	if target_num is None:
		return []

	low = 0
	high = len(records) - 1
	last_less_index = -1

	while low <= high:
		middle = (low + high) // 2
		middle_num = to_numeric(records[middle].get(field))
		if middle_num is None:
			high = middle - 1
			continue
		if middle_num < target_num:
			last_less_index = middle
			low = middle + 1
		else:
			high = middle - 1

	if last_less_index < 0:
		return []
	return _copy_records(records, 0, last_less_index)


def _binary_search_between(
	records: list[dict[str, Any]],
	field: str,
	target: object,
	target_max: object | None,
) -> list[dict[str, Any]]:
	"""Return all records whose numeric value falls within the target range."""
	target_min = to_numeric(target)
	target_max_num = to_numeric(target_max) if target_max is not None else None
	if target_min is None or target_max_num is None:
		return []

	low = 0
	high = len(records) - 1
	first_ge_index = len(records)

	while low <= high:
		middle = (low + high) // 2
		middle_num = to_numeric(records[middle].get(field))
		if middle_num is None:
			low = middle + 1
			continue
		if middle_num >= target_min:
			first_ge_index = middle
			high = middle - 1
		else:
			low = middle + 1

	low = 0
	high = len(records) - 1
	last_le_index = -1

	while low <= high:
		middle = (low + high) // 2
		middle_num = to_numeric(records[middle].get(field))
		if middle_num is None:
			high = middle - 1
			continue
		if middle_num <= target_max_num:
			last_le_index = middle
			low = middle + 1
		else:
			high = middle - 1

	if first_ge_index > last_le_index or first_ge_index >= len(records) or last_le_index < 0:
		return []
	return _copy_records(records, first_ge_index, last_le_index)



def linear_search(
	records: list[dict[str, Any]],
	field: str,
	target: object,
	operator: Literal["equals", "like", "greater", "less", "between", "any"] = "equals",
	target_max: object | None = None,
) -> list[dict[str, Any]]:
	"""Find records matching the provided operator condition.

	Args:
		records: List of record dictionaries to search.
		field: Record field/key to evaluate.
		target: Primary comparison value (or minimum for 'between').
		operator: Comparison mode: 'equals', 'like', 'greater', 'less', 'between', or 'any'.
		target_max: Maximum value for 'between' operator (required for 'between').

	Returns:
		A list of matching record copies.
	"""
	matches: list[dict[str, Any]] = []

	for record in records:
		value = record.get(field)
		if _matches_operator(value, operator, target, target_max):
			matches.append(record.copy())

	return matches


def binary_search(
	records: list[dict[str, Any]],
	field: str,
	target: object,
	operator: Literal["equals", "like", "greater", "less", "between", "any"] = "equals",
	target_max: object | None = None,
) -> list[dict[str, Any]]:
	"""Search sorted records using the provided operator.

	Args:
		records: Records sorted by `field` (list of dicts).
		field: Field name used for sorting and comparison.
		target: Primary comparison value (or minimum for 'between').
		operator: Comparison mode: 'equals', 'like', 'greater', 'less', 'between', or 'any'.
		target_max: Maximum value for 'between' operator.

	Returns:
		A list of matching record copies. For 'like' and 'any' the function falls back to a linear scan.
	"""
	if not records:
		return []

	if operator in ("like", "any"):
		return linear_search(records, field, target, operator, target_max)

	if operator == "equals":
		return _binary_search_equals(records, field, target)

	if operator == "greater":
		return _binary_search_greater(records, field, target)

	if operator == "less":
		return _binary_search_less(records, field, target)

	if operator == "between":
		return _binary_search_between(records, field, target, target_max)

	return []

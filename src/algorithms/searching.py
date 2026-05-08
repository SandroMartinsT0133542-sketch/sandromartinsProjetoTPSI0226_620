"""Search algorithms used by the service layer.

Helpers are module-level and intentionally public (no leading underscore).
Each function includes its own docstring that explains behavior and complexity.
"""

from typing import Any


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



def linear_search(records: list[dict], field: str, target: object) -> list[dict]:
	"""Scan all records sequentially and return exact matches.
	
	**Time Complexity:** O(n) where n is the number of records
	**Space Complexity:** O(m) where m is the number of matches
	**Best for:** Unsorted data or when full scan is necessary
	
	This algorithm examines each record in order to find matches. Type normalization
	ensures consistent comparison across mixed data types. Multiple matches are
	supported (important for duplicate values in the field).
	
	Args:
	    records: List of dictionaries to search
	    field: The key/field name to search in each record
	    target: The value to search for (matched via normalized key comparison)
	
	Returns:
	    list: List of matching records (copies, not references)
	
	Examples:
	    >>> data = [
	    ...     {"id": "1", "score": "90"},
	    ...     {"id": "2", "score": "90"},
	    ...     {"id": "3", "score": "85"}
	    ... ]
	    >>> linear_search(data, "score", 90)
	    [{"id": "1", "score": "90"}, {"id": "2", "score": "90"}]
	    >>> linear_search(data, "score", "not_found")
	    []
	"""
	target_key = search_key(target)
	matches: list[dict[str, Any]] = []

	for record in records:
		if search_key(record.get(field)) == target_key:
			matches.append(record.copy())

	return matches


def binary_search(records: list[dict], field: str, target: object) -> list[dict]:
	"""Search in a field-sorted list and return all matching records.
	
	**Time Complexity:** O(log n + m) where n is number of records, m is matches
	**Space Complexity:** O(m) where m is the number of matches
	**Best for:** Large sorted datasets where performance is critical
	**Requirement:** Records must be sorted by the search field
	
	Uses binary search to locate the first match, then expands linearly to capture
	all consecutive duplicates. This is much faster than linear search on large
	sorted datasets, though it requires the input to be pre-sorted.
	
	Args:
	    records: List of dictionaries, sorted by the search field
	    field: The key/field name to search in each record
	    target: The value to search for
	
	Returns:
	    list: All matching records in original order (copies, not references)
	
	Examples:
	    >>> data = [
	    ...     {"id": "1", "value": "10"},
	    ...     {"id": "2", "value": "20"},
	    ...     {"id": "3", "value": "20"},
	    ...     {"id": "4", "value": "30"}
	    ... ]
	    >>> binary_search(data, "value", "20")
	    [{"id": "2", "value": "20"}, {"id": "3", "value": "20"}]
	"""
	if not records:
		return []

	target_key = search_key(target)
	low = 0
	high = len(records) - 1
	found_index = -1

	# Binary search for any match
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

	# Expand left to find the first matching record
	start = found_index
	while start > 0 and search_key(records[start - 1].get(field)) == target_key:
		start -= 1

	# Expand right to find the last matching record
	end = found_index
	last_index = len(records) - 1
	while end < last_index and search_key(records[end + 1].get(field)) == target_key:
		end += 1

	return [records[index].copy() for index in range(start, end + 1)]

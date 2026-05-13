"""Sorting algorithms used by the service layer.

Helpers are public (no leading underscore) and documented per-function.
"""

from typing import Any


def to_numeric(value: object) -> float | None:
	"""Convert supported values to float for consistent numeric comparison.

	Accepts booleans, ints/floats, and numeric strings. Returns ``None`` for
	empty strings or values that cannot be converted.
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


def sort_key(record: dict[str, Any], field: str) -> tuple[int, float | str]:
	"""Normalize one record value into a deterministic key.

	Returns (priority, normalized_value) where numbers come first, then
	strings (case-folded), and None last.
	"""
	value = record.get(field)
	numeric = to_numeric(value)
	if numeric is not None:
		return (0, numeric)
	if value is None:
		return (2, "")
	return (1, str(value).strip().casefold())


def should_swap(
	left: tuple[int, float | str],
	right: tuple[int, float | str],
	descending: bool,
) -> bool:
	"""Return whether two adjacent keys should be swapped.

	When ``descending`` is False the comparison is ascending (swap if left > right).
	When ``descending`` is True the comparison is inverted.
	"""
	return left < right if descending else left > right


def bubble_sort(records: list[dict[str, Any]], field: str, descending: bool = False) -> list[dict[str, Any]]:
	"""Sort records using bubble sort.

	Args:
		records: List of records (dicts) to sort.
		field: Field name to sort by.
		descending: If True, sort in descending order.

	Returns:
		A new list with records sorted by the specified field.
	"""
	ordered = [record.copy() for record in records]
	total = len(ordered)
	if total < 2:
		return ordered

	# Bubble sort with early termination optimization
	for end in range(total - 1, 0, -1):
		swapped = False
		for index in range(end):
			left_key = sort_key(ordered[index], field)
			right_key = sort_key(ordered[index + 1], field)
			if should_swap(left_key, right_key, descending):
				ordered[index], ordered[index + 1] = ordered[index + 1], ordered[index]
				swapped = True
		# If no swaps occurred, data is sorted
		if not swapped:
			break
	return ordered


def insertion_sort(records: list[dict[str, Any]], field: str, descending: bool = False) -> list[dict[str, Any]]:
	"""Sort records using insertion sort.

	Args:
		records: List of records (dicts) to sort.
		field: Field name to sort by.
		descending: If True, sort in descending order.

	Returns:
		A new list with records sorted by the specified field.
	"""
	ordered = [record.copy() for record in records]
	total = len(ordered)
	if total < 2:
		return ordered

	# Insert each element into its correct position among sorted elements
	for index in range(1, total):
		current = ordered[index]
		current_key = sort_key(current, field)
		position = index - 1

		# Shift larger/smaller elements right to make space
		while position >= 0:
			position_key = sort_key(ordered[position], field)
			if not should_swap(position_key, current_key, descending):
				break
			ordered[position + 1] = ordered[position]
			position -= 1
		ordered[position + 1] = current

	return ordered
def merge_sort(records: list[dict[str, Any]], field: str, descending: bool = False) -> list[dict[str, Any]]:
	"""Sort records using merge sort.

	Args:
		records: List of records (dicts) to sort.
		field: Field name to sort by.
		descending: If True, sort in descending order.

	Returns:
		A new list with records sorted by the specified field.
	"""
	ordered = [record.copy() for record in records]
	
	def _merge(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[dict[str, Any]]:
		"""Merge two sorted lists into one."""
		result: list[dict[str, Any]] = []
		i = j = 0
		
		while i < len(left) and j < len(right):
			left_key = sort_key(left[i], field)
			right_key = sort_key(right[j], field)
			
			if should_swap(left_key, right_key, descending):
				result.append(right[j])
				j += 1
			else:
				result.append(left[i])
				i += 1
		
		# Add remaining elements
		result.extend(left[i:])
		result.extend(right[j:])
		return result
	
	def _merge_sort_impl(arr: list[dict[str, Any]]) -> list[dict[str, Any]]:
		"""Recursive merge sort implementation."""
		if len(arr) <= 1:
			return arr
		
		mid = len(arr) // 2
		left = _merge_sort_impl(arr[:mid])
		right = _merge_sort_impl(arr[mid:])
		return _merge(left, right)
	
	return _merge_sort_impl(ordered)


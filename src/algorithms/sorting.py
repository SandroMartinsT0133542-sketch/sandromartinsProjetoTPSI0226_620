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


def quick_sort(records: list[dict[str, Any]], field: str, descending: bool = False) -> list[dict[str, Any]]:
	"""Sort records using quick sort.

	Args:
		records: List of records (dicts) to sort.
		field: Field name to sort by.
		descending: If True, sort in descending order.

	Returns:
		A new list with records sorted by the specified field.
	"""
	ordered = [record.copy() for record in records]
	
	def _partition(arr: list[dict[str, Any]], low: int, high: int) -> int:
		"""Partition around pivot using median-of-three for better performance."""
		if high - low > 2:
			# Median-of-three pivot selection
			first = sort_key(arr[low], field)
			mid = sort_key(arr[(low + high) // 2], field)
			last = sort_key(arr[high], field)
			
			if first > mid:
				first, mid = mid, first
			if mid > last:
				mid, last = last, mid
			if first > mid:
				mid = first
			
			pivot_idx = (low + high) // 2 if mid == sort_key(arr[(low + high) // 2], field) else (low if mid == sort_key(arr[low], field) else high)
		else:
			pivot_idx = low
		
		# Move pivot to end
		arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
		pivot = sort_key(arr[high], field)
		
		i = low
		for j in range(low, high):
			current = sort_key(arr[j], field)
			should_left = current < pivot if not descending else current > pivot
			if should_left:
				arr[i], arr[j] = arr[j], arr[i]
				i += 1
		
		arr[i], arr[high] = arr[high], arr[i]
		return i
	
	def _quick_sort_impl(arr: list[dict[str, Any]], low: int, high: int) -> None:
		"""Recursive quick sort implementation."""
		if low < high:
			partition_idx = _partition(arr, low, high)
			_quick_sort_impl(arr, low, partition_idx - 1)
			_quick_sort_impl(arr, partition_idx + 1, high)
	
	if len(ordered) > 1:
		_quick_sort_impl(ordered, 0, len(ordered) - 1)
	
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


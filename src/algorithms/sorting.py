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


def bubble_sort(records: list[dict], field: str, descending: bool = False) -> list[dict]:
	"""Sort records with bubble sort by selected field and order.
	
	**Time Complexity:** O(n²) average/worst case, O(n) best case (already sorted)
	**Space Complexity:** O(n) for the output list copy
	**Best for:** Small datasets, educational purposes, or nearly sorted data
	
	Bubble sort repeatedly steps through the list, compares adjacent pairs, and
	swaps them if they're in the wrong order. It has an optimization that stops
	early if a pass makes no swaps (data is sorted).
	
	Args:
	    records: List of dictionaries to sort
	    field: The field name to sort by
	    descending: If True, sort descending; otherwise ascending (default: False)
	
	Returns:
	    list: Sorted list of records (original not mutated)
	
	Examples:
	    >>> data = [{"name": "Bob", "age": "25"}, {"name": "Alice", "age": "30"}]
	    >>> bubble_sort(data, "age")
	    [{"name": "Bob", "age": "25"}, {"name": "Alice", "age": "30"}]
	    >>> bubble_sort(data, "age", descending=True)
	    [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
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


def insertion_sort(records: list[dict], field: str, descending: bool = False) -> list[dict]:
	"""Sort records with insertion sort by selected field and order.
	
	**Time Complexity:** O(n²) average/worst case, O(n) best case (already sorted)
	**Space Complexity:** O(n) for the output list copy
	**Best for:** Small datasets, nearly sorted data, or online sorting
	**Stability:** Stable (preserves order of equal elements)
	
	Insertion sort builds the sorted list one item at a time, inserting each element
	into its correct position among previously sorted elements. Efficient for small
	datasets and better than bubble sort in practice.
	
	Args:
	    records: List of dictionaries to sort
	    field: The field name to sort by
	    descending: If True, sort descending; otherwise ascending (default: False)
	
	Returns:
	    list: Sorted list of records (original not mutated)
	
	Examples:
	    >>> data = [{"id": "3"}, {"id": "1"}, {"id": "2"}]
	    >>> insertion_sort(data, "id")
	    [{"id": "1"}, {"id": "2"}, {"id": "3"}]
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


def quick_sort(records: list[dict], field: str, descending: bool = False) -> list[dict]:
	"""Sort records with quick sort by selected field and order.
	
	**Time Complexity:** O(n log n) average case, O(n²) worst case (sorted input)
	**Space Complexity:** O(log n) average case for recursion, O(n) worst case
	**Best for:** Large datasets, general-purpose sorting
	**Note:** Not stable (may reorder equal elements)
	
	Quk sort is a divide-and-conquer algorithm that partitions the list around
	a pivot and recursively sorts the partitions. Uses median-of-three pivot selection
	to avoid worst-case behavior on already-sorted data.ic
	
	Args:
	    records: List of dictionaries to sort
	    field: The field name to sort by
	    descending: If True, sort descending; otherwise ascending (default: False)
	
	Returns:
	    list: Sorted list of records (original not mutated)
	"""
	ordered = [record.copy() for record in records]
	
	def _partition(arr: list[dict], low: int, high: int) -> int:
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
			should_left = current < pivot if descending else current > pivot
			if should_left:
				arr[i], arr[j] = arr[j], arr[i]
				i += 1
		
		arr[i], arr[high] = arr[high], arr[i]
		return i
	
	def _quick_sort_impl(arr: list[dict], low: int, high: int) -> None:
		"""Recursive quick sort implementation."""
		if low < high:
			partition_idx = _partition(arr, low, high)
			_quick_sort_impl(arr, low, partition_idx - 1)
			_quick_sort_impl(arr, partition_idx + 1, high)
	
	if len(ordered) > 1:
		_quick_sort_impl(ordered, 0, len(ordered) - 1)
	
	return ordered


def merge_sort(records: list[dict], field: str, descending: bool = False) -> list[dict]:
	"""Sort records with merge sort by selected field and order.
	
	**Time Complexity:** O(n log n) guaranteed in all cases
	**Space Complexity:** O(n) additional space for merging
	**Best for:** Large datasets where guaranteed O(n log n) is needed
	**Stability:** Stable (preserves order of equal elements)
	
	Merge sort is a divide-and-conquer algorithm that divides the list in half,
	recursively sorts each half, and merges them. Slower than quick sort in practice
	due to higher constant factors and memory usage, but guarantees O(n log n).
	
	Args:
	    records: List of dictionaries to sort
	    field: The field name to sort by
	    descending: If True, sort descending; otherwise ascending (default: False)
	
	Returns:
	    list: Sorted list of records (original not mutated)
	"""
	ordered = [record.copy() for record in records]
	
	def _merge(left: list[dict], right: list[dict]) -> list[dict]:
		"""Merge two sorted lists into one."""
		result: list[dict] = []
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
	
	def _merge_sort_impl(arr: list[dict]) -> list[dict]:
		"""Recursive merge sort implementation."""
		if len(arr) <= 1:
			return arr
		
		mid = len(arr) // 2
		left = _merge_sort_impl(arr[:mid])
		right = _merge_sort_impl(arr[mid:])
		return _merge(left, right)
	
	return _merge_sort_impl(ordered)


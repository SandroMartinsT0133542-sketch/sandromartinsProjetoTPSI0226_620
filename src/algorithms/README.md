# Algorithms Module

This module provides manual implementations of core search and sort algorithms for the fitness management system. All algorithms handle data normalization internally to ensure consistent comparison across numeric, string, and mixed-type records.

## Overview

The algorithms module is split into two files:

- **`sorting.py`** – Implements three manual sorting algorithms: bubble sort, insertion sort, and merge sort.
- **`searching.py`** – Implements two manual search algorithms: linear search and binary search with support for multiple comparison operators.

Both modules share a **normalization pattern** to handle diverse data types reliably:
1. Convert numeric strings and values to floats for comparison
2. Prioritize numbers first, then strings (case-folded), then None/missing values
3. Ensure ascending/descending order is applied uniformly

---

## Data Normalization Workflow

### Key Concepts

**Normalization** ensures that comparisons work correctly regardless of data type:

#### Sorting: `sort_key(record, field)`
Converts any record field value into a deterministic tuple `(priority, value)`:
- **Priority 0**: Numeric values (numbers come first)
- **Priority 1**: String values (case-folded for case-insensitive comparison)
- **Priority 2**: None/missing (last in sort order)

Example:
```python
sort_key({"weight_kg": 75.5}, "weight_kg")     # Returns (0, 75.5)
sort_key({"notes": "Recovery"}, "notes")       # Returns (1, "recovery")
sort_key({"data": None}, "data")               # Returns (2, "")
```

#### Searching: `search_key(value)`
Converts a single value into the same tuple format as `sort_key`:
- Used to compare search targets with record values uniformly
- Supports exact match, substring search, numeric range comparisons

Example:
```python
search_key("weight_kg")        # User input like "Weight kg" is normalized
search_key(75.5)               # Numeric search targets remain numeric
search_key(None)               # Missing values normalized to (2, "")
```

#### Numeric Conversion: `to_numeric(value)`
Safely converts values to float:
- Returns `None` if value cannot be converted
- Handles booleans, integers, floats, and numeric strings
- Used as a pre-check before numeric comparisons

---

## Sorting Algorithms

### 1. Bubble Sort (`bubble_sort`)

**Description**: Repeatedly compares adjacent elements and swaps them if they are in the wrong order. Includes early termination when no swaps occur in a pass.

**Signature**:
```python
def bubble_sort(records: list[dict], field: str, descending: bool = False) -> list[dict]
```

**Complexity**:
- Time: O(n²) worst/average case, O(n) best case (sorted data)
- Space: O(1) auxiliary space (in-place swap)

**Workflow**:
1. Copy input records (preserves original)
2. For each position from end to start:
   - Compare adjacent pairs
   - Use `should_swap()` to decide swap direction (ascending/descending)
   - Stop early if no swaps occur in a pass (data is sorted)

**When to Use**: Educational purposes, nearly sorted data.

**Example**:
```python
records = [
    {"record_id": 1, "weight_kg": 80.5},
    {"record_id": 2, "weight_kg": 75.0},
    {"record_id": 3, "weight_kg": 82.3}
]
sorted_asc = bubble_sort(records, "weight_kg", descending=False)
sorted_desc = bubble_sort(records, "weight_kg", descending=True)
```

---

### 2. Insertion Sort (`insertion_sort`)

**Description**: Builds a sorted result by inserting each element into its correct position among already-sorted elements. Efficient for small datasets and nearly sorted data.

**Signature**:
```python
def insertion_sort(records: list[dict], field: str, descending: bool = False) -> list[dict]
```

**Complexity**:
- Time: O(n²) worst/average case, O(n) best case (sorted data)
- Space: O(1) auxiliary space (in-place insertion)

**Workflow**:
1. Copy input records
2. For each element starting from index 1:
   - Compare with preceding elements
   - Shift larger/smaller elements right (depending on order)
   - Insert current element into correct position

**When to Use**: Small datasets, nearly sorted data, online sorting (streaming).

**Example**:
```python
records = [
    {"name": "Alice", "weight_kg": 70},
    {"name": "Bob", "weight_kg": 85},
    {"name": "Charlie", "weight_kg": 75}
]
sorted_asc = insertion_sort(records, "weight_kg")
```

---

### 3. Merge Sort (`merge_sort`)

**Description**: Divide-and-conquer algorithm that recursively splits the list in half, sorts each half, and merges them back together. Stable and predictable performance.

**Signature**:
```python
def merge_sort(records: list[dict], field: str, descending: bool = False) -> list[dict]
```

**Complexity**:
- Time: O(n log n) all cases (consistent performance)
- Space: O(n) auxiliary space (temporary merge arrays)

**Workflow**:
1. Copy input records
2. Recursively split list in half until single elements remain
3. Merge sorted halves:
   - Compare elements from both halves
   - Use `should_swap()` to maintain order (ascending/descending)
   - Append remaining elements

**Helper Functions**:
- `_merge_sorted_lists(left, right, field, descending)` – Merges two sorted lists
- `_merge_sort_recursive(records, field, descending)` – Recursive split-and-merge

**When to Use**: Large datasets, when consistent O(n log n) performance is required, stable sort needed.

**Example**:
```python
large_dataset = [...]  # 10,000+ records
sorted_records = merge_sort(large_dataset, "body_fat_pct", descending=False)
```

---

## Searching Algorithms

### 1. Linear Search (`linear_search`)

**Description**: Iterates through all records sequentially, checking each against the search condition. No pre-sorting required.

**Signature**:
```python
def linear_search(
    records: list[dict],
    field: str,
    target: object,
    operator: str = "equals",
    target_max: object | None = None
) -> list[dict]
```

**Complexity**:
- Time: O(n) – must check every record
- Space: O(k) – k matching records

**Supported Operators**:
- `equals` – Exact match using normalized keys
- `like` – Substring search (case-insensitive)
- `greater` – Value > target (numeric only)
- `less` – Value < target (numeric only)
- `between` – target_min ≤ value ≤ target_max (numeric only)
- `any` – Value matches any in comma-separated target list

**Workflow**:
1. Initialize empty results list
2. For each record:
   - Check if field value matches operator condition
   - Use `_matches_operator()` helper for condition logic
   - Copy matching records to results
3. Return all matches

**When to Use**: Small datasets, unsorted data, complex/text-based searches.

**Example**:
```python
# Exact match
results = linear_search(records, "record_id", 5, operator="equals")

# Substring search
results = linear_search(records, "notes", "recovery", operator="like")

# Numeric range
results = linear_search(records, "weight_kg", 70, operator="greater")

# Between range
results = linear_search(records, "daily_calories", 2000, operator="between", target_max=2500)
```

---

### 2. Binary Search (`binary_search`)

**Description**: Efficient search on **pre-sorted** data that repeatedly halves the search space. Falls back to linear search for text-based operators.

**Signature**:
```python
def binary_search(
    records: list[dict],
    field: str,
    target: object,
    operator: str = "equals",
    target_max: object | None = None
) -> list[dict]
```

**Complexity**:
- Time: O(log n) for numeric operators, O(n) fallback for text-based
- Space: O(k) – k matching records
- **Prerequisite**: Records must be sorted by the search field

**Supported Operators**:
Same as linear search, but with performance characteristics:
- `equals` – O(log n) with boundary expansion
- `like` / `any` – Falls back to O(n) linear scan
- `greater` / `less` / `between` – O(log n) range queries

**Workflow**:

#### For `equals`:
1. Binary search for any matching element
2. Expand left to find first match
3. Expand right to find last match
4. Use `_binary_search_equals()` helper

#### For `greater` / `less` / `between`:
1. Use binary search to find boundary indices
2. Return slice of matching records
3. Use operator-specific helpers: `_binary_search_greater()`, `_binary_search_less()`, `_binary_search_between()`

#### Fallback for `like` / `any`:
- Text-based searches require sequential scan
- Binary search cannot efficiently skip regions with substring matches
- Delegates to `linear_search()`

**When to Use**: Large sorted datasets, repeated searches on same field, when O(log n) performance is required.

**Example**:
```python
# Pre-sort records (done internally by service layer)
sorted_records = insertion_sort(records, "weight_kg")

# Exact match (O(log n))
results = binary_search(sorted_records, "weight_kg", 75.0, operator="equals")

# Numeric range (O(log n))
results = binary_search(sorted_records, "daily_calories", 2000, operator="between", target_max=2500)

# Text search (falls back to O(n))
results = binary_search(sorted_records, "notes", "recovery", operator="like")
```

---

## Comparison Helper: `should_swap`

**Purpose**: Centralized logic for determining sort order (ascending vs. descending).

**Signature**:
```python
def should_swap(left: tuple, right: tuple, descending: bool) -> bool
```

**Logic**:
- If `descending=False` (ascending): swap if `left > right`
- If `descending=True` (descending): swap if `left < right`
- Works on normalized tuples `(priority, value)`

**Usage**: Called by all sorting algorithms to ensure consistent order direction.

---

## Integration with Service Layer

The service layer (`progress_service.py`) orchestrates algorithm usage:

1. **Field Name Resolution** (`_resolve_field_name`):
   - Maps user input ("weight", "Weight kg", etc.) to record keys
   - Ensures algorithms receive normalized field names

2. **Search Flow**:
   ```python
   search_records(field="weight", target=75, algorithm="binary", operator="equals")
   # → Resolves field to "weight_kg"
   # → Sorts records by weight_kg (insertion sort)
   # → Calls binary_search() on sorted results
   ```

3. **Sort Flow**:
   ```python
   sort_records(field="weight", algorithm="bubble", descending=False)
   # → Resolves field to "weight_kg"
   # → Calls bubble_sort() with normalized field
   # → Benchmarks performance and returns sorted records
   ```

4. **Statistics & Filtering**:
   - Uses normalized data for accurate min/max/avg calculations
   - Filters by numeric ranges using `_filter_numeric_range`

---

## Example Workflow: Complete Search + Sort Flow

```python
# User input: search for records with weight > 70 kg, then sort by date

from progress_service import search_records, sort_records

# Step 1: Search (linear search on unsorted data)
results = search_records(
    field="weight",
    target=70,
    algorithm="linear",
    operator="greater"
)
# Service resolves "weight" → "weight_kg"
# Linear search compares normalized values (0, 70.0) > (0, record_value)

# Step 2: Sort results by date (ascending)
sorted_results = sort_records(
    field="date",
    algorithm="insertion",
    descending=False,
    records=results
)
# Service resolves "date" → "record_date"
# Insertion sort builds ordered list using sort_key normalization

# Output: 5 records with weight > 70 kg, sorted by date ascending
```

---

## Performance Summary

| Algorithm | Best Case | Average Case | Worst Case | Space | Stable | Use Case |
|-----------|-----------|--------------|-----------|-------|--------|----------|
| **Bubble Sort** | O(n) | O(n²) | O(n²) | O(1) | Yes | Educational, nearly sorted |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | Yes | Small data, online |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Large data, consistent perf |
| **Linear Search** | O(1) | O(n) | O(n) | O(k) | N/A | Unsorted, small data |
| **Binary Search** | O(log n)* | O(log n)* | O(log n)* | O(k) | N/A | Sorted, large data |

*For numeric operators; text-based operators fall back to O(n)

---

## Testing & Validation

To test algorithm implementations:

```bash
# Compile module syntax
python -m py_compile src/algorithms/sorting.py src/algorithms/searching.py

# Run integration tests via CLI
python src/main.py

# Manual test: sort records by weight
# → Enter "sort" → Select field "weight" → Select algorithm "bubble"

# Manual test: search records
# → Enter "search" → Field "weight" → Operator "greater" → Value "70"
```

---

## References

- **Normalization pattern**: Ensures data type consistency across algorithms
- **Sorting key function**: Enables multi-type record sorting
- **Operator matching**: Supports six search operators for flexible queries
- **Service integration**: Field name resolution bridges user input to algorithm execution

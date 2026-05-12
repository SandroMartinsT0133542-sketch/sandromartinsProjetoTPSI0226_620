# SQL-Like Operators Implementation

## Overview
The fitness management system now supports SQL-like comparison operators across both linear and binary search algorithms. This allows users to perform flexible queries beyond simple exact matches.

## Operators Supported

### 1. **equals** (default)
- **Description:** Exact match on field value
- **Use Case:** Find records with specific values
- **Example:** `weight = 75.0`
- **Linear:** O(n) exact comparison
- **Binary:** O(log n) binary search + boundary expansion
- **Numeric & Text:** Both supported

### 2. **like**
- **Description:** Case-insensitive substring matching
- **Use Case:** Partial text search (e.g., find all notes containing "protein")
- **Example:** `notes LIKE '%protein%'`
- **Linear:** O(n) string containment check
- **Binary:** Falls back to linear (can't efficiently binary search substrings)
- **Applies To:** Text fields only
- **Behavior:** Empty target matches nothing; whitespace normalized

### 3. **greater**
- **Description:** Greater-than comparison (>)
- **Use Case:** Find records above a threshold
- **Example:** `weight > 75`
- **Linear:** O(n) numeric comparison
- **Binary:** O(log n) binary boundary search
- **Applies To:** Numeric fields only
- **Returns:** All records where field value > target

### 4. **less**
- **Description:** Less-than comparison (<)
- **Use Case:** Find records below a threshold
- **Example:** `weight < 70`
- **Linear:** O(n) numeric comparison
- **Binary:** O(log n) binary boundary search
- **Applies To:** Numeric fields only
- **Returns:** All records where field value < target

### 5. **between**
- **Description:** Range check (min ≤ value ≤ max)
- **Use Case:** Find records within a range
- **Example:** `weight BETWEEN 65 AND 75`
- **Linear:** O(n) range comparison
- **Binary:** O(log n) dual boundary search
- **Applies To:** Numeric fields only
- **Requires:** Both `target` (min) and `target_max` (max) parameters
- **Returns:** All records where min ≤ field ≤ max (inclusive)

### 6. **any**
- **Description:** Match against set of comma-separated values
- **Use Case:** Find records matching any of multiple criteria
- **Example:** `name IN ['Alice', 'Eve']` (input as `Alice,Eve`)
- **Linear:** O(n) set membership check
- **Binary:** Falls back to linear (requires scanning all values)
- **Behavior:** 
  - Comma-separated list: `value1,value2,value3`
  - Case-insensitive for text fields
  - Supports both exact match and substring matching within the set

## Implementation Details

### Algorithm Layer (`src/algorithms/searching.py`)

#### New Helper: `_matches_operator()`
```python
def _matches_operator(
    record_value: Any, 
    operator: str, 
    target: object, 
    target_max: object | None = None
) -> bool
```
Centralized operator evaluation logic used by both search algorithms.

#### Updated `linear_search()` Signature
```python
def linear_search(
    records: list[dict[str, Any]],
    field: str,
    target: object,
    operator: Literal["equals", "like", "greater", "less", "between", "any"] = "equals",
    target_max: object | None = None,
) -> list[dict[str, Any]]
```
- Scans all records and applies operator condition
- O(n) time complexity regardless of operator
- Supports all 6 operators natively

#### Updated `binary_search()` Signature
```python
def binary_search(
    records: list[dict[str, Any]],
    field: str,
    target: object,
    operator: Literal["equals", "like", "greater", "less", "between", "any"] = "equals",
    target_max: object | None = None,
) -> list[dict[str, Any]]
```
- **Requires:** Records sorted by search field
- **Fallback Logic:**
  - `'like'` and `'any'` → automatically fall back to `linear_search()`
  - Other operators use optimized binary boundary-finding
- **Complexity:**
  - `equals`: O(log n + m) where m = number of matches
  - `greater`/`less`/`between`: O(log n)
  - `like`/`any`: O(n) via fallback

### Service Layer (`src/services/progress_service.py`)

#### Updated `search_records()` Signature
```python
def search_records(
    field: str,
    target: str | int | float,
    algorithm: str = "linear",
    operator: str = "equals",
    target_max: str | int | float | None = None,
    records: list[Record] | None = None,
) -> list[Record]
```
- Maintains backward compatibility (operator defaults to "equals")
- Handles binary fallback transparently
- If binary + incompatible operator → switches to linear automatically

### GUI Layer (`src/gui/main_view.py`)

#### New Instance Variables
```python
self.search_operator_var = StringVar(value="equals")
self._operator_options = ["equals", "like", "greater", "less", "between", "any"]
self.search_value_max = ttk.Entry(...)  # Hidden by default
```

#### Updated Layout
- **Row 0:** Field selector → Operator dropdown → Value input → Max value input (conditional) → Action buttons
- **Operator Combobox:** Dropdown with all 6 operator modes
- **Max Value Field:** Only visible when "between" is selected
- **Help Text:** Describes all operators and binary search limitations

#### Event Handlers
- `_on_operator_changed()`: Triggered when operator selection changes
- `_update_max_field_visibility()`: Shows/hides "Max" field based on operator
- Updated `_search()`: Passes operator and target_max to service layer
- Updated `_reset_search()`: Resets operator to "equals" and clears both value fields

## Usage Examples

### Example 1: Find Weight Greater Than 70 kg
1. Field: `Weight`
2. Operator: `greater`
3. Value: `70`
4. Click `Linear` or `Binary`
→ Returns all records where weight > 70

### Example 2: Find Notes Containing "protein"
1. Field: `Notes`
2. Operator: `like`
3. Value: `protein`
4. Click `Linear` (binary will auto-fallback)
→ Returns all records with "protein" in notes (case-insensitive)

### Example 3: Find Weight In Range 65–75 kg
1. Field: `Weight`
2. Operator: `between`
3. Value: `65`
4. Max: `75`
5. Click `Linear` or `Binary`
→ Returns all records where 65 ≤ weight ≤ 75

### Example 4: Find Calories By User Preference
1. Field: `Calories`
2. Operator: `any`
3. Value: `2000,2200,2400`
4. Click `Linear` (binary will auto-fallback)
→ Returns records matching any of [2000, 2200, 2400]

## Backward Compatibility

All changes are **backward compatible**:
- Default operator is `"equals"` (existing behavior)
- Service layer accepts `operator` parameter as optional (defaults to "equals")
- Old code calling `search_records(field, target, algorithm)` continues to work
- CLI and other modules unaffected

## Testing

Comprehensive test suite validates:
- ✅ All 6 operators with linear search
- ✅ All 6 operators with binary search
- ✅ Automatic fallback for incompatible binary + operator combinations
- ✅ Boundary conditions (duplicates, edge values)
- ✅ Numeric vs. text field handling
- ✅ "between" range inclusivity (min ≤ value ≤ max)
- ✅ "any" comma-separated parsing

## Performance Implications

| Operation | Time Complexity | Best Used When |
|-----------|-----------------|----------------|
| Linear search (any operator) | O(n) | Unsorted data or small datasets |
| Binary equals | O(log n + m) | Large sorted dataset, many duplicates |
| Binary greater/less/between | O(log n) | Large sorted dataset, threshold queries |
| Binary like/any | O(n) fallback | Not recommended; use linear instead |

### Recommendation
- Use **Linear** for unsorted data or if any operator except "equals" is needed on large datasets
- Use **Binary** for equals/greater/less/between on large sorted datasets
- Binary "like"/"any" will auto-fallback to linear, so minimal performance penalty if selected by mistake

## Assignment Compliance

✅ All search algorithms remain **manually implemented** (no Python built-in search shortcuts)
✅ **Time/Space complexity** documented in docstrings
✅ **Modular architecture** maintained across algorithm/service/GUI layers
✅ **No built-in operators** (all logic custom-implemented in `_matches_operator`)
✅ **Robust error handling** on type mismatches and invalid numeric conversions

## Files Modified

1. **`src/algorithms/searching.py`**
   - Added `_matches_operator()` helper
   - Extended `linear_search()` with operator support
   - Extended `binary_search()` with operator support and fallback logic

2. **`src/services/progress_service.py`**
   - Updated `search_records()` signature to accept operator and target_max
   - Added fallback logic for binary + incompatible operator combinations

3. **`src/gui/main_view.py`**
   - Added operator selector combobox
   - Added dynamic "Max" value field
   - Updated `_search()` to pass operator and target_max
   - Added `_on_operator_changed()` event handler
   - Added `_update_max_field_visibility()` helper
   - Updated `_reset_search()` to reset operator and max field

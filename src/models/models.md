# Models Module

The `models` module provides data structure helpers for building, parsing, and serializing fitness progress records. It uses dictionaries instead of classes to keep the project lightweight and suitable for a student assignment.

---

## Overview

The models module defines a single entity type:

- **Progress Entry** – Represents one fitness tracking record with 7 attributes including an auto-generated unique ID

**Key Principle**: All models are built as plain dictionaries with consistent types and validation. This allows seamless JSON serialization and is more flexible for student projects than class-based models.

---

## Progress Entry Model

### Record Structure

A progress entry is a dictionary with the following fields:

```python
{
    "record_id": 1,              # int - Unique auto-generated ID
    "user_id": 1,                # int - Owner of this record
    "record_date": "14-05-2026", # str - DD-MM-YYYY format
    "weight_kg": 75.5,           # float - Body weight in kilograms
    "body_fat_pct": 22.3,        # float - Body fat percentage
    "daily_calories": 2150,      # int - Caloric intake
    "notes": "Recovery day"      # str - User notes (optional)
}
```

### Field Specifications

| Field            | Type  | Range               | Purpose           | Example        |
| ---------------- | ----- | ------------------- | ----------------- | -------------- |
| `record_id`      | int   | 1+ (auto-generated) | Unique identifier | 5              |
| `user_id`        | int   | 1+                  | Owner reference   | 3              |
| `record_date`    | str   | DD-MM-YYYY          | Date of entry     | "14-05-2026"   |
| `weight_kg`      | float | Typically 30-200    | Body weight       | 75.5           |
| `body_fat_pct`   | float | 0-60                | Body fat %        | 22.3           |
| `daily_calories` | int   | 0-10000             | Caloric intake    | 2150           |
| `notes`          | str   | 0-1000 chars        | Optional memo     | "Recovery day" |

### Total Attributes

The record has **7 attributes**, meeting the assignment requirement of **5+ attributes plus auto-generated ID**.

---

## Key Functions

### `build_progress_entry(...) -> Record`

**Purpose**: Construct a new progress entry dictionary with all fields normalized to expected types.

**Signature**:

```python
def build_progress_entry(
    record_id: int,
    user_id: int,
    record_date: str,
    weight_kg: float,
    body_fat_pct: float,
    daily_calories: int,
    notes: str,
) -> Record
```

**Workflow**:

1. Accept all 7 parameters as individual arguments
2. Normalize each to its expected type using type cast
3. Return dictionary with all fields

**Returns**: Dictionary with type-normalized fields.

**Example**:

```python
from models.progress_entry import build_progress_entry

record = build_progress_entry(
    record_id=1,
    user_id=10,
    record_date="14-05-2026",
    weight_kg=75.5,
    body_fat_pct=22.3,
    daily_calories=2150,
    notes="Recovery day"
)

# Returns:
# {
#     "record_id": 1,
#     "user_id": 10,
#     "record_date": "14-05-2026",
#     "weight_kg": 75.5,
#     "body_fat_pct": 22.3,
#     "daily_calories": 2150,
#     "notes": "Recovery day"
# }
```

**Used By**:

- Service layer when creating new records
- Parsing functions when normalizing deserialized data

---

### `parse_progress_entry(raw: dict) -> Record`

**Purpose**: Normalize and coerce raw/partial data (from JSON or user input) into a valid progress entry structure with sensible defaults.

**Signature**:

```python
def parse_progress_entry(raw: dict[str, Any]) -> Record
```

**Workflow**:

1. Accept a raw dictionary (may be incomplete, wrong types, etc.)
2. Extract each field with a default fallback
3. Call `build_progress_entry()` to normalize types
4. Return validated record

**Defaults Used**:

- `record_id` → 0 (will be replaced by service layer)
- `user_id` → 0
- `record_date` → "" (empty string)
- `weight_kg` → 0.0
- `body_fat_pct` → 0.0
- `daily_calories` → 0
- `notes` → "" (empty string)

**Returns**: Fully normalized dictionary (same structure as `build_progress_entry()`).

**Example**:

```python
from models.progress_entry import parse_progress_entry

# Incomplete data from JSON (missing some fields)
raw = {
    "record_id": 5,
    "user_id": 10,
    "weight_kg": 75.5,
    # ... other fields missing ...
}

record = parse_progress_entry(raw)

# Returns (with defaults filled):
# {
#     "record_id": 5,
#     "user_id": 10,
#     "record_date": "",          # Default
#     "weight_kg": 75.5,
#     "body_fat_pct": 0.0,        # Default
#     "daily_calories": 0,        # Default
#     "notes": ""                 # Default
# }
```

**Used By**:

- Service layer when loading records from JSON
- Update record flow to coerce user-provided changes
- Data migration or import routines

---

### `serialize_progress_entry(record: Record) -> Record`

**Purpose**: Prepare a record for JSON persistence by normalizing it (identical behavior to `parse_progress_entry` in current implementation).

**Signature**:

```python
def serialize_progress_entry(record: Record) -> Record
```

**Workflow**:

1. Accept a record dictionary
2. Pass through `parse_progress_entry()` for consistency
3. Ensure all fields are JSON-compatible types (int, float, str)

**Returns**: Validated record ready for JSON serialization.

**Example**:

```python
from models.progress_entry import serialize_progress_entry

record = {
    "record_id": 1,
    "user_id": 10,
    "record_date": "14-05-2026",
    "weight_kg": 75.5,
    "body_fat_pct": 22.3,
    "daily_calories": 2150,
    "notes": "Recovery day"
}

serialized = serialize_progress_entry(record)
# Same as input (all types already valid for JSON)

# Can be safely written to JSON
import json
json_str = json.dumps(serialized)
```

**Used By**:

- Service layer before persisting records to JSON
- Export/backup routines

---

## Data Flow Diagram

```
User Input
    ↓
[Create/Update Record]
    ↓
parse_progress_entry() [normalize raw data]
    ↓
[Validate business logic in service]
    ↓
build_progress_entry() [construct final record]
    ↓
In-Memory Store (progress_state["records"])
    ↓
serialize_progress_entry() [prepare for JSON]
    ↓
json.dump()
    ↓
data/progress_records.json
```

---

## Integration with Service Layer

The service layer (`progress_service.py`) uses models at key points:

### Creating a New Record

```python
# In progress_service.create_record()
record = build_progress_entry(
    record_id=record_id,
    user_id=active_user_id,
    record_date=payload["record_date"],
    weight_kg=cast(float, payload["weight_kg"]),
    body_fat_pct=cast(float, payload["body_fat_pct"]),
    daily_calories=cast(int, payload["daily_calories"]),
    notes=cast(str, payload["notes"]),
)
```

### Loading Records from JSON

```python
# In progress_service.initialize_service()
progress_state["records"] = [
    parse_progress_entry(record) for record in load_records(db)
]
```

### Updating a Record

```python
# In progress_service.update_record()
updated_record = record.copy()
updated_record.update(updates)
records[index] = parse_progress_entry(updated_record)
```

### Saving to JSON

```python
# In progress_service.save_state()
save_records(
    db,
    [serialize_progress_entry(record) for record in records]
)
```

---

## Type Alias

```python
Record = dict[str, Any]
```

Used throughout the system to represent a progress entry or any record-like dictionary.

---

## Why Dictionaries Instead of Classes?

**Advantages for Student Project**:

- ✅ Simpler to understand (no OOP concepts required)
- ✅ Direct JSON serialization (no custom encoders needed)
- ✅ Flexible: fields can be added/removed easily
- ✅ Matches assignment model (entity with attributes + ID)

**Disadvantages**:

- ❌ No type hints at runtime (Python dicts are untyped)
- ❌ No methods (helpers are module-level functions)
- ❌ Easier to accidentally create malformed records

**Mitigation**:

- Parse/build functions enforce structure
- Service layer validates before persistence
- Clear documentation (this README)

---

## Example Complete Workflow

```python
from models.progress_entry import build_progress_entry, parse_progress_entry, serialize_progress_entry
import json

# Step 1: Build a new record from user input
record = build_progress_entry(
    record_id=1,
    user_id=5,
    record_date="14-05-2026",
    weight_kg=75.5,
    body_fat_pct=22.3,
    daily_calories=2150,
    notes="Good workout"
)

# Step 2: Store in memory
records_list = [record]

# Step 3: Prepare for JSON
serialized = [serialize_progress_entry(r) for r in records_list]

# Step 4: Write to file
json_data = json.dumps(serialized, indent=4)
print(json_data)
# Output:
# [
#     {
#         "record_id": 1,
#         "user_id": 5,
#         "record_date": "14-05-2026",
#         "weight_kg": 75.5,
#         "body_fat_pct": 22.3,
#         "daily_calories": 2150,
#         "notes": "Good workout"
#     }
# ]

# Step 5: Load back from JSON
loaded = json.loads(json_data)
parsed_records = [parse_progress_entry(r) for r in loaded]

# Step 6: Use in service
assert parsed_records[0]["weight_kg"] == 75.5
```

---

## Testing

```bash
# Test record creation
python -c "
from src.models.progress_entry import build_progress_entry
r = build_progress_entry(1, 5, '14-05-2026', 75.5, 22.3, 2150, 'Test')
print(r['weight_kg'])  # Should print: 75.5
"

# Test parsing with defaults
python -c "
from src.models.progress_entry import parse_progress_entry
r = parse_progress_entry({'record_id': 1})
print(r)  # Should show all 7 fields with defaults
"

# Test JSON roundtrip
python -c "
import json
from src.models.progress_entry import build_progress_entry, serialize_progress_entry, parse_progress_entry
r1 = build_progress_entry(1, 5, '14-05-2026', 75.5, 22.3, 2150, 'Test')
s = serialize_progress_entry(r1)
j = json.dumps(s)
r2 = parse_progress_entry(json.loads(j))
assert r1 == r2, 'Roundtrip failed'
print('Roundtrip OK')
"
```

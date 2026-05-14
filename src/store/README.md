# Store Module

The `store` module provides JSON persistence helpers for loading and saving records. It handles file I/O, directory creation, JSON parsing, and graceful error recovery. This layer abstracts persistence details from the service layer.

---

## Overview

The store module contains a single file:

- **`storage.py`** – JSON read/write utilities with automatic directory creation and error handling

**Key Principle**: Store layer is unaware of data semantics. It reads/writes JSON records as dictionaries with minimal validation, leaving business logic to the service layer.

---

## Storage Module (`storage.py`)

### Purpose

Provide low-level JSON persistence operations for both users and progress records, with special handling for grouped record structures.

### Key Functions

#### `initialize_database(db_path: Path) -> None`

**Purpose**: Ensure the JSON file and parent directories exist. Creates an empty JSON array if the file doesn't exist.

**Signature**:

```python
def initialize_database(db_path: Path) -> None
```

**Workflow**:

1. Create all parent directories (including intermediate ones)
2. Check if file exists
3. If not, write empty JSON array `[]` to file
4. Return silently (no error if already exists)

**Example**:

```python
from pathlib import Path
from store.storage import initialize_database

db_path = Path("data/progress_records.json")
initialize_database(db_path)
# Creates data/ directory if needed
# Creates data/progress_records.json with `[]` if needed
```

**Used By**:

- Services during startup
- Before any read/write operation
- Ensures file is always valid JSON

---

#### `load_records(db_path: Path) -> list[Record]`

**Purpose**: Read and parse JSON from a file, returning a flat list of records.

**Signature**:

```python
def load_records(db_path: Path) -> list[Record]
```

**Returns**: List of record dictionaries. Empty list on error or missing file.

**Workflow**:

1. **File Check**
   - If file doesn't exist, initialize it and return `[]`

2. **Read & Parse**
   - Read file as UTF-8 text
   - Parse JSON string
   - Return empty list if file is empty

3. **Structured Data Handling**
   - Check if file is `progress_records.json`
   - If yes: flatten grouped structure (see below)
   - If no: treat as flat list

4. **Type Validation**
   - Extract only records with valid types
   - Filter out non-dict items
   - Keep only `(str, int, float)` values

5. **Error Recovery**
   - Catch JSON parsing errors gracefully
   - Print warning if parse fails
   - Return empty list (fail-safe)

**Returns**: Flat list of valid records or empty list on any error.

**Example**:

```python
from pathlib import Path
from store.storage import load_records

records = load_records(Path("data/progress_records.json"))
print(f"Loaded {len(records)} records")

# If file doesn't exist, doesn't return error—just empty list
# If JSON is malformed, prints warning and returns empty list
```

---

##### Progress Records Grouping (Special Case)

For `progress_records.json`, records are stored grouped by user_id:

**On-Disk Format**:

```json
[
    {
        "user_id": 1,
        "records": [
            {"record_id": 1, "weight_kg": 75.5, ...},
            {"record_id": 2, "weight_kg": 76.0, ...}
        ]
    },
    {
        "user_id": 2,
        "records": [
            {"record_id": 10, "weight_kg": 68.0, ...}
        ]
    }
]
```

**Load Process**:

1. Iterate through each user group
2. Extract `records` array from group
3. Flatten all records into single list
4. Add `user_id` from group to each record
5. Return flat list

**In-Memory Representation**:

```python
[
    {"record_id": 1, "user_id": 1, "weight_kg": 75.5, ...},
    {"record_id": 2, "user_id": 1, "weight_kg": 76.0, ...},
    {"record_id": 10, "user_id": 2, "weight_kg": 68.0, ...}
]
```

This allows the service layer to work with a flat list while the disk stores grouped data.

---

#### `save_records(db_path: Path, records: list[Record]) -> bool`

**Purpose**: Write records to JSON file in an appropriate structure (grouped for progress_records.json, flat otherwise).

**Signature**:

```python
def save_records(db_path: Path, records: list[Record]) -> bool
```

**Parameters**:

- `db_path` – Path to JSON file
- `records` – List of record dicts to persist

**Returns**: `True` on success, `False` on I/O error.

**Workflow**:

1. **Initialization**
   - Call `initialize_database()` to ensure file/dirs exist

2. **Determine Format**
   - If filename is `progress_records.json`: use grouped format
   - Otherwise: use flat format

3. **Format Selection**

   **For Flat Files** (users.json, etc.):
   - Write records directly as JSON array
   - Example:
     ```json
     [
         {"user_id": 1, "username": "admin", ...},
         {"user_id": 2, "username": "alice", ...}
     ]
     ```

   **For Grouped Files** (progress_records.json):
   - Group records by `user_id`
   - Structure:
     ```json
     [
         {
             "user_id": 1,
             "records": [
                 {"record_id": 1, ...},
                 {"record_id": 2, ...}
             ]
         },
         {
             "user_id": 2,
             "records": [
                 {"record_id": 10, ...}
             ]
         }
     ]
     ```

4. **Write to File**
   - Serialize to JSON with 4-space indentation
   - Write to file as UTF-8
   - Return `True`

5. **Error Handling**
   - Catch `OSError` (file write issues)
   - Catch `TypeError` (non-serializable objects)
   - Print error message
   - Return `False`

**Example**:

```python
from pathlib import Path
from store.storage import save_records

records = [
    {"record_id": 1, "user_id": 1, "weight_kg": 75.5, ...},
    {"record_id": 2, "user_id": 1, "weight_kg": 76.0, ...}
]

success = save_records(Path("data/progress_records.json"), records)
if not success:
    print("Warning: Could not save records")
```

---

### Grouped Format Implementation Detail

For `progress_records.json`, the save workflow:

```python
grouped: dict[int, list[Record]] = {}

# Group records by user_id
for record in records:
    user_id = int(record.get("user_id", 0))
    if user_id not in grouped:
        grouped[user_id] = []
    grouped[user_id].append(record)

# Convert to list of {user_id, records} dicts
output = [
    {"user_id": user_id, "records": group_records}
    for user_id, group_records in grouped.items()
]

# Write output to JSON
json_str = json.dumps(output, indent=4)
db_path.write_text(json_str, encoding="utf-8")
```

---

## Data Flow Diagram

### Startup (Load)

```
Application Start
    ↓
services.initialize_service()
    ↓
store.initialize_database()
    → Ensures data/progress_records.json exists
    ↓
store.load_records()
    → Reads JSON file
    → Flattens grouped structure
    → Returns flat record list
    ↓
Service Layer
    → parse_progress_entry() for each record
    → Store in memory (progress_state["records"])
    ↓
Ready for CRUD operations
```

### Shutdown (Save)

```
User presses Ctrl+C or selects Quit
    ↓
CLI prompts: "Save records? (Y/N)"
    ↓
If Yes:
    services.save_state()
        ↓
        serialize_progress_entry() for each record
        ↓
        store.save_records()
            → Groups by user_id
            → Writes to JSON with 4-space indent
            ✓ Data persisted
```

---

## Error Handling Strategy

### Fail-Safe Approach

All errors are caught at the store level to prevent crashes:

```python
try:
    # File I/O and JSON parsing
    raw_data = db_path.read_text(encoding="utf-8")
    loaded_data = json.loads(raw_data)
except (OSError, JSONDecodeError, ValueError, TypeError) as error:
    print(f"[Warning] Could not load records: {error}")
    return []  # Return empty list, not error
```

**Philosophy**:

- ✅ Never crash on file read/write issues
- ✅ Print warning to user
- ✅ Return empty/false gracefully
- ✅ Let service layer handle "no data" case

### Common Errors Handled

| Error               | Cause                   | Recovery                         |
| ------------------- | ----------------------- | -------------------------------- |
| `FileNotFoundError` | File doesn't exist      | Create empty file                |
| `JSONDecodeError`   | Corrupted JSON          | Return empty list, print warning |
| `PermissionError`   | Cannot write file       | Return False, print warning      |
| `TypeError`         | Non-serializable object | Return False, print warning      |
| `ValueError`        | Type coercion fails     | Skip that record, continue       |

---

## Type Aliases

```python
Record = dict[str, int | float | str]
```

Records can contain integers (IDs, counts), floats (weights, percentages), or strings (names, dates, notes).

---

## File Organization

Typical data directory structure:

```
workspace/
├── data/
│   ├── users.json                # Flat list of users
│   └── progress_records.json     # Grouped by user_id
├── benchmarks/
│   ├── bubble_results.json
│   ├── insertion_results.json
│   └── merge_results.json
└── src/
    └── store/
        ├── __init__.py
        └── storage.py
```

---

## JSON Format Examples

### users.json (Flat)

```json
[
  {
    "user_id": 1,
    "username": "admin",
    "display_name": "Administrator",
    "email": "admin@fitness.local",
    "phone": "+351900000000",
    "password_hash": "abc123..."
  },
  {
    "user_id": 2,
    "username": "alice",
    "display_name": "Alice Smith",
    "email": "alice@example.com",
    "phone": "+351912345678",
    "password_hash": "def456..."
  }
]
```

### progress_records.json (Grouped)

```json
[
  {
    "user_id": 1,
    "records": [
      {
        "record_id": 1,
        "user_id": 1,
        "record_date": "14-05-2026",
        "weight_kg": 75.5,
        "body_fat_pct": 22.3,
        "daily_calories": 2150,
        "notes": "Recovery day"
      },
      {
        "record_id": 2,
        "user_id": 1,
        "record_date": "15-05-2026",
        "weight_kg": 76.0,
        "body_fat_pct": 22.1,
        "daily_calories": 2200,
        "notes": "Good workout"
      }
    ]
  },
  {
    "user_id": 2,
    "records": [
      {
        "record_id": 10,
        "user_id": 2,
        "record_date": "14-05-2026",
        "weight_kg": 68.0,
        "body_fat_pct": 18.5,
        "daily_calories": 1800,
        "notes": ""
      }
    ]
  }
]
```

---

## Testing

```bash
# Test initialize
python -c "
from pathlib import Path
from src.store.storage import initialize_database
import tempfile
import os

with tempfile.TemporaryDirectory() as tmpdir:
    db = Path(tmpdir) / 'test.json'
    from src.store.storage import initialize_database
    initialize_database(db)
    print(f'File exists: {db.exists()}')
    print(f'Content: {db.read_text()}')
"

# Test load/save roundtrip
python -c "
from pathlib import Path
from src.store.storage import save_records, load_records
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    db = Path(tmpdir) / 'test.json'

    records = [
        {'record_id': 1, 'user_id': 1, 'weight_kg': 75.5},
        {'record_id': 2, 'user_id': 1, 'weight_kg': 76.0}
    ]

    save_records(db, records)
    loaded = load_records(db)

    print(f'Saved: {len(records)} records')
    print(f'Loaded: {len(loaded)} records')
    print(f'Match: {records == loaded}')
"
```

# Services Module

The `services` module provides the core business logic layer, orchestrating CRUD operations, authentication, search, sort, and statistics functions. It sits between the CLI/GUI and the persistence layer, managing state and applying validation rules.

---

## Overview

The services module contains two primary services:

- **`auth_service.py`** – User authentication and account management
- **`progress_service.py`** – Fitness progress record CRUD, search, sort, and statistics

Each service maintains an in-memory state dictionary that mirrors the JSON persistence layer, ensuring consistent data access and enabling efficient batch operations.

---

## Auth Service (`auth_service.py`)

### Purpose

Manage user accounts, authentication, and session state. Integrates with the store layer for JSON persistence and utils for password hashing.

### State Dictionary

```python
auth_state: dict = {
    "users_db": Path(...) / "data" / "users.json",  # Path to JSON store
    "users": [],                                      # In-memory user list
    "current_username": None,                        # Logged-in user (None = not logged in)
    "current_user_id": None,                         # Logged-in user ID
}
```

### Key Functions

#### `initialize_auth(db_path: Path | None = None) -> None`

**Purpose**: Load user data from JSON and create a default admin account if the database is empty.

**Workflow**:

1. Set users database path (or use provided override)
2. Call store's `initialize_database()` to ensure file exists
3. Load users from JSON into memory
4. If no users exist, create default admin account
   - Username: `admin`
   - Password: `admin` (hashed)
   - Email: `admin@fitness.local`
   - Phone: `+351900000000`
   - User ID: 1
5. Save default admin to JSON

**Example**:

```python
from services.auth_service import initialize_auth
from pathlib import Path

# Initialize with default path
initialize_auth()

# Or with custom path
initialize_auth(Path("/custom/data/users.json"))
```

**Called By**:

- Main application startup
- During first-run setup

---

#### `save_users() -> bool`

**Purpose**: Persist in-memory user list to JSON file.

**Returns**: `True` on success, `False` on I/O failure.

**Workflow**:

1. Get database path from auth_state
2. Get users list from auth_state
3. Call store's `save_records()` to write JSON
4. Return success/failure

**Example**:

```python
from services.auth_service import register_user, save_users

# After registering a new user
register_user("alice", "Alice Smith", "SecurePass123")
if not save_users():
    print("Error saving users to disk")
```

---

#### `register_user(username: str, display_name: str, password: str, email: str = "", phone: str = "") -> tuple[bool, str]`

**Purpose**: Create a new user account with input validation and uniqueness checks.

**Signature**:

```python
def register_user(
    username: str,           # Unique login name
    display_name: str,       # Human-readable name
    password: str,           # Plaintext (will be hashed)
    email: str = "",         # Contact email (optional)
    phone: str = "",         # Contact phone (optional)
) -> tuple[bool, str]        # (success, message)
```

**Validation**:

1. Trim all inputs
2. Check all required fields are provided
3. Verify username is unique
4. Verify email is unique (or assign default if empty)
5. Verify phone is unique (or assign default if empty)
6. Verify display_name is unique

**Returns**: `(True, "")` on success or `(False, error_message)` on failure.

**Failures**:

- `(False, "All fields are required.")` – Missing field after trim
- `(False, "That username is already taken.")` – Username collision
- `(False, "That email is already registered.")` – Email collision
- `(False, "That phone number is already registered.")` – Phone collision
- `(False, "That display name is already taken.")` – Display name collision

**Example**:

```python
from services.auth_service import register_user, save_users

success, msg = register_user(
    username="alice",
    display_name="Alice Smith",
    password="SecurePass123",
    email="alice@example.com",
    phone="+351912345678"
)

if success:
    save_users()
    print("Registration successful")
else:
    print(f"Registration failed: {msg}")
```

---

#### `authenticate(username: str, password: str) -> tuple[bool, int | None]`

**Purpose**: Verify login credentials and return the authenticated user's ID.

**Returns**: `(True, user_id)` on success or `(False, None)` on failure.

**Workflow**:

1. Find user by username (case-sensitive)
2. Hash provided password
3. Compare hash with stored `password_hash`
4. If match, set session state (`current_username`, `current_user_id`)
5. Return success/failure

**Example**:

```python
from services.auth_service import authenticate, current_user_id

success, user_id = authenticate("admin", "admin")
if success:
    print(f"Logged in as user {user_id}")
else:
    print("Invalid credentials")

# Check current session
logged_in_id = current_user_id()
print(f"Current user: {logged_in_id}")
```

---

#### `current_user_id() -> int | None`

**Purpose**: Retrieve the ID of the currently logged-in user.

**Returns**: `int` (user ID) if logged in, `None` otherwise.

**Example**:

```python
from services.auth_service import current_user_id

uid = current_user_id()
if uid is not None:
    print(f"User {uid} is logged in")
else:
    print("No user is logged in")
```

---

## Progress Service (`progress_service.py`)

### Purpose

Manage fitness progress records: CRUD operations, search, sort, statistics, and persistence. Uses the same in-memory + JSON persistence pattern as auth_service.

### State Dictionary

```python
progress_state: dict = {
    "db": Path(...) / "data" / "progress_records.json",  # JSON path
    "records": [],                                        # In-memory records
    "initialized": False,                                # Flag for lazy init
}
```

### Key Functions

#### `initialize_service(db_path: Path | None = None) -> None`

**Purpose**: Load progress records from JSON into memory.

**Workflow**:

1. Set database path (or use provided override)
2. Call store's `initialize_database()` to ensure file exists
3. Load records from JSON using `load_records()`
4. Parse each record using `parse_progress_entry()` for normalization
5. Mark as initialized

**Example**:

```python
from services.progress_service import initialize_service

initialize_service()
```

---

#### `list_records() -> list[Record]`

**Purpose**: Return all progress records for the current logged-in user.

**Workflow**:

1. Ensure service is initialized
2. Get current user ID from auth_service
3. Filter records by user_id
4. Return copies (avoid accidental mutations)

**Returns**: List of record dictionaries.

**Example**:

```python
from services.progress_service import list_records

records = list_records()
print(f"You have {len(records)} records")
```

---

#### `create_record(payload: Record) -> Record`

**Purpose**: Create a new record with auto-generated ID and attach to current user.

**Signature**:

```python
def create_record(payload: Record) -> Record
```

**Payload Fields**:

- `record_date` – Required, DD-MM-YYYY format
- `weight_kg` – Required, float
- `body_fat_pct` – Required, float
- `daily_calories` – Required, int
- `notes` – Optional, string

**Workflow**:

1. Ensure initialized
2. Calculate next record_id (max existing + 1)
3. Get current user_id from auth_service (or use payload override)
4. Call `build_progress_entry()` with all fields
5. Append to in-memory records list
6. Return copy of new record

**Returns**: The newly created record (with record_id set).

**Example**:

```python
from services.progress_service import create_record

new_record = create_record({
    "record_date": "14-05-2026",
    "weight_kg": 75.5,
    "body_fat_pct": 22.3,
    "daily_calories": 2150,
    "notes": "Good day"
})

print(f"Created record {new_record['record_id']}")
```

---

#### `find_by_id(record_id: int, user_id: int | str | None = None) -> Record | None`

**Purpose**: Look up one record by ID (optionally filtered by user).

**Returns**: Record dict if found, `None` otherwise.

**Example**:

```python
from services.progress_service import find_by_id

record = find_by_id(5)
if record:
    print(f"Found: {record['weight_kg']} kg")
else:
    print("Record not found")
```

---

#### `update_record(record_id: int, updates: Record, user_id: int | str | None = None) -> bool`

**Purpose**: Modify an existing record by ID.

**Workflow**:

1. Find record by ID
2. Create copy
3. Update with new values (calls `parse_progress_entry()` for validation)
4. Replace in-memory records list
5. Return success/failure

**Returns**: `True` if updated, `False` if not found.

**Example**:

```python
from services.progress_service import update_record

success = update_record(5, {
    "weight_kg": 76.0,
    "notes": "Updated"
})

if success:
    print("Record updated")
else:
    print("Record not found")
```

---

#### `delete_record(record_id: int, user_id: int | str | None = None) -> bool`

**Purpose**: Remove a record by ID (typically with user confirmation in CLI).

**Returns**: `True` if deleted, `False` if not found.

**Example**:

```python
from services.progress_service import delete_record

success = delete_record(5)
if success:
    print("Record deleted")
```

---

#### `search_records(field: str, target: object, algorithm: str = "linear", operator: str = "equals", target_max: object | None = None, records: list[Record] | None = None) -> list[Record]`

**Purpose**: Search records using linear or binary search with flexible operators.

**Parameters**:

- `field` – Field to search (e.g., "weight", "date")
- `target` – Search value
- `algorithm` – "linear" or "binary"
- `operator` – "equals", "like", "greater", "less", "between", "any"
- `target_max` – Maximum for "between" operator
- `records` – Optional pre-filtered records (defaults to current user)

**Workflow**:

1. Resolve field name via `_resolve_field_name()` (handles user input variations)
2. Get search space (provided records or current user's records)
3. If binary search, auto-sort using `insertion_sort()` first
4. Call appropriate search algorithm
5. Return matching records

**Returns**: List of matching record copies.

**Example**:

```python
from services.progress_service import search_records

# Linear search for weight > 70 kg
results = search_records("weight", 70, algorithm="linear", operator="greater")

# Binary search for exact weight match (on sorted data)
results = search_records("weight_kg", 75.5, algorithm="binary", operator="equals")

# Find records between two values
results = search_records("daily_calories", 2000, operator="between", target_max=2500)
```

---

#### `sort_records(field: str, algorithm: str, descending: bool = False, records: list[Record] | None = None) -> list[Record]`

**Purpose**: Sort records using bubble, insertion, or merge sort.

**Parameters**:

- `field` – Field to sort by
- `algorithm` – "bubble", "insertion", or "merge"
- `descending` – `False` for ascending, `True` for descending
- `records` – Optional pre-filtered records (defaults to current user)

**Workflow**:

1. Resolve field name via `_resolve_field_name()`
2. Get sort space (provided records or current user's records)
3. Call appropriate sorting algorithm via `run_benchmarks()` (records timing)
4. Return sorted records

**Returns**: List of sorted record copies.

**Example**:

```python
from services.progress_service import sort_records

# Bubble sort ascending
results = sort_records("weight_kg", "bubble", descending=False)

# Merge sort descending
results = sort_records("record_date", "merge", descending=True)
```

---

#### `compute_statistics() -> dict[str, int | float]`

**Purpose**: Calculate summary statistics for current user's records.

**Returns**: Dictionary with:

- `count` – Number of records
- `avg_weight` – Average weight in kg
- `avg_body_fat` – Average body fat %
- `min_weight` – Minimum weight
- `max_weight` – Maximum weight
- `total_calories` – Sum of all calories

**Example**:

```python
from services.progress_service import compute_statistics

stats = compute_statistics()
print(f"Average weight: {stats['avg_weight']} kg")
print(f"Record count: {stats['count']}")
```

---

#### `filter_weight_range(minimum: float, maximum: float, records: list[Record] | None = None) -> list[Record]`

**Purpose**: Filter records where weight falls within a range.

**Returns**: Matching records.

**Example**:

```python
from services.progress_service import filter_weight_range

# Find records between 70-80 kg
results = filter_weight_range(70, 80)
```

---

#### `filter_body_fat_range(...) -> list[Record]`

**Purpose**: Filter records where body fat % falls within a range.

---

#### `filter_calories_range(...) -> list[Record]`

**Purpose**: Filter records where daily calories falls within a range.

---

#### `save_state() -> bool`

**Purpose**: Persist current in-memory records to JSON.

**Returns**: `True` on success, `False` on failure.

**Workflow**:

1. Serialize all records using `serialize_progress_entry()`
2. Call store's `save_records()` to write JSON
3. Return success/failure

**Example**:

```python
from services.progress_service import save_state

# After creating/updating records
success = save_state()
if not success:
    print("Warning: Could not save to disk")
```

---

### Field Name Resolution

#### `_resolve_field_name(field: str) -> str`

**Purpose**: Map user-friendly field names to record keys.

**Aliases**:

- "id", "recordid" → "record_id"
- "date" → "record_date"
- "weight", "weight kg" → "weight_kg"
- "body fat", "body_fat" → "body_fat_pct"
- "calories" → "daily_calories"
- "notes" → "notes"

**Workflow**:

1. Strip whitespace
2. Convert to lowercase
3. Replace spaces with underscores
4. Look up in aliases dictionary
5. Return mapped key or original if no match

**Example**:

```python
_resolve_field_name("Weight")        # Returns "weight_kg"
_resolve_field_name("body fat %")    # Returns "body_fat_pct"
_resolve_field_name("notes")         # Returns "notes"
```

---

## Integration Diagram

```
CLI Input
    ↓
[Validation via utils.validators]
    ↓
Service Layer (progress_service)
    ├─ create_record() / update_record() / delete_record()
    ├─ search_records() [uses algorithms module]
    ├─ sort_records() [uses algorithms module with benchmarking]
    ├─ compute_statistics()
    └─ save_state()
    ↓
Store Layer (store.storage)
    ├─ load_records()
    └─ save_records()
    ↓
JSON Persistence (data/*.json)
```

---

## Session State Management

**Before Any Operation**:

- Call `ensure_initialized()` to lazily load data (called by all public functions)
- Checks `initialized` flag
- Only loads from JSON once per application run

**User Authentication**:

- Login sets `auth_state["current_user_id"]`
- All progress_service functions filter by this user_id
- Multi-user records share same JSON but are isolated in code

**In-Memory vs Persistent**:

- Records are cached in memory for performance
- Changes don't hit disk until `save_state()` is called
- End-of-program prompt asks user to save

---

## Error Handling

All service functions use try-except around I/O and parsing:

```python
try:
    records.append(new_record)
except (ValueError, TypeError) as e:
    print(f"Error processing record: {e}")
    return False
```

Failures are gracefully handled with user-friendly error messages.

---

## Testing

```bash
# Test user registration
python -c "
from src.services.auth_service import initialize_auth, register_user, save_users
initialize_auth()
success, msg = register_user('test', 'Test User', 'TestPass123')
print(f'Registered: {success}')
save_users()
"

# Test record creation
python -c "
from src.services.progress_service import initialize_service, create_record, list_records
from src.services.auth_service import initialize_auth, authenticate, save_users
from src.services.progress_service import save_state

initialize_auth()
authenticate('admin', 'admin')
initialize_service()

record = create_record({
    'record_date': '14-05-2026',
    'weight_kg': 75.5,
    'body_fat_pct': 22.3,
    'daily_calories': 2150,
    'notes': 'Test'
})
print(f'Created: {record[\"record_id\"]}')
save_state()
"
```

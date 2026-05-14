# Utils Module

The `utils` module provides shared utility functions for validation, password hashing, user generation, and performance benchmarking. These utilities are used across the service and CLI layers to ensure consistent data validation and quality metrics.

---

## Overview

The utils module consists of three primary components:

- **`validators.py`** – Input validation using regex patterns and type checking
- **`users.py`** – User account generation and password hashing
- **`benchmark.py`** – Algorithm performance measurement and logging

---

## Validators Module (`validators.py`)

### Purpose

Provides centralized regex-based validation for CLI input and field constraints. All validators return consistent result tuples with boolean status and error messages.

### Regex Patterns

| Pattern          | Purpose           | Example            | Notes                              |
| ---------------- | ----------------- | ------------------ | ---------------------------------- |
| `EMAIL_REGEX`    | Email validation  | `user@example.com` | Local + domain format              |
| `PHONE_REGEX`    | Phone validation  | `+351912345678`    | 9-12 digits, optional country code |
| `DATE_REGEX`     | Date validation   | `14-05-2026`       | Strict DD-MM-YYYY format           |
| `PASSWORD_REGEX` | Password strength | `Secure@123`       | Min 8 chars, 1 uppercase, 1 number |

### Validation Functions

#### `validate_non_empty(value: str, field_label: str) -> ValidationResult`

**Purpose**: Check that input text is not empty (whitespace-only strings are rejected).

**Returns**: `(bool, str)` – `(True, "")` on success or `(False, error_message)` on failure.

**Example**:

```python
from validators import validate_non_empty

success, msg = validate_non_empty("Alice", "Name")
# Returns: (True, "")

success, msg = validate_non_empty("  ", "Name")
# Returns: (False, "Name cannot be empty.")
```

---

#### `validate_email(value: str) -> ValidationResult`

**Purpose**: Validate email format against RFC-like pattern.

**Regex**: Allows alphanumeric, dots, underscores, `%`, `+`, `-` in local part; standard domain format.

**Returns**: `(bool, str)` – `(True, "")` on success or `(False, error_message)` on failure.

**Example**:

```python
success, msg = validate_email("user@example.com")
# Returns: (True, "")

success, msg = validate_email("invalid@.com")
# Returns: (False, "Invalid email format. Example: user@example.com")
```

---

#### `validate_phone(value: str) -> ValidationResult`

**Purpose**: Validate phone number format for national or international use.

**Pattern**:

- Optional country prefix: `+` followed by 1-3 digits
- Core number: 9-12 digits

**Returns**: `(bool, str)` – `(True, "")` on success or `(False, error_message)` on failure.

**Example**:

```python
success, msg = validate_phone("+351912345678")
# Returns: (True, "")

success, msg = validate_phone("912345678")
# Returns: (True, "")

success, msg = validate_phone("12345")
# Returns: (False, "Invalid phone format. Use 9-12 digits, optional country prefix (e.g., +351912345678).")
```

---

#### `validate_date(value: str) -> ValidationResult`

**Purpose**: Validate date format as DD-MM-YYYY with range checking for day (01-31) and month (01-12).

**Returns**: `(bool, str)` – `(True, "")` on success or `(False, error_message)` on failure.

**Example**:

```python
success, msg = validate_date("14-05-2026")
# Returns: (True, "")

success, msg = validate_date("32-13-2026")
# Returns: (False, "Invalid date format. Use DD-MM-YYYY.")

success, msg = validate_date("14/05/2026")
# Returns: (False, "Invalid date format. Use DD-MM-YYYY.")
```

---

#### `validate_password(value: str) -> ValidationResult`

**Purpose**: Ensure password meets minimum strength requirements.

**Requirements**:

- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 digit (0-9)

**Returns**: `(bool, str)` – `(True, "")` on success or `(False, error_message)` on failure.

**Example**:

```python
success, msg = validate_password("SecurePass123")
# Returns: (True, "")

success, msg = validate_password("weak")
# Returns: (False, "Invalid password. Minimum 8 chars, at least 1 uppercase letter and 1 number.")

success, msg = validate_password("nouppercase123")
# Returns: (False, "Invalid password. Minimum 8 chars, at least 1 uppercase letter and 1 number.")
```

---

#### `validate_number(value: str, field_label: str, minimum: float | None = None, maximum: float | None = None) -> ValidationResultWithValue`

**Purpose**: Parse and validate numeric input with optional range boundaries.

**Returns**: `(bool, str, float | None)` – `(True, "", parsed_value)` on success or `(False, error_message, None)` on failure.

**Example**:

```python
success, msg, val = validate_number("75.5", "Weight (kg)", minimum=50, maximum=150)
# Returns: (True, "", 75.5)

success, msg, val = validate_number("45.2", "Weight (kg)", minimum=50, maximum=150)
# Returns: (False, "Weight (kg) must be >= 50.", None)

success, msg, val = validate_number("abc", "Weight (kg)")
# Returns: (False, "Weight (kg) must be a numeric value.", None)
```

---

### Integration with CLI

Validators are called from CLI input routines to reject invalid entries:

```python
from utils.validators import validate_email, validate_password

# In registration flow
email = input("Enter email: ")
success, msg = validate_email(email)
if not success:
    print(f"Error: {msg}")
    return

password = input("Enter password: ")
success, msg = validate_password(password)
if not success:
    print(f"Error: {msg}")
    return
```

---

## Users Module (`users.py`)

### Purpose

Handles user account data structures and secure password hashing for authentication.

### Key Functions

#### `hash_password(password: str) -> str`

**Purpose**: Convert a plaintext password into a SHA-256 hash for secure storage.

**Algorithm**: SHA-256 (irreversible one-way hash).

**Returns**: Hexadecimal string (64 characters).

**Example**:

```python
from utils.users import hash_password

hashed = hash_password("MyPassword123")
# Returns: "abc123def456..." (64-char hex string)

# Same input always produces same hash
hashed2 = hash_password("MyPassword123")
# hashed == hashed2  (True)
```

**Security Notes**:

- One-way function: cannot reverse to get original password
- Deterministic: same input produces same hash (suitable for comparison)
- Not salted: simple implementation for student project
- For production: use bcrypt, scrypt, or Argon2

---

#### `generate_user(username: str, display_name: str, email: str, phone: str, password: str) -> User`

**Purpose**: Create a new user dictionary with all required fields and hashed password.

**Signature**:

```python
User = dict[str, int | str]
```

**Returns**: Dictionary with keys:

- `username` – Unique login identifier
- `display_name` – Human-readable name
- `email` – Contact email
- `phone` – Contact phone
- `password_hash` – SHA-256 hashed password (not plaintext)

**Example**:

```python
from utils.users import generate_user

user = generate_user(
    username="alice",
    display_name="Alice Smith",
    email="alice@example.com",
    phone="+351912345678",
    password="SecurePass123"
)
# Returns:
# {
#     "username": "alice",
#     "display_name": "Alice Smith",
#     "email": "alice@example.com",
#     "phone": "+351912345678",
#     "password_hash": "abc123..."
# }
```

**Workflow**:

1. Accept plaintext credentials
2. Hash password using `hash_password()`
3. Bundle all fields into user dict
4. Return to caller (typically `auth_service.register_user()`)

---

## Benchmark Module (`benchmark.py`)

### Purpose

Measure algorithm execution time and persist results to JSON for performance analysis. Used by the service layer when running sorting operations.

### Key Function

#### `run_benchmarks(algorithm: str, dataSize: int, callback: Callable, search_key: str | None = None) -> list[dict]`

**Purpose**: Execute a sorting/search algorithm, measure runtime, and save results to JSON.

**Signature**:

```python
def run_benchmarks(
    algorithm: str,                              # "bubble", "insertion", "merge", etc.
    dataSize: int,                               # Number of records processed
    callback: Callable[[], list[dict]],          # Function that runs the algorithm
    search_key: str | None = None                # Field being sorted/searched
) -> list[dict]
```

**Returns**: Result of the algorithm (list of sorted/matched records).

**Workflow**:

1. **Record Start Time**
   - Capture time before algorithm execution
   - Print status message

2. **Execute Callback**
   - Call user-provided function
   - Function contains the actual algorithm (bubble_sort, merge_sort, etc.)
   - May raise exceptions (caught and reported)

3. **Record End Time & Calculate Elapsed**
   - Capture time after execution
   - Calculate difference (rounded to 4 decimals)
   - Print status message

4. **Build Results Dict**

   ```python
   {
       "algorithm": "bubble",
       "data_size": 15000,
       "elapsed_time": 7.9052,
       "search_key": "body_fat_pct"
   }
   ```

5. **Persist to JSON**
   - Create `benchmarks/` folder if needed
   - File path: `benchmarks/{algorithm}_results.json`
   - Load existing results from file (if present)
   - Append new result to list
   - Write updated list back to file

6. **Return Algorithm Result**
   - Pass through the callback's return value (sorted/searched records)
   - Ensures transparent wrapping (calling code gets expected data)

**Example**:

```python
from utils.benchmark import run_benchmarks
from algorithms.sorting import bubble_sort

# Wrapper that calls bubble_sort with specific parameters
def benchmark_bubble():
    return bubble_sort(records, field="weight_kg", descending=False)

# Execute benchmark
result = run_benchmarks(
    algorithm="bubble",
    dataSize=15000,
    callback=benchmark_bubble,
    search_key="weight_kg"
)

# result is the sorted list of records
# benchmarks/bubble_results.json now contains timing data
```

---

### Benchmark Results File Format

**Example**: `benchmarks/bubble_results.json`

```json
[
  {
    "algorithm": "bubble",
    "data_size": 15000,
    "elapsed_time": 7.9052,
    "search_key": "body_fat_pct"
  },
  {
    "algorithm": "bubble",
    "data_size": 15000,
    "elapsed_time": 8.1234,
    "search_key": "weight_kg"
  }
]
```

**Fields**:

- `algorithm` – Name of sorting algorithm
- `data_size` – Number of records processed
- `elapsed_time` – Execution time in seconds (float, 4 decimals)
- `search_key` – Field that was sorted (for context)

---

### Benchmark Files Location

Results are stored in the workspace root:

```
benchmarks/
  ├── bubble_results.json      # All bubble sort benchmarks
  ├── insertion_results.json   # All insertion sort benchmarks
  └── merge_results.json       # All merge sort benchmarks
```

Each file contains an array of benchmark runs. New runs are appended, preserving history.

---

### Integration with Service Layer

The service layer uses benchmarking when sorting records:

```python
# In progress_service.py, sort_records() function
return run_benchmarks(
    "bubble",
    len(sort_space),
    lambda: bubble_sort(sort_space, field=sort_field, descending=descending),
    search_key=sort_field
)
```

**Benefits**:

- Transparent: calling code receives sorted records (no side effects)
- Historical: all runs are logged for later analysis
- Lightweight: minimal overhead (only ~1ms overhead for measurement)

---

### Error Handling

**File I/O Errors**:

- Try-catch around file operations
- Print warning if save fails
- Still return algorithm result (graceful degradation)

```python
try:
    os.makedirs("benchmarks", exist_ok=True)
    # ... read/write file ...
except IOError as e:
    print(f"Error saving benchmark results: {e}")
finally:
    return result  # Always return the algorithm result
```

---

## Type Aliases

```python
# From validators.py
ValidationResult = tuple[bool, str]
ValidationResultWithValue = tuple[bool, str, int | float | None]

# From users.py
User = dict[str, int | str]

# From benchmark.py (implicit)
BenchmarkResult = dict[str, str | float | int | None]
```

---

## Summary Table

| Module         | Function               | Purpose                        | Returns                    |
| -------------- | ---------------------- | ------------------------------ | -------------------------- |
| **validators** | `validate_non_empty()` | Check string is not empty      | `(bool, str)`              |
|                | `validate_email()`     | Check email format             | `(bool, str)`              |
|                | `validate_phone()`     | Check phone format             | `(bool, str)`              |
|                | `validate_date()`      | Check DD-MM-YYYY format        | `(bool, str)`              |
|                | `validate_password()`  | Check password strength        | `(bool, str)`              |
|                | `validate_number()`    | Parse & validate numeric range | `(bool, str, float\|None)` |
| **users**      | `hash_password()`      | SHA-256 hash password          | `str` (hex)                |
|                | `generate_user()`      | Create user dict               | `dict`                     |
| **benchmark**  | `run_benchmarks()`     | Measure & log algorithm time   | Algorithm result           |

---

## Testing

```bash
# Test validators
python -c "from src.utils.validators import validate_email; print(validate_email('test@example.com'))"

# Test users
python -c "from src.utils.users import hash_password; print(len(hash_password('test')))"

# Test benchmarks (via CLI sorting)
python src/main.py  # Use "sort" command to trigger benchmarks
```

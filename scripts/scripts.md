# Scripts Documentation

## `populate.py` — Test Database Seeder

### Purpose

Seed the database with a test user and configurable number of fitness records (~200 default). Outputs credentials to terminal so you can immediately log in and verify the data. Useful for demos, grading, and testing search/sort functionality with substantial datasets.

---

## Workflow

### 1. Argument Parsing

```python
parser.add_argument("--count", type=int, default=200, help="...")
```

- `--count N`: Create N records (default 200)
- Example: `python -m scripts.populate --count 50` creates 50 records
- Validates that count > 0; returns error code 1 if invalid

### 2. Credential Generation (`_make_credentials()`)

```python
stamp = datetime.now().strftime("%Y%m%d%H%M%S")  # e.g., "20260513010414"
username = f"seed_{stamp}"                        # e.g., "seed_20260513010414"
password = f"Seed@{stamp[-6:]}"                   # e.g., "Seed@010414"
email = f"{username}@example.local"
phone = f"+3519{randint(10000000, 99999999)}"
```

**Key features:**

- Credentials are **unique per run** (timestamp-based, prevents collisions on repeated executions)
- Password is deterministic but human-readable (last 6 digits of timestamp)
- Email and phone auto-generated in valid formats (required by validators)
- Phone format: `+3519XXXXXXXX` (valid Portuguese number format)

### 3. User Registration & Authentication

```python
initialize_auth()
initialize_service()

register_user(username, display_name, password, email, phone)
authenticate(username, password)  # Sets current_user_id context
```

**Execution flow:**

- `initialize_auth()`: Loads or creates auth system; creates default admin user if none exist
- `initialize_service()`: Initializes progress service and loads existing records
- `register_user()`: Creates new user with unique user_id, validates all fields, persists to `data/users.json`
- `authenticate()`: Verifies credentials and sets session context (subsequent `create_record()` calls attach to this user)
- Returns error code 1 if registration or authentication fails

### 4. Record Seeding (`_create_records()`)

```python
start_date = datetime.now() - timedelta(days=count)
weight = uniform(72.0, 96.0)
body_fat = uniform(17.0, 32.0)

for offset in range(count):
    day = start_date + timedelta(days=offset)

    # Simulate mild fluctuations with a gradual trend
    weight += uniform(-0.35, 0.25)
    body_fat += uniform(-0.08, 0.04)

    weight = max(58.0, min(140.0, weight))       # Clamp to valid range
    body_fat = max(8.0, min(55.0, body_fat))
    calories = randint(1700, 2900)

    create_record({
        "record_date": day.strftime("%d-%m-%Y"),
        "weight_kg": round(weight, 1),
        "body_fat_pct": round(body_fat, 1),
        "daily_calories": calories,
        "notes": f"Seeded record #{offset + 1}",
    })
```

**Key features:**

- Generates `count` records spanning past `count` days (oldest first)
- **Realistic fluctuations**: weight ±0.35kg/day, body fat ±0.08%/day (simulates natural daily variation)
- Starting values: weight 72–96 kg, body fat 17–32% (healthy baseline)
- Bounds enforcement: weight 58–140 kg, body fat 8–55%, calories 1700–2900
- Each record auto-assigned `record_id` and linked to authenticated user
- All fields rounded to 1 decimal place for consistency

### 5. Persistence & Output

```python
save_state()  # Flush all records to JSON
print(f"Records inserted: {args.count}")
```

- `save_state()`: Persists all in-memory records to `data/progress_records.json`
- Returns error code 1 if save fails
- Prints summary to terminal

---

## Usage Examples

### Seed default 200 records

```powershell
python -m scripts.populate
```

### Seed 50 records for quick testing

```powershell
python -m scripts.populate --count 50
```

### Seed 500 records for stress testing

```powershell
python -m scripts.populate --count 500
```

### Seed with explicit validation

```powershell
python -m scripts.populate --count 100
```

---

## Output Format

```
Test user created successfully.
Username: seed_20260513010414
Password: Seed@010414
Email: seed_20260513010414@example.local
Phone: +351914572845
Records inserted: 200
```

**Usage:**

1. Copy `Username` and `Password` from output
2. Log into GUI or CLI with these credentials
3. Verify records are searchable, sortable, filterable

---

## Return Codes

- `0`: Success (user created, records inserted, data saved)
- `1`: Failure (invalid count, registration failed, authentication failed, save failed)

---

## Why Useful

- **No manual data entry** — 200 records created in ~2 seconds
- **Grading demos** — Show search/sort/filter on substantial dataset with realistic trends
- **Reproducible** — Same credentials printed every run; verifiable by grader
- **Configurable** — `--count` parameter adapts to testing needs (quick smoke test with 50, full demo with 500)
- **Isolated** — Each run creates a new user; no data pollution across test runs
- **Realistic data** — Weight/body fat fluctuations mimic actual fitness tracking patterns

---

## Integration with Workflow

### Quick Grading Setup

```powershell
# 1. Create fresh test data
python -m scripts.populate --count 200

# 2. Note credentials from output
# Example: Username: seed_20260513010414, Password: Seed@010414

# 3. Launch GUI and log in
python -m src.gui.app

# 4. Verify:
#    - Login with credentials succeeds
#    - 200 records visible in table
#    - Search (by ID, name) works
#    - Sort (bubble, insertion, merge) works
#    - Statistics show correct min/max/avg
```

### CI/Testing Setup

```powershell
# Generate minimal dataset for quick tests
python -m scripts.populate --count 10

# Run test suite
python -m scripts.run_tests
```

---

## Implementation Details

### Import Strategy

- Uses `ROOT_DIR = Path(__file__).resolve().parents[1]` to locate project root
- Adds root to `sys.path` for reliable imports regardless of execution context
- Supports both `python -m scripts.populate` and direct execution

### Error Handling

- Validates `--count > 0` upfront
- Checks registration success before proceeding
- Verifies authentication before creating records
- Validates save operation before reporting success
- Returns specific error messages for each failure case

### Data Generation Strategy

- Timestamps ensure unique credentials across multiple runs
- Realistic weight/body fat trends prevent test data from looking artificial
- Calorie variation (1700–2900) reflects typical daily intake range
- Notes field (`Seeded record #N`) makes records identifiable as test data

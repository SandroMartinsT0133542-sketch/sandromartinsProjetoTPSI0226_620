# Scripts Module

The `scripts` module provides utility scripts for testing, seeding, and developing the fitness management application. These scripts are run from the command line and help with local testing, benchmarking, and data population.

---

## Overview

The scripts module contains:

- **`populate.py`** – Creates test users and seeds progress records with realistic data
- **`run_tests.py`** – Placeholder for automated test suite
- **`scripts.md`** – Documentation for running scripts

**Purpose**: Support development and testing workflows without modifying the main codebase.

---

## Populate Script (`populate.py`)

### Purpose

Create a test user with auto-generated credentials and insert randomized fitness progress records spanning multiple days. Useful for:

- Local testing with realistic data
- Benchmarking algorithms with large datasets
- Testing search/sort on varied data

### Command Line Usage

```bash
# Create 200 records (default)
python scripts/populate.py

# Create 1000 records
python scripts/populate.py --count 1000

# Create 50 records
python scripts/populate.py --count 50
```

### Output

The script prints generated credentials to terminal:

```
Registering user: seed_20260514143022
Password: Seed@143022
Email: seed_20260514143022@example.local
Phone: +35191234567
Created 200 progress records
Data saved successfully
```

Credentials can be used to log in and view/manipulate seeded data.

---

### Implementation Details

#### Argument Parser

```python
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a test user and seed progress records.")
    parser.add_argument("--count", type=int, default=200, help="Number of records to create (default: 200).")
    return parser
```

**Arguments**:

- `--count` – Number of progress records to create (default: 200)

---

#### Credential Generation

```python
def _make_credentials() -> tuple[str, str, str, str]:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    username = f"seed_{stamp}"
    password = f"Seed@{stamp[-6:]}"
    email = f"{username}@example.local"
    phone = f"+3519{randint(10000000, 99999999)}"
    return username, password, email, phone
```

**Generated Credentials**:

- **Username**: `seed_YYYYMMDDHHmmss` (timestamp-based, unique each run)
- **Password**: `Seed@HHmmss` (meets strength requirements: 8+ chars, uppercase, digit)
- **Email**: `seed_YYYYMMDDHHmmss@example.local`
- **Phone**: `+3519` + 8 random digits

**Why Timestamp-Based**:

- Guarantees uniqueness across multiple runs
- Easy to identify seeded users in database
- Allows multiple concurrent test users

---

#### Record Generation

```python
def _create_records(count: int) -> None:
    start_date = datetime.now() - timedelta(days=count)
    weight = uniform(72.0, 96.0)
    body_fat = uniform(17.0, 32.0)

    for offset in range(count):
        day = start_date + timedelta(days=offset)

        # Simulate mild fluctuations with a gradual trend
        weight += uniform(-0.35, 0.25)
        body_fat += uniform(-0.08, 0.04)

        weight = max(58.0, min(140.0, weight))
        # ... more data generation
```

**Workflow**:

1. **Start Date**
   - Begin `count` days ago
   - Creates realistic historical data

2. **Initial Values**
   - Weight: random 72-96 kg
   - Body fat: random 17-32%
   - Calories: random 1800-2500 cal

3. **Daily Fluctuations** (Loop for each day)
   - Weight varies by ±0.35 kg per day (realistic)
   - Body fat varies by ±0.08% per day (realistic)
   - Calories vary by ±200-300 cal per day
   - Clamp weight to safe range (58-140 kg)

4. **Trend Simulation**
   - Small positive bias toward weight loss (lean toward -0.25)
   - Gradual improvement in body fat
   - Realistic meal and workout patterns

---

#### Data Format

Each seeded record includes:

- `record_date` – DD-MM-YYYY format (one entry per day)
- `weight_kg` – Fluctuates daily
- `body_fat_pct` – Gradually improves
- `daily_calories` – Varies by day
- `notes` – Auto-generated fitness observations

**Example Records Created**:

```
Day 1: 2026-05-04, 73.2 kg, 23.1%, 2100 cal, "Light cardio"
Day 2: 2026-05-05, 72.9 kg, 22.9%, 2250 cal, "Good session"
Day 3: 2026-05-06, 73.1 kg, 23.2%, 2050 cal, "Rest day"
...
Day 200: 2026-05-14, 71.5 kg, 21.2%, 1900 cal, "Final workout"
```

---

### Complete Workflow

```
$ python scripts/populate.py --count 500

1. Initialize auth service
   → Load/create users.json

2. Generate unique credentials
   → Username: seed_20260514143022
   → Password: Seed@143022
   → etc.

3. Register new user
   → Add to auth_state["users"]
   → Save to users.json

4. Initialize progress service
   → Load/create progress_records.json

5. Generate 500 records (one per day)
   → Starting 500 days ago
   → Realistic fluctuations
   → Various notes

6. Create each record
   → Call create_record() for each
   → Auto-assign record_id (1 to 500)
   → Attach to seed user

7. Save to disk
   → Call save_state()
   → Write progress_records.json (grouped)
   → Write users.json (flat)

8. Print summary
   Registering user: seed_20260514143022
   Password: Seed@143022
   Email: seed_20260514143022@example.local
   Phone: +35191234567
   Created 500 progress records
   Data saved successfully
```

---

### Use Cases

**Testing Search Algorithms**:

```bash
python scripts/populate.py --count 10000
# Then search/sort in CLI to test performance on large datasets
```

**Benchmarking**:

```bash
python scripts/populate.py --count 15000
# Sorting 15000 records will generate benchmark data in benchmarks/*.json
```

**Testing Statistics**:

```bash
python scripts/populate.py --count 200
# Login with printed credentials
# View statistics of 200 realistic records
```

**Development**:

```bash
python scripts/populate.py
# Quick setup of test user without manual registration
```

---

## Run Tests Script (`run_tests.py`)

### Purpose

Placeholder for automated test suite. Currently not fully implemented in assignment.

**Future Use**:

- Unit tests for validators, models, services
- Integration tests for CRUD workflows
- Algorithm correctness tests
- Data persistence tests

### Placeholder Structure

```python
#!/usr/bin/env python3
"""
Automated test suite for the fitness management application.

Run with: python scripts/run_tests.py
"""

import sys
import unittest

# Test discovery and execution
if __name__ == "__main__":
    # TODO: Implement test suites
    pass
```

---

## Scripts Directory

```
scripts/
├── __init__.py           # Package marker
├── README.md             # This file
├── populate.py           # Data seeding utility
├── run_tests.py          # Test runner (placeholder)
└── scripts.md            # Usage documentation
```

---

## Integration Points

### With Auth Service

```python
from services.auth_service import initialize_auth, register_user, save_users

initialize_auth()
success, msg = register_user(username, display_name, password, email, phone)
save_users()
```

- Seeds random users
- Tests registration flow
- Verifies user persistence

### With Progress Service

```python
from services.progress_service import initialize_service, create_record, save_state
from services.auth_service import authenticate

authenticate(username, password)
initialize_service()

for day in range(count):
    record = create_record({...})

save_state()
```

- Creates records under seeded user
- Tests CRUD workflows
- Verifies persistence

### With Models

```python
from models.progress_entry import build_progress_entry

record = build_progress_entry(
    record_id=1,
    user_id=uid,
    record_date=date_str,
    weight_kg=weight,
    body_fat_pct=body_fat,
    daily_calories=calories,
    notes=notes,
)
```

- Validates model construction
- Tests type normalization

---

## Example: Manual Testing Workflow

```bash
# Step 1: Populate with test data
$ python scripts/populate.py --count 1000
Registering user: seed_20260514143022
Password: Seed@143022
...

# Step 2: Run application
$ python src/main.py

# Step 3: Log in with seeded credentials
> Enter username: seed_20260514143022
> Enter password: Seed@143022
> Login successful

# Step 4: Test features
> Enter action: search
> Enter field: weight
> Enter value: 73
> Enter algorithm: binary
> Found 150 records...

> Enter action: sort
> Enter field: body_fat
> Enter algorithm: merge
> Sorted 1000 records in 0.2345 seconds
> Results saved to benchmarks/merge_results.json

# Step 5: View statistics
> Enter action: statistics
> Count: 1000
> Average weight: 72.8 kg
> Average body fat: 22.1%
> Min weight: 58.0 kg
> Max weight: 96.3 kg
> Total calories: 2,150,000
```

---

## Command Reference

| Command                                    | Purpose                        |
| ------------------------------------------ | ------------------------------ |
| `python scripts/populate.py`               | Create 200 test records        |
| `python scripts/populate.py --count 500`   | Create 500 test records        |
| `python scripts/populate.py --count 10000` | Large dataset for benchmarking |
| `python scripts/run_tests.py`              | Run automated tests (future)   |

---

## Notes

- Seeded data is stored in the same `data/` directory as regular data
- Multiple runs of populate.py will create multiple users (different timestamps)
- Each user's records are isolated by `user_id`
- Data persists between application runs
- Delete records or users manually if cleanup needed

---

## Testing Utilities

To manually test components:

```bash
# Test validators
python -c "from src.utils.validators import validate_email; print(validate_email('test@example.com'))"

# Test models
python -c "from src.models.progress_entry import build_progress_entry; print(build_progress_entry(1, 1, '14-05-2026', 75.5, 22.3, 2150, 'test'))"

# Test algorithms
python -c "from src.algorithms.sorting import bubble_sort; records = [{'id': 1, 'w': 3}, {'id': 2, 'w': 1}]; print(bubble_sort(records, 'w'))"
```

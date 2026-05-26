# Fitness Management System (FastAPI + PostgreSQL)

Small Python project exposing a FastAPI HTTP service for managing fitness progress records stored in PostgreSQL.

Default login: `admin` / `admin` (created automatically on first run if no users exist)

## Quick start

### Option A: Start PostgreSQL with Docker Compose (recommended)

1. Start PostgreSQL:

```powershell
docker compose up -d
```

2. Create local environment file:

```powershell
Copy-Item .env.example .env
```

3. Start the API:

```powershell
python -m alembic upgrade head
uvicorn src.main:app --reload
```

### Option B: Use an existing PostgreSQL instance

1. Create and activate the virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies (if needed):

```powershell
pip install -r requirements.txt
```

3. Configure environment variables:

```powershell
Copy-Item .env.example .env
```

Update `DATABASE_URL` in `.env` if your PostgreSQL credentials/host differ from defaults.

4. Run the API service:

```powershell
python -m alembic upgrade head
uvicorn src.main:app --reload
```

5. Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## API Structure

- `src/routes/auth.py` - JWT auth routes (`/auth/register`, `/auth/login`, `/auth/me`)
- `src/routes/records.py` - Record CRUD routes (`/records`)
- `src/routes/search.py` - Search/sort/filter routes (`/records/search`, `/records/sort`, filters)
- `src/routes/statistics.py` - Statistics route (`/records/statistics`)
- `src/main.py` - Health endpoints (`/health`, `/health/db`)

## Documentation

Additional documentation files:

- **[OPERATORS.md](OPERATORS.md)** — Search and filter operators (equals, like, greater than, between, etc.)
- **[benchmarks/README.md](benchmarks/README.md)** — Benchmark result format, generation workflow, and analysis notes
- **[scripts/README.md](scripts/README.md)** — Utility scripts documentation, including `populate.py` for seeding test data
- **[src/utils/README.md](src/utils/README.md)** — Utility functions documentation (validators, user management, benchmarking)
- **[src/algorithms/README.md](src/algorithms/README.md)** — Manual implementations of sorting and searching algorithms with workflows and examples
- **[src/models/README.md](src/models/README.md)** — Record structure, parsing, serialization, and data flow
- **[src/store/README.md](src/store/README.md)** — JSON storage management, including file structure and data handling
- **[src/services/README.md](src/services/README.md)** — Business logic and service layer documentation, including record management, filtering, and statistics calculations

## Project layout

`src/algorithms/sorting.py` and `src/algorithms/searching.py` — manual sort/search algorithms.
`src/models/progress_entry.py` — record normalization and serialization helpers.
`src/store/storage.py` — persistence helpers for JSON files.
`src/utils/validators.py`, `src/utils/users.py`, `src/utils/benchmark.py` — validation, helper utilities, and performance tracking.
`benchmarks/` — benchmark results stored per algorithm as JSON files.

## Persistence

- Primary storage: PostgreSQL (configured via `DATABASE_URL` in `.env`).
- Schema changes are managed via Alembic migrations (`python -m alembic upgrade head`).
- Default admin user is seeded on first startup when no users exist.

## Database Migrations (Alembic)

Create a migration after changing ORM models:

```powershell
python -m alembic revision --autogenerate -m "describe_change"
```

Apply all pending migrations:

```powershell
python -m alembic upgrade head
```

Check current DB revision:

```powershell
python -m alembic current
```

## Benchmarking

- Benchmark results are stored in `benchmarks/` directory, organized by algorithm (e.g., `benchmarks/bubble_results.json`).
- Each benchmark entry includes:
  - `algorithm`: Name of the sorting algorithm (e.g., "bubble")
  - `data_size`: Number of records sorted
  - `elapsed_time`: Time taken to sort (in seconds, rounded to 4 decimal places)
  - `search_key`: The key used for sorting (e.g., "weight_kg", "body_fat_pct")

Records and users are read at startup. The UI and services provide explicit save operations and may prompt to save on exit.

## Running tests

Run the included test runner (if you use the provided virtual environment):

```powershell
python scripts/run_tests.py
```

Or use unittest discovery directly:

```powershell
python -m unittest discover -s tests
```

## Features

- CRUD for fitness progress records with validation.
- Manual implementations of linear/binary search and bubble/insertion/merge sort.
- Filtering and basic statistics (count, averages, min/max, totals).
- PostgreSQL-backed persistence with Alembic migrations.
- FastAPI endpoints for auth, CRUD, searching, sorting, filtering, and statistics.

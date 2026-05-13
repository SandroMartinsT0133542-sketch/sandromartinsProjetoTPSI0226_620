# Fitness Management System (GUI + JSON)

Small Python project providing a Tkinter GUI and a fallback CLI for managing fitness progress records stored in JSON files.

Default login: `admin` / `Admin@2026` (present for demo; change before production)

## Quick start

1. Create and activate the virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies (if needed):

```powershell
pip install -r requirements.txt
```

3. Run the application (GUI opens by default):

```powershell
python src/main.py
```

If Tkinter is unavailable the application will fall back to a CLI alternative.

## Documentation

Additional documentation files:

- **[OPERATORS.md](OPERATORS.md)** — Search and filter operators (equals, like, greater than, between, etc.)
- **[scripts/scripts.md](scripts/scripts.md)** — Utility scripts documentation, including `populate.py` for seeding test data

## Project layout

`src/algorithms/sorting.py` — manual sorting algorithms (bubble, insertion, merge).
`src/store/storage.py` — persistence helpers for JSON files.
`src/utils/validators.py`, `src/utils/users.py` — validation and helper utilities.
`src/utils/benchmark.py` — performance benchmarking for sorting algorithms (tracks algorithm, data size, execution time, and search key).
`benchmarks/` — benchmark results stored per algorithm as JSON files.

## Persistence

- Records file: `data/progress_records.json`
- Users file: `data/users.json`

## Benchmarking

- Benchmark results are stored in `benchmarks/` directory, organized by algorithm (e.g., `benchmarks/bubble_sort.json`).
- Each benchmark entry includes:
  - `algorithm`: Name of the sorting algorithm (e.g., "bubble_sort")
  - `data_size`: Number of records sorted
  - `elapsed_time`: Time taken to sort (in seconds, rounded to 4 decimal places)
  - `search_key`: The key used for sorting (e.g., "weight", "body_fat")

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
- JSON-backed persistence for records and users.
- Tkinter GUI with dialogs for adding/updating records.

# Fitness Management System (GUI + JSON)

Small Python project providing a Tkinter GUI and a fallback CLI for managing fitness progress records stored in JSON files.

Default login: `admin` / `admin` (created automatically on first run if no users exist)

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

- Records file: `data/progress_records.json`
- Users file: `data/users.json`

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
- JSON-backed persistence for records and users.
- Tkinter GUI with dialogs for adding/updating records.

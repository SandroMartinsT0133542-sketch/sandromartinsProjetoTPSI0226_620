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

## Project layout

- `src/main.py` — application entry point.
- `src/gui/app.py`, `src/gui/login_view.py`, `src/gui/main_view.py`, `src/gui/add_record_dialog.py`, `src/gui/record_table.py` — GUI code and dialogs.
- `src/algorithms/searching.py` — manual search algorithms (linear, binary).
- `src/algorithms/sorting.py` — manual sorting algorithms (bubble, insertion).
- `src/services/auth_service.py` — user sign up / sign in (JSON-backed).
- `src/services/progress_service.py` — CRUD, sorting, searching, statistics and filtering.
- `src/models/progress_entry.py` — data model and normalization helpers.
- `src/data/storage.py` — persistence helpers for JSON files.
- `src/utils/validators.py`, `src/utils/users.py` — validation and helper utilities.
- `data/progress_records.json`, `data/users.json` — default JSON stores (sample/demo data).
- `scripts/run_tests.py` — convenience script to run the test suite.
- `tests/` — place for unit tests (if present).

## Persistence

- Records file: `data/progress_records.json`
- Users file: `data/users.json`

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
- Manual implementations of linear/binary search and bubble/insertion sort.
- Filtering and basic statistics (count, averages, min/max, totals).
- JSON-backed persistence for records and users.
- Tkinter GUI with dialogs for adding/updating records; CLI fallback available.

## Notes and TODOs

- [TODO] Add unit tests for all CRUD, search/sort and validation flows.
- [TODO] Add a quick database reset/seed command for demos.
- [TODO] Improve CLI output formatting for wide terminals.

If you'd like, I can run the tests now or open a PR with this README change.

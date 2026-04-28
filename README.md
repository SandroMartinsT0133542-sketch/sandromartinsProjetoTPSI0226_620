# Fitness Management System (GUI + JSON)

Python school project for managing fitness progress records through a small Tkinter interface with JSON persistence.

Default login: `admin` / `Admin@2026`

You can also create a new account from the GUI or the fallback CLI before signing in.

## Current Features

- Create, list, search, update, and delete records.
- Manual search algorithms: linear and binary.
- Manual sorting algorithms: bubble and insertion.
- Statistics: count, averages, min/max, and total calories.
- Weight-range filtering.
- Regex and numeric validation for user input.
- Sign up and sign in with a second JSON file for users.
- Login system backed by a second JSON file.
- Save on demand and save prompt on exit.
- Sample-data loader for quick demo/testing.
- Small GUI for day-to-day use.

## Project Structure

- [src/main.py](src/main.py): application entry point.
- [src/gui/app.py](src/gui/app.py): Tkinter interface.
- [src/cli/app.py](src/cli/app.py): interactive menu and prompts.
- [src/services/auth_service.py](src/services/auth_service.py): JSON-backed login handling.
- [src/services/progress_service.py](src/services/progress_service.py): CRUD, search, sorting, statistics, filtering, and sample records.
- [src/data/storage.py](src/data/storage.py): JSON storage setup and persistence.
- [src/models/progress_entry.py](src/models/progress_entry.py): record normalization helpers.
- [src/algorithms/searching.py](src/algorithms/searching.py): manual search algorithms.
- [src/algorithms/sorting.py](src/algorithms/sorting.py): manual sorting algorithms.
- [src/utils/validators.py](src/utils/validators.py): validation helpers.

## How To Run

1. Activate the virtual environment.

```powershell
.venv\Scripts\Activate.ps1
```

2. Start the application.

```powershell
python src/main.py
```

The GUI opens by default. If Tkinter cannot start in your environment, the app falls back to the CLI.

## Demo Data

Use menu option `10` in the CLI to load three sample records into the JSON store and save them immediately. This is useful for fast smoke tests and grading demos.

## Persistence

- Database file: `data/progress_records.json`
- User file: `data/users.json`
- Records are loaded at startup.
- Changes can be saved from the menu.
- Exiting asks whether to save before closing.

## Requirements Checklist

### Main Entity

- [done] Use one main fitness entity with 5+ attributes.
- [done] Generate a unique ID automatically for each new record.

### CRUD Flow

- [done] Create new records from the CLI.
- [done] List all stored records.
- [done] Search records by multiple fields.
- [done] Update existing records with validation.
- [done] Delete records with confirmation.

### Search and Sorting

- [done] Implement linear search manually.
- [done] Implement binary search manually.
- [done] Implement bubble sort manually.
- [done] Implement insertion sort manually.
- [done] Allow sorting by selected field.
- [done] Allow ascending and descending order.

### Statistics and Filters

- [done] Show record count.
- [done] Show average weight.
- [done] Show average body fat.
- [done] Show minimum and maximum weight.
- [done] Show total calories.
- [done] Filter records by weight range.

### Validation

- [done] Validate email format with regex.
- [done] Validate phone format with regex.
- [done] Validate date format with regex.
- [done] Validate password strength with regex.
- [done] Validate numeric fields with range checks.
- [done] Show specific error messages for invalid input.

### Persistence

- [done] Persist data in JSON.
- [done] Support sign up and sign in.
- [done] Store users in a second JSON file.
- [done] Load records at startup.
- [done] Save records on demand.
- [done] Prompt to save before exiting.
- [done] Handle database read/write errors safely.

### Architecture and Code Quality

- [done] Split the project into multiple modules.
- [done] Keep CLI logic separate from service logic.
- [done] Keep search and sort algorithms in dedicated modules.
- [done] Use try/except around persistence boundaries.
- [done] Keep helper functions small and single-purpose.

### Demo and Usability

- [done] Provide a sample-data loader for quick demos.
- [done] Make the app runnable from the main entry point.
- [done] Keep the README aligned with the current implementation.

### Still Open

- [TODO] Add automated tests for CRUD, search, sorting, and validation flows.
- [TODO] Add a database reset option for quick clean demos.
- [TODO] Improve output formatting for long notes and wider terminal screens.
- [TODO] Add import/export support if the assignment later requires file exchange.

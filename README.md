# Fitness Management System (CLI + JSON)

School project for a Python management system focused on fitness tracking.

Current status: planning and project structure only.

## Goal

Develop a complete management system with CLI interface and persistent data storage (JSON), aligned with assignment grading criteria.

## Development Decision

- Procedural and modular approach (no class-based architecture for now).
- Keep files as placeholders during this phase.
- No implementation code in this stage; only structure and planning.

## Functional Requirements To Cover

1. Data registration:

- Create new records with at least 5 attributes.
- Auto-generate unique ID.

2. Query and search:

- List all records.
- Search by ID, name, and other relevant fields.
- Use at least 2 search algorithms (for example linear and binary search).

3. Update:

- Edit existing records with validation.

4. Delete:

- Remove records with user confirmation.

5. Sorting:

- Implement at least 2 manual sorting algorithms.
- Allow sorting by selected field and ascending/descending order.

6. Statistics and processing:

- Averages/totals/counts.
- Min/max values.
- Filters by threshold/range.

## Validation Requirements (Regex)

- Validate at least 3 data types (for example email, phone, password, date).
- Block invalid input.
- Show clear and specific error messages.

## Persistence Requirements

- JSON storage.
- Load on startup.
- Save on demand.
- Save on program exit with S/N confirmation.

## Technical Requirements

- Modularization using multiple files.
- Exception handling with try/except.

## Project Structure (Placeholder Only)

```
.
|-- README.md
|-- data/
|   `-- progress_records.json
`-- src/
	|-- main.py
	|-- cli/
	|   |-- __init__.py
	|   `-- app.py
	|-- services/
	|   |-- __init__.py
	|   `-- progress_service.py
	|-- algorithms/
	|   |-- __init__.py
	|   |-- searching.py
	|   `-- sorting.py
	|-- utils/
	|   |-- __init__.py
	|   `-- validators.py
	|-- data/
	|   |-- __init__.py
	|   `-- storage.py
	`-- models/
		|-- __init__.py
		`-- progress_entry.py
```

## Module Responsibility Map

- [src/main.py](src/main.py): Application entry point and startup handoff to CLI.
- [src/cli/app.py](src/cli/app.py): User interaction flow (menu, prompts, and operation handlers).
- [src/services/progress_service.py](src/services/progress_service.py): Core business operations (CRUD, search, sorting, statistics, filtering).
- [src/models/progress_entry.py](src/models/progress_entry.py): Record dictionary shape helpers (build/parse/serialize).
- [src/algorithms/searching.py](src/algorithms/searching.py): Manual search algorithms (linear and binary).
- [src/algorithms/sorting.py](src/algorithms/sorting.py): Manual sorting algorithms (bubble and insertion).
- [src/utils/validators.py](src/utils/validators.py): Input validation helpers (regex and numeric constraints).
- [src/data/storage.py](src/data/storage.py): JSON persistence functions (load and save).

- [src/**init**.py](src/__init__.py): Top-level package marker and scope description.
- [src/cli/**init**.py](src/cli/__init__.py): CLI package intent and export surface.
- [src/services/**init**.py](src/services/__init__.py): Services package intent and export surface.
- [src/models/**init**.py](src/models/__init__.py): Models package intent and export surface.
- [src/algorithms/**init**.py](src/algorithms/__init__.py): Algorithms package intent and export surface.
- [src/utils/**init**.py](src/utils/__init__.py): Utilities package intent and export surface.
- [src/data/**init**.py](src/data/__init__.py): Data package intent and export surface.

## Next Step

Start implementing modules one by one, beginning with input validation and JSON persistence.

## Environment Setup

1. Create and use the virtual environment:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`

2. Install dependencies (currently placeholder list):

- `pip install -r requirements.txt`

3. Add new packages to `requirements.txt` as implementation begins.

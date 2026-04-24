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

## Next Step

Start implementing modules one by one, beginning with input validation and JSON persistence.

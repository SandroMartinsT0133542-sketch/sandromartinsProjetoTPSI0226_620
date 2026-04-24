"""CLI layer: handles user interaction and delegates logic to services."""

from services.progress_service import (
	compute_statistics,
	create_record,
	delete_record,
	filter_weight_range,
	find_by_id,
	list_records,
	search_records,
	sort_records,
	update_record,
)


def _show_menu() -> None:
	"""Display all available CLI options for the user."""
	pass


def _print_record(record: dict) -> None:
	"""Render one record in a readable single-line or multi-line format."""
	pass


def _create_record_flow() -> None:
	"""Collect input, validate fields, and create a new record."""
	pass


def _list_records_flow() -> None:
	"""Fetch all records and print them in the CLI."""
	pass


def _search_records_flow() -> None:
	"""Ask for field/algorithm and show matching records."""
	pass


def _update_record_flow() -> None:
	"""Collect partial updates for an existing record and apply validation."""
	pass


def _delete_record_flow() -> None:
	"""Request deletion confirmation and remove a record by ID."""
	pass


def _sort_records_flow() -> None:
	"""Request sorting criteria and display sorted results."""
	pass


def _statistics_flow() -> None:
	"""Show aggregate statistics (count, average, min, max)."""
	pass


def _filter_records_flow() -> None:
	"""Filter records by weight range and display matching items."""
	pass


def _save_flow() -> None:
	"""Persist current in-memory records to JSON storage."""
	pass


def run_app() -> None:
	"""Run the main command loop until user chooses to exit."""
	# Keep imported service functions referenced for scaffold clarity.
	_ = (
		list_records,
		create_record,
		find_by_id,
		update_record,
		delete_record,
		search_records,
		sort_records,
		compute_statistics,
		filter_weight_range,
	)
	pass


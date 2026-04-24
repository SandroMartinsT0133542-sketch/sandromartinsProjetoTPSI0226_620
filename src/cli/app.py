"""CLI layer: handles user interaction and delegates logic to services."""

from typing import Any, Callable, cast


# type validator callbale with string, string or string, callable[[str], tuple[bool, str]], optional field label for error messages

ValidatorOne = Callable[[str], tuple[bool, str]]
ValidatorTwo = Callable[[str, str], tuple[bool, str]]
Validator = ValidatorOne | ValidatorTwo
Record = dict[str, Any]

from services.progress_service import (
    compute_statistics,
    create_record,
    delete_record,
    filter_weight_range,
    find_by_id,
    initialize_service,
    list_records,
    save_state,
    search_records,
    seed_sample_records,
    sort_records,
    update_record,
)

from utils.validators import (
    validate_date,
    validate_email,
    validate_float,
    validate_int,
    validate_non_empty,
    validate_password,
    validate_phone,
)


def _show_menu() -> None:
    """Display all available CLI options for the user."""
    print("\n=== Fitness Management System ===")
    print("1. Create record")
    print("2. List records")
    print("3. Search records")
    print("4. Update record")
    print("5. Delete record")
    print("6. Sort records")
    print("7. Statistics")
    print("8. Filter by weight range")
    print("9. Save now")
    print("10. Load sample records")
    print("0. Exit")


def _print_record(record: Record) -> None:
    """Render one record in a readable single-line format."""
    print(
        f"ID: {record['record_id']} | Name: {record['client_name']} | "
        f"Date: {record['record_date']} | Weight: {record['weight_kg']} kg | "
        f"Body Fat: {record['body_fat_pct']}% | Calories: {record['daily_calories']}"
    )


# str, validator: Callable[[str], tuple[bool, str]], field_label: str | None = None) -> str:
def _prompt_text(prompt: str, validator: Validator, field_label: str | None = None) -> str:
    """Prompt until a text validator accepts the value."""
    while True:
        value = input(prompt).strip()
        if field_label is None:
            is_valid, message = cast(ValidatorOne, validator)(value)
        else:
            is_valid, message = cast(ValidatorTwo, validator)(value, field_label)
        if is_valid:
            return value
        print(f"Error: {message}")


def _prompt_float(prompt: str, field_label: str, minimum: float | None = None, maximum: float | None = None) -> float:
    """Prompt until a float value passes validation."""
    while True:
        is_valid, message, parsed = validate_float(input(prompt).strip(), field_label, minimum=minimum, maximum=maximum)
        if is_valid and parsed is not None:
            return parsed
        print(f"Error: {message}")


def _prompt_int(prompt: str, field_label: str, minimum: int | None = None, maximum: int | None = None) -> int:
    """Prompt until an integer value passes validation."""
    while True:
        is_valid, message, parsed = validate_int(input(prompt).strip(), field_label, minimum=minimum, maximum=maximum)
        if is_valid and parsed is not None:
            return parsed
        print(f"Error: {message}")


def _create_record_flow() -> None:
    """Collect input, validate fields, and create a new record."""
    payload: dict[str, Any] = {
        "client_name": _prompt_text("Client name: ", validate_non_empty, "Client name"),
        "email": _prompt_text("Email: ", validate_email),
        "phone": _prompt_text("Phone (+country optional): ", validate_phone),
        "record_date": _prompt_text("Record date (DD-MM-YYYY): ", validate_date),
        "password": _prompt_text("Password: ", validate_password),
        "weight_kg": _prompt_float("Weight (kg): ", "Weight", minimum=1.0, maximum=500.0),
        "body_fat_pct": _prompt_float("Body fat (%): ", "Body fat", minimum=1.0, maximum=80.0),
        "daily_calories": _prompt_int("Daily calories: ", "Daily calories", minimum=500, maximum=12000),
        "notes": input("Notes: ").strip(),
    }
    created = create_record(payload)
    print(f"Record created with ID {created['record_id']}.")


def _list_records_flow() -> None:
    """Fetch all records and print them in the CLI."""
    records = list_records()
    if not records:
        print("No records available.")
        return
    for record in records:
        _print_record(record)


def _search_records_flow() -> None:
    """Ask for field/algorithm and show matching records."""
    field_map = {
        "1": ("record_id", "ID", "int"),
        "2": ("client_name", "Name", "text"),
        "3": ("email", "Email", "text"),
        "4": ("record_date", "Date", "text"),
        "5": ("weight_kg", "Weight", "float"),
        "6": ("body_fat_pct", "Body fat", "float"),
        "7": ("daily_calories", "Calories", "int"),
    }
    print("Search by: 1) ID  2) Name  3) Email  4) Date  5) Weight  6) Body Fat  7) Calories")
    field_choice = input("Option: ").strip()
    selected = field_map.get(field_choice)
    if selected is None:
        print("Invalid field option.")
        return

    field, label, field_type = selected
    print("Algorithm: 1) Linear  2) Binary")
    algorithm = "binary" if input("Option: ").strip() == "2" else "linear"

    if field_type == "int":
        target = _prompt_int(f"{label} value: ", label)
    elif field_type == "float":
        target = _prompt_float(f"{label} value: ", label)
    else:
        target = input(f"{label} value: ").strip()

    matches = search_records(field=field, target=target, algorithm=algorithm)
    if not matches:
        print("No matching records found.")
        return
    for record in matches:
        _print_record(record)


def _update_record_flow() -> None:
    """Collect partial updates for an existing record and apply validation."""
    record_id = _prompt_int("Record ID to update: ", "Record ID", minimum=1)
    existing = find_by_id(record_id)
    if existing is None:
        print("Record not found.")
        return

    print("Leave fields empty to keep current values.")
    updates: dict[str, Any] = {}

    name_value = input(f"Client name [{existing['client_name']}]: ").strip()
    if name_value:
        is_valid, message = validate_non_empty(name_value, "Client name")
        if not is_valid:
            print(f"Error: {message}")
            return
        updates["client_name"] = name_value

    email_value = input(f"Email [{existing['email']}]: ").strip()
    if email_value:
        is_valid, message = validate_email(email_value)
        if not is_valid:
            print(f"Error: {message}")
            return
        updates["email"] = email_value

    phone_value = input(f"Phone [{existing['phone']}]: ").strip()
    if phone_value:
        is_valid, message = validate_phone(phone_value)
        if not is_valid:
            print(f"Error: {message}")
            return
        updates["phone"] = phone_value

    date_value = input(f"Date [{existing['record_date']}]: ").strip()
    if date_value:
        is_valid, message = validate_date(date_value)
        if not is_valid:
            print(f"Error: {message}")
            return
        updates["record_date"] = date_value

    password_value = input("Password [hidden]: ").strip()
    if password_value:
        is_valid, message = validate_password(password_value)
        if not is_valid:
            print(f"Error: {message}")
            return
        updates["password"] = password_value

    weight_value = input(f"Weight [{existing['weight_kg']}]: ").strip()
    if weight_value:
        is_valid, message, parsed = validate_float(weight_value, "Weight", minimum=1.0, maximum=500.0)
        if not is_valid or parsed is None:
            print(f"Error: {message}")
            return
        updates["weight_kg"] = parsed

    body_fat_value = input(f"Body fat [{existing['body_fat_pct']}]: ").strip()
    if body_fat_value:
        is_valid, message, parsed = validate_float(body_fat_value, "Body fat", minimum=1.0, maximum=80.0)
        if not is_valid or parsed is None:
            print(f"Error: {message}")
            return
        updates["body_fat_pct"] = parsed

    calories_value = input(f"Calories [{existing['daily_calories']}]: ").strip()
    if calories_value:
        is_valid, message, parsed = validate_int(calories_value, "Daily calories", minimum=500, maximum=12000)
        if not is_valid or parsed is None:
            print(f"Error: {message}")
            return
        updates["daily_calories"] = parsed

    notes_value = input(f"Notes [{existing['notes']}]: ").strip()
    if notes_value:
        updates["notes"] = notes_value

    if not updates:
        print("No changes provided.")
        return

    if update_record(record_id, updates):
        print("Record updated successfully.")
    else:
        print("Could not update record.")


def _delete_record_flow() -> None:
    """Request deletion confirmation and remove a record by ID."""
    record_id = _prompt_int("Record ID to delete: ", "Record ID", minimum=1)
    existing = find_by_id(record_id)
    if existing is None:
        print("Record not found.")
        return

    _print_record(existing)
    confirmation = input("Confirm delete (S/N): ").strip().upper()
    if confirmation != "S":
        print("Delete canceled.")
        return

    if delete_record(record_id):
        print("Record deleted.")
    else:
        print("Could not delete record.")


def _sort_records_flow() -> None:
    """Request sorting criteria and display sorted results."""
    field_map = {
        "1": "client_name",
        "2": "record_date",
        "3": "weight_kg",
        "4": "body_fat_pct",
        "5": "daily_calories",
    }
    print("Sort field: 1) Name  2) Date  3) Weight  4) Body Fat  5) Calories")
    field_choice = input("Option: ").strip()
    field = field_map.get(field_choice)
    if field is None:
        print("Invalid field option.")
        return

    print("Algorithm: 1) Bubble  2) Insertion")
    algorithm = "bubble" if input("Option: ").strip() == "1" else "insertion"
    order = input("Order (C for ascending / D for descending): ").strip().upper()
    descending = order == "D"

    try:
        sorted_records = sort_records(field=field, algorithm=algorithm, descending=descending)
    except ValueError as error:
        print(f"Error: {error}")
        return

    if not sorted_records:
        print("No records to sort.")
        return
    for record in sorted_records:
        _print_record(record)


def _statistics_flow() -> None:
    """Show aggregate statistics (count, average, min, max)."""
    stats = compute_statistics()
    if stats["count"] == 0:
        print("No records for statistics.")
        return

    print(f"Total records: {stats['count']}")
    print(f"Average weight: {stats['avg_weight']:.2f} kg")
    print(f"Average body fat: {stats['avg_body_fat']:.2f}%")
    print(f"Minimum weight: {stats['min_weight']:.2f} kg")
    print(f"Maximum weight: {stats['max_weight']:.2f} kg")
    print(f"Total calories: {stats['total_calories']}")


def _filter_records_flow() -> None:
    """Filter records by weight range and display matching items."""
    minimum = _prompt_float("Minimum weight: ", "Minimum weight", minimum=0.0)
    maximum = _prompt_float("Maximum weight: ", "Maximum weight", minimum=0.0)
    if minimum > maximum:
        print("Error: Invalid range. Minimum must be less than or equal to maximum.")
        return

    filtered = filter_weight_range(minimum=minimum, maximum=maximum)
    if not filtered:
        print("No records found in that range.")
        return
    for record in filtered:
        _print_record(record)


def _save_flow() -> None:
    """Persist current in-memory records to SQLite storage."""
    if save_state():
        print("Records saved successfully.")
    else:
        print("Save failed.")


def _seed_sample_records_flow() -> None:
    """Populate the app with a small demo dataset and persist it."""
    created = seed_sample_records()
    if created == 0:
        print("Sample records were not loaded because data already exists.")
        return

    if save_state():
        print(f"Loaded and saved {created} sample records.")
    else:
        print("Sample records were created in memory but could not be saved.")


def run_app() -> None:
    """Run the main command loop until user chooses to exit."""
    initialize_service()
    while True:
        _show_menu()
        try:
            option = input("Select an option: ").strip()
        except EOFError:
            print()
            break

        match option:
            case "1":
                _create_record_flow()
            case "2":
                _list_records_flow()
            case "3":
                _search_records_flow()
            case "4":
                _update_record_flow()
            case "5":
                _delete_record_flow()
            case "6":
                _sort_records_flow()
            case "7":
                _statistics_flow()
            case "8":
                _filter_records_flow()
            case "9":
                _save_flow()
            case "10":
                _seed_sample_records_flow()
            case "0":
                try:
                    save_choice = input("Save before exit? (S/N): ").strip().upper()
                except EOFError:
                    save_choice = "N"
                if save_choice == "S":
                    _save_flow()
                print("Goodbye.")
                break
            case _:
                print("Invalid option. Try again.")

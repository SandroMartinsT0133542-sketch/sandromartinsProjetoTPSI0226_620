"""Validation helpers for CLI input and field constraints."""

import re


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^(\+\d{1,3})?\d{9,12}$")
DATE_REGEX = re.compile(r"^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*\d).{8,}$")


def validate_non_empty(value: str, field_label: str) -> tuple[bool, str]:
	"""Validate that input text is not empty."""
	if value.strip() == "":
		return False, f"{field_label} cannot be empty."
	return True, ""


def validate_email(value: str) -> tuple[bool, str]:
	"""Validate email format using regex rules."""
	if not EMAIL_REGEX.match(value):
		return False, "Invalid email format. Example: user@example.com"
	return True, ""


def validate_phone(value: str) -> tuple[bool, str]:
	"""Validate phone number format (national/international style)."""
	if not PHONE_REGEX.match(value):
		return False, "Invalid phone format. Use 9-12 digits, optional country prefix (e.g., +351912345678)."
	return True, ""


def validate_date(value: str) -> tuple[bool, str]:
	"""Validate date format (DD-MM-YYYY)."""
	if not DATE_REGEX.match(value):
		return False, "Invalid date format. Use DD-MM-YYYY."
	return True, ""


def validate_password(value: str) -> tuple[bool, str]:
	"""Validate password strength requirements."""
	if not PASSWORD_REGEX.match(value):
		return False, "Invalid password. Minimum 8 chars, at least 1 uppercase letter and 1 number."
	return True, ""


def validate_float(
	value: str,
	field_label: str,
	minimum: float | None = None,
	maximum: float | None = None,
) -> tuple[bool, str, float | None]:
	"""Validate and parse a float value with optional range boundaries."""
	try:
		parsed = float(value)
	except ValueError:
		return False, f"{field_label} must be a numeric value.", None

	if minimum is not None and parsed < minimum:
		return False, f"{field_label} must be >= {minimum}.", None
	if maximum is not None and parsed > maximum:
		return False, f"{field_label} must be <= {maximum}.", None

	return True, "", parsed


def validate_int(
	value: str,
	field_label: str,
	minimum: int | None = None,
	maximum: int | None = None,
) -> tuple[bool, str, int | None]:
	"""Validate and parse an integer value with optional range boundaries."""
	try:
		parsed = int(value)
	except ValueError:
		return False, f"{field_label} must be an integer value.", None

	if minimum is not None and parsed < minimum:
		return False, f"{field_label} must be >= {minimum}.", None
	if maximum is not None and parsed > maximum:
		return False, f"{field_label} must be <= {maximum}.", None

	return True, "", parsed


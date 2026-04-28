"""Validation helpers for CLI input and field constraints."""
import re


# Type aliases for validation results
ValidationResult = tuple[bool, str]
ValidationResultWithValue = tuple[bool, str, int | float | None]

# Precompiled regex patterns for efficiency references:
# - Email: Basic format with local and domain parts, allowing common characters.
# - Phone: 9-12 digits, optional international prefix with '+'.
# - Date: Strict DD-MM-YYYY format with valid day/month ranges.
# - Password: Minimum 8 characters, at least one uppercase letter and one number.
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^(\+\d{1,3})?\d{9,12}$")
DATE_REGEX = re.compile(r"^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*\d).{8,}$")


def validate_non_empty(value: str, field_label: str) -> ValidationResult:
	"""Validate that input text is not empty."""
	if value.strip() == "":
		return False, f"{field_label} cannot be empty."
	return True, ""


def validate_email(value: str) -> ValidationResult:
	"""Validate email format using regex rules."""
	if not EMAIL_REGEX.match(value):
		return False, "Invalid email format. Example: user@example.com"
	return True, ""


def validate_phone(value: str) -> ValidationResult:
	"""Validate phone number format (national/international style)."""
	if not PHONE_REGEX.match(value):
		return False, "Invalid phone format. Use 9-12 digits, optional country prefix (e.g., +351912345678)."
	return True, ""


def validate_date(value: str) -> ValidationResult:
	"""Validate date format (DD-MM-YYYY)."""
	if not DATE_REGEX.match(value):
		return False, "Invalid date format. Use DD-MM-YYYY."
	return True, ""


def validate_password(value: str) -> ValidationResult:
	"""Validate password strength requirements."""
	if not PASSWORD_REGEX.match(value):
		return False, "Invalid password. Minimum 8 chars, at least 1 uppercase letter and 1 number."
	return True, ""

def validate_number(
	value: str,
	field_label: str,
	minimum: int | float | None = None,
	maximum: int | float | None = None,
) -> ValidationResultWithValue:
	"""Validate and parse a numeric value with optional range boundaries."""
	try:
		parsed = float(value)
	except ValueError:
		return False, f"{field_label} must be a numeric value.", None

	if minimum is not None and parsed < minimum:
		return False, f"{field_label} must be >= {minimum}.", None
	if maximum is not None and parsed > maximum:
		return False, f"{field_label} must be <= {maximum}.", None

	return True, "", parsed


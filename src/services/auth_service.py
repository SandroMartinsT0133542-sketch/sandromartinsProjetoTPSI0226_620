"""Authentication helpers backed by a small JSON user store."""

from hashlib import sha256
from pathlib import Path
from typing import Any

from data.storage import initialize_database, load_records, save_records


Record = dict[str, Any]


users_db = Path(__file__).resolve().parents[2] / "data" / "users.json"
users: list[Record] = []
current_username: str | None = None
current_user_id_value: int | None = None


def _hash_password(password: str) -> str:
	return sha256(password.encode("utf-8")).hexdigest()


def initialize_auth(db_path: Path | None = None) -> None:
	"""Load users from JSON and create a default account if needed."""
	global users_db, users
	if db_path is not None:
		users_db = db_path
	initialize_database(users_db)
	users[:] = [dict(user) for user in load_records(users_db)]
	if not users:
		users[:] = [
			{
				"user_id": 1,
				"username": "admin",
				"display_name": "Administrator",
				"email": "admin@fitness.local",
				"phone": "+351900000000",
				"password_hash": _hash_password("Admin@2026"),
			},
		]
		save_users()


def save_users() -> bool:
	"""Persist the in-memory user list to JSON."""
	return save_records(users_db, users)


def register_user(username: str, display_name: str, email: str, phone: str, password: str) -> tuple[bool, str]:
	"""Create a new user account unless the username already exists."""
	global users
	if not users:
		initialize_auth()

	username = username.strip()
	display_name = display_name.strip()
	email = email.strip()
	phone = phone.strip()
	if not username or not display_name or not email or not phone or not password:
		return False, "All fields are required."

	for user in users:
		if user.get("username") == username:
			return False, "That username is already taken."

	next_id = max((int(user.get("user_id", 0)) for user in users), default=0) + 1
	users.append(
		{
			"user_id": next_id,
			"username": username,
			"display_name": display_name,
			"email": email,
			"phone": phone,
			"password_hash": _hash_password(password),
		}
	)
	if save_users():
		return True, "Account created successfully."
	users.pop()
	return False, "Could not save the new account."


def authenticate(username: str, password: str) -> bool:
	"""Check credentials against the stored users and mark the current user."""
	global current_username, current_user_id_value
	if not users:
		initialize_auth()

	password_hash = _hash_password(password)
	for user in users:
		if user.get("username") == username and user.get("password_hash") == password_hash:
			current_username = username
			current_user_id_value = int(user.get("user_id", 0))
			return True
	return False


def current_user() -> str | None:
	"""Return the currently authenticated username, if any."""
	return current_username


def current_user_id() -> int | None:
	"""Return the currently authenticated user ID, if any."""
	return current_user_id_value


def logout() -> None:
	"""Clear the active login session."""
	global current_username, current_user_id_value
	current_username = None
	current_user_id_value = None
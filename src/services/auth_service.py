"""Authentication helpers backed by a small JSON user store."""

from pathlib import Path
from typing import cast

try:
	from store import initialize_database, load_records, save_records
	from utils import generate_user, hash_password
except ModuleNotFoundError:
	from src.store import initialize_database, load_records, save_records
	from src.utils import generate_user, hash_password

Record = dict[str, str | int | float]


auth_state: dict[str, list[Record] | str | int | Path | None]  = {
	"users_db": Path(__file__).resolve().parents[2] / "data" / "users.json",
	"users": [],
	"current_username": None,
	"current_user_id": None,
}

def initialize_auth(db_path: Path | None = None) -> None:
	"""Load users from JSON and create a default account if needed."""
	if db_path is not None:
		auth_state["users_db"] = db_path
	users_db: Path = cast(Path, auth_state["users_db"])
	initialize_database(users_db)
	loaded_users = [dict(user) for user in load_records(users_db)]
	auth_state["users"] = loaded_users
	if not loaded_users:
		auth_state["users"] = [
			{
				"user_id": 1,
				"username": "admin",
				"display_name": "Administrator",
				"email": "admin@fitness.local",
				"phone": "+351900000000",
				"password_hash": hash_password("admin"),
			},
		]
		save_users()


def save_users() -> bool:
	"""Persist the in-memory user list to JSON."""
	users_db: Path = cast(Path, auth_state["users_db"])
	users: list[Record] = cast(list[Record], auth_state["users"])
	return save_records(users_db, users)


def register_user(
	username: str,
	display_name: str,
	password: str,
	email: str = "",
	phone: str = "",
) -> tuple[bool, str]:
	"""Create a new user account unless the username already exists."""
	users: list[Record] = cast(list[Record], auth_state["users"])
	if not users:
		initialize_auth()
		users = cast(list[Record], auth_state["users"])

	clean_username = username.strip()
	clean_display = display_name.strip()
	clean_password = password.strip()
	clean_email = email.strip() if email.strip() else f"{clean_username}@fitness.local"
	clean_phone = phone.strip() if phone.strip() else "+351900000000"

	user = generate_user(
		clean_username,
		clean_display,
		clean_email,
		clean_phone,
		clean_password,
	)

	if not user["username"] or not user["display_name"] or not user["email"] or not user["phone"] or not user["password_hash"]:
		return False, "All fields are required."

	max_user_id = 0
	for existing_user in users:
		try:
			existing_id = int(existing_user.get("user_id", 0))
		except (TypeError, ValueError):
			existing_id = 0
		if existing_id > max_user_id:
			max_user_id = existing_id

	for existing_user in users:
		if existing_user.get("username") == user["username"]:
			return False, "That username is already taken."
		elif existing_user.get("email") == user["email"]:
			return False, "That email is already registered."
		elif existing_user.get("phone") == user["phone"]:
			return False, "That phone number is already registered."
		elif existing_user.get("display_name") == user["display_name"]:
			return False, "That display name is already taken."

	user["user_id"] = max_user_id + 1
	users.append(cast(Record, user))

	if save_users():
		return True, "Account created successfully."
	users.pop()
	return False, "Could not save the new account."


def authenticate(username: str, password: str) -> bool:
	"""Check credentials against the stored users and mark the current user."""
	users: list[Record] = cast(list[Record], auth_state["users"])
	if not users:
		initialize_auth()
		users = cast(list[Record], auth_state["users"])

	password_hash = hash_password(password)
	for user in users:
		if user.get("username") == username and user.get("password_hash") == password_hash:
			auth_state["current_username"] = username
			auth_state["current_user_id"] = int(user.get("user_id", 0))
			return True
	auth_state["current_username"] = None
	auth_state["current_user_id"] = None
	return False


def current_user() -> str | None:
	"""Return the currently authenticated username, if any."""
	return cast(str | None, auth_state["current_username"])



def current_user_id() -> int | None:
	"""Return the currently authenticated user ID, if any."""
	return cast(int | None, auth_state["current_user_id"])


def logout() -> None:
	"""Clear the active login session."""
	auth_state["current_username"] = None
	auth_state["current_user_id"] = None

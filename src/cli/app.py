"""Legacy CLI fallback for environments where the GUI cannot start."""

from services.auth_service import authenticate, initialize_auth, current_user, register_user
from services.progress_service import initialize_service, list_records, save_state


def run_app() -> None:
	"""Load data, ask for a login, and optionally save before exit."""
	initialize_auth()
	print("GUI unavailable. Legacy CLI fallback is minimal by design.")
	mode = input("Do you want to sign up first? (S/N): ").strip().upper()
	if mode == "S":
		display_name = input("Display name: ").strip()
		username = input("Username: ").strip()
		password = input("Password: ").strip()
		success, message = register_user(username, display_name, password)
		print(message)
		if not success:
			return
	else:
		username = input("Username: ").strip()
		password = input("Password: ").strip()

	if not authenticate(username, password):
		print("Login failed.")
		return

	initialize_service()
	print(f"Signed in as {current_user() or username}.")
	print(f"Loaded {len(list_records())} record(s).")
	try:
		save_choice = input("Save before exit? (S/N): ").strip().upper()
	except EOFError:
		save_choice = "N"
	if save_choice == "S":
		if save_state():
			print("Records saved.")
		else:
			print("Save failed.")
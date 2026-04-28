"""Minimal Tkinter GUI for managing fitness progress records."""

from tkinter import Listbox, StringVar, Tk, messagebox, simpledialog, ttk
from typing import Any, cast

from services.auth_service import (authenticate,current_user_id, initialize_auth, logout, register_user)

from services.progress_service import (
	create_record,
	delete_record,
	find_by_id,
	initialize_service,
	list_records_by_user,
	save_state,
)
from utils.validators import (
	validate_date,
	validate_email,
	validate_number,
	validate_non_empty,
	validate_password,
	validate_phone,
)


Payload = dict[str, str | float | int]

class FitnessApp:
	"""Compact GUI with unified auth dialog and menu-driven main interface."""

	def __init__(self, root: Tk) -> None:
		self.root = root
		self.root.title("Fitness Records")
		self.root.geometry("500x550")
		self.root.minsize(400, 450)

		initialize_auth()
		initialize_service()

		self.current_username = ""
		self.current_user_id = ""
		self.is_signup_mode = False
		self.records: list[dict[str, Any]] = []
		self.status_text = StringVar(value="Ready.")

		self.container = ttk.Frame(self.root, padding=12)
		self.container.pack(fill="both", expand=True)

		self._show_auth()

	def _clear_container(self) -> None:
		"""Clear all widgets from container."""
		for widget in self.container.winfo_children():
			widget.destroy()

	def _show_auth(self) -> None:
		"""Compact auth dialog with toggle between login and signup modes."""
		self._clear_container()
		self.status_text.set("Authenticate")

		auth_card = ttk.Frame(self.container, padding=20)
		auth_card.place(relx=0.5, rely=0.5, anchor="center")

		# Header
		title_text = "Create Account" if self.is_signup_mode else "Login"
		title_label = ttk.Label(auth_card, text=title_text, font=("Arial", 14, "bold"))
		title_label.pack(pady=(0, 16))

		# Form frame
		form_frame = ttk.Frame(auth_card)
		form_frame.pack(fill="x", pady=(0, 16))

		# Username (always visible)
		ttk.Label(form_frame, text="Username").pack(anchor="w", pady=(0, 2))
		username_entry = ttk.Entry(form_frame, width=32)
		username_entry.pack(anchor="w", pady=(0, 10))

		# Signup-only fields
		display_name_entry = None
		email_entry = None
		phone_entry = None

		if self.is_signup_mode:
			ttk.Label(form_frame, text="Display Name").pack(anchor="w", pady=(0, 2))
			display_name_entry = ttk.Entry(form_frame, width=32)
			display_name_entry.pack(anchor="w", pady=(0, 10))

			ttk.Label(form_frame, text="Email").pack(anchor="w", pady=(0, 2))
			email_entry = ttk.Entry(form_frame, width=32)
			email_entry.pack(anchor="w", pady=(0, 10))

			ttk.Label(form_frame, text="Phone").pack(anchor="w", pady=(0, 2))
			phone_entry = ttk.Entry(form_frame, width=32)
			phone_entry.pack(anchor="w", pady=(0, 10))

		# Password (always visible)
		ttk.Label(form_frame, text="Password").pack(anchor="w", pady=(0, 2))
		password_entry = ttk.Entry(form_frame, width=32, show="*")
		password_entry.pack(anchor="w")

		# Button frame
		button_frame = ttk.Frame(auth_card)
		button_frame.pack(fill="x", pady=(16, 10))

		def do_login() -> None:
			username = username_entry.get().strip()
			password = password_entry.get().strip()
			if not username or not password:
				messagebox.showerror("Login", "Username and password required.")
				return

			if not authenticate(username, password):
				messagebox.showerror("Login", "Invalid credentials.")
				return

			self.current_username = username
			self.current_user_id = str(current_user_id())
			if not self.current_user_id or self.current_user_id == "None":
				messagebox.showerror("Login", "Failed to retrieve user ID.")
				return

			self.root.title(f"Fitness Records - {self.current_username}")
			self._show_menu()

		def do_signup() -> None:
			username = username_entry.get().strip()
			display_name = display_name_entry.get().strip() if display_name_entry else ""
			email = email_entry.get().strip() if email_entry else ""
			phone = phone_entry.get().strip() if phone_entry else ""
			password = password_entry.get().strip()

			if not all([username, display_name, email, phone, password]):
				messagebox.showerror("Sign up", "All fields required.")
				return

			is_valid, msg = validate_email(email)
			if not is_valid:
				messagebox.showerror("Sign up", msg)
				return

			is_valid, msg = validate_phone(phone)
			if not is_valid:
				messagebox.showerror("Sign up", msg)
				return

			is_valid, msg = validate_password(password)
			if not is_valid:
				messagebox.showerror("Sign up", msg)
				return

			success, msg = register_user(username, display_name, password, email, phone)
			if not success:
				messagebox.showerror("Sign up", msg)
				return

			messagebox.showinfo("Sign up", "Account created! Please log in.")
			self.is_signup_mode = False
			self._show_auth()

		def toggle_mode() -> None:
			self.is_signup_mode = not self.is_signup_mode
			self._show_auth()

		if not self.is_signup_mode:
			ttk.Button(button_frame, text="Login", command=do_login).pack(fill="x")
		else:
			ttk.Button(button_frame, text="Sign up", command=do_signup).pack(fill="x")

		ttk.Button(button_frame, text="Toggle to " + ("login" if self.is_signup_mode else "signup"), command=toggle_mode).pack(fill="x", pady=(6, 0))

		ttk.Label(self.container, textvariable=self.status_text, anchor="w", padding=(12, 4)).pack(side="bottom", fill="x")

	def _show_menu(self) -> None:
		"""Menu-driven main interface after login."""
		self._clear_container()
		self.records = list_records_by_user(self.current_user_id)

		menu_frame = ttk.Frame(self.container, padding=20)
		menu_frame.place(relx=0.5, rely=0.5, anchor="center")

		ttk.Label(menu_frame, text="Main Menu", font=("Arial", 16, "bold")).pack(pady=(0, 20))

		options = [
			("1. Add Record", self._add_record),
			("2. View Records", self._view_records),
			("3. Filter Records", self._filter_records),
			("4. Sort Records", self._sort_records),
			("5. Record Details", self._view_details),
			("6. Delete Record", self._delete_record),
			("7. Logout", self._logout),
		]

		for text, command in options:
			ttk.Button(menu_frame, text=text, width=25, command=command).pack(fill="x", pady=4)

		ttk.Label(self.container, textvariable=self.status_text, anchor="w", padding=(12, 4)).pack(side="bottom", fill="x")
		self._update_status(f"Logged in as {self.current_username}")

	def _add_record(self) -> None:
		"""Modal to add a new record."""
		dialog = Tk()
		dialog.title("Add Record")
		dialog.geometry("420x650")
		dialog.transient(self.root)
		dialog.grab_set()

		fields: dict[str, Any] = {}
		form_frame = ttk.Frame(dialog, padding=15)
		form_frame.pack(fill="both", expand=True)

		ttk.Label(form_frame, text="Add New Record", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

		for field_name, label_text in (
			("client_name", "Client Name"),
			("email", "Email"),
			("phone", "Phone"),
			("record_date", "Date (DD-MM-YYYY)"),
			("password", "Password"),
			("weight_kg", "Weight (kg)"),
			("body_fat_pct", "Body Fat (%)"),
			("daily_calories", "Daily Calories"),
			("notes", "Notes"),
		):
			ttk.Label(form_frame, text=label_text).pack(anchor="w", pady=(8, 2))
			show_val = "*" if field_name == "password" else ""
			entry = ttk.Entry(form_frame, width=40, show=show_val)
			entry.pack(anchor="w", fill="x")
			fields[field_name] = entry

		def save() -> None:
			try:
				payload: Payload = {
					"client_name": fields["client_name"].get().strip(),
					"email": fields["email"].get().strip(),
					"phone": fields["phone"].get().strip(),
					"record_date": fields["record_date"].get().strip(),
					"password": fields["password"].get().strip(),
					"weight_kg": float(fields["weight_kg"].get().strip()),
					"body_fat_pct": float(fields["body_fat_pct"].get().strip()),
					"daily_calories": int(fields["daily_calories"].get().strip()),
					"notes": fields["notes"].get().strip(),
					"user_id": self.current_user_id,
				}
			except ValueError:
				messagebox.showerror("Error", "Invalid numeric values.")
				return

			# Validate
			is_valid, msg = validate_non_empty(cast(str, payload["client_name"]), "Client name")
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			is_valid, msg = validate_email(cast(str, payload["email"]))
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			is_valid, msg = validate_phone(cast(str, payload["phone"]))
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			is_valid, msg = validate_date(cast(str, payload["record_date"]))
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			is_valid, msg = validate_password(cast(str, payload["password"]))
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			is_valid, msg, _weight = validate_number( cast(str, payload["weight_kg"]), "Weight", 1.0, 500.0)
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			is_valid, msg, _bf = validate_number(cast(str, payload["body_fat_pct"]), "Body fat", 1.0, 80.0)
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			is_valid, msg, _cal = validate_number(str(payload["daily_calories"]), "Calories", 500, 12000)
			if not is_valid:
				messagebox.showerror("Validation", msg)
				return

			try:
				create_record(payload)
				save_state()
				self._update_status("Record added successfully.")
				dialog.destroy()
				self.records = list_records_by_user(self.current_user_id)
				self._show_menu()
			except Exception as e:
				messagebox.showerror("Error", f"Failed to save: {e}")

		button_frame = ttk.Frame(form_frame)
		button_frame.pack(fill="x", pady=(16, 0))
		ttk.Button(button_frame, text="Save", command=save).pack(fill="x")
		ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(fill="x", pady=(6, 0))

	def _view_records(self) -> None:
		"""Show list of user's records."""
		self.records = list_records_by_user(self.current_user_id)
		if not self.records:
			messagebox.showinfo("Records", "No records found.")
			return

		dialog = Tk()
		dialog.title("Your Records")
		dialog.geometry("700x400")
		dialog.transient(self.root)
		dialog.grab_set()

		listbox = Listbox(dialog, height=15)
		listbox.pack(fill="both", expand=True, padx=10, pady=10)

		for record in self.records:
			listbox.insert(
				0,
				f'{record["record_id"]} | {record["client_name"]} | {record["record_date"]} | '
				f'{record["weight_kg"]:.1f}kg | {record["body_fat_pct"]:.1f}% | {record["daily_calories"]}cal',
			)

		ttk.Button(dialog, text="Close", command=dialog.destroy).pack(fill="x", padx=10, pady=(0, 10))
		self._update_status(f"Showing {len(self.records)} record(s).")

	def _filter_records(self) -> None:
		"""Filter records by client name."""
		query = simpledialog.askstring("Filter", "Search by client name:", parent=self.root)
		if not query:
			return

		filtered = [r for r in self.records if query.lower() in str(r["client_name"]).lower()]
		if not filtered:
			messagebox.showinfo("Filter", "No matches found.")
			return

		dialog = Tk()
		dialog.title("Filtered Records")
		dialog.geometry("700x400")
		dialog.transient(self.root)
		dialog.grab_set()

		listbox = Listbox(dialog)
		listbox.pack(fill="both", expand=True, padx=10, pady=10)

		for record in filtered:
			listbox.insert(
				0,
				f'{record["record_id"]} | {record["client_name"]} | {record["record_date"]} | '
				f'{record["weight_kg"]:.1f}kg | {record["body_fat_pct"]:.1f}% | {record["daily_calories"]}cal',
			)

		ttk.Button(dialog, text="Close", command=dialog.destroy).pack(fill="x", padx=10, pady=(0, 10))
		self._update_status(f"Found {len(filtered)} match(es).")

	def _sort_records(self) -> None:
		"""Sort records by field."""
		choice = simpledialog.askstring(
			"Sort",
			"Choose:\n1. Date (ascending)\n2. Date (descending)\n3. Weight (ascending)\n4. Weight (descending)",
			parent=self.root,
		)
		if not choice or choice not in "1234":
			return

		choice_idx = int(choice) - 1
		if choice_idx == 0:
			sorted_recs = sorted(self.records, key=lambda r: r["record_date"])
		elif choice_idx == 1:
			sorted_recs = sorted(self.records, key=lambda r: r["record_date"], reverse=True)
		elif choice_idx == 2:
			sorted_recs = sorted(self.records, key=lambda r: r["weight_kg"])
		else:
			sorted_recs = sorted(self.records, key=lambda r: r["weight_kg"], reverse=True)

		dialog = Tk()
		dialog.title("Sorted Records")
		dialog.geometry("700x400")
		dialog.transient(self.root)
		dialog.grab_set()

		listbox = Listbox(dialog)
		listbox.pack(fill="both", expand=True, padx=10, pady=10)

		for record in sorted_recs:
			listbox.insert(
				0,
				f'{record["record_id"]} | {record["client_name"]} | {record["record_date"]} | '
				f'{record["weight_kg"]:.1f}kg | {record["body_fat_pct"]:.1f}% | {record["daily_calories"]}cal',
			)

		ttk.Button(dialog, text="Close", command=dialog.destroy).pack(fill="x", padx=10, pady=(0, 10))

	def _view_details(self) -> None:
		"""Show detailed view of a selected record."""
		if not self.records:
			messagebox.showinfo("Details", "No records available.")
			return

		record_id_str = simpledialog.askstring("Details", "Enter record ID:", parent=self.root)
		if not record_id_str:
			return

		try:
			record_id = int(record_id_str)
		except ValueError:
			messagebox.showerror("Error", "Invalid record ID.")
			return

		record = find_by_id(record_id)
		if not record or record.get("user_id") != self.current_user_id:
			messagebox.showerror("Error", "Record not found or access denied.")
			return

		dialog = Tk()
		dialog.title(f"Record {record_id} Details")
		dialog.geometry("400x500")
		dialog.transient(self.root)
		dialog.grab_set()

		details_frame = ttk.Frame(dialog, padding=15)
		details_frame.pack(fill="both", expand=True)

		for key, value in record.items():
			if key == "user_id":
				continue
			ttk.Label(details_frame, text=f"{key.upper()}:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 2))
			ttk.Label(details_frame, text=str(value), wraplength=300, justify="left").pack(anchor="w", pady=(0, 6))

		ttk.Button(details_frame, text="Close", command=dialog.destroy).pack(fill="x", pady=(16, 0))

	def _delete_record(self) -> None:
		"""Delete a record."""
		record_id_str = simpledialog.askstring("Delete", "Enter record ID to delete:", parent=self.root)
		if not record_id_str:
			return

		try:
			record_id = int(record_id_str)
		except ValueError:
			messagebox.showerror("Error", "Invalid record ID.")
			return

		record = find_by_id(record_id)
		if not record or record.get("user_id") != self.current_user_id:
			messagebox.showerror("Error", "Record not found or access denied.")
			return

		if not messagebox.askyesno("Confirm", f'Delete record for {record["client_name"]}?'):
			return

		if delete_record(record_id):
			save_state()
			self.records = list_records_by_user(self.current_user_id)
			self._update_status("Record deleted.")
			self._show_menu()
		else:
			messagebox.showerror("Error", "Could not delete record.")

	def _logout(self) -> None:
		"""Logout and return to auth dialog."""
		logout()
		self.current_username = ""
		self.current_user_id = ""
		self.records = []
		self.is_signup_mode = False
		self.root.title("Fitness Records")
		self._show_auth()

	def _update_status(self, msg: str) -> None:
		"""Update status bar message."""
		self.status_text.set(msg)

def run_gui() -> None:
	"""Start the Tkinter application."""
	root = Tk()
	FitnessApp(root)
	root.mainloop()

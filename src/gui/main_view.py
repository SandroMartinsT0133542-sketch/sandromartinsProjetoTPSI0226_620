from tkinter import ttk, messagebox
from typing import Callable

from services.progress_service import list_records_by_user, delete_record, save_state
from .record_table import RecordTable
from .add_record_dialog import show_add_dialog


class MainView(ttk.Frame):
    def __init__(self, parent, user_id: str, username: str, on_logout: Callable[[], None]):
        super().__init__(parent, padding=8)
        self.user_id = user_id
        self.username = username
        self.on_logout = on_logout

        self.status = ttk.Label(self, text=f"Logged in as {self.username}")
        self.status.pack(side="bottom", fill="x")

        self._build()
        self.load_records()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 6))

        ttk.Label(top, text=f"Welcome, {self.username}", font=("Arial", 12, "bold")).pack(side="left")

        btns = ttk.Frame(top)
        btns.pack(side="right")
        ttk.Button(btns, text="Add Record", command=self._add).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete", command=self._delete).pack(side="left", padx=4)
        ttk.Button(btns, text="Refresh", command=self.load_records).pack(side="left", padx=4)
        ttk.Button(btns, text="Logout", command=self._logout).pack(side="left", padx=4)

        self.table = RecordTable(self, on_select=None)
        self.table.pack(fill="both", expand=True)

    def load_records(self):
        records = list_records_by_user(self.user_id)
        self.table.load(records)
        self.status.config(text=f"Showing {len(records)} record(s). Logged in as {self.username}")

    def _add(self):
        show_add_dialog(self, self.user_id, on_saved=self.load_records)

    def _delete(self):
        rid = self.table.selected_id()
        if rid is None:
            messagebox.showinfo("Delete", "Select a record to delete.")
            return

        rec = None
        # confirmation prompt
        if not messagebox.askyesno("Confirm", f"Delete record {rid}?"):
            return

        if delete_record(rid):
            save_state()
            self.load_records()
            messagebox.showinfo("Delete", "Record deleted.")
        else:
            messagebox.showerror("Delete", "Could not delete record.")

    def _logout(self):
        self.on_logout()

from tkinter import ttk, messagebox, StringVar
from typing import Any, Callable

from services.progress_service import (
    Record,
    delete_record,
    list_records_by_user,
    save_state,
    search_records,
    sort_records,
)
from .record_table import RecordTable
from .add_record_dialog import show_add_dialog


class MainView(ttk.Frame):
    def __init__(self, parent: Any, user_id: str, username: str, on_logout: Callable[[], None]):
        super().__init__(parent, padding=8)
        self.user_id = user_id
        self.username = username
        self.on_logout = on_logout
        self._displayed_records: list[Record] | None = None
        self._sort_field: str | None = None
        self._sort_descending = False
        self._search_fields = {
            "Record ID": "record_id",
            "Date": "record_date",
            "Weight": "weight_kg",
            "Body Fat": "body_fat_pct",
            "Calories": "daily_calories",
            "Notes": "notes",
        }
        self.search_field_var = StringVar(value="Notes")
        self.sort_algo_var = StringVar(value="insertion")
        self._sort_algorithms = ["bubble", "insertion", "quick", "merge"]
        self.search_operator_var = StringVar(value="equals")
        self._operator_options = ["equals", "like", "greater", "less", "between", "any"]

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
        ttk.Label(btns, text="Sort:").pack(side="left", padx=(8,2))
        ttk.Combobox(btns, textvariable=self.sort_algo_var, values=self._sort_algorithms, state="readonly", width=10).pack(side="left", padx=(0,8))
        ttk.Button(btns, text="Logout", command=self._logout).pack(side="left", padx=4)

        search_bar = ttk.LabelFrame(self, text="Search & Filter")
        search_bar.pack(fill="x", pady=(0, 6))

        # Row 0: Field, Operator, Value controls
        ttk.Label(search_bar, text="Field").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.search_field = ttk.Combobox(search_bar, textvariable=self.search_field_var, values=list(self._search_fields.keys()), state="readonly", width=12)
        self.search_field.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=4)

        ttk.Label(search_bar, text="Op").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.search_operator = ttk.Combobox(search_bar, textvariable=self.search_operator_var, values=self._operator_options, state="readonly", width=10)
        self.search_operator.grid(row=0, column=3, sticky="w", padx=(0, 8), pady=4)
        self.search_operator.bind("<<ComboboxSelected>>", self._on_operator_changed)

        ttk.Label(search_bar, text="Value").grid(row=0, column=4, sticky="w", padx=6, pady=4)
        self.search_value = ttk.Entry(search_bar, width=16)
        self.search_value.grid(row=0, column=5, sticky="we", padx=(0, 8), pady=4)

        # Row 0 continued: Max value (hidden by default for "between")
        ttk.Label(search_bar, text="Max").grid(row=0, column=6, sticky="w", padx=6, pady=4)
        self.search_value_max = ttk.Entry(search_bar, width=16)
        self.search_value_max.grid(row=0, column=7, sticky="we", padx=(0, 8), pady=4)

        # Row 0 continued: Action buttons
        ttk.Button(search_bar, text="Use Selected", command=self._use_selected_value).grid(row=0, column=8, padx=(0, 6), pady=4)
        ttk.Button(search_bar, text="Linear", command=self._search_linear).grid(row=0, column=9, padx=(0, 4), pady=4)
        ttk.Button(search_bar, text="Binary", command=self._search_binary).grid(row=0, column=10, padx=(0, 6), pady=4)
        ttk.Button(search_bar, text="Reset", command=self._reset_search).grid(row=0, column=11, padx=(0, 6), pady=4)

        # Help text
        ttk.Label(
            search_bar,
            text="Operators: equals (exact), like (substring), greater (>), less (<), between (range), any (comma-separated).",
            foreground="#555",
            font=("Arial", 9)
        ).grid(row=1, column=0, columnspan=12, sticky="w", padx=6, pady=(0, 2))

        ttk.Label(
            search_bar,
            text="Binary search is faster but requires sorted data and doesn't support 'like' or 'any' (will use linear).",
            foreground="#555",
            font=("Arial", 9)
        ).grid(row=2, column=0, columnspan=12, sticky="w", padx=6, pady=(0, 2))

        ttk.Label(
            search_bar,
            text="Tip: Select a row, then click 'Use Selected' to pull its value into the search box.",
            foreground="#555",
            font=("Arial", 9)
        ).grid(row=3, column=0, columnspan=12, sticky="w", padx=6, pady=(0, 4))

        search_bar.grid_columnconfigure(5, weight=1)
        search_bar.grid_columnconfigure(7, weight=1)

        # Hide max field initially
        self._update_max_field_visibility()

        self.table = RecordTable(self, on_select=None, on_sort=self._sort_by_column)
        self.table.pack(fill="both", expand=True)

    def load_records(self):
        records = list_records_by_user(self.user_id)
        self._displayed_records = [record.copy() for record in records]
        self.table.load(records)
        self.status.config(text=f"Showing {len(records)} record(s). Logged in as {self.username}")

    def _current_records(self) -> list[Record]:
        if self._displayed_records is None:
            return list_records_by_user(self.user_id)
        return [record.copy() for record in self._displayed_records]

    def _show_records(self, records: list[Record], status: str) -> None:
        self._displayed_records = [record.copy() for record in records]
        self.table.load(records)
        self.status.config(text=status)

    def _add(self):
        show_add_dialog(self, self.user_id, on_saved=self.load_records)

    def _delete(self):
        rid = self.table.selected_id()
        if rid is None:
            messagebox.showinfo("Delete", "Select a record to delete.")
            return

        if not messagebox.askyesno("Confirm", f"Delete record {rid}?"):
            return

        if delete_record(rid, self.user_id):
            save_state()
            self.load_records()
            messagebox.showinfo("Delete", "Record deleted.")
        else:
            messagebox.showerror("Delete", "Could not delete record.")

    def _logout(self):
        self.on_logout()

    def _sort_by_column(self, field: str) -> None:
        records = self._current_records()
        if not records:
            return

        if self._sort_field == field:
            self._sort_descending = not self._sort_descending
        else:
            self._sort_field = field
            self._sort_descending = False

        ordered = sort_records(field, self.sort_algo_var.get(), descending=self._sort_descending, records=records)
        direction = "descending" if self._sort_descending else "ascending"
        self._show_records(ordered, f"Sorted by {field} ({direction}). Showing {len(ordered)} record(s).")

    def _search(self, algorithm: str) -> None:
        field_label = self.search_field_var.get()
        field = self._search_fields.get(field_label, "notes")
        operator = self.search_operator_var.get()
        target = self.search_value.get().strip()
        target_max = self.search_value_max.get().strip() if operator == "between" else None

        if not target:
            messagebox.showinfo("Search", "Enter a value to search.")
            return

        if operator == "between" and not target_max:
            messagebox.showinfo("Search", "For 'between' operator, enter both min and max values.")
            return

        base_records = list_records_by_user(self.user_id)
        results = search_records(field, target, algorithm=algorithm, operator=operator, target_max=target_max, records=base_records)
        mode_label = "Binary search" if algorithm == "binary" else "Linear search"
        op_label = f" ({operator})" if operator != "equals" else ""
        self._show_records(results, f"{mode_label} by {field_label}{op_label} returned {len(results)} record(s).")

    def _on_operator_changed(self, event: Any = None) -> None:
        """Handle operator selection change to show/hide max value field."""
        self._update_max_field_visibility()

    def _update_max_field_visibility(self) -> None:
        """Show max value field only when 'between' operator is selected."""
        operator = self.search_operator_var.get()
        if operator == "between":
            # Make max field visible
            self.search_value_max.grid()
            self.search_value_max.delete(0, "end")
        else:
            # Hide max field
            self.search_value_max.grid_remove()

    def _search_linear(self) -> None:
        self._search("linear")

    def _search_binary(self) -> None:
        self._search("binary")

    def _use_selected_value(self) -> None:
        selected_id = self.table.selected_id()
        if selected_id is None:
            messagebox.showinfo("Search", "Select a row first.")
            return

        records = self._current_records()
        selected_record = next((record for record in records if int(record.get("record_id", -1)) == selected_id), None)
        if not selected_record:
            messagebox.showinfo("Search", "Could not read the selected row.")
            return

        field_label = self.search_field_var.get()
        field = self._search_fields.get(field_label, "notes")
        value = selected_record.get(field, "")
        self.search_value.delete(0, "end")
        self.search_value.insert(0, str(value))
        self.status.config(text=f"Copied selected {field_label} value into the search box.")

    def _reset_search(self) -> None:
        self.search_field_var.set("Notes")
        self.search_operator_var.set("equals")
        self.search_value.delete(0, "end")
        self.search_value_max.delete(0, "end")
        self._update_max_field_visibility()
        self.load_records()

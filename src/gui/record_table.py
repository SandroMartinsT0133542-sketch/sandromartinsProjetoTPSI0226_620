from tkinter import ttk
from typing import Any, Callable

from services.progress_service import Record


class RecordTable(ttk.Frame):
    def __init__(
        self,
        parent,
        on_select: Callable[[int], None] | None = None,
        on_sort: Callable[[str], None] | None = None,
    ):
        super().__init__(parent)
        self.on_select = on_select
        self.on_sort = on_sort
        self.columns = (
            ("id", "record_id", "ID"),
            ("date", "record_date", "Date"),
            ("weight", "weight_kg", "Weight (kg)"),
            ("bf", "body_fat_pct", "Body Fat (%)"),
            ("cal", "daily_calories", "Calories"),
            ("notes", "notes", "Notes"),
        )
        self.tree = ttk.Treeview(self, columns=tuple(column[0] for column in self.columns), show="headings")
        for column_name, field_name, title in self.columns:
            self.tree.heading(column_name, text=title, command=lambda field=field_name: self._on_sort(field))

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("weight", width=90, anchor="center")
        self.tree.column("bf", width=90, anchor="center")
        self.tree.column("cal", width=90, anchor="center")
        self.tree.column("notes", width=260)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _on_sort(self, field: str):
        if self.on_sort:
            self.on_sort(field)

    def load(self, records: list[Record]):
        for r in self.tree.get_children():
            self.tree.delete(r)

        for rec in records:
            self.tree.insert(
                "",
                "end",
                iid=str(rec.get("record_id")),
                values=(
                    rec.get("record_id"),
                    rec.get("record_date"),
                    f"{rec.get('weight_kg', 0):.1f}",
                    f"{rec.get('body_fat_pct', 0):.1f}",
                    rec.get("daily_calories", ""),
                    rec.get("notes", ""),
                ),
            )

    def selected_id(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            return None
        try:
            return int(sel[0])
        except Exception:
            return None

    def _on_select(self, _ev):
        sid = self.selected_id()
        if sid and self.on_select:
            self.on_select(sid)

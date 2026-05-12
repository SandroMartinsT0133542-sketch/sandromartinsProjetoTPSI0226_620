from tkinter import ttk
from typing import Callable


class RecordTable(ttk.Frame):
    def __init__(self, parent, on_select: Callable[[int], None] | None = None):
        super().__init__(parent)
        self.on_select = on_select
        self.tree = ttk.Treeview(self, columns=("id", "date", "weight", "bf", "cal", "notes"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("weight", text="Weight (kg)")
        self.tree.heading("bf", text="Body Fat (%)")
        self.tree.heading("cal", text="Calories")
        self.tree.heading("notes", text="Notes")

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

    def load(self, records: list[dict]):
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

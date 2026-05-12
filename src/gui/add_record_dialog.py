from tkinter import Toplevel, ttk, messagebox
from typing import Any, Callable, cast

from services.progress_service import create_record, save_state
from utils.validators import (
    validate_date,
    validate_number,
)


def show_add_dialog(parent: Toplevel, user_id: str, on_saved: Callable[[], None] | None = None) -> None:
    dialog = Toplevel(parent)
    dialog.title("Add Record")
    dialog.geometry("480x560")
    dialog.transient(parent)
    dialog.grab_set()

    fields: dict[str, Any] = {}
    frm = ttk.Frame(dialog, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Add New Record", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

    for name, label in (
        ("record_date", "Date (DD-MM-YYYY)"),
        ("weight_kg", "Weight (kg)"),
        ("body_fat_pct", "Body Fat (%)"),
        ("daily_calories", "Daily Calories"),
        ("notes", "Notes"),
    ):
        ttk.Label(frm, text=label).pack(anchor="w", pady=(8, 2))
        show = "*" if name == "password" else ""
        ent = ttk.Entry(frm, width=48, show=show)
        ent.pack(anchor="w", fill="x")
        fields[name] = ent

    def save():
        try:
            payload: dict[str, float | int | str] = {
                "record_date": fields["record_date"].get().strip(),
                "weight_kg": float(fields["weight_kg"].get().strip()),
                "body_fat_pct": float(fields["body_fat_pct"].get().strip()),
                "daily_calories": int(fields["daily_calories"].get().strip()),
                "notes": fields["notes"].get().strip(),
                "user_id": int(user_id) if isinstance(user_id, int) and user_id.isdigit() else user_id,
            }
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values.")
            return

        ok, msg = validate_date(cast(str, payload["record_date"]))
        if not ok:
            messagebox.showerror("Validation", msg)
            return

        ok, msg, _ = validate_number(cast(str, payload["weight_kg"]), "Weight", 1.0, 500.0)
        if not ok:
            messagebox.showerror("Validation", msg)
            return

        ok, msg, _ = validate_number(cast(str, payload["body_fat_pct"]), "Body fat", 1.0, 80.0)
        if not ok:
            messagebox.showerror("Validation", msg)
            return

        ok, msg, _ = validate_number(cast(str, payload["daily_calories"]), "Calories", 500, 12000)
        if not ok:
            messagebox.showerror("Validation", msg)
            return

        try:
            create_record(payload)
            save_state()
            if on_saved:
                on_saved()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    btns = ttk.Frame(frm)
    btns.pack(fill="x", pady=(12, 0))
    ttk.Button(btns, text="Save", command=save).pack(fill="x")
    ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(fill="x", pady=(6, 0))

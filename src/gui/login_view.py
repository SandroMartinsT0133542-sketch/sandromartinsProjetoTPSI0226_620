from tkinter import ttk, messagebox
from tkinter import StringVar
from typing import Callable

from services.auth_service import authenticate, current_user_id, initialize_auth, register_user
from utils.validators import validate_email, validate_phone, validate_password


class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_success: Callable[[str, str], None]):
        super().__init__(parent, padding=12)
        self.on_success = on_success
        self.is_signup_mode = False
        initialize_auth()

        self.status = StringVar(value="Authenticate")
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        card = ttk.Frame(self, padding=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        title_text = "Create Account" if self.is_signup_mode else "Login"
        ttk.Label(card, text=title_text, font=("Arial", 14, "bold")).pack(pady=(0, 16))

        form = ttk.Frame(card)
        form.pack(fill="x", pady=(0, 16))

        ttk.Label(form, text="Username").pack(anchor="w", pady=(0, 2))
        self.username = ttk.Entry(form, width=32)
        self.username.pack(anchor="w", pady=(0, 10))

        self.display_name = None
        self.email = None
        self.phone = None

        if self.is_signup_mode:
            ttk.Label(form, text="Display Name").pack(anchor="w", pady=(0, 2))
            self.display_name = ttk.Entry(form, width=32)
            self.display_name.pack(anchor="w", pady=(0, 10))

            ttk.Label(form, text="Email").pack(anchor="w", pady=(0, 2))
            self.email = ttk.Entry(form, width=32)
            self.email.pack(anchor="w", pady=(0, 10))

            ttk.Label(form, text="Phone").pack(anchor="w", pady=(0, 2))
            self.phone = ttk.Entry(form, width=32)
            self.phone.pack(anchor="w", pady=(0, 10))

        ttk.Label(form, text="Password").pack(anchor="w", pady=(0, 2))
        self.password = ttk.Entry(form, width=32, show="*")
        self.password.pack(anchor="w")

        btns = ttk.Frame(card)
        btns.pack(fill="x", pady=(16, 10))

        if not self.is_signup_mode:
            ttk.Button(btns, text="Login", command=self._do_login).pack(fill="x")
        else:
            ttk.Button(btns, text="Sign up", command=self._do_signup).pack(fill="x")

        ttk.Button(btns, text="Toggle to " + ("login" if self.is_signup_mode else "signup"), command=self._toggle).pack(fill="x", pady=(6, 0))

        ttk.Label(self, textvariable=self.status, anchor="w", padding=(12, 4)).pack(side="bottom", fill="x")

    def _toggle(self):
        self.is_signup_mode = not self.is_signup_mode
        self._build()

    def _do_login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        if not username or not password:
            messagebox.showerror("Login", "Username and password required.")
            return

        if not authenticate(username, password):
            messagebox.showerror("Login", "Invalid credentials.")
            return

        uid = str(current_user_id())
        if not uid or uid == "None":
            messagebox.showerror("Login", "Failed to retrieve user ID.")
            return

        self.on_success(uid, username)

    def _do_signup(self):
        username = self.username.get().strip()
        display = self.display_name.get().strip() if self.display_name else ""
        email = self.email.get().strip() if self.email else ""
        phone = self.phone.get().strip() if self.phone else ""
        password = self.password.get().strip()

        if not all([username, display, email, phone, password]):
            messagebox.showerror("Sign up", "All fields required.")
            return

        ok, msg = validate_email(email)
        if not ok:
            messagebox.showerror("Sign up", msg)
            return

        ok, msg = validate_phone(phone)
        if not ok:
            messagebox.showerror("Sign up", msg)
            return

        ok, msg = validate_password(password)
        if not ok:
            messagebox.showerror("Sign up", msg)
            return

        success, msg = register_user(username, display, password, email, phone)
        if not success:
            messagebox.showerror("Sign up", msg)
            return

        messagebox.showinfo("Sign up", "Account created! Please log in.")
        self.is_signup_mode = False
        self._build()

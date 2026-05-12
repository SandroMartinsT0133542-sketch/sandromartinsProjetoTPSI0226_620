"""Tkinter GUI entrypoint using modularized views."""

from tkinter import Tk
from tkinter import ttk
from services.progress_service import initialize_service
from .login_view import LoginFrame
from .main_view import MainView


class App:
	def __init__(self, root: Tk) -> None:
		self.root = root
		self.root.title("Fitness Records")
		self.root.geometry("900x600")
		self.root.minsize(700, 500)

		initialize_service()

		self.container = ttk.Frame(self.root)
		self.container.pack(fill="both", expand=True)

		self.current_user_id: str | None = None
		self.current_username: str | None = None

		self._show_login()

	def _clear(self):
		for w in self.container.winfo_children():
			w.destroy()

	def _show_login(self):
		self._clear()
		lf = LoginFrame(self.container, on_success=self._on_login)
		lf.pack(fill="both", expand=True)

	def _on_login(self, user_id: str, username: str):
		self.current_user_id = user_id
		self.current_username = username
		self.root.title(f"Fitness Records - {username}")
		self._show_main()

	def _show_main(self):
		self._clear()
		mv = MainView(self.container, user_id=self.current_user_id, username=self.current_username, on_logout=self._do_logout)
		mv.pack(fill="both", expand=True)

	def _do_logout(self):
		# clear any auth state in services if needed
		self.current_user_id = None
		self.current_username = None
		self.root.title("Fitness Records")
		self._show_login()


def run_gui() -> None:
	root = Tk()
	App(root)
	root.mainloop()

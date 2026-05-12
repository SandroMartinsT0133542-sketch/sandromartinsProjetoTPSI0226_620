"""Application entry point for the fitness management app.

This module attempts to launch the GUI and falls back to the CLI when the
graphical toolkit is unavailable (for example in headless environments or
when the optional `tkinter` package is not installed).
"""

def main() -> None:
	"""Start the GUI, with CLI fallback for headless environments.

	This function imports GUI-related modules lazily so the program can run in
	environments that do not have `tkinter` available.
	"""
	try:
		# Import GUI pieces only when attempting to start the graphical mode.
		from gui.app import run_gui
		run_gui()
	except Exception as err:
		print(f"Error: {err}")

if __name__ == "__main__":
	main()


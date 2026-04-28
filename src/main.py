"""Application entry point for the fitness management app."""

from tkinter import TclError

from cli.app import run_app as run_cli
from gui.app import run_gui


def main() -> None:
	"""Start the GUI, with CLI fallback for headless environments."""
	try:
		run_gui()
	except TclError:
		run_cli()


if __name__ == "__main__":
	main()


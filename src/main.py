"""Application entry point for the fitness management CLI."""

from cli.app import run_app


def main() -> None:
	"""Start the CLI loop and coordinate startup responsibilities."""
	run_app()


if __name__ == "__main__":
	main()


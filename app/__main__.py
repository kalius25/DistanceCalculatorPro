"""DistanceCalculatorPro executable entry point."""

from app.presentation.app import main


def run() -> None:
    """Run the desktop application and propagate its exit code."""
    raise SystemExit(main())


if __name__ == "__main__":  # pragma: no cover
    run()

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .theme_manager import ThemeManager


def create_application() -> tuple[QApplication, MainWindow]:
    application = QApplication(sys.argv)
    application.setApplicationName(MainWindow.APPLICATION_NAME)
    application.setApplicationVersion(MainWindow.APPLICATION_VERSION)

    styles_directory = Path(__file__).resolve().parent / "styles"
    theme_manager = ThemeManager(styles_directory)
    theme_manager.apply_theme(application, "light")

    main_window = MainWindow(application, theme_manager)
    return application, main_window


def main() -> int:
    application, main_window = create_application()
    main_window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())

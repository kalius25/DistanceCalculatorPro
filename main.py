import sys

from PySide6.QtWidgets import QApplication

from app.config.config import APP_NAME
from app.gui.main_window import MainWindow
from app.utils.logger import logger


def main():

    logger.info("Starting application...")

    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
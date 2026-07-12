from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Distance Calculator Pro")

        self.resize(1200, 750)
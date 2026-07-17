from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QFileDialog,
    QHBoxLayout,
)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Distance Calculator Pro")

        self.resize(900, 600)

        self.build_ui()

    def build_ui(self):

        widget = QWidget()

        self.setCentralWidget(widget)

        layout = QVBoxLayout(widget)

        title = QLabel("Distance Calculator Pro")

        title.setStyleSheet("font-size:24px;font-weight:bold")

        layout.addWidget(title)

        row = QHBoxLayout()

        self.file_edit = QLineEdit()

        self.file_edit.setPlaceholderText("Chọn file Excel...")

        row.addWidget(self.file_edit)

        btn = QPushButton("Chọn File")

        btn.clicked.connect(self.choose_file)

        row.addWidget(btn)

        layout.addLayout(row)

        self.status = QLabel("Sẵn sàng.")

        layout.addWidget(self.status)

    def choose_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn Excel",
            "",
            "Excel (*.xlsx)"
        )

        if filename:

            self.file_edit.setText(filename)
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QFileDialog,
    QHBoxLayout,
    QComboBox,
)

from app.services.excel_service import ExcelService


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Distance Calculator Pro")

        self.resize(900, 600)

        self.excel_service = ExcelService()

        self.build_ui()

    def build_ui(self):

        widget = QWidget()

        self.setCentralWidget(widget)

        layout = QVBoxLayout(widget)

        title = QLabel("Distance Calculator Pro")

        title.setStyleSheet(
            "font-size:24px;font-weight:bold"
        )

        layout.addWidget(title)

        # ==========================
        # File Excel
        # ==========================

        file_row = QHBoxLayout()

        self.file_edit = QLineEdit()

        self.file_edit.setPlaceholderText(
            "Chọn file Excel..."
        )

        file_row.addWidget(self.file_edit)

        self.btn_open = QPushButton("Chọn File")

        self.btn_open.clicked.connect(
            self.choose_file
        )

        file_row.addWidget(self.btn_open)

        layout.addLayout(file_row)

        # ==========================
        # Sheet
        # ==========================

        sheet_row = QHBoxLayout()

        sheet_row.addWidget(
            QLabel("Sheet")
        )

        self.sheet_combo = QComboBox()

        sheet_row.addWidget(
            self.sheet_combo
        )

        layout.addLayout(sheet_row)

        layout.addStretch()

        self.status = QLabel("Sẵn sàng.")

        layout.addWidget(self.status)

    def choose_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn File Excel",
            "",
            "Excel (*.xlsx)"
        )

        if not filename:
            return

        self.file_edit.setText(filename)

        try:

            sheets = self.excel_service.open_workbook(
                filename
            )

            self.sheet_combo.clear()

            self.sheet_combo.addItems(
                sheets
            )

            self.status.setText(
                f"Đã mở Workbook ({len(sheets)} sheet)"
            )

        except Exception as ex:

            self.status.setText(str(ex))
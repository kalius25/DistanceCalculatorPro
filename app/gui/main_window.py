from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from app.models.excel_table_model import ExcelTableModel
from app.services.excel_service import ExcelService


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Distance Calculator Pro")

        self.resize(1000, 650)

        self.excel_service = ExcelService()

        self.table_model = ExcelTableModel()

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

        self.sheet_combo.currentTextChanged.connect(
            self.load_preview
        )

        sheet_row.addWidget(
            self.sheet_combo
        )

        layout.addLayout(sheet_row)

        # ==========================
        # Preview
        # ==========================

        self.table = QTableView()

        self.table.setModel(self.table_model)

        self.table.setAlternatingRowColors(True)

        self.table.setSelectionBehavior(
            QTableView.SelectRows
        )

        self.table.setSelectionMode(
            QTableView.SingleSelection
        )

        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

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

            self.sheet_combo.blockSignals(True)

            self.sheet_combo.clear()

            self.sheet_combo.addItems(sheets)

            self.sheet_combo.blockSignals(False)

            if sheets:
                self.sheet_combo.setCurrentIndex(0)
                self.load_preview(sheets[0])

            self.status.setText(
                f"Đã mở Workbook ({len(sheets)} sheet)"
            )

        except Exception as ex:

            self.status.setText(str(ex))

    def load_preview(self, sheet_name: str):

        if not sheet_name:
            return

        try:

            headers = self.excel_service.read_headers(
                sheet_name
            )

            rows = self.excel_service.read_preview(
                sheet_name
            )

            self.table_model.set_data(
                headers,
                rows
            )

            self.table.resizeColumnsToContents()

            self.status.setText(
                f"Preview {len(rows)} dòng"
            )

        except Exception as ex:

            self.status.setText(str(ex))
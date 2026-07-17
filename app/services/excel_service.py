from pathlib import Path
from openpyxl import load_workbook


class ExcelService:
    """
    Xử lý đọc Workbook Excel.
    """

    def __init__(self):
        self.file_path = None
        self.workbook = None

    def open_workbook(self, file_path: str):

        self.file_path = Path(file_path)

        self.workbook = load_workbook(
            filename=self.file_path,
            read_only=True,
            data_only=True
        )

        return self.workbook.sheetnames

    def get_sheet_names(self):

        if self.workbook is None:
            return []

        return self.workbook.sheetnames
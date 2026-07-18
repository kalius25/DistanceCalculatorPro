"""
Distance Calculator Pro

Calculation Controller
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.route_models import RouteRequest
from app.services.excel_service import ExcelService


@dataclass(slots=True)
class ColumnMapping:
    origin: str
    destination: str
    distance: str
    duration: str


class CalculationController:

    def __init__(self, excel_service: ExcelService):

        self._excel = excel_service

    # ======================================================
    # Workbook
    # ======================================================

    def get_sheet_names(self) -> list[str]:
        return self._excel.get_sheet_names()

    def get_headers(self, sheet_name: str) -> list[str]:
        return self._excel.read_headers(sheet_name)

    def get_preview(
        self,
        sheet_name: str,
        max_rows: int = 100,
    ):
        headers = self._excel.read_headers(sheet_name)
        rows = self._excel.read_preview(
            sheet_name,
            max_rows=max_rows,
        )

        return headers, rows

    # ======================================================
    # Validate
    # ======================================================

    def validate_mapping(
        self,
        mapping: ColumnMapping,
    ) -> tuple[bool, str]:

        if not mapping.origin:
            return False, "Chưa chọn Origin."

        if not mapping.destination:
            return False, "Chưa chọn Destination."

        if mapping.origin == mapping.destination:
            return False, "Origin và Destination không được trùng."

        if not mapping.distance:
            return False, "Chưa chọn cột Distance."

        if not mapping.duration:
            return False, "Chưa chọn cột Duration."

        return True, ""

    # ======================================================
    # Build Requests
    # ======================================================

    def build_requests(
        self,
        sheet_name: str,
        mapping: ColumnMapping,
    ) -> list[RouteRequest]:

        ok, message = self.validate_mapping(mapping)

        if not ok:
            raise ValueError(message)

        headers = self._excel.read_headers(sheet_name)

        rows = self._excel.read_all(sheet_name)

        header_index = {
            name: index
            for index, name in enumerate(headers)
        }

        requests: list[RouteRequest] = []

        for excel_row, values in enumerate(rows, start=2):

            origin = values[
                header_index[mapping.origin]
            ]

            destination = values[
                header_index[mapping.destination]
            ]

            requests.append(
                RouteRequest(
                    row_number=excel_row,
                    origin=str(origin).strip(),
                    destination=str(destination).strip(),
                )
            )

        return requests
from pathlib import Path

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from app.batch.summary import BatchSummary
from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode
from app.presentation.workspace_configuration import (
    ColumnMapping,
    ProviderConfiguration,
    WorkspaceConfiguration,
)
from app.workbooks.models import WorkbookInfo, WorksheetInfo


class HomePage(QWidget):
    """File workspace with selection, recent files and workbook preview."""

    browse_requested = Signal()
    clear_recent_requested = Signal()
    file_selected = Signal(str)
    sheet_changed = Signal(str)
    column_mapping_changed = Signal(str, str, str)
    provider_configuration_changed = Signal(str, str, bool, bool, bool)
    workspace_configuration_changed = Signal(object)
    workspace_ready_changed = Signal(bool)
    retry_failed_requested = Signal()

    SUPPORTED_EXTENSIONS = frozenset({".xlsx", ".xlsm", ".csv"})
    DEFAULT_PREVIEW_ROWS = 20
    PREVIEW_ROW_OPTIONS = (20, 50, 100, 200, 500)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected_file: str | None = None
        self._workbook_info: WorkbookInfo | None = None
        self._current_worksheet: WorksheetInfo | None = None
        self._preview_row_limit = self.DEFAULT_PREVIEW_ROWS
        self._mapping_valid = False
        self._provider_valid = False
        self._workspace_ready = False
        self._workspace_locked = False
        self.setObjectName("pageWorkspace")
        self.setAcceptDrops(True)
        self._create_widgets()
        self._create_layout()
        self._connect_signals()
        self._apply_initial_state()

    @property
    def selected_file(self) -> str | None:
        return self._selected_file

    @property
    def workbook_info(self) -> WorkbookInfo | None:
        return self._workbook_info

    @property
    def selected_sheet_name(self) -> str | None:
        if self._current_worksheet is None:
            return None
        return self._current_worksheet.name

    @property
    def column_mapping(self) -> ColumnMapping | None:
        if not self._mapping_valid:
            return None
        return ColumnMapping(
            origin_column=str(self._origin_column_selector.currentData()),
            destination_column=str(self._destination_column_selector.currentData()),
            result_column=str(self._result_column_selector.currentData()),
        )

    @property
    def provider_configuration(self) -> ProviderConfiguration | None:
        if not self._provider_valid:
            return None
        return ProviderConfiguration(
            provider=ProviderType(str(self._provider_selector.currentData())),
            travel_mode=TravelMode(str(self._travel_mode_selector.currentData())),
            avoid_tolls=self._avoid_tolls_checkbox.isChecked(),
            avoid_highways=self._avoid_highways_checkbox.isChecked(),
            avoid_ferries=self._avoid_ferries_checkbox.isChecked(),
        )

    @property
    def workspace_configuration(self) -> WorkspaceConfiguration | None:
        mapping = self.column_mapping
        provider = self.provider_configuration
        if mapping is None or provider is None:
            return None
        return WorkspaceConfiguration(
            mapping,
            provider,
            skip_existing_results=(self._skip_existing_results_checkbox.isChecked()),
        )

    @property
    def workspace_ready(self) -> bool:
        return self._workspace_ready

    @property
    def workspace_locked(self) -> bool:
        return self._workspace_locked

    @classmethod
    def accepts_file(cls, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in cls.SUPPORTED_EXTENSIONS

    def set_selected_file(self, file_path: str) -> None:
        normalized_path = str(Path(file_path))
        path = Path(normalized_path)
        self._selected_file = normalized_path
        self._selected_file_name.setText(path.name)
        self._selected_file_path.setText(normalized_path)
        self._selected_file_path.setToolTip(normalized_path)
        self._file_information_frame.setVisible(True)
        self._empty_file_information.setVisible(False)
        self._file_ready_label.setText("Inspecting workbook…")
        self.clear_inspection()
        self._workspace_status.setText("Inspecting workbook…")

    def clear_selected_file(self) -> None:
        self._selected_file = None
        self._selected_file_name.clear()
        self._selected_file_path.clear()
        self._file_information_frame.setVisible(False)
        self._empty_file_information.setVisible(True)
        self._workspace_status.setText("No workbook selected")
        self.clear_inspection()

    def set_inspection(self, workbook_info: WorkbookInfo) -> None:
        self._workbook_info = workbook_info
        self._file_type_value.setText(workbook_info.file_type)
        self._file_size_value.setText(
            f"{self._format_file_size(workbook_info.file_size_bytes)} "
            f"({workbook_info.file_size_bytes:,} bytes)"
        )
        self._modified_value.setText(
            workbook_info.modified_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        self._file_ready_label.setText("Ready to inspect")
        self._file_ready_label.setProperty("ready", True)
        self._refresh_style(self._file_ready_label)

        self._sheet_selector.blockSignals(True)
        self._sheet_selector.clear()
        self._sheet_selector.addItems(
            [sheet.name for sheet in workbook_info.worksheets]
        )
        self._sheet_selector.blockSignals(False)
        self._inspector_frame.setVisible(True)

        if workbook_info.worksheets:
            self._show_worksheet(workbook_info.worksheets[0])
            self._workspace_status.setText(
                f"Workbook ready · {len(workbook_info.worksheets)} sheet(s)"
            )
        else:
            self._clear_worksheet_details()
            self._headers_status_value.setText("No")
            self._workspace_status.setText("Workbook contains no worksheets")

        self._toggle_source_panels_button.setChecked(True)

    def set_inspection_error(self, message: str) -> None:
        self.clear_inspection()
        self._file_ready_label.setText("Inspection failed")
        self._file_ready_label.setProperty("ready", False)
        self._refresh_style(self._file_ready_label)
        self._workspace_status.setText(f"Inspection failed · {message}")

    def clear_inspection(self) -> None:
        self._workbook_info = None
        self._current_worksheet = None
        if hasattr(self, "_inspector_frame"):
            self._inspector_frame.setVisible(False)
            self._sheet_selector.clear()
            self._preview_model.clear()
        if hasattr(self, "_origin_column_selector"):
            self._populate_column_mapping(())
        if hasattr(self, "_workspace_readiness_status"):
            self._update_workspace_readiness()

    def set_recent_files(self, file_paths: list[str]) -> None:
        self._recent_files.clear()
        if not file_paths:
            item = QListWidgetItem("No recent workbooks")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._recent_files.addItem(item)
            self._clear_recent_button.setEnabled(False)
            return

        self._clear_recent_button.setEnabled(True)
        for file_path in file_paths:
            path = Path(file_path)
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self._recent_files.addItem(item)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if self._event_file_path(event) is not None:
            event.acceptProposedAction()
            self._drop_zone.setProperty("dragActive", True)
            self._refresh_style(self._drop_zone)
            return
        event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:  # noqa: N802
        self._reset_drop_zone()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        file_path = self._event_file_path(event)
        self._reset_drop_zone()
        if file_path is None:
            event.ignore()
            return
        event.acceptProposedAction()
        self.file_selected.emit(file_path)

    def _create_widgets(self) -> None:
        self._title_label = QLabel("File Workspace", self)
        self._title_label.setObjectName("lblPageTitle")
        self._description_label = QLabel(
            "Select an Excel or CSV workbook to begin a distance-calculation job.",
            self,
        )
        self._description_label.setObjectName("lblPageDescription")
        self._toggle_source_panels_button = QPushButton("Hide file panels", self)
        self._toggle_source_panels_button.setObjectName("btnToggleSourcePanels")
        self._toggle_source_panels_button.setCheckable(True)
        self._toggle_source_panels_button.setIcon(qta.icon("fa5s.chevron-up"))

        self._selection_frame = self._create_section_frame("frmSelectionPanel")
        selection_layout = QVBoxLayout(self._selection_frame)
        selection_layout.setContentsMargins(16, 14, 16, 16)
        selection_layout.setSpacing(10)
        selection_layout.addWidget(self._section_title("Select Workbook"))

        self._drop_zone = QFrame(self._selection_frame)
        self._drop_zone.setObjectName("frmDropZone")
        drop_layout = QVBoxLayout(self._drop_zone)
        drop_layout.setContentsMargins(18, 18, 18, 18)
        drop_layout.setSpacing(7)
        self._drop_icon = QLabel(self._drop_zone)
        self._drop_icon.setObjectName("lblDropIcon")
        self._drop_icon.setPixmap(qta.icon("fa5s.upload").pixmap(36, 36))
        self._drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_title = QLabel("Drag & drop a workbook here", self._drop_zone)
        self._drop_title.setObjectName("lblDropTitle")
        self._drop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_hint = QLabel(
            "Supported formats: .xlsx, .xlsm, .csv", self._drop_zone
        )
        self._drop_hint.setObjectName("lblDropHint")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(self._drop_icon)
        drop_layout.addWidget(self._drop_title)
        drop_layout.addWidget(self._drop_hint)
        selection_layout.addWidget(self._drop_zone, 1)

        or_layout = QHBoxLayout()
        or_layout.addStretch(1)
        or_label = QLabel("or", self._selection_frame)
        or_label.setObjectName("lblDropHint")
        or_layout.addWidget(or_label)
        or_layout.addStretch(1)
        selection_layout.addLayout(or_layout)
        self._browse_button = QPushButton("Browse files…", self._selection_frame)
        self._browse_button.setObjectName("btnBrowseWorkbook")
        self._browse_button.setIcon(qta.icon("fa5s.folder-open"))
        selection_layout.addWidget(
            self._browse_button, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self._recent_frame = self._create_section_frame("frmRecentPanel")
        recent_layout = QVBoxLayout(self._recent_frame)
        recent_layout.setContentsMargins(0, 14, 0, 0)
        recent_layout.setSpacing(8)
        recent_title = self._section_title("Recent Workbooks")
        recent_title.setContentsMargins(16, 0, 16, 0)
        recent_layout.addWidget(recent_title)
        self._recent_files = QListWidget(self._recent_frame)
        self._recent_files.setObjectName("lstRecentWorkbooks")
        self._recent_files.setAlternatingRowColors(True)
        recent_layout.addWidget(self._recent_files, 1)
        self._clear_recent_button = QPushButton("Clear Recent List", self._recent_frame)
        self._clear_recent_button.setObjectName("btnClearRecent")
        self._clear_recent_button.setIcon(qta.icon("fa5s.trash-alt"))
        recent_layout.addWidget(self._clear_recent_button)

        self._file_panel = self._create_section_frame("frmFilePanel")
        file_panel_layout = QVBoxLayout(self._file_panel)
        file_panel_layout.setContentsMargins(16, 14, 16, 16)
        file_panel_layout.setSpacing(10)
        file_panel_layout.addWidget(self._section_title("File Information"))
        self._empty_file_information = QLabel(
            "Select a workbook to view its information.", self._file_panel
        )
        self._empty_file_information.setObjectName("lblWorkspaceEmptyState")
        self._empty_file_information.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_file_information.setWordWrap(True)
        file_panel_layout.addWidget(self._empty_file_information, 1)

        self._file_information_frame = QFrame(self._file_panel)
        self._file_information_frame.setObjectName("frmSelectedFile")
        file_info_layout = QVBoxLayout(self._file_information_frame)
        file_info_layout.setContentsMargins(12, 12, 12, 12)
        file_info_layout.setSpacing(9)
        file_heading = QHBoxLayout()
        self._selected_icon = QLabel(self._file_information_frame)
        self._selected_icon.setPixmap(qta.icon("fa5s.file-excel").pixmap(34, 34))
        heading_text = QVBoxLayout()
        self._selected_file_name = QLabel(self._file_information_frame)
        self._selected_file_name.setObjectName("lblSelectedFileName")
        self._file_ready_label = QLabel(self._file_information_frame)
        self._file_ready_label.setObjectName("lblFileReady")
        heading_text.addWidget(self._selected_file_name)
        heading_text.addWidget(self._file_ready_label)
        file_heading.addWidget(self._selected_icon)
        file_heading.addLayout(heading_text, 1)
        file_info_layout.addLayout(file_heading)

        detail_grid = QGridLayout()
        detail_grid.setHorizontalSpacing(12)
        detail_grid.setVerticalSpacing(9)
        self._file_type_value = QLabel(self._file_information_frame)
        self._file_size_value = QLabel(self._file_information_frame)
        self._modified_value = QLabel(self._file_information_frame)
        self._selected_file_path = QLabel(self._file_information_frame)
        self._selected_file_path.setWordWrap(True)
        for row, (caption, value) in enumerate(
            (
                ("Type:", self._file_type_value),
                ("Size:", self._file_size_value),
                ("Modified:", self._modified_value),
                ("Path:", self._selected_file_path),
            )
        ):
            caption_label = QLabel(caption, self._file_information_frame)
            caption_label.setObjectName("lblInspectorCaption")
            value.setObjectName("lblInspectorValue")
            detail_grid.addWidget(caption_label, row, 0)
            detail_grid.addWidget(value, row, 1)
        detail_grid.setColumnStretch(1, 1)
        file_info_layout.addLayout(detail_grid)
        file_panel_layout.addWidget(self._file_information_frame, 1)

        self._create_inspector_widgets()
        self._create_summary_widgets()
        self._workspace_status = QLabel(self)
        self._workspace_status.setObjectName("lblWorkspaceStatus")

    def _create_inspector_widgets(self) -> None:
        self._inspector_frame = self._create_section_frame("frmWorkbookInspector")
        inspector_layout = QVBoxLayout(self._inspector_frame)
        inspector_layout.setContentsMargins(16, 14, 16, 14)
        inspector_layout.setSpacing(10)
        inspector_layout.addWidget(self._section_title("Workbook Inspector"))

        summary_layout = QHBoxLayout()
        worksheet_layout = QVBoxLayout()
        worksheet_caption = QLabel("Worksheet", self._inspector_frame)
        worksheet_caption.setObjectName("lblInspectorCaption")
        self._sheet_selector = QComboBox(self._inspector_frame)
        self._sheet_selector.setObjectName("cmbWorksheet")
        worksheet_layout.addWidget(worksheet_caption)
        worksheet_layout.addWidget(self._sheet_selector)
        summary_layout.addLayout(worksheet_layout, 3)

        preview_rows_layout = QVBoxLayout()
        preview_rows_caption = QLabel("Preview rows", self._inspector_frame)
        preview_rows_caption.setObjectName("lblInspectorCaption")
        self._preview_rows_selector = QComboBox(self._inspector_frame)
        self._preview_rows_selector.setObjectName("cmbPreviewRows")
        self._preview_rows_selector.addItems(
            tuple(str(value) for value in self.PREVIEW_ROW_OPTIONS)
        )
        self._preview_rows_selector.setCurrentText(str(self.DEFAULT_PREVIEW_ROWS))
        preview_rows_layout.addWidget(preview_rows_caption)
        preview_rows_layout.addWidget(self._preview_rows_selector)
        summary_layout.addLayout(preview_rows_layout, 1)

        self._row_count_value = self._summary_value("Rows", summary_layout)
        self._column_count_value = self._summary_value("Columns", summary_layout)
        self._headers_status_value = self._summary_value(
            "Detected headers", summary_layout
        )
        summary_layout.addStretch(1)
        inspector_layout.addLayout(summary_layout)

        self._mapping_frame = QFrame(self._inspector_frame)
        self._mapping_frame.setObjectName("frmColumnMapping")
        mapping_layout = QGridLayout(self._mapping_frame)
        mapping_layout.setContentsMargins(12, 10, 12, 10)
        mapping_layout.setHorizontalSpacing(12)
        mapping_layout.setVerticalSpacing(6)
        mapping_title = QLabel("Column Mapping", self._mapping_frame)
        mapping_title.setObjectName("lblSectionTitle")
        mapping_layout.addWidget(mapping_title, 0, 0, 1, 3)
        self._origin_column_selector = self._mapping_selector(
            "Origin column", "cmbOriginColumn", mapping_layout, 1
        )
        self._destination_column_selector = self._mapping_selector(
            "Destination column", "cmbDestinationColumn", mapping_layout, 2
        )
        self._result_column_selector = self._mapping_selector(
            "Result column", "cmbResultColumn", mapping_layout, 3
        )
        self._mapping_status = QLabel(self._mapping_frame)
        self._mapping_status.setObjectName("lblMappingStatus")
        mapping_layout.addWidget(self._mapping_status, 4, 0, 1, 3)
        mapping_layout.setColumnStretch(0, 1)
        mapping_layout.setColumnStretch(1, 1)
        mapping_layout.setColumnStretch(2, 1)
        self._provider_frame = QFrame(self._inspector_frame)
        self._provider_frame.setObjectName("frmProviderConfiguration")
        provider_layout = QGridLayout(self._provider_frame)
        provider_layout.setContentsMargins(12, 10, 12, 10)
        provider_layout.setHorizontalSpacing(12)
        provider_layout.setVerticalSpacing(6)
        provider_title = QLabel("Route Provider", self._provider_frame)
        provider_title.setObjectName("lblSectionTitle")
        provider_layout.addWidget(provider_title, 0, 0, 1, 3)

        provider_caption = QLabel("Provider", self._provider_frame)
        provider_caption.setObjectName("lblInspectorCaption")
        self._provider_selector = QComboBox(self._provider_frame)
        self._provider_selector.setObjectName("cmbRouteProvider")
        self._provider_selector.addItem(
            ProviderType.GOOGLE_MAPS_WEB.value,
            ProviderType.GOOGLE_MAPS_WEB.value,
        )
        provider_layout.addWidget(provider_caption, 1, 0)
        provider_layout.addWidget(self._provider_selector, 2, 0)

        travel_caption = QLabel("Travel mode", self._provider_frame)
        travel_caption.setObjectName("lblInspectorCaption")
        self._travel_mode_selector = QComboBox(self._provider_frame)
        self._travel_mode_selector.setObjectName("cmbTravelMode")
        for label, mode in (
            ("Driving", TravelMode.DRIVING),
            ("Walking", TravelMode.WALKING),
        ):
            self._travel_mode_selector.addItem(label, mode.value)
        provider_layout.addWidget(travel_caption, 1, 1)
        provider_layout.addWidget(self._travel_mode_selector, 2, 1)

        avoid_caption = QLabel("Route options", self._provider_frame)
        avoid_caption.setObjectName("lblInspectorCaption")
        provider_layout.addWidget(avoid_caption, 1, 2)
        avoid_layout = QHBoxLayout()
        self._avoid_tolls_checkbox = QCheckBox("Avoid tolls", self._provider_frame)
        self._avoid_tolls_checkbox.setObjectName("chkAvoidTolls")
        self._avoid_highways_checkbox = QCheckBox(
            "Avoid highways", self._provider_frame
        )
        self._avoid_highways_checkbox.setObjectName("chkAvoidHighways")
        self._avoid_ferries_checkbox = QCheckBox("Avoid ferries", self._provider_frame)
        self._avoid_ferries_checkbox.setObjectName("chkAvoidFerries")
        avoid_layout.addWidget(self._avoid_tolls_checkbox)
        avoid_layout.addWidget(self._avoid_highways_checkbox)
        avoid_layout.addWidget(self._avoid_ferries_checkbox)
        avoid_layout.addStretch(1)
        provider_layout.addLayout(avoid_layout, 2, 2)

        self._skip_existing_results_checkbox = QCheckBox(
            "Skip rows already containing a result",
            self._provider_frame,
        )
        self._skip_existing_results_checkbox.setObjectName("chkSkipExistingResults")
        self._skip_existing_results_checkbox.setChecked(True)
        provider_layout.addWidget(self._skip_existing_results_checkbox, 3, 0, 1, 3)

        self._provider_status = QLabel(self._provider_frame)
        self._provider_status.setObjectName("lblProviderStatus")
        provider_layout.addWidget(self._provider_status, 4, 0, 1, 3)

        self._workspace_readiness_status = QLabel(self._provider_frame)
        self._workspace_readiness_status.setObjectName("lblWorkspaceReadinessStatus")
        provider_layout.addWidget(self._workspace_readiness_status, 5, 0, 1, 3)
        provider_layout.setColumnStretch(0, 1)
        provider_layout.setColumnStretch(1, 1)
        provider_layout.setColumnStretch(2, 3)
        configuration_row = QHBoxLayout()
        configuration_row.setSpacing(10)
        configuration_row.addWidget(self._mapping_frame, 1)
        configuration_row.addWidget(self._provider_frame, 1)
        inspector_layout.addLayout(configuration_row)

        preview_frame = QFrame(self._inspector_frame)
        preview_frame.setObjectName("frmPreviewPanel")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        preview_layout.setSpacing(8)
        self._preview_title = QLabel(
            f"Data Preview (first {self.DEFAULT_PREVIEW_ROWS} rows)",
            preview_frame,
        )
        self._preview_title.setObjectName("lblPreviewTitle")
        preview_layout.addWidget(self._preview_title)
        self._preview_table = QTableView(preview_frame)
        self._preview_table.setObjectName("tblDataPreview")
        self._preview_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._preview_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._preview_table.setAlternatingRowColors(True)
        self._preview_table.verticalHeader().setDefaultSectionSize(24)
        self._preview_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self._preview_table.horizontalHeader().setStretchLastSection(True)
        self._preview_model = QStandardItemModel(self._preview_table)
        self._preview_table.setModel(self._preview_model)
        preview_layout.addWidget(self._preview_table, 1)
        inspector_layout.addWidget(preview_frame, 1)

    def _create_summary_widgets(self) -> None:
        self._summary_frame = self._create_section_frame("frmBatchSummary")
        summary_layout = QHBoxLayout(self._summary_frame)
        summary_layout.setContentsMargins(16, 10, 16, 10)
        summary_layout.setSpacing(12)
        self._summary_label = QLabel("No batch summary available", self._summary_frame)
        self._summary_label.setObjectName("lblBatchSummary")
        self._summary_label.setWordWrap(True)
        self._retry_failed_button = QPushButton("Retry Failed", self._summary_frame)
        self._retry_failed_button.setObjectName("btnRetryFailed")
        self._retry_failed_button.setIcon(qta.icon("fa5s.redo"))
        self._retry_failed_button.setEnabled(False)
        summary_layout.addWidget(self._summary_label, 1)
        summary_layout.addWidget(self._retry_failed_button)
        self._summary_frame.setVisible(False)

    def set_batch_summary(self, summary: BatchSummary) -> None:
        """Render the latest batch summary and expose retry when useful."""
        state = "Stopped" if summary.stopped else "Completed"
        self._summary_label.setText(
            f"{state}: {summary.successful:,}/{summary.total:,} successful · "
            f"Failed {summary.failed:,} · Skipped {summary.skipped:,} · "
            f"Invalid {summary.invalid:,} · Retried {summary.retry_count:,}"
        )
        self._retry_failed_button.setEnabled(summary.failed > 0)
        self._summary_frame.setVisible(True)

    def clear_batch_summary(self) -> None:
        """Clear the visible batch summary and disable retry."""
        self._summary_label.setText("No batch summary available")
        self._retry_failed_button.setEnabled(False)
        self._summary_frame.setVisible(False)

    def _create_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Keep the workspace heading and status in a dedicated, non-collapsible
        # container. Hiding the source panels must never reflow these labels.
        self._workspace_header = QFrame(self)
        self._workspace_header.setObjectName("frmWorkspaceHeader")
        self._workspace_header.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        header_layout = QVBoxLayout(self._workspace_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        heading_layout = QHBoxLayout()
        heading_layout.addWidget(self._title_label)
        heading_layout.addStretch(1)
        heading_layout.addWidget(self._toggle_source_panels_button)
        header_layout.addLayout(heading_layout)
        self._description_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._workspace_status.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        header_layout.addWidget(self._description_label)
        header_layout.addWidget(self._workspace_status)
        layout.addWidget(
            self._workspace_header,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        layout.addWidget(self._summary_frame)

        self._source_panels_container = QWidget(self)
        top_layout = QHBoxLayout(self._source_panels_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)
        top_layout.addWidget(self._selection_frame, 1)
        top_layout.addWidget(self._recent_frame, 1)
        top_layout.addWidget(self._file_panel, 1)
        layout.addWidget(self._source_panels_container, 2)
        layout.addWidget(self._inspector_frame, 5)

    def _connect_signals(self) -> None:
        self._browse_button.clicked.connect(self.browse_requested.emit)
        self._clear_recent_button.clicked.connect(self.clear_recent_requested.emit)
        self._recent_files.itemActivated.connect(self._on_recent_file_activated)
        self._sheet_selector.currentTextChanged.connect(self._on_sheet_changed)
        self._preview_rows_selector.currentTextChanged.connect(
            self._on_preview_row_limit_changed
        )
        for selector in (
            self._origin_column_selector,
            self._destination_column_selector,
            self._result_column_selector,
        ):
            selector.currentTextChanged.connect(self._on_mapping_changed)
        self._provider_selector.currentTextChanged.connect(
            self._on_provider_configuration_changed
        )
        self._travel_mode_selector.currentTextChanged.connect(
            self._on_provider_configuration_changed
        )
        for checkbox in (
            self._avoid_tolls_checkbox,
            self._avoid_highways_checkbox,
            self._avoid_ferries_checkbox,
        ):
            checkbox.toggled.connect(self._on_provider_option_toggled)
        self._skip_existing_results_checkbox.toggled.connect(
            self._on_resume_option_toggled
        )
        self._toggle_source_panels_button.toggled.connect(
            self._set_source_panels_hidden
        )
        self._retry_failed_button.clicked.connect(self.retry_failed_requested.emit)

    def _apply_initial_state(self) -> None:
        self.clear_selected_file()
        self.set_recent_files([])
        self._sync_route_option_availability()
        self._validate_provider_configuration()
        self._update_workspace_readiness()
        self.clear_batch_summary()

    def _show_worksheet(self, worksheet: WorksheetInfo) -> None:
        self._current_worksheet = worksheet
        self._row_count_value.setText(f"{worksheet.row_count:,}")
        self._column_count_value.setText(f"{worksheet.column_count:,}")
        has_headers = bool(worksheet.headers and any(worksheet.headers))
        self._headers_status_value.setText("Yes" if has_headers else "No")
        self._populate_column_mapping(worksheet.headers)
        self._render_preview(worksheet)

    def _render_preview(self, worksheet: WorksheetInfo) -> None:
        self._preview_model.clear()
        headers = list(worksheet.headers)
        column_count = max(
            worksheet.column_count,
            len(headers),
            max((len(row) for row in worksheet.preview_rows), default=0),
        )
        if not headers:
            headers = [f"Column {index}" for index in range(1, column_count + 1)]
        elif len(headers) < column_count:
            headers.extend(
                f"Column {index}" for index in range(len(headers) + 1, column_count + 1)
            )
        self._preview_model.setHorizontalHeaderLabels(headers)
        for row in worksheet.preview_rows[: self._preview_row_limit]:
            values = list(row) + [""] * (column_count - len(row))
            items: list[QStandardItem] = []
            for value in values:
                item = QStandardItem(value)
                item.setToolTip(value)
                items.append(item)
            self._preview_model.appendRow(items)
        preview_count = min(len(worksheet.preview_rows), self._preview_row_limit)
        self._preview_title.setText(
            f"Data Preview (first {preview_count} rows)"
            if preview_count
            else "Data Preview (no data rows)"
        )
        self._resize_preview_columns()

    def _set_source_panels_hidden(self, hidden: bool) -> None:
        self._source_panels_container.setVisible(not hidden)
        self._toggle_source_panels_button.setText(
            "Show file panels" if hidden else "Hide file panels"
        )
        icon_name = "fa5s.chevron-down" if hidden else "fa5s.chevron-up"
        self._toggle_source_panels_button.setIcon(qta.icon(icon_name))

    def _on_preview_row_limit_changed(self, value: str) -> None:
        try:
            preview_row_limit = int(value)
        except ValueError:
            return
        if preview_row_limit not in self.PREVIEW_ROW_OPTIONS:
            return
        self._preview_row_limit = preview_row_limit
        if self._current_worksheet is not None:
            self._render_preview(self._current_worksheet)

    def _resize_preview_columns(self) -> None:
        self._preview_table.resizeColumnsToContents()
        header = self._preview_table.horizontalHeader()
        for column in range(self._preview_model.columnCount()):
            width = min(max(header.sectionSize(column), 120), 360)
            header.resizeSection(column, width)

    def _clear_worksheet_details(self) -> None:
        self._current_worksheet = None
        for label in (
            self._row_count_value,
            self._column_count_value,
            self._headers_status_value,
        ):
            label.setText("0")
        self._preview_model.clear()
        self._populate_column_mapping(())

    def _on_sheet_changed(self, sheet_name: str) -> None:
        if self._workbook_info is None:
            return
        worksheet = next(
            (
                sheet
                for sheet in self._workbook_info.worksheets
                if sheet.name == sheet_name
            ),
            None,
        )
        if worksheet is not None:
            self._show_worksheet(worksheet)
            self.sheet_changed.emit(sheet_name)

    def _on_recent_file_activated(self, item: QListWidgetItem) -> None:
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(file_path, str):
            self.file_selected.emit(file_path)

    def _event_file_path(self, event: QDragEnterEvent | QDropEvent) -> str | None:
        urls = event.mimeData().urls()
        if len(urls) != 1 or not urls[0].isLocalFile():
            return None
        file_path = urls[0].toLocalFile()
        return file_path if self.accepts_file(file_path) else None

    def _reset_drop_zone(self) -> None:
        self._drop_zone.setProperty("dragActive", False)
        self._refresh_style(self._drop_zone)

    @staticmethod
    def _refresh_style(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _mapping_selector(
        self,
        caption: str,
        object_name: str,
        layout: QGridLayout,
        column: int,
    ) -> QComboBox:
        label = QLabel(caption, self._mapping_frame)
        label.setObjectName("lblInspectorCaption")
        selector = QComboBox(self._mapping_frame)
        selector.setObjectName(object_name)
        layout.addWidget(label, 1, column - 1)
        layout.addWidget(selector, 2, column - 1)
        return selector

    def _populate_column_mapping(self, headers: tuple[str, ...]) -> None:
        selectors = (
            self._origin_column_selector,
            self._destination_column_selector,
            self._result_column_selector,
        )
        for selector in selectors:
            selector.blockSignals(True)
            selector.clear()
            selector.addItem("Select column…", "")
            for index, header in enumerate(headers, start=1):
                display_name = header or f"Column {index}"
                selector.addItem(display_name, display_name)
            selector.blockSignals(False)
        self._auto_detect_mapping(headers)
        self._validate_mapping()

    def _auto_detect_mapping(self, headers: tuple[str, ...]) -> None:
        normalized = {header.casefold().strip(): header for header in headers if header}
        keyword_groups = (
            (
                self._origin_column_selector,
                ("origin", "from", "điểm đi", "nơi đi", "tọa độ nơi đi"),
            ),
            (
                self._destination_column_selector,
                (
                    "destination",
                    "to",
                    "điểm đến",
                    "nơi đến",
                    "tọa độ nơi đến",
                ),
            ),
            (
                self._result_column_selector,
                ("result", "distance", "kết quả", "khoảng cách"),
            ),
        )
        for selector, keywords in keyword_groups:
            match = next(
                (
                    header
                    for key, header in normalized.items()
                    if any(word in key for word in keywords)
                ),
                None,
            )
            if match is not None:
                selector.setCurrentText(match)

    def _on_mapping_changed(self, _value: str) -> None:
        self._validate_mapping()

    def _validate_mapping(self) -> None:
        origin = self._origin_column_selector.currentData() or ""
        destination = self._destination_column_selector.currentData() or ""
        result = self._result_column_selector.currentData() or ""
        selected = [value for value in (origin, destination, result) if value]
        self._mapping_valid = len(selected) == 3 and len(set(selected)) == 3
        if self._mapping_valid:
            self._mapping_status.setText("Mapping ready")
            self._mapping_status.setProperty("valid", True)
            self.column_mapping_changed.emit(origin, destination, result)
        elif len(selected) != len(set(selected)):
            self._mapping_status.setText("Each role must use a different column")
            self._mapping_status.setProperty("valid", False)
        else:
            self._mapping_status.setText(
                "Select origin, destination and result columns"
            )
            self._mapping_status.setProperty("valid", False)
        self._refresh_style(self._mapping_status)
        self._update_workspace_readiness()

    def _on_resume_option_toggled(self, _checked: bool) -> None:
        self._update_workspace_readiness()

    def _on_provider_configuration_changed(self, _value: str) -> None:
        self._sync_route_option_availability()
        self._validate_provider_configuration()

    def _sync_route_option_availability(self) -> None:
        mode = self._travel_mode_selector.currentData()
        walking = mode == TravelMode.WALKING.value
        self._avoid_tolls_checkbox.setEnabled(not walking)
        self._avoid_highways_checkbox.setEnabled(not walking)
        if walking:
            self._avoid_tolls_checkbox.setChecked(False)
            self._avoid_highways_checkbox.setChecked(False)

    def _on_provider_option_toggled(self, _checked: bool) -> None:
        self._sync_route_option_availability()
        self._validate_provider_configuration()

    def _validate_provider_configuration(self) -> None:
        provider = self._provider_selector.currentData() or ""
        travel_mode = self._travel_mode_selector.currentData() or ""
        self._provider_valid = bool(provider and travel_mode)
        if self._provider_valid:
            self._provider_status.setText("Provider ready")
            self._provider_status.setProperty("valid", True)
            self.provider_configuration_changed.emit(
                provider,
                travel_mode,
                self._avoid_tolls_checkbox.isChecked(),
                self._avoid_highways_checkbox.isChecked(),
                self._avoid_ferries_checkbox.isChecked(),
            )
        else:
            self._provider_status.setText("Select a provider and travel mode")
            self._provider_status.setProperty("valid", False)
        self._refresh_style(self._provider_status)
        self._update_workspace_readiness()

    def _update_workspace_readiness(self) -> None:
        configuration = self.workspace_configuration
        ready = configuration is not None
        if ready:
            self._workspace_readiness_status.setText("Setup ready for calculation")
            self._workspace_readiness_status.setProperty("valid", True)
            self.workspace_configuration_changed.emit(configuration)
        elif not self._mapping_valid and not self._provider_valid:
            self._workspace_readiness_status.setText(
                "Complete column mapping and provider configuration"
            )
            self._workspace_readiness_status.setProperty("valid", False)
        elif not self._mapping_valid:
            self._workspace_readiness_status.setText("Complete column mapping")
            self._workspace_readiness_status.setProperty("valid", False)
        else:
            self._workspace_readiness_status.setText("Complete provider configuration")
            self._workspace_readiness_status.setProperty("valid", False)

        if ready != self._workspace_ready:
            self._workspace_ready = ready
            self.workspace_ready_changed.emit(ready)
        self._refresh_style(self._workspace_readiness_status)

    def set_workspace_locked(self, locked: bool) -> None:
        """Lock or unlock all inputs that define a calculation job."""
        self._workspace_locked = locked
        enabled = not locked
        self._source_panels_container.setEnabled(enabled)
        self._sheet_selector.setEnabled(enabled)
        self._preview_rows_selector.setEnabled(enabled)
        self._mapping_frame.setEnabled(enabled)
        self._provider_frame.setEnabled(enabled)

    def _create_section_frame(self, object_name: str) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName(object_name)
        return frame

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text, self)
        label.setObjectName("lblSectionTitle")
        return label

    def _summary_value(self, caption: str, parent_layout: QHBoxLayout) -> QLabel:
        block = QVBoxLayout()
        caption_label = QLabel(caption, self._inspector_frame)
        caption_label.setObjectName("lblInspectorCaption")
        value = QLabel("0", self._inspector_frame)
        value.setObjectName("lblSummaryValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        block.addWidget(caption_label, alignment=Qt.AlignmentFlag.AlignCenter)
        block.addWidget(value, alignment=Qt.AlignmentFlag.AlignCenter)
        parent_layout.addLayout(block, 1)
        return value

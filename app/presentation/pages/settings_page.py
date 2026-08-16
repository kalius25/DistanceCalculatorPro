from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    """User-facing appearance and diagnostics preferences."""

    theme_changed = Signal(str)
    diagnostics_changed = Signal(bool, bool, bool, bool, bool, bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_layout()
        self._connect_signals()
        self.set_theme("light")
        self.set_diagnostics(False, False, False, False, False, False)

    def _create_layout(self) -> None:
        title = QLabel("Settings")
        title.setObjectName("lblPageTitle")

        description = QLabel(
            "Configure application appearance and optional diagnostics."
        )
        description.setObjectName("lblPageDescription")
        description.setWordWrap(True)

        appearance_group = QGroupBox("Appearance")
        appearance_form = QFormLayout(appearance_group)
        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName("cmbSettingsTheme")
        self._theme_combo.addItem("Light", "light")
        self._theme_combo.addItem("Dark", "dark")
        appearance_form.addRow("Theme", self._theme_combo)

        diagnostics_group = QGroupBox("Diagnostics")
        diagnostics_layout = QVBoxLayout(diagnostics_group)

        self._debug_enabled = QCheckBox("Enable debug mode")
        self._debug_enabled.setObjectName("chkSettingsDebug")

        self._trace_browser = QCheckBox("Trace browser events")
        self._trace_browser.setObjectName("chkSettingsTraceBrowser")
        self._parser_diagnostics = QCheckBox("Parser diagnostics")
        self._parser_diagnostics.setObjectName("chkSettingsParserDiagnostics")
        self._save_html = QCheckBox("Save HTML")
        self._save_html.setObjectName("chkSettingsSaveHtml")
        self._save_screenshot = QCheckBox("Save screenshot")
        self._save_screenshot.setObjectName("chkSettingsSaveScreenshot")
        self._save_json = QCheckBox("Save parser JSON")
        self._save_json.setObjectName("chkSettingsSaveJson")

        diagnostics_layout.addWidget(self._debug_enabled)
        diagnostics_layout.addWidget(self._trace_browser)
        diagnostics_layout.addWidget(self._parser_diagnostics)
        diagnostics_layout.addWidget(self._save_html)
        diagnostics_layout.addWidget(self._save_screenshot)
        diagnostics_layout.addWidget(self._save_json)

        note = QLabel(
            "Diagnostic captures are disabled unless Debug Mode is enabled."
        )
        note.setObjectName("lblSettingsDiagnosticsNote")
        note.setWordWrap(True)
        diagnostics_layout.addWidget(note)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(appearance_group)
        layout.addWidget(diagnostics_group)
        layout.addStretch()

    def _connect_signals(self) -> None:
        self._theme_combo.currentIndexChanged.connect(self._emit_theme_changed)
        diagnostics_controls = (
            self._debug_enabled,
            self._trace_browser,
            self._parser_diagnostics,
            self._save_html,
            self._save_screenshot,
            self._save_json,
        )
        for control in diagnostics_controls:
            control.toggled.connect(self._on_diagnostics_changed)

    @property
    def theme_name(self) -> str:
        value = self._theme_combo.currentData()
        return value if isinstance(value, str) else "light"

    @property
    def diagnostics_state(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return (
            self._debug_enabled.isChecked(),
            self._trace_browser.isChecked(),
            self._parser_diagnostics.isChecked(),
            self._save_html.isChecked(),
            self._save_screenshot.isChecked(),
            self._save_json.isChecked(),
        )

    def set_theme(self, theme_name: str) -> None:
        index = self._theme_combo.findData(theme_name)
        if index >= 0:
            self._theme_combo.blockSignals(True)
            self._theme_combo.setCurrentIndex(index)
            self._theme_combo.blockSignals(False)
        else:
            self._theme_combo.blockSignals(True)
            self._theme_combo.setCurrentIndex(0)
            self._theme_combo.blockSignals(False)

    def set_diagnostics(
        self,
        enabled: bool,
        trace_browser: bool,
        parser_diagnostics: bool,
        save_html: bool,
        save_screenshot: bool,
        save_json: bool,
    ) -> None:
        controls = (
            (self._debug_enabled, enabled),
            (self._trace_browser, trace_browser),
            (self._parser_diagnostics, parser_diagnostics),
            (self._save_html, save_html),
            (self._save_screenshot, save_screenshot),
            (self._save_json, save_json),
        )
        for control, checked in controls:
            control.blockSignals(True)
            control.setChecked(checked)
            control.blockSignals(False)
        self._update_diagnostics_enabled_state(enabled)

    def _emit_theme_changed(self, _index: int) -> None:
        self.theme_changed.emit(self.theme_name)

    def _on_diagnostics_changed(self, _checked: bool) -> None:
        enabled = self._debug_enabled.isChecked()
        self._update_diagnostics_enabled_state(enabled)
        self.diagnostics_changed.emit(*self.diagnostics_state)

    def _update_diagnostics_enabled_state(self, enabled: bool) -> None:
        dependent_controls = (
            self._trace_browser,
            self._parser_diagnostics,
            self._save_html,
            self._save_screenshot,
            self._save_json,
        )
        for control in dependent_controls:
            control.setEnabled(enabled)

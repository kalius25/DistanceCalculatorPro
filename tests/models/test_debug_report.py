from pathlib import Path

from app.models.debug_report import DebugReport


def test_debug_report_defaults():
    report = DebugReport()

    assert report.url is None
    assert report.html_file is None
    assert report.screenshot_file is None
    assert report.parser_report_file is None
    assert report.error_message is None


def test_debug_report_custom_values():
    report = DebugReport(
        url="https://maps.google.com",
        html_file=Path("page.html"),
        screenshot_file=Path("page.png"),
        parser_report_file=Path("parser.txt"),
        error_message="Parse error",
    )

    assert report.url == "https://maps.google.com"
    assert report.html_file == Path("page.html")
    assert report.screenshot_file == Path("page.png")
    assert report.parser_report_file == Path("parser.txt")
    assert report.error_message == "Parse error"
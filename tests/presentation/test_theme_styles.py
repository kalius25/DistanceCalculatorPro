

def test_light_theme_uses_native_checkbox_indicator() -> None:
    from pathlib import Path

    stylesheet = Path(
        "app/presentation/styles/light.qss"
    ).read_text(encoding="utf-8")

    assert "QCheckBox::indicator" not in stylesheet


def test_dark_theme_uses_native_checkbox_indicator() -> None:
    from pathlib import Path

    stylesheet = Path(
        "app/presentation/styles/dark.qss"
    ).read_text(encoding="utf-8")

    assert "QCheckBox::indicator" not in stylesheet

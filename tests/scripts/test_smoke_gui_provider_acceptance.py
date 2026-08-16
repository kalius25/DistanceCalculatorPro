from pathlib import Path


def test_gui_acceptance_uses_one_qapplication_per_process() -> None:
    source = Path("scripts/smoke_gui_provider_acceptance.py").read_text(
        encoding="utf-8"
    )

    run_provider_source = source[
        source.index("def _run_provider(") : source.index("\n\ndef _print_result")
    ]
    main_source = source[source.index("def main(") :]

    assert "create_application()" not in run_provider_source
    assert main_source.count("create_application()") == 1

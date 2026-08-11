from unittest.mock import patch

import pytest

import app.__main__ as app_main


def test_run_exits_with_application_return_code() -> None:
    with patch.object(app_main, "main", return_value=7) as main:
        with pytest.raises(SystemExit) as error:
            app_main.run()

    main.assert_called_once_with()
    assert error.value.code == 7


def test_run_exits_with_zero_when_application_succeeds() -> None:
    with patch.object(app_main, "main", return_value=0):
        with pytest.raises(SystemExit) as error:
            app_main.run()

    assert error.value.code == 0

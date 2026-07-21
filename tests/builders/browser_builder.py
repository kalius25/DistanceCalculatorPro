from unittest.mock import MagicMock


def make_browser():
    browser = MagicMock()

    context = MagicMock()

    page = MagicMock()

    context.new_page.return_value = page

    browser.__enter__.return_value = context
    browser.__exit__.return_value = False

    return browser, context, page
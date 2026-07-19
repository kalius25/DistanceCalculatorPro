from app.engine.browser_manager import BrowserManager

with BrowserManager(headless=False) as browser:

    page = browser.new_page()

    page.goto("https://www.google.com")

    input("Chrome đã mở. Nhấn Enter để đóng...")
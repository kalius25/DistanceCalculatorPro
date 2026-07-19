from app.engine.browser_manager import BrowserManager
from app.engine.google_maps_engine import GoogleMapsEngine

with BrowserManager(headless=False) as browser:

    engine = GoogleMapsEngine(browser)

    page = engine.open_route(
    "Cần Thơ",
    "Long Xuyên"
)
    print(page.url)

    input("Quan sát Google Maps rồi nhấn Enter...")
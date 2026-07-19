from app.engine.browser_manager import BrowserManager
from app.engine.google_maps_engine import GoogleMapsEngine

with BrowserManager(headless=False) as browser:

    engine = GoogleMapsEngine(browser)

    ok, message = engine.health_check()

    print(ok)

    print(message)

    input("Nhấn Enter để kết thúc...")
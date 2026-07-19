from app.engine.browser_manager import BrowserManager
from app.engine.google_maps_engine import GoogleMapsEngine
from app.engine.google_maps_locator import GoogleMapsLocator

with BrowserManager(headless=False) as browser:

    engine = GoogleMapsEngine(browser)

    page = engine.open()

    print(
        GoogleMapsLocator.search_box(page).count()
    )

    input("Nhấn Enter để đóng...")
from app.engine.browser_manager import BrowserManager
from app.engine.google_maps_engine import GoogleMapsEngine
from app.engine.google_maps_parser import GoogleMapsParser


with BrowserManager(headless=False) as browser:

    engine = GoogleMapsEngine(browser)

    page = engine.open_route(
        "Cần Thơ",
        "Long Xuyên",
    )

    page.wait_for_timeout(3000)

    duration = GoogleMapsParser.parse_duration(page)

    distance = GoogleMapsParser.parse_distance(page)

    print()

    print("=" * 50)
    print("Duration :", duration)
    print("Distance :", distance)
    print("=" * 50)

    input("Press Enter...")
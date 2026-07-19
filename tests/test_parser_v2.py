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

    result = GoogleMapsParser.parse(
        page,
        origin="Cần Thơ",
        destination="Long Xuyên",
    )

    print("=" * 60)

    print("Provider :", result.provider)

    print("Success  :", result.success)

    print("Routes   :", len(result.routes))

    print("=" * 60)

    for i, route in enumerate(result.routes, start=1):

        print()

        print(f"Route #{i}")

        print("Summary :", route.summary)

        print("Distance:", route.distance_text)

        print("KM      :", route.distance_km)

        print("Duration:", route.duration_text)

        print("Minutes :", route.duration_minutes)

        print("Toll    :", route.has_toll)

    input("Press Enter...")
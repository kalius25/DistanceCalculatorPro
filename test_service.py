from app.engine.browser_manager import BrowserManager

from app.providers.google_web_provider import GoogleWebProvider

from app.services.calculation_service import CalculationService


with BrowserManager(headless=False) as browser:

    provider = GoogleWebProvider(browser)

    service = CalculationService(provider)

    result = service.calculate(
        "Cần Thơ",
        "Long Xuyên",
    )

    print()

    print("=" * 60)

    print(result.success)

    print(result.provider)

    print(result.origin)

    print(result.destination)

    print()

    for route in result.routes:

        print(route.distance_text)

        print(route.duration_text)

        print(route.distance_km)

        print(route.duration_minutes)

        print()

    input("Press Enter...")
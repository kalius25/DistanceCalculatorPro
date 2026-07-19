"""
Sprint 1.4

Kiểm thử toàn bộ Business Layer

RouteRequest
        ↓
CalculationService
        ↓
GoogleWebProvider
        ↓
GoogleMapsEngine
        ↓
GoogleMapsParser
        ↓
RouteResult
"""

from app.engine.browser_manager import BrowserManager

from app.enums.travel_mode import TravelMode
from app.enums.route_preference import RoutePreference

from app.models.route_request import RouteRequest

from app.providers.google_web_provider import GoogleWebProvider

from app.services.calculation_service import CalculationService


def print_result(result):

    print()
    print("=" * 80)

    print("Provider :", result.provider)
    print("Success  :", result.success)

    print("Origin   :", result.request.origin)
    print("Dest     :", result.request.destination)

    print("Travel   :", result.request.travel_mode.value)

    print("Toll     :", result.request.toll_preference.value)
    print("Ferry    :", result.request.ferry_preference.value)
    print("Highway  :", result.request.highway_preference.value)

    if not result.success:

        print()
        print("ERROR")
        print(result.error)

        return

    print()
    print("Found Routes :", len(result.routes))
    print("Best Route   :", result.selected_route + 1)

    print()

    for index, route in enumerate(result.routes, start=1):

        print("-" * 60)

        print(f"Route #{index}")

        print("Summary       :", route.summary)

        print()

        print("Distance Text :", route.distance_text)
        print("Distance KM   :", route.distance_km)

        print()

        print("Duration Text :", route.duration_text)
        print("Minutes       :", route.duration_minutes)

        print()

        print("Has Toll      :", route.has_toll)
        print("Has Ferry     :", route.has_ferry)
        print("Has Highway   :", route.has_highway)

    print("=" * 80)


def main():

    request = RouteRequest(

        origin="Cần Thơ",

        destination="Long Xuyên",

        travel_mode=TravelMode.DRIVING,

        toll_preference=RoutePreference.AUTO,

        ferry_preference=RoutePreference.AUTO,

        highway_preference=RoutePreference.AUTO,
    )

    with BrowserManager(headless=False) as browser:

        provider = GoogleWebProvider(browser)

        service = CalculationService(provider)

        result = service.calculate(request)

        print_result(result)

    input("\nPress ENTER to exit...")


if __name__ == "__main__":
    main()
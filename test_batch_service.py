"""
Kiểm thử toàn bộ pipeline:

RouteRequest
    ↓
CalculationService
    ↓
GoogleWebProvider
    ↓
GoogleMapsEngine
    ↓
GoogleMapsParser
"""

from app.engine.browser_manager import BrowserManager

from app.models.route_request import RouteRequest

from app.providers.google_web_provider import GoogleWebProvider

from app.services.calculation_service import CalculationService
from app.services.batch_calculation_service import BatchCalculationService


def progress(current, total, request, result):

    status = "OK" if result.success else "ERROR"

    print(
        f"[{current}/{total}] "
        f"{status} "
        f"{request.origin} -> {request.destination}"
    )

    if not result.success:
        print("   Error:", result.error)


def print_result(result):

    print("=" * 80)

    print("Provider      :", result.provider)
    print("Origin        :", result.origin)
    print("Destination   :", result.destination)
    print("Success       :", result.success)

    if not result.success:
        print("Error         :", result.error)
        return

    print("Total Routes  :", len(result.routes))
    print("Selected Route:", result.selected_route)

    best = result.best_route

    if best:

        print()

        print("***** BEST ROUTE *****")

        print("Summary       :", best.summary)
        print("Distance      :", best.distance_text)
        print("Distance (km) :", best.distance_km)

        print("Duration      :", best.duration_text)
        print("Minutes       :", best.duration_minutes)

        print("Has Toll      :", best.has_toll)

    print()

    print("----- ALL ROUTES -----")

    for i, route in enumerate(result.routes):

        print()

        print(f"Route #{i+1}")

        print("Summary :", route.summary)
        print("Distance:", route.distance_text)
        print("KM      :", route.distance_km)
        print("Duration:", route.duration_text)
        print("Minutes :", route.duration_minutes)
        print("Toll    :", route.has_toll)

    print("=" * 80)


def main():

    requests = [

        RouteRequest(
            origin="Cần Thơ",
            destination="Long Xuyên",
        ),

        RouteRequest(
            origin="Long Xuyên",
            destination="Châu Đốc",
        ),

        RouteRequest(
            origin="Mỹ Tho",
            destination="Cần Thơ",
        ),

        RouteRequest(
            origin="ABCXYZ",
            destination="Long Xuyên",
        ),
    ]

    with BrowserManager(headless=False) as browser:

        provider = GoogleWebProvider(browser)

        service = CalculationService(provider)

        batch = BatchCalculationService(service)

        results = batch.calculate(
            requests,
            progress_callback=progress,
        )

    print()
    print()
    print("#" * 80)
    print("SUMMARY")
    print("#" * 80)

    success = 0
    failed = 0

    for result in results:

        if result.success:
            success += 1
        else:
            failed += 1

        print_result(result)

    print()
    print("Success :", success)
    print("Failed  :", failed)
    print("Total   :", len(results))


if __name__ == "__main__":
    main()
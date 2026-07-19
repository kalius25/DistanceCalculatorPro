"""
Distance Calculator Pro

Google Maps Engine
"""

from __future__ import annotations

from playwright.sync_api import TimeoutError

from app.engine.browser_manager import BrowserManager

from app.engine.google_maps_locator import GoogleMapsLocator

from urllib.parse import quote_plus

from app.engine.google_maps_url_builder import GoogleMapsUrlBuilder

class GoogleMapsEngine:
    """
    Engine điều khiển Google Maps bằng Playwright.
    """

    GOOGLE_MAPS_URL = "https://www.google.com/maps"

    def __init__(self, browser: BrowserManager):

        self._browser = browser

    # =====================================================
    # Open Google Maps
    # =====================================================

    def open(self):

        page = self._browser.new_page()

        page.goto(
            self.GOOGLE_MAPS_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        return page

    # =====================================================
    # Health Check
    # =====================================================

    def health_check(self) -> tuple[bool, str]:

        try:

            page = self.open()

            title = page.title()

            if "Google Maps" in title:

                page.close()

                return True, title

            page.close()

            return False, title

        except TimeoutError:

            return False, "Timeout"

        except Exception as ex:

            return False, str(ex)

    def wait_until_ready(self, page):

        search = GoogleMapsLocator.search_box(page)

        search.wait_for(
            state="visible",
            timeout=30000,
        )

    def search_place(
        self,
        page,
        place: str,
    ):

        search = GoogleMapsLocator.search_box(page)

        search.click()

        search.fill("")

        search.fill(place)

        search.press("Enter")

        page.wait_for_load_state("networkidle")

    def search(self, page, keyword):

        search = GoogleMapsLocator.search_box(page)

        search.click()

        search.type("Cần Thơ", delay=50)

        print(page.evaluate("""
        () => document.activeElement.tagName
        """))

        print(page.evaluate("""
        () => document.activeElement.name
        """))

        page.keyboard.press("Enter")



    def open_route(self, origin: str, destination: str):

        origin = quote_plus(origin)
        destination = quote_plus(destination)

        url = (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={origin}"
            f"&destination={destination}"
            "&travelmode=driving"
        )

        page = self._browser.new_page()

        page.goto(
            url,
            wait_until="domcontentloaded",
        )

        return page
    
    def open_route(self, origin: str, destination: str,):

        page = self._browser.new_page()

        url = GoogleMapsUrlBuilder.build_route(
            origin,
            destination,
        )

        print("Open URL:")
        print(url)

        page.goto(
            url,
            wait_until="domcontentloaded",
        )

        return page
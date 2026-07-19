from pathlib import Path

from app.engine.browser_manager import BrowserManager
from app.engine.google_maps_engine import GoogleMapsEngine


OUTPUT_DIR = Path("logs") / "debug"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HTML_FILE = OUTPUT_DIR / "route.html"
PNG_FILE = OUTPUT_DIR / "route.png"


def main():

    with BrowserManager(headless=False) as browser:

        engine = GoogleMapsEngine(browser)

        page = engine.open_route(
            origin="Cần Thơ",
            destination="Long Xuyên",
        )

        print("=" * 60)
        print("Current URL")
        print(page.url)
        print("=" * 60)

        print("Waiting page render...")

        # Đợi giao diện Google Maps render đầy đủ
        page.wait_for_timeout(5000)

        print("Saving HTML...")

        html = page.content()

        HTML_FILE.write_text(
            html,
            encoding="utf-8",
        )

        print(f"Saved: {HTML_FILE}")

        print("Saving Screenshot...")

        page.screenshot(
            path=str(PNG_FILE),
            full_page=True,
        )

        print(f"Saved: {PNG_FILE}")

        print("=" * 60)
        print("Done")
        print("=" * 60)

        input("Press Enter to close browser...")


if __name__ == "__main__":
    main()
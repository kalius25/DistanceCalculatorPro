from pathlib import Path

APP_NAME = "Distance Calculator Pro"
APP_VERSION = "0.3.0"

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

APP_DIR = ROOT_DIR / "app"

RESOURCE_DIR = ROOT_DIR / "resources"

ICON_DIR = RESOURCE_DIR / "icons"

IMAGE_DIR = RESOURCE_DIR / "images"

STYLE_DIR = RESOURCE_DIR / "styles"

FONT_DIR = RESOURCE_DIR / "fonts"

TRANSLATION_DIR = RESOURCE_DIR / "translations"

LOG_DIR = ROOT_DIR / "logs"

DOC_DIR = ROOT_DIR / "docs"

TEST_DIR = ROOT_DIR / "tests"

DATA_DIR = ROOT_DIR / "data"

CACHE_DIR = DATA_DIR / "cache"

OUTPUT_DIR = DATA_DIR / "output"

TEMP_DIR = DATA_DIR / "temp"
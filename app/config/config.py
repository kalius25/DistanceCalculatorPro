from pathlib import Path

APP_NAME = "Distance Calculator Pro"

VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parents[2]

RESOURCE_DIR = ROOT / "app" / "resources"

DATABASE_DIR = ROOT / "database"

CACHE_DB = DATABASE_DIR / "distance_cache.db"

LOG_DIR = ROOT / "logs"

DEFAULT_SAVE_INTERVAL = 20

DEFAULT_THREADS = 2

GOOGLE_TIMEOUT = 30000
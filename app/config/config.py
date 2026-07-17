from pathlib import Path

APP_NAME = "Distance Calculator Pro"
APP_VERSION = "0.1.0"

ROOT_DIR = Path(__file__).resolve().parents[2]

RESOURCE_DIR = ROOT_DIR / "app" / "resources"

LOG_DIR = ROOT_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)
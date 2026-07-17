from loguru import logger

from app.config.config import LOG_DIR

logger.add(
    LOG_DIR / "application.log",
    rotation="5 MB",
    retention=10,
    encoding="utf-8"
)
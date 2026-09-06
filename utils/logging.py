"""Internal logging — technical details go here, never into user-facing
error messages (see ui error-state convention in pages/*)."""
import logging
import sys

_logger = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = logging.getLogger("foresight_nexus")
        _logger.setLevel(logging.INFO)
        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
            _logger.addHandler(handler)
    return _logger


def log_error(context: str, exc: Exception) -> None:
    get_logger().error(f"{context}: {exc!r}")

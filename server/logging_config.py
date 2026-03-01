import sys
from loguru import logger


def setup_logging():
    """
    Configure the root logger to write logs to stderr at INFO level.
    The log format is:
    {time:%Y-%m-%d %H:%M:%S} | {level} | {name} | {message}
    """
    logger.remove()

    logger.add(
        sys.stderr,
        catch=True,
        level="INFO",
        format=f"{time:%Y-%m-%d %H:%M:%S} | {level} | {name} | {message}",
    )


__all__ = ["logger", "setup_logging"]

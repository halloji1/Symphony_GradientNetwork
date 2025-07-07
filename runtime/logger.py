# runtime/logger.py

import logging
import sys

LOG_LEVEL = logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger("ecn")


def set_level(level: str):
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    logger.setLevel(level_map.get(level.lower(), logging.INFO))


def info(msg: str):
    logger.info(msg)


def debug(msg: str):
    logger.debug(msg)


def warning(msg: str):
    logger.warning(msg)


def error(msg: str):
    logger.error(msg)


def critical(msg: str):
    logger.critical(msg)

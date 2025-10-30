"""
COMP-5700 Exercise 11: Forensics with Logging (logger)
Author: Jacob Murrah
Date: 11/03/2025
"""


import logging
from pathlib import Path
import time

_LOG_FILE = Path(__file__).with_name("OUTPUT.log")
_LOG_FORMAT = "%(asctime)s %(levelname)s %(funcName)s %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z%z"

logger = logging.getLogger("exercise11")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    file_handler = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8")
    formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)

    formatter.converter = time.localtime
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def quote_str(val):
    if isinstance(val, str):
        return f"'{val}'"
    return val


def get_logger() -> logging.Logger:
    logger.info("Starting log for the exercise 11 code snippet.")
    return logger

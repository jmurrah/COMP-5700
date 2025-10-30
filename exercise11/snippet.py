"""
COMP-5700 Exercise 11: Forensics with Logging (snippet)
Author: Jacob Murrah
Date: 11/03/2025
"""


from logger import get_logger, quote_str

logger = get_logger()


def simpleDiv(a, b):
    logger.info("Arguments provided -> a:%s, b:%s", quote_str(a), quote_str(b))
    try:
        return a / b
    except Exception:
        logger.exception(
            "Exception encountered with a=%s, b=%s", quote_str(a), quote_str(b)
        )


def mul(a, b):
    logger.info("Arguments provided -> a:%s, b:%s", quote_str(a), quote_str(b))
    try:
        return a * b
    except Exception:
        logger.exception(
            "Exception encountered with a=%s, b=%s", quote_str(a), quote_str(b)
        )


def add(a, b):
    logger.info("Arguments provided -> a:%s, b:%s", quote_str(a), quote_str(b))
    try:
        return a + b
    except Exception:
        logger.exception(
            "Exception encountered with a=%s, b=%s", quote_str(a), quote_str(b)
        )


def sub(a, b):
    logger.info("Arguments provided -> a:%s, b:%s", quote_str(a), quote_str(b))
    try:
        return a - b
    except Exception:
        logger.exception(
            "Exception encountered with a=%s, b=%s", quote_str(a), quote_str(b)
        )


if __name__ == "__main__":
    print("Running code snippet with logging...")
    simpleDiv(10, 2)  # happy path
    simpleDiv(10, "4")  # type error exception

    mul(5, 4)  # happy path
    mul("5", "4")  # type error exception

    add(3, 7)  # happy path
    add("3", 7)  # type error exception

    sub(10, 4)  # happy path
    sub(10, "4")  # type error exception

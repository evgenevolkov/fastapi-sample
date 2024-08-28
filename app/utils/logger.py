from decouple import config
import logging


logging_level = config('logging_level')


def get_logger(name):
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging_level)
        formatter = logging.Formatter(
            '%(levelname)-8s - %(asctime)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.setLevel(logging_level)

    return logger
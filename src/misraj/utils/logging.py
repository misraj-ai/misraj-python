import dataclasses
import logging
from colorama import Fore, Style, init


def get_logger(name, rank=0):
    init()
    logger = logging.getLogger(f"{name}-{rank}")
    logger.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Custom formatter with colors
    class ColoredFormatter(logging.Formatter):
        format_str = f'[misraj][Rank {rank}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'

        FORMATS = {
            logging.INFO: Fore.GREEN + format_str + Style.RESET_ALL,
            logging.WARNING: Fore.YELLOW + format_str + Style.RESET_ALL,
            logging.ERROR: Fore.RED + format_str + Style.RESET_ALL,
            logging.DEBUG: format_str
        }

        def format(self, record):
            log_format = self.FORMATS.get(record.levelno, self.format_str)
            formatter = logging.Formatter(log_format)
            return formatter.format(record)

    # Set formatter
    console_handler.setFormatter(ColoredFormatter())

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger




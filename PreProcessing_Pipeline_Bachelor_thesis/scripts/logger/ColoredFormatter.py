import logging

from colorama import Fore, Style


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_colors = {
            logging.DEBUG: Fore.BLUE,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA
        }
        level_color = log_colors.get(record.levelno, Fore.WHITE)
        record.levelname = level_color + record.levelname + Style.RESET_ALL
        record.msg = level_color + str(record.msg) + Style.RESET_ALL
        return super().format(record)

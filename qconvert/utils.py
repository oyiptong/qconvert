import logging
import sys

command_logger_set = False


def setup_command_logger(loglevel=None):
    global command_logger_set
    if not command_logger_set:
        loglevel = loglevel or logging.INFO
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(loglevel)

        try:
            from colorlog import ColoredFormatter
            fmt = ColoredFormatter("%(log_color)s%(message)s",
                                   log_colors={
                                       "DEBUG": "cyan",
                                       "INFO": "green",
                                       "WARNING": "yellow",
                                       "ERROR": "red",
                                       "CRITICAL": "bold_red"})
        except ImportError:
            # fall back to non-colored output
            fmt = logging.Formatter("%(message)s")

        handler.setFormatter(fmt)

        logger = logging.getLogger("command")
        logger.addHandler(handler)
        logger.setLevel(loglevel)
        command_logger_set = True
    else:
        logger = logging.getLogger("command")

    return logger

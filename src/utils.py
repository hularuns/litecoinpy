import logging
import sys

def get_logger(module_name, log_level: int = logging.DEBUG):
    logger = logging.getLogger(module_name)

    if not logger.hasHandlers():
        # Set up the console handler
        log_format = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(log_format)

        logger.setLevel(log_level)
        logger.addHandler(console_handler)

        # Prevent propagation to the root logger
        logger.propagate = False

    return logger

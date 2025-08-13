import logging
from scripts.logger.ColoredFormatter import ColoredFormatter
from colorama import init


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with a colored formatter.
    
    Args:
        name (str): The name of the logger, typically passed as __name__.
        level: Logger level, default: logging.INFO
    
    Returns:
        logging.Logger: Configured logger.
    """
    # Initialize colorama
    init(autoreset=True)

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)  # You can change this level if needed

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Set the formatter to the console handler
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger

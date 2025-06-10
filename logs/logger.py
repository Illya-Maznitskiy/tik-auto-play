import logging
import os
import sys
from datetime import datetime


# Get the directory where the current script (logger.py) is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Get parent root with dirname()
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Define the logs directory relative to the project root
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# Define the log file path with a timestamp
LOG_FILE_PATH = os.path.join(
    LOG_DIR,
    f"tiktok_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
)


def setup_logger():
    """
    Sets up a logger that outputs to both the console and a file.
    """
    logger = logging.getLogger("tiktok_automation_logger")
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if the logger is already set up
    if not logger.handlers:
        # Create a formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console Handler
        console_handler = logging.StreamHandler(
            sys.stdout
        )  # Explicitly use stdout
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        console_handler.setStream(sys.stdout)
        console_handler.stream.reconfigure(encoding="utf-8", errors="replace")

        logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Initialize the logger
logger = setup_logger()

# Code block for testing the logger directly
if __name__ == "__main__":
    logger.info("This is an info message with an emoji 😊")
    logger.warning("Warning with ⚠️")
    logger.error("Error with ❌")
    print(f"Log file created at: {LOG_FILE_PATH}")

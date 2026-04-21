import logging
import sys
from pathlib import Path


def setup_logger(log_level=logging.INFO, log_file: Path = None):
    """Centralized logging configuration."""
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
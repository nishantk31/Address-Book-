import logging
import sys
from app.core.config import settings

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("address_book")
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.hasHandlers():
        return logger

    log_level_str = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    # Stream handler sending logs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    
    # Clear, production-ready logging format showing datetime, severity, source location
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.propagate = False
    
    return logger

logger = setup_logger()

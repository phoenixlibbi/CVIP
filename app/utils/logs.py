import logging
import os
from logging.handlers import RotatingFileHandler

def logging_setup():
    """Configure logging for the application"""
    # Define the log directory and files
    LOG_DIR = "logs"
    INFO_LOG = os.path.join(LOG_DIR, "info.log")
    ERROR_LOG = os.path.join(LOG_DIR, "error.log")
    
    # Create the log directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # Configure the logging for info logs
    info_logger = logging.getLogger("info_logger")
    info_logger.setLevel(logging.INFO)
    
    # Create a rotating file handler for info logs
    info_handler = RotatingFileHandler(INFO_LOG, maxBytes=1024 * 1024, backupCount=5)
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    info_logger.addHandler(info_handler)
    
    # Configure the logging for error logs
    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)
    
    # Create a rotating file handler for error logs
    error_handler = RotatingFileHandler(ERROR_LOG, maxBytes=1024 * 1024, backupCount=5)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(error_handler)
    
    return info_logger, error_logger
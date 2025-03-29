"""
Logging utility for the Event Throttler system.

This module provides centralized logging configuration and functions
for use throughout the application.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# Import default settings from config - direct import
from config import (
    LOG_LEVEL, 
    LOG_TO_CONSOLE, 
    LOG_TO_FILE, 
    LOG_DIRECTORY, 
    MAX_LOG_SIZE_MB, 
    LOG_BACKUP_COUNT
)

def setup_logger(
    logger_name: str,
    log_level: int = LOG_LEVEL,
    log_to_console: bool = LOG_TO_CONSOLE,
    log_to_file: bool = LOG_TO_FILE,
    log_dir: str = LOG_DIRECTORY,
    log_file: Optional[str] = None,
    max_file_size_mb: int = MAX_LOG_SIZE_MB,
    backup_count: int = LOG_BACKUP_COUNT
) -> logging.Logger:
    """
    Configure and return a logger with specified settings.
    
    Args:
        logger_name: Name of the logger to create/get
        log_level: Logging level (default: INFO)
        log_to_console: Whether to log to console (default: True)
        log_to_file: Whether to log to file (default: False)
        log_dir: Directory to store log files (default: "logs")
        log_file: Specific filename (default: same as logger_name + .log)
        max_file_size_mb: Maximum size of log file in MB before rotation (default: 10)
        backup_count: Number of backup log files to keep (default: 5)
        
    Returns:
        configured logging.Logger instance
    """
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers (in case the logger already exists)
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set default log filename based on logger name if not provided
        if log_file is None:
            log_file = f"{logger_name}.log"
        
        file_path = os.path.join(log_dir, log_file)
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=max_file_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Convenience function to get the root application logger
def get_app_logger(log_to_file: bool = False) -> logging.Logger:
    """
    Get the main application logger.
    
    Args:
        log_to_file: Whether to log to file (default: False)
        
    Returns:
        The configured application logger
    """
    return setup_logger(
        logger_name="event_throttler",
        log_to_file=log_to_file
    )

# Convenience function to get a module-specific logger
def get_module_logger(module_name: str, log_to_file: bool = False) -> logging.Logger:
    """
    Get a logger for a specific module within the application.
    
    Args:
        module_name: Name of the module (will be appended to the app logger name)
        log_to_file: Whether to log to file (default: False)
        
    Returns:
        The configured module logger
    """
    return setup_logger(
        logger_name=f"event_throttler.{module_name}",
        log_to_file=log_to_file
    )
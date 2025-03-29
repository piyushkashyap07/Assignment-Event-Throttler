"""
Configuration settings for the Event Throttler system.

This module contains various configuration settings that can be
adjusted without modifying the core code.
"""
import logging

# Logging Configuration
LOG_LEVEL = logging.INFO  # Default log level
LOG_TO_CONSOLE = True     # Whether to log to console
LOG_TO_FILE = False       # Whether to log to file by default
LOG_DIRECTORY = "logs"    # Directory to store log files
MAX_LOG_SIZE_MB = 10      # Maximum size of log file before rotation
LOG_BACKUP_COUNT = 5      # Number of backup log files to keep

# Throttler Configuration
DEFAULT_WINDOW = 10       # Default throttling window in seconds

# Performance Settings
CLEANUP_INTERVAL = 3600   # Interval (in seconds) to clean up old keys (optional feature)
MAX_KEYS = 1000000        # Maximum number of keys to track before cleanup
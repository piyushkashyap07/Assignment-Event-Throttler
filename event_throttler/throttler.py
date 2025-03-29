"""
Event Throttler for Trading Platform

This module provides an EventThrottler class that implements a sliding window
approach to throttle events based on a specified key.
"""
import threading
from typing import Dict, Optional
from collections import defaultdict

# Import the custom logger and configuration
from logger import get_module_logger
from config import DEFAULT_WINDOW

# Get a logger for this module
logger = get_module_logger("throttler")

class EventThrottler:
    """
    A class that throttles events based on a sliding window approach.
    
    For each unique key, only the first event within a specified time window
    is processed. All subsequent events within that window are ignored.
    """
    
    def __init__(self, window: int = DEFAULT_WINDOW):
        """
        Initialize the EventThrottler with a specified window size.
        
        Args:
            window: The throttling window in seconds (default from config).
        """
        self._window = window
        self._last_processed_timestamps: Dict[str, int] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        logger.info(f"EventThrottler initialized with window of {window} seconds")
    
    def should_process(self, timestamp: int, event_id: str, key: str) -> bool:
        """
        Determines if an event should be processed based on the throttling rule.
        
        Args:
            timestamp: Time (in seconds) the event arrived.
            event_id: Unique event ID (not used in throttling logic).
            key: Unique identifier for the user/session.
            
        Returns:
            bool: True if the event should be processed, False otherwise.
        """
        with self._lock:
            # Check if we've seen this key before
            if key not in self._last_processed_timestamps:
                # First time seeing this key, so process it
                self._last_processed_timestamps[key] = timestamp
                logger.debug(f"Processing new key: {key}, event: {event_id}, timestamp: {timestamp}")
                return True
            
            last_timestamp = self._last_processed_timestamps[key]
            time_diff = timestamp - last_timestamp
            
            # If the time difference is greater than the window, process the event
            if time_diff >= self._window:
                self._last_processed_timestamps[key] = timestamp
                logger.debug(f"Processing after window: {key}, event: {event_id}, " 
                             f"time since last: {time_diff}s")
                return True
            
            # Otherwise, throttle the event
            logger.debug(f"Throttling: {key}, event: {event_id}, " 
                         f"time since last: {time_diff}s (window: {self._window}s)")
            return False
    
    def update_window(self, new_window: int) -> None:
        """
        Updates the throttling window size dynamically.
        
        Args:
            new_window: The new throttling window size in seconds.
        """
        with self._lock:
            old_window = self._window
            self._window = new_window
            logger.info(f"Window updated from {old_window}s to {new_window}s")
    
    def get_window(self) -> int:
        """
        Returns the current throttling window size.
        
        Returns:
            int: The current window size in seconds.
        """
        with self._lock:
            return self._window
    
    def clear(self) -> None:
        """
        Clears all stored timestamps, effectively resetting the throttler.
        """
        with self._lock:
            self._last_processed_timestamps.clear()
            logger.info("EventThrottler has been cleared")
    
    def get_key_count(self) -> int:
        """
        Returns the number of keys currently being tracked.
        
        Returns:
            int: Number of keys in the throttler.
        """
        with self._lock:
            return len(self._last_processed_timestamps)
"""
Unit tests for the EventThrottler class.
"""
import unittest
import threading
import time
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
# This ensures we can import the modules directly
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

# Import the throttler module directly
from throttler import EventThrottler
from logger import setup_logger

# Configure a logger for tests with minimal output
test_logger = setup_logger(
    logger_name="event_throttler_tests",
    log_level=logging.WARNING  # Only show warnings and errors during tests
)

class EventThrottlerTests(unittest.TestCase):
    """Test cases for the EventThrottler class."""
    
    def test_basic_throttling(self):
        """Test basic throttling functionality with a single key."""
        throttler = EventThrottler(window=10)
        
        # First event should be processed
        self.assertTrue(throttler.should_process(1, "e1", "userA"))
        
        # Event within window should be throttled
        self.assertFalse(throttler.should_process(5, "e2", "userA"))
        
        # Event after window should be processed
        self.assertTrue(throttler.should_process(12, "e3", "userA"))
        
        # Event within new window should be throttled
        self.assertFalse(throttler.should_process(20, "e4", "userA"))
    
    def test_multiple_keys(self):
        """Test throttling with multiple keys."""
        throttler = EventThrottler(window=10)
        
        # Events for different users should be processed independently
        self.assertTrue(throttler.should_process(1, "e1", "userA"))
        self.assertTrue(throttler.should_process(2, "e2", "userB"))
        self.assertTrue(throttler.should_process(3, "e3", "userC"))
        
        # Events within window for each user should be throttled
        self.assertFalse(throttler.should_process(5, "e4", "userA"))
        self.assertFalse(throttler.should_process(6, "e5", "userB"))
        self.assertFalse(throttler.should_process(7, "e6", "userC"))
        
        # Events after window for each user should be processed
        self.assertTrue(throttler.should_process(12, "e7", "userA"))
        self.assertTrue(throttler.should_process(13, "e8", "userB"))
        self.assertTrue(throttler.should_process(14, "e9", "userC"))
    
    def test_edge_cases(self):
        """Test edge cases like exactly at window boundary."""
        throttler = EventThrottler(window=10)
        
        # First event processed
        self.assertTrue(throttler.should_process(10, "e1", "userA"))
        
        # Edge case: event exactly at window boundary should be processed
        self.assertTrue(throttler.should_process(20, "e2", "userA"))
        
        # Event just before window boundary should be throttled
        self.assertFalse(throttler.should_process(29, "e3", "userA"))
        
        # Event just after window boundary should be processed
        self.assertTrue(throttler.should_process(31, "e4", "userA"))
        
        # Test with zero timestamp
        self.assertTrue(throttler.should_process(0, "e5", "userB"))
    
    def test_update_window(self):
        """Test dynamic window update functionality."""
        throttler = EventThrottler(window=10)
        
        # First event processed
        self.assertTrue(throttler.should_process(1, "e1", "userA"))
        
        # Update window to 20 seconds
        throttler.update_window(20)
        
        # Event within new window should be throttled
        self.assertFalse(throttler.should_process(15, "e2", "userA"))
        
        # Event after new window should be processed
        self.assertTrue(throttler.should_process(22, "e3", "userA"))
    
    def test_thread_safety(self):
        """Test thread safety with concurrent access."""
        throttler = EventThrottler(window=10)
        results = []
        
        def worker(user_id, timestamps):
            for ts, event_id in timestamps:
                result = throttler.should_process(ts, event_id, f"user{user_id}")
                results.append((user_id, ts, event_id, result))
        
        # Create test data for 3 users with overlapping timestamps
        user1_data = [(1, "e1"), (5, "e4"), (12, "e7"), (15, "e10")]
        user2_data = [(2, "e2"), (7, "e5"), (13, "e8"), (16, "e11")]
        user3_data = [(3, "e3"), (9, "e6"), (14, "e9"), (17, "e12")]
        
        # Create and start threads
        threads = [
            threading.Thread(target=worker, args=(1, user1_data)),
            threading.Thread(target=worker, args=(2, user2_data)),
            threading.Thread(target=worker, args=(3, user3_data))
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Check expected results
        user_results = {1: [], 2: [], 3: []}
        for user_id, _, _, result in results:
            user_results[user_id].append(result)
        
        # For each user, the pattern should be: True, False, True, False
        for user_id in [1, 2, 3]:
            self.assertEqual(user_results[user_id].count(True), 2)
            self.assertEqual(user_results[user_id].count(False), 2)

if __name__ == "__main__":
    unittest.main()
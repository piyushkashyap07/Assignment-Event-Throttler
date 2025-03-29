"""
Example usage of the EventThrottler class.

This script demonstrates how to use the EventThrottler in a trading platform
scenario with both basic and advanced features.
"""
import sys
import time
import logging
import random
import os
from pathlib import Path
from threading import Thread

# Add the parent directory to the Python path
# This ensures we can import the modules directly
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

# Import the necessary modules directly
from throttler import EventThrottler
from logger import setup_logger

# Set up logging for the example script
# Make sure the logs directory exists
logs_dir = os.path.join(parent_dir, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure the logger
logger = setup_logger(
    logger_name="event_throttler_example",
    log_level=logging.INFO,
    log_to_console=True,
    log_to_file=True,
    log_dir=logs_dir,  # Use the absolute path
    log_file="example_run.log"
)

def basic_example():
    """Run the basic example from the problem statement."""
    logger.info("Running basic example...")
    throttler = EventThrottler(window=10)
    
    results = [
        throttler.should_process(1, "e1", "userA"),   # True (first event)
        throttler.should_process(5, "e2", "userA"),   # False (within 10s window)
        throttler.should_process(12, "e3", "userA"),  # True (after window)
        throttler.should_process(15, "e4", "userB"),  # True (new user)
        throttler.should_process(20, "e5", "userB"),  # False (still within window)
    ]
    
    expected = [True, False, True, True, False]
    
    for i, (result, expected_result) in enumerate(zip(results, expected)):
        logger.info(f"Event {i+1}: Expected {expected_result}, Got {result}")
    
    logger.info("Basic example completed.")

def high_load_example(num_users=1000, events_per_user=100):
    """
    Test the throttler under high load with many users and events.
    
    Args:
        num_users: Number of unique users to simulate.
        events_per_user: Number of events per user.
    """
    logger.info(f"Running high load example with {num_users} users " 
                f"and {events_per_user} events per user...")
    
    throttler = EventThrottler(window=5)
    start_time = time.time()
    
    processed_count = 0
    throttled_count = 0
    
    # Generate events for each user
    for user_id in range(num_users):
        user_key = f"user{user_id}"
        base_timestamp = 0
        
        for event_num in range(events_per_user):
            # Random time increment (0-10 seconds)
            timestamp_increment = random.randint(0, 10)
            base_timestamp += timestamp_increment
            event_id = f"e{user_id}_{event_num}"
            
            # Process the event
            result = throttler.should_process(base_timestamp, event_id, user_key)
            
            if result:
                processed_count += 1
            else:
                throttled_count += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    total_events = num_users * events_per_user
    
    logger.info(f"High load example completed in {total_time:.4f} seconds")
    logger.info(f"Total events: {total_events}")
    logger.info(f"Processed events: {processed_count} ({processed_count/total_events*100:.2f}%)")
    logger.info(f"Throttled events: {throttled_count} ({throttled_count/total_events*100:.2f}%)")
    logger.info(f"Events per second: {total_events/total_time:.2f}")
    logger.info(f"Active keys in throttler: {throttler.get_key_count()}")

def threaded_example():
    """Test the throttler with concurrent threads."""
    logger.info("Running threaded example...")
    throttler = EventThrottler(window=5)
    
    def user_thread(user_id, num_events=20):
        """Simulate events from a single user."""
        user_key = f"threadUser{user_id}"
        base_timestamp = 0
        processed = 0
        
        for i in range(num_events):
            # Random time increment (0-3 seconds)
            timestamp_increment = random.randint(0, 3)
            base_timestamp += timestamp_increment
            event_id = f"e{user_id}_{i}"
            
            result = throttler.should_process(base_timestamp, event_id, user_key)
            if result:
                processed += 1
        
        logger.info(f"Thread {user_id}: Processed {processed}/{num_events} events")
    
    # Create and start 10 threads
    threads = []
    for i in range(10):
        thread = Thread(target=user_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    logger.info("Threaded example completed.")

def dynamic_window_example():
    """Demonstrate dynamically changing the window size."""
    logger.info("Running dynamic window example...")
    throttler = EventThrottler(window=10)
    
    # Initial window of 10 seconds
    logger.info(f"Initial window: {throttler.get_window()} seconds")
    logger.info(f"Event at t=1: {throttler.should_process(1, 'e1', 'userX')}")  # True
    logger.info(f"Event at t=5: {throttler.should_process(5, 'e2', 'userX')}")  # False
    
    # Change window to 3 seconds
    throttler.update_window(3)
    logger.info(f"Window updated to: {throttler.get_window()} seconds")
    
    # With a 3-second window, this event would be outside the window from the first event
    # But the throttler uses the timestamp of the most recently processed event,
    # which was at t=1, so 5 is still within the new 3-second window from t=1
    logger.info(f"Event at t=5 (still throttled): {throttler.should_process(5, 'e3', 'userX')}")  # True
    
    # This event is outside the new window
    logger.info(f"Event at t=7: {throttler.should_process(7, 'e4', 'userX')}")  # False
    
    # This event is within the new window
    logger.info(f"Event at t=9: {throttler.should_process(9, 'e5', 'userX')}")  # True
    
    logger.info("Dynamic window example completed.")

if __name__ == "__main__":
    logger.info("Starting EventThrottler examples")
    
    # Run examples
    basic_example()
    print("\n")
    
    dynamic_window_example()
    print("\n")
    
    threaded_example()
    print("\n")
    
    # Reduce the number of users for quicker execution
    high_load_example(num_users=100, events_per_user=100)
    
    logger.info("All examples completed")
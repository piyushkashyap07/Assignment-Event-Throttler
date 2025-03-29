# Event Throttler

A high-performance event throttling system for trading platforms that prevents system overload by processing only the first event for a given key within a sliding time window.

## Features

- **Sliding Window Throttling**: For each key (user/session), only the first event within a time window is processed
- **High Performance**: Optimized for handling 100K+ unique keys
- **Thread-Safe**: Can be safely used in multi-threaded environments
- **Dynamic Window Adjustment**: Allows changing the throttling window size at runtime
- **Configurable Logging**: Centralized logging system with console and file output options
- **Modular Design**: Clean separation of concerns with configuration, logging, and core functionality

## Project Structure

```
event_throttler/
├── throttler.py            # Core EventThrottler class
├── logger.py               # Centralized logging utility
├── config.py               # Configuration settings
├── examples/
│   └── usage_example.py    # Example usage script
├── tests/
│   └── test_throttler.py   # Unit tests
└── logs/                   # Generated log files directory (created automatically)
```

## Usage

### Basic Usage

```python
from throttler import EventThrottler

# Create a throttler with the default window (from config.py)
throttler = EventThrottler()

# Or specify a custom window
throttler = EventThrottler(window=10)

# Check if events should be processed
print(throttler.should_process(1,  "e1", "userA"))   # True (first event)
print(throttler.should_process(5,  "e2", "userA"))   # False (within 10s window)
print(throttler.should_process(12, "e3", "userA"))   # True (after window)
print(throttler.should_process(15, "e4", "userB"))   # True (new user)
print(throttler.should_process(20, "e5", "userB"))   # False (still within window)
```

### Running the Example

```bash
# From the project root directory
python examples/usage_example.py
```

### Running Tests

```bash
# Run all tests
python tests/test_throttler.py

# Run a specific test
python tests/test_throttler.py EventThrottlerTests.test_basic_throttling
```

## Configuring Logging

The system uses a centralized logging utility that can be configured through `config.py` or at runtime:

```python
# In config.py - Default settings
LOG_LEVEL = logging.INFO
LOG_TO_CONSOLE = True
LOG_TO_FILE = False
LOG_DIRECTORY = "logs"

# At runtime - Enable file logging for a specific module
from logger import setup_logger
import logging

logger = setup_logger(
    logger_name="my_module",
    log_level=logging.DEBUG,  # More detailed logging
    log_to_file=True,         # Enable file logging
    log_file="my_module.log"  # Custom log file name
)

# Then use the logger as usual
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
```

## Dynamic Window Management

You can change the throttling window size at runtime:

```python
# Update the throttling window to 20 seconds
throttler.update_window(20)

# Get the current window size
current_window = throttler.get_window()  # Returns 20
```

## API Reference

### `EventThrottler(window: int = DEFAULT_WINDOW)`

- **window**: The throttling window in seconds (default from config.py)

### `should_process(timestamp: int, event_id: str, key: str) -> bool`

Determines if an event should be processed based on the throttling rule.

- **timestamp**: Time (in seconds) the event arrived
- **event_id**: Unique event ID (not used in throttling logic)
- **key**: Unique identifier for the user/session
- **Returns**: `True` if the event should be processed, `False` otherwise

### `update_window(new_window: int) -> None`

Updates the throttling window size dynamically.

- **new_window**: The new throttling window size in seconds

### `get_window() -> int`

Returns the current throttling window size.

- **Returns**: The current window size in seconds

### `clear() -> None`

Clears all stored timestamps, effectively resetting the throttler.

### `get_key_count() -> int`

Returns the number of keys currently being tracked.

- **Returns**: Number of keys in the throttler

## Performance Considerations

The `EventThrottler` uses a dictionary to store the last processed timestamp for each key, providing O(1) lookups for efficient performance even with a large number of keys.

Thread safety is implemented using a reentrant lock (`threading.RLock`), which allows the same thread to acquire the lock multiple times without deadlocking.

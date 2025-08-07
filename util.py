import sys
import traceback
import os
import time
import random

from playwright.sync_api import Page

# Define paths that are considered "library" paths
# Using sys.base_prefix and sys.exec_prefix for better robustness with virtual environments
STANDARD_LIBRARY_PATHS = [
    os.path.abspath(os.path.join(sys.base_prefix, 'lib', 'python' + sys.version[:3])),
    os.path.abspath(os.path.join(sys.exec_prefix, 'lib', 'python' + sys.version[:3])),
    os.path.abspath(os.path.join(sys.exec_prefix, 'lib', 'python' + sys.version[:3], 'lib-dynload')),
]

SITE_PACKAGES_PATHS = [
    os.path.abspath(path) for path in sys.path if 'site-packages' in path
]


def is_library_file(filepath):
    abs_filepath = os.path.abspath(filepath)
    for lib_path in STANDARD_LIBRARY_PATHS + SITE_PACKAGES_PATHS:
        try:
            # Check if the file path starts with a known library path
            # Using commonpath to determine if abs_filepath is within lib_path
            if os.path.commonpath([abs_filepath, lib_path]) == lib_path:
                return True
        except ValueError:
            # commonpath can raise ValueError if paths are on different drives
            pass
    return False


def print_filtered_traceback(exc_type=None, exc_value=None, tb=None):
    """
    Prints a traceback, attempting to filter out frames from standard
    library and site-packages. If no exception info is provided,
    it retrieves the current exception being handled.
    """
    # If no exception info is provided, get it from the current context
    if exc_type is None and exc_value is None and tb is None:
        exc_type, exc_value, tb = sys.exc_info()

    if tb is None:  # No exception active or passed
        print("No exception information available to print a traceback.")
        return

    print("--- Filtered Traceback (only your code) ---")

    # Extract all frames from the traceback object
    frames = traceback.extract_tb(tb)

    filtered_frames_str = ""
    found_your_code = False
    for frame_info in frames:
        # If the file is NOT a library file, include it
        if not is_library_file(frame_info.filename):
            found_your_code = True
            filtered_frames_str += f'  File "{frame_info.filename}", line {frame_info.lineno}, in {frame_info.name}\n'
            if frame_info.line:  # Add the source line if available
                filtered_frames_str += f'    {frame_info.line.strip()}\n'

    if found_your_code:
        print(filtered_frames_str)
    else:
        print("No 'your code' frames found in the traceback (all frames appear to be library calls).")

    # Print the exception type and message
    print(f"{exc_type.__name__}: {exc_value}")
    print("------------------------------------------")


def wait(min_seconds: float, max_seconds: float) -> None:
    """
    Waits for a random number of seconds between min_seconds and max_seconds.
    This function is asynchronous and should be awaited.

    Args:
        min_seconds: The minimum number of seconds to wait.
        max_seconds: The maximum number of seconds to wait.
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

# Helper function for human-like typing
def human_type(page: Page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.2) -> None:
    """
    Types text into a selector with a human-like delay between characters.

    Args:
        page: The Playwright page object.
        selector: The CSS selector of the input field.
        text: The text to type.
        min_delay: Minimum delay between key presses in seconds.
        max_delay: Maximum delay between key presses in seconds.
    """
    #print(f"Human-typing into '{selector}'...")
    for char in text:
        # Ensure you are using page.press() here, not page.type()
        page.press(selector, char)
        wait(min_delay, max_delay)
    #print(f"Finished typing into '{selector}'.")

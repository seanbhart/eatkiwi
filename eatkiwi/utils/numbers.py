"""
This module provides functions for working with numbers.

Functions:
    get_unix_time: Returns the current Unix time as an integer.

"""
import time


def get_unix_time() -> int:
    """
    Returns the current Unix time as an integer.

    Returns:
        int: The current Unix time.

    """
    return int(time.time())

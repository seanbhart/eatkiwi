"""
This module contains utility functions for sending generic casts.

Functions:
    error_reply(client, cast) -> None:
        Sends an error message to the author of a given cast.

"""

import logging
from farcaster.models import Parent


def error_reply(client, cast) -> None:
    """
    Sends an error message to the author of a given cast.

    Args:
        client: The client to use for sending the error message.
        cast: The cast that caused the error.

    Returns:
        None

    """
    try:
        client.post_cast(f"something went wrong. I think I lost my 🥝", parent=Parent(fid=cast.author.fid, hash=cast.hash))
    except Exception as e:
        logging.error(f"Failed sending message: {e}")

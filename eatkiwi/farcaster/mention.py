
import logging
from typing import Tuple
from farcaster.models import Parent
from eatkiwi.utils.openai import generate_pithy_reply


def mention(commands_instance, notification):
    # Check if the mention has a known command
    logging.info(f"notification cast: {notification.content.cast}")
    if commands_instance.command_exists(notification):
        commands_instance.handle_command(notification)
    else:

        # No command was given with the mention, so assume the caller wants the link "eaten"
        commands_instance.eat.eat_notification(notification)

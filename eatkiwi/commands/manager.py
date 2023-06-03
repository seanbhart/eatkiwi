"""
This file contains the command handling logic for the eatkiwi bot.
Special thanks to @alexpaden for the command framework used here.
Reference: https://github.com/alexpaden/ditti-bot
"""

import logging
import os

from farcaster.models import Parent
from eatkiwi.commands.eat import Eat

COM_EAT = "eat"


class Commands:
    def __init__(self, fcc, bot_fname, dev_mode):
        self.dev_mode = dev_mode
        self.fcc = fcc
        self.bot_fname = bot_fname
        self.eat = Eat(fcc, bot_fname, dev_mode)
        self.command_mapping = command_mapping = {
            COM_EAT: self.handle_eat_command,
        }

    # Check if a command exists after the mention
    def command_exists(self, notification):
        command_prefix = f"{self.bot_fname} "
        for command in self.command_mapping.keys():
            if notification.content.cast.text.lower().startswith(command_prefix + command):
                return True
        return False

    # Process a command given after mentioning the bot
    def handle_command(self, notification):
        command_prefix = f"{self.bot_fname} "
        for command, handler in self.command_mapping.items():
            if notification.content.cast.text.lower().startswith(command_prefix + command):
                handler(notification)
                break

    # Process a command given in a reply (with no mention)
    def handle_command(self, notification):
        for command, handler in self.command_mapping.items():
            if notification.content.cast.text.lower().startswith(command):
                handler(notification)
                break

    # Handle eat command
    def handle_eat_command(self, notification):
        self.handle_eat_command(
            notification, COM_EAT, self.perform_eat_command
        )

    # Post to farcaster
    def post_to_farcaster(self, text: str, parent: Parent):
        try:
            if dev_mode:
                logging.info("Posting to farcaster (but dev mode)")
            else:
                self.fcc.post_cast(text=text, parent=parent)
        except Exception as e:
            self.handle_error(e, "Error while posting to farcaster")

    # Perform eat command
    def perform_eat_command(self, notification):
        self.eat.eat_notification(notification)

    # Handle error
    def handle_error(self, error, message):
        logging.error(f"{message}: {error}")

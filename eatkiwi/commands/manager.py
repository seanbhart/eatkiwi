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
    
    # check if a command exists after the mention
    def command_exists(self, notification):
        command_prefix = f"{self.bot_fname} "
        for command in self.command_mapping.keys():
            if notification.content.cast.text.lower().startswith(command_prefix + command):
                return True
        return False

    # process a command given after mentioning the bot
    def handle_command(self, notification):
        command_prefix = f"{self.bot_fname} "
        for command, handler in self.command_mapping.items():
            if notification.content.cast.text.lower().startswith(command_prefix + command):
                handler(notification)
                break
    
    # process a command given in a reply (with no mention)
    def handle_command(self, notification):
        for command, handler in self.command_mapping.items():
            if notification.content.cast.text.lower().startswith(command):
                handler(notification)
                break

    def handle_generic_command(self, notification, command, perform_func):
        if self.should_command_run(
            notification.content.cast.hash,
            command,
            notification.content.cast.author.username,
        ):
            try:
                perform_func(notification)
                self.mark_command_run(notification.content.cast.hash)
            except Exception as e:
                self.handle_error(e, f"Error while handling {command} command")

    def handle_eat_command(self, notification):
        self.handle_eat_command(
            notification, COM_EAT, self.perform_eat_command
        )
    
    def handle_help_command(self, notification):
        self.handle_generic_command(notification, HELP_COM, self.perform_help_command)

    def post_to_farcaster(self, text: str, parent: Parent):
        try:
            if dev_mode:
                logging.info("Posting to farcaster (but dev mode)")
            else:
                self.fcc.post_cast(text=text, parent=parent)
        except Exception as e:
            self.handle_error(e, "Error while posting to farcaster")

    def perform_eat_command(self, notification):
        logging.info("Performing eat command")
        self.eat.eat_notification(notification)
        logging.info("Eat command completed")

    def perform_help_command(self, notification):
        logging.info("Performing help command")
        reply = (
            "Thanks for your interest in eatkiwi bot! "
            "Tag @seanhart for further assistance. 🥝"
        )
        parent = Parent(fid=notification.content.cast.author.fid, hash=notification.content.cast.hash)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Help command completed")
    
    def should_command_run(self, hash: str, type: str, username: str):
        try:
            result = (
                self.supabase.table("command").select("*").eq("hash", hash).execute()
            )
            if result.data == []:
                self.supabase.table("command").insert(
                    {"hash": hash, "type": type, "caller": username}
                ).execute()
                return True
            elif not result.data[0]["completed"]:
                return True
            else:
                return False
        except Exception as e:
            self.handle_error(e, "Error while checking if command should run: {hash}")
            return False

    def handle_error(self, error, message):
        logging.error(f"{message}: {error}")

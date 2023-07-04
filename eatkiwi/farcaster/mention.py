
import logging


def mention(commands_instance, notification):
    logging.info(f"mention: {notification}")
    # Check if the mention has a known command
    if commands_instance.command_exists(notification):
        commands_instance.handle_mention_command(notification)
    else:
        logging.info(f"[mention] No command found in mention: {notification.content.cast.text}")
        # No command was given with the mention, so assume the caller wants the link "eaten"
        commands_instance.eat.eat_notification(notification)

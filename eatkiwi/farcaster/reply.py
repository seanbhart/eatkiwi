import logging


def reply(commands_instance, notification):
    logging.info(f"reply: {notification}")
    # Check if the mention has a known command
    if commands_instance.command_exists(notification):
        commands_instance.handle_reply_command(notification)
    else:
        logging.info(f"[reply] No command found in reply: {notification.content.cast.text}")
        # No command was given with the mention, so assume the caller wants the link "eaten"
        commands_instance.eat.eat_notification(notification)

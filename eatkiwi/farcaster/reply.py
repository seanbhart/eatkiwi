import logging


def reply(commands_instance, notification):
    # TODO: process replies
    # Don't process replies at the moment, but log reply text
    # for behavior analysis - consider trying to process replies
    # without mentions or commands
    logging.info(f"REPLY: {notification.content.cast.text}")

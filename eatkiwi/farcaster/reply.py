import logging


def reply(commands_instance, notification):
    # Replies should have some text indicating the style of writing desired and
    # have the parent cast as an @eatkiwi cast with a link
    commands_instance.eat.eat_notification(notification)

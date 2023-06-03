"""
This module contains functions for listening to notifications and casts from Warpcast and responding according to commands.

Functions:
    stream_notifications(commands_instance) -> None:
        Streams new notifications to the loaded fid from Warpcast
    
    stream_casts(commands_instance) -> None:
        Streams any new casts from Warpcast

"""

import logging
from decouple import config
from pymongo import MongoClient
from eatkiwi.utils.links import extract_link, check_url_contains_domains
from eatkiwi.farcaster.mention import mention
from eatkiwi.farcaster.reply import reply
from eatkiwi.farcaster.utils import error_reply


def stream_notifications(commands_instance) -> None:
    """
    Streams new notifications to the loaded fid from Warpcast
    """
    logging.info("streaming notifications")
    fcc = commands_instance.fcc
    bot_fname = commands_instance.bot_fname
    
    for notification in fcc.stream_notifications(skip_existing=True):
        # Check the cast in the notification
        if not notification:
            continue

        # Check if the notification is for a mention or reply
        if notification.type == 'cast-mention':
            mention(commands_instance, notification)
        elif notification.type == 'cast-reply':
            reply(commands_instance, notification)


def stream_casts(commands_instance) -> None:
    """
    Streams any new casts from Warpcast
    """
    logging.info("streaming casts")
    fcc = commands_instance.fcc
    bot_fname = commands_instance.bot_fname

    mongo_client = MongoClient(config("MONGO_URL"))
    db = mongo_client[config("MONGO_DB_FC")]
    collection = db[config("MONGO_FC_COLLECTION_LINKS")]

    # Stream new casts, and if a link is found, repost to FC
    for cast in fcc.stream_casts():
        if not cast:
            continue
            
        current_cast = cast
        link = extract_link(current_cast.text)
        if link is None:
            continue
        
        # these domains should be avoided
        domains = ["kiwistand", "warpcast", "alphacaster", "twitter", "youtube.com", "youtu.be", "cloudinary", "imgur", "reddit", "discord"]
        if check_url_contains_domains(link, domains):
            continue
        
        # don't post the same link twice
        result = collection.find_one({"link": link})
        if result:
            continue

        try:
            # Post links directly in the text, not as an attachment or embed
            # to ensure the link is visible in the cast received by the notification stream (if someone mentions the content)
            fcc.post_cast(f"🥝 reply \"in the style of ___\" for a title and summary of this link 🥝\n{link}")
            collection.insert_one({"link": link})
            
        except Exception as e:
            logging.error(f"Failed sending message: {e}")
            error_reply(fcc, cast)

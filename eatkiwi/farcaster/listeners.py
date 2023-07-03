"""
This module contains functions for listening to notifications and casts from Warpcast and responding according to commands.

Functions:
    stream_notifications(commands_instance) -> None:
        Streams new notifications to the loaded fid from Warpcast
    
    stream_casts(commands_instance) -> None:
        Streams any new casts from Warpcast

"""

import json
import time
import logging
from decouple import config
from pymongo import MongoClient
from requests.exceptions import ChunkedEncodingError
from eatkiwi.utils.links import extract_link, get_text_from_webpage, check_url_contains_domains
from eatkiwi.utils.openai import check_link_for_web3_content
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
    
    retry_delay = 5

    while True:
        try:
            for notification in fcc.stream_notifications(skip_existing=True):
                # Check the cast in the notification
                if not notification:
                    continue

                # Check if the notification is for a mention or reply
                if notification.type == 'cast-mention':
                    mention(commands_instance, notification)
                elif notification.type == 'cast-reply':
                    reply(commands_instance, notification)
        
        except json.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError occurred while streaming notifications, retrying in {retry_delay} seconds: {e}")
            time.sleep(retry_delay)


def stream_casts(commands_instance) -> None:
    """
    Streams any new casts from Warpcast
    """
    logging.info("streaming casts")
    fcc = commands_instance.fcc
    bot_fname = commands_instance.bot_fname

    mongo_client = MongoClient(config("MONGO_URL"))
    db = mongo_client[config("MONGO_DB_FC")]
    collection_links = db[config("MONGO_FC_COLLECTION_LINKS")]
    collection_eat_casts = db[config("MONGO_FC_COLLECTION_EAT_CASTS")]

    max_retries = 3
    retry_delay = 5

    while True:
        try:
            # Stream new casts, and if a link is found, repost to FC
            for cast in fcc.stream_casts():
                if not cast: continue
                    
                current_cast = cast
                link = extract_link(current_cast.text)
                if link is None: continue
                
                # these domains should be avoided
                domains = config("BANNED_DOMAINS").split(',')
                if check_url_contains_domains(link, domains): continue
                
                # don't post the same link twice
                result = collection_links.find_one({"link": link})
                if result: continue
                
                try:
                    # check if the link contains web3 content
                    page_content = get_text_from_webpage(link)
                    if not page_content: continue
                    answer, title = check_link_for_web3_content(page_content)
                    if not answer:
                        # store rejected links in the database as well
                        collection_links.insert_one({"link": link})
                        continue
                except Exception as e:
                    logging.error(f"Failed getting title or saving link: {e}")
                    continue
                
                try:
                    # Post links directly in the text, not as an attachment or embed
                    # to ensure the link is visible in the cast received by the
                    # notification stream (if someone mentions the content)
                    cast_content = fcc.post_cast(f"🥝 {title}\n{link}")

                    # store the link in a separate collection to provide a simple check for duplicates
                    collection_links.insert_one({"link": link})

                    # store the original cast in a separate collection for reference if requested
                    collection_eat_casts.insert_one({
                        "eat_cast_hash": cast_content.cast.hash,
                        "original_cast_hash": current_cast.hash,
                        "original_cast_username": current_cast.author.username
                    })
                except Exception as e:
                    logging.error(f"[stream_casts] Failed sending message: {e}")
                    continue

        except ChunkedEncodingError as e:
            max_retries -= 1
            if max_retries <= 0:
                logging.error(f"Failed to stream casts after multiple retries: {e}")
                break
            logging.warning(f"ChunkedEncodingError occurred, retrying in {retry_delay} seconds: {e}")
            time.sleep(retry_delay)
        
        except json.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError occurred while streaming casts, retrying in {retry_delay} seconds: {e}")
            time.sleep(retry_delay)

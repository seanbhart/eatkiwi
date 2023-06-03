"""
This module contains functions for listening to notifications and casts from Warpcast and responding according to commands.

Functions:
    stream_notifications(commands_instance) -> None:
        Streams new notifications to the loaded fid from Warpcast
    
    stream_casts(commands_instance) -> None:
        Streams any new casts from Warpcast

"""

import json
import logging
from decouple import config
from pymongo import MongoClient
from farcaster.models import Parent
from eatkiwi.utils.strings import truncate_string_by_character, trim_generated_cast_text, remove_substrings, trim_to_cast_max_bytes
from eatkiwi.utils.links import extract_link, check_url_contains_domains, get_text_from_webpage
from eatkiwi.utils.openai import generate_webpage_title, generate_webpage_title_and_summary
from eatkiwi.farcaster.mention import mention
from eatkiwi.farcaster.reply import reply
from eatkiwi.farcaster.utils import error_reply
from eatkiwi.kiwi.message import send_link_to_kiwistand


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

        logging.info(f"notification: {notification}")
        logging.info(f"notification type: {notification.type}")
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
    # fcc = commands_instance.fcc
    # bot_fname = commands_instance.bot_fname

    # mongo_client = MongoClient(config("MONGO_URL"))
    # db = mongo_client[config("MONGO_DB_FC")]
    # collection = db[config("MONGO_FC_COLLECTION_LINKS")]

    # # Stream new casts, and if a link is found, post to kiwistand
    # for cast in fcc.stream_casts():
    #     if not cast:
    #         continue
            
    #     current_cast = cast
    #     link = extract_link(current_cast.text)
    #     if link is None:
    #         continue
        
    #     # these domains should be avoided
    #     domains = ["kiwistand.com", "warpcast.com", "alphacaster.xyz"]
    #     if check_url_contains_domains(link, domains):
    #         continue
        
    #     # don't post the same link twice
    #     result = collection.find_one({"link": link})
    #     if result:
    #         continue

    #     page_content = get_text_from_webpage(link)
    #     if page_content is None:
    #         continue

    #     # title = generate_webpage_title(page_content)
    #     # summary = generate_webpage_summary(page_content)
    #     title, summary = generate_webpage_title_and_summary(page_content)
    #     if title is None or summary is None:
    #         continue

    #     # remove any substrings from the title and summary
    #     substrings_to_remove = ["Title: ", "Summary: "]
    #     title = remove_substrings(title, substrings_to_remove)
    #     summary = remove_substrings(summary, substrings_to_remove)

    #     if title is None or title == "" or title == " " or title == "Access denied":
    #         continue

    #     # now that it is likely to be castable, save the link to the db
    #     collection.insert_one({"link": link})

    #     try:
    #         # truncate the entire cast to the max cast length (320 bytes)
    #         generated_cast = trim_generated_cast_text(title, current_cast.author.username, current_cast.hash, link, max_bytes=320, dev=dev)
    #     except Exception as e:
    #         logging.error(f"Failed trimming cast: {e}")
    #         error_reply(fcc, cast)

    #     # post the link to fc
    #     try:
    #         # Post links directly in the text, not as an attachment or embed
    #         # to ensure the link is visible in the cast received by the notification stream
    #         eatkiwi_cast = fcc.post_cast(generated_cast)

    #         # Post a reply to the cast with a trimmed summary (if needed)
    #         summary = trim_to_cast_max_bytes(summary)
    #         # client.post_cast(f"🥝 summary\n{summary}", parent=Parent(fid=eatkiwi_cast.author.fid, hash=eatkiwi_cast.hash))
    #         fcc.post_cast(summary, parent=Parent(fid=eatkiwi_cast.cast.author.fid, hash=eatkiwi_cast.cast.hash))

    #     except Exception as e:
    #         logging.error(f"Failed sending message: {e}")
    #         error_reply(fcc, cast)


# def eat_kiwi_cast(commands_instance) -> None:
#     fcc = commands_instance.fcc
#     bot_fname = commands_instance.bot_fname

#     # Stream new casts mentioning the chatbot, find the link in the cast, and post to kiwistand
#     for cast in fcc.stream_notifications(skip_existing=True):
#         if not cast:
#             continue
            
#         # check if cast has the word "eat" in it
#         # if it does get the original cast and send the link to kiwistand
#         if "eat" not in cast.content.cast.text.lower() or cast.content.cast.parent_hash is None:
#             continue
        
#         # ensure the parent cast (original cast) is from the bot
#         original_cast = fcc.get_cast(cast.content.cast.parent_hash).cast
#         if original_cast.author.username != bot_fname:
#             logging.warn("STRANGE BEHAVIOR: parent cast is not from bot, ending")
#             continue

#         link = extract_link(original_cast.text)
#         if link is None:
#             # try to find an embedded link or an attachment link
#             if hasattr(original_cast, 'embeds') and original_cast.embeds is not None:
#                 if original_cast.embeds[0].url is not None:
#                     link = original_cast.embeds[0].url
#             elif hasattr(original_cast, 'attachments') and original_cast.attachments is not None:
#                 if original_cast.attachments[0].open_graph.url is not None:
#                     link = original_cast.attachments[0].open_graph.url
#             continue

#         # check if link is from urls to skip
#         domains = ["kiwistand.com", "warpcast.com", "alphacaster.xyz"]
#         if check_url_contains_domains(link, domains):
#             continue

#         # title = get_page_title(link)
#         page_content = get_text_from_webpage(link)
#         title = generate_webpage_title(page_content)

#         if title is None or title == "" or title == " " or title == "Access denied":
#             continue

#         # send link to kiwistand
#         # truncate the title to the max kiwi post length (80 characters)
#         title = truncate_string_by_character(title, max_characters=80)
#         if send_link_to_kiwistand(link, title, mnemonic):
#             try:
#                 # add a reaction to the notificationying cast
#                 fcc.post_cast("🥝 nom nom nom\nhttps://news.kiwistand.com/new", parent=Parent(fid=cast.content.cast.author.fid, hash=cast.content.cast.hash))
#             except Exception as e:
#                 logging.error(f"Failed sending message: {e}")
#                 error_reply(fcc, cast)
import logging
from decouple import config
from farcaster import Warpcast
from farcaster.models import Parent
from eatkiwi.utils.bytes import cut_off_string
from eatkiwi.utils.links import extract_link, get_page_title
from eatkiwi.utils.kiwi import send_link_to_kiwistand


# The client will automagically cycle through access tokens
client = Warpcast(config("FARCASTER_MNEMONIC_DEV01"), rotation_duration=1)

def trim_to_cast(s):
    return cut_off_string(s, 320)

def stream_notifications():
    # Stream new casts mentioning the chatbot, find the link in the cast, and post to kiwistand
    for cast in client.stream_notifications(skip_existing=True):
        if cast:
            logging.info(f"hash: {cast.content.cast.hash}:")
            logging.info(f"parent_hash: {cast.content.cast.parent_hash}:")
            logging.info(f"thread_hash: {cast.content.cast.thread_hash}:")
            logging.info(f"text: {cast.content.cast.text}:")
            logging.info(f"mentions: {cast.content.cast.mentions}:")
            logging.info(f"reactions: {cast.content.cast.reactions}:")
            logging.info(f"username: {cast.actor.username}:")
            logging.info(f"display_name: {cast.actor.display_name}:")
            logging.info("----")

            link = extract_link(cast.text)
            logging.info(f"link: {link}")
            title = get_page_title(link)
            logging.info(f"title: {title}")

            # if link is not None and title is not None:
            #     # post the link to kiwistand
            #     send_link_to_kiwistand(link, title)

            # last_cast = client.post_cast(m, parent=Parent(fid=cast.actor.fid, hash=cast.content.cast.hash))
            pass

def stream_casts():
    logging.info("streaming casts")
    # Stream new casts, and if a link is found, post to kiwistand
    for cast in client.stream_casts():
        if cast:
            logging.info(f"{cast.author.username}:")
            logging.info(cast.text)
            logging.info("----")

            link = extract_link(cast.text)
            logging.info(f"link: {link}")
            title = get_page_title(link)
            logging.info(f"title: {title}")

            # if link is not None and title is not None:
            #     # post the link to kiwistand
            #     send_link_to_kiwistand(link, title)
                
            pass

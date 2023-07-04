import re
import logging

from decouple import config
from pymongo import MongoClient
from farcaster import Warpcast
from farcaster.models import Parent
from eatkiwi.utils.links import get_page_content
from eatkiwi.utils.openai import generate_webpage_title_and_summary
from eatkiwi.utils.strings import trim_to_cast_max_bytes
from eatkiwi.farcaster.utils import error_reply


class Skin:
    SKIN_PATTERN = r'\bskin\b'

    def __init__(self, fcc: Warpcast, bot_fname, dev_mode):
        self.fcc = fcc
        self.bot_fname = bot_fname
        self.DEV_MODE = dev_mode
    

    def skin_offline_reply(self):
        if re.search(self.SKIN_PATTERN):
            return "I'm sorry, but I'm not skinning 🥝casts🥝 right now."


    def skin_notification(self, notification):
        logging.info(f"[skin_notification] Received notification: {notification}")

        try:
            # The parent cast is the one that should be skinned
            parent_cast = self.fcc.get_cast(notification.content.cast.parent_hash).cast
            logging.info(f"[skin_notification] Parent cast: {parent_cast}")

            # Ensure that the notification is a reply to a cast from the bot
            if f"@{parent_cast.author.username}" != self.bot_fname:
                logging.error(f"[skin_notification] Parent cast is not from bot: {parent_cast.author.username}")
                # self.fcc.post_cast("Sorry, I only skin 🥝links🥝 I post. Ask me to 🥝skin🥝 one of my own casts and I'll share the original cast!", parent=Parent(fid=notification.content.cast.author.fid, hash=notification.content.cast.hash))
                return
            
            # Query the database for the hash of the replied-to bot cast to get the original cast info
            mongo_client = MongoClient(config("MONGO_URL"))
            db = mongo_client[config("MONGO_DB_FC")]
            collection_eat_casts = db[config("MONGO_FC_COLLECTION_EAT_CASTS")]
            result = collection_eat_casts.find_one({"eat_cast_hash": parent_cast.hash})
            if result is None:
                logging.error(f"[skin_notification] Failed to find original cast for hash: {parent_cast.hash}")
                # self.fcc.post_cast("Sorry, I couldn't find the original cast. Ask me to 🥝skin🥝 one of my own casts and I'll share the original cast!", parent=Parent(fid=notification.content.cast.author.fid, hash=notification.content.cast.hash))
                return
            
            # Create a warpcast url for the original cast
            original_cast_url = f"https://warpcast.com/{result['original_cast_username']}/{result['original_cast_hash']}"

            # Reply to the notifying cast with the original cast url
            logging.info(f"[skin_notification] Sending original cast url: {original_cast_url}")
            # self.fcc.post_cast(f"🥝 Here's the original cast: {original_cast_url}", parent=Parent(fid=notification.content.cast.author.fid, hash=notification.content.cast.hash))

        except Exception as e:
            logging.error(f"[skin_notification] Failed sending cast: {e}")
            error_reply(self.fcc, notification.content.cast)

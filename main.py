import re
import time
import logging
from farcaster import Warpcast
from farcaster.models import Parent
from decouple import config

# Configuring logging to output to the console at or above this level
logging.basicConfig(level=logging.INFO)

# The client will automagically cycle through access tokens
client = Warpcast(config("FARCASTER_MNEMONIC_DEV01"), rotation_duration=1)

def trim_to_cast(s):
    encoded = s.encode('utf-8')
    while len(encoded) > 320:
        s = s[:-1]
        encoded = s.encode('utf-8')
    return s

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

        

        # last_cast = client.post_cast(m, parent=Parent(fid=cast.actor.fid, hash=cast.content.cast.hash))
        
        pass

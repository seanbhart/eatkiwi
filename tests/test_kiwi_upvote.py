import logging
logging.basicConfig(level=logging.info)

from decouple import config
from eatkiwi.kiwi.message import upvote_link_on_kiwistand

MNEMONIC = config("FARCASTER_MNEMONIC_DEV01")

if __name__ == "__main__":
    """
    This function sends a test link to Kiwistand. 

    The link provided should NOT be an original link, indicating that
    the link has been submitted before. It's important that the link
    HAS been previously submitted to ensure accurate testing and analysis.
    """
    href = "https://www.theblock.co/post/232604/coinbase-ceo-cites-rising-threat-from-china-in-fresh-plea-to-us-officials"
    upvote_link_on_kiwistand(href, MNEMONIC)
